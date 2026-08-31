#!/usr/bin/env python3
"""Read-only Zoho reconstruction for Aug 17–20 (forensic).

Hard rules:
- GET + COQL SELECT only. Never create/update/delete.
- Never print tokens, emails, phones, or raw click IDs.
- Cap API volume. Stop on rate limit.
- Does not set ZOHO_CRM_ENABLED.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_sales_ops_week_readonly as week  # noqa: E402

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
LOCAL_OUT = Path(__file__).resolve().parents[1] / ".local" / "zoho" / "aug18-forensic-zoho.json"
PUB_OUT = Path(__file__).resolve().parents[1] / "xray" / "data" / "aug18-forensic-zoho.json"

# PT window covering Aug 17–20 inclusive. AU evening Aug 18 is still in this range.
WINDOW_START = "2026-08-17T00:00:00-07:00"
WINDOW_END = "2026-08-21T00:00:00-07:00"
MAX_CALLS = 6

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
)
JUNK_STATUSES = {"junk lead"}
NOT_FIT = {"decided against / not a fit", "not a fit"}


def hash_id(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def company_token(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    cleaned = re.sub(r"[^A-Za-z0-9]", "", text)
    return f"{cleaned[:1].upper()}…{len(text)}" if cleaned else f"len:{len(text)}"


def classify(rec: dict[str, Any], notes: str) -> str:
    status = str(rec.get("Lead_Status") or "").strip().lower()
    form = str(rec.get("Form_Source") or "").strip().lower()
    blob = f"{status} {form} {notes}".lower()
    if any(h in blob for h in TEST_HINTS) or form == "api integration test":
        return "internal_test"
    if status in JUNK_STATUSES or "spam" in blob:
        return "spam_or_junk"
    if any(h in blob for h in SEEKER_HINTS) or "job-seeker" in blob:
        return "job_seeker"
    if status in NOT_FIT:
        return "employer_not_a_fit"
    if "job order" in status or "discovery scheduled" in status:
        return "employer_progressed"
    if "brochure" in status or "attempted to contact" in status or "new enquiry" in status:
        return "employer_probable"
    if rec.get("Company") or rec.get("Job_Position_Required"):
        return "employer_probable"
    return "unknown"


NOTE_KEYS = (
    "lp_version",
    "lp_variant",
    "landing_page_url",
    "landing_page",
    "match_type",
    "utm_matchtype",
    "utm_device",
    "device",
    "category",
    "intent",
    "baseline_label",
    "company_size",
    "positions_needed",
    "hiring_timeline",
)


def parse_notes(raw: str) -> dict[str, str]:
    text = week.EMAIL_RE.sub("[email]", str(raw or ""))
    text = re.sub(r"(gclid|wbraid|gbraid)\s*[:=]\s*\S+", r"\1=[redacted]", text, flags=re.I)
    found: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        val = val.strip()[:160]
        if key in NOTE_KEYS and val:
            found[key] = val
    return found


def sanitize(rec: dict[str, Any]) -> dict[str, Any]:
    notes_raw = str(rec.get("Other_Client_Profile_Information") or rec.get("Description") or "")
    notes = parse_notes(notes_raw)
    gclid = rec.get("utm_gclid") or ""
    role = str(rec.get("Job_Position_Required") or "").strip()[:80]
    created = str(rec.get("Created_Time") or "")
    return {
        "record_id": str(rec.get("id") or ""),
        "created": created[:19],
        "created_date_pt": created[:10],
        "region": str(rec.get("Region") or "")[:16],
        "status": str(rec.get("Lead_Status") or "")[:64],
        "source": str(rec.get("Lead_Source") or "")[:40],
        "form_source": str(rec.get("Form_Source") or "")[:48],
        "utm_source": str(rec.get("utm_source") or "")[:32],
        "utm_medium": str(rec.get("utm_medium") or "")[:32],
        "utm_campaign": str(rec.get("utm_campaign") or "")[:64],
        "utm_term": str(rec.get("utm_term") or "")[:80],
        "campaign_name": str(rec.get("Campaign_Name") or rec.get("utm_campaign") or "")[:64],
        "role_requested": role,
        "has_company": bool(str(rec.get("Company") or "").strip()),
        "company_token": company_token(rec.get("Company")),
        "has_gclid": week.click_present(gclid),
        "gclid_hash": hash_id(gclid),
        "website_host": week.host_of(rec.get("Website") or ""),
        "referrer_host": week.host_of(rec.get("Referrer") or rec.get("Referring_URL") or ""),
        "looks_app_host": "virtualcoworker.app"
        in f"{rec.get('Website') or ''} {rec.get('Referrer') or ''} {rec.get('Referring_URL') or ''}".lower(),
        "notes_len": len(notes_raw),
        "lp_version": notes.get("lp_version") or notes.get("baseline_label") or "",
        "landing_page": notes.get("landing_page_url") or notes.get("landing_page") or "",
        "match_type": notes.get("match_type") or notes.get("utm_matchtype") or "",
        "device": notes.get("utm_device") or notes.get("device") or "",
        "intent": notes.get("intent") or "",
        "category": notes.get("category") or "",
        "company_size": notes.get("company_size") or "",
        "quality": classify(rec, notes_raw),
    }


def try_coql(token: str, api: str, fields: str) -> tuple[int, Any]:
    sql = (
        f"select {fields} from Leads where Created_Time >= '{WINDOW_START}' "
        f"and Created_Time < '{WINDOW_END}' order by Created_Time desc limit 200"
    )
    return week.post_json(week.crm_url(api, "/coql"), token, {"select_query": sql})


def main() -> int:
    week.load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    week.ensure_local_dir()
    week.MAX_CALLS = MAX_CALLS
    creds = week.load_credentials()
    token = str(week.refresh_access_token(creds)["access_token"])
    api = creds["api_domain"]

    field_sets = [
        (
            "id, Created_Time, Region, Lead_Status, Lead_Source, Form_Source, "
            "Company, Job_Position_Required, utm_source, utm_medium, utm_campaign, "
            "utm_term, Campaign_Name, Website, Referrer, Referring_URL, Created_By, "
            "utm_gclid, Other_Client_Profile_Information"
        ),
        (
            "id, Created_Time, Region, Lead_Status, Lead_Source, Form_Source, "
            "Company, Job_Position_Required, utm_source, utm_medium, utm_campaign, "
            "utm_term, Campaign_Name, Website, Referrer, Referring_URL, Created_By, "
            "utm_gclid"
        ),
        (
            "id, Created_Time, Region, Lead_Status, Lead_Source, Form_Source, "
            "utm_source, utm_medium, utm_campaign, Campaign_Name, Website, Referrer, "
            "Referring_URL, Created_By, utm_gclid"
        ),
    ]

    body = None
    used_fields = ""
    status = 0
    for fields in field_sets:
        status, body = try_coql(token, api, fields)
        if status == 200:
            used_fields = fields
            break
        print(f"COQL retry after http={status} err={str(week.redact(body))[:200]}", flush=True)

    if status != 200:
        print(f"COQL failed http={status} err={str(week.redact(body))[:240]}")
        return 1

    raw_rows = week.rows_of(body)
    leads = [sanitize(r) for r in raw_rows]
    usa = [r for r in leads if str(r.get("region") or "").upper() in {"USA", "US", "UNITED STATES"}]
    au = [r for r in leads if str(r.get("region") or "").upper() in {"AU", "AUS", "AUSTRALIA"}]
    aug18 = [r for r in leads if str(r.get("created_date_pt") or "") == "2026-08-18"]

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "window_start": WINDOW_START,
        "window_end_exclusive": WINDOW_END,
        "timezone": "America/Los_Angeles for Created_Time filter; record stamps are CRM local",
        "api": "Zoho CRM v8 COQL SELECT",
        "api_calls": week.CALLS,
        "fields_used": used_fields,
        "leads_in_window": len(leads),
        "quality_counts": week.count_map(leads, "quality"),
        "by_region": week.count_map(leads, "region"),
        "by_status": week.count_map(leads, "status"),
        "aug18_pt": {
            "n": len(aug18),
            "usa": [r for r in aug18 if r in usa],
            "au": [r for r in aug18 if r in au],
            "other": [r for r in aug18 if r not in usa and r not in au],
        },
        "usa": usa,
        "au": au,
        "gclid_leads": [r for r in leads if r.get("has_gclid")],
    }
    LOCAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    PUB_OUT.parent.mkdir(parents=True, exist_ok=True)
    PUB_OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in payload if k not in {"usa", "au", "aug18_pt", "gclid_leads"}}, indent=2))
    print(f"wrote {LOCAL_OUT}")
    print(f"wrote {PUB_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
