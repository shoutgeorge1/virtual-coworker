#!/usr/bin/env python3
"""Build xray/data/experiments-snapshot.json for the Site experiments tab.

No invented winners. Prefer real event counts when available:

1. Local event log (default): xray/data/experiments-events.json
   Schema: { "events": [ { "event": "experiment_view", "experiment_id": "...",
                           "experiment_variant": "a", ... }, ... ] }
   Or a bare JSON array of the same objects.

2. GA4 Data API when google-analytics-data is installed + ADC / service account
   works. Property ID: env GA4_PROPERTY_ID, else DEFAULT_GA4_PROPERTY_ID_US
   (G-2V3V0BS6JW → 549075481). On auth/API failure: keep inventory, set
   data_status to awaiting_source — do not invent numbers. Successful empty
   pull → live zeros (“wired, 0 events in window”).

Usage:
  export GA4_PROPERTY_ID=549075481   # optional; script default is the same US id
  python3 ads-launch/pull_experiments_snapshot.py
  python3 ads-launch/pull_experiments_snapshot.py --events path/to/events.json

Auth (prefer service account — durable for daily pulls / Automation):
  GOOGLE_APPLICATION_CREDENTIALS=/path/to/ga4-viewer-sa.json
  # SA email must be Viewer on the GA4 property (Admin → Property access management)
  # Avoid: gcloud auth application-default login (often blocked — unverified user OAuth)
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

# US property for measurement G-2V3V0BS6JW (Admin → Property settings).
# Prefer env GA4_PROPERTY_ID; this is the durable documented fallback (not a secret).
DEFAULT_GA4_PROPERTY_ID_US = "549075481"


def _load_dotenv_quiet() -> None:
    """Load repo .env / vision/.env.local into os.environ if present (no override)."""
    for path in (REPO / ".env", REPO / "vision" / ".env.local"):
        if not path.is_file():
            continue
        try:
            for raw in path.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                if not key or key in os.environ:
                    continue
                val = val.strip().strip("'").strip('"')
                os.environ[key] = val
        except OSError:
            continue


def resolve_ga4_property_id() -> str:
    return (os.environ.get("GA4_PROPERTY_ID") or "").strip() or DEFAULT_GA4_PROPERTY_ID_US


# Keep in sync with vision/lib/experiments.ts + SITE-EXPERIMENTS.md
# EXPERIMENTS_LIVE stays false; only SELECTIVE_LIVE_EXPERIMENTS run.
SELECTIVE_LIVE_IDS = frozenset({"us_hero_portrait"})

EXPERIMENT_DEFS: list[dict[str, Any]] = [
    {
        "id": "us_hero_portrait",
        "label": "US /us hero — female navy (a) vs male AU portrait (b)",
        "surface": "US hub /us hero photo only",
        "variants": ["a", "b"],
        "variant_labels": {
            "a": "Female navy · va-us.jpg (baseline control face)",
            "b": "Male portrait · va-au.jpg (challenger)",
        },
        "fires_click": False,
        "click_note": (
            "Views = experiment_view. Converts = experiment_convert (form success / phone). "
            "No experiment_click on this test — do not invent Ads image CTR."
        ),
        "preview_path": "/us",
        "baseline_note": (
            "Control arm A keeps the historic converting /us face. Form, copy, and tracking "
            "on the money LP are unchanged — hero photo only."
        ),
    },
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
            "a": "Who should you hire first",
            "b": "Take the quiz. See who to hire",
            "c": "Find the teammate that gets you your week back",
        },
        "fires_click": True,
        "click_note": "Teaser tap + quiz start / CTA → experiment_click",
    },
    {
        "id": "chat_launcher",
        "label": "Chat launcher label",
        "surface": "engage chat launcher",
        "variants": ["a", "b"],
        "variant_labels": {"a": "Chat with us", "b": "Chat — hiring help"},
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
    {
        "id": "role_imagery",
        "label": "Role / trust imagery — set A (defaults) vs set B",
        "surface": "services page + market LPs + late trust",
        "variants": ["a", "b"],
        "variant_labels": {"a": "set A (defaults)", "b": "set B (challenger)"},
        "fires_click": False,
        "click_note": "Imagery swap — views + convert rate matter more than click CTR",
    },
]

# Not random A/B — live creative swaps measured by URL CVR, not experiment_* arms.
LIVE_SWAPS: list[dict[str, Any]] = [
    {
        "id": "marketing_a_orange",
        "label": "Marketing A orange on marketing LPs",
        "kind": "live_swap",
        "status": "live",
        "surfaces": [
            "/us/digital-marketing",
            "/us/social-media",
        ],
        "asset": "/roles/marketing-a.png",
        "measure": (
            "Week-over-week form starts + leads on those URLs (GA4 / Zoho). "
            "Not random A/B — no experiment_id arms."
        ),
        "unavailable": [
            "Image-level Google Ads CTR for this face (Ads asset scores incomplete)",
            "experiment_view / experiment_convert split (not an experiment_* test)",
        ],
        "media_report_anchor": "media.html#live-tests",
    },
]

METRICS_AVAILABILITY = {
    "can_measure": [
        "experiment_view by experiment_id + experiment_variant (GA4 custom dims once registered)",
        "experiment_convert (form success / phone fan-out) by variant",
        "employer_form_started / employer_inquiry_submitted on URLs (page-level)",
        "Keyword / RSA CTR from Search ads (not image-level)",
    ],
    "unavailable": [
        "Image-level Google Ads impressions / clicks / CTR for hero faces",
        "Fake winners — empty cells mean not pulled yet, not zero traffic",
    ],
}

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


def try_ga4_pull() -> tuple[list[dict[str, Any]], str | None, bool]:
    """GA4 Data API.

    Returns (events, note, connected).
    connected=True means auth + property query worked (events may be empty).
    """
    property_id = resolve_ga4_property_id()
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange,
            Dimension,
            Metric,
            RunReportRequest,
        )
    except ImportError:
        return [], "google-analytics-data not installed — pip install google-analytics-data", False

    try:
        client = BetaAnalyticsDataClient()
        prop = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
        events_out: list[dict[str, Any]] = []

        # Prefer variant breakdown via event-scoped custom dimensions.
        try:
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
            return events_out, "Connected", True
        except Exception as dim_exc:  # noqa: BLE001
            # If custom dims missing, still prove connectivity + raw event counts.
            try:
                raw_total = 0
                for event_name in ("experiment_view", "experiment_click", "experiment_convert"):
                    req = RunReportRequest(
                        property=prop,
                        date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
                        dimensions=[Dimension(name="eventName")],
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
                        raw_total += int(row.metric_values[0].value) if row.metric_values else 0
                note = (
                    f"Connected to {property_id}; custom dims experiment_id/experiment_variant "
                    f"not queryable yet ({dim_exc}). Raw experiment_* eventCount in window: {raw_total}. "
                    "Register those event params as custom dimensions in GA4 Admin, then re-pull."
                )
                return [], note, True
            except Exception as exc:  # noqa: BLE001
                return [], f"GA4 pull failed: {exc}", False
    except Exception as exc:  # noqa: BLE001 — never crash; surface note
        return [], f"GA4 pull failed: {exc}", False


def build_snapshot(
    counts: dict[str, dict[str, dict[str, int]]] | None,
    *,
    source: str,
    source_note: str,
    data_status: str,
    window: str | None,
    ga4_note: str | None = None,
) -> dict[str, Any]:
    # None = not pulled yet (dashes). Dict (even empty) = pulled → show zeros.
    has_data = counts is not None
    experiments: list[dict[str, Any]] = []
    total_views = total_clicks = total_converts = 0

    for defn in EXPERIMENT_DEFS:
        exp_id = defn["id"]
        metrics_by_variant: dict[str, dict[str, Any]] = {}
        for v in defn["variants"]:
            if has_data and counts is not None:
                raw = counts.get(exp_id, {}).get(v, {"views": 0, "clicks": 0, "converts": 0})
                views, clicks, converts = raw["views"], raw["clicks"], raw["converts"]
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

        status = "live" if exp_id in SELECTIVE_LIVE_IDS else "parked"
        experiments.append(
            {
                **defn,
                "status": status,
                "winner": None,
                "metrics_by_variant": metrics_by_variant,
            }
        )

    # Live-only totals so parked zeros don't drown the running board.
    live_views = live_clicks = live_converts = 0
    if has_data and counts is not None:
        for exp_id in SELECTIVE_LIVE_IDS:
            for v_counts in counts.get(exp_id, {}).values():
                live_views += v_counts.get("views", 0)
                live_clicks += v_counts.get("clicks", 0)
                live_converts += v_counts.get("converts", 0)

    if has_data:
        totals = {
            "views": total_views,
            "clicks": total_clicks,
            "ctr_pct": rate(total_clicks, total_views),
            "converts": total_converts,
        }
        live_totals = {
            "views": live_views,
            "clicks": live_clicks,
            "ctr_pct": rate(live_clicks, live_views),
            "converts": live_converts,
        }
    else:
        totals = {
            "views": None,
            "clicks": None,
            "ctr_pct": None,
            "converts": None,
        }
        live_totals = {
            "views": None,
            "clicks": None,
            "ctr_pct": None,
            "converts": None,
        }

    prop = resolve_ga4_property_id()
    if source == "ga4" and has_data and live_views == 0 and live_clicks == 0:
        scoreboard_next = (
            f"US GA4 property {prop} connected. Selective live us_hero_portrait has "
            "0 experiment_* events with variant breakdown in the pull window — not broken. "
            "Register custom dims experiment_id / experiment_variant in GA4 Admin if needed, "
            "then re-run ads-launch/pull_experiments_snapshot.py and redeploy xray."
        )
    elif source == "ga4":
        scoreboard_next = (
            f"US scoreboard pulling from property {prop}. Re-run "
            "ads-launch/pull_experiments_snapshot.py after traffic; redeploy xray. "
            "AU GTM still missing."
        )
    else:
        scoreboard_next = (
            f"Property id ready ({prop} for G-2V3V0BS6JW). Run "
            "ads-launch/pull_experiments_snapshot.py with ADC "
            "(`gcloud auth application-default login`) or a service account JSON, "
            "OR drop an export at xray/data/experiments-events.json. Redeploy xray. "
            "AU GTM still missing — do not invent AU ids."
        )

    prior: dict[str, Any] = {}
    if OUT.is_file():
        try:
            prior = json.loads(OUT.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}

    snap: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": source,
        "source_note": source_note,
        "primary_kpi": "views_and_converts",
        "primary_kpi_note": (
            "For us_hero_portrait: views = experiment_view, converts = experiment_convert. "
            "CTR only when experiment_click fires (most parked tests). "
            "Image-level Ads CTR is unavailable — do not invent it."
        ),
        "window": window,
        "data_status": data_status,
        "experiments_live_master": False,
        "selective_live": sorted(SELECTIVE_LIVE_IDS),
        "baseline": {
            "path": "/us",
            "label": "Paid LP baseline · control",
            "note": (
                "Money LP form, copy, and tracking stay frozen. "
                "Only the /us hero portrait is in a selective 50/50. "
                "EXPERIMENTS_LIVE remains false globally."
            ),
            "control_variant": "a",
            "control_asset": "/brand/va-us.jpg",
        },
        "metrics_availability": METRICS_AVAILABILITY,
        "events": {
            "view": "experiment_view",
            "click": "experiment_click",
            "convert": "experiment_convert",
            "payload_fields": ["experiment_id", "experiment_variant", "convert_reason"],
        },
        "assist_events": ASSIST_EVENTS,
        "wiring": {
            "us_gtm": "GTM-M92DX9BJ",
            "us_ga4_measurement": "G-2V3V0BS6JW",
            "us_ga4_property_id": prop,
            "us_datalayer_experiment_events": "confirmed",
            "us_ga4_experiment_bridge": (
                "MarketGtm installs collect sendBeacon for experiment_* "
                "(GTM alone only sent page_view; gtag event is swallowed under GTM)"
            ),
            "au_gtm": "missing",
            "au_ga4": "missing",
            "au_blocker": (
                "Need a new Australia GTM container ID + GA4 measurement ID for the microsite. "
                "Paste into Vercel as NEXT_PUBLIC_GTM_AU and NEXT_PUBLIC_GA4_AU. "
                "Do not reuse US GTM-M92DX9BJ or legacy WP GTM-KNDLKVW."
            ),
            "homepage_h1": "locked — do not A/B until George asks",
            "scoreboard_next": scoreboard_next,
        },
        "ga4": {
            "connected": source == "ga4",
            "property_id": prop,
            "measurement_id_us": "G-2V3V0BS6JW",
            "note": ga4_note
            or (
                f"Using property {prop}. Set GA4_PROPERTY_ID to override. "
                "Needs ADC (`gcloud auth application-default login`) or "
                "GOOGLE_APPLICATION_CREDENTIALS service account with Viewer on the property."
            ),
        },
        "totals": totals,
        "live_totals": live_totals,
        "live_swaps": LIVE_SWAPS,
        "experiments": experiments,
        "docs": {
            "site": "vision/docs/SITE-EXPERIMENTS.md",
            "module": "vision/lib/experiments.ts",
            "see_in_ga4": (
                "GA4 → Admin → DebugView (or Reports → Realtime → Events) on property "
                f"{prop} (G-2V3V0BS6JW). Look for experiment_view / experiment_click / "
                "experiment_convert with params experiment_id + experiment_variant."
            ),
            "xray_tab": "ab-tests.html",
            "media_report": "media.html#live-tests",
        },
    }

    # Preserve hand-authored Ads expansion notes if present.
    if isinstance(prior.get("us_exact_phrase_expansion"), dict):
        snap["us_exact_phrase_expansion"] = prior["us_exact_phrase_expansion"]

    return snap


def main() -> int:
    _load_dotenv_quiet()
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
        help="Do not attempt GA4 Data API (local events / inventory only)",
    )
    args = parser.parse_args()

    prop = resolve_ga4_property_id()
    events = load_events(args.events)
    source = "local_events"
    source_note = f"Aggregated from {args.events.relative_to(REPO)}"
    data_status = "live"
    window = "local_file"
    ga4_note = None
    ga4_connected = False

    if not events and not args.skip_ga4:
        ga4_events, ga4_note_out, ga4_connected = try_ga4_pull()
        ga4_note = ga4_note_out
        if ga4_connected:
            events = ga4_events
            source = "ga4"
            window = "28daysAgo → today"
            if events:
                source_note = (
                    f"Aggregated from GA4 Data API property {prop} "
                    "(customEvent:experiment_id / experiment_variant)"
                )
            else:
                source_note = (
                    f"GA4 property {prop} connected — 0 experiment_* events with variant "
                    "breakdown in window (28daysAgo → today). Wired, not broken."
                )

    if ga4_connected:
        snap = build_snapshot(
            aggregate(events),
            source=source,
            source_note=source_note,
            data_status="live",
            window=window,
            ga4_note=ga4_note,
        )
    elif events:
        snap = build_snapshot(
            aggregate(events),
            source=source,
            source_note=source_note,
            data_status=data_status,
            window=window,
            ga4_note=ga4_note,
        )
    else:
        snap = build_snapshot(
            None,
            source="inventory_only",
            source_note=(
                f"US dataLayer + gtag bridge fire experiment_view/click/convert on /us. "
                f"Property id {prop} (G-2V3V0BS6JW) is set for the pull path; "
                "scoreboard numbers need a successful GA4 API auth or a local export "
                "at xray/data/experiments-events.json. "
                "AU GTM still missing — no visit tags on /au."
            ),
            data_status="awaiting_source",
            window=None,
            ga4_note=ga4_note,
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT.relative_to(REPO)} · status={snap['data_status']} · "
        f"source={snap['source']} · property={prop}"
    )
    if ga4_note:
        print(f"GA4 note: {ga4_note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
