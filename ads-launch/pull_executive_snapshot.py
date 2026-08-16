#!/usr/bin/env python3
"""Read-only executive snapshot for VC_* Search US+AU (max 2 GAQL calls).

Hard rules:
- No mutate / upload / enable
- On RESOURCE_EXHAUSTED: STOP, do not retry
- Exactly 2 light calls: US campaigns (date range covering early CPL) + AU campaigns
- Early US CPL = VC_* spend for Aug 8–10 ÷ sales-ops enquiry counts (not Ads conversions)
- No search-term dumps (kept out of Executive; ops uses Ads UI)
- Writes xray/data/executive-snapshot.json for the Executive tab

Usage (from shoutgeorge-ads venv):
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    /Users/george/Developer/virtual-coworker/ads-launch/pull_executive_snapshot.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from sg_google_ads.client import build_client, run_gaql  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import (  # noqa: E402
    ApiAccessError,
    QuotaExhaustedError,
    SgGoogleAdsError,
)

US_ID = "4967151855"
AU_ID = "5735391940"
OUT = Path(__file__).resolve().parents[1] / "xray" / "data" / "executive-snapshot.json"
REPO = Path(__file__).resolve().parents[1]
US_EDITOR_CSV = REPO / "ads-launch" / "google-ads-editor-import-us.csv"
VC_ENV = SG_ROOT / "clients" / "virtual-coworker.env"

# Known live US LPs (Editor Final URLs) — metrics derived, not landing_page_view API
US_LP_CATALOG = [
    {
        "slug": "us",
        "name": "US hub",
        "path": "/us",
        "url": "https://www.virtualcoworker.app/us",
        "why": "CORE campaign Final URL — main hire/VA traffic lands here.",
        "source_campaign": "VC_US_S_CORE",
    },
    {
        "slug": "administrative-support",
        "name": "Admin / EA",
        "path": "/us/administrative-support",
        "url": "https://www.virtualcoworker.app/us/administrative-support",
        "why": "ROLES admin Final URL — EA / admin intent.",
        "term_hints": ("administrative", "admin assistant", "executive assistant", "virtual assistant business"),
    },
    {
        "slug": "bookkeeping",
        "name": "Bookkeeping",
        "path": "/us/bookkeeping",
        "url": "https://www.virtualcoworker.app/us/bookkeeping",
        "why": "ROLES bookkeeping Final URL — bookkeeper searches.",
        "term_hints": ("bookkeep", "book keeper"),
    },
    {
        "slug": "accounting",
        "name": "Accounting",
        "path": "/us/accounting",
        "url": "https://www.virtualcoworker.app/us/accounting",
        "why": "ROLES accounting Final URL — live category LP.",
        "term_hints": ("accounting", "accountant"),
    },
    {
        "slug": "customer-service",
        "name": "Customer service",
        "path": "/us/customer-service",
        "url": "https://www.virtualcoworker.app/us/customer-service",
        "why": "ROLES CSR Final URL — support / CSR searches.",
        "term_hints": ("customer service", "customer support", "csr"),
    },
    {
        "slug": "digital-marketing",
        "name": "Digital marketing",
        "path": "/us/digital-marketing",
        "url": "https://www.virtualcoworker.app/us/digital-marketing",
        "why": "ROLES marketing Final URL — live category LP.",
        "term_hints": ("digital marketing", "marketing va", "seo", "ppc"),
    },
    {
        "slug": "social-media",
        "name": "Social media",
        "path": "/us/social-media",
        "url": "https://www.virtualcoworker.app/us/social-media",
        "why": "ROLES social Final URL — live category LP.",
        "term_hints": ("social media",),
    },
]

# Human lead handoff for early CPL (sales ops — not Ads conversions)
# Window matches Cheyenne’s Aug 8–10 US enquiry report.
HUMAN_LEADS_US_EARLY = {
    "market": "US",
    "window_start": "2026-08-08",
    "window_end": "2026-08-10",
    "label": "Sat Aug 8 – Mon Aug 10",
    "source": "Sales ops handoff (Cheyenne) — US enquiries Aug 8–10 inclusive",
    "enquiries": 4,
    "sales_calls_booked": 2,
    "junk_job_seeker": 1,
    "not_a_fit": 1,
    "not_a_fit_detail": "Project-based — not a fit for ongoing hire",
    "campaigns_for_spend": ["VC_US_S_CORE", "VC_US_S_ROLES"],
    "caveat": (
        "Early / small sample — do not treat as steady-state CPL. "
        "Job-seeker junk never counts as a win."
    ),
}

# AU Stage 1 woke ~Aug 9. No ops enquiry counts yet (Cheyenne Aug 10 was US-only).
HUMAN_LEADS_AU_EARLY = {
    "market": "AU",
    "status": "waiting_on_leads",
    "window_start": "2026-08-08",
    "window_end": "2026-08-10",
    "label": "Sat Aug 8 – Mon Aug 10",
    "spend_window_note": "VC_AU_* spend started Sun Aug 9 (nothing Aug 8)",
    "source": (
        "No AU enquiry counts in ops email yet — Cheyenne Aug 10 handoff was US-only. "
        "Holly owns APAC Monday updates; waiting on first AU lead report."
    ),
    "enquiries": None,
    "sales_calls_booked": None,
    "junk_job_seeker": None,
    "not_a_fit": None,
    "campaigns_for_spend": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
    "caveat": (
        "Cost per enquiry: not yet (no AU lead report in email)."
    ),
}

# Qualitative operator notes (not from API) — kept honest for CEO walkthroughs
# Executive shows curated buyer signals + themes — never raw early ST dumps.
# Insight spend lines are refreshed in _refresh_operator_insights() after each pull.
OPERATOR_NOTES = {
    "narrative_as_of": "2026-08-10",
    "status_banner": (
        "US and Australia Search are live. Paying per click until call tracking is trusted. "
        "Clear Google Ads recommendations daily (account score)."
    ),
    "budgets": [
        {"label": "US", "amount": "~$125/day", "detail": "Core $75 + Roles $50", "kind": "live_test"},
        {"label": "Australia", "amount": "Live", "detail": "new Search campaigns", "kind": "priority"},
    ],
    "whats_working": {
        "ad_copy_themes": [
            "Hire a Filipino / Philippines VA — employer copy, not job-seeker copy",
            "You interview. You pick. — matches the real hiring process",
            "Dedicated teammate, not a gig marketplace",
            "Agency / firm / company — same words buyers type",
        ],
        "note": "Themes in the live US ads. One high-click Offshore ad was left unchanged on purpose.",
    },
    "insights": [
        "US early cost per lead (Aug 8–10): loading from Ads spend + sales handoff…",
        "US (7 days): loading…",
        "US daily plan is about $125 — watch spend vs budget on high days.",
        "Almost all US ad clicks still land on the US home page. Role pages are live but quiet.",
        "Australia new Search: loading…",
        "Still paying per click. US phone · Australia 1300. A tap is not the same as a real conversation.",
        "Clear Recommendations in Google Ads every day. That is how Google scores the account.",
    ],
    "buyer_signals": [
        {
            "term": "philippines virtual assistant agency",
            "why": "Employer shopping for a PH VA agency",
            "market": "US",
        },
        {
            "term": "philippines outsourcing agency",
            "why": "Business looking for a provider, not a job",
            "market": "US",
        },
        {
            "term": "remote staffing agency",
            "why": "Staffing language buyers actually use",
            "market": "US",
        },
        {
            "term": "virtual assistant firm / company",
            "why": "Shopping for a company, not a gig listing",
            "market": "US",
        },
        {
            "term": "va workers ph",
            "why": "Messy shorthand — watch if spend climbs",
            "market": "US",
        },
    ],
    "lp_highlights": [
        {
            "name": "US home (/us)",
            "why": "Takes almost all US paid clicks right now",
            "url": "https://www.virtualcoworker.app/us",
        },
        {
            "name": "Role pages (admin, bookkeeping, marketing…)",
            "why": "Live for Role Search — little paid traffic yet",
            "url": "https://www.virtualcoworker.app/us/administrative-support",
        },
        {
            "name": "Australia home (/au)",
            "why": "Live with 1300 · new ads just started",
            "url": "https://www.virtualcoworker.app/au",
        },
        {
            "name": "Quiz pages",
            "why": "Built, not in paid traffic yet",
            "url": "https://www.virtualcoworker.app/us/quiz",
        },
    ],
    "whats_next": [
        "<strong>Daily</strong> — clear Google Ads recommendations + review search terms",
        "<strong>Australia GTM + GA4</strong> — visit tags first (prerequisite)",
        "<strong>Then</strong> AU website calls 60+ seconds · AU calls from ads (US website-call already live)",
        "<strong>Then</strong> CRM",
    ],
    "coming_soon": [
        "Quiz ~70% · not on live path · ads Paused",
        "Booked consult as a stronger later signal (click ≠ booked)",
        "Zoho → Job Order → Placement (CRM value overrides site $)",
        "Site tests scoreboard still blank",
    ],
    "done_today": [
        "US Search live · Brand off · GTM/GA4 live · ~$125/day",
        "US phone 310 on site + Call · 888 unlinked from new Ads",
        "Human RSAs on CORE + ROLES (winners left alone)",
        "US sitelinks cleaned · callouts/snippet already good",
        "AU phone 1300 on site · Stage 1 waiting on traffic",
        "Form chips + modeled $ on /us /au · Google + Clutch stars",
        "Job-seeker hard redirect to virtualcoworker.com.ph",
        "Thank-you overlay live (call + book · not Ads primary)",
        "Quiz parked ~70% · ads Paused",
    ],
    "honesty": (
        "US and Australia Search are live. Paying per click until call tracking is trusted. "
        "Early US cost-per-lead is on this page (small sample). Job seekers are not counted as wins."
    ),
    "lp_ab_note": (
        "Homepage H1 locked unless George asks. Site tests scoreboard still blank."
    ),
}

# Curated bidding themes for Executive (never dump raw early search terms)
KEYWORD_THEMES = {
    "label": "Employer agency-hire Exact themes",
    "note": "Curated bidding themes — not raw search terms. Priority = agency/firm/company seekers.",
    "executive_surface": True,
    "themes": [
        {
            "theme": "PH VA / staffing agency · firm · company",
            "market": "US + AU",
            "campaign": "VC_*_S_CORE",
            "why": "Highest intent — employer shopping for an agency to staff PH remote workers",
        },
        {
            "theme": "Philippines outsourcing agency",
            "market": "US + AU",
            "campaign": "VC_*_S_CORE",
            "why": "Outsourcing-agency language · clear B2B provider search",
        },
        {
            "theme": "hire VA / Filipino VA (supporting)",
            "market": "US + AU",
            "campaign": "VC_*_S_CORE",
            "why": "Useful but messier — hire/recruit can mix employer + job-seeker",
        },
        {
            "theme": "bookkeeping / accounting hire",
            "market": "US + AU",
            "campaign": "VC_*_S_ROLES",
            "why": "Role LP Final URLs",
        },
        {
            "theme": "customer service / admin / EA",
            "market": "US + AU",
            "campaign": "VC_*_S_ROLES",
            "why": "Role LP Final URLs",
        },
        {
            "theme": "digital marketing / social media hire",
            "market": "US + AU",
            "campaign": "VC_*_S_ROLES",
            "why": "Role LP Final URLs",
        },
    ],
}


def _money(micros: Any) -> float:
    try:
        return float(micros) / 1_000_000.0
    except (TypeError, ValueError):
        return 0.0


def _pct(impressions: int, clicks: int) -> float | None:
    if impressions <= 0:
        return None
    return round(100.0 * clicks / impressions, 2)


def _avg_cpc(cost: float, clicks: int) -> float | None:
    if clicks <= 0:
        return None
    return round(cost / clicks, 2)


def _metrics_blob(
    impressions: int,
    clicks: int,
    cost: float,
    conversions: float = 0.0,
) -> dict[str, Any]:
    blob: dict[str, Any] = {
        "impressions": impressions,
        "clicks": clicks,
        "ctr_pct": _pct(impressions, clicks),
        "cost_usd": round(cost, 2),
        "avg_cpc_usd": _avg_cpc(cost, clicks),
    }
    if conversions:
        blob["conversions"] = round(float(conversions), 2)
    return blob


def _enum_name(val: Any) -> str | None:
    if val is None:
        return None
    if hasattr(val, "name"):
        return str(val.name)
    text = str(val).strip()
    return text or None


# 14 inclusive UTC days in one call so Python can split last 7 vs prior 7.
# Still VC_US_% only — no Brand, no full-account pagination. No 3rd Ads call.
_PULL_END_D = datetime.now(timezone.utc).date()
US_PULL_END = _PULL_END_D.isoformat()
US_PULL_START = (_PULL_END_D - timedelta(days=13)).isoformat()
AU_PULL_START = US_PULL_START
AU_PULL_END = US_PULL_END

CAMPAIGN_Q_US = f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.bidding_strategy_type,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.average_cpc,
      metrics.ctr,
      metrics.conversions
    FROM campaign
    WHERE campaign.name LIKE 'VC_US_%'
      AND campaign.status != 'REMOVED'
      AND segments.date BETWEEN '{US_PULL_START}' AND '{US_PULL_END}'
"""

