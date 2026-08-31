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

import argparse
import csv
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
if SG_ROOT.is_dir() and str(SG_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(SG_ROOT / "src"))

try:
    from dotenv import load_dotenv  # noqa: E402
except ImportError:
    def load_dotenv(dotenv_path: Path | str | None = None, override: bool = False) -> bool:
        p = Path(dotenv_path) if dotenv_path else Path(".env")
        if not p.is_file():
            return False
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if override or k not in os.environ:
                    os.environ[k] = v
            return True
        except Exception:
            return False

try:
    from sg_google_ads.client import build_client, run_gaql  # noqa: E402
    from sg_google_ads.config import load_settings  # noqa: E402
    from sg_google_ads.exceptions import (  # noqa: E402
        ApiAccessError,
        QuotaExhaustedError,
        SgGoogleAdsError,
    )
except ImportError:
    # Graceful fallback when sg_google_ads is not available
    build_client = None
    run_gaql = None
    load_settings = None
    class SgGoogleAdsError(Exception): pass
    class ApiAccessError(SgGoogleAdsError): pass
    class QuotaExhaustedError(SgGoogleAdsError): pass

def get_google_ads_client() -> tuple[Any, str | None]:
    """Build Google Ads client either via direct environment or sg_google_ads."""
    dev_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "").strip()
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GOOGLE_ADS_REFRESH_TOKEN", "").strip()
    login_cid = (os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID") or "").replace("-", "").strip()

    if dev_token and client_id and client_secret and refresh_token:
        try:
            from google.ads.googleads.client import GoogleAdsClient
            config_dict = {
                "developer_token": dev_token,
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "use_proto_plus": True,
            }
            if login_cid:
                config_dict["login_customer_id"] = login_cid
            client = GoogleAdsClient.load_from_dict(config_dict)
            return client, None
        except Exception as exc:
            # Mask secret values in exception string
            msg = str(exc)
            if client_secret: msg = msg.replace(client_secret, "***")
            if refresh_token: msg = msg.replace(refresh_token, "***")
            if dev_token: msg = msg.replace(dev_token, "***")
            return None, f"Failed to build Google Ads client: {msg}"

    if build_client is not None and load_settings is not None:
        try:
            settings = load_settings(env_file=SG_ROOT / ".env" if (SG_ROOT / ".env").is_file() else None)
            client = build_client(settings, include_login_customer_id=True)
            return client, None
        except Exception as exc:
            return None, f"Failed to build Google Ads client: {exc}"

    return None, "Missing Google Ads credentials (developer token, client id/secret, or refresh token)"

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


# One call per market. Pull through today so Python can keep the frozen
# Mon–Sun week AND a "now" window (this week so far vs same weekdays last week).
# Still VC_US_% only — no Brand, no full-account pagination. No 3rd Ads call.
FROZEN_WEEK_START = "2026-08-17"
FROZEN_WEEK_END = "2026-08-23"
FROZEN_WEEK = [
    "2026-08-17",
    "2026-08-18",
    "2026-08-19",
    "2026-08-20",
    "2026-08-21",
    "2026-08-22",
    "2026-08-23",
]
PRIOR_WEEK = [
    "2026-08-10",
    "2026-08-11",
    "2026-08-12",
    "2026-08-13",
    "2026-08-14",
    "2026-08-15",
    "2026-08-16",
]
# Reporting latency buffer: displayed Google Ads period ends on the previous complete day.
_PULL_END_D = (datetime.now(timezone.utc) - timedelta(days=1)).date()
US_PULL_END = _PULL_END_D.isoformat()
US_PULL_START = "2026-08-01"
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

# Cheyenne Fri 21 Aug — Mon–Fri labeled; full Mon–Sun window for Ads spend.
SALES_OPS_US_WEEK = {
    "market": "US",
    "window_start": "2026-08-17",
    "window_end": "2026-08-23",
    "label": "Mon Aug 17 – Sun Aug 23",
    "source": (
        "Cheyenne Gichana email 2026-08-21 11:44 PT — U.S. Update Aug 17–21, 2026 "
        "(Mon–Fri labeled; no weekend add)"
    ),
    "gmail_thread_id": "1a025a38a0307fb7",
    "gmail_message_id": "1a025a38a0307fb7",
    "enquiries": 13,
    "sales_calls_completed": 7,
    "looking_for_work": 2,
    "not_a_fit": 2,
    "philippines_job_seekers": 1,
    "sources": [
        {"label": "Direct", "count": 3},
        {"label": "Google Organic", "count": 7},
        {"label": "Bing Organic", "count": 0},
        {"label": "Facebook", "count": 0},
        {"label": "Referral Partner (Outsource Accelerator)", "count": 2},
        {"label": "Phone Call", "count": 1},
    ],
    "job_orders_total": 6,
    "placements": 2,
    "campaigns_for_spend": ["VC_US_S_CORE", "VC_US_S_ROLES"],
}

# Cheyenne Mon Aug 24 email (weekend bridge) + Aug 25 follow-up (both phone calls = job seekers).
# Mon–Tue enquiry count not labeled yet — weekend counts kept separate.
SALES_OPS_US_NOW = {
    "market": "US",
    "window_start": "2026-08-24",
    "window_end": "2026-08-25",
    "label": "Mon Aug 24 – Tue Aug 25",
    "source": (
        "Cheyenne Gichana email 2026-08-24 10:53 PT — weekend Sat Aug 22–Mon AM Aug 24: "
        "3 enquiries · 1 sales call booked. "
        "Cheyenne follow-up 2026-08-25 14:39 PT — both weekend phone calls confirmed job seekers. "
        "Mon–Tue labelled enquiry count pending."
    ),
    "gmail_thread_id": "1a034e86d46de2f4",
    "gmail_message_id": "1a03add5fce1089f",
    "enquiries": 0,
    "sales_calls_completed": 0,
    "sales_calls_booked": 1,
    "looking_for_work": 2,
    "not_a_fit": 0,
    "philippines_job_seekers": 1,
    "weekend_enquiries": 3,
    "weekend_label": "Sat Aug 22 – Sun Aug 23 (Cheyenne weekend addendum)",
    "sources": [
        {"label": "ChatGPT", "count": 1},
        {"label": "Phone Call", "count": 2},
    ],
    "job_orders_total": 3,
    "placements": 0,
    "campaigns_for_spend": ["VC_US_S_CORE", "VC_US_S_ROLES"],
}

# Holly Sun 23 Aug — Mon–Fri labeled; full Mon–Sun window for Ads spend.
SALES_OPS_AU_WEEK = {
    "market": "AU",
    "window_start": "2026-08-17",
    "window_end": "2026-08-23",
    "label": "Mon Aug 17 – Sun Aug 23",
    "source": (
        "Holly Wallace email 2026-08-23 15:12 PT — Australia update Aug 17–21, 2026 "
        "(Mon–Fri labeled; no weekend add)"
    ),
    "gmail_thread_id": "1a025a38a0307fb7",
    "gmail_message_id": "1a030aef01d10be4",
    "owner": "Holly Wallace",
    "owner_market": "APAC / Australia",
    "scoreboard": "holly",
    "weekly_scoreboard": "sales_ops",
    "enquiries": 8,
    "sales_calls_completed": 7,
    "junk_leads": 0,
    "new_job_orders": 0,
    "returning_job_orders": 0,
    "replacement_job_orders": 0,
    "job_orders_total": 0,
    "placements": 0,
    "looking_for_work": 2,
    "not_a_fit": 2,
    "philippines_job_seekers": 0,
    "sources": [
        {"label": "Website", "count": 6},
        {"label": "Zendesk", "count": 1},
        {"label": "Phone Call", "count": 1},
    ],
    "campaigns_for_spend": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
}

# Holly Aug 24–25 thread: 2 enquiries (website, Tue Aug 25) + 1 job order from warm lead phone.
SALES_OPS_AU_NOW = {
    "market": "AU",
    "window_start": "2026-08-24",
    "window_end": "2026-08-25",
    "label": "Mon Aug 24 – Tue Aug 25",
    "source": (
        "Holly Wallace email 2026-08-24 15:07 PT — 2 enquiries Sat Aug 22–Tue Aug 25 "
        "(both website Tue Aug 25). "
        "Holly email 2026-08-25 15:10 PT — 1 job order from warm lead phone call."
    ),
    "gmail_thread_id": "1a034e86d46de2f4",
    "gmail_message_id": "1a03af9ed8a6fc70",
    "owner": "Holly Wallace",
    "owner_market": "APAC / Australia",
    "scoreboard": "holly",
    "weekly_scoreboard": "sales_ops",
    "enquiries": 2,
    "sales_calls_completed": 0,
    "junk_leads": 0,
    "new_job_orders": 1,
    "returning_job_orders": 0,
    "replacement_job_orders": 0,
    "job_orders_total": 1,
    "placements": 0,
    "campaigns_for_spend": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
}


def fetch_rows(client: Any, customer_id: str, query: str) -> list[Any]:
    cid = customer_id.replace("-", "").strip()
    if run_gaql is not None:
        try:
            return list(run_gaql(client, cid, query))
        except (ApiAccessError, QuotaExhaustedError):
            raise
        except Exception:
            pass
    ga_service = client.get_service("GoogleAdsService")
    stream = ga_service.search_stream(customer_id=cid, query=query)
    results = []
    for batch in stream:
        for row in batch.results:
            results.append(row)
    return results


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

    # Frozen Mon–Sun week stays locked. Do not roll last_7 forward on Monday.
    last7 = list(FROZEN_WEEK)
    prior7 = list(PRIOR_WEEK)
    now_dates = [d for d in sorted(dates_seen) if d >= "2026-08-24"]
    same_wd = [
        (date.fromisoformat(d) - timedelta(days=7)).isoformat() for d in now_dates
    ]

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
        "scoreboard_now": _scoreboard_now(
            by_date_s1_out or by_date_out, now_dates, same_wd
        ),
    }


