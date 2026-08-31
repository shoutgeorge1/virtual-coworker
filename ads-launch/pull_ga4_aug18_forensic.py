#!/usr/bin/env python3
"""GA4 Data API forensic window for Aug 17–20. Not Google Ads API."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "ads-launch"))

from pull_ga4_executive import (  # noqa: E402
    DEFAULT_GA4_PROPERTY_ID_US,
    MEASUREMENT_ID_AU,
    MEASUREMENT_ID_US,
    _load_dotenv_quiet,
    _metric_map,
    _pct_rate,
    resolve_ga4_property_id,
    resolve_ga4_property_id_au,
)

OUT = REPO / "xray" / "data" / "aug18-forensic-ga4.json"
START = "2026-08-17"
END = "2026-08-20"
FOCUS = "2026-08-18"


def _client():
    from google.analytics.data_v1beta import BetaAnalyticsDataClient

    _load_dotenv_quiet()
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or ""
    if not creds:
        fallback = REPO / ".local" / "ga4" / "service-account.json"
        if fallback.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(fallback)
    return BetaAnalyticsDataClient()


def run_property(client: Any, property_id: str, label: str, measurement_id: str) -> dict[str, Any]:
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Filter,
        FilterExpression,
        FilterExpressionList,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    if not property_id:
        return {"ok": False, "error": "missing_property_id"}
    prop = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
    calls: list[dict[str, Any]] = []

    def report(name: str, req: Any) -> Any:
        resp = client.run_report(req)
        calls.append({"n": len(calls) + 1, "name": name, "ok": True, "rows": len(resp.rows or [])})
        return resp

    overview_metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "conversions",
        "averageSessionDuration",
    ]
    resp1 = report(
        "by_date",
        RunReportRequest(
            property=prop,
            date_ranges=[DateRange(start_date=START, end_date=END)],
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name=m) for m in overview_metrics],
            order_bys=[OrderBy(dimension={"dimension_name": "date"})],
        ),
    )
    by_date = []
    for row in resp1.rows or []:
        mets = _metric_map(row, overview_metrics)
        day = row.dimension_values[0].value if row.dimension_values else ""
        if len(day) == 8:
            day = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
        by_date.append(
            {
                "date": day,
                "sessions": int(mets.get("sessions") or 0),
                "users": int(mets.get("totalUsers") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
                "bounce_rate_pct": _pct_rate(mets.get("bounceRate")),
                "conversions": float(mets.get("conversions") or 0),
                "avg_session_seconds": round(float(mets.get("averageSessionDuration") or 0), 1),
            }
        )

    land_metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "conversions",
        "averageSessionDuration",
    ]
    resp2 = report(
        "landing_by_date",
        RunReportRequest(
            property=prop,
            date_ranges=[DateRange(start_date=START, end_date=END)],
            dimensions=[Dimension(name="date"), Dimension(name="landingPagePlusQueryString")],
            metrics=[Metric(name=m) for m in land_metrics],
            order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
            limit=80,
        ),
    )
    landings = []
    for row in resp2.rows or []:
        mets = _metric_map(row, land_metrics)
        day = row.dimension_values[0].value if row.dimension_values else ""
        if len(day) == 8:
            day = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
        path = row.dimension_values[1].value if len(row.dimension_values) > 1 else ""
        landings.append(
            {
                "date": day,
                "path": path.split("?")[0],
                "sessions": int(mets.get("sessions") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
                "conversions": float(mets.get("conversions") or 0),
                "avg_session_seconds": round(float(mets.get("averageSessionDuration") or 0), 1),
            }
        )

    event_metrics = ["eventCount", "conversions"]
    resp3 = report(
        "events_by_date",
        RunReportRequest(
            property=prop,
            date_ranges=[DateRange(start_date=START, end_date=END)],
            dimensions=[Dimension(name="date"), Dimension(name="eventName")],
            metrics=[Metric(name=m) for m in event_metrics],
            order_bys=[OrderBy(metric={"metric_name": "eventCount"}, desc=True)],
            limit=120,
        ),
    )
    events = []
    interesting = (
        "form_start",
        "form_submit",
        "generate_lead",
        "employer_inquiry",
        "thank_you",
        "phone",
        "call",
        "qualify_lead",
        "close_convert",
        "purchase",
        "experiment_convert",
        "lp_micro",
        "session_start",
        "user_engagement",
        "page_view",
        "click",
    )
    for row in resp3.rows or []:
        mets = _metric_map(row, event_metrics)
        day = row.dimension_values[0].value if row.dimension_values else ""
        if len(day) == 8:
            day = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
        name = row.dimension_values[1].value if len(row.dimension_values) > 1 else ""
        if day == FOCUS or any(n in (name or "").lower() for n in interesting):
            events.append(
                {
                    "date": day,
                    "event": name,
                    "count": int(mets.get("eventCount") or 0),
                    "conversions": float(mets.get("conversions") or 0),
                }
            )

    channel_metrics = ["sessions", "engagedSessions", "conversions"]
    resp4 = report(
        "channel_device_aug18",
        RunReportRequest(
            property=prop,
            date_ranges=[DateRange(start_date=FOCUS, end_date=FOCUS)],
            dimensions=[
                Dimension(name="sessionDefaultChannelGroup"),
                Dimension(name="deviceCategory"),
                Dimension(name="landingPagePlusQueryString"),
            ],
            metrics=[Metric(name=m) for m in channel_metrics],
            order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
            limit=40,
        ),
    )
    channels = []
    for row in resp4.rows or []:
        mets = _metric_map(row, channel_metrics)
        dims = [d.value for d in (row.dimension_values or [])]
        channels.append(
            {
                "channel": dims[0] if dims else "",
                "device": dims[1] if len(dims) > 1 else "",
                "path": (dims[2].split("?")[0] if len(dims) > 2 else ""),
                "sessions": int(mets.get("sessions") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "conversions": float(mets.get("conversions") or 0),
            }
        )

    watch_paths = ["/us", "/au", "/au/recruitment", "/us/real-estate", "/us/recruitment"]
    expr = FilterExpression(
        or_group=FilterExpressionList(
            expressions=[
                FilterExpression(
                    filter=Filter(
                        field_name="landingPagePlusQueryString",
                        string_filter=Filter.StringFilter(
                            match_type=Filter.StringFilter.MatchType.BEGINS_WITH,
                            value=path,
                        ),
                    )
                )
                for path in watch_paths
            ]
        )
    )
    resp5 = report(
        "watched_paths_window",
        RunReportRequest(
            property=prop,
            date_ranges=[DateRange(start_date=START, end_date=END)],
            dimensions=[Dimension(name="date"), Dimension(name="landingPagePlusQueryString")],
            metrics=[Metric(name=m) for m in land_metrics],
            dimension_filter=expr,
            order_bys=[OrderBy(dimension={"dimension_name": "date"})],
            limit=40,
        ),
    )
    watched = []
    for row in resp5.rows or []:
        mets = _metric_map(row, land_metrics)
        day = row.dimension_values[0].value if row.dimension_values else ""
        if len(day) == 8:
            day = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
        path = row.dimension_values[1].value if len(row.dimension_values) > 1 else ""
        watched.append(
            {
                "date": day,
                "path": path.split("?")[0],
                "sessions": int(mets.get("sessions") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
                "conversions": float(mets.get("conversions") or 0),
                "avg_session_seconds": round(float(mets.get("averageSessionDuration") or 0), 1),
            }
        )

    return {
        "ok": True,
        "label": label,
        "property_id": property_id,
        "measurement_id": measurement_id,
        "api_calls": calls,
        "by_date": by_date,
        "focus": next((d for d in by_date if d["date"] == FOCUS), None),
        "landings_aug18": [r for r in landings if r["date"] == FOCUS][:20],
        "events_aug18": [r for r in events if r["date"] == FOCUS],
        "channels_aug18": channels,
        "watched_paths": watched,
    }


def main() -> int:
    client = _client()
    us_id = resolve_ga4_property_id() or DEFAULT_GA4_PROPERTY_ID_US
    au_id = resolve_ga4_property_id_au()
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "api": "ga4_data_api",
        "window": f"{START} → {END}",
        "focus_day": FOCUS,
        "timezone_note": "GA4 property timezone (US and AU properties separately). Dates are property-local.",
        "US": run_property(client, us_id, "US", MEASUREMENT_ID_US),
        "AU": run_property(client, au_id, "AU", MEASUREMENT_ID_AU) if au_id else {"ok": False, "error": "no_au_property"},
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(OUT),
        "us_ok": payload["US"].get("ok"),
        "au_ok": payload["AU"].get("ok"),
        "us_focus": payload["US"].get("focus"),
        "au_focus": payload["AU"].get("focus"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