# AU: active campaigns with impressions in the same 14-day window (VC_AU_* + any leftover).
# One call. Brand is labeled, not centered. No extra 30-day pull.
CAMPAIGN_Q_AU = f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.bidding_strategy_type,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.average_cpc,
      metrics.ctr,
      metrics.conversions
    FROM campaign
    WHERE campaign.status != 'REMOVED'
      AND segments.date BETWEEN '{AU_PULL_START}' AND '{AU_PULL_END}'
      AND metrics.impressions > 0
"""

# Cheyenne Fri EOW — latest Gmail as of 2026-08-14. Do not add Zoho 18 on top.
SALES_OPS_US_WEEK = {
    "market": "US",
    "window_start": "2026-08-10",
    "window_end": "2026-08-16",
    "label": "Mon Aug 10 – Sun Aug 16",
    "source": "Cheyenne Gichana email 2026-08-14 15:40 PT — U.S. Update",
    "gmail_thread_id": "1a0026f806356417",
    "enquiries": 14,
    "sales_calls_completed": 9,
    "looking_for_work": 4,
    "not_a_fit": 2,
    "philippines_job_seekers": 1,
    "sources": [
        {"label": "Google Organic", "count": 8},
        {"label": "Bing Organic", "count": 1},
        {"label": "Facebook", "count": 2},
        {"label": "Referral Partner", "count": 1},
        {"label": "Phone Call", "count": 1},
        {"label": "Forbes", "count": 1},
    ],
    "campaigns_for_spend": ["VC_US_S_CORE", "VC_US_S_ROLES"],
}


def fetch_rows(client: Any, customer_id: str, query: str) -> list[Any]:
    return list(run_gaql(client, customer_id, query))


def _campaign_cohort(name: str) -> str:
    n = name or ""
    if n.startswith("VC_AU_") or n.startswith("VC_US_"):
        return "stage1"
    if n.startswith("PM_AU_") or "Brand" in n:
        # Brand deferred — still label so UI can demote, not center strategy on it
        if "Brand" in n:
            return "legacy_brand"
        return "legacy"
    return "legacy"


def _iso_days_ending(end: str, days: int) -> list[str]:
    d1 = date.fromisoformat(end[:10])
    return [(d1 - timedelta(days=days - 1 - i)).isoformat() for i in range(days)]


def _sum_date_map(by_date: dict[str, Any], dates: list[str]) -> dict[str, Any]:
    impr = clicks = 0
    cost = conv = 0.0
    for d in dates:
        v = by_date.get(d) or {}
        impr += int(v.get("impressions") or 0)
        clicks += int(v.get("clicks") or 0)
        cost += float(v.get("cost_usd") or 0)
        conv += float(v.get("conversions") or 0)
    return _metrics_blob(impr, clicks, cost, conv)


def summarize_campaigns(rows: list[Any]) -> dict[str, Any]:
    by_campaign: dict[str, dict[str, Any]] = {}
    by_date: dict[str, dict[str, int | float]] = {}
    by_date_stage1: dict[str, dict[str, int | float]] = {}
    today_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    dates_seen: set[str] = set()

    for row in rows:
        name = row.campaign.name
        status = row.campaign.status.name if hasattr(row.campaign.status, "name") else str(row.campaign.status)
        day = str(row.segments.date)
        dates_seen.add(day)
        impr = int(row.metrics.impressions or 0)
        clicks = int(row.metrics.clicks or 0)
        cost = _money(row.metrics.cost_micros)
        conv = float(getattr(row.metrics, "conversions", 0) or 0)
        bidding = _enum_name(getattr(row.campaign, "bidding_strategy_type", None))

        slot = by_campaign.setdefault(
            name,
            {
                "name": name,
                "status": status,
                "cohort": _campaign_cohort(name),
                "bidding_strategy_type": bidding,
                "impressions": 0,
                "clicks": 0,
                "cost_usd": 0.0,
                "conversions": 0.0,
                "by_date": {},
            },
        )
        if bidding:
            slot["bidding_strategy_type"] = bidding
        slot["impressions"] += impr
        slot["clicks"] += clicks
        slot["cost_usd"] += cost
        slot["conversions"] += conv
        dslot = slot["by_date"].setdefault(
            day, {"impressions": 0, "clicks": 0, "cost_usd": 0.0, "conversions": 0.0}
        )
        dslot["impressions"] += impr
        dslot["clicks"] += clicks
        dslot["cost_usd"] += cost
        dslot["conversions"] += conv

        g = by_date.setdefault(
            day, {"impressions": 0, "clicks": 0, "cost_usd": 0.0, "conversions": 0.0}
        )
        g["impressions"] += impr
        g["clicks"] += clicks
        g["cost_usd"] += cost
        g["conversions"] += conv
        if slot.get("cohort") == "stage1":
            s1 = by_date_stage1.setdefault(
                day, {"impressions": 0, "clicks": 0, "cost_usd": 0.0, "conversions": 0.0}
            )
            s1["impressions"] += impr
            s1["clicks"] += clicks
            s1["cost_usd"] += cost
            s1["conversions"] += conv

    latest = max(dates_seen) if dates_seen else today_key
    today_totals = by_date.get(today_key) or by_date.get(latest) or {
        "impressions": 0,
        "clicks": 0,
        "cost_usd": 0.0,
    }
    today_label = today_key if today_key in by_date else latest
    today_is_utc_calendar = today_key in by_date

    last7 = _iso_days_ending(latest, 7)
    prior_end = (date.fromisoformat(last7[0]) - timedelta(days=1)).isoformat()
    prior7 = _iso_days_ending(prior_end, 7)

    campaigns_out = []
    for name, slot in sorted(by_campaign.items(), key=lambda kv: -float(kv[1]["cost_usd"])):
        campaigns_out.append(
            {
                "name": name,
                "status": slot["status"],
                "cohort": slot.get("cohort") or _campaign_cohort(name),
                "bidding_strategy_type": slot.get("bidding_strategy_type"),
                "last_7_days": _sum_date_map(slot["by_date"], last7),
                "prior_7_days": _sum_date_map(slot["by_date"], prior7),
                "focus_day": _metrics_blob(
                    int(slot["by_date"].get(today_label, {}).get("impressions", 0)),
                    int(slot["by_date"].get(today_label, {}).get("clicks", 0)),
                    float(slot["by_date"].get(today_label, {}).get("cost_usd", 0.0)),
                    float(slot["by_date"].get(today_label, {}).get("conversions", 0.0)),
                ),
            }
        )

    stage1 = [c for c in campaigns_out if c.get("cohort") == "stage1"]
    legacy = [c for c in campaigns_out if c.get("cohort") != "stage1"]

    def _sum_camps(camps: list[dict[str, Any]], key: str) -> dict[str, Any]:
        impr = sum(int((c.get(key) or {}).get("impressions") or 0) for c in camps)
        clicks = sum(int((c.get(key) or {}).get("clicks") or 0) for c in camps)
        cost = sum(float((c.get(key) or {}).get("cost_usd") or 0) for c in camps)
        conv = sum(float((c.get(key) or {}).get("conversions") or 0) for c in camps)
        return _metrics_blob(impr, clicks, cost, conv)

    by_date_out = {
        d: _metrics_blob(
            int(v["impressions"]),
            int(v["clicks"]),
            float(v["cost_usd"]),
            float(v.get("conversions") or 0),
        )
        for d, v in sorted(by_date.items())
    }
    by_date_s1_out = {
        d: _metrics_blob(
            int(v["impressions"]),
            int(v["clicks"]),
            float(v["cost_usd"]),
            float(v.get("conversions") or 0),
        )
        for d, v in sorted(by_date_stage1.items())
    }
    date_min = min(dates_seen) if dates_seen else None
    date_max = max(dates_seen) if dates_seen else None
    last7_s1 = _sum_date_map(by_date_s1_out, last7)
    prior7_s1 = _sum_date_map(by_date_s1_out, prior7)

    return {
        "window": (
            f"{date_min}_to_{date_max}" if date_min and date_max else "LAST_7_DAYS"
        ),
        "focus_day": today_label,
        "focus_day_note": (
            "UTC calendar today present in pull"
            if today_is_utc_calendar
            else "UTC today not in rows yet — showing latest date in pull window"
        ),
        "totals_focus_day": _metrics_blob(
            int(today_totals["impressions"]),
            int(today_totals["clicks"]),
            float(today_totals["cost_usd"]),
            float(today_totals.get("conversions") or 0),
        ),
        "totals_last_7_days": _sum_date_map(by_date_out, last7),
        "totals_prior_7_days": _sum_date_map(by_date_out, prior7),
        "totals_stage1_last_7_days": last7_s1 if by_date_s1_out else _sum_camps(stage1, "last_7_days"),
        "totals_stage1_prior_7_days": prior7_s1 if by_date_s1_out else _sum_camps(stage1, "prior_7_days"),
        "totals_legacy_last_7_days": _sum_camps(legacy, "last_7_days"),
        "compare_7v7": {
            "last_7": {"start": last7[0], "end": last7[-1], **last7_s1},
            "prior_7": {"start": prior7[0], "end": prior7[-1], **prior7_s1},
            "note_30d": (
                "30-day vs 30-day: next — not enough Stage 1 history yet "
                "(no extra Ads call)."
            ),
        },
        "campaigns": campaigns_out,
        "by_date": by_date_out,
        "by_date_stage1": by_date_s1_out,
        "dates_in_pull": sorted(dates_seen),
        "last_7_dates": last7,
        "prior_7_dates": prior7,
    }


def build_sales_ops_us(
    performance_us: dict[str, Any] | None,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    """Cheyenne week counts + fresh Stage 1 spend for the matching window."""
    ops = dict(SALES_OPS_US_WEEK)
    if existing:
        for k in (
            "sources",
            "zoho_census",
            "gmail_thread_id",
            "source",
            "looking_for_work",
            "not_a_fit",
            "philippines_job_seekers",
            "sales_calls_completed",
            "enquiries",
        ):
            if existing.get(k) is not None:
                ops[k] = existing[k]
    ops["window_start"] = SALES_OPS_US_WEEK["window_start"]
    ops["window_end"] = SALES_OPS_US_WEEK["window_end"]
    ops["label"] = SALES_OPS_US_WEEK["label"]
    start = str(ops.get("window_start") or "2026-08-10")
    end = str(ops.get("window_end") or "2026-08-16")
    by_date = (performance_us or {}).get("by_date_stage1") or (
        performance_us or {}
    ).get("by_date") or {}
    impr = clicks = 0
    cost = 0.0
    for d, m in sorted(by_date.items()):
        if start <= d <= end:
            impr += int(m.get("impressions") or 0)
            clicks += int(m.get("clicks") or 0)
            cost += float(m.get("cost_usd") or 0)
    spend = round(cost, 2)
    n_enq = int(ops.get("enquiries") or 0)
    n_calls = int(ops.get("sales_calls_completed") or 0)
    cpl = round(spend / n_enq, 2) if n_enq else None
    cost_call = round(spend / n_calls, 2) if n_calls else None
    ops.update(
        {
            "spend_usd": spend,
            "spend_note": (
                f"US Core+Roles {start}–{end} through Ads pull "
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC."
            ),
            "impressions": impr,
            "clicks": clicks,
            "avg_cpc_usd": _avg_cpc(spend, clicks),
            "cost_per_enquiry_usd": cpl,
            "cost_per_sales_call_completed_usd": cost_call,
            "math_plain": (
                f"${spend:,.2f} spend ÷ {n_enq} enquiries = ${cpl:,.2f} per enquiry"
                if cpl is not None
                else ""
            ),
            "math_completed_call": (
                f"${spend:,.2f} spend ÷ {n_calls} sales calls completed = "
                f"${cost_call:,.2f} per completed call"
                if cost_call is not None
                else ""
            ),
            "caveat": (
                "Sales-ops cost uses Cheyenne’s 14 enquiries. "
                "Monday Aug 10 also sits in the prior Sat–Mon sample — do not add weeks."
            ),
        }
    )
    return ops


def build_early_cpl_us(performance_us: dict[str, Any] | None) -> dict[str, Any]:
    """Spend ÷ human enquiries for Cheyenne’s Aug 8–10 window (VC_US_* only)."""
    leads = dict(HUMAN_LEADS_US_EARLY)
    start = str(leads["window_start"])
    end = str(leads["window_end"])
    by_date = (performance_us or {}).get("by_date") or {}
    day_rows: list[dict[str, Any]] = []
    impr = clicks = 0
    cost = 0.0
    for d, m in sorted(by_date.items()):
        if start <= d <= end:
            day_rows.append({"date": d, **m})
            impr += int(m.get("impressions") or 0)
            clicks += int(m.get("clicks") or 0)
            cost += float(m.get("cost_usd") or 0)

    spend = round(cost, 2)
    enquiries = int(leads["enquiries"])
    booked = int(leads["sales_calls_booked"])
    cpl_enquiry = round(spend / enquiries, 2) if enquiries > 0 else None
    cpl_booked = round(spend / booked, 2) if booked > 0 else None
    math_plain = (
        f"${spend:,.2f} spend ÷ {enquiries} enquiries = "
        f"${cpl_enquiry:,.2f} per enquiry"
        if cpl_enquiry is not None
        else "Spend or enquiry count missing"
    )
    math_booked = (
        f"${spend:,.2f} spend ÷ {booked} sales calls booked = "
        f"${cpl_booked:,.2f} per booked call"
        if cpl_booked is not None
        else None
    )

    return {
        **leads,
        "spend_usd": spend,
        "impressions": impr,
        "clicks": clicks,
        "avg_cpc_usd": _avg_cpc(spend, clicks),
        "cost_per_enquiry_usd": cpl_enquiry,
        "cost_per_sales_call_booked_usd": cpl_booked,
        "math_plain": math_plain,
        "math_booked_call": math_booked,
        "breakdown": (
            f"{enquiries} enquiries · {booked} sales calls booked · "
            f"{int(leads['junk_job_seeker'])} junk (job seeker) · "
            f"{int(leads['not_a_fit'])} not a fit"
        ),
        "by_day": day_rows,
        "dates_with_spend": [r["date"] for r in day_rows],
    }


def build_early_au_preliminary(performance_au: dict[str, Any] | None) -> dict[str, Any]:
    """AU early window: VC_* spend only. CPL stays null until ops reports enquiries."""
    meta = dict(HUMAN_LEADS_AU_EARLY)
    # Stage 1 woke ~Aug 9 — use VC_* (stage1) totals, not legacy PM_AU_*.
    stage1 = (performance_au or {}).get("totals_stage1_last_7_days") or {}
    # Prefer day rows that fall in the early window when by_date is VC-only-ish
    # (Aug 9–10 in current pull match stage1; Aug 8 may include legacy crumbs).
    start = str(meta["window_start"])
    end = str(meta["window_end"])
    by_date = (performance_au or {}).get("by_date") or {}
    day_rows: list[dict[str, Any]] = []
    for d, m in sorted(by_date.items()):
        if start <= d <= end:
            day_rows.append({"date": d, **m})

    spend = round(float(stage1.get("cost_usd") or 0), 2)
    clicks = int(stage1.get("clicks") or 0)
    impr = int(stage1.get("impressions") or 0)
    enquiries = meta.get("enquiries")
    booked = meta.get("sales_calls_booked")
    cpl_enquiry = (
        round(spend / int(enquiries), 2)
        if enquiries and int(enquiries) > 0
        else None
    )
    cpl_booked = (
        round(spend / int(booked), 2) if booked and int(booked) > 0 else None
    )
    if cpl_enquiry is not None:
        math_plain = (
            f"${spend:,.2f} spend ÷ {enquiries} enquiries = "
            f"${cpl_enquiry:,.2f} per enquiry"
        )
        math_booked = (
            f"${spend:,.2f} spend ÷ {booked} sales calls booked = "
            f"${cpl_booked:,.2f} per booked call"
            if cpl_booked is not None
            else None
        )
        status = "has_leads"
    else:
        math_plain = (
            "Cost per enquiry: not yet (no AU lead report in email)."
        )
        math_booked = None
        status = "waiting_on_leads"

    return {
        **meta,
        "status": status,
        "spend_usd": spend,
        "impressions": impr,
        "clicks": clicks,
        "avg_cpc_usd": _avg_cpc(spend, clicks) if clicks else stage1.get("avg_cpc_usd"),
        "cost_per_enquiry_usd": cpl_enquiry,
        "cost_per_sales_call_booked_usd": cpl_booked,
        "math_plain": math_plain,
        "math_booked_call": math_booked,
        "breakdown": (
            f"{enquiries} enquiries · {booked} sales calls booked"
            if enquiries is not None
            else "Lead counts not reported yet"
        ),
        "by_day": day_rows,
        "dates_with_spend": [r["date"] for r in day_rows if float(r.get("cost_usd") or 0) > 0],
    }


def _refresh_operator_insights(
    performance_us: dict[str, Any] | None,
    performance_au: dict[str, Any] | None,
    early_cpl: dict[str, Any] | None,
    early_au: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Copy OPERATOR_NOTES and overwrite spend / CPL lines from this pull."""
    op = json.loads(json.dumps(OPERATOR_NOTES))  # deep copy
    us = performance_us or {}
    au = performance_au or {}
    us_w = us.get("totals_stage1_last_7_days") or us.get("totals_last_7_days") or {}
    au_w = au.get("totals_stage1_last_7_days") or {}
    focus = us.get("totals_focus_day") or {}
    us_cost = float(us_w.get("cost_usd") or 0)
    us_clicks = int(us_w.get("clicks") or 0)
    us_cpc = us_w.get("avg_cpc_usd")
    au_cost = float(au_w.get("cost_usd") or 0)
    au_clicks = int(au_w.get("clicks") or 0)
    au_cpc = au_w.get("avg_cpc_usd")
    focus_cost = float(focus.get("cost_usd") or 0)

    cpl = early_cpl or {}
    cpl_line = (
        f"US early cost per lead ({cpl.get('label') or 'Aug 8–10'}): "
        f"{cpl.get('math_plain') or '—'}. "
        f"{cpl.get('math_booked_call') or ''}. "
        f"{cpl.get('breakdown') or ''}. "
        f"{cpl.get('caveat') or 'Early / small sample.'}"
    ).replace(" . ", ". ").strip()

    eau = early_au or {}
    if eau.get("cost_per_enquiry_usd") is not None:
        au_early_line = (
            f"Australia early cost per lead ({eau.get('label') or 'Aug 8–10'}): "
            f"{eau.get('math_plain') or '—'}. "
            f"{eau.get('math_booked_call') or ''}. "
            f"{eau.get('caveat') or 'Early / small sample.'}"
        ).replace(" . ", ". ").strip()
    elif float(eau.get("spend_usd") or 0) > 0 or int(eau.get("clicks") or 0) > 0:
        au_early_line = (
            f"Australia — early / waiting on lead counts "
            f"({eau.get('label') or 'Aug 8–10'}): "
            f"${float(eau.get('spend_usd') or 0):,.2f} spend · "
            f"{int(eau.get('clicks') or 0)} clicks"
            + (
                f" · about ${float(eau['avg_cpc_usd']):.0f} each"
                if eau.get("avg_cpc_usd") is not None
                else ""
            )
            + ". CPL not available until ops reports AU enquiries."
        )
    else:
        au_early_line = (
            "Australia — early / waiting on lead counts. "
            "New Search live; CPL waits on first ops enquiry report."
        )

    us_line = (
        f"US (pull window): ${us_cost:,.0f} spent · {us_clicks} clicks"
        + (f" · ${us_cpc:.2f} each" if us_cpc is not None else "")
        + ". Core Search is cheaper and busier. Role Search is more specific and costs more."
    )
    focus_line = (
        f"US daily plan is about $125. Latest day in pull ran about ${focus_cost:,.0f} — watch spend vs budget."
        if focus_cost > 0
        else "US daily plan is about $125 — watch spend vs budget on high days."
    )
    au_line = (
        f"Australia new Search: ${au_cost:,.0f} · {au_clicks} clicks"
        + (f" · about ${au_cpc:.0f} each" if au_cpc is not None else "")
        + ". Older paused campaigns are not in the VC_* table."
        if au_cost > 0 or au_clicks > 0
        else "Australia new Search: waiting on traffic in this pull."
    )

    honesty_bits = [
        "US and Australia Search are live. Paying per click until call tracking is trusted.",
    ]

    op["insights"] = [
        cpl_line,
        au_early_line,
        us_line,
        focus_line,
        "Almost all US ad clicks still land on the US home page. Role pages are live but quiet.",
        au_line,
        "Still paying per click. US phone · Australia 1300. A tap is not the same as a real conversation.",
        "Clear Recommendations in Google Ads every day. That is how Google scores the account.",
    ]
    op["honesty"] = " ".join(honesty_bits)
    op["early_cpl_summary"] = cpl.get("math_plain")
    op["early_au_summary"] = eau.get("math_plain")
    return op