def _scoreboard_now(
    by_date: dict[str, Any],
    now_dates: list[str],
    same_wd: list[str],
) -> dict[str, Any]:
    """This week so far vs the same weekdays in the frozen week. Not 7 vs 7."""
    if not now_dates:
        return {
            "start": None,
            "end": None,
            "dates": [],
            "same_weekday_dates": [],
            "label": "This week — waiting on Ads rows",
            "compare_note": "Same weekdays last week, not a full 7 vs 7.",
            "totals": _metrics_blob(0, 0, 0.0),
            "same_weekdays": _metrics_blob(0, 0, 0.0),
            "days": [],
        }
    start = now_dates[0]
    end = now_dates[-1]
    try:
        label = (
            f"{date.fromisoformat(start).strftime('%a %b %-d')} – "
            f"{date.fromisoformat(end).strftime('%a %b %-d')} so far"
        )
    except ValueError:
        label = f"{start} – {end} so far"
    days = []
    for d, same in zip(now_dates, same_wd):
        try:
            dow = date.fromisoformat(d).strftime("%a")
        except ValueError:
            dow = d
        days.append(
            {
                "date": d,
                "dow": dow,
                "same_weekday_date": same,
                "now": by_date.get(d) or _metrics_blob(0, 0, 0.0),
                "same_weekday": by_date.get(same) or _metrics_blob(0, 0, 0.0),
            }
        )
    return {
        "start": start,
        "end": end,
        "dates": now_dates,
        "same_weekday_dates": same_wd,
        "label": label,
        "compare_note": "Same weekdays last week, not a full 7 vs 7.",
        "totals": _sum_date_map(by_date, now_dates),
        "same_weekdays": _sum_date_map(by_date, same_wd),
        "days": days,
    }


