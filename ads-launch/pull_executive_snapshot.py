#!/usr/bin/env python3
"""Read-only executive snapshot for VC_* Search US+AU (max 2 GAQL calls).

Hard rules:
- No mutate / upload / enable
- On RESOURCE_EXHAUSTED: STOP, do not retry
- Exactly 2 light calls: US campaigns + AU campaigns (status + spend)
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
from datetime import datetime, timezone
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

# Qualitative operator notes (not from API) — kept honest for CEO walkthroughs
# Executive shows curated buyer signals + themes — never raw early ST dumps.
OPERATOR_NOTES = {
    "narrative_as_of": "2026-08-09",
    "status_banner": (
        "North star = qualified business value — not form-fill volume. "
        "Phone is Ads conversion north star for now; consult booking later; Max Conv later. "
        "US Stage 1 live (~$298 early window for 1 employer + 1 job-seeker; not real CPA). "
        "Hot: website calls 60+ sec · AU GTM still a gap · modeled lead score on form (analytics only) · Zoho qualify later."
    ),
    "budgets": [
        {"label": "US", "amount": "~$125/day", "detail": "live", "kind": "live_test"},
        {"label": "Australia", "amount": "legacy spend live", "detail": "PM_AU_* in window", "kind": "priority"},
    ],
    "whats_working": {
        "ad_copy_themes": [
            "Hire Filipino / Philippines VA (employer path)",
            "Dedicated seat — not a marketplace gig",
            "You interview the shortlist before anyone joins",
            "Staffing partner for SMBs — not a job board",
        ],
        "note": "Ops read of live RSA themes — not an Ads asset-ranking export.",
    },
    "insights": [
        (
            "US CORE is the volume engine (~16% CTR, ~$2 CPC). "
            "ROLES costs more per click — useful for role LP tests, not the main dial yet."
        ),
        (
            "Keyword priority = employer agency-hire intent: Philippines VA / staffing "
            "agency · firm · company · outsourcing. Plain “hire/recruit” is messier "
            "(employer vs job-seeker). Odd shorthand (e.g. “va workers ph”) stays "
            "watch / pause if it eats spend. Job-seeker junk stays off this page."
        ),
        (
            "Almost all measurable US clicks still land on /us (CORE Final URL). "
            "Role LPs are live; per-URL spend needs Ads UI / GA4 later."
        ),
        (
            "Australia account spend in the last 7 days is mostly legacy PM_AU_* Search "
            "(Paused mid-window can still show in LAST_7_DAYS). Stage 1 VC_AU_* is not driving it."
        ),
        (
            "Conversion posture: do not train bidding on raw form fills. "
            "Phone is Ads conversion north star for now; consult booking later; Max Conv later. "
            "Early US ~$300 per unknown-quality inquiry is a gut check only. "
            "Website now captures company size × positions → modeled lead_score / $ for analytics (not Ads bidding). "
            "Zoho Qualified → Job Order → Placement is the truth ladder; CRM value supersedes the site estimate."
        ),
        (
            "AU phone: GBP / listing stays 1300 886 740 (4.8★ / 23 Sydney). "
            "US Google 5.0★ / 39 + Clutch on LP (yellow stars, not yellow boxes). "
            "1300 voicemail still says Alex — Holly / Chey / Raffie. "
            "Public dial stays 1300 — not a personal mobile. AU GTM/GA4 still a gap; US GTM/GA4 live."
        ),
        (
            "Thank-you: Call still conversion lead (888 / 1300). "
            "Bordered booking overlay auto-opens on eligible TY "
            "(US “Book your 30-minute hiring consult” / AU “Book a 30-minute hiring chat”) + Call. "
            "Close + Pick a time reopens. Not Ads primary. "
            "Job seeker tap → location.replace(https://virtualcoworker.com.ph) so Back stays off the employer LP. "
            "Homepage H1 locked (“Your week is full…”) unless George asks."
        ),
    ],
    "buyer_signals": [
        {
            "term": "philippines virtual assistant agency",
            "why": "Highest-intent shape · employer looking for a PH VA agency",
            "market": "US",
        },
        {
            "term": "philippines outsourcing agency",
            "why": "Agency / outsourcing buyer language · not a job seeker",
            "market": "US",
        },
        {
            "term": "remote staffing agency / agencies",
            "why": "Staffing-agency wording buyers actually use",
            "market": "US",
        },
        {
            "term": "virtual assistant firm / company",
            "why": "Firm/company = shopping for a provider, not a gig listing",
            "market": "US",
        },
        {
            "term": "va workers ph",
            "why": "Watch / pause candidate · odd shorthand, not a clean win if spend climbs",
            "market": "US",
        },
    ],
    "lp_highlights": [
        {
            "name": "US hub (/us)",
            "why": "CORE Final URL — carries most US clicks and spend",
            "url": "https://www.virtualcoworker.app/us",
        },
        {
            "name": "Role LPs (admin, bookkeeping, CSR, marketing…)",
            "why": "Live for ROLES · good for creative tests once call tracking is solid",
            "url": "https://www.virtualcoworker.app/us/administrative-support",
        },
        {
            "name": "Australia hub (/au)",
            "why": "Live with 1300 · GBP 4.8★ / 23 + Clutch · form chips (size + positions) · Caitlin copy",
            "url": "https://www.virtualcoworker.app/au",
        },
        {
            "name": "Quiz LPs (later, ~70%)",
            "why": "Not traffic-ready. Rework later. Quiz not highlighted enough yet — likely needs quiz-as-hero, not a homepage-clone widget. Ads Paused. Enable George-only (never auto-complete). Checklist step 36.",
            "url": "https://www.virtualcoworker.app/us/quiz",
        },
    ],
    "whats_next": [
        "<strong>Website calls 60+ seconds</strong> — US + AU (bidding signal)",
        "<strong>AU GTM/GA4 + ad-call wins</strong> — still a gap vs US",
        "<strong>Review thank-you overlay US/AU</strong> — Call + book · not Ads primary (Checklist step 37)",
        "<strong>AU 1300 voicemail</strong> — fix Alex greeting (Holly / Chey / Raffie)",
        "<strong>Then Zoho qualified → Ads</strong> — modeled site value is estimate only",
        "<strong>Later — Quiz LP (~70%)</strong> — Rework later. Not traffic-ready. Ads Paused. Enable George-only. Checklist step 36.",
    ],
    "coming_soon": [
        "Quiz LP (~70%) — rework later · not traffic-ready · VC_US_S_QUIZ / VC_AU_S_QUIZ Paused · Enable George-only",
        "Consult booking as Ads signal later · Max Conv later (phone north star for now)",
        "Modeled lead value → CRM override ladder (not Ads bidding yet)",
        "Site tests scoreboard (GTM/GA4 wiring — still blank) · messaging A/B later (H1 locked)",
    ],
    "done_today": [
        "AU phone on site (1300 886 740)",
        "US Search live · Brand off · US GTM/GA4 live",
        "Form chips (company size + positions) + modeled $ on /us /au (analytics only)",
        "Google stars US 5.0/39 · AU 4.8/23 + Clutch (yellow stars, not boxes)",
        "Caitlin copy live · job-seeker hard redirect to virtualcoworker.com.ph",
        "Thank-you overlay live (Call + book · not Ads primary) — review US/AU still open",
        "Team updated (Holly + Caitlin threads)",
        "Quiz LP parked ~70% — rework later (Paused ads, not highlighted enough yet)",
    ],
    "honesty": (
        "Optimize toward qualified business value — not form-fill volume. "
        "Phone is Ads conversion north star for now; consult booking later; Max Conv later. "
        "US Stage 1 live; early ~$300/inquiry is noise. AU GBP 4.8★/23 + US 5.0★/39 + Clutch on LP. "
        "1300 listing stays, voicemail still Alex. AU GTM still a gap. "
        "Modeled $ on site is estimate only until Zoho. Thank-you: Call + booking overlay (not Ads primary). "
        "Quiz LP ~70% — not traffic-ready, rework later; ads still Paused. "
        "Homepage H1 locked unless George asks."
    ),
    "lp_ab_note": (
        "Homepage H1 locked (“Your week is full…”) unless George asks. Messaging A/B later. "
        "Site tests scoreboard still needs GTM/GA4 wiring — see Checklist step 35."
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


def _metrics_blob(impressions: int, clicks: int, cost: float) -> dict[str, Any]:
    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr_pct": _pct(impressions, clicks),
        "cost_usd": round(cost, 2),
        "avg_cpc_usd": _avg_cpc(cost, clicks),
    }


CAMPAIGN_Q_US = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.average_cpc,
      metrics.ctr
    FROM campaign
    WHERE campaign.name LIKE 'VC_US_%'
      AND campaign.status != 'REMOVED'
      AND segments.date DURING LAST_7_DAYS
"""