def _normalize_neg_text(raw: str) -> tuple[str, str]:
    """Return (clean_text, match_kind) where match_kind is phrase|broad."""
    s = (raw or "").strip()
    # Editor CSV often stores Phrase as """work as"""
    if s.count('"') >= 2 or (s.startswith('"') and s.endswith('"')):
        text = re.sub(r'^"+|"+$', "", s).strip().strip('"').strip()
        return text, "phrase"
    return s.strip(), "broad"


def load_operator_negatives(csv_path: Path = US_EDITOR_CSV) -> dict[str, Any]:
    """Read VC_US_* campaign negatives from Editor CSV (no Ads API)."""
    items: list[dict[str, Any]] = []
    if not csv_path.is_file():
        return {
            "source": "missing_editor_csv",
            "label": "operator-negatived",
            "items": [],
            "jobseekers_live": [],
        }

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("Criterion Type") or "") != "Campaign negative":
                continue
            camp = row.get("Campaign") or ""
            if not camp.startswith("VC_US_"):
                continue
            text, kind = _normalize_neg_text(row.get("Keyword") or "")
            if not text:
                continue
            comment = row.get("Comment") or ""
            cohort = (
                "VC_Neg_JobSeekers_Live"
                if "VC_Neg_JobSeekers_Live" in comment
                else "stage1_curated"
            )
            items.append(
                {
                    "text": text,
                    "match": kind,
                    "cohort": cohort,
                    "campaign": camp,
                }
            )

    # Dedupe by text+match, prefer JobSeekers cohort label
    by_key: dict[str, dict[str, Any]] = {}
    for it in items:
        key = f"{it['text'].casefold()}|{it['match']}"
        prev = by_key.get(key)
        if not prev or (
            prev.get("cohort") != "VC_Neg_JobSeekers_Live"
            and it["cohort"] == "VC_Neg_JobSeekers_Live"
        ):
            by_key[key] = {
                "text": it["text"],
                "match": it["match"],
                "cohort": it["cohort"],
            }

    uniq = sorted(by_key.values(), key=lambda x: (x["cohort"] != "VC_Neg_JobSeekers_Live", x["text"]))
    jobseek = [x["text"] for x in uniq if x["cohort"] == "VC_Neg_JobSeekers_Live"]
    return {
        "source": "editor_csv_vc_us_campaign_negatives",
        "label": "operator-negatived",
        "csv": str(csv_path.relative_to(REPO)) if csv_path.is_relative_to(REPO) else str(csv_path),
        "unique_count": len(uniq),
        "jobseekers_live": jobseek,
        "items": uniq,
    }