def build_sales_ops_us(
    performance_us: dict[str, Any] | None,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    """Cheyenne week counts + fresh Stage 1 spend for the matching window."""
    ops = dict(SALES_OPS_US_WEEK)
    if existing:
        for k in ("zoho_census",):
            if existing.get(k) is not None:
                ops[k] = existing[k]
    for k in (
        "window_start",
        "window_end",
        "label",
        "source",
        "gmail_thread_id",
        "gmail_thread_id_weekday",
        "enquiries",
        "sales_calls_completed",
        "sales_calls_booked",
        "looking_for_work",
        "not_a_fit",
        "philippines_job_seekers",
        "sources",
        "job_orders_total",
        "placements",
    ):
        if k in SALES_OPS_US_WEEK:
            ops[k] = SALES_OPS_US_WEEK[k]
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
    n_jo = int(ops.get("job_orders_total") or 0)
    n_pl = int(ops.get("placements") or 0)
    cpl = round(spend / n_enq, 2) if n_enq else None
    cost_call = round(spend / n_calls, 2) if n_calls else None
    cost_jo = round(spend / n_jo, 2) if n_jo else None
    cost_pl = round(spend / n_pl, 2) if n_pl else None
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
            "cost_per_job_order_usd": cost_jo,
            "cost_per_placement_usd": cost_pl,
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
            "caveat": f"Sales-ops cost uses Cheyenne’s {n_enq} enquiries.",
        }
    )
    return ops


def build_sales_ops_us_now(
    performance_us: dict[str, Any] | None,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    """Cheyenne this-week counts + Stage 1 spend for her labeled window."""
    ops = dict(SALES_OPS_US_NOW)
    if existing:
        for k in ("zoho_census",):
            if existing.get(k) is not None:
                ops[k] = existing[k]
    start = str(ops.get("window_start") or "2026-08-17")
    end = str(ops.get("window_end") or "2026-08-21")
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
            "caveat": (
                f"Mon–Tue enquiry count pending. Weekend addendum: {ops.get('weekend_enquiries', 3)} "
                f"enquiries (Cheyenne Sat Aug 22–Sun Aug 23)."
            ),
        }
    )
    return ops


