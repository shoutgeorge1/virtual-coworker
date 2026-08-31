#!/usr/bin/env python3
"""High-level GA4 pull for Executive (GA4 Data API — not Google Ads API).

US: 5 RunReport requests. AU (optional): 3 more — overview, landings, channels.
Writes:
  - xray/data/ga4-snapshot.json  (US at top level; `au` is a separate block)
  - merges `ga4` into xray/data/executive-snapshot.json (preserves Ads rows)

Do not blend US + AU into one total.

Also refreshes experiments snapshot via pull_experiments_snapshot (separate
GA4 calls for experiment_* — optional with --skip-experiments).

Usage:
  .venv/bin/python ads-launch/pull_ga4_executive.py
  .venv/bin/python ads-launch/pull_ga4_executive.py --skip-experiments

Auth: GA4_PROPERTY_ID (US) + optional GA4_PROPERTY_ID_AU +
GOOGLE_APPLICATION_CREDENTIALS (repo .env). Same Viewer SA for both.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUT_GA4 = REPO / "xray" / "data" / "ga4-snapshot.json"
OUT_EXEC = REPO / "xray" / "data" / "executive-snapshot.json"
DEFAULT_GA4_PROPERTY_ID_US = "549075481"
MEASUREMENT_ID_US = "G-2V3V0BS6JW"
MEASUREMENT_ID_AU = "G-7X1K9V2LFE"

# Cap: overview + landings + channels + device + events = 5 (US)
MAX_REPORTS = 5
# AU extra: overview + landings + channels (no device/events)
MAX_REPORTS_AU = 3
# Same face week as Executive Ads (not rolling 7daysAgo).
GA4_WEEK_START = "2026-08-17"
GA4_WEEK_END = "2026-08-23"
GA4_WINDOW_LABEL = f"{GA4_WEEK_START} → {GA4_WEEK_END}"
GA4_PRIOR_START = "2026-08-10"
GA4_PRIOR_END = "2026-08-16"
GA4_PRIOR_LABEL = f"{GA4_PRIOR_START} → {GA4_PRIOR_END}"
THIS_RANGE = "date_range_0"
PRIOR_RANGE = "date_range_1"


def _range_key(row: Any, extra_dims: int) -> str:
    dvs = list(row.dimension_values or [])
    if len(dvs) > extra_dims:
        return dvs[-1].value or THIS_RANGE
    return THIS_RANGE


def _week_date_ranges(DateRange: Any) -> list:
    return [
        DateRange(start_date=GA4_WEEK_START, end_date=GA4_WEEK_END),
        DateRange(start_date=GA4_PRIOR_START, end_date=GA4_PRIOR_END),
    ]


def _load_dotenv_quiet() -> None:
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
                os.environ[key] = val.strip().strip("'").strip('"')
        except OSError:
            continue


def resolve_ga4_property_id() -> str:
    return (os.environ.get("GA4_PROPERTY_ID") or "").strip() or DEFAULT_GA4_PROPERTY_ID_US


def resolve_ga4_property_id_au() -> str:
    return (os.environ.get("GA4_PROPERTY_ID_AU") or "").strip()


def _plain_ga4_error(exc: BaseException) -> str:
    msg = str(exc)
    name = type(exc).__name__
    if (
        "PERMISSION_DENIED" in msg
        or "403" in msg
        or name in ("PermissionDenied", "Forbidden")
    ):
        return (
            "Permission denied on the AU GA4 property. The Viewer grant may need a few "
            "minutes, or the service account is not actually on this property."
        )
    return msg


def _metric_map(row: Any, metric_names: list[str]) -> dict[str, float | int]:
    out: dict[str, float | int] = {}
    for i, name in enumerate(metric_names):
        raw = row.metric_values[i].value if i < len(row.metric_values) else "0"
        try:
            if "." in str(raw):
                out[name] = float(raw)
            else:
                out[name] = int(raw)
        except ValueError:
            out[name] = 0
    return out


def _pct_rate(raw: float | int | None) -> float | None:
    """GA4 engagementRate / bounceRate often arrive as 0–1 fractions."""
    if raw is None:
        return None
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    if v <= 1.0:
        return round(100.0 * v, 1)
    return round(v, 1)


def _infer_market(path: str) -> str:
    p = (path or "").lower().split("?")[0]
    if p == "/au" or p.startswith("/au/"):
        return "AU"
    if p == "/us" or p.startswith("/us/"):
        return "US"
    if p == "/ph" or p.startswith("/ph/"):
        return "PH"
    return "other"


def _path_kind(path: str) -> str:
    p = (path or "").lower().split("?")[0].rstrip("/") or "/"
    if p in ("", "(not set)", "(empty path)"):
        return "unknown"
    if p == "/us":
        return "us_home"
    if p.startswith("/us/quiz"):
        return "quiz"
    if p.startswith("/us/"):
        return "role_lp"
    if p == "/au" or p.startswith("/au/"):
        return "au"
    if p == "/thank-you" or p.startswith("/thank-you"):
        return "thank_you"
    if p in ("/", "/how-it-works", "/services", "/privacy", "/terms"):
        return "other_site"
    return "other"


def _nice_path(path: str) -> str:
    p = (path or "").strip()
    if not p or p == "(empty path)":
        return "untagged"
    if p == "(not set)":
        return "untagged"
    return p


def _is_garbage_landing(path: str) -> bool:
    p = (path or "").strip().lower()
    return p in ("", "(empty path)", "(not set)", "(not set)", "untagged")


def build_insights(
    *,
    last7: dict[str, Any],
    landings: list[dict[str, Any]],
    channels: list[dict[str, Any]],
    devices: list[dict[str, Any]],
    devices_by_channel: list[dict[str, Any]],
    events: list[dict[str, Any]],
    market_sessions: dict[str, int],
    notes: list[str],
) -> list[str]:
    """Plain-English why bullets — no invented conversions, no obvious restates."""
    insights: list[str] = []
    s7 = int(last7.get("sessions") or 0)
    eng_rate = last7.get("engagement_rate_pct")
    bounce = last7.get("bounce_rate_pct")
    _ = events  # kept for callers; not lectured on Executive
    _ = notes

    home = next((L for L in landings if L.get("path_kind") == "us_home"), None)
    roles = [L for L in landings if L.get("path_kind") == "role_lp"]
    role_sess = sum(int(L.get("sessions") or 0) for L in roles)

    # Why: ads Final URLs still mostly hub, not role LPs
    if home and role_sess >= 0 and s7:
        home_sess = int(home.get("sessions") or 0)
        if home_sess >= role_sess * 2:
            insights.append(
                "Most paid clicks still open the US home page — role ads exist, but "
                "Final URLs haven’t shifted traffic onto role pages yet."
            )

    # Sales 75% — short hypothesis, small sample, don’t overclaim retention
    sales = next(
        (L for L in roles if (L.get("path") or "").rstrip("/") == "/us/sales"),
        None,
    )
    if sales and home:
        sales_eng = sales.get("engagement_rate_pct")
        home_eng = home.get("engagement_rate_pct")
        sales_n = int(sales.get("sessions") or 0)
        if (
            sales_eng is not None
            and home_eng is not None
            and sales_n >= 3
            and sales_eng >= home_eng + 15
        ):
            insights.append(
                f"/us/sales: {sales_eng:.0f}% stayed and looked around "
                f"({sales_n} visits) vs /us at {home_eng:.0f}% — maybe the sales pitch "
                "matches the search better. Tiny sample; not “retention.”"
            )

    paid = next((c for c in channels if "paid" in (c.get("channel") or "").lower()), None)
    direct = next((c for c in channels if (c.get("channel") or "") == "Direct"), None)
    if direct and int(direct.get("sessions") or 0) >= 10:
        d_n = int(direct.get("sessions") or 0)
        p_n = int((paid or {}).get("sessions") or 0)
        insights.append(
            f"“Direct” is {d_n} sessions (Paid Search {p_n}): typed URL, bookmarks, "
            "team checks, and some paid clicks that lose the ad tag — not mysterious "
            "organic growth."
        )

    if eng_rate is not None and bounce is not None:
        insights.append(
            f"About {eng_rate:.0f}% stayed and looked around; "
            f"{bounce:.0f}% left right away. (Website behavior — not Ad CTR.)"
        )

    # Device: use Paid Search split when available — George expects ~80% mobile
    paid_dev = [
        r
        for r in (devices_by_channel or [])
        if "paid" in (r.get("channel") or "").lower()
    ]
    paid_m = sum(
        int(r.get("sessions") or 0)
        for r in paid_dev
        if (r.get("device") or "").lower() == "mobile"
    )
    paid_d = sum(
        int(r.get("sessions") or 0)
        for r in paid_dev
        if (r.get("device") or "").lower() == "desktop"
    )
    paid_tot = paid_m + paid_d
    mobile = next((d for d in devices if (d.get("device") or "").lower() == "mobile"), None)
    desktop = next((d for d in devices if (d.get("device") or "").lower() == "desktop"), None)
    if paid_tot >= 20:
        m_pct = round(100.0 * paid_m / paid_tot)
        if m_pct < 55:
            insights.append(
                f"Paid Search device split: {m_pct}% mobile / {100 - m_pct}% desktop "
                f"({paid_m} vs {paid_d}). Expected ~80% mobile for search ads — "
                "worth checking Ads device reports + whether mobile LP feels broken. "
                "Site viewport/sticky CTA look fine; early sample may still skew."
            )
        elif m_pct < 70:
            insights.append(
                f"Paid Search is {m_pct}% mobile ({paid_m} vs {paid_d} desktop) — "
                "closer to normal search mix than site-wide, but not the ~80% we’d "
                "expect yet. Small pilot; watch next week."
            )
        else:
            insights.append(
                f"Paid Search is mostly mobile ({m_pct}% — {paid_m} vs {paid_d} desktop), "
                "as expected for search ads."
            )
    elif mobile and desktop and s7:
        m = int(mobile.get("sessions") or 0)
        d = int(desktop.get("sessions") or 0)
        insights.append(
            f"Site-wide devices: desktop {d} vs mobile {m}. Direct/team traffic can "
            "inflate desktop — check Paid Search device split before calling a mobile bug."
        )

    if int(market_sessions.get("AU") or 0) == 0:
        insights.append(
            "This US property has no /au landings — Australia tags go to a separate AU property."
        )

    return insights[:7]


def pull_ga4_au(client: Any, property_id: str) -> dict[str, Any]:
    """AU property only — 3 RunReports. Do not mix into US totals."""
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    prop = (
        property_id
        if property_id.startswith("properties/")
        else f"properties/{property_id}"
    )
    calls: list[dict[str, Any]] = []
    notes: list[str] = []
    insights: list[str] = []

    overview_metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "conversions",
        "averageSessionDuration",
    ]
    resp1 = client.run_report(
        RunReportRequest(
            property=prop,
            date_ranges=_week_date_ranges(DateRange),
            metrics=[Metric(name=m) for m in overview_metrics],
        )
    )
    calls.append({"n": 1, "name": "au_overview", "ok": True})
    last7_raw: dict[str, Any] = {m: 0 for m in overview_metrics}
    prior_raw: dict[str, Any] = {m: 0 for m in overview_metrics}
    for row in resp1.rows or []:
        mets = _metric_map(row, overview_metrics)
        if _range_key(row, 0) == PRIOR_RANGE:
            prior_raw = mets
        else:
            last7_raw = mets
    sess = int(last7_raw.get("sessions") or 0)
    eng = int(last7_raw.get("engagedSessions") or 0)
    last7 = {
        "sessions": sess,
        "users": int(last7_raw.get("totalUsers") or 0),
        "engaged_sessions": eng,
        "engagement_rate_pct": _pct_rate(last7_raw.get("engagementRate")),
        "bounce_rate_pct": _pct_rate(last7_raw.get("bounceRate")),
        "conversions": float(last7_raw.get("conversions") or 0),
        "avg_session_seconds": round(float(last7_raw.get("averageSessionDuration") or 0), 1),
    }
    prior7 = {
        "sessions": int(prior_raw.get("sessions") or 0),
        "users": int(prior_raw.get("totalUsers") or 0),
        "engaged_sessions": int(prior_raw.get("engagedSessions") or 0),
        "engagement_rate_pct": _pct_rate(prior_raw.get("engagementRate")),
        "bounce_rate_pct": _pct_rate(prior_raw.get("bounceRate")),
        "conversions": float(prior_raw.get("conversions") or 0),
        "avg_session_seconds": round(float(prior_raw.get("averageSessionDuration") or 0), 1),
    }

    land_metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "averageSessionDuration",
    ]
    resp2 = client.run_report(
        RunReportRequest(
            property=prop,
            date_ranges=[DateRange(start_date=GA4_WEEK_START, end_date=GA4_WEEK_END)],
            dimensions=[Dimension(name="landingPage")],
            metrics=[Metric(name=m) for m in land_metrics],
            order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
            limit=15,
        )
    )
    calls.append({"n": 2, "name": "au_landing_pages", "ok": True})

    landings: list[dict[str, Any]] = []
    au_path_sessions = 0
    thank_you_sessions = 0
    for row in resp2.rows or []:
        path = row.dimension_values[0].value if row.dimension_values else "(not set)"
        if path is None or str(path).strip() == "":
            path = "(empty path)"
        mets = _metric_map(row, land_metrics)
        kind = _path_kind(path)
        sessions = int(mets.get("sessions") or 0)
        if kind == "au":
            au_path_sessions += sessions
        if kind == "thank_you":
            thank_you_sessions += sessions
        landings.append(
            {
                "path": path,
                "path_display": _nice_path(path),
                "path_kind": kind,
                "sessions": sessions,
                "users": int(mets.get("totalUsers") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
                "bounce_rate_pct": _pct_rate(mets.get("bounceRate")),
                "avg_session_seconds": round(float(mets.get("averageSessionDuration") or 0), 1),
                "duration_metric": "averageSessionDuration",
                "market_guess": _infer_market(path),
            }
        )

    ch_metrics = ["sessions", "totalUsers", "engagedSessions", "engagementRate"]
    resp3 = client.run_report(
        RunReportRequest(
            property=prop,
            date_ranges=_week_date_ranges(DateRange),
            dimensions=[Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name=m) for m in ch_metrics],
            order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
            limit=20,
        )
    )
    calls.append({"n": 3, "name": "au_channels", "ok": True})

    channels: list[dict[str, Any]] = []
    paid_search_sessions_prior = 0
    for row in resp3.rows or []:
        ch = row.dimension_values[0].value if row.dimension_values else "(not set)"
        mets = _metric_map(row, ch_metrics)
        rng = _range_key(row, 1)
        sess_n = int(mets.get("sessions") or 0)
        if rng == PRIOR_RANGE:
            if "paid" in (ch or "").lower():
                paid_search_sessions_prior += sess_n
            continue
        channels.append(
            {
                "channel": ch,
                "sessions": sess_n,
                "users": int(mets.get("totalUsers") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
            }
        )

    paid = next(
        (c for c in channels if "paid" in (c.get("channel") or "").lower()),
        None,
    )
    paid_n = int((paid or {}).get("sessions") or 0)
    paid_eng = (paid or {}).get("engagement_rate_pct")

    if sess == 0:
        notes.append(
            "No sessions in the last 7 days. Australia tags only went live around "
            "12 Aug 2026 — empty is expected if ads have not yet hit this property."
        )
        insights.append(
            "AU property looks empty so far — tags only live since ~12 Aug, not proof ads are failing."
        )
    else:
        if au_path_sessions:
            notes.append(
                f"/au pages received {au_path_sessions} landing visits — tags are firing "
                "on the Australia microsite."
            )
        else:
            notes.append(
                "Traffic in this AU property did not land on /au paths — check the stream "
                "is the Australia pages."
            )
        if paid_n:
            notes.append(
                f"Paid Google ads visits: {paid_n} (the useful volume). "
                "Thank-you / form hits are likely internal testing, not leads."
            )
        else:
            notes.append(
                "Some site traffic, but no paid Google ads visits yet — likely team checks, not ads."
            )
        if thank_you_sessions:
            notes.append(
                f"{thank_you_sessions} thank-you landings — treat as George/sales/agent tests, not leads."
            )
        if last7.get("engagement_rate_pct") is not None:
            insights.append(
                f"About {last7['engagement_rate_pct']:.0f}% stayed and looked around "
                f"({sess} visits)."
            )

    assert len(calls) <= MAX_REPORTS_AU

    top_paths = [
        L["path_display"]
        for L in landings
        if L.get("sessions") and L.get("path_kind") != "unknown"
    ][:4]
    summary_bits = [
        f"Last 7 days (AU site tags): {sess:,} sessions · {int(last7.get('users') or 0):,} users.",
        f"Paid Google ads visits: {paid_n}.",
    ]
    if last7.get("engagement_rate_pct") is not None and sess:
        summary_bits.append(
            f"About {last7['engagement_rate_pct']:.0f}% stayed and looked around."
        )
    if top_paths:
        summary_bits.append("Top landings: " + ", ".join(top_paths) + ".")
    if notes:
        summary_bits.append(notes[0])

    return {
        "ok": True,
        "property_id": property_id,
        "measurement_id": MEASUREMENT_ID_AU,
        "window": GA4_WINDOW_LABEL,
        "window_prior": GA4_PRIOR_LABEL,
        "tags_live_since": "2026-08-12",
        "run_report_requests": len(calls),
        "api_calls": calls,
        "totals_last_7_days": last7,
        "totals_prior_7_days": prior7,
        "paid_search_sessions": paid_n,
        "paid_search_sessions_prior": paid_search_sessions_prior,
        "paid_search_engagement_rate_pct": paid_eng,
        "au_path_sessions": au_path_sessions,
        "thank_you_sessions": thank_you_sessions,
        "top_landing_pages": landings,
        "channels": channels,
        "insights": insights,
        "notes": notes,
        "summary_plain": " ".join(summary_bits),
    }


def pull_ga4() -> dict[str, Any]:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        OrderBy,
        RunReportRequest,
    )

    property_id = resolve_ga4_property_id()
    prop = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
    client = BetaAnalyticsDataClient()
    calls: list[dict[str, Any]] = []
    notes: list[str] = []

    # --- 1) Totals: last 7 days only (no "today" — goes stale between refreshes) ---
    overview_metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "conversions",
        "averageSessionDuration",
    ]
    req1 = RunReportRequest(
        property=prop,
        date_ranges=_week_date_ranges(DateRange),
        metrics=[Metric(name=m) for m in overview_metrics],
    )
    resp1 = client.run_report(req1)
    calls.append({"n": 1, "name": "overview_engagement_conversions", "ok": True})

    last7_raw: dict[str, Any] = {m: 0 for m in overview_metrics}
    prior_raw: dict[str, Any] = {m: 0 for m in overview_metrics}
    for row in resp1.rows or []:
        mets = _metric_map(row, overview_metrics)
        if _range_key(row, 0) == PRIOR_RANGE:
            prior_raw = mets
        else:
            last7_raw = mets

    def _totals(raw: dict[str, Any]) -> dict[str, Any]:
        sess = int(raw.get("sessions") or 0)
        eng = int(raw.get("engagedSessions") or 0)
        return {
            "sessions": sess,
            "users": int(raw.get("totalUsers") or 0),
            "engaged_sessions": eng,
            "engagement_rate_pct": _pct_rate(raw.get("engagementRate")),
            "bounce_rate_pct": _pct_rate(raw.get("bounceRate")),
            "conversions": float(raw.get("conversions") or 0),
            "avg_session_seconds": round(float(raw.get("averageSessionDuration") or 0), 1),
        }

    last7 = _totals(last7_raw)
    prior7 = _totals(prior_raw)

    # --- 2) Landing pages + engagement ---
    land_metrics = [
        "sessions",
        "totalUsers",
        "engagedSessions",
        "engagementRate",
        "bounceRate",
        "averageSessionDuration",
    ]
    req2 = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=GA4_WEEK_START, end_date=GA4_WEEK_END)],
        dimensions=[Dimension(name="landingPage")],
        metrics=[Metric(name=m) for m in land_metrics],
        order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
        limit=15,
    )
    resp2 = client.run_report(req2)
    calls.append({"n": 2, "name": "landing_pages_engagement", "ok": True})

    landings: list[dict[str, Any]] = []
    market_sessions = {"US": 0, "AU": 0, "PH": 0, "other": 0}
    kind_sessions = {
        "us_home": 0,
        "role_lp": 0,
        "quiz": 0,
        "au": 0,
        "thank_you": 0,
        "other_site": 0,
        "other": 0,
        "unknown": 0,
    }
    for row in resp2.rows or []:
        path = row.dimension_values[0].value if row.dimension_values else "(not set)"
        if path is None or str(path).strip() == "":
            path = "(empty path)"
        mets = _metric_map(row, land_metrics)
        market = _infer_market(path)
        kind = _path_kind(path)
        sessions = int(mets.get("sessions") or 0)
        market_sessions[market] = market_sessions.get(market, 0) + sessions
        kind_sessions[kind] = kind_sessions.get(kind, 0) + sessions
        landings.append(
            {
                "path": path,
                "path_display": _nice_path(path),
                "path_kind": kind,
                "sessions": sessions,
                "users": int(mets.get("totalUsers") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
                "bounce_rate_pct": _pct_rate(mets.get("bounceRate")),
                "avg_session_seconds": round(float(mets.get("averageSessionDuration") or 0), 1),
                "duration_metric": "averageSessionDuration",
                "market_guess": market,
            }
        )

    # --- 3) Channels + engagement ---
    ch_metrics = ["sessions", "totalUsers", "engagedSessions", "engagementRate"]
    req3 = RunReportRequest(
        property=prop,
        date_ranges=_week_date_ranges(DateRange),
        dimensions=[Dimension(name="sessionDefaultChannelGroup")],
        metrics=[Metric(name=m) for m in ch_metrics],
        order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
        limit=20,
    )
    resp3 = client.run_report(req3)
    calls.append({"n": 3, "name": "channels_engagement", "ok": True})

    channels: list[dict[str, Any]] = []
    paid_search_sessions_prior = 0
    for row in resp3.rows or []:
        ch = row.dimension_values[0].value if row.dimension_values else "(not set)"
        mets = _metric_map(row, ch_metrics)
        rng = _range_key(row, 1)
        sess_n = int(mets.get("sessions") or 0)
        if rng == PRIOR_RANGE:
            if "paid" in (ch or "").lower():
                paid_search_sessions_prior += sess_n
            continue
        channels.append(
            {
                "channel": ch,
                "sessions": sess_n,
                "users": int(mets.get("totalUsers") or 0),
                "engaged_sessions": int(mets.get("engagedSessions") or 0),
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
            }
        )

    # --- 4) Device × channel (Paid Search split for desktop/mobile investigation) ---
    req4 = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=GA4_WEEK_START, end_date=GA4_WEEK_END)],
        dimensions=[
            Dimension(name="deviceCategory"),
            Dimension(name="sessionDefaultChannelGroup"),
        ],
        metrics=[
            Metric(name="sessions"),
            Metric(name="engagedSessions"),
            Metric(name="engagementRate"),
        ],
        order_bys=[OrderBy(metric={"metric_name": "sessions"}, desc=True)],
        limit=30,
    )
    resp4 = client.run_report(req4)
    calls.append({"n": 4, "name": "device_by_channel", "ok": True})

    devices_by_channel: list[dict[str, Any]] = []
    device_agg: dict[str, dict[str, Any]] = {}
    for row in resp4.rows or []:
        dev = row.dimension_values[0].value if row.dimension_values else "(not set)"
        ch = (
            row.dimension_values[1].value
            if row.dimension_values and len(row.dimension_values) > 1
            else "(not set)"
        )
        mets = _metric_map(row, ["sessions", "engagedSessions", "engagementRate"])
        sess = int(mets.get("sessions") or 0)
        eng = int(mets.get("engagedSessions") or 0)
        devices_by_channel.append(
            {
                "device": dev,
                "channel": ch,
                "sessions": sess,
                "engaged_sessions": eng,
                "engagement_rate_pct": _pct_rate(mets.get("engagementRate")),
            }
        )
        agg = device_agg.get(dev) or {
            "device": dev,
            "sessions": 0,
            "engaged_sessions": 0,
        }
        agg["sessions"] += sess
        agg["engaged_sessions"] += eng
        device_agg[dev] = agg

    devices: list[dict[str, Any]] = []
    for agg in device_agg.values():
        sess = int(agg["sessions"] or 0)
        eng = int(agg["engaged_sessions"] or 0)
        devices.append(
            {
                "device": agg["device"],
                "sessions": sess,
                "engaged_sessions": eng,
                "engagement_rate_pct": (
                    round(100.0 * eng / sess, 1) if sess else None
                ),
            }
        )
    devices.sort(key=lambda d: -int(d.get("sessions") or 0))

    # --- 5) Top events (kept for raw JSON; not lectured on Executive) ---
    req5 = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=GA4_WEEK_START, end_date=GA4_WEEK_END)],
        dimensions=[Dimension(name="eventName")],
        metrics=[
            Metric(name="eventCount"),
            Metric(name="conversions"),
            Metric(name="totalUsers"),
        ],
        order_bys=[OrderBy(metric={"metric_name": "eventCount"}, desc=True)],
        limit=12,
    )
    resp5 = client.run_report(req5)
    calls.append({"n": 5, "name": "top_events", "ok": True})

    events: list[dict[str, Any]] = []
    skip_events = {
        "session_start",
        "first_visit",
        "page_view",
        "user_engagement",
        "scroll",
    }
    for row in resp5.rows or []:
        name = row.dimension_values[0].value if row.dimension_values else "(not set)"
        mets = _metric_map(row, ["eventCount", "conversions", "totalUsers"])
        events.append(
            {
                "event": name,
                "event_count": int(mets.get("eventCount") or 0),
                "conversions": float(mets.get("conversions") or 0),
                "users": int(mets.get("totalUsers") or 0),
                "is_noise": name in skip_events,
            }
        )
    interesting_events = [e for e in events if not e.get("is_noise")][:8]

    assert len(calls) <= MAX_REPORTS

    au_in_us_property = int(market_sessions.get("AU") or 0)
    if au_in_us_property == 0:
        notes.append(
            "US site tags only. Australia is a separate GA4 property — see the AU block."
        )
    else:
        notes.append(
            f"Saw {au_in_us_property} sessions on /au paths in the US property — "
            "spill / shared host only, not a substitute for AU tags."
        )

    insights = build_insights(
        last7=last7,
        landings=landings,
        channels=channels,
        devices=devices,
        devices_by_channel=devices_by_channel,
        events=interesting_events,
        market_sessions=market_sessions,
        notes=notes,
    )

    s7 = int(last7.get("sessions") or 0)
    u7 = int(last7.get("users") or 0)
    # Filter garbage landings from the human summary
    top_paths = [
        L["path_display"]
        for L in landings
        if L.get("sessions") and L.get("path_kind") != "unknown"
    ][:4]
    top_ch = [c["channel"] for c in channels[:3] if c.get("sessions")]
    summary_bits = [
        f"Last 7 days (US site tags): {s7:,} sessions · {u7:,} users.",
    ]
    if last7.get("engagement_rate_pct") is not None:
        summary_bits.append(
            f"About {last7['engagement_rate_pct']:.0f}% stayed and looked around."
        )
    if top_paths:
        summary_bits.append("Top landings: " + ", ".join(top_paths) + ".")
    if top_ch:
        summary_bits.append("Traffic: " + ", ".join(top_ch) + ".")
    summary_bits.append(notes[0])

    # Compare hub vs roles for UI callout
    compare = {
        "us_home_sessions": int(kind_sessions.get("us_home") or 0),
        "role_lp_sessions": int(kind_sessions.get("role_lp") or 0),
        "quiz_sessions": int(kind_sessions.get("quiz") or 0),
        "thank_you_sessions": int(kind_sessions.get("thank_you") or 0),
        "note": (
            "Path buckets from landingPage dimension. Role LPs = /us/* except home/quiz."
        ),
    }

    # Paid Search device split for Executive callout
    paid_dev_rows = [
        r
        for r in devices_by_channel
        if "paid" in (r.get("channel") or "").lower()
    ]
    paid_mobile = sum(
        int(r.get("sessions") or 0)
        for r in paid_dev_rows
        if (r.get("device") or "").lower() == "mobile"
    )
    paid_desktop = sum(
        int(r.get("sessions") or 0)
        for r in paid_dev_rows
        if (r.get("device") or "").lower() == "desktop"
    )
    paid_tot = paid_mobile + paid_desktop
    device_finding = {
        "site_desktop": next(
            (d.get("sessions") for d in devices if (d.get("device") or "").lower() == "desktop"),
            0,
        ),
        "site_mobile": next(
            (d.get("sessions") for d in devices if (d.get("device") or "").lower() == "mobile"),
            0,
        ),
        "paid_search_mobile": paid_mobile,
        "paid_search_desktop": paid_desktop,
        "paid_search_mobile_pct": (
            round(100.0 * paid_mobile / paid_tot) if paid_tot else None
        ),
        "verdict": None,
        "note": None,
    }
    if paid_tot >= 20:
        pct = device_finding["paid_search_mobile_pct"] or 0
        if pct < 55:
            device_finding["verdict"] = "watch"
            device_finding["note"] = (
                f"Paid Search only {pct}% mobile ({paid_mobile} vs {paid_desktop} desktop). "
                "Expected ~80% for search ads. Microsite viewport + sticky CTA look fine — "
                "not an obvious mobile-break bug. Early sample + Direct inflating site-wide desktop."
            )
        elif pct < 70:
            device_finding["verdict"] = "early"
            device_finding["note"] = (
                f"Paid Search {pct}% mobile — closer to normal, not yet ~80%. Small pilot."
            )
        else:
            device_finding["verdict"] = "ok"
            device_finding["note"] = (
                f"Paid Search {pct}% mobile — in line with search-ad expectations."
            )
    else:
        device_finding["verdict"] = "thin"
        device_finding["note"] = (
            "Not enough Paid Search sessions yet to judge mobile vs desktop."
        )

    snap: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "api": "ga4_data_api",
        "api_note": (
            "GA4 Data API (analyticsdata.googleapis.com) — NOT Google Ads API. "
            "Does not consume the Ads developer-token ops budget."
        ),
        "metric_labels": {
            "ad_ctr": "Ad CTR — clicks ÷ impressions in Google Ads",
            "stayed_and_looked": "Stayed and looked around — engaged sessions ÷ sessions",
            "left_right_away": "Left right away — sessions that were not engaged",
        },
        "property_id": property_id,
        "measurement_id_us": MEASUREMENT_ID_US,
        "window": GA4_WINDOW_LABEL,
        "window_prior": GA4_PRIOR_LABEL,
        "run_report_requests": len(calls),
        "run_report_max": MAX_REPORTS,
        "api_calls": calls,
        "quota_note": (
            "GA4 standard properties typically allow on the order of 25k–200k "
            "tokens/day (property-dependent). A few small RunReport calls are "
            "negligible. Separate from Google Ads API quota (~15k ops/day)."
        ),
        "totals_last_7_days": last7,
        "totals_prior_7_days": prior7,
        "paid_search_sessions_prior": paid_search_sessions_prior,
        "market_from_landing_path": market_sessions,
        "path_kind_sessions": kind_sessions,
        "landing_compare": compare,
        "top_landing_pages": landings,
        "channels": channels,
        "devices": devices,
        "devices_by_channel": devices_by_channel,
        "device_finding": device_finding,
        "events_top": events,
        "events_interesting": interesting_events,
        "insights": insights,
        "notes": notes,
        "summary_plain": " ".join(summary_bits),
    }

    au_id = resolve_ga4_property_id_au()
    if au_id:
        try:
            snap["au"] = pull_ga4_au(client, au_id)
        except Exception as exc:  # noqa: BLE001
            snap["au"] = {
                "ok": False,
                "property_id": au_id,
                "measurement_id": MEASUREMENT_ID_AU,
                "error": str(exc),
                "error_plain": _plain_ga4_error(exc),
                "summary_plain": _plain_ga4_error(exc),
                "tags_live_since": "2026-08-12",
            }
    else:
        snap["au"] = {
            "ok": False,
            "error_plain": "GA4_PROPERTY_ID_AU not set.",
            "summary_plain": "AU property id not set — skipped.",
        }
    snap["run_report_requests_total"] = int(snap["run_report_requests"]) + int(
        (snap.get("au") or {}).get("run_report_requests") or 0
    )
    return snap


def merge_into_executive(ga4: dict[str, Any]) -> None:
    if OUT_EXEC.is_file():
        exec_snap = json.loads(OUT_EXEC.read_text(encoding="utf-8"))
    else:
        exec_snap = {
            "generated_at_utc": ga4["generated_at_utc"],
            "note": "Ads snapshot missing — GA4 section only",
        }
    exec_snap["ga4"] = ga4
    exec_snap["ga4_merged_at_utc"] = ga4["generated_at_utc"]
    OUT_EXEC.write_text(json.dumps(exec_snap, indent=2) + "\n", encoding="utf-8")


def refresh_experiments() -> int:
    script = REPO / "ads-launch" / "pull_experiments_snapshot.py"
    py = sys.executable
    print(f"Refreshing experiments via {script.name}…")
    return subprocess.call([py, str(script)], cwd=str(REPO))


def main() -> int:
    _load_dotenv_quiet()
    parser = argparse.ArgumentParser(description="Pull high-level GA4 for Executive")
    parser.add_argument(
        "--skip-experiments",
        action="store_true",
        help="Do not also run pull_experiments_snapshot.py",
    )
    args = parser.parse_args()

    prop = resolve_ga4_property_id()
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or ""
    if not creds or not Path(creds).expanduser().is_file():
        fallback = REPO / "credentials" / "ga4-viewer-sa.json"
        if fallback.is_file():
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(fallback)
            creds = str(fallback)

    print(f"GA4 US {prop} · AU {os.environ.get('GA4_PROPERTY_ID_AU') or '(unset)'} · creds={creds or '(ADC)'}")
    try:
        ga4 = pull_ga4()
    except Exception as exc:  # noqa: BLE001
        print(f"GA4 pull failed: {exc}", file=sys.stderr)
        return 1

    OUT_GA4.parent.mkdir(parents=True, exist_ok=True)
    OUT_GA4.write_text(json.dumps(ga4, indent=2) + "\n", encoding="utf-8")
    merge_into_executive(ga4)
    print(
        f"Wrote {OUT_GA4.relative_to(REPO)} + merged ga4 → "
        f"{OUT_EXEC.relative_to(REPO)} · reports={ga4['run_report_requests']}"
    )
    print(f"Summary: {ga4['summary_plain']}")
    for line in ga4.get("insights") or []:
        print(f"  · {line}")
    au = ga4.get("au") or {}
    if au:
        print(f"AU: {au.get('summary_plain') or au.get('error_plain') or au}")
        for line in au.get("insights") or []:
            print(f"  · {line}")

    if not args.skip_experiments:
        rc = refresh_experiments()
        if rc != 0:
            print(f"experiments refresh exited {rc} (GA4 executive still saved)", file=sys.stderr)
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