def _neg_matches_term(term: str, neg_text: str, match: str) -> bool:
    t = term.casefold().strip()
    n = neg_text.casefold().strip()
    if not t or not n:
        return False
    if match == "phrase":
        return re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", t) is not None
    # Broad: every negative token must appear as a whole word
    words = set(t.split())
    return all(tok in words for tok in n.split())


def annotate_term_negatives(
    terms: list[dict[str, Any]], negatives_payload: dict[str, Any]
) -> list[dict[str, Any]]:
    negs = negatives_payload.get("items") or []
    out = []
    for term in terms:
        text = term.get("search_term") or ""
        hits = [
            n
            for n in negs
            if _neg_matches_term(text, n["text"], n.get("match") or "broad")
        ]
        row = dict(term)
        if hits:
            # Prefer JobSeekers_Live hit for display
            hits.sort(key=lambda n: (n.get("cohort") != "VC_Neg_JobSeekers_Live", n["text"]))
            primary = hits[0]
            row["negatived"] = True
            row["negatived_status"] = "Negatived — not bidding"
            row["negatived_label"] = "operator-negatived"
            row["negatived_cohort"] = primary.get("cohort")
            row["negatived_by"] = primary.get("text")
        else:
            row["negatived"] = False
        out.append(row)
    return out