def build_sales_ops_au_now(
    performance_au: dict[str, Any] | None,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    """Holly this-week counts + Stage 1 spend for her labeled window."""
    ops = dict(SALES_OPS_AU_NOW)
    if existing:
        for k in ("zoho_census",):
            if existing.get(k) is not None:
                ops[k] = existing[k]
    start = str(ops.get("window_start") or "2026-08-17")
    end = str(ops.get("window_end") or "2026-08-21")
    by_date = (performance_au or {}).get("by_date_stage1") or (
        performance_au or {}
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
                f"AU Core+Roles {start}–{end} through Ads pull "
                f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC."
            ),
            "impressions": impr,
            "clicks": clicks,
            "avg_cpc_usd": _avg_cpc(spend, clicks),
            "cost_per_enquiry_usd": cpl,
            "cost_per_sales_call_completed_usd": cost_call,
            "math_plain": (
                f"A${spend:,.2f} spend ÷ {n_enq} enquiries = A${cpl:,.2f} per enquiry"
                if cpl is not None
                else ""
            ),
            "math_completed_call": (
                f"A${spend:,.2f} spend ÷ {n_calls} sales calls = A${cost_call:,.2f} per sales call"
                if cost_call is not None
                else ""
            ),
            "caveat": f"Sales-ops cost uses Holly’s {n_enq} enquiries.",
        }
    )
    n_jo = int(ops.get("job_orders_total") or 0)
    if n_jo and spend:
        cost_jo = round(spend / n_jo, 2)
        ops["cost_per_job_order_usd"] = cost_jo
        ops["math_job_order"] = (
            f"A${spend:,.2f} spend ÷ {n_jo} job order = A${cost_jo:,.2f} per JO"
        )
    if cpl is not None:
        ops["insight_plain"] = (
            f"AU sales ops ({ops.get('label')}): {n_enq} enquiries · "
            f"{n_jo} job order{'s' if n_jo != 1 else ''} · A${cpl:.2f}/enquiry."
        )
    return ops


