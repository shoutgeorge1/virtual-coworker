#!/usr/bin/env python3
"""One extra Zoho COQL for quality-gate fields. GET/COQL only.

Never writes to Zoho. Never sets ZOHO_CRM_ENABLED. Never prints emails,
phones, or raw GCLIDs. One COQL call. Stop on rate limit.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_sales_ops_week_readonly as week  # noqa: E402

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
OUT = Path(__file__).resolve().parents[1] / ".local" / "zoho" / "quality-gate-extra-coql.json"

WINDOW_START = "2026-08-17T00:00:00-07:00"
WINDOW_END = "2026-08-21T00:00:00-07:00"
MAX_CALLS = 2

KNOWN_GCLID = {
    "6724032000029986002",
    "6724032000029876002",
    "6724032000029875002",
    "6724032000029868001",
    "6724032000029820005",
}


def hash_id(raw: object) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


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

    fields = (
        "id, Created_Time, Region, Lead_Status, Blueprint_Lead_Status, "
        "Qualification_Status, Discovery_Call_Date, Form_Source, Company, "
        "Job_Position_Required, utm_gclid, utm_source, utm_medium, utm_campaign, "
        "utm_term"
    )
    sql = (
        f"select {fields} from Leads where Created_Time >= '{WINDOW_START}' "
        f"and Created_Time < '{WINDOW_END}' order by Created_Time desc limit 200"
    )
    status, body = week.post_json(week.crm_url(api, "/coql"), token, {"select_query": sql})
    if status != 200:
        print(f"COQL failed http={status} err={str(week.redact(body))[:240]}")
        return 1

    rows = []
    for rec in week.rows_of(body):
        rid = str(rec.get("id") or "")
        if rid not in KNOWN_GCLID:
            continue
        rows.append(
            {
                "record_id": rid,
                "created": str(rec.get("Created_Time") or "")[:19],
                "region": str(rec.get("Region") or "")[:16],
                "status": str(rec.get("Lead_Status") or "")[:64],
                "blueprint_status": str(rec.get("Blueprint_Lead_Status") or "")[:64],
                "qualification_status": str(rec.get("Qualification_Status") or "")[:48],
                "discovery_call_date": str(rec.get("Discovery_Call_Date") or "")[:32],
                "form_source": str(rec.get("Form_Source") or "")[:40],
                "has_company": bool(str(rec.get("Company") or "").strip()),
                "role_requested": str(rec.get("Job_Position_Required") or "")[:80],
                "has_gclid": week.click_present(rec.get("utm_gclid")),
                "gclid_hash": hash_id(rec.get("utm_gclid")),
                "utm_source": str(rec.get("utm_source") or "")[:32],
                "utm_medium": str(rec.get("utm_medium") or "")[:32],
                "utm_campaign": str(rec.get("utm_campaign") or "")[:48],
                "utm_term": str(rec.get("utm_term") or "")[:80],
            }
        )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "api": "Zoho CRM v8 COQL SELECT",
        "api_calls": week.CALLS,
        "stopped": week.STOPPED,
        "window_start": WINDOW_START,
        "window_end_exclusive": WINDOW_END,
        "note": "Paid gclid people only. No emails, phones, or raw GCLIDs.",
        "n": len(rows),
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