def summarize_search_terms(rows: list[Any], *, top_n: int = 15) -> dict[str, Any]:
    agg: dict[str, dict[str, Any]] = {}
    for row in rows:
        term = row.search_term_view.search_term
        camp = row.campaign.name
        key = term.casefold().strip()
        slot = agg.setdefault(
            key,
            {
                "search_term": term,
                "campaigns": set(),
                "impressions": 0,
                "clicks": 0,
                "cost_usd": 0.0,
            },
        )
        slot["campaigns"].add(camp)
        slot["impressions"] += int(row.metrics.impressions or 0)
        slot["clicks"] += int(row.metrics.clicks or 0)
        slot["cost_usd"] += _money(row.metrics.cost_micros)

    scored = []
    for slot in agg.values():
        scored.append(
            {
                "search_term": slot["search_term"],
                "campaigns": sorted(slot["campaigns"]),
                **_metrics_blob(
                    int(slot["impressions"]),
                    int(slot["clicks"]),
                    float(slot["cost_usd"]),
                ),
            }
        )
    scored.sort(key=lambda r: (r["clicks"], r["cost_usd"], r["impressions"]), reverse=True)

    negatives = load_operator_negatives()
    top = annotate_term_negatives(scored[:top_n], negatives)
    return {
        "window": "LAST_7_DAYS",
        "source": "google_ads_api",
        "row_count_raw": len(rows),
        "unique_terms": len(scored),
        "top_by_clicks": top,
        "negatives": {
            "source": negatives.get("source"),
            "label": negatives.get("label"),
            "unique_count": negatives.get("unique_count"),
            "jobseekers_live": negatives.get("jobseekers_live"),
            "note": (
                "Matched against Editor CSV campaign negatives (VC_US_*), "
                "including VC_Neg_JobSeekers_Live Phrase cohort. "
                "Historical clicks may still show from before the negative was live."
            ),
        },
    }


