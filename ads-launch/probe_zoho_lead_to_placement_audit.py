#!/usr/bin/env python3
"""Read-only Zoho CRM lead-to-placement audit (2026-08-18).

Hard rules:
- GET + COQL SELECT only. Never create/update/delete/upsert/convert.
- Never print tokens, client secrets, emails, phones, or raw click IDs.
- Cap API volume. Stop on rate limit.
- Does not set ZOHO_CRM_ENABLED or ZOHO_SUBMISSION_ENABLED.
- Does not call Google Ads.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent / "zoho"))
from _common import (  # noqa: E402
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    http_get_json,
    http_post_json,
    load_credentials,
    refresh_access_token,
    write_json,
)

REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / ".env"
MAX_CALLS = 85
CALLS = 0
STOPPED: str | None = None

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().\-]{7,}\d)")
HOST_RE = re.compile(r"https?://([^/\s]+)", re.I)

TEST_HINTS = (
    "[test]",
    "test lead",
    "api integration test",
    "zoflowx",
    "agent assign test",
    "vc-zoho-test",
    "test_gclid",
)
SEEKER_HINTS = (
    "job seeker",
    "jobseeker",
    "work seeker",
    "work-seeker",
    "looking for work",
    "applicant",
    "i am applying",
    "i'm applying",
    "resume",
    "cv attached",
)
JUNK_STATUSES = {"junk lead"}
NOT_FIT_STATUSES = {"decided against / not a fit", "not a fit"}
FIELD_INTEREST = (
    "gclid",
    "gbraid",
    "wbraid",
    "utm",
    "google",
    "ads",
    "click",
    "campaign",
    "adgroup",
    "ad_group",
    "keyword",
    "search",
    "landing",
    "referrer",
    "referring",
    "source",
    "form",
    "gravity",
    "submission",
    "status",
    "stage",
    "owner",
    "qualify",
    "qualif",
    "note",
    "follow",
    "call",
    "email",
    "import",
    "seeker",
    "spam",
    "junk",
    "test",
    "candidate",
    "applicant",
    "talent",
    "convert",
    "account",
    "contact",
    "region",
    "website",
    "layout",
    "tag",
    "phone",
    "description",
    "profile",
    "invoice",
    "contract",
    "recruit",
    "sync",
    "linked",
    "client",
)


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def redact(value: Any) -> Any:
    if isinstance(value, str):
        s = EMAIL_RE.sub("[email]", value)
        s = PHONE_RE.sub("[phone]", s)
        if "gclid" in s.lower() and len(s) > 12:
            return f"[gclid:{len(s)}chars]"
        return s
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def name_of(obj: Any) -> str:
    if isinstance(obj, dict):
        return str(obj.get("name") or "")
    return str(obj or "")


def host_of(url: Any) -> str:
    if not isinstance(url, str) or not url:
        return ""
    m = HOST_RE.search(url)
    if m:
        return m.group(1).lower()[:80]
    low = url.lower()
    for h in (
        "virtualcoworker.app",
        "virtualcoworker.com.au",
        "virtualcoworker.com.ph",
        "virtualcoworker.com",
    ):
        if h in low:
            return h
    return "(non-url)"


def filled(val: Any) -> bool:
    if val is None:
        return False
    if isinstance(val, dict):
        return bool(val.get("id") or val.get("name"))
    s = str(val).strip()
    return s not in ("", "null", "None", "False")


def bump() -> bool:
    global CALLS, STOPPED
    CALLS += 1
    if CALLS > MAX_CALLS:
        STOPPED = f"hit MAX_CALLS={MAX_CALLS}"
        return False
    return True


def get(url: str, token: str) -> tuple[int, Any]:
    global STOPPED
    if not bump():
        return 0, {"error": STOPPED}
    status, body = http_get_json(url, access_token=token, timeout=45)
    if status == 429:
        STOPPED = "rate_limited HTTP 429"
    return status, body


def coql(url: str, token: str, sql: str) -> tuple[int, Any]:
    global STOPPED
    if not bump():
        return 0, {"error": STOPPED}
    status, body = http_post_json(url, {"select_query": sql}, access_token=token, timeout=45)
    if status == 429:
        STOPPED = "rate_limited HTTP 429"
    return status, body


def count_val(body: Any) -> int | None:
    if not isinstance(body, dict):
        return None
    data = body.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        for v in data[0].values():
            try:
                return int(v)
            except (TypeError, ValueError):
                continue
    return None


def grouped(body: Any, key: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(body, dict):
        return out
    for row in body.get("data") or []:
        if not isinstance(row, dict):
            continue
        k = row.get(key)
        cnt = None
        for kk, v in row.items():
            if kk == key:
                continue
            try:
                cnt = int(v)
            except (TypeError, ValueError):
                continue
        label = name_of(k) if isinstance(k, dict) else (str(k) if k not in (None, "") else "(blank)")
        out.append({"key": redact(label) or "(blank)", "count": cnt})
    return out


def pick_vals(field: dict[str, Any]) -> list[str]:
    raw = field.get("pick_list_values") or []
    out: list[str] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                display = str(item.get("display_value") or item.get("actual_value") or "").strip()
                if display and display not in {"-None-", "--None--"}:
                    out.append(display)
    return out


def field_brief(f: dict[str, Any]) -> dict[str, Any]:
    api = str(f.get("api_name") or "")
    label = str(f.get("field_label") or f.get("display_label") or "")
    dtype = str(f.get("data_type") or "")
    row: dict[str, Any] = {
        "label": label,
        "api_name": api,
        "type": dtype,
        "custom": bool(f.get("custom_field")),
        "read_only": bool(f.get("read_only") or f.get("field_read_only")),
        "required": bool(f.get("required") or f.get("system_mandatory")),
        "lookup": None,
    }
    if dtype in {"lookup", "ownerlookup", "multilookup"}:
        lookup = f.get("lookup") or {}
        if isinstance(lookup, dict):
            row["lookup"] = {
                "module": (lookup.get("module") or {}).get("api_name")
                if isinstance(lookup.get("module"), dict)
                else lookup.get("module"),
                "display_label": lookup.get("display_label"),
            }
    if dtype in {"picklist", "multipicklist"}:
        row["picklist"] = pick_vals(f)[:80]
    return row


def interesting_field(f: dict[str, Any]) -> bool:
    blob = f"{f.get('api_name') or ''} {f.get('field_label') or ''} {f.get('display_label') or ''}".lower()
    return any(h in blob for h in FIELD_INTEREST)


def blob_of(rec: dict[str, Any], keys: tuple[str, ...]) -> str:
    parts: list[str] = []
    for k in keys:
        v = rec.get(k)
        if isinstance(v, dict):
            v = v.get("name")
        if v:
            parts.append(str(v))
    return " ".join(parts).lower()


def classify_enquiry(rec: dict[str, Any]) -> str:
    status = str(rec.get("Lead_Status") or "").strip().lower()
    text = blob_of(
        rec,
        (
            "Company",
            "First_Name",
            "Last_Name",
            "Form_Source",
            "Other_Client_Profile_Information",
            "Job_Position_Required",
            "Lead_Source",
        ),
    )
    if any(h in text for h in TEST_HINTS) or "api integration test" in text:
        return "internal_test"
    if status in JUNK_STATUSES:
        return "spam_or_junk_status"
    if any(h in text for h in SEEKER_HINTS):
        return "job_seeker_text_hint"
    if status in NOT_FIT_STATUSES:
        return "not_a_fit_status"
    if status in {"job order submitted", "placement", "discovery scheduled"}:
        return "employer_progressed_status"
    if filled(rec.get("Company")):
        return "unclassified_has_company"
    return "unclassified"


def ads_tie(rec: dict[str, Any], gclid_key: str, utm_source_key: str, utm_medium_key: str, campaign_key: str) -> str:
    gclid = filled(rec.get(gclid_key))
    src = str(rec.get(utm_source_key) or "").lower()
    med = str(rec.get(utm_medium_key) or "").lower()
    camp = str(rec.get(campaign_key) or rec.get("Campaign_Name") or "").lower()
    lead_src = str(rec.get("Lead_Source") or "").lower()
    if gclid:
        return "gclid_present"
    googleish = any(x in src for x in ("google", "googleads")) or "google" in lead_src
    paidish = med in {"cpc", "ppc", "paid", "paidsearch"} or "vc_" in camp
    if googleish and paidish:
        return "google_utm_no_gclid"
    if googleish:
        return "google_source_or_utm_no_gclid"
    if filled(rec.get(utm_source_key)) or filled(rec.get(campaign_key)):
        return "other_utm_no_gclid"
    return "no_ads_fields"


def summarize_enquiries(records: list[dict[str, Any]]) -> dict[str, Any]:
    classes: Counter[str] = Counter()
    ads: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    regions: Counter[str] = Counter()
    form_src: Counter[str] = Counter()
    creators: Counter[str] = Counter()
    owners: Counter[str] = Counter()
    hosts: Counter[str] = Counter()
    emails: Counter[str] = Counter()
    phones: Counter[str] = Counter()
    companies: Counter[str] = Counter()
    attr = Counter()
    preview: list[dict[str, Any]] = []
    for rec in records:
        cls = classify_enquiry(rec)
        classes[cls] += 1
        ads[ads_tie(rec, "utm_gclid", "utm_source", "utm_medium", "utm_campaign")] += 1
        statuses[str(rec.get("Lead_Status") or "(blank)")] += 1
        sources[str(rec.get("Lead_Source") or "(blank)")] += 1
        regions[str(rec.get("Region") or "(blank)")] += 1
        form_src[str(rec.get("Form_Source") or "(blank)")[:60]] += 1
        creators[name_of(rec.get("Created_By")) or "(blank)"] += 1
        owners[name_of(rec.get("Owner")) or "(blank)"] += 1
        for url_key in ("Referring_URL", "Referrer", "Website"):
            h = host_of(rec.get(url_key))
            if h:
                hosts[h] += 1
        em = rec.get("Email")
        if isinstance(em, str) and em.strip():
            emails[em.strip().lower()] += 1
        ph = rec.get("Phone")
        if isinstance(ph, str) and len(re.sub(r"\D", "", ph)) >= 8:
            phones[re.sub(r"\D", "", ph)] += 1
        co = str(rec.get("Company") or "").strip().lower()
        if co:
            companies[co] += 1
        for k in (
            "utm_gclid",
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "Campaign_Name",
            "Referring_URL",
            "Referrer",
            "Website",
            "Form_Source",
            "Gravity_Form_Entry_ID",
            "Submission_Timestamp",
            "Job_Position_Required",
            "Other_Client_Profile_Information",
        ):
            if filled(rec.get(k)):
                attr[k] += 1
        preview.append(
            {
                "created": str(rec.get("Created_Time") or "")[:19],
                "company": str(rec.get("Company") or "")[:40],
                "status": str(rec.get("Lead_Status") or "")[:40],
                "source": str(rec.get("Lead_Source") or "")[:30],
                "form_source": str(rec.get("Form_Source") or "")[:40],
                "region": str(rec.get("Region") or "")[:12],
                "owner": name_of(rec.get("Owner"))[:28],
                "created_by": name_of(rec.get("Created_By"))[:28],
                "class": cls,
                "ads_tie": ads_tie(rec, "utm_gclid", "utm_source", "utm_medium", "utm_campaign"),
                "has_gclid": filled(rec.get("utm_gclid")),
                "utm_source": str(rec.get("utm_source") or "")[:24],
                "utm_medium": str(rec.get("utm_medium") or "")[:16],
                "utm_campaign": str(rec.get("utm_campaign") or rec.get("Campaign_Name") or "")[:36],
                "utm_term": bool(filled(rec.get("utm_term"))),
                "referrer_host": host_of(rec.get("Referring_URL") or rec.get("Referrer") or ""),
                "has_notes": filled(rec.get("Other_Client_Profile_Information")),
                "converted": bool(rec.get("Converted__s") or rec.get("Converted_Account") or rec.get("Converted_Deal")),
                "gravity_or_sid": filled(rec.get("Gravity_Form_Entry_ID")),
            }
        )
    dup_email = sum(1 for n in emails.values() if n > 1)
    dup_phone = sum(1 for n in phones.values() if n > 1)
    dup_company = sum(1 for n in companies.values() if n > 1)
    return {
        "n": len(records),
        "classes": dict(classes),
        "ads_tie": dict(ads),
        "statuses": dict(statuses.most_common(25)),
        "sources": dict(sources.most_common(20)),
        "regions": dict(regions.most_common(12)),
        "form_source": dict(form_src.most_common(15)),
        "created_by": dict(creators.most_common(15)),
        "owners": dict(owners.most_common(15)),
        "hosts": dict(hosts.most_common(15)),
        "attr_fill": dict(attr),
        "duplicate_emails_in_sample": dup_email,
        "duplicate_phones_in_sample": dup_phone,
        "duplicate_companies_in_sample": dup_company,
        "preview": preview[:25],
    }


def main() -> int:
    load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2

    ensure_local_dir()
    creds = load_credentials()
    token_body = refresh_access_token(creds)
    token = str(token_body["access_token"])
    api = creds["api_domain"]
    coql_url = crm_url(api, "/coql")
    now = datetime.now(timezone.utc)
    since_14 = (now - timedelta(days=14)).strftime("%Y-%m-%dT00:00:00+00:00")
    since_30 = (now - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00+00:00")
    since_90 = (now - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00+00:00")
    week_start = "2026-08-11T00:00:00-07:00"  # Mon 10 Aug PT was previous; this week Mon 17
    # Current week Mon 17 – today (Tue 18). Also last complete week Mon 10–Sun 16.
    this_week_start = "2026-08-17T00:00:00-07:00"
    last_week_start = "2026-08-10T00:00:00-07:00"
    last_week_end = "2026-08-17T00:00:00-07:00"

    out: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "api_version": "v8",
        "windows": {
            "14d": since_14,
            "30d": since_30,
            "90d": since_90,
            "this_week_start_pt": this_week_start,
            "last_week_start_pt": last_week_start,
            "last_week_end_pt": last_week_end,
        },
        "queries": {},
        "modules": [],
        "fields": {},
        "related_lists": {},
        "samples": {},
        "related_samples": {},
        "users_brief": {},
        "ask_ash": [],
        "stopped": None,
    }

    def q(label: str, sql: str, *, group_key: str | None = None) -> dict[str, Any]:
        st, body = coql(coql_url, token, sql)
        rec: dict[str, Any] = {"http": st, "sql": sql}
        if st != 200:
            rec["error"] = redact(
                body.get("message") if isinstance(body, dict) else str(body)[:220]
            )
            if isinstance(body, dict) and body.get("details"):
                rec["details"] = redact(body.get("details"))
        elif group_key or "group by" in sql.lower():
            key = group_key or sql.split("select ", 1)[1].split(",", 1)[0].strip()
            rec["rows"] = grouped(body, key)
        else:
            rec["count"] = count_val(body)
        out["queries"][label] = rec
        print(
            f"{label}: http={st} count={rec.get('count')} "
            f"rows={len(rec.get('rows') or [])} err={str(rec.get('error') or '')[:70]}"
        )
        return rec

    # --- org / modules / users ---
    st, org_body = get(crm_url(api, "/org"), token)
    if isinstance(org_body, dict):
        orgs = org_body.get("org") or []
        org0 = orgs[0] if orgs else {}
        out["org"] = {
            "http": st,
            "company_name": org0.get("company_name"),
            "primary": org0.get("primary"),
            "time_zone": org0.get("time_zone"),
            "currency": org0.get("iso_code") or org0.get("currency"),
            "license": (org0.get("license_details") or {}).get("paid_type")
            if isinstance(org0.get("license_details"), dict)
            else None,
            "users_license_purchased": (org0.get("license_details") or {}).get("users_license_purchased")
            if isinstance(org0.get("license_details"), dict)
            else None,
        }
        print(f"org: {out['org']}")

    st, mod_body = get(crm_url(api, "/settings/modules"), token)
    modules = []
    if isinstance(mod_body, dict):
        for m in mod_body.get("modules") or []:
            if not isinstance(m, dict):
                continue
            modules.append(
                {
                    "api_name": m.get("api_name"),
                    "plural": m.get("plural_label"),
                    "singular": m.get("singular_label"),
                    "api_supported": m.get("api_supported"),
                    "generated_type": m.get("generated_type"),
                    "visible": m.get("visible"),
                }
            )
    out["modules"] = modules
    write_json(LOCAL_ZOHO / "audit-2026-08-18-modules.json", {"http": st, "modules": modules})
    print(f"modules: {len(modules)} api_supported={sum(1 for m in modules if m.get('api_supported'))}")

    st, users_body = get(crm_url(api, "/users?type=AllUsers"), token)
    users_brief = []
    if isinstance(users_body, dict):
        for u in users_body.get("users") or []:
            if not isinstance(u, dict):
                continue
            users_brief.append(
                {
                    "name": u.get("full_name") or u.get("name"),
                    "status": u.get("status"),
                    "profile": (u.get("profile") or {}).get("name")
                    if isinstance(u.get("profile"), dict)
                    else u.get("profile"),
                    "role": (u.get("role") or {}).get("name")
                    if isinstance(u.get("role"), dict)
                    else u.get("role"),
                    "email_domain": (str(u.get("email") or "").split("@")[-1].lower() if u.get("email") else None),
                }
            )
    out["users_brief"] = {
        "http": st,
        "n": len(users_brief),
        "active": sum(1 for u in users_brief if str(u.get("status")).lower() == "active"),
        "people": users_brief,
    }
    print(f"users: n={len(users_brief)}")

    field_modules = [
        "Leads",
        "Job_Orders",
        "Deals",
        "Contacts",
        "Accounts",
        "Calls",
        "Tasks",
        "Notes",
        "Emails",
    ]
    for mod in field_modules:
        if STOPPED:
            break
        st, body = get(crm_url(api, f"/settings/fields?module={mod}"), token)
        if st != 200 or not isinstance(body, dict):
            out["fields"][mod] = {
                "http": st,
                "error": redact(body.get("message") if isinstance(body, dict) else str(body)[:180]),
            }
            print(f"fields {mod}: http={st}")
            continue
        fields = [f for f in (body.get("fields") or []) if isinstance(f, dict)]
        interesting = [field_brief(f) for f in fields if interesting_field(f)]
        out["fields"][mod] = {
            "http": st,
            "count": len(fields),
            "interesting": interesting,
            "all_api_names": [str(f.get("api_name")) for f in fields],
        }
        print(f"fields {mod}: n={len(fields)} interesting={len(interesting)}")

    for mod in ("Leads", "Job_Orders", "Deals", "Contacts"):
        if STOPPED:
            break
        st, body = get(crm_url(api, f"/settings/related_lists?module={mod}"), token)
        lists = []
        if isinstance(body, dict):
            for rl in body.get("related_lists") or []:
                if not isinstance(rl, dict):
                    continue
                lists.append(
                    {
                        "api_name": rl.get("api_name"),
                        "display_label": rl.get("display_label"),
                        "type": rl.get("type"),
                        "href": rl.get("href"),
                        "module": (rl.get("module") or {}).get("api_name")
                        if isinstance(rl.get("module"), dict)
                        else rl.get("module"),
                    }
                )
        out["related_lists"][mod] = {"http": st, "lists": lists}
        print(f"related {mod}: n={len(lists)} http={st}")

    # --- census ---
    for mod in ("Leads", "Job_Orders", "Deals", "Contacts", "Accounts", "Calls", "Tasks"):
        q(f"{mod}.all", f"select COUNT(id) from {mod} where Created_Time is not null")
        q(f"{mod}.90d", f"select COUNT(id) from {mod} where Created_Time >= '{since_90}'")
        q(f"{mod}.30d", f"select COUNT(id) from {mod} where Created_Time >= '{since_30}'")
        q(f"{mod}.14d", f"select COUNT(id) from {mod} where Created_Time >= '{since_14}'")

    q("Leads.this_week", f"select COUNT(id) from Leads where Created_Time >= '{this_week_start}'")
    q(
        "Leads.last_week",
        f"select COUNT(id) from Leads where Created_Time >= '{last_week_start}' and Created_Time < '{last_week_end}'",
    )

    q(
        "Leads.status_90d",
        f"select Lead_Status, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Lead_Status",
    )
    q(
        "Leads.status_14d",
        f"select Lead_Status, COUNT(id) from Leads where Created_Time >= '{since_14}' group by Lead_Status",
    )
    q(
        "Leads.source_90d",
        f"select Lead_Source, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Lead_Source",
    )
    q(
        "Leads.source_14d",
        f"select Lead_Source, COUNT(id) from Leads where Created_Time >= '{since_14}' group by Lead_Source",
    )
    q(
        "Leads.region_90d",
        f"select Region, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Region",
    )
    q(
        "Leads.form_14d",
        f"select Form_Source, COUNT(id) from Leads where Created_Time >= '{since_14}' group by Form_Source",
    )
    q("Leads.gclid_all", "select COUNT(id) from Leads where utm_gclid is not null")
    q("Leads.gclid_90d", f"select COUNT(id) from Leads where utm_gclid is not null and Created_Time >= '{since_90}'")
    q("Leads.gclid_14d", f"select COUNT(id) from Leads where utm_gclid is not null and Created_Time >= '{since_14}'")
    q("Leads.utm_source_14d", f"select COUNT(id) from Leads where utm_source is not null and Created_Time >= '{since_14}'")
    q("Leads.utm_term_all", "select COUNT(id) from Leads where utm_term is not null")
    q("Leads.referring_14d", f"select COUNT(id) from Leads where Referring_URL is not null and Created_Time >= '{since_14}'")
    q("Leads.converted_90d", f"select COUNT(id) from Leads where Converted__s = true and Created_Time >= '{since_90}'")
    q("Leads.converted_all", "select COUNT(id) from Leads where Converted__s = true")
    q("Leads.phone_source_90d", f"select COUNT(id) from Leads where Lead_Source = 'Phone' and Created_Time >= '{since_90}'")
    q("Leads.website_source_90d", f"select COUNT(id) from Leads where Lead_Source = 'Website' and Created_Time >= '{since_90}'")
    q("Leads.google_source_90d", f"select COUNT(id) from Leads where Lead_Source = 'Google' and Created_Time >= '{since_90}'")
    q("Leads.junk_90d", f"select COUNT(id) from Leads where Lead_Status = 'Junk Lead' and Created_Time >= '{since_90}'")
    q(
        "Leads.jo_submitted_90d",
        f"select COUNT(id) from Leads where Lead_Status = 'Job Order Submitted' and Created_Time >= '{since_90}'",
    )
    q(
        "Leads.new_auto_14d",
        f"select COUNT(id) from Leads where Lead_Status = 'New Enquiry (Auto)' and Created_Time >= '{since_14}'",
    )

    q(
        "Job_Orders.stage_90d",
        f"select Stage, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Stage",
    )
    q(
        "Job_Orders.region_90d",
        f"select Region, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Region",
    )
    q("Job_Orders.gclid_all", "select COUNT(id) from Job_Orders where UTM_Gclid is not null")
    q(
        "Job_Orders.linked_enquiry_90d",
        f"select COUNT(id) from Job_Orders where Client_Name is not null and Created_Time >= '{since_90}'",
    )
    q(
        "Job_Orders.unlinked_90d",
        f"select COUNT(id) from Job_Orders where Client_Name is null and Created_Time >= '{since_90}'",
    )
    q("Job_Orders.recruit_all", "select COUNT(id) from Job_Orders where Recruit_Job_Opening_ID is not null")

    q("Deals.stage_90d", f"select Stage, COUNT(id) from Deals where Created_Time >= '{since_90}' group by Stage")
    q("Deals.region_90d", f"select Region, COUNT(id) from Deals where Created_Time >= '{since_90}' group by Region")

    q(
        "Calls.type_90d",
        f"select Call_Type, COUNT(id) from Calls where Created_Time >= '{since_90}' group by Call_Type",
    )

    # --- record samples ---
    lead_fields = (
        "id,First_Name,Last_Name,Company,Email,Phone,Lead_Source,Lead_Status,Created_Time,Created_By,"
        "Owner,Region,Country,Form_Source,utm_source,utm_medium,utm_campaign,utm_term,utm_content,"
        "utm_gclid,Campaign_Name,Gravity_Form_Entry_ID,Referring_URL,Referrer,Website,"
        "Submission_Timestamp,Job_Position_Required,Other_Client_Profile_Information,"
        "Converted__s,Converted_Account,Converted_Contact,Converted_Deal,Account,"
        "Job_Order_submitted_via_form,Tag"
    )
    jo_fields = (
        "id,Name,Job_Title,Stage,Created_Time,Created_By,Owner,Region,Client_Name,Linked_Sales_Enquiry,"
        "Linked_Account,UTM_Gclid,UTM_Source,UTM_Medium,UTM_Campaign,UTM_Term,Client_Status,"
        "Recruit_Job_Opening_ID,Last_Sync_Source,Company_Name,Company_Website"
    )
    deal_fields = (
        "id,Deal_Name,Stage,Lead_Source,Created_Time,Created_By,Owner,Region,Account_Name,"
        "Contact_Name,Contract_Invoice_Status,Amount,Closing_Date"
    )
    call_fields = (
        "id,Subject,Call_Type,Call_Duration,Call_Start_Time,Created_Time,Created_By,Owner,"
        "Who_Id,What_Id,Call_Result,Description"
    )
    task_fields = "id,Subject,Status,Priority,Due_Date,Created_Time,Owner,Who_Id,What_Id,Description,Closed_Time"

    samples_spec = [
        ("Leads", lead_fields, 200),
        ("Job_Orders", jo_fields, 100),
        ("Deals", deal_fields, 80),
        ("Calls", call_fields, 80),
        ("Tasks", task_fields, 80),
    ]
    for mod, fields, per_page in samples_spec:
        if STOPPED:
            break
        st, body = get(
            crm_url(
                api,
                f"/{mod}?per_page={per_page}&sort_by=Created_Time&sort_order=desc&fields={quote(fields)}",
            ),
            token,
        )
        recs = body.get("data") if isinstance(body, dict) else None
        if st != 200 or not isinstance(recs, list):
            out["samples"][mod] = {
                "http": st,
                "error": redact(body.get("message") if isinstance(body, dict) else str(body)[:180]),
            }
            print(f"sample {mod}: http={st}")
            continue
        recs = [r for r in recs if isinstance(r, dict)]
        if mod == "Leads":
            summary = summarize_enquiries(recs)
            # also split 14d vs older in this newest-N sample
            cutoff = since_14
            recent = [r for r in recs if str(r.get("Created_Time") or "") >= cutoff]
            summary["in_sample_created_since_14d"] = summarize_enquiries(recent) if recent else {"n": 0}
        elif mod == "Job_Orders":
            stages = Counter(str(r.get("Stage") or "(blank)") for r in recs)
            linked = sum(1 for r in recs if filled(r.get("Client_Name")))
            gclid = sum(1 for r in recs if filled(r.get("UTM_Gclid")))
            names = Counter()
            preview = []
            for r in recs:
                names[str(r.get("Name") or r.get("Job_Title") or "")[:40]] += 1
                preview.append(
                    {
                        "created": str(r.get("Created_Time") or "")[:19],
                        "name": str(r.get("Name") or r.get("Job_Title") or "")[:40],
                        "stage": str(r.get("Stage") or "")[:36],
                        "region": str(r.get("Region") or "")[:12],
                        "owner": name_of(r.get("Owner"))[:28],
                        "created_by": name_of(r.get("Created_By"))[:28],
                        "has_client_lookup": filled(r.get("Client_Name")),
                        "linked_enquiry_text": bool(filled(r.get("Linked_Sales_Enquiry"))),
                        "has_gclid": filled(r.get("UTM_Gclid")),
                        "utm_source": str(r.get("UTM_Source") or "")[:24],
                        "client_status": str(r.get("Client_Status") or "")[:24],
                        "recruit_id": filled(r.get("Recruit_Job_Opening_ID")),
                    }
                )
            summary = {
                "n": len(recs),
                "stages": dict(stages.most_common(20)),
                "linked_client_name": linked,
                "unlinked_client_name": len(recs) - linked,
                "has_gclid": gclid,
                "duplicate_names_in_sample": sum(1 for n in names.values() if n > 1),
                "preview": preview[:20],
            }
        elif mod == "Deals":
            stages = Counter(str(r.get("Stage") or "(blank)") for r in recs)
            regions = Counter(str(r.get("Region") or "(blank)") for r in recs)
            invoice = Counter(str(r.get("Contract_Invoice_Status") or "(blank)") for r in recs)
            has_account = sum(1 for r in recs if filled(r.get("Account_Name")))
            has_contact = sum(1 for r in recs if filled(r.get("Contact_Name")))
            preview = [
                {
                    "created": str(r.get("Created_Time") or "")[:19],
                    "name": str(r.get("Deal_Name") or "")[:40],
                    "stage": str(r.get("Stage") or "")[:36],
                    "region": str(r.get("Region") or "")[:12],
                    "owner": name_of(r.get("Owner"))[:28],
                    "has_account": filled(r.get("Account_Name")),
                    "has_contact": filled(r.get("Contact_Name")),
                    "invoice_status": str(r.get("Contract_Invoice_Status") or "")[:28],
                    "lead_source": str(r.get("Lead_Source") or "")[:24],
                }
                for r in recs[:20]
            ]
            summary = {
                "n": len(recs),
                "stages": dict(stages.most_common(20)),
                "regions": dict(regions),
                "invoice_status": dict(invoice.most_common(12)),
                "has_account": has_account,
                "has_contact": has_contact,
                "preview": preview,
            }
        elif mod == "Calls":
            types = Counter(str(r.get("Call_Type") or "(blank)") for r in recs)
            results = Counter(str(r.get("Call_Result") or "(blank)")[:40] for r in recs)
            who = sum(1 for r in recs if filled(r.get("Who_Id")))
            what = sum(1 for r in recs if filled(r.get("What_Id")))
            gclid_in_desc = 0
            preview = []
            for r in recs:
                desc = str(r.get("Description") or "")
                if "gclid" in desc.lower():
                    gclid_in_desc += 1
                preview.append(
                    {
                        "created": str(r.get("Created_Time") or "")[:19],
                        "subject": str(r.get("Subject") or "")[:50],
                        "type": str(r.get("Call_Type") or "")[:16],
                        "duration": str(r.get("Call_Duration") or "")[:12],
                        "result": str(r.get("Call_Result") or "")[:30],
                        "owner": name_of(r.get("Owner"))[:28],
                        "has_who": filled(r.get("Who_Id")),
                        "who": name_of(r.get("Who_Id"))[:28],
                        "has_what": filled(r.get("What_Id")),
                        "what": name_of(r.get("What_Id"))[:28],
                    }
                )
            summary = {
                "n": len(recs),
                "types": dict(types),
                "results": dict(results.most_common(15)),
                "linked_who": who,
                "linked_what": what,
                "gclid_in_description": gclid_in_desc,
                "preview": preview[:15],
            }
        else:
            statuses = Counter(str(r.get("Status") or "(blank)") for r in recs)
            who = sum(1 for r in recs if filled(r.get("Who_Id")))
            what = sum(1 for r in recs if filled(r.get("What_Id")))
            preview = [
                {
                    "created": str(r.get("Created_Time") or "")[:19],
                    "subject": str(r.get("Subject") or "")[:50],
                    "status": str(r.get("Status") or "")[:24],
                    "due": str(r.get("Due_Date") or "")[:19],
                    "owner": name_of(r.get("Owner"))[:28],
                    "has_who": filled(r.get("Who_Id")),
                    "has_what": filled(r.get("What_Id")),
                }
                for r in recs[:15]
            ]
            summary = {
                "n": len(recs),
                "statuses": dict(statuses.most_common(15)),
                "linked_who": who,
                "linked_what": what,
                "preview": preview,
            }
        summary["http"] = st
        out["samples"][mod] = summary
        print(f"sample {mod}: n={summary.get('n')}")

    # Related lists on a few newest Leads / Job Orders (IDs only, redacted elsewhere)
    lead_ids: list[str] = []
    st, body = get(
        crm_url(api, "/Leads?per_page=5&sort_by=Created_Time&sort_order=desc&fields=id,Company,Lead_Status,Lead_Source"),
        token,
    )
    if isinstance(body, dict):
        for r in body.get("data") or []:
            if isinstance(r, dict) and r.get("id"):
                lead_ids.append(str(r["id"]))
    rel_names = ["Notes", "Calls", "Tasks", "Emails", "Attachments"]
    for lid in lead_ids[:3]:
        rec: dict[str, Any] = {"lead_id_suffix": lid[-6:], "related": {}}
        for rel in rel_names:
            if STOPPED:
                break
            st, body = get(crm_url(api, f"/Leads/{lid}/{rel}"), token)
            n = 0
            err = None
            sample_subj = []
            if st == 200 and isinstance(body, dict):
                rows = body.get("data") or []
                n = len(rows) if isinstance(rows, list) else 0
                for row in (rows or [])[:3]:
                    if isinstance(row, dict):
                        sample_subj.append(
                            {
                                "subject": str(row.get("Subject") or row.get("Note_Title") or row.get("File_Name") or "")[:50],
                                "created": str(row.get("Created_Time") or "")[:19],
                                "owner": name_of(row.get("Owner"))[:24],
                            }
                        )
            else:
                err = redact(body.get("message") if isinstance(body, dict) else str(body)[:120])
            rec["related"][rel] = {"http": st, "n": n, "error": err, "sample": sample_subj}
        out["related_samples"][lid[-6:]] = rec
        print(f"related lead …{lid[-6:]}: { {k: v.get('http') for k, v in rec['related'].items()} }")

    jo_ids: list[str] = []
    st, body = get(
        crm_url(api, "/Job_Orders?per_page=3&sort_by=Created_Time&sort_order=desc&fields=id,Name,Stage,Client_Name"),
        token,
    )
    if isinstance(body, dict):
        for r in body.get("data") or []:
            if isinstance(r, dict) and r.get("id"):
                jo_ids.append(str(r["id"]))
    for jid in jo_ids[:2]:
        rec = {"jo_id_suffix": jid[-6:], "related": {}}
        for rel in ("Notes", "Calls", "Tasks"):
            if STOPPED:
                break
            st, body = get(crm_url(api, f"/Job_Orders/{jid}/{rel}"), token)
            n = 0
            err = None
            if st == 200 and isinstance(body, dict):
                rows = body.get("data") or []
                n = len(rows) if isinstance(rows, list) else 0
            else:
                err = redact(body.get("message") if isinstance(body, dict) else str(body)[:120])
            rec["related"][rel] = {"http": st, "n": n, "error": err}
        out["related_samples"][f"jo_{jid[-6:]}"] = rec

    out["calls"] = CALLS
    out["stopped"] = STOPPED
    write_json(LOCAL_ZOHO / "audit-lead-to-placement-2026-08-18.json", out)
    print(f"calls={CALLS} stopped={STOPPED} wrote audit-lead-to-placement-2026-08-18.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
