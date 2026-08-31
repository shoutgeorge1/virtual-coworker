#!/usr/bin/env python3
"""Create exactly ONE safe Sales Enquiry test record. Create-only.

Does not set ZOHO_CRM_ENABLED or ZOHO_SUBMISSION_ENABLED.
Suppresses workflows/cadences via documented trigger=[] .
Never writes Discovery Scheduled / Job Order Submitted / Placement.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

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

REPO = Path(__file__).resolve().parents[2]
ENV_PATH = REPO / ".env"
MODULE = "Leads"
SAFE_STATUS = "New Enquiry (Auto)"
DANGER_STATUS = {
    "Discovery Scheduled",
    "Job Order Submitted",
    "Placement",
    "Create Job Opening",
    "Pre-Qualified",
    "Contact Successful",
    "Discovery Booked",
    "Discovery Completed",
    "Qualified",
}


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


def pick(rec: dict[str, Any], key: str) -> str:
    v = rec.get(key)
    if isinstance(v, dict):
        return str(v.get("name") or v.get("id") or "")
    if v is None:
        return ""
    return str(v)


def main() -> int:
    load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    if (os.environ.get("ZOHO_SUBMISSION_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_SUBMISSION_ENABLED is true (leave production posting off)")
        return 2

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    submission_id = f"VC-ZOHO-TEST-{ts}"
    email = f"shoutgeorge1+vc-zoho-test-{ts}@gmail.com"
    notes = (
        "TEST RECORD — DO NOT CONTACT — DO NOT QUALIFY — DO NOT CONVERT\n\n"
        "--- VC LP payload ---\n"
        f"submission_id: {submission_id}\n"
        "lead_source_requested: API Integration Test\n"
        "market: US\n"
        "created_by: virtual-coworker LP integration test\n"
        "ads_note: no gclid/gbraid/wbraid on this first record\n"
    )
    record = {
        "First_Name": "Zoho",
        "Last_Name": "Integration Test",
        "Company": "[TEST] Virtual Coworker API",
        "Email": email,
        "Phone": "+15550100199",
        "Lead_Source": "Other",
        "Form_Source": "API Integration Test",
        "Lead_Status": SAFE_STATUS,
        "Region": "USA",
        "Gravity_Form_Entry_ID": submission_id,
        "Other_Client_Profile_Information": notes,
        "Submission_Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
    }

    ensure_local_dir()
    creds = load_credentials()
    token_body = refresh_access_token(creds)
    token = str(token_body["access_token"])
    api_domain = creds["api_domain"]
    print(f"Token ok. api_domain={api_domain} module={MODULE}")
    print(f"submission_id={submission_id}")

    payload = {
        "data": [record],
        "trigger": [],
        "skip_feature_execution": [{"name": "cadences"}],
    }
    st, body = http_post_json(
        crm_url(api_domain, f"/{MODULE}"),
        payload,
        access_token=token,
    )
    write_json(
        LOCAL_ZOHO / "safe-test-create-response.json",
        {"http_status": st, "body": body, "submission_id": submission_id},
    )
    print(f"CREATE HTTP {st}")
    if st == 429 or (isinstance(body, dict) and str(body.get("code") or "") in {"RATE_LIMIT", "TOO_MANY_REQUESTS"}):
        print("RATE LIMIT. Stop.")
        return 3
    if not isinstance(body, dict):
        print("Create failed: non-JSON")
        return 1

    row = (body.get("data") or [None])[0] if isinstance(body.get("data"), list) else None
    record_id = ""
    code = ""
    if isinstance(row, dict):
        code = str(row.get("code") or "")
        details = row.get("details") if isinstance(row.get("details"), dict) else {}
        record_id = str(details.get("id") or row.get("id") or "")
        print(f"create code={code} id={record_id or '(none)'}")
        if row.get("message"):
            print(f"create message={row.get('message')}")

    if st >= 400 or not record_id:
        print("CREATE FAILED. No further records. Production still off.")
        return 1

    gst, got = http_get_json(
        crm_url(api_domain, f"/{MODULE}/{record_id}"),
        access_token=token,
    )
    write_json(
        LOCAL_ZOHO / "safe-test-get-response.json",
        {"http_status": gst, "id": record_id},
    )
    print(f"GET HTTP {gst}")
    rec: dict[str, Any] = {}
    if isinstance(got, dict) and isinstance(got.get("data"), list) and got["data"]:
        rec = got["data"][0] if isinstance(got["data"][0], dict) else {}

    status = pick(rec, "Lead_Status")
    blueprint = pick(rec, "Blueprint_Lead_Status")
    jo_flag = rec.get("Job_Order_submitted_via_form")
    converted = rec.get("Converted__s")
    book = rec.get("Book_free_consultation")
    qual = pick(rec, "Qualification_Status")
    owner = pick(rec, "Owner")
    company = pick(rec, "Company")
    form_source = pick(rec, "Form_Source")
    lead_source = pick(rec, "Lead_Source")
    gclid = pick(rec, "utm_gclid")
    notes_got = pick(rec, "Other_Client_Profile_Information")

    print("STORED")
    print(f"  Company={company}")
    print(f"  Lead_Status={status}")
    print(f"  Blueprint_Lead_Status={blueprint or '(empty)'}")
    print(f"  Lead_Source={lead_source}")
    print(f"  Form_Source={form_source}")
    print(f"  Job_Order_submitted_via_form={jo_flag}")
    print(f"  Converted__s={converted}")
    print(f"  Book_free_consultation={book}")
    print(f"  Qualification_Status={qual or '(empty)'}")
    print(f"  utm_gclid={gclid or '(empty)'}")
    print(f"  Owner={owner or '(empty)'}")
    print(f"  Gravity_Form_Entry_ID={pick(rec, 'Gravity_Form_Entry_ID')}")

    stop_reasons: list[str] = []
    if status in DANGER_STATUS or blueprint in DANGER_STATUS:
        stop_reasons.append(f"status looks like Ads conversion filter: {status!r} / {blueprint!r}")
    if jo_flag is True:
        stop_reasons.append("Job_Order_submitted_via_form is true")
    if converted is True:
        stop_reasons.append("record marked converted")
    if book is True:
        stop_reasons.append("Book_free_consultation is true")
    if qual in {"Passed", "Qualified"}:
        stop_reasons.append(f"Qualification_Status={qual}")
    if "[TEST]" not in company:
        stop_reasons.append("company label missing [TEST]")
    if "DO NOT CONVERT" not in notes_got:
        stop_reasons.append("notes banner missing")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api_domain": api_domain,
        "api_version": "v8",
        "module_api_name": MODULE,
        "module_display": "Sales Enquiries",
        "record_id": record_id,
        "submission_id": submission_id,
        "create_code": code,
        "lead_status": status,
        "blueprint_lead_status": blueprint,
        "lead_source": lead_source,
        "form_source": form_source,
        "company": company,
        "owner": owner,
        "utm_gclid": gclid,
        "job_order_submitted_via_form": jo_flag,
        "converted": converted,
        "stop_reasons": stop_reasons,
        "batch_created": False,
        "zoho_submission_enabled": "false",
        "zoho_crm_enabled": (os.environ.get("ZOHO_CRM_ENABLED") or "").strip() or "unset",
    }
    write_json(LOCAL_ZOHO / "safe-test-summary.json", summary)
    out_md = Path(__file__).resolve().parent / "SALES-ENQUIRY-LP-INTEGRATION.md"
    # written later by report step; keep JSON for the recap

    if stop_reasons:
        print("STOP — unexpected stored values:")
        for r in stop_reasons:
            print(f"  - {r}")
        print("No batch. Production posting still off.")
        return 4

    print("FIRST TEST OK — stored as New Enquiry (Auto), no JO/Discovery/click id.")
    print("No batch will be created. Production posting still off.")
    print(f"RECORD_ID={record_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