def _term_maps_to_lp(term: str, hints: tuple[str, ...]) -> bool:
    t = term.casefold()
    return any(h in t for h in hints)


def derive_landing_pages(campaigns: dict[str, Any] | None) -> dict[str, Any]:
    """Catalog US LPs + CORE campaign metrics on hub. No search-term API.

    Snapshot budget is 2/2 for US + AU campaign pulls — no landing_page_view.
    """
    camp_by_name = {
        c["name"]: c for c in ((campaigns or {}).get("campaigns") or [])
    }
    core = camp_by_name.get("VC_US_S_CORE") or {}
    roles = camp_by_name.get("VC_US_S_ROLES") or {}
    core_m = core.get("last_7_days") or _metrics_blob(0, 0, 0.0)
    roles_m = roles.get("last_7_days") or _metrics_blob(0, 0, 0.0)

    pages: list[dict[str, Any]] = []
    for meta in US_LP_CATALOG:
        slug = meta["slug"]
        if slug == "us":
            metrics = dict(core_m)
            attribution = "VC_US_S_CORE Final URL → /us"
        else:
            # Role LPs live; per-URL spend needs Ads UI / later GA4 — not a 3rd API call
            metrics = _metrics_blob(0, 0, 0.0)
            attribution = (
                f"Live category LP (ROLES campaign "
                f"{int(roles_m.get('clicks') or 0)} clicks / 7d — not split by URL here)"
            )

        pages.append(
            {
                "name": meta["name"],
                "path": meta["path"],
                "url": meta["url"],
                "why": meta["why"],
                "attribution": attribution,
                "signal_terms": [],
                **metrics,
            }
        )

    pages.sort(key=lambda p: (p.get("clicks") or 0, p.get("impressions") or 0), reverse=True)

    return {
        "window": (campaigns or {}).get("window") or "LAST_7_DAYS",
        "source": "derived_from_campaign_final_urls",
        "source_note": (
            "Hub metrics = VC_US_S_CORE. Role LPs are live; "
            "per-URL split skipped (API budget = US+AU campaigns only)."
        ),
        "label": "US LP catalog + CORE traffic",
        "roles_unmapped_clicks": int(roles_m.get("clicks") or 0),
        "roles_campaign_clicks": int(roles_m.get("clicks") or 0),
        "pages": pages,
    }


