#!/usr/bin/env python3
"""Build xray/data/experiments-snapshot.json for the Site experiments tab.

No invented winners. Prefer real event counts when available:

1. Local event log (default): xray/data/experiments-events.json
   Schema: { "events": [ { "event": "experiment_view", "experiment_id": "...",
                           "experiment_variant": "a", ... }, ... ] }
   Or a bare JSON array of the same objects.

2. Optional GA4 Data API when GA4_PROPERTY_ID is set and google-analytics-data
   is installed + ADC/service account works. On auth/API failure: keep inventory,
   set data_status to awaiting_source — do not invent numbers.

Usage:
  python3 ads-launch/pull_experiments_snapshot.py
  python3 ads-launch/pull_experiments_snapshot.py --events path/to/events.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "xray" / "data" / "experiments-snapshot.json"
DEFAULT_EVENTS = REPO / "xray" / "data" / "experiments-events.json"

# Keep in sync with vision/lib/experiments.ts + SITE-EXPERIMENTS.md
EXPERIMENT_DEFS: list[dict[str, Any]] = [
    {
        "id": "exit_popup",
        "label": "Exit / timed popup copy",
        "surface": "employer LP popup",
        "variants": ["a", "b", "c"],
        "variant_labels": {
            "a": "Skip Upwork roulette",
            "b": "Tired of hiring that eats your week",
            "c": "One clear seat",
        },
        "fires_click": True,
        "click_note": "Hire / job / phone CTAs → experiment_click",
    },
    {
        "id": "quiz_copy",
        "label": "Quiz teaser + reward framing",
        "surface": "hero teaser + role quiz",
        "variants": ["a", "b", "c"],
        "variant_labels": {
            "a": "Get your week back",
            "b": "Stop guessing your next hire",
            "c": "Which hire buys back the most time",
        },
        "fires_click": True,
        "click_note": "Teaser tap + quiz start / CTA → experiment_click",
    },
    {
        "id": "chat_launcher",
        "label": "Chat launcher label",
        "surface": "engage chat launcher",
        "variants": ["a", "b"],
        "variant_labels": {"a": "Label A", "b": "Label B"},
        "fires_click": True,
        "click_note": "Open chat → experiment_click",
    },
    {
        "id": "gate_headline",
        "label": "Form gate headline",
        "surface": "LeadGate card title",
        "variants": ["a", "b"],
        "variant_labels": {"a": "Headline A", "b": "Headline B"},
        "fires_click": False,
        "click_note": "Views fire; no dedicated experiment_click yet — use form_start / convert once GA4 is wired",
    },
    {
        "id": "lp_density",
        "label": "Landing density — wordy (a) vs lean (b)",
        "surface": "market landing page body",
        "variants": ["a", "b"],
        "variant_labels": {"a": "wordy", "b": "lean"},
        "fires_click": False,
        "click_note": "Density test — same CTAs both arms. Primary later KPI: form_start / convert rate, not click CTR",
    },
]

ASSIST_EVENTS = [
    {"event": "exit_intent_shown", "maps_to": "exit_popup view assist"},
    {"event": "conversion_assist_cta_clicked", "maps_to": "exit_popup click assist"},
    {"event": "quiz_started", "maps_to": "quiz_copy engagement"},
    {"event": "lead_magnet_completed", "maps_to": "quiz_copy complete"},
    {"event": "chat_opened", "maps_to": "chat_launcher open"},
    {"event": "employer_form_started", "maps_to": "gate / density form start"},
    {"event": "phone_cta_clicked", "maps_to": "phone click (also fans out experiment_convert)"},
    {"event": "employer_inquiry_submitted", "maps_to": "form success (also fans out experiment_convert)"},
]


def empty_metrics() -> dict[str, Any]:
    return {
        "views": None,
        "clicks": None,
        "ctr_pct": None,
        "converts": None,
        "convert_rate_pct": None,
    }


def rate(numer: int | None, denom: int | None) -> float | None:
    if numer is None or denom is None or denom <= 0:
        return None
    return round(100.0 * numer / denom, 2)


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return [e for e in raw if isinstance(e, dict)]
    if isinstance(raw, dict):
        events = raw.get("events") or raw.get("rows") or []
        return [e for e in events if isinstance(e, dict)]
    return []


def aggregate(events: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, int]]]:
    """id → variant → {views, clicks, converts}"""
    out: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"views": 0, "clicks": 0, "converts": 0})
    )
    for row in events:
        name = str(row.get("event") or row.get("event_name") or "").strip()
        exp_id = str(row.get("experiment_id") or "").strip()
        variant = str(row.get("experiment_variant") or "").strip().lower()
        if not exp_id or variant not in ("a", "b", "c"):
            # GA4-style nested params
            params = row.get("event_params") or row.get("params") or {}
            if isinstance(params, dict):
                exp_id = exp_id or str(params.get("experiment_id") or "").strip()
                variant = variant or str(params.get("experiment_variant") or "").strip().lower()
        if not exp_id or variant not in ("a", "b", "c"):
            continue
        bucket = out[exp_id][variant]
        if name == "experiment_view":
            bucket["views"] += int(row.get("count") or row.get("eventCount") or 1)
        elif name == "experiment_click":
            bucket["clicks"] += int(row.get("count") or row.get("eventCount") or 1)
        elif name == "experiment_convert":
            bucket["converts"] += int(row.get("count") or row.get("eventCount") or 1)
    return out


def try_ga4_pull() -> tuple[list[dict[str, Any]], str | None]:
    """Optional GA4 Data API. Returns (events, error_note)."""
    property_id = (os.environ.get("GA4_PROPERTY_ID") or "").strip()
    if not property_id:
        return [], None
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
    except ImportError:
        return [], "google-analytics-data not installed — use local events JSON"

    try:
        client = BetaAnalyticsDataClient()
        prop = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
        events_out: list[dict[str, Any]] = []
        for event_name in ("experiment_view", "experiment_click", "experiment_convert"):
            req = RunReportRequest(
                property=prop,
                date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
                dimensions=[
                    Dimension(name="eventName"),
                    Dimension(name="customEvent:experiment_id"),
                    Dimension(name="customEvent:experiment_variant"),
                ],
                metrics=[Metric(name="eventCount")],
                dimension_filter={
                    "filter": {
                        "field_name": "eventName",
                        "string_filter": {"value": event_name},
                    }
                },
            )
            resp = client.run_report(req)
            for row in resp.rows:
                dims = [d.value for d in row.dimension_values]
                count = int(row.metric_values[0].value) if row.metric_values else 0
                events_out.append(
                    {
                        "event": dims[0] if dims else event_name,
                        "experiment_id": dims[1] if len(dims) > 1 else "",
                        "experiment_variant": dims[2] if len(dims) > 2 else "",
                        "count": count,
                    }
                )
        return events_out, None
    except Exception as exc:  # noqa: BLE001 — stub: never crash; surface note
        return [], f"GA4 pull failed: {exc}"


def build_snapshot(
    counts: dict[str, dict[str, dict[str, int]]] | None,
    *,
    source: str,
    source_note: str,
    data_status: str,
    window: str | None,
    ga4_note: str | None = None,
) -> dict[str, Any]:
    has_data = bool(counts)
    experiments: list[dict[str, Any]] = []
    total_views = total_clicks = total_converts = 0
    saw_any = False

    for defn in EXPERIMENT_DEFS:
        exp_id = defn["id"]
        metrics_by_variant: dict[str, dict[str, Any]] = {}
        for v in defn["variants"]:
            if has_data and counts is not None:
                raw = counts.get(exp_id, {}).get(v, {"views": 0, "clicks": 0, "converts": 0})
                views, clicks, converts = raw["views"], raw["clicks"], raw["converts"]
                saw_any = True
                total_views += views
                total_clicks += clicks
                total_converts += converts
                metrics_by_variant[v] = {
                    "views": views,
                    "clicks": clicks,
                    "ctr_pct": rate(clicks, views),
                    "converts": converts,
                    "convert_rate_pct": rate(converts, views),
                }
            else:
                metrics_by_variant[v] = empty_metrics()

        experiments.append(
            {
                **defn,
                "status": "active",
                "winner": None,
                "metrics_by_variant": metrics_by_variant,
            }
        )

    if has_data and saw_any:
        totals = {
            "views": total_views,
            "clicks": total_clicks,
            "ctr_pct": rate(total_clicks, total_views),
            "converts": total_converts,
        }
    else:
        totals = {
            "views": None,
            "clicks": None,
            "ctr_pct": None,
            "converts": None,
        }

    prop = (os.environ.get("GA4_PROPERTY_ID") or "").strip() or None
    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "source_note": source_note,
        "primary_kpi": "ctr",
        "primary_kpi_note": (
            "CTR = experiment_click ÷ experiment_view (by experiment_id + experiment_variant). "
            "Conversions column is reserved — experiment_convert already fires on form_submit / phone_click."
        ),
        "window": window,
        "data_status": data_status,
        "events": {
            "view": "experiment_view",
            "click": "experiment_click",
            "convert": "experiment_convert",
            "payload_fields": ["experiment_id", "experiment_variant", "convert_reason"],
        },
        "assist_events": ASSIST_EVENTS,
        "ga4": {
            "connected": source == "ga4",
            "property_id": prop,
            "note": ga4_note
            or "Set GA4_PROPERTY_ID + ADC / service account, or place events at xray/data/experiments-events.json",
        },
        "totals": totals,
        "experiments": experiments,
        "docs": {
            "site": "vision/docs/SITE-EXPERIMENTS.md",
            "module": "vision/lib/experiments.ts",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull / build experiments snapshot for xray")
    parser.add_argument(
        "--events",
        type=Path,
        default=DEFAULT_EVENTS,
        help="Local events JSON path (default: xray/data/experiments-events.json)",
    )
    parser.add_argument(
        "--skip-ga4",
        action="store_true",
        help="Do not attempt GA4 Data API even if GA4_PROPERTY_ID is set",
    )
    args = parser.parse_args()

    events = load_events(args.events)
    source = "local_events"
    source_note = f"Aggregated from {args.events.relative_to(REPO)}"
    data_status = "live"
    window = "local_file"
    ga4_note = None

    if not events and not args.skip_ga4:
        ga4_events, ga4_err = try_ga4_pull()
        if ga4_events:
            events = ga4_events
            source = "ga4"
            source_note = "Aggregated from GA4 Data API (customEvent:experiment_id / experiment_variant)"
            window = "28daysAgo → today"
            ga4_note = "Connected"
        elif ga4_err:
            ga4_note = ga4_err

    if not events:
        snap = build_snapshot(
            None,
            source="inventory_only",
            source_note=(
                "No live event counts yet. Microsite already pushes experiment_view / "
                "experiment_click / experiment_convert to dataLayer. "
                "Drop a GA4 export at xray/data/experiments-events.json or set GA4_PROPERTY_ID."
            ),
            data_status="awaiting_source",
            window=None,
            ga4_note=ga4_note,
        )
    else:
        snap = build_snapshot(
            aggregate(events),
            source=source,
            source_note=source_note,
            data_status=data_status,
            window=window,
            ga4_note=ga4_note,
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(REPO)} · status={snap['data_status']} · source={snap['source']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
