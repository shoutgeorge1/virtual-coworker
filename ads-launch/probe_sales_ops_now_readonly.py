#!/usr/bin/env python3
"""Read-only Zoho census for this week so far. Does not overwrite the frozen week file."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_sales_ops_week_readonly as week  # noqa: E402

PT = ZoneInfo("America/Los_Angeles")
now_pt = datetime.now(PT)
monday_pt = (now_pt - timedelta(days=now_pt.weekday())).replace(
    hour=0, minute=0, second=0, microsecond=0
)
end_pt = (now_pt + timedelta(days=1)).replace(
    hour=0, minute=0, second=0, microsecond=0
)
week.WINDOW_START = monday_pt.isoformat()
week.WINDOW_END = end_pt.isoformat()


def main() -> int:
    if not os.environ.get("GITHUB_ACTIONS"):
        week.load_dotenv(week.ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    week.ensure_local_dir()
    creds = week.load_credentials()
    token = str(week.refresh_access_token(creds)["access_token"])
    api = creds["api_domain"]
    coql = week.crm_url(api, "/coql")
    fields = (
        "id, Created_Time, Region, Lead_Status, Lead_Source, Form_Source, "
        "utm_source, utm_medium, utm_campaign, Campaign_Name, Website, Referrer, "
        "Referring_URL, Created_By, utm_gclid"
    )
    sql = (
        f"select {fields} from Leads where Created_Time >= '{week.WINDOW_START}' "
        f"and Created_Time < '{week.WINDOW_END}' order by Created_Time desc limit 200"
    )
    st, body = week.post_json(coql, token, {"select_query": sql})
    if st != 200:
        print(f"COQL failed http={st} err={str(week.redact(body))[:240]}")
        return 1
    leads = [week.sanitize_lead(r) for r in week.rows_of(body)]
    usa = [r for r in leads if str(r.get("region") or "").upper() in {"USA", "US", "UNITED STATES"}]
    au = [r for r in leads if str(r.get("region") or "").upper() in {"AU", "AUS", "AUSTRALIA"}]

    def region_block(rows):
        return {
            "n": len(rows),
            "with_utm_gclid": sum(1 for r in rows if r.get("has_gclid")),
            "discovery_scheduled": sum(
                1 for r in rows if "discovery scheduled" in str(r.get("status") or "").lower()
            ),
            "job_order_submitted": sum(
                1 for r in rows if "job order" in str(r.get("status") or "").lower()
            ),
            "by_source": week.count_map(rows, "source"),
            "by_status": week.count_map(rows, "status"),
        }

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "window_start": week.WINDOW_START,
        "window_end_exclusive": week.WINDOW_END,
        "api_calls": week.CALLS,
        "leads_in_window": len(leads),
        "usa": region_block(usa),
        "au": region_block(au),
        "all_regions": week.count_map(leads, "region"),
        "cheyenne_note": (
            "Zoho census only — US Cost / enquiry on Executive uses Cheyenne’s "
            "labeled count from Gmail, not this row total."
        ),
    }
    out = Path(__file__).resolve().parents[1] / "xray" / "data" / "sales-ops-week-zoho-now.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
