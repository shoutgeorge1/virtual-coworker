#!/usr/bin/env python3
"""Read-only Zoho gap probe for the Job Order / Placement Ads pipeline audit.

Hard rules:
- GET + COQL SELECT only. Never create/update/delete/upsert/convert.
- Never print tokens, emails, phones, or raw click IDs.
- Cap API volume. Stop on rate limit.
- Does not set ZOHO_CRM_ENABLED or ZOHO_SUBMISSION_ENABLED.
- Does not call Google Ads.
- Does not move or inspect [TEST] rows beyond GET-by-id status.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
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
MAX_CALLS = 55
CALLS = 0
STOPPED: str | None = None
EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().\-]{7,}\d)")
TEST_IDS = (
    "6724032000029820001",
    "6724032000029822001",
    "6724032000029823001",
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
    since_90 = (now - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00+00:00")
    since_30 = (now - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00+00:00")

    out: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "api_version": "v8",
        "windows": {"90d": since_90, "30d": since_30},
        "queries": {},
        "settings": {},
        "test_records": {},
        "samples": {},
        "stopped": None,
    }

    def q(label: str, sql: str, *, group_key: str | None = None) -> dict[str, Any]:
        st, body = coql(coql_url, token, sql)
        rec: dict[str, Any] = {"http": st, "sql": sql}
        if st != 200:
            rec["error"] = redact(body.get("message") if isinstance(body, dict) else str(body)[:220])
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

    setting_paths = [
        ("layouts_Leads", "/settings/layouts?module=Leads"),
        ("layouts_Job_Orders", "/settings/layouts?module=Job_Orders"),
        ("layouts_Deals", "/settings/layouts?module=Deals"),
        ("pipelines_Deals", "/settings/pipelines?module=Deals"),
        ("pipelines_Job_Orders", "/settings/pipelines?module=Job_Orders"),
        ("blueprints", "/settings/blueprints"),
        ("automation_rules_Leads", "/settings/automation/rules?module=Leads"),
        ("automation_rules_Job_Orders", "/settings/automation/rules?module=Job_Orders"),
        ("automation_rules_Deals", "/settings/automation/rules?module=Deals"),
        ("webhooks", "/settings/automation/webhooks"),
        ("functions", "/settings/functions"),
        ("workflow_actions", "/settings/automation/actions"),
    ]
    for label, path in setting_paths:
        if STOPPED:
            break
        st, body = get(crm_url(api, path), token)
        brief: dict[str, Any] = {"http": st, "path": path}
        if st != 200:
            brief["error"] = redact(body.get("message") if isinstance(body, dict) else str(body)[:180])
        elif isinstance(body, dict):
            for key in (
                "layouts",
                "pipelines",
                "blueprints",
                "workflow_rules",
                "rules",
                "webhooks",
                "functions",
                "actions",
            ):
                rows = body.get(key)
                if isinstance(rows, list):
                    brief[key] = [
                        {
                            "name": r.get("name") or r.get("display_label") or r.get("api_name"),
                            "id_suffix": str(r.get("id") or "")[-6:],
                            "status": r.get("status") or r.get("active"),
                            "module": (
                                (r.get("module") or {}).get("api_name")
                                if isinstance(r.get("module"), dict)
                                else r.get("module")
                            ),
                            "source": r.get("source") or r.get("generated_type"),
                        }
                        for r in rows
                        if isinstance(r, dict)
                    ][:80]
                    brief["n"] = len(rows)
        out["settings"][label] = brief
        print(f"settings {label}: http={st} n={brief.get('n')} err={str(brief.get('error') or '')[:60]}")

    for tid in TEST_IDS:
        if STOPPED:
            break
        st, body = get(
            crm_url(
                api,
                f"/Leads/{tid}?fields=id,Company,Lead_Status,Form_Source,utm_gclid,Region,Converted__s",
            ),
            token,
        )
        rec = {"http": st, "id_suffix": tid[-6:]}
        if st == 200 and isinstance(body, dict) and body.get("data"):
            row = body["data"][0]
            rec.update(
                {
                    "company": str(row.get("Company") or "")[:50],
                    "status": str(row.get("Lead_Status") or ""),
                    "form_source": str(row.get("Form_Source") or "")[:40],
                    "region": str(row.get("Region") or ""),
                    "has_gclid": filled(row.get("utm_gclid")),
                    "converted": bool(row.get("Converted__s")),
                }
            )
        else:
            rec["error"] = redact(body.get("message") if isinstance(body, dict) else str(body)[:160])
        out["test_records"][tid] = rec
        print(f"test {tid[-6:]}: http={st} status={rec.get('status')} company={rec.get('company')}")

    q("Leads.90d", f"select COUNT(id) from Leads where Created_Time >= '{since_90}'")
    q("Leads.email_90d", f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Email is not null")
    q("Leads.phone_90d", f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Phone is not null")
    q("Leads.gclid_90d", f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and utm_gclid is not null")
    q(
        "Leads.no_email_phone_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Email is null and Phone is null",
    )
    q(
        "Leads.unmatchable_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Email is null and Phone is null and utm_gclid is null",
    )
    q("Leads.no_company_90d", f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Company is null")
    q(
        "Leads.no_followup_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Next_Follow_Up_Date is null",
    )
    q(
        "Leads.opt_out_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Email_Opt_Out = true",
    )
    q(
        "Leads.status_90d",
        f"select Lead_Status, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Lead_Status",
    )
    q(
        "Leads.region_90d",
        f"select Region, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Region",
    )
    q(
        "Leads.jo_status_usa_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Lead_Status = 'Job Order Submitted' and Region = 'USA'",
    )
    q(
        "Leads.jo_status_au_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Lead_Status = 'Job Order Submitted' and Region = 'AU'",
    )
    q(
        "Leads.discovery_90d",
        f"select COUNT(id) from Leads where Created_Time >= '{since_90}' and Lead_Status = 'Discovery Scheduled'",
    )
    q("Job_Orders.90d", f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}'")
    q(
        "Job_Orders.email_90d",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and Email is not null",
    )
    q(
        "Job_Orders.phone_90d",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and Phone_1 is not null",
    )
    q(
        "Job_Orders.gclid_90d",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and UTM_Gclid is not null",
    )
    q(
        "Job_Orders.no_email_phone_90d",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and Email is null and Phone_1 is null",
    )
    q(
        "Job_Orders.unlinked_90d",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and Client_Name is null",
    )
    q(
        "Job_Orders.stage_placement_90d",
        f"select COUNT(id) from Job_Orders where Created_Time >= '{since_90}' and Stage = 'Placement'",
    )
    q(
        "Job_Orders.client_status_90d",
        f"select Client_Status, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Client_Status",
    )
    q("Deals.90d", f"select COUNT(id) from Deals where Created_Time >= '{since_90}'")
    q(
        "Deals.work_email_90d",
        f"select COUNT(id) from Deals where Created_Time >= '{since_90}' and Work_Email is not null",
    )
    q(
        "Deals.personal_email_90d",
        f"select COUNT(id) from Deals where Created_Time >= '{since_90}' and Personal_Email is not null",
    )
    q(
        "Deals.no_account_90d",
        f"select COUNT(id) from Deals where Created_Time >= '{since_90}' and Account_Name is null",
    )
    q(
        "Deals.no_contact_90d",
        f"select COUNT(id) from Deals where Created_Time >= '{since_90}' and Contact_Name is null",
    )
    q(
        "Deals.region_blank_90d",
        f"select COUNT(id) from Deals where Created_Time >= '{since_90}' and Region is null",
    )
    q("Deals.stage_90d", f"select Stage, COUNT(id) from Deals where Created_Time >= '{since_90}' group by Stage")

    samples = [
        (
            "Leads",
            "id,Company,Lead_Status,Lead_Source,Region,Owner,Created_Time,Form_Source,"
            "utm_gclid,utm_source,Email,Phone,Next_Follow_Up_Date,Email_Opt_Out",
        ),
        (
            "Job_Orders",
            "id,Name,Stage,Region,Owner,Created_Time,Client_Name,Client_Status,"
            "UTM_Gclid,Email,Phone_1,Company_Name",
        ),
        (
            "Deals",
            "id,Deal_Name,Stage,Region,Owner,Created_Time,Account_Name,Contact_Name,"
            "Work_Email,Personal_Email,Contract_Invoice_Status,Start_Date",
        ),
    ]
    for mod, fields in samples:
        if STOPPED:
            break
        st, body = get(
            crm_url(
                api,
                f"/{mod}?per_page=30&sort_by=Created_Time&sort_order=desc&fields={quote(fields)}",
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
        preview = []
        enquiry_ids: list[str] = []
        for r in recs:
            row = {
                "created": str(r.get("Created_Time") or "")[:19],
                "status": str(r.get("Lead_Status") or r.get("Stage") or "")[:40],
                "region": str(r.get("Region") or "")[:12],
                "owner": name_of(r.get("Owner"))[:28],
                "has_email": filled(r.get("Email") or r.get("Work_Email") or r.get("Personal_Email")),
                "has_phone": filled(r.get("Phone") or r.get("Phone_1")),
                "has_gclid": filled(r.get("utm_gclid") or r.get("UTM_Gclid")),
                "has_followup": filled(r.get("Next_Follow_Up_Date")),
                "opt_out": bool(r.get("Email_Opt_Out")),
                "has_account": filled(r.get("Account_Name")),
                "has_contact": filled(r.get("Contact_Name")),
                "has_client_lookup": filled(r.get("Client_Name")),
                "client_status": str(r.get("Client_Status") or "")[:24],
                "form_source": str(r.get("Form_Source") or "")[:32],
                "name": str(r.get("Company") or r.get("Name") or r.get("Deal_Name") or "")[:36],
            }
            preview.append(row)
            cid = r.get("Client_Name")
            if isinstance(cid, dict) and cid.get("id"):
                enquiry_ids.append(str(cid["id"]))
        extra: dict[str, Any] = {}
        if mod == "Job_Orders":
            extra["duplicate_enquiry_lookups_in_30"] = sum(
                1 for n in Counter(enquiry_ids).values() if n > 1
            )
            extra["unique_enquiry_lookups_in_30"] = len(set(enquiry_ids))
        extra["n"] = len(recs)
        extra["http"] = st
        extra["with_email"] = sum(1 for p in preview if p["has_email"])
        extra["with_phone"] = sum(1 for p in preview if p["has_phone"])
        extra["with_gclid"] = sum(1 for p in preview if p["has_gclid"])
        extra["no_click_no_email_no_phone"] = sum(
            1 for p in preview if not p["has_gclid"] and not p["has_email"] and not p["has_phone"]
        )
        extra["preview"] = preview
        out["samples"][mod] = extra
        print(
            f"sample {mod}: n={len(recs)} email={extra['with_email']} "
            f"phone={extra['with_phone']} gclid={extra['with_gclid']}"
        )

    # Hop-check: for first 8 newest JOs with a Client_Name, GET the enquiry (IDs only + region/gclid)
    jo_sample = out["samples"].get("Job_Orders") or {}
    hop: list[dict[str, Any]] = []
    st, body = get(
        crm_url(
            api,
            "/Job_Orders?per_page=8&sort_by=Created_Time&sort_order=desc"
            "&fields=id,Name,Region,Client_Name,UTM_Gclid,Email,Phone_1,Stage",
        ),
        token,
    )
    jo_rows = body.get("data") if isinstance(body, dict) else None
    if isinstance(jo_rows, list):
        for r in jo_rows:
            if STOPPED:
                break
            if not isinstance(r, dict):
                continue
            client = r.get("Client_Name") if isinstance(r.get("Client_Name"), dict) else {}
            lid = str((client or {}).get("id") or "")
            hop_row: dict[str, Any] = {
                "jo_suffix": str(r.get("id") or "")[-6:],
                "jo_region": str(r.get("Region") or ""),
                "jo_has_gclid": filled(r.get("UTM_Gclid")),
                "jo_has_email": filled(r.get("Email")),
                "jo_has_phone": filled(r.get("Phone_1")),
                "enquiry_suffix": lid[-6:] if lid else None,
            }
            if lid:
                st2, body2 = get(
                    crm_url(
                        api,
                        f"/Leads/{lid}?fields=id,Region,utm_gclid,Email,Phone,Lead_Status,Company",
                    ),
                    token,
                )
                hop_row["enquiry_http"] = st2
                if st2 == 200 and isinstance(body2, dict) and body2.get("data"):
                    e = body2["data"][0]
                    hop_row.update(
                        {
                            "enquiry_region": str(e.get("Region") or ""),
                            "enquiry_has_gclid": filled(e.get("utm_gclid")),
                            "enquiry_has_email": filled(e.get("Email")),
                            "enquiry_has_phone": filled(e.get("Phone")),
                            "enquiry_status": str(e.get("Lead_Status") or "")[:36],
                            "region_mismatch": bool(
                                e.get("Region")
                                and r.get("Region")
                                and str(e.get("Region")) != str(r.get("Region"))
                            ),
                            "gclid_lost_on_jo": bool(filled(e.get("utm_gclid")) and not filled(r.get("UTM_Gclid"))),
                        }
                    )
            hop.append(hop_row)
    out["attribution_hop_sample"] = hop
    print(f"hop sample n={len(hop)}")

    out["calls"] = CALLS
    out["stopped"] = STOPPED
    write_json(LOCAL_ZOHO / "audit-jo-placement-pipeline-2026-08-19.json", out)
    print(f"calls={CALLS} stopped={STOPPED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
