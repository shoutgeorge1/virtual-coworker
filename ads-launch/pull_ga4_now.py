#!/usr/bin/env python3
"""GA4 now-window (this week so far vs same weekdays last week).

Does not replace the frozen Aug 10–16 GA4 block. Merges `ga4.now` only.
US 2 reports + AU 2 reports. Not Google Ads API.
"""

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
    GA4_WEEK_END,
    GA4_WEEK_START,
    MEASUREMENT_ID_AU,
    MEASUREMENT_ID_US,
    OUT_EXEC,
    OUT_GA4,
    _load_dotenv_quiet,
    _metric_map,
    _pct_rate,
    resolve_ga4_property_id,
    resolve_ga4_property_id_au,
)

NOW_START = "2026-08-24"
NOW_END = "2026-08-24"
SAME_START = "2026-08-17"
SAME_END = "2026-08-17"


def _overview(client: Any, property_id: str, DateRange: Any, Metric: Any, RunReportRequest: Any) -> dict[str, Any]:
    prop = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
    metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "conversions",
        "averageSessionDuration",
    ]
    req = RunReportRequest(
        property=prop,
        date_ranges=[
            DateRange(start_date=NOW_START, end_date=NOW_END),
            DateRange(start_date=SAME_START, end_date=SAME_END),
        ],
        metrics=[Metric(name=m) for m in metrics],
    )
    resp = client.run_report(req)
    now_raw = {m: 0 for m in metrics}
    same_raw = {m: 0 for m in metrics}
    for row in resp.rows or []:
        mets = _metric_map(row, metrics)
        dvs = list(row.dimension_values or [])
        key = dvs[-1].value if dvs else "date_range_0"
        target = same_raw if key == "date_range_1" else now_raw
        target.update(mets)

    def pack(raw: dict[str, Any]) -> dict[str, Any]:
        sess = int(raw.get("sessions") or 0)
        eng = int(raw.get("engagedSessions") or 0)
        return {
            "sessions": sess,
            "users": int(raw.get("totalUsers") or 0),
            "engaged_sessions": eng,
            "engagement_rate_pct": _pct_rate(raw.get("engagementRate")),
            "bounce_rate_pct": _pct_rate(raw.get("bounceRate")),
            "conversions": float(raw.get("conversions") or 0),
            "avg_session_seconds": float(raw.get("averageSessionDuration") or 0),
        }

    return {"now": pack(now_raw), "same_weekdays": pack(same_raw)}


LAND_METRICS = [
    "sessions",
    "totalUsers",
    "engagedSessions",
    "engagementRate",
    "bounceRate",
    "averageSessionDuration",
]