# AU account has legacy PM_AU_* spend + optional Stage 1 VC_AU_*.
# Filter by activity (impressions > 0) — NOT VC_AU_% only (that lied at $0 while PM_AU spent).
CAMPAIGN_Q_AU = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.average_cpc,
      metrics.ctr
    FROM campaign
    WHERE campaign.status != 'REMOVED'
      AND segments.date DURING LAST_7_DAYS
      AND metrics.impressions > 0
"""


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


def summarize_campaigns(rows: list[Any]) -> dict[str, Any]:
    by_campaign: dict[str, dict[str, Any]] = {}
    by_date: dict[str, dict[str, int | float]] = {}
    today_key = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Account timezone may differ; also track max date present as "latest day in pull"
    dates_seen: set[str] = set()

    for row in rows:
        name = row.campaign.name
        status = row.campaign.status.name if hasattr(row.campaign.status, "name") else str(row.campaign.status)
        date = str(row.segments.date)
        dates_seen.add(date)
        impr = int(row.metrics.impressions or 0)
        clicks = int(row.metrics.clicks or 0)
        cost = _money(row.metrics.cost_micros)

        slot = by_campaign.setdefault(
            name,
            {
                "name": name,
                "status": status,
                "cohort": _campaign_cohort(name),
                "impressions": 0,
                "clicks": 0,
                "cost_usd": 0.0,
                "by_date": {},
            },
        )
        slot["impressions"] += impr
        slot["clicks"] += clicks
        slot["cost_usd"] += cost
        dslot = slot["by_date"].setdefault(date, {"impressions": 0, "clicks": 0, "cost_usd": 0.0})
        dslot["impressions"] += impr
        dslot["clicks"] += clicks
        dslot["cost_usd"] += cost

        g = by_date.setdefault(date, {"impressions": 0, "clicks": 0, "cost_usd": 0.0})
        g["impressions"] += impr
        g["clicks"] += clicks
        g["cost_usd"] += cost

    latest = max(dates_seen) if dates_seen else today_key
    today_totals = by_date.get(today_key) or by_date.get(latest) or {
        "impressions": 0,
        "clicks": 0,
        "cost_usd": 0.0,
    }
    # Prefer calendar today if present; else note latest day in window
    today_label = today_key if today_key in by_date else latest
    today_is_utc_calendar = today_key in by_date

    week_impr = sum(int(v["impressions"]) for v in by_date.values())
    week_clicks = sum(int(v["clicks"]) for v in by_date.values())
    week_cost = sum(float(v["cost_usd"]) for v in by_date.values())

    campaigns_out = []
    for name, slot in sorted(by_campaign.items(), key=lambda kv: -float(kv[1]["cost_usd"])):
        campaigns_out.append(
            {
                "name": name,
                "status": slot["status"],
                "cohort": slot.get("cohort") or _campaign_cohort(name),
                "last_7_days": _metrics_blob(
                    int(slot["impressions"]),
                    int(slot["clicks"]),
                    float(slot["cost_usd"]),
                ),
                "focus_day": _metrics_blob(
                    int(slot["by_date"].get(today_label, {}).get("impressions", 0)),
                    int(slot["by_date"].get(today_label, {}).get("clicks", 0)),
                    float(slot["by_date"].get(today_label, {}).get("cost_usd", 0.0)),
                ),
            }
        )

    stage1 = [c for c in campaigns_out if c.get("cohort") == "stage1"]
    legacy = [c for c in campaigns_out if c.get("cohort") != "stage1"]
    def _sum_camps(camps: list[dict[str, Any]]) -> dict[str, Any]:
        impr = sum(int((c.get("last_7_days") or {}).get("impressions") or 0) for c in camps)
        clicks = sum(int((c.get("last_7_days") or {}).get("clicks") or 0) for c in camps)
        cost = sum(float((c.get("last_7_days") or {}).get("cost_usd") or 0) for c in camps)
        return _metrics_blob(impr, clicks, cost)

    return {
        "window": "LAST_7_DAYS",
        "focus_day": today_label,
        "focus_day_note": (
            "UTC calendar today present in pull"
            if today_is_utc_calendar
            else "UTC today not in rows yet — showing latest date in LAST_7_DAYS window"
        ),
        "totals_focus_day": _metrics_blob(
            int(today_totals["impressions"]),
            int(today_totals["clicks"]),
            float(today_totals["cost_usd"]),
        ),
        "totals_last_7_days": _metrics_blob(week_impr, week_clicks, week_cost),
        "totals_stage1_last_7_days": _sum_camps(stage1),
        "totals_legacy_last_7_days": _sum_camps(legacy),
        "campaigns": campaigns_out,
        "dates_in_pull": sorted(dates_seen),
    }


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
        print("API call 1/2: VC_US_% campaign metrics LAST_7_DAYS …", flush=True)
        us_rows = fetch_rows(client, US_ID, CAMPAIGN_Q_US)
        api_calls.append(
            {
                "n": 1,
                "name": "campaign_metrics_vc_us_last_7_days",
                "ok": True,
                "row_count": len(us_rows),
            }
        )
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call 1: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 1, "name": "campaign_metrics_vc_us_last_7_days", "ok": False, "error": str(exc)}
        )
        _write_payload(started, api_calls, None, None, hard_stop=str(exc))
        return 1
    except ApiAccessError as exc:
        print(f"STOP API on call 1: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 1, "name": "campaign_metrics_vc_us_last_7_days", "ok": False, "error": str(exc)}
        )
        _write_payload(started, api_calls, None, None, hard_stop=str(exc))
        return 1

    # Call 2 — AU account campaigns with impressions in LAST_7_DAYS (legacy PM_AU_* + any VC_AU_*).
    try:
        print("API call 2/2: AU campaigns with impressions LAST_7_DAYS …", flush=True)
        au_rows = fetch_rows(client, AU_ID, CAMPAIGN_Q_AU)
        api_calls.append(
            {
                "n": 2,
                "name": "campaign_metrics_au_active_last_7_days",
                "ok": True,
                "row_count": len(au_rows),
            }
        )
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call 2: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 2, "name": "campaign_metrics_au_active_last_7_days", "ok": False, "error": str(exc)}
        )
        us = summarize_campaigns(us_rows)
        _write_payload(started, api_calls, us, None, hard_stop=str(exc))
        return 1
    except ApiAccessError as exc:
        print(f"STOP API on call 2: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": 2, "name": "campaign_metrics_au_active_last_7_days", "ok": False, "error": str(exc)}
        )
        us = summarize_campaigns(us_rows)
        _write_payload(started, api_calls, us, None, hard_stop=str(exc))
        return 1

    us = summarize_campaigns(us_rows)
    au = summarize_campaigns(au_rows)
    # Do NOT fabricate fake VC_AU $0 "Enabled" shells — that hid real legacy spend.
    if not (au.get("campaigns") or []):
        zero = _metrics_blob(0, 0, 0.0)
        au = {
            "window": "LAST_7_DAYS",
            "focus_day": None,
            "focus_day_note": "No AU campaigns with impressions in LAST_7_DAYS",
            "totals_focus_day": zero,
            "totals_last_7_days": zero,
            "totals_stage1_last_7_days": zero,
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
    payload = {
        "generated_at_utc": finished,
        "pull_started_utc": started,
        "customer_ids": {"us": US_ID, "au": AU_ID},
        "filter": "VC_US_% + AU campaigns with impressions LAST_7_DAYS",
        "api_calls_used": len(api_calls),
        "api_calls_max": 2,
        "api_calls": api_calls,
        "hard_stop": hard_stop,
        "conversions_note": "Phone wins not scored as KPIs here yet.",
        "performance_us": performance_us,
        "performance_au": performance_au,
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
        "operator": OPERATOR_NOTES,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    return OUT


if __name__ == "__main__":
    raise SystemExit(main())
