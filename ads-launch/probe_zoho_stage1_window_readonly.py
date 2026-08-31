#!/usr/bin/env python3
"""Read-only Zoho COQL for Stage 1 window (2026-08-06 .. today).

Hard rules:
- GET + COQL SELECT only. Never create/update/delete.
- Never print tokens, emails, phones, or raw click IDs.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "zoho"))
from _common import (  # noqa: E402
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    load_credentials,
    refresh_access_token,
    write_json,
)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().\-]{7,}\d)")
CALLS = 0
MAX_CALLS = 18
STOPPED = None

STAGE1_START = "2026-08-06T00:00:00+00:00"
# Brisbane lag buffer: also count Modified_Time in window separately if needed.
OUT_NAME = "probe-stage1-window-2026-08-14.json"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def redact(s: Any) -> Any:
    if isinstance(s, str):
        s = EMAIL_RE.sub("[email]", s)
        s = PHONE_RE.sub("[phone]", s)
        return s
    if isinstance(s, dict):
        return {k: redact(v) for k, v in s.items()}
    if isinstance(s, list):
        return [redact(x) for x in s]
    return s


def name_of(obj: Any) -> str:
    if isinstance(obj, dict):
        return str(obj.get("name") or "")
    return str(obj or "")


def click_present(val: Any) -> bool:
    return bool(val) and str(val).strip() not in ("", "null", "None")


def post_json(url: str, token: str, payload: dict[str, Any]) -> tuple[int, Any]:
    global CALLS, STOPPED
    CALLS += 1
    if CALLS > MAX_CALLS:
        STOPPED = "cap"
        return 0, {"error": "cap"}
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
        with urllib.request.urlopen(req, timeout=45) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.getcode() or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
        if status in (429, 403) or "RATE" in raw.upper() or "LIMIT" in raw.upper():
            STOPPED = f"rate {status}"
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, {"raw": raw[:200]}


def count_val(body: Any) -> int | None:
    if not isinstance(body, dict):
        return None
    data = body.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        row = data[0]
        for _k, v in row.items():
            try:
                return int(v)
            except (TypeError, ValueError):
                continue
    return None


def rows_of(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


def host_of(url: Any) -> str:
    s = str(url or "").strip()
    if not s:
        return ""
    s = s.replace("https://", "").replace("http://", "")
    return s.split("/")[0][:64]


def sanitize_lead(rec: dict[str, Any]) -> dict[str, Any]:
    gclid = rec.get("utm_gclid") or ""
    website = str(rec.get("Website") or "")
    referrer = str(rec.get("Referrer") or rec.get("Referring_URL") or "")
    camp = str(rec.get("Campaign_Name") or rec.get("utm_campaign") or "")
    return {
        "created": str(rec.get("Created_Time") or "")[:19],
        "submission_ts": str(rec.get("Submission_Timestamp") or "")[:19],
        "region": str(rec.get("Region") or "")[:16],
        "status": str(rec.get("Lead_Status") or "")[:48],
        "source": str(rec.get("Lead_Source") or "")[:32],
        "form_source": str(rec.get("Form_Source") or "")[:40],
        "utm_source": str(rec.get("utm_source") or "")[:32],
        "utm_medium": str(rec.get("utm_medium") or "")[:32],
        "utm_campaign": str(rec.get("utm_campaign") or "")[:48],
        "campaign_name": camp[:48],
        "created_by": name_of(rec.get("Created_By"))[:32],
        "has_gclid": click_present(gclid),
        "gclid_len": len(str(gclid)) if click_present(gclid) else 0,
        "website_host": host_of(website),
        "referrer_host": host_of(referrer),
        "looks_app_host": "virtualcoworker.app" in f"{website} {referrer}".lower(),
        "looks_vc_campaign": "VC_" in camp.upper() or "vc_us" in camp.lower() or "vc_au" in camp.lower(),
        "company": str(rec.get("Company") or "")[:40],
    }


def sanitize_jo(rec: dict[str, Any]) -> dict[str, Any]:
    gclid = rec.get("UTM_Gclid") or ""
    camp = str(rec.get("UTM_Campaign") or "")
    return {
        "created": str(rec.get("Created_Time") or "")[:19],
        "region": str(rec.get("Region") or "")[:16],
        "stage": str(rec.get("Stage") or "")[:48],
        "utm_source": str(rec.get("UTM_Source") or "")[:32],
        "utm_campaign": camp[:48],
        "created_by": name_of(rec.get("Created_By"))[:32],
        "has_gclid": click_present(gclid),
        "gclid_len": len(str(gclid)) if click_present(gclid) else 0,
        "has_enquiry_lookup": bool(name_of(rec.get("Client_Name"))),
        "looks_vc_campaign": "VC_" in camp.upper(),
        "company": str(rec.get("Company_Name") or rec.get("Name") or "")[:40],
    }


def aggregate_leads(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_region: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_source: dict[str, int] = {}
    by_utm: dict[str, int] = {}
    by_form: dict[str, int] = {}
    by_creator: dict[str, int] = {}
    hosts: dict[str, int] = {}
    camps: dict[str, int] = {}
    gclid_n = 0
    app_n = 0
    vc_camp_n = 0
    googleish_source = 0
    googleish_utm = 0
    blank_attr = 0
    discovery = 0
    for r in rows:
        region = r.get("region") or "(blank)"
        by_region[region] = by_region.get(region, 0) + 1
        st = r.get("status") or "(blank)"
        by_status[st] = by_status.get(st, 0) + 1
        src = r.get("source") or "(blank)"
        by_source[src] = by_source.get(src, 0) + 1
        utm = r.get("utm_source") or "(blank)"
        by_utm[utm] = by_utm.get(utm, 0) + 1
        form = r.get("form_source") or "(blank)"
        by_form[form] = by_form.get(form, 0) + 1
        creator = r.get("created_by") or "(blank)"
        by_creator[creator] = by_creator.get(creator, 0) + 1
        wh = r.get("website_host") or r.get("referrer_host") or "(blank)"
        hosts[wh] = hosts.get(wh, 0) + 1
        camp = r.get("campaign_name") or r.get("utm_campaign") or "(blank)"
        camps[camp] = camps.get(camp, 0) + 1
        if r.get("has_gclid"):
            gclid_n += 1
        if r.get("looks_app_host"):
            app_n += 1
        if r.get("looks_vc_campaign"):
            vc_camp_n += 1
        if str(src).lower() in {"google", "googleads", "google ads"}:
            googleish_source += 1
        if str(utm).lower() in {"google", "googleads", "google ads"}:
            googleish_utm += 1
        if (
            not r.get("has_gclid")
            and not str(src).strip()
            and not str(utm).strip()
            and not str(camp).strip()
        ) or (
            not r.get("has_gclid")
            and str(src).lower() in {"", "website", "(blank)"}
            and str(utm).lower() in {"", "(blank)", "(direct)", "direct"}
            and not r.get("looks_vc_campaign")
        ):
            blank_attr += 1
        if "discovery scheduled" in str(st).lower():
            discovery += 1
    return {
        "n": len(rows),
        "by_region": dict(sorted(by_region.items(), key=lambda x: (-x[1], x[0]))),
        "by_status": dict(sorted(by_status.items(), key=lambda x: (-x[1], x[0]))),
        "by_source": dict(sorted(by_source.items(), key=lambda x: (-x[1], x[0]))),
        "by_utm_source": dict(sorted(by_utm.items(), key=lambda x: (-x[1], x[0]))),
        "by_form_source": dict(sorted(by_form.items(), key=lambda x: (-x[1], x[0]))),
        "by_created_by": dict(sorted(by_creator.items(), key=lambda x: (-x[1], x[0]))),
        "hosts_top": dict(sorted(hosts.items(), key=lambda x: (-x[1], x[0]))[:12]),
        "campaigns_top": dict(sorted(camps.items(), key=lambda x: (-x[1], x[0]))[:15]),
        "with_utm_gclid": gclid_n,
        "looks_app_host": app_n,
        "looks_vc_campaign": vc_camp_n,
        "lead_source_googleish": googleish_source,
        "utm_source_googleish": googleish_utm,
        "blank_or_weak_attribution": blank_attr,
        "discovery_scheduled": discovery,
    }


def main() -> int:
    load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    ensure_local_dir()
    creds = load_credentials()
    token = str(refresh_access_token(creds)["access_token"])
    api = creds["api_domain"]
    coql = crm_url(api, "/coql")
    now = datetime.now(timezone.utc)
    out: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "window_start": STAGE1_START,
        "window_note": "Stage 1 paid Search approx VC_* live; Created_Time >= 2026-08-06 UTC",
        "queries": {},
        "aggregates": {},
        "samples": {},
        "calls": 0,
        "stopped_reason": None,
        "read_only": True,
    }

    def q(label: str, sql: str, *, sample: bool = False) -> Any:
        global STOPPED
        if STOPPED:
            out["queries"][label] = {"skipped": STOPPED, "sql": sql}
            print(f"{label}: skipped ({STOPPED})")
            return out["queries"][label]
        st, body = post_json(coql, token, {"select_query": sql})
        rec: dict[str, Any] = {"http": st, "sql": sql}
        if st != 200:
            rec["error"] = redact(body.get("message") if isinstance(body, dict) else str(body)[:180])
        elif sample or ("limit" in sql.lower() and "count(" not in sql.lower()):
            rec["n"] = len(rows_of(body))
            rec["rows_raw_n"] = rec["n"]
        else:
            rec["count"] = count_val(body)
        out["queries"][label] = rec
        print(f"{label}: http={st} count={rec.get('count')} n={rec.get('n')} err={str(rec.get('error', ''))[:100]}")
        return rec, body if st == 200 else None

    # Cheap counts first
    q(
        "Leads.stage1_total",
        f"select COUNT(id) from Leads where Created_Time >= '{STAGE1_START}'",
    )
    q(
        "Leads.stage1_gclid",
        f"select COUNT(id) from Leads where Created_Time >= '{STAGE1_START}' and utm_gclid is not null",
    )
    q(
        "Leads.stage1_usa",
        f"select COUNT(id) from Leads where Created_Time >= '{STAGE1_START}' and Region = 'USA'",
    )
    q(
        "Leads.stage1_au",
        f"select COUNT(id) from Leads where Created_Time >= '{STAGE1_START}' and Region = 'AU'",
    )
    q(
        "Leads.stage1_discovery",
        f"select COUNT(id) from Leads where Created_Time >= '{STAGE1_START}' and Lead_Status = 'Discovery Scheduled'",
    )
    q(
        "Leads.stage1_source_google",
        f"select COUNT(id) from Leads where Created_Time >= '{STAGE1_START}' and Lead_Source = 'Google'",
    )
    q(
        "Job_Orders.stage1_total",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{STAGE1_START}'",
    )
    q(
        "Job_Orders.stage1_gclid",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{STAGE1_START}' and UTM_Gclid is not null",
    )
    q(
        "Job_Orders.stage1_usa",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{STAGE1_START}' and Region = 'USA'",
    )
    q(
        "Job_Orders.stage1_au",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{STAGE1_START}' and Region = 'AU'",
    )

    # Pull rows for attribution signals (cap 200; Stage 1 window should be small)
    lead_fields = (
        "id, Created_Time, Submission_Timestamp, Region, Lead_Status, Company, Lead_Source, "
        "Form_Source, utm_source, utm_medium, utm_campaign, Campaign_Name, Website, Referrer, "
        "Referring_URL, Created_By, utm_gclid"
    )
    leads_all: list[dict[str, Any]] = []
    for page_label, offset in (("Leads.stage1_page1", 0), ("Leads.stage1_page2", 200)):
        if STOPPED:
            break
        # COQL offset via limit N offset M not always supported; use Created_Time paging if needed.
        if offset == 0:
            sql = (
                f"select {lead_fields} from Leads where Created_Time >= '{STAGE1_START}' "
                f"order by Created_Time desc limit 200"
            )
        else:
            # Only fetch page2 if page1 was full
            if len(leads_all) < 200:
                break
            oldest = leads_all[-1].get("created")
            if not oldest:
                break
            sql = (
                f"select {lead_fields} from Leads where Created_Time >= '{STAGE1_START}' "
                f"and Created_Time < '{oldest}' order by Created_Time desc limit 200"
            )
        _rec, body = q(page_label, sql, sample=True)
        if not body:
            break
        rows = [sanitize_lead(r) for r in rows_of(body)]
        leads_all.extend(rows)
        out["queries"][page_label]["n"] = len(rows)

    jo_fields = (
        "id, Created_Time, Region, Stage, UTM_Source, UTM_Campaign, Created_By, "
        "Name, Company_Name, Client_Name, UTM_Gclid"
    )
    _rec, body = q(
        "Job_Orders.stage1_rows",
        f"select {jo_fields} from Job_Orders where Created_Time >= '{STAGE1_START}' "
        f"order by Created_Time desc limit 200",
        sample=True,
    )
    jos = [sanitize_jo(r) for r in rows_of(body)] if body else []

    out["samples"]["leads"] = leads_all  # company names only; no email/phone
    out["samples"]["job_orders"] = jos
    out["aggregates"]["leads"] = aggregate_leads(leads_all)
    out["aggregates"]["job_orders"] = {
        "n": len(jos),
        "by_region": {},
        "by_stage": {},
        "with_utm_gclid": sum(1 for r in jos if r.get("has_gclid")),
        "looks_vc_campaign": sum(1 for r in jos if r.get("looks_vc_campaign")),
        "utm_source_googleish": sum(
            1 for r in jos if str(r.get("utm_source") or "").lower() in {"google", "googleads", "google ads"}
        ),
    }
    for r in jos:
        region = r.get("region") or "(blank)"
        out["aggregates"]["job_orders"]["by_region"][region] = (
            out["aggregates"]["job_orders"]["by_region"].get(region, 0) + 1
        )
        stage = r.get("stage") or "(blank)"
        out["aggregates"]["job_orders"]["by_stage"][stage] = (
            out["aggregates"]["job_orders"]["by_stage"].get(stage, 0) + 1
        )

    # Confidence buckets for Stage 1 story (honest)
    buckets = {
        "paid_strong_gclid": 0,
        "paid_weak_google_utm_or_source_no_gclid": 0,
        "vc_campaign_name": 0,
        "app_host": 0,
        "blank_or_website_only": 0,
        "discovery_scheduled_total": 0,
        "discovery_scheduled_with_gclid": 0,
        "discovery_scheduled_googleish_no_gclid": 0,
        "by_market": {
            "USA": {"total": 0, "gclid": 0, "googleish_no_gclid": 0, "blankish": 0, "discovery": 0},
            "AU": {"total": 0, "gclid": 0, "googleish_no_gclid": 0, "blankish": 0, "discovery": 0},
            "(blank/other)": {"total": 0, "gclid": 0, "googleish_no_gclid": 0, "blankish": 0, "discovery": 0},
        },
    }
    for r in leads_all:
        market = r.get("region") if r.get("region") in ("USA", "AU") else "(blank/other)"
        m = buckets["by_market"][market]
        m["total"] += 1
        googleish = (
            str(r.get("source") or "").lower() in {"google", "googleads", "google ads"}
            or str(r.get("utm_source") or "").lower() in {"google", "googleads", "google ads"}
        )
        if r.get("has_gclid"):
            buckets["paid_strong_gclid"] += 1
            m["gclid"] += 1
        elif googleish:
            buckets["paid_weak_google_utm_or_source_no_gclid"] += 1
            m["googleish_no_gclid"] += 1
        else:
            buckets["blank_or_website_only"] += 1
            m["blankish"] += 1
        if r.get("looks_vc_campaign"):
            buckets["vc_campaign_name"] += 1
        if r.get("looks_app_host"):
            buckets["app_host"] += 1
        if "discovery scheduled" in str(r.get("status") or "").lower():
            buckets["discovery_scheduled_total"] += 1
            m["discovery"] += 1
            if r.get("has_gclid"):
                buckets["discovery_scheduled_with_gclid"] += 1
            elif googleish:
                buckets["discovery_scheduled_googleish_no_gclid"] += 1

    out["aggregates"]["confidence_buckets"] = buckets
    out["calls"] = CALLS
    out["stopped_reason"] = STOPPED
    write_json(LOCAL_ZOHO / OUT_NAME, out)
    print(f"\nWrote {LOCAL_ZOHO / OUT_NAME} calls={CALLS} stopped={STOPPED}")
    print(json.dumps({"counts": {k: v.get("count") for k, v in out["queries"].items() if "count" in v}, "agg": out["aggregates"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
