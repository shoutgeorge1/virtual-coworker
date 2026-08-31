#!/usr/bin/env python3
"""Read-only Zoho ping for lead-quality reconciliation.

GET fields + one COQL. Never writes. Never sets ZOHO_CRM_ENABLED.
Never prints emails, phones, or raw GCLIDs. Does not call Google Ads.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "zoho"))
from _common import (  # noqa: E402
    crm_url,
    ensure_local_dir,
    http_get_json,
    load_credentials,
    refresh_access_token,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_sales_ops_week_readonly as week  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
ENV_PATH = REPO / ".env"
LOCAL_OUT = REPO / ".local" / "zoho" / "lead-quality-recon.json"
PUB_OUT = REPO / "xray" / "data" / "lead-quality-recon.json"

# This week Mon–Sun. PT midnight so Sunday evening PT is included.
WINDOW_START = "2026-08-17T00:00:00-07:00"
WINDOW_END = "2026-08-24T00:00:00-07:00"
MAX_CALLS = 3

CLASS_NAME_HINTS = (
    "inquiry_class",
    "enquiry_class",
    "lead_class",
    "vc_inquiry",
    "buyer_type",
    "customer_type",
    "lead_type",
    "enquiry_type",
    "inquiry_type",
    "intent_class",
    "quality_class",
)
CLASS_VALUE_HINTS = (
    "qualified employer",
    "job seeker",
    "internal test",
    "probable employer",
)
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
    "looking for work",
    "i am applying",
    "i'm applying",
    "resume",
    "cv attached",
    "want a job",
    "work seeker",
)
JUNK_STATUSES = {"junk lead"}
NOT_FIT = {"decided against / not a fit", "not a fit"}
SALES_BUCKETS = {
    "qualified employer": "qualified_employer",
    "probable employer": "probable_employer",
    "job seeker": "job_seeker",
    "junk": "junk",
    "spam": "junk",
    "internal test": "test",
    "test": "test",
    "unknown": "needs_review",
    "needs review": "needs_review",
    "unknown / needs review": "needs_review",
}


def hash_id(raw: object) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def field_looks_like_class(api_name: str, label: str, values: list[str]) -> bool:
    blob = f"{api_name} {label}".lower()
    if any(h in blob for h in CLASS_NAME_HINTS):
        return True
    joined = " ".join(values).lower()
    return any(h in joined for h in CLASS_VALUE_HINTS)


def picklist_values(field: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for key in ("pick_list_values", "picklist_values"):
        rows = field.get(key) or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict):
                val = str(row.get("display_value") or row.get("actual_value") or "").strip()
            else:
                val = str(row or "").strip()
            if val and val not in ("-None-", "--None--"):
                out.append(val[:64])
    return out


def infer_class(rec: dict[str, Any], notes: str, sales_mark: str) -> tuple[str, str]:
    if sales_mark:
        mapped = SALES_BUCKETS.get(sales_mark.lower().strip(), "")
        if mapped:
            return mapped, "sales_tick"
        return "needs_review", "sales_tick_unmapped"
    status = str(rec.get("Lead_Status") or "").strip().lower()
    form = str(rec.get("Form_Source") or "").strip().lower()
    blob = f"{status} {form} {notes}".lower()
    if any(h in blob for h in TEST_HINTS) or form == "api integration test":
        return "test", "inferred"
    if status in JUNK_STATUSES or "spam" in blob:
        return "junk", "inferred"
    if any(h in blob for h in SEEKER_HINTS) or "job-seeker" in blob:
        return "job_seeker", "inferred"
    if status in NOT_FIT:
        return "not_a_fit", "inferred"
    if "job order" in status:
        return "qualified_employer", "inferred"
    if "discovery scheduled" in status or "brochure" in status or "attempted to contact" in status:
        return "probable_employer", "inferred"
    if "new enquiry" in status:
        return "needs_review", "inferred"
    return "needs_review", "inferred"


def booked_call(rec: dict[str, Any]) -> bool:
    if str(rec.get("Discovery_Call_Date") or "").strip():
        return True
    status = str(rec.get("Lead_Status") or "").lower()
    return "discovery scheduled" in status


def sales_mark_of(rec: dict[str, Any], class_field: str) -> str:
    if not class_field:
        return ""
    raw = rec.get(class_field)
    if isinstance(raw, dict):
        return str(raw.get("name") or raw.get("display_value") or "")[:48]
    return str(raw or "").strip()[:48]


def sanitize(rec: dict[str, Any], class_field: str) -> dict[str, Any]:
    notes_raw = str(rec.get("Other_Client_Profile_Information") or rec.get("Description") or "")
    notes_l = notes_raw.lower()
    mark = sales_mark_of(rec, class_field)
    quality, quality_source = infer_class(rec, notes_l, mark)
    gclid = rec.get("utm_gclid") or ""
    return {
        "record_id": str(rec.get("id") or ""),
        "created": str(rec.get("Created_Time") or "")[:19],
        "region": str(rec.get("Region") or "")[:16],
        "status": str(rec.get("Lead_Status") or "")[:64],
        "qualification_status": str(rec.get("Qualification_Status") or "")[:48],
        "sales_mark": mark,
        "quality": quality,
        "quality_source": quality_source,
        "form_step": True,
        "booked_call": booked_call(rec),
        "discovery_call_date": str(rec.get("Discovery_Call_Date") or "")[:32],
        "form_source": str(rec.get("Form_Source") or "")[:40],
        "has_company": bool(str(rec.get("Company") or "").strip()),
        "role_requested": str(rec.get("Job_Position_Required") or "")[:80],
        "utm_source": str(rec.get("utm_source") or "")[:32],
        "utm_medium": str(rec.get("utm_medium") or "")[:32],
        "utm_campaign": str(rec.get("utm_campaign") or "")[:48],
        "utm_term": str(rec.get("utm_term") or "")[:80],
        "has_gclid": week.click_present(gclid),
        "gclid_hash": hash_id(gclid),
        "paid": week.click_present(gclid) and str(rec.get("utm_medium") or "").lower() == "cpc",
    }


def main() -> int:
    week.load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    week.MAX_CALLS = MAX_CALLS
    week.CALLS = 0
    week.STOPPED = None
    ensure_local_dir()
    creds = load_credentials()
    token = str(refresh_access_token(creds)["access_token"])
    api = creds["api_domain"]

    week.CALLS += 1
    st, fields_body = http_get_json(
        crm_url(api, "/settings/fields?module=Leads"),
        access_token=token,
    )
    if st != 200 or not isinstance(fields_body, dict):
        print(f"fields GET failed http={st}")
        return 1

    class_candidates: list[dict[str, Any]] = []
    known_names: set[str] = set()
    for field in fields_body.get("fields") or []:
        if not isinstance(field, dict):
            continue
        api_name = str(field.get("api_name") or "")
        label = str(field.get("field_label") or field.get("display_label") or "")
        values = picklist_values(field)
        known_names.add(api_name)
        if field_looks_like_class(api_name, label, values):
            class_candidates.append(
                {
                    "api_name": api_name,
                    "label": label[:64],
                    "values": values[:12],
                }
            )

    preferred = ""
    for name in ("VC_Inquiry_Class", "Inquiry_Class", "Enquiry_Class", "Qualification_Status"):
        if any(c["api_name"] == name for c in class_candidates) or name in known_names:
            if name != "Qualification_Status" or not preferred:
                preferred = name
            if name == "VC_Inquiry_Class":
                break
    if not preferred:
        for cand in class_candidates:
            if cand["api_name"] not in {"Lead_Status", "Blueprint_Lead_Status"}:
                preferred = cand["api_name"]
                break

    extra = ""
    if preferred and preferred not in {
        "id",
        "Created_Time",
        "Region",
        "Lead_Status",
        "Qualification_Status",
        "Discovery_Call_Date",
        "Form_Source",
        "Company",
        "Job_Position_Required",
        "utm_gclid",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "Description",
        "Other_Client_Profile_Information",
    }:
        extra = f", {preferred}"

    fields = (
        "id, Created_Time, Region, Lead_Status, Qualification_Status, "
        "Discovery_Call_Date, Form_Source, Company, Job_Position_Required, "
        "utm_gclid, utm_source, utm_medium, utm_campaign, utm_term, "
        f"Description, Other_Client_Profile_Information{extra}"
    )
    sql = (
        f"select {fields} from Leads where Created_Time >= '{WINDOW_START}' "
        f"and Created_Time < '{WINDOW_END}' order by Created_Time desc limit 200"
    )
    status, body = week.post_json(week.crm_url(api, "/coql"), token, {"select_query": sql})
    if status != 200:
        print(f"COQL failed http={status} err={str(week.redact(body))[:240]}")
        return 1

    rows = [sanitize(rec, preferred) for rec in week.rows_of(body)]
    paid = [r for r in rows if r.get("paid")]
    quality_counts = dict(Counter(r["quality"] for r in paid).most_common())
    source_counts = dict(Counter(r["quality_source"] for r in paid).most_common())

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "api": "Zoho CRM v8 GET fields + COQL SELECT",
        "api_calls": week.CALLS,
        "stopped": week.STOPPED,
        "window_start": WINDOW_START,
        "window_end_exclusive": WINDOW_END,
        "week_label": "17–23 Aug 2026 (Mon–Sun)",
        "note": "Paid = utm_gclid + utm_medium=cpc. No emails, phones, or raw GCLIDs.",
        "ash_note": (
            "Ash emailed 20 Aug: read-only forensic audit of the lead-to-placement path. "
            "Update next week. He has not said a sales class field is live."
        ),
        "class_field": {
            "api_name": preferred,
            "exists": bool(preferred) and preferred in known_names,
            "is_dedicated": preferred in {"VC_Inquiry_Class", "Inquiry_Class", "Enquiry_Class"},
            "candidates": class_candidates[:8],
        },
        "leads_in_window": len(rows),
        "paid_people": len(paid),
        "quality_counts_paid": quality_counts,
        "quality_source_counts_paid": source_counts,
        "sales_ticks_filled": sum(1 for r in paid if r.get("sales_mark")),
        "booked_among_paid": sum(1 for r in paid if r.get("booked_call")),
        "people": paid,
        "unpaid_in_window": len(rows) - len(paid),
        "ads_snapshot": {
            "as_of": "2026-08-19",
            "note": "Click-date Ads counts from executive-snapshot. Not a live Ads pull.",
            "us": {"2026-08-17": 0, "2026-08-18": 2.0, "2026-08-19": 0},
            "au": {"2026-08-17": 0, "2026-08-18": 4.0, "2026-08-19": 1.0},
            "us_total": 2.0,
            "au_total": 5.0,
            "combined": 7.0,
        },
    }
    text = json.dumps(payload, indent=2) + "\n"
    LOCAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    PUB_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_OUT.write_text(text, encoding="utf-8")
    PUB_OUT.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "api_calls": payload["api_calls"],
                "class_field": payload["class_field"]["api_name"],
                "dedicated": payload["class_field"]["is_dedicated"],
                "candidates": [c["api_name"] for c in class_candidates],
                "leads_in_window": payload["leads_in_window"],
                "paid_people": payload["paid_people"],
                "quality_counts_paid": quality_counts,
                "sales_ticks_filled": payload["sales_ticks_filled"],
                "booked_among_paid": payload["booked_among_paid"],
            },
            indent=2,
        )
    )
    print(f"wrote {PUB_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