def main() -> int:
    load_dotenv(SG_ROOT / ".env", override=False)
    if VC_ENV.is_file():
        load_dotenv(VC_ENV, override=True)

    settings = load_settings(env_file=SG_ROOT / ".env")
    api_calls: list[dict[str, Any]] = []
    started = datetime.now(timezone.utc).isoformat()

    try:
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        print(f"ERROR building client: {exc}", file=sys.stderr)
        return 1

    us_rows: list[Any] = []
    au_rows: list[Any] = []

    # Call 1 — US VC_* campaign metrics (status + spend)
    try:
        print(
            f"API call 1/2: VC_US_% campaign metrics {US_PULL_START}→{US_PULL_END} …",
            flush=True,
        )
        us_rows = fetch_rows(client, US_ID, CAMPAIGN_Q_US)
        api_calls.append(
            {
                "n": 1,
                "name": "campaign_metrics_vc_us_date_range",
                "ok": True,
                "row_count": len(us_rows),
                "date_range": f"{US_PULL_START}_to_{US_PULL_END}",
            }
        )
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call 1: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 1, "name": "campaign_metrics_vc_us_date_range", "ok": False, "error": str(exc)}
        )
        _write_payload(started, api_calls, None, None, hard_stop=str(exc))
        return 1
    except ApiAccessError as exc:
        print(f"STOP API on call 1: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 1, "name": "campaign_metrics_vc_us_date_range", "ok": False, "error": str(exc)}
        )
        _write_payload(started, api_calls, None, None, hard_stop=str(exc))
        return 1

    # Call 2 — AU active campaigns, same 14-day by-date window (split last 7 vs prior 7 in Python).
    try:
        print(
            f"API call 2/2: AU campaigns with impressions {AU_PULL_START}→{AU_PULL_END} …",
            flush=True,
        )
        au_rows = fetch_rows(client, AU_ID, CAMPAIGN_Q_AU)
        api_calls.append(
            {
                "n": 2,
                "name": "campaign_metrics_au_active_14d",
                "ok": True,
                "row_count": len(au_rows),
                "date_range": f"{AU_PULL_START}_to_{AU_PULL_END}",
            }
        )
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call 2: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 2, "name": "campaign_metrics_au_active_14d", "ok": False, "error": str(exc)}
        )
        us = summarize_campaigns(us_rows)
        _write_payload(started, api_calls, us, None, hard_stop=str(exc))
        return 1
    except ApiAccessError as exc:
        print(f"STOP API on call 2: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 2, "name": "campaign_metrics_au_active_14d", "ok": False, "error": str(exc)}
        )
        us = summarize_campaigns(us_rows)
        _write_payload(started, api_calls, us, None, hard_stop=str(exc))
        return 1

    us = summarize_campaigns(us_rows)
    us["window"] = f"{US_PULL_START}_to_{US_PULL_END}"
    us["window_note"] = (
        f"VC_US_% · segments.date BETWEEN {US_PULL_START} AND {US_PULL_END} "
        "(14-day by-date · last 7 vs prior 7 split in Python · no 3rd Ads call)"
    )
    au = summarize_campaigns(au_rows)
    au["window"] = f"{AU_PULL_START}_to_{AU_PULL_END}"
    au["window_note"] = (
        f"AU campaigns with impressions · BETWEEN {AU_PULL_START} AND {AU_PULL_END} "
        "(14-day by-date · last 7 vs prior 7 split in Python)"
    )
    # Do NOT fabricate fake VC_AU $0 "Enabled" shells — that hid real legacy spend.
    if not (au.get("campaigns") or []):
        zero = _metrics_blob(0, 0, 0.0)
        au = {
            "window": f"{AU_PULL_START}_to_{AU_PULL_END}",
            "focus_day": None,
            "focus_day_note": "No AU campaigns with impressions in the 14-day window",
            "totals_focus_day": zero,
            "totals_last_7_days": zero,
            "totals_prior_7_days": zero,
            "totals_stage1_last_7_days": zero,
            "totals_stage1_prior_7_days": zero,
            "totals_legacy_last_7_days": zero,
            "campaigns": [],
            "dates_in_pull": [],
        }
    path = _write_payload(started, api_calls, us, au, hard_stop=None)
    print(f"Wrote {path}")
    print(f"API calls used: {len(api_calls)} (max 2)")
    return 0