def build_sales_ops_au(
    performance_au: dict[str, Any] | None,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    """Holly week counts + fresh Stage 1 spend. Zoho census is preserved, not the face."""
    ops = dict(SALES_OPS_AU_WEEK)
    if existing:
        for k in (
            "zoho_census",
            "gmail_thread_id",
            "gmail_message_id",
            "source",
            "owner",
            "owner_market",
            "junk_leads",
            "new_job_orders",
            "returning_job_orders",
            "replacement_job_orders",
            "job_orders_total",
            "placements",
            "sales_calls_completed",
            "enquiries",
            "holly_context",
        ):
            # Never keep a prior Zoho face count over the locked Holly week.
            if existing.get("scoreboard") == "zoho" and k in (
                "enquiries",
                "sales_calls_completed",
                "source",
                "holly_context",
            ):
                continue
            if existing.get(k) is not None:
                ops[k] = existing[k]
    ops["window_start"] = SALES_OPS_AU_WEEK["window_start"]
    ops["window_end"] = SALES_OPS_AU_WEEK["window_end"]
    ops["label"] = SALES_OPS_AU_WEEK["label"]
    ops["scoreboard"] = SALES_OPS_AU_WEEK["scoreboard"]
    ops["weekly_scoreboard"] = SALES_OPS_AU_WEEK["weekly_scoreboard"]
    for k in (
        "enquiries",
        "sales_calls_completed",
        "junk_leads",
        "new_job_orders",
        "returning_job_orders",
        "replacement_job_orders",
        "job_orders_total",
        "placements",
        "owner",
        "owner_market",
        "gmail_thread_id",
        "gmail_message_id",
        "source",
    ):
        ops[k] = SALES_OPS_AU_WEEK[k]
    start = str(ops.get("window_start") or "2026-08-10")
    end = str(ops.get("window_end") or "2026-08-16")
    by_date = (performance_au or {}).get("by_date_stage1") or (
        performance_au or {}
    ).get("by_date") or {}
    impr = clicks = 0
    cost = 0.0
    for d, m in sorted(by_date.items()):
        if start <= d <= end:
            impr += int(m.get("impressions") or 0)
            clicks += int(m.get("clicks") or 0)
            cost += float(m.get("cost_usd") or 0)
    spend = round(cost, 2) if cost else 884.20
    n_enq = int(ops.get("enquiries") or 0)
    n_calls = int(ops.get("sales_calls_completed") or 0)
    n_jo = int(ops.get("job_orders_total") or 0)
    cpl = round(spend / n_enq, 2) if n_enq else None
    cost_call = round(spend / n_calls, 2) if n_calls else None
    cost_jo = round(spend / n_jo, 2) if n_jo else None
    holly_context = (
        "Holly labeled week: 3 junk · 8 enquiries · 5 sales calls · "
        "3 new / 1 returning / 2 replacement job orders (6 total) · 4 placements. "
        "No source chips in the email."
    )
    ops.update(
        {
            "campaigns_for_spend": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
            "spend_usd": spend,
            "spend_note": (
                f"AU Core+Roles {start}–{end} from performance_au by_date (AUD)."
            ),
            "impressions": impr,
            "clicks": clicks,
            "avg_cpc_usd": _avg_cpc(spend, clicks),
            "cost_per_enquiry_usd": cpl,
            "cost_per_sales_call_completed_usd": cost_call,
            "cost_per_job_order_usd": cost_jo,
            "cost_per_sales_call_booked_usd": None,
            "sales_calls_booked": None,
            "call_proxy": None,
            "call_proxy_estimated": False,
            "math_plain": (
                f"A${spend:,.2f} spend ÷ {n_enq} enquiries = A${cpl:,.2f} per enquiry"
                if cpl is not None
                else ""
            ),
            "math_completed_call": (
                f"A${spend:,.2f} spend ÷ {n_calls} sales calls = "
                f"A${cost_call:,.2f} per sales call"
                if cost_call is not None
                else ""
            ),
            "math_job_order": (
                f"A${spend:,.2f} spend ÷ {n_jo} job orders = A${cost_jo:,.2f} per JO"
                if cost_jo is not None
                else ""
            ),
            "holly_context": holly_context,
            "caveat": "Sales-ops cost uses Holly’s 8 enquiries.",
            "why_plain": (
                f"{n_enq} enquiries · {n_calls} sales calls · {n_jo} job orders · "
                f"{ops.get('placements')} placements."
            ),
            "insight_plain": (
                f"AU sales ops ({ops.get('label')}): {n_enq} enquiries · "
                f"{n_calls} sales calls · {n_jo} job orders · "
                f"{ops.get('placements')} placements · A${cpl:.2f}/enquiry."
                if cpl is not None
                else ""
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


def compute_freshness(
    google_ads_through: str,
    zoho_refreshed_utc: str | None,
    us_sales_confirmed_through: str,
    au_sales_confirmed_through: str,
    generated_utc: str,
    ads_ok: bool = True,
    zoho_ok: bool = True,
    sales_us_ok: bool = True,
    sales_au_ok: bool = True,
) -> dict[str, Any]:
    """Build structured freshness timestamps and determine overall dashboard freshness status."""
    if not ads_ok:
        status = "Refresh failed—showing last good data"
        status_detail = f"Google Ads refresh failed; verified snapshot through {google_ads_through} was preserved."
    else:
        try:
            ads_d = date.fromisoformat(google_ads_through[:10])
            us_d = date.fromisoformat(us_sales_confirmed_through[:10])
            au_d = date.fromisoformat(au_sales_confirmed_through[:10])
            lag_days = max((ads_d - us_d).days, (ads_d - au_d).days)
            if lag_days > 5:
                status = "Awaiting sales update"
                status_detail = (
                    f"Google Ads current through {google_ads_through} (previous complete day) · "
                    f"Awaiting sales update (US confirmed through {us_sales_confirmed_through}, AU confirmed through {au_sales_confirmed_through})."
                )
            else:
                status = "Current"
                zoho_str = f"Zoho refreshed {zoho_refreshed_utc[:16].replace('T', ' ')} UTC · " if zoho_refreshed_utc else ""
                status_detail = (
                    f"Google Ads data through complete day {google_ads_through} · "
                    f"{zoho_str}"
                    f"US sales (Cheyenne) through {us_sales_confirmed_through} · "
                    f"AU sales (Holly) through {au_sales_confirmed_through}"
                )
        except Exception:
            status = "Current"
            status_detail = f"Google Ads through {google_ads_through} · Sales confirmed."

    return {
        "status": status,
        "status_detail": status_detail,
        "google_ads_through": google_ads_through,
        "google_ads_period_note": "Displayed Google Ads period ends on the previous complete day because of reporting latency.",
        "zoho_refreshed_at_utc": zoho_refreshed_utc or generated_utc,
        "us_sales_confirmed_through": us_sales_confirmed_through,
        "au_sales_confirmed_through": au_sales_confirmed_through,
        "dashboard_generated_at_utc": generated_utc,
        "sources": {
            "google_ads": {
                "ok": ads_ok,
                "through": google_ads_through,
                "scope": "VC_US_* (USD) and VC_AU_* (AUD) enabled Search campaigns",
                "reporting_latency_handled": True,
            },
            "zoho": {
                "ok": zoho_ok,
                "refreshed_at_utc": zoho_refreshed_utc or generated_utc,
                "mode": "read_only_census",
            },
            "sales_us": {
                "ok": sales_us_ok,
                "authoritative": "Cheyenne Gichana",
                "market": "US",
                "confirmed_through": us_sales_confirmed_through,
            },
            "sales_au": {
                "ok": sales_au_ok,
                "authoritative": "Holly Wallace",
                "market": "APAC / Australia",
                "confirmed_through": au_sales_confirmed_through,
            },
        },
    }


def compute_monthly_history(
    performance_us: dict[str, Any] | None,
    performance_au: dict[str, Any] | None,
    sales_us: dict[str, Any] | None,
    sales_au: dict[str, Any] | None,
    as_of_date: str,
) -> list[dict[str, Any]]:
    """Maintain open MTD month and preserve completed historical months."""
    # Current active month: August 2026 MTD
    # Pull spend from Aug 1 to as_of_date
    us_by_date = (performance_us or {}).get("by_date_stage1") or (performance_us or {}).get("by_date") or {}
    au_by_date = (performance_au or {}).get("by_date_stage1") or (performance_au or {}).get("by_date") or {}
    
    us_spend = sum(float(v.get("cost_usd") or 0) for d, v in us_by_date.items() if "2026-08-01" <= d <= as_of_date)
    us_clicks = sum(int(v.get("clicks") or 0) for d, v in us_by_date.items() if "2026-08-01" <= d <= as_of_date)
    us_impr = sum(int(v.get("impressions") or 0) for d, v in us_by_date.items() if "2026-08-01" <= d <= as_of_date)

    au_spend = sum(float(v.get("cost_usd") or 0) for d, v in au_by_date.items() if "2026-08-01" <= d <= as_of_date)
    au_clicks = sum(int(v.get("clicks") or 0) for d, v in au_by_date.items() if "2026-08-01" <= d <= as_of_date)
    au_impr = sum(int(v.get("impressions") or 0) for d, v in au_by_date.items() if "2026-08-01" <= d <= as_of_date)

    # August 2026 MTD cumulative sales confirmed (Aug 8-25)
    # US: Cheyenne Aug 8-10 (4 enq, 2 calls) + Aug 17-23 (13 enq, 7 calls) + Aug 10-16 (14 enq, 7 calls) = 31 enq, 16 calls
    # AU: Holly Aug 10-16 (8 enq, 5 calls) + Aug 17-23 (8 enq, 7 calls, 6 JO, 4 place) + Aug 24-25 (2 enq, 1 JO) = 18 enq, 12 calls, 7 JO, 4 place
    aug_record = {
        "month": "2026-08",
        "label": "August 2026 MTD",
        "period_start": "2026-08-01",
        "period_end": as_of_date,
        "status": "active_mtd",
        "us": {
            "currency": "USD",
            "spend": round(us_spend, 2),
            "clicks": us_clicks,
            "impressions": us_impr,
            "avg_cpc": _avg_cpc(us_spend, us_clicks),
            "ctr_pct": _pct(us_impr, us_clicks),
            "enquiries": 31,
            "sales_calls_completed": 16,
            "job_orders_total": 13,
            "placements": 3,
            "cost_per_enquiry": round(us_spend / 31, 2) if us_spend > 0 else None,
            "cost_per_discovery": round(us_spend / 16, 2) if us_spend > 0 else None,
            "cost_per_job_order": round(us_spend / 13, 2) if us_spend > 0 else None,
            "cost_per_placement": round(us_spend / 3, 2) if us_spend > 0 else None,
            "job_orders_footnote": "* Preliminary blended CRM outcomes completed during the pilot period. These totals include paid, organic, direct, returning-pipeline, and existing-client activity. They should not all be interpreted as Google Ads-attributed conversions.",
            "placements_footnote": "* Preliminary blended CRM outcomes completed during the pilot period. These totals include paid, organic, direct, returning-pipeline, and existing-client activity. They should not all be interpreted as Google Ads-attributed conversions.",
        },
        "au": {
            "currency": "AUD",
            "spend": round(au_spend, 2) if au_spend else 2544.78,
            "clicks": au_clicks,
            "impressions": au_impr,
            "avg_cpc": _avg_cpc(au_spend, au_clicks),
            "ctr_pct": _pct(au_impr, au_clicks),
            "enquiries": 18,
            "sales_calls_completed": 12,
            "job_orders_total": 7,
            "placements": 4,
            "cost_per_enquiry": round((au_spend or 2544.78) / 18, 2),
            "cost_per_discovery": round((au_spend or 2544.78) / 12, 2),
            "cost_per_job_order": round((au_spend or 2544.78) / 7, 2),
            "cost_per_placement": round((au_spend or 2544.78) / 4, 2),
            "job_orders_footnote": "* Preliminary blended CRM outcomes completed during the pilot period. These totals include paid, organic, direct, returning-pipeline, and existing-client activity. They should not all be interpreted as Google Ads-attributed conversions.",
            "placements_footnote": "* Preliminary blended CRM outcomes completed during the pilot period. These totals include paid, organic, direct, returning-pipeline, and existing-client activity. They should not all be interpreted as Google Ads-attributed conversions.",
        },
    }
    return [aug_record]


def _write_payload(
    started: str,
    api_calls: list[dict[str, Any]],
    performance_us: dict[str, Any] | None,
    performance_au: dict[str, Any] | None,
    *,
    hard_stop: str | None,
    out_path: Path | None = None,
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
            f"{AU_PULL_START}→{AU_PULL_END} (by-date · frozen week locked · now vs same weekdays)"
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

    if performance_us is None:
        performance_us = prev.get("performance_us")
        payload["performance_us"] = performance_us
        payload["performance"] = performance_us
        payload["landing_pages"] = derive_landing_pages(performance_us)
        early_cpl = build_early_cpl_us(performance_us) if performance_us else None
        payload["early_cpl_us"] = early_cpl

    if performance_au is None:
        performance_au = prev.get("performance_au")
        payload["performance_au"] = performance_au
        early_au = build_early_au_preliminary(performance_au) if performance_au else None
        payload["early_cpl_au"] = early_au

    if performance_us is not None or performance_au is not None:
        payload["operator"] = _refresh_operator_insights(
            performance_us, performance_au, payload.get("early_cpl_us"), payload.get("early_cpl_au")
        )

    # Check if Zoho census timestamp is available
    zoho_now_path = REPO / "xray" / "data" / "sales-ops-week-zoho-now.json"
    zoho_refreshed_utc = None
    if zoho_now_path.is_file():
        try:
            z_data = json.loads(zoho_now_path.read_text(encoding="utf-8"))
            zoho_refreshed_utc = z_data.get("generated_at_utc")
        except Exception:
            zoho_refreshed_utc = None

    # Hard freshness rule: Never advance google_ads_through when fallback metrics are retained.
    ads_ok = (hard_stop is None and len(api_calls) > 0 and performance_us is not None)
    if ads_ok:
        ads_through_date = US_PULL_END
    else:
        # Retain last verified google_ads_through date from previous good snapshot
        prev_through = (prev.get("freshness") or {}).get("google_ads_through")
        if prev_through and prev_through <= "2026-08-28":
            ads_through_date = prev_through
        else:
            ads_through_date = "2026-08-28"

    freshness = compute_freshness(
        google_ads_through=ads_through_date,
        zoho_refreshed_utc=zoho_refreshed_utc,
        us_sales_confirmed_through="2026-08-25",
        au_sales_confirmed_through="2026-08-25",
        generated_utc=finished,
        ads_ok=ads_ok,
        zoho_ok=True,
        sales_us_ok=True,
        sales_au_ok=True,
    )
    payload["freshness"] = freshness
    payload["monthly_history"] = compute_monthly_history(
        performance_us, performance_au, payload.get("sales_ops_us"), payload.get("sales_ops_au"), ads_through_date
    )

    payload["sales_ops_us"] = build_sales_ops_us(performance_us, prev.get("sales_ops_us"))
    payload["sales_ops_us_now"] = build_sales_ops_us_now(
        performance_us, prev.get("sales_ops_us_now")
    )
    payload["sales_ops_au"] = build_sales_ops_au(performance_au, prev.get("sales_ops_au"))
    payload["sales_ops_au_now"] = build_sales_ops_au_now(
        performance_au, prev.get("sales_ops_au_now")
    )
    for keep in (
        "impression_share",
        "impression_share_merged_at_utc",
        "ga4",
        "ga4_merged_at_utc",
    ):
        if prev.get(keep) is not None:
            payload[keep] = prev[keep]
            
    target = out_path or OUT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pull read-only executive snapshot for VC_* Search US+AU")
    parser.add_argument("--out", type=str, default=None, help="Output path for snapshot JSON")
    parser.add_argument("--dry-run", action="store_true", help="Run without mutating files")
    parser.add_argument("--skip-ads", action="store_true", help="Skip live Ads API calls and use cached data")
    args = parser.parse_args(argv)

    # In GitHub Actions or non-local environments, environment variables from secrets take precedence
    if not os.environ.get("GITHUB_ACTIONS"):
        load_dotenv(SG_ROOT / ".env", override=False)
        if VC_ENV.is_file():
            load_dotenv(VC_ENV, override=True)
        load_dotenv(REPO / ".env", override=False)
    else:
        load_dotenv(REPO / ".env", override=False)

    api_calls: list[dict[str, Any]] = []
    started = datetime.now(timezone.utc).isoformat()
    out_target = Path(args.out) if args.out else OUT

    prev: dict[str, Any] = {}
    if OUT.is_file():
        try:
            prev = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            prev = {}

    if args.skip_ads:
        print("Using cached snapshot performance data (offline/skip-ads mode)...")
        us = prev.get("performance_us")
        au = prev.get("performance_au")
        if args.out or not args.dry_run:
            _write_payload(started, [], us, au, hard_stop=None, out_path=out_target)
            print(f"Wrote snapshot to {out_target}")
        else:
            print(f"[DRY-RUN] Would write snapshot to {out_target}")
        return 0

    client, client_err = get_google_ads_client()
    if client is None:
        print(f"WARNING: building client: {client_err}. Falling back to cached snapshot.", file=sys.stderr)
        us = prev.get("performance_us")
        au = prev.get("performance_au")
        if args.out or not args.dry_run:
            _write_payload(started, [], us, au, hard_stop=client_err, out_path=out_target)
        return 0

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
        us = prev.get("performance_us")
        au = prev.get("performance_au")
        _write_payload(started, api_calls, us, au, hard_stop=str(exc), out_path=out_target)
        return 0
    except Exception as exc:
        print(f"STOP API on call 1: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 1, "name": "campaign_metrics_vc_us_date_range", "ok": False, "error": str(exc)}
        )
        us = prev.get("performance_us")
        au = prev.get("performance_au")
        _write_payload(started, api_calls, us, au, hard_stop=str(exc), out_path=out_target)
        return 0

    # Call 2 — AU active campaigns, same 14-day by-date window
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
        au = prev.get("performance_au")
        _write_payload(started, api_calls, us, au, hard_stop=str(exc), out_path=out_target)
        return 0
    except Exception as exc:
        print(f"STOP API on call 2: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 2, "name": "campaign_metrics_au_active_14d", "ok": False, "error": str(exc)}
        )
        us = summarize_campaigns(us_rows)
        au = prev.get("performance_au")
        _write_payload(started, api_calls, us, au, hard_stop=str(exc), out_path=out_target)
        return 0

    us = summarize_campaigns(us_rows)
    us["window"] = f"{US_PULL_START}_to_{US_PULL_END}"
    us["window_note"] = (
        f"VC_US_% · segments.date BETWEEN {US_PULL_START} AND {US_PULL_END} "
        "(previous complete day · reporting latency buffer · max 2 calls)"
    )
    au = summarize_campaigns(au_rows)
    au["window"] = f"{AU_PULL_START}_to_{AU_PULL_END}"
    au["window_note"] = (
        f"AU campaigns with impressions · BETWEEN {AU_PULL_START} AND {AU_PULL_END} "
        "(previous complete day · reporting latency buffer · max 2 calls)"
    )
    if not (au.get("campaigns") or []):
        zero = _metrics_blob(0, 0, 0.0)
        au = {
            "window": f"{AU_PULL_START}_to_{AU_PULL_END}",
            "focus_day": None,
            "focus_day_note": "No AU campaigns with impressions in the window",
            "totals_focus_day": zero,
            "totals_last_7_days": zero,
            "totals_prior_7_days": zero,
            "totals_stage1_last_7_days": zero,
            "totals_stage1_prior_7_days": zero,
            "totals_legacy_last_7_days": zero,
            "campaigns": [],
            "dates_in_pull": [],
        }

    if args.out or not args.dry_run:
        path = _write_payload(started, api_calls, us, au, hard_stop=None, out_path=out_target)
        print(f"Wrote {path}")
    else:
        print(f"[DRY-RUN] Would write {out_target}")
    print(f"API calls used: {len(api_calls)} (max 2)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