def _landings(
    client: Any,
    property_id: str,
    DateRange: Any,
    Dimension: Any,
    Metric: Any,
    OrderBy: Any,
    RunReportRequest: Any,
    *,
    start: str = NOW_START,
    end: str = NOW_END,
) -> list[dict[str, Any]]:
    from pull_ga4_executive import _path_kind, _infer_market

    prop = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
    req = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=start, end_date=end)],
        # landingPage is already the clean pathname. PlusQueryString would
        # split the same page across UTMs and break the CRO table.
        dimensions=[Dimension(name="landingPage")],
        metrics=[Metric(name=m) for m in LAND_METRICS],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
        limit=15,
    )
    resp = client.run_report(req)
    out = []
    for row in resp.rows or []:
        path = (row.dimension_values[0].value if row.dimension_values else "") or "(not set)"
        mets = _metric_map(row, LAND_METRICS)
        out.append(
            {
                "path": path,
                "path_display": path if path != "(not set)" else "untagged",
                "path_kind": _path_kind(path),
                "sessions": int(mets.get("sessions") or 0),
                "users": int(mets.get("totalUsers") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
                "bounce_rate_pct": _pct_rate(mets.get("bounceRate")),
                "avg_session_seconds": round(float(mets.get("averageSessionDuration") or 0), 1),
                "duration_metric": "averageSessionDuration",
                "market_guess": _infer_market(path),
            }
        )
    return out


def _merge_landing_duration(existing: list[dict[str, Any]], fresh: list[dict[str, Any]]) -> None:
    """Fill avg session duration on a frozen landing list without changing counts."""
    by_path = {str(p.get("path") or ""): p for p in fresh}
    for row in existing:
        src = by_path.get(str(row.get("path") or ""))
        if not src:
            continue
        if src.get("avg_session_seconds") is not None:
            row["avg_session_seconds"] = src.get("avg_session_seconds")
            row["duration_metric"] = "averageSessionDuration"


def main() -> int:
    _load_dotenv_quiet()
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or ""
    if not creds or not Path(creds).expanduser().is_file():
        fallback = REPO / "credentials" / "ga4-viewer-sa.json"
        if fallback.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(fallback)

    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, OrderBy, RunReportRequest

    client = BetaAnalyticsDataClient()
    us_id = resolve_ga4_property_id() or DEFAULT_GA4_PROPERTY_ID_US
    au_id = resolve_ga4_property_id_au()
    now: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window": f"{NOW_START} → {NOW_END}",
        "window_same_weekdays": f"{SAME_START} → {SAME_END}",
        "compare_note": "Same weekdays last week, not a full 7 vs 7. Thursday is partial in the US.",
        "property_id": us_id,
        "measurement_id_us": MEASUREMENT_ID_US,
    }
    us_ov = _overview(client, us_id, DateRange, Metric, RunReportRequest)
    now["totals_now"] = us_ov["now"]
    now["totals_same_weekdays"] = us_ov["same_weekdays"]
    now["top_landing_pages"] = _landings(client, us_id, DateRange, Dimension, Metric, OrderBy, RunReportRequest)
    us_frozen_land = _landings(
        client,
        us_id,
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
        start=GA4_WEEK_START,
        end=GA4_WEEK_END,
    )
    if au_id:
        au_ov = _overview(client, au_id, DateRange, Metric, RunReportRequest)
        now["au"] = {
            "ok": True,
            "property_id": au_id,
            "measurement_id": MEASUREMENT_ID_AU,
            "totals_now": au_ov["now"],
            "totals_same_weekdays": au_ov["same_weekdays"],
            "top_landing_pages": _landings(
                client, au_id, DateRange, Dimension, Metric, OrderBy, RunReportRequest
            ),
        }
        au_frozen_land = _landings(
            client,
            au_id,
            DateRange,
            Dimension,
            Metric,
            OrderBy,
            RunReportRequest,
            start=GA4_WEEK_START,
            end=GA4_WEEK_END,
        )
    else:
        au_frozen_land = []
    if OUT_GA4.is_file():
        ga4 = json.loads(OUT_GA4.read_text(encoding="utf-8"))
    else:
        ga4 = {}
    _merge_landing_duration(ga4.get("top_landing_pages") or [], us_frozen_land)
    _merge_landing_duration((ga4.get("au") or {}).get("top_landing_pages") or [], au_frozen_land)
    ga4["now"] = now
    OUT_GA4.write_text(json.dumps(ga4, indent=2) + "\n", encoding="utf-8")
    if OUT_EXEC.is_file():
        exec_snap = json.loads(OUT_EXEC.read_text(encoding="utf-8"))
        exec_snap.setdefault("ga4", {})
        exec_snap["ga4"]["now"] = now
        exec_snap["ga4_now_merged_at_utc"] = now["generated_at_utc"]
        OUT_EXEC.write_text(json.dumps(exec_snap, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "us_now": now.get("totals_now"),
        "us_same": now.get("totals_same_weekdays"),
        "au_now": (now.get("au") or {}).get("totals_now"),
        "landings": [p.get("path") for p in (now.get("top_landing_pages") or [])[:5]],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
