#!/usr/bin/env python3
"""Read-only Zoho CRM probe for Virtual Coworker (2026-08-13).

Hard rules:
- GET + COQL SELECT only. Never create/update/delete/upsert/convert.
- Never print tokens, client secrets, refresh tokens, or raw emails/phones.
- Cap API volume. Stop on rate limit.
- Does not set ZOHO_CRM_ENABLED. Does not call Google Ads.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "zoho"))

from _common import (  # noqa: E402
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    http_get_json,
    load_credentials,
    mask_secret,
    refresh_access_token,
    write_json,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = REPO_ROOT / ".env"
OUT_MD = Path(__file__).resolve().parent / "ZOHO-CRM-READ-2026-08-13.md"
SAMPLE_PER_MODULE = 30
MAX_CALLS = 50
COUNT_GROUP_MODULES = 6
CALLS = 0
STOPPED_REASON = None

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().\-]{7,}\d)")
TRACK_HINTS = (
    "gclid",
    "gbraid",
    "wbraid",
    "utm",
    "google",
    "ads",
    "click",
    "zapier",
    "callrail",
    "calendly",
    "campaign",
    "source",
    "landing",
    "referrer",
    "market",
    "website",
    "submission",
    "job_seeker",
    "jobseeker",
    "layout",
    "status",
    "country",
    "currency",
)

PRIORITY_LABELS = {
    "leads",
    "contacts",
    "accounts",
    "deals",
    "potentials",
    "campaigns",
    "job orders",
    "job openings",
    "job openings/orders",
    "placements",
    "candidates",
    "applications",
    "vendors",
    "calls",
    "tasks",
}

VC_DOMAINS = {
    "virtualcoworker.com",
    "virtualcoworker.com.au",
    "virtualcoworker.com.ph",
    "virtualcoworker.app",
}


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def bump() -> bool:
    global CALLS, STOPPED_REASON
    CALLS += 1
    if CALLS > MAX_CALLS:
        STOPPED_REASON = f"hit MAX_CALLS={MAX_CALLS}"
        return False
    return True


def get(url: str, token: str) -> tuple[int, Any]:
    global STOPPED_REASON
    if not bump():
        return 0, {"error": STOPPED_REASON}
    status, body = http_get_json(url, access_token=token)
    if status == 429:
        STOPPED_REASON = "rate_limited HTTP 429"
    return status, body


def post_json(url: str, token: str, payload: dict[str, Any]) -> tuple[int, Any]:
    global STOPPED_REASON
    if not bump():
        return 0, {"error": STOPPED_REASON}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.getcode() or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
        if status == 429:
            STOPPED_REASON = "rate_limited HTTP 429"
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, {"raw": raw[:300]}


def email_domain(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    m = EMAIL_RE.search(value)
    if not m:
        return None
    return m.group(0).split("@", 1)[1].lower()


def redact(value: Any) -> Any:
    if isinstance(value, str):
        s = EMAIL_RE.sub("[email]", value)
        s = PHONE_RE.sub("[phone]", s)
        return s
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def name_of(obj: Any) -> str:
    if isinstance(obj, dict):
        return str(obj.get("name") or obj.get("id") or "")
    if obj is None:
        return ""
    return str(obj)


def field_map(fields: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for f in fields:
        api = str(f.get("api_name") or "")
        if api:
            out[api] = f
    return out


def looks_tracking(api: str, label: str) -> bool:
    blob = f"{api} {label}".lower()
    return any(h in blob for h in TRACK_HINTS)


def pick_modules(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    picked: list[dict[str, Any]] = []
    seen: set[str] = set()
    for m in modules:
        api = str(m.get("api_name") or "")
        if not api or api in seen:
            continue
        label = f"{m.get('plural_label') or ''} {m.get('singular_label') or ''} {api}".lower()
        generated = bool(m.get("generated_type") == "default" and m.get("module_name"))
        interesting = any(p in label for p in PRIORITY_LABELS) or any(
            x in api.lower()
            for x in ("job", "place", "lead", "contact", "account", "deal", "campaign", "candidate")
        )
        custom = m.get("generated_type") == "custom"
        if interesting or (custom and "job" in label):
            picked.append(m)
            seen.add(api)
    # Always include standard if present
    for api in ("Leads", "Contacts", "Accounts", "Deals", "Campaigns"):
        for m in modules:
            if m.get("api_name") == api and api not in seen:
                picked.append(m)
                seen.add(api)
    return picked[:12]


def sample_fields_for(fmap: dict[str, dict[str, Any]]) -> list[str]:
    wanted = [
        "id",
        "First_Name",
        "Last_Name",
        "Full_Name",
        "Email",
        "Phone",
        "Company",
        "Account_Name",
        "Lead_Source",
        "Source",
        "Lead_Status",
        "Status",
        "Stage",
        "Website",
        "Created_Time",
        "Created_By",
        "Layout",
        "Owner",
        "GCLID",
        "$gclid",
        "Gclid",
        "Google_Ad",
        "Ad_Campaign_Name",
        "AdGroup_Name",
        "Keyword",
        "UTM_Source",
        "UTM_Medium",
        "UTM_Campaign",
        "Campaign_Source",
        "Description",
        "Country",
        "Mailing_Country",
        "Billing_Country",
        "Currency",
        "Tag",
        "Tags",
    ]
    have = [w for w in wanted if w in fmap or w.startswith("$")]
    # plus any tracking-ish custom fields
    extra = [
        api
        for api, f in fmap.items()
        if looks_tracking(api, str(f.get("field_label") or ""))
        and api not in have
        and f.get("data_type") not in {"profileimage", "RRULE", "subform", "fileupload"}
    ]
    out = []
    for x in have + extra:
        if x not in out:
            out.append(x)
    return out[:40]


def summarize_sample(records: list[dict[str, Any]], fmap: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sources: Counter[str] = Counter()
    creators: Counter[str] = Counter()
    layouts: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    websites: Counter[str] = Counter()
    email_domains: Counter[str] = Counter()
    has_gclid = 0
    has_utm = 0
    has_google_ads_fields = 0
    rows: list[dict[str, Any]] = []
    gclid_keys = [k for k in fmap if "gclid" in k.lower()]
    utm_keys = [k for k in fmap if "utm" in k.lower()]
    ads_keys = [
        k
        for k in fmap
        if any(x in k.lower() for x in ("google_ad", "adgroup", "ad_campaign", "keyword", "click_type"))
    ]

    for rec in records:
        src = rec.get("Lead_Source") or rec.get("Source") or rec.get("Origin") or ""
        if isinstance(src, dict):
            src = src.get("name") or ""
        sources[str(src) or "(blank)"] += 1
        creators[name_of(rec.get("Created_By"))] += 1
        layouts[name_of(rec.get("Layout"))] += 1
        st = rec.get("Lead_Status") or rec.get("Status") or rec.get("Stage") or ""
        if isinstance(st, dict):
            st = st.get("name") or ""
        statuses[str(st) or "(blank)"] += 1

        web = str(rec.get("Website") or "")
        if web:
            low = web.lower()
            if "virtualcoworker.app" in low:
                websites["virtualcoworker.app"] += 1
            elif "virtualcoworker.com.ph" in low:
                websites["virtualcoworker.com.ph"] += 1
            elif "virtualcoworker.com.au" in low:
                websites["virtualcoworker.com.au"] += 1
            elif "virtualcoworker.com" in low:
                websites["virtualcoworker.com"] += 1
            elif "zapier" in low:
                websites["zapier"] += 1
            else:
                websites["other"] += 1

        em = rec.get("Email")
        d = email_domain(em)
        if d:
            email_domains[d] += 1

        gclid_hit = False
        for k in gclid_keys:
            if rec.get(k):
                gclid_hit = True
        if rec.get("$gclid"):
            gclid_hit = True
        if gclid_hit:
            has_gclid += 1
        if any(rec.get(k) for k in utm_keys):
            has_utm += 1
        if any(rec.get(k) for k in ads_keys):
            has_google_ads_fields += 1

        company = rec.get("Company") or rec.get("Account_Name") or rec.get("Name") or ""
        if isinstance(company, dict):
            company = company.get("name") or ""
        rows.append(
            {
                "first_name": str(rec.get("First_Name") or rec.get("Full_Name") or "")[:24],
                "company": str(company)[:40],
                "source": str(src)[:40],
                "status": str(st)[:30],
                "created": str(rec.get("Created_Time") or "")[:19],
                "created_by": name_of(rec.get("Created_By"))[:30],
                "has_gclid": gclid_hit,
            }
        )

    return {
        "n": len(records),
        "sources": dict(sources.most_common(15)),
        "created_by": dict(creators.most_common(15)),
        "layouts": dict(layouts.most_common(10)),
        "statuses": dict(statuses.most_common(12)),
        "website_hosts": dict(websites),
        "email_domains_top": dict(email_domains.most_common(12)),
        "has_gclid": has_gclid,
        "has_utm": has_utm,
        "has_google_ads_fields": has_google_ads_fields,
        "preview": rows[:12],
    }


def count_from_coql(body: Any) -> int | None:
    if not isinstance(body, dict):
        return None
    data = body.get("data")
    if isinstance(data, list) and data:
        row = data[0]
        if isinstance(row, dict):
            for k, v in row.items():
                if "count" in k.lower() or k.lower() == "id":
                    try:
                        return int(v)
                    except (TypeError, ValueError):
                        continue
            vals = list(row.values())
            if vals:
                try:
                    return int(vals[0])
                except (TypeError, ValueError):
                    return None
    info = body.get("info")
    if isinstance(info, dict) and info.get("count") is not None:
        try:
            return int(info["count"])
        except (TypeError, ValueError):
            return None
    return None


def main() -> int:
    load_dotenv(ENV_PATH)
    enabled = (os.environ.get("ZOHO_CRM_ENABLED") or "").strip().lower()
    if enabled == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true. Probe requires it stay false.")
        return 2

    ensure_local_dir()
    creds = load_credentials()
    print(f"Credentials source={creds.get('source')} client_id={mask_secret(creds.get('client_id'))}")
    print(f"ZOHO_CRM_ENABLED={enabled or 'unset'} (must stay false)")

    token_body = refresh_access_token(creds)
    token = str(token_body["access_token"])
    api_domain = creds["api_domain"]
    print(f"Token refresh ok. api_domain={api_domain} (token not printed)")

    findings: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api_domain": api_domain,
        "accounts_url": creds["accounts_url"],
        "zoho_crm_enabled": enabled or "false",
        "calls": 0,
        "org": {},
        "users": {},
        "modules": [],
        "module_fields": {},
        "counts": {},
        "samples": {},
        "integrations_traces": {},
        "errors": [],
    }

    # --- org ---
    st, org_body = get(crm_url(api_domain, "/org"), token)
    write_json(LOCAL_ZOHO / "raw-org.json", {"http_status": st, "body": redact(org_body)})
    orgs = []
    if isinstance(org_body, dict):
        orgs = org_body.get("org") or []
    if isinstance(orgs, list) and orgs:
        o = orgs[0] if isinstance(orgs[0], dict) else {}
        findings["org"] = {
            "http_status": st,
            "company_name": o.get("company_name") or o.get("org_name"),
            "domain_name": o.get("domain_name"),
            "primary": o.get("primary"),
            "iso_code": o.get("iso_code"),
            "currency_locale": o.get("currency_locale"),
            "time_zone": o.get("time_zone"),
            "mc_status": o.get("mc_status"),
            "license_details": {
                k: (o.get("license_details") or {}).get(k)
                for k in ("paid", "users_license_purchased", "paid_type", "trial")
                if isinstance(o.get("license_details"), dict)
            },
            "zia_org_enrichment": bool(o.get("zia_org_enrichment")),
        }
    else:
        findings["errors"].append(f"org HTTP {st}")
        findings["org"] = {"http_status": st, "body_keys": list(org_body) if isinstance(org_body, dict) else type(org_body).__name__}

    # --- users ---
    st, users_body = get(crm_url(api_domain, "/users?type=AllUsers"), token)
    write_json(LOCAL_ZOHO / "raw-users-redacted.json", {"http_status": st, "body": redact(users_body)})
    users = []
    if isinstance(users_body, dict):
        users = users_body.get("users") or []
    user_rows = []
    domain_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    profile_counts: Counter[str] = Counter()
    for u in users if isinstance(users, list) else []:
        if not isinstance(u, dict):
            continue
        d = email_domain(u.get("email"))
        if d:
            domain_counts[d] += 1
        status_counts[str(u.get("status") or "")] += 1
        prof = name_of(u.get("profile"))
        profile_counts[prof] += 1
        user_rows.append(
            {
                "full_name": u.get("full_name") or u.get("name"),
                "status": u.get("status"),
                "email_domain": d,
                "vc_email": d in VC_DOMAINS if d else False,
                "role": name_of(u.get("role")),
                "profile": prof,
                "confirmed": u.get("confirm"),
                "created_time": str(u.get("created_time") or "")[:19],
            }
        )
    findings["users"] = {
        "http_status": st,
        "count": len(user_rows),
        "status_counts": dict(status_counts),
        "email_domains": dict(domain_counts.most_common()),
        "profiles": dict(profile_counts),
        "people": user_rows,
    }

    # --- modules ---
    st, mod_body = get(crm_url(api_domain, "/settings/modules"), token)
    write_json(LOCAL_ZOHO / "raw-modules.json", {"http_status": st, "body": mod_body if not isinstance(mod_body, dict) else {
        "modules": [
            {
                "api_name": m.get("api_name"),
                "plural_label": m.get("plural_label"),
                "singular_label": m.get("singular_label"),
                "generated_type": m.get("generated_type"),
                "api_supported": m.get("api_supported"),
                "module_name": m.get("module_name"),
                "access_type": m.get("access_type"),
                "visible": m.get("visible"),
                "creatable": m.get("creatable"),
                "viewable": m.get("viewable"),
            }
            for m in (mod_body.get("modules") or [])
            if isinstance(m, dict)
        ]
    }})
    modules: list[dict[str, Any]] = []
    if isinstance(mod_body, dict):
        for m in mod_body.get("modules") or []:
            if not isinstance(m, dict):
                continue
            if m.get("api_supported") is False:
                continue
            modules.append(
                {
                    "api_name": m.get("api_name"),
                    "plural_label": m.get("plural_label"),
                    "singular_label": m.get("singular_label"),
                    "generated_type": m.get("generated_type"),
                    "module_name": m.get("module_name"),
                    "access_type": m.get("access_type"),
                    "visible": m.get("visible"),
                    "creatable": m.get("creatable"),
                    "viewable": m.get("viewable"),
                    "editable": m.get("editable"),
                }
            )
    findings["modules"] = modules
    picked = pick_modules(modules)
    findings["picked_modules"] = [m.get("api_name") for m in picked]

    # --- fields for picked modules ---
    for m in picked:
        if STOPPED_REASON:
            break
        api = str(m.get("api_name"))
        st, fbody = get(crm_url(api_domain, f"/settings/fields?module={api}"), token)
        fields_raw = []
        if isinstance(fbody, dict):
            fields_raw = fbody.get("fields") or []
        slim = []
        tracking = []
        for f in fields_raw if isinstance(fields_raw, list) else []:
            if not isinstance(f, dict):
                continue
            row = {
                "api_name": f.get("api_name"),
                "field_label": f.get("field_label") or f.get("display_label"),
                "data_type": f.get("data_type"),
                "custom_field": f.get("custom_field"),
                "system_mandatory": f.get("system_mandatory"),
            }
            slim.append(row)
            if looks_tracking(str(row["api_name"] or ""), str(row["field_label"] or "")):
                tracking.append(row)
        findings["module_fields"][api] = {
            "http_status": st,
            "field_count": len(slim),
            "trackingish": tracking,
            "all_api_names": [s["api_name"] for s in slim],
        }
        write_json(LOCAL_ZOHO / f"raw-fields-{api}.json", {"http_status": st, "fields": slim})

    # related lists + layouts for a few employer modules
    for api in findings["picked_modules"][:6]:
        if STOPPED_REASON:
            break
        st, rbody = get(crm_url(api_domain, f"/settings/related_lists?module={api}"), token)
        names = []
        if isinstance(rbody, dict):
            for r in rbody.get("related_lists") or []:
                if isinstance(r, dict):
                    names.append(
                        {
                            "api_name": r.get("api_name"),
                            "display_label": r.get("display_label"),
                            "module": (r.get("module") or {}).get("api_name") if isinstance(r.get("module"), dict) else r.get("module"),
                        }
                    )
        findings.setdefault("related_lists", {})[api] = names
        adsish = [n for n in names if any(x in json.dumps(n).lower() for x in ("google", "ads", "campaign", "zapier"))]
        if adsish:
            findings["integrations_traces"].setdefault("related_lists_adsish", {})[api] = adsish

    # webhooks / integrations (best-effort; extra scopes may 403)
    for path, key in (
        ("/settings/webhooks", "webhooks"),
        ("/settings/automation/workflows", "workflows"),
    ):
        if STOPPED_REASON:
            break
        st, body = get(crm_url(api_domain, path), token)
        snippet = {"http_status": st}
        if isinstance(body, dict):
            snippet["code"] = body.get("code")
            snippet["message"] = body.get("message")
            if body.get("webhooks"):
                snippet["count"] = len(body["webhooks"]) if isinstance(body["webhooks"], list) else None
            if body.get("workflow"):
                snippet["count"] = len(body["workflow"]) if isinstance(body["workflow"], list) else None
            keys = [k for k in body.keys() if k not in {"webhooks", "workflow"}]
            snippet["keys"] = keys[:20]
        findings["integrations_traces"][key] = snippet

    # --- COQL counts ---
    since_90 = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00+00:00")
    coql_url = crm_url(api_domain, "/coql")
    for m in picked:
        if STOPPED_REASON:
            break
        api = str(m.get("api_name"))
        fmap = field_map(
            [
                {"api_name": n}
                for n in (findings["module_fields"].get(api, {}).get("all_api_names") or [])
            ]
        )
        if not fmap:
            continue
        rec: dict[str, Any] = {"module": api}
        st, body = post_json(coql_url, token, {"select_query": f"select COUNT(id) from {api}"})
        rec["all_time_http"] = st
        rec["all_time"] = count_from_coql(body)
        if st >= 400:
            rec["all_time_error"] = redact(
                (body.get("message") if isinstance(body, dict) else str(body)[:180])
            )
        if "Created_Time" in fmap:
            st2, body2 = post_json(
                coql_url,
                token,
                {"select_query": f"select COUNT(id) from {api} where Created_Time >= '{since_90}'"},
            )
            rec["last_90d_http"] = st2
            rec["last_90d"] = count_from_coql(body2)
            if st2 >= 400:
                rec["last_90d_error"] = redact(
                    body2.get("message") if isinstance(body2, dict) else str(body2)[:180]
                )
        do_group = len(findings["counts"]) < COUNT_GROUP_MODULES
        if do_group:
            for group_field in ("Lead_Source", "Source"):
                if group_field not in fmap:
                    continue
                if STOPPED_REASON:
                    break
                q = f"select {group_field}, COUNT(id) from {api} group by {group_field} limit 50"
                stg, bg = post_json(coql_url, token, {"select_query": q})
                if stg == 200 and isinstance(bg, dict) and isinstance(bg.get("data"), list):
                    grouped = []
                    for row in bg["data"]:
                        if not isinstance(row, dict):
                            continue
                        key = row.get(group_field)
                        cnt = None
                        for k, v in row.items():
                            if k != group_field:
                                try:
                                    cnt = int(v)
                                except (TypeError, ValueError):
                                    continue
                        grouped.append(
                            {
                                "key": redact(name_of(key) if isinstance(key, dict) else key),
                                "count": cnt,
                            }
                        )
                    rec[f"by_{group_field}"] = grouped[:20]
                else:
                    rec[f"by_{group_field}_http"] = stg
        findings["counts"][api] = rec

    # --- samples ---
    for m in picked:
        if STOPPED_REASON:
            break
        api = str(m.get("api_name"))
        names = findings["module_fields"].get(api, {}).get("all_api_names") or []
        fmap = field_map([{"api_name": n} for n in names])
        if not fmap:
            continue
        fields = sample_fields_for(fmap)
        # Zoho GET records: fields comma-separated, skip $gclid in fields param
        fields_q = ",".join(f for f in fields if not str(f).startswith("$"))
        path = f"/{api}?per_page={SAMPLE_PER_MODULE}&sort_by=Created_Time&sort_order=desc"
        if fields_q:
            path += f"&fields={urllib.parse.quote(fields_q) if False else fields_q}"
        st, body = get(crm_url(api_domain, path), token)
        records = []
        if isinstance(body, dict):
            records = body.get("data") or []
        if st >= 400:
            findings["samples"][api] = {
                "http_status": st,
                "error": redact(body.get("message") if isinstance(body, dict) else str(body)[:180]),
            }
            continue
        if not isinstance(records, list):
            records = []
        findings["samples"][api] = summarize_sample(
            [r for r in records if isinstance(r, dict)], fmap
        )
        findings["samples"][api]["http_status"] = st
        findings["samples"][api]["fields_requested"] = [f for f in fields if not str(f).startswith("$")]

    findings["calls"] = CALLS
    findings["stopped_reason"] = STOPPED_REASON
    write_json(LOCAL_ZOHO / "probe-summary-2026-08-13.json", findings)
    write_markdown(findings)
    print(f"Wrote {OUT_MD}")
    print(f"API calls={CALLS} stopped={STOPPED_REASON}")
    print("No CRM records were written. ZOHO_CRM_ENABLED left false. No email sent.")
    return 0


def write_markdown(f: dict[str, Any]) -> None:
    org = f.get("org") or {}
    users = f.get("users") or {}
    modules = f.get("modules") or []
    counts = f.get("counts") or {}
    samples = f.get("samples") or {}
    fields = f.get("module_fields") or {}
    traces = f.get("integrations_traces") or {}

    visible = [m for m in modules if m.get("visible") is not False]
    custom = [m for m in modules if m.get("generated_type") == "custom"]
    jobish = [
        m
        for m in modules
        if any(x in f"{m.get('plural_label')} {m.get('api_name')}".lower() for x in ("job", "place", "candidate"))
    ]

    def bullet_counts() -> list[str]:
        lines = []
        for api, rec in counts.items():
            all_t = rec.get("all_time")
            d90 = rec.get("last_90d")
            err = rec.get("all_time_error")
            if err and all_t is None:
                lines.append(f"- **{api}**: count failed ({err})")
            else:
                extra = f"; last 90 days: **{d90}**" if d90 is not None else ""
                lines.append(f"- **{api}**: {all_t} all-time{extra}")
        return lines

    def tracking_gaps() -> list[str]:
        lines = []
        for api, meta in fields.items():
            names = [str(n).lower() for n in (meta.get("all_api_names") or [])]
            has_gclid = any("gclid" in n for n in names)
            has_utm = any("utm" in n for n in names)
            has_google = any("google" in n or n.startswith("ad_") or "adgroup" in n for n in names)
            track = meta.get("trackingish") or []
            labels = ", ".join(f"`{t.get('api_name')}`" for t in track[:18]) or "(none that look like ads/UTM/source)"
            lines.append(
                f"- **{api}** ({meta.get('field_count')} fields): GCLID field={'yes' if has_gclid else 'NO'}; "
                f"UTM={'yes' if has_utm else 'NO'}; Google-Ads-ish={'yes' if has_google else 'NO'}. Tracking-ish: {labels}"
            )
        return lines

    people = users.get("people") or []
    active = [p for p in people if str(p.get("status")).lower() == "active"]
    non_vc = [p for p in people if p.get("email_domain") and not p.get("vc_email")]
    agencyish = [
        p
        for p in non_vc
        if p.get("email_domain")
        and p.get("email_domain")
        not in VC_DOMAINS
        and not str(p.get("email_domain") or "").endswith("zoho.com")
        and p.get("email_domain") != "gmail.com"
    ]

    lines = [
        "# Zoho CRM read — 13 Aug 2026",
        "",
        "Read-only look at the Virtual Coworker Zoho CRM. **Nothing was written.** `ZOHO_CRM_ENABLED` stayed **false**. No email was sent. Google Ads API was not called.",
        "",
        f"Generated: {f.get('generated_at')}  ",
        f"Org name in Zoho: **{org.get('company_name') or '(unknown)'}**  ",
        f"API calls this pass: **{f.get('calls')}** (cap {MAX_CALLS})"
        + (f" — stopped: {f.get('stopped_reason')}" if f.get("stopped_reason") else ""),
        "",
        "## What’s going on (plain English)",
        "",
    ]

    # We'll fill bullets after we have data — the caller writes findings first.
    # This function builds them from findings.

    org_name = org.get("company_name") or "this Zoho org"
    n_users = users.get("count") or 0
    n_mod = len(modules)
    jo_count = None
    contact_count = None
    for api, rec in counts.items():
        low = api.lower()
        if "job" in low and jo_count is None:
            jo_count = rec.get("all_time")
        if api == "Contacts":
            contact_count = rec.get("all_time")

    bullets = [
        f"The login we have is **Zoho CRM** for **{org_name}** — not a second mystery product. Time zone: {org.get('time_zone') or 'unknown'}. Currency locale: {org.get('currency_locale') or org.get('iso_code') or 'unknown'}.",
        f"There are **{n_users} users** on the seat list. Active: {len(active)}. Email domains: {', '.join(f'{k} ({v})' for k, v in (users.get('email_domains') or {}).items()) or 'unknown'}.",
        f"CRM has **{n_mod} API-visible modules**. Custom modules: {', '.join(m.get('api_name') or '' for m in custom) or 'none found'}. Job/placement-ish: {', '.join((m.get('plural_label') or m.get('api_name') or '') for m in jobish) or 'none found'}.",
        f"George’s old UI note (no Leads, Job Orders + Placements) is checked against this API list below — not assumed.",
        f"Contacts all-time count: **{contact_count}**. Job-order-ish all-time count: **{jo_count}**. Compare later to the Ads story of **67 US + 36 AU “Zoho JO” uploads** (those are Google Ads conversion *uploads via Zapier*, not proof of this CRM).",
        "The paid microsite (`virtualcoworker.app`) is **not** writing into Zoho today. The app switch `ZOHO_CRM_ENABLED` is still false.",
        "Do **not** treat this CRM as the source of truth for Google Ads conversions. The agencies already uploaded “job orders” into Ads through Zapier; that is a separate, messy meter.",
    ]
    for b in bullets:
        lines.append(f"- {b}")

    lines += [
        "",
        "## Org",
        "",
        f"- Company: {org.get('company_name')}",
        f"- Domain name in Zoho: {org.get('domain_name')}",
        f"- Time zone: {org.get('time_zone')}",
        f"- Currency locale / ISO: {org.get('currency_locale')} / {org.get('iso_code')}",
        f"- License: {org.get('license_details')}",
        "",
        "## Who’s in here",
        "",
        f"- Users returned: **{n_users}**",
        f"- Status mix: {users.get('status_counts')}",
        f"- Profiles: {users.get('profiles')}",
        f"- Email domains: {users.get('email_domains')}",
        "",
        "People (name + domain only — no emails):",
        "",
    ]
    for p in people:
        flag = ""
        if p.get("email_domain") and not p.get("vc_email") and p.get("email_domain") not in {"zoho.com"}:
            flag = " ← **not a virtualcoworker.com address**"
        lines.append(
            f"- {p.get('full_name')} · {p.get('status')} · {p.get('profile')} / {p.get('role')} · `{p.get('email_domain')}`{flag}"
        )

    if agencyish:
        lines += [
            "",
            "Non-VC, non-Zoho domains (possible agency leftovers):",
            "",
        ]
        for p in agencyish:
            lines.append(f"- {p.get('full_name')} · `{p.get('email_domain')}` · {p.get('status')} · {p.get('profile')}")

    lines += [
        "",
        "## Modules present",
        "",
        "| API name | Label | Type | Visible | View | Create |",
        "|----------|-------|------|---------|------|--------|",
    ]
    for m in modules:
        lines.append(
            f"| `{m.get('api_name')}` | {m.get('plural_label') or ''} | {m.get('generated_type') or ''} | "
            f"{m.get('visible')} | {m.get('viewable')} | {m.get('creatable')} |"
        )

    lines += [
        "",
        f"Inventoried fields for: {', '.join(f.get('picked_modules') or [])}",
        "",
        "## Tracking fields (this is the Ads question)",
        "",
        "Google can only import offline conversions if the CRM still has the **Google click id** (GCLID) on the same record as the real outcome. Missing that field = we cannot do a clean import later.",
        "",
        *tracking_gaps(),
        "",
        "## Volume",
        "",
        *bullet_counts(),
        "",
        "## Sample records (redacted)",
        "",
        "First name + company + source + date only. Emails and phones stripped.",
        "",
    ]

    for api, samp in samples.items():
        if samp.get("error"):
            lines.append(f"### {api}")
            lines.append("")
            lines.append(f"Could not sample: {samp.get('error')} (HTTP {samp.get('http_status')})")
            lines.append("")
            continue
        lines += [
            f"### {api} (newest {samp.get('n')} looked at)",
            "",
            f"- Sources: {samp.get('sources')}",
            f"- Created by: {samp.get('created_by')}",
            f"- Statuses: {samp.get('statuses')}",
            f"- Layouts: {samp.get('layouts')}",
            f"- Website hosts in sample: {samp.get('website_hosts')}",
            f"- Email domains in sample: {samp.get('email_domains_top')}",
            f"- Records with GCLID filled: **{samp.get('has_gclid')}** / {samp.get('n')}",
            f"- Records with UTM filled: **{samp.get('has_utm')}** / {samp.get('n')}",
            f"- Records with Google Ads-ish fields filled: **{samp.get('has_google_ads_fields')}** / {samp.get('n')}",
            "",
            "| First name | Company | Source | Status | Created | Created by | GCLID? |",
            "|------------|---------|--------|--------|---------|------------|--------|",
        ]
        for row in samp.get("preview") or []:
            lines.append(
                f"| {row.get('first_name') or ''} | {row.get('company') or ''} | {row.get('source') or ''} | "
                f"{row.get('status') or ''} | {row.get('created') or ''} | {row.get('created_by') or ''} | "
                f"{'yes' if row.get('has_gclid') else ''} |"
            )
        lines.append("")

        by_src = (counts.get(api) or {}).get("by_Lead_Source") or (counts.get(api) or {}).get("by_Source")
        if by_src:
            lines.append("All-time source breakdown (CRM count, not a sample):")
            lines.append("")
            for row in by_src:
                lines.append(f"- {row.get('key') or '(blank)'}: {row.get('count')}")
            lines.append("")

    lines += [
        "",
        "## Zapier / Google Ads / CallRail / Calendly traces",
        "",
        f"- Webhooks API: {traces.get('webhooks')}",
        f"- Workflows API: {traces.get('workflows')}",
        f"- Related lists that look ads-ish: {traces.get('related_lists_adsish') or '(none spotted in first 6 modules)'}",
        "",
        "Ads conversion actions already known from the **forensic Ads pull** (not from this Zoho call):",
        "",
        "- US: `Zoho JO Submitted US [Original] via Zapier` — **67** conversions (2024-08-01 to 2026-08-12), plus a duplicate `Standard OCI` action with **23**.",
        "- AU: `Zoho JO Submitted AU [Original] via Zapier` — **36** conversions, plus `Standard OCI` **14**.",
        "- Those live in Google Ads as **uploaded clicks**. They are **not** this CRM proving 67/36 real job orders.",
        "",
        "## Can we trust this for Google Ads conversions?",
        "",
        "**No. Do not turn Zoho into a Primary Ads conversion today.**",
        "",
        "### Broken / missing for a clean Ads import",
        "",
        "- Click ids (GCLID) have to exist on the CRM record. See the tracking-field section — if they are missing, offline import cannot match the original ad click.",
        "- Zapier already created a *second* meter in Ads (“Zoho JO Submitted”). Using Zoho again without a single definition would double-count.",
        "- The `.app` paid form is not writing to Zoho (`ZOHO_CRM_ENABLED=false`). New paid inquiries are not landing here.",
        "- Job-seeker vs employer mix has to be checked in the samples above before any “lead” is treated as money.",
        "- US vs AU: we have **one CRM token**. If Australia sales live in another Zoho org or Recruit, this pass cannot see it.",
        "",
        "### What is actually usable",
        "",
        "- This org is reachable read-only. We can keep counting and sampling without turning the write switch on.",
        "- User list shows who still has a seat (including leftover domains).",
        "- Module list settles CRM vs Recruit for *this* token: if Job Orders exist here as a CRM module, we do not need to guess Recruit yet.",
        "- Volume + source breakdown (when COQL worked) is the first honest CRM census the agencies never gave George.",
        "",
        "## Job Orders vs the 67 US / 36 AU story",
        "",
        "Those numbers came from **Google Ads conversion uploads named Zoho JO**, not from a CRM export we had before today. This probe’s Job Order counts (all-time and last 90 days) are the first CRM-side check. If CRM Job Orders are far from 67+36, the Ads number is a Zapier story, not a hiring story. If they are close, we still cannot call them “real employer job orders” until sales says what the Status field means.",
        "",
        "## Recommended next human step",
        "",
        "Ask **Cheyenne / Holly / Braden** (whoever owns Zoho day-to-day) one question: *“When a real US employer becomes a job order, which list and which status in this CRM is that?”* Then we can map Ads later. Do not enable Zoho writes. Do not make Zoho a Primary conversion.",
        "",
        "I can keep reading (more samples, more date splits) if that is useful. **No email was sent.** Findings first — a CEO/ops email is only worth drafting after someone on the team confirms what a Job Order means.",
        "",
        "## Guardrails this pass",
        "",
        "- Zoho: read only",
        "- Google Ads API: not called",
        "- `ZOHO_CRM_ENABLED`: false (unchanged)",
        "- Brand: not enabled",
        "- Email: not sent, no draft in this file",
        "- Dashboard: no new X-ray page",
        "",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