def _write_payload(
    started: str,
    api_calls: list[dict[str, Any]],
    performance_us: dict[str, Any] | None,
    performance_au: dict[str, Any] | None,
    *,
    hard_stop: str | None,
) -> Path:
    finished = datetime.now(timezone.utc).isoformat()
    # No search-term API — empty shell keeps LP derive + negatives CSV-only.
    negatives = load_operator_negatives()
    search_terms = {
        "window": "LAST_7_DAYS",
        "source": "skipped_by_design",
        "row_count_raw": 0,
        "unique_terms": 0,
        "top_by_clicks": [],
        "negatives": {
            "source": negatives.get("source"),
            "label": negatives.get("label"),
            "unique_count": negatives.get("unique_count"),
            "jobseekers_live": negatives.get("jobseekers_live"),
            "note": "Search terms not pulled (2-call budget = US + AU campaigns only).",
        },
    }
    landing_pages = derive_landing_pages(performance_us)
    early_cpl = build_early_cpl_us(performance_us) if performance_us else None
    early_au = build_early_au_preliminary(performance_au) if performance_au else None
    operator = _refresh_operator_insights(
        performance_us, performance_au, early_cpl, early_au
    )
    payload = {
        "generated_at_utc": finished,
        "pull_started_utc": started,
        "customer_ids": {"us": US_ID, "au": AU_ID},
        "filter": (
            f"VC_US_% {US_PULL_START}→{US_PULL_END} + AU active campaigns "
            f"{AU_PULL_START}→{AU_PULL_END} (14d by-date · last 7 vs prior 7 in Python)"
        ),
        "api_calls_used": len(api_calls),
        "api_calls_max": 2,
        "api_calls": api_calls,
        "hard_stop": hard_stop,
        "conversions_note": (
            "US CORE/ROLES on Maximize Conversions. Primary stack (George): phone click, "
            "60s calls from ads, 60s website calls, VC_US_Thank_You (GTM v5). Old actions "
            "Secondary, not deleted. Thank-you may show Inactive until a gclid-attributed fire. "
            "Phone click is a tap — demote when volume exists. Job seekers never count. "
            "Early CPL still uses sales-ops enquiry counts. AU website tags wait on AU GTM."
        ),
        "performance_us": performance_us,
        "performance_au": performance_au,
        "early_cpl_us": early_cpl,
        "early_cpl_au": early_au,
        # Backward compat for older UI readers
        "performance": performance_us,
        "customer_id": US_ID,
        "search_terms": search_terms,
        "search_terms_executive": {
            "surface": False,
            "reason": "No search-term dump on Executive.",
        },
        "keywords": KEYWORD_THEMES,
        "landing_pages": landing_pages,
        "operator": operator,
    }
    prev: dict[str, Any] = {}
    if OUT.is_file():
        try:
            prev = json.loads(OUT.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}
    payload["sales_ops_us"] = build_sales_ops_us(performance_us, prev.get("sales_ops_us"))
    if prev.get("sales_ops_au"):
        payload["sales_ops_au"] = prev["sales_ops_au"]
    for keep in (
        "impression_share",
        "impression_share_merged_at_utc",
        "ga4",
        "ga4_merged_at_utc",
    ):
        if prev.get(keep) is not None:
            payload[keep] = prev[keep]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    return OUT


if __name__ == "__main__":
    raise SystemExit(main())
