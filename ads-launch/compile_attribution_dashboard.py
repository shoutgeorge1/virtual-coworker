#!/usr/bin/env python3
"""Compile unified Ads → GA4 → Zoho attribution dashboard JSON.

Read-only. No Google Ads API calls. Joins on-disk snapshots + Zoho census artifacts.
Output: xray/data/attribution-unified.json

Refresh inputs first (optional, capped):
  pull_executive_snapshot.py / pull_ga4_executive.py / pull_impression_share.py /
  pull_daily_watch.py / Zoho probe scripts

Then:
  python3 ads-launch/compile_attribution_dashboard.py
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "xray" / "data"
OUT = DATA / "attribution-unified.json"
NUMBERS_CSV = (
    REPO
    / "ads-launch"
    / "ATTRIBUTION-RECOVERY-2026-08-13"
    / "ATTRIBUTION-NUMBERS-2026-08-13.csv"
)

# Configurable: separate noisy launch from cleaner Stage-1 traffic.
CLEAN_TRAFFIC_SINCE = "2026-08-08"


def load(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def money(n: Any) -> float | None:
    if n is None:
        return None
    try:
        return round(float(n), 2)
    except (TypeError, ValueError):
        return None


def pct(n: Any) -> float | None:
    if n is None:
        return None
    try:
        return round(float(n), 1)
    except (TypeError, ValueError):
        return None


def sync_status(ts: str | None, *, stale_hours: float = 36) -> dict[str, Any]:
    if not ts:
        return {"status": "missing", "last_success_utc": None, "age_hours": None}
    try:
        raw = ts.replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
        if age_h <= stale_hours:
            status = "healthy"
        elif age_h <= stale_hours * 2:
            status = "delayed"
        else:
            status = "stale"
        return {
            "status": status,
            "last_success_utc": ts,
            "age_hours": round(age_h, 1),
        }
    except Exception:
        return {"status": "failed", "last_success_utc": ts, "age_hours": None}


def event_count(events: list[dict], name: str) -> int:
    for e in events or []:
        if (e.get("event") or "") == name:
            return int(e.get("event_count") or 0)
    return 0


def classify_search_term(term: str, *, job_seeker_like: bool) -> str:
    t = (term or "").lower()
    if job_seeker_like:
        return "job_seeker"
    if any(x in t for x in ("job", "hiring near me", "salary", "resume", "work from home philippines")):
        return "job_seeker"
    if any(x in t for x in ("belay", "time etc", "upwork", "fiverr", "onlinejobs")):
        return "competitor"
    if any(x in t for x in ("bpo", "call center", "call centre", "outsourcing company")):
        return "bpo"
    if any(x in t for x in ("what is", "how to", "meaning of", "definition")):
        return "research"
    if any(x in t for x in ("medical", "nurse", "coding", "developer", "engineer")):
        return "irrelevant"
    if any(
        x in t
        for x in (
            "virtual assistant",
            "offshore",
            "filipino",
            "philippines",
            "bookkeep",
            "admin",
            "hire va",
            "va for",
        )
    ):
        return "likely_employer"
    return "ambiguous"


def load_zoho_numbers(path: Path) -> dict[str, Any]:
    out: dict[str, Any] = {"rows": [], "by_metric": {}}
    if not path.exists():
        return out
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out["rows"].append(row)
            key = row.get("metric") or ""
            out["by_metric"][key] = row
    return out


def stage1_campaigns(perf: dict | None, market: str) -> list[dict]:
    if not perf:
        return []
    rows = []
    for c in perf.get("campaigns") or []:
        name = c.get("name") or ""
        if not name.startswith(f"VC_{market}_"):
            continue
        if c.get("status") not in ("ENABLED", "PAUSED", None):
            continue
        last = c.get("last_7_days") or {}
        focus = c.get("focus_day") or {}
        rows.append(
            {
                "campaign": name,
                "status": c.get("status"),
                "cohort": c.get("cohort"),
                "market": market,
                "currency": "USD" if market == "US" else "AUD",
                "spend_7d": money(last.get("cost_usd")),
                "clicks_7d": last.get("clicks"),
                "impressions_7d": last.get("impressions"),
                "ctr_pct_7d": pct(last.get("ctr_pct")),
                "cpc_7d": money(last.get("avg_cpc_usd")),
                "spend_focus_day": money(focus.get("cost_usd")),
                "clicks_focus_day": focus.get("clicks"),
                "ads_conversions_7d": last.get("conversions"),
                "source": "Google Ads",
            }
        )
    return rows


def merge_is(campaigns: list[dict], is_block: dict | None) -> list[dict]:
    by_name = {c.get("name"): c for c in (is_block or {}).get("campaigns") or []}
    for row in campaigns:
        info = by_name.get(row["campaign"]) or {}
        row["search_is_pct"] = pct(info.get("search_is_pct"))
        row["lost_is_rank_pct"] = pct(info.get("lost_is_rank_pct"))
        row["lost_is_budget_pct"] = pct(info.get("lost_is_budget_pct"))
        row["search_top_is_pct"] = pct(info.get("search_top_is_pct"))
        row["search_abs_top_is_pct"] = pct(info.get("search_abs_top_is_pct"))
        row["daily_budget"] = money(info.get("daily_budget_usd"))
        # CRM outcomes not joined per campaign yet
        row["crm_qualified_outcomes"] = None
        row["crm_note"] = "Zoho not joined to campaign yet — see CRM outcomes block"
    return campaigns


def build_spend_windows(exec_snap: dict) -> dict[str, Any]:
    us = exec_snap.get("performance_us") or {}
    au = exec_snap.get("performance_au") or {}
    us_by = us.get("by_date") or {}
    au_by = au.get("by_date") or {}
    us_dates = sorted(us_by.keys())
    au_dates = sorted(au_by.keys())

    def sum_days(by_date: dict, dates: list[str]) -> dict[str, Any]:
        imp = clicks = 0
        cost = 0.0
        for d in dates:
            row = by_date.get(d) or {}
            imp += int(row.get("impressions") or 0)
            clicks += int(row.get("clicks") or 0)
            cost += float(row.get("cost_usd") or 0)
        return {
            "impressions": imp,
            "clicks": clicks,
            "cost": money(cost),
            "ctr_pct": pct((clicks / imp * 100) if imp else None),
            "cpc": money((cost / clicks) if clicks else None),
            "dates": dates,
        }

    us_focus = us.get("focus_day")
    au_focus = au.get("focus_day")

    def windows_for(by_date: dict, all_dates: list[str], focus: str | None, totals_7d: dict) -> dict:
        if not all_dates:
            return {}
        last = all_dates[-1]
        yday = all_dates[-2] if len(all_dates) >= 2 else None
        last3 = all_dates[-3:]
        clean = [d for d in all_dates if d >= CLEAN_TRAFFIC_SINCE]
        return {
            "today": {
                **sum_days(by_date, [last] if last else []),
                "label": f"Focus day {focus or last}",
                "note": "Calendar day present in last Ads pull — not live clock",
            },
            "yesterday": sum_days(by_date, [yday] if yday else []),
            "last_3_days": sum_days(by_date, last3),
            "last_7_days": {
                "impressions": totals_7d.get("impressions"),
                "clicks": totals_7d.get("clicks"),
                "cost": money(totals_7d.get("cost_usd")),
                "ctr_pct": pct(totals_7d.get("ctr_pct")),
                "cpc": money(totals_7d.get("avg_cpc_usd")),
                "dates": all_dates,
            },
            "since_clean_traffic": {
                **sum_days(by_date, clean),
                "since": CLEAN_TRAFFIC_SINCE,
            },
            "month_to_date": {
                "status": "unavailable",
                "note": "Need a dedicated MTD Ads pull — not in current snapshot",
            },
        }

    return {
        "US": {
            "currency": "USD",
            "source": "Google Ads",
            "window_note": us.get("window_note") or us.get("window"),
            "windows": windows_for(
                us_by, us_dates, us_focus, us.get("totals_stage1_last_7_days") or us.get("totals_last_7_days") or {}
            ),
        },
        "AU": {
            "currency": "AUD",
            "source": "Google Ads",
            "window_note": au.get("window_note") or au.get("window"),
            "note": "AUD amounts — do not sum with USD",
            "windows": windows_for(
                au_by,
                au_dates,
                au_focus,
                au.get("totals_stage1_last_7_days") or au.get("totals_last_7_days") or {},
            ),
        },
        "combined_spend_forbidden": True,
        "clean_traffic_since": CLEAN_TRAFFIC_SINCE,
    }


def build_alerts(
    *,
    us_clicks: int,
    au_clicks: int,
    form_starts: int,
    form_submits: int,
    phone_clicks: int,
    mobile_pct: float | None,
    ads_conv_us: Any,
    ga4_conv: Any,
    zoho_app_write: bool,
    search_terms: list[dict],
) -> list[dict]:
    alerts = []
    paid_clicks = (us_clicks or 0) + (au_clicks or 0)
    primary_site = form_submits + phone_clicks
    if paid_clicks >= 100 and primary_site == 0:
        alerts.append(
            {
                "id": "traffic_no_conversion",
                "severity": "high",
                "title": "Traffic but no primary website conversions",
                "detail": f"{paid_clicks} Stage-1 clicks in Ads window vs {form_submits} form submits / {phone_clicks} phone clicks in GA4 event list.",
                "evidence": ["Google Ads clicks", "GA4 events"],
            }
        )
    if form_starts >= 5 and form_submits == 0:
        alerts.append(
            {
                "id": "form_abandonment",
                "severity": "high",
                "title": "Form starts with no submissions in GA4 event list",
                "detail": f"GA4 shows form_start={form_starts}, no employer_inquiry_submitted in top events.",
                "evidence": ["GA4 form_start"],
            }
        )
    if mobile_pct is not None and mobile_pct >= 55:
        alerts.append(
            {
                "id": "mobile_mix",
                "severity": "medium",
                "title": "Paid Search majority mobile",
                "detail": f"Paid Search ~{mobile_pct}% mobile. Watch sticky/chat interference and form completion by device.",
                "evidence": ["GA4 device_by_channel"],
            }
        )
    if ads_conv_us in (0, 0.0, None) and ga4_conv in (0, 0.0, None):
        alerts.append(
            {
                "id": "tracking_desert",
                "severity": "medium",
                "title": "Ads + GA4 conversion columns both near zero",
                "detail": "Expected on Maximize Clicks while pipe is proven — but confirm GTM maps employer_inquiry_submitted / phone.",
                "evidence": ["Google Ads conversions", "GA4 conversions"],
            }
        )
    if not zoho_app_write:
        alerts.append(
            {
                "id": "crm_disconnect",
                "severity": "critical",
                "title": ".app leads are not writing to Zoho",
                "detail": "ZOHO_CRM_ENABLED is off. Website leads and Zoho Sales Enquiries are two movies. Email/webhook is the live design.",
                "evidence": ["Zoho census Aug 13", "vision zoho adapter"],
            }
        )
    waste = [t for t in search_terms if t.get("classification") in ("job_seeker", "irrelevant", "bpo") and (t.get("cost") or 0) >= 20]
    if waste:
        top = waste[0]
        alerts.append(
            {
                "id": "query_waste",
                "severity": "medium",
                "title": "Search term spend on weak intent",
                "detail": f"Top example: “{top.get('search_term')}” · ${top.get('cost')} · {top.get('classification')} · {top.get('campaign')}",
                "evidence": ["daily-watch search terms"],
                "action": "Review in Editor — do not auto-negative from this dashboard",
            }
        )
    return alerts


def build_recommendations(campaigns: list[dict], alerts: list[dict]) -> list[dict]:
    recs = []
    for c in campaigns:
        lost_rank = c.get("lost_is_rank_pct") or 0
        lost_budget = c.get("lost_is_budget_pct") or 0
        if lost_rank >= 50 and lost_budget <= 20:
            recs.append(
                {
                    "id": f"rank_{c['campaign']}",
                    "title": f"{c['campaign']} is rank-constrained, not budget-constrained",
                    "detail": (
                        f"Lost IS rank {lost_rank}% vs lost IS budget {lost_budget}%. "
                        "Raising budget alone is unlikely to fix auction coverage — check relevance, RSA, and CPC competitiveness."
                    ),
                    "evidence": [
                        f"search_is={c.get('search_is_pct')}%",
                        f"lost_rank={lost_rank}%",
                        f"lost_budget={lost_budget}%",
                    ],
                    "do_not": ["Add Broad Match", "Blindly raise budget"],
                }
            )
        if lost_budget >= 40 and lost_rank <= 30:
            recs.append(
                {
                    "id": f"budget_{c['campaign']}",
                    "title": f"{c['campaign']} is losing coverage to budget",
                    "detail": (
                        f"Lost IS budget {lost_budget}% vs lost IS rank {lost_rank}%. "
                        "If query quality is clean, budget is the bottleneck — still a human decision."
                    ),
                    "evidence": [f"lost_budget={lost_budget}%", f"lost_rank={lost_rank}%"],
                    "do_not": ["Auto-raise budget from this panel"],
                }
            )
    for a in alerts:
        if a["id"] == "crm_disconnect":
            recs.append(
                {
                    "id": "wire_zoho",
                    "title": "Wire .app → Zoho before trusting CRM outcomes on paid",
                    "detail": "Map utm_gclid (not $gclid). Keep writes off until Caitlin/Cheyenne confirm the qualified status. Stay on Maximize Clicks.",
                    "evidence": ["EXECUTIVE-TRUTH Aug 13", "ZOHO-DICTIONARY"],
                    "do_not": ["Offline import of historical 576 gclids as Primary"],
                }
            )
        if a["id"] == "form_abandonment":
            recs.append(
                {
                    "id": "form_ux",
                    "title": "Investigate form abandonment before scaling spend",
                    "detail": "GA4 form_start without matching submits. Confirm mobile sticky/chat no longer covers submit, and GTM maps employer_inquiry_submitted.",
                    "evidence": ["GA4 events", "conversion-assist hierarchy"],
                }
            )
    if not recs:
        recs.append(
            {
                "id": "keep_cleaning",
                "title": "Keep search-term hygiene; do not expand match types",
                "detail": "Signal-development phase. Exact + controlled Phrase. Dashboard is diagnostic — mutations stay in Editor.",
                "evidence": ["Stage 1 strategy"],
            }
        )
    return recs


def main() -> None:
    exec_snap = load(DATA / "executive-snapshot.json") or {}
    ga4 = load(DATA / "ga4-snapshot.json") or {}
    is_snap = load(DATA / "impression-share.json") or {}
    daily = load(DATA / "daily-watch.json") or {}
    recovery = load(DATA / "recovery-audit.json") or {}
    zoho_num = load_zoho_numbers(NUMBERS_CSV)

    us_perf = exec_snap.get("performance_us") or {}
    au_perf = exec_snap.get("performance_au") or {}
    us_stage = us_perf.get("totals_stage1_last_7_days") or us_perf.get("totals_last_7_days") or {}
    au_stage = au_perf.get("totals_stage1_last_7_days") or au_perf.get("totals_last_7_days") or {}

    campaigns = merge_is(stage1_campaigns(us_perf, "US"), is_snap.get("performance_us")) + merge_is(
        stage1_campaigns(au_perf, "AU"), is_snap.get("performance_au")
    )

    # Search terms
    search_terms: list[dict] = []
    for market_key, market_block in (daily.get("markets") or {}).items():
        top = ((market_block.get("search_terms") or {}).get("top_by_spend") or [])[:40]
        for row in top:
            term = row.get("search_term") or ""
            search_terms.append(
                {
                    "market": market_key,
                    "country": market_key,
                    "campaign": row.get("campaign"),
                    "ad_group": row.get("ad_group"),
                    "search_term": term,
                    "keyword": row.get("keyword"),
                    "match_type": row.get("match_type"),
                    "cost": money(row.get("cost_usd")),
                    "clicks": row.get("clicks"),
                    "impressions": row.get("impressions"),
                    "cpc": money(row.get("avg_cpc_usd") or row.get("cpc")),
                    "ads_conversions": row.get("conversions"),
                    "status": row.get("status"),
                    "classification": classify_search_term(
                        term, job_seeker_like=bool(row.get("job_seeker_like"))
                    ),
                    "crm_qualified": None,
                    "source": "Google Ads",
                    "window": daily.get("window"),
                }
            )

    events_top = ga4.get("events_top") or []
    form_starts = event_count(events_top, "form_start") + event_count(
        events_top, "employer_form_started"
    )
    form_submits = event_count(events_top, "employer_inquiry_submitted") + event_count(
        events_top, "form_submit_success"
    )
    phone_clicks = event_count(events_top, "phone_click") + event_count(
        events_top, "phone_cta_clicked"
    )
    quiz_starts = event_count(events_top, "quiz_started")
    quiz_completes = event_count(events_top, "quiz_completed")
    chat_opens = event_count(events_top, "chat_opened") + event_count(
        events_top, "chat_widget_open"
    )
    popup_shows = event_count(events_top, "exit_intent_shown") + event_count(
        events_top, "popup_impression"
    )

    ga4_totals = ga4.get("totals_last_7_days") or {}
    au_ga4 = (ga4.get("au") or {}).get("totals_last_7_days") or {}
    device = ga4.get("device_paid_search") or ga4.get("device") or {}
    mobile_pct = device.get("paid_search_mobile_pct")

    early_us = exec_snap.get("early_cpl_us") or {}
    early_au = exec_snap.get("early_cpl_au") or {}

    bm = zoho_num.get("by_metric") or {}

    def zm(metric: str) -> Any:
        row = bm.get(metric) or {}
        try:
            return int(row.get("n") or 0) if row.get("n") not in (None, "") else None
        except ValueError:
            return row.get("n")

    zoho_block = {
        "source": "Zoho CRM (read-only census Aug 13)",
        "gate": "NOT READY FOR CRM WRITES OR OFFLINE IMPORT",
        "app_writes_enabled": False,
        "modules": {
            "sales_enquiries": "Leads (UI: Sales Enquiries)",
            "job_orders": "Job_Orders",
            "placements": "Deals (UI: Placements)",
            "calls": "Calls (no gclid)",
        },
        "last_90d": {
            "sales_enquiries": 647,
            "job_orders": zm("zoho_job_orders_90d") or 242,
            "placements": 122,
            "calls": 379,
            "note": "All sources — not paid-search-only",
        },
        "gclid": {
            "enquiries_with_utm_gclid_all_time": zm("zoho_sales_enquiries_with_gclid") or 576,
            "job_orders_direct_utm_gclid": zm("zoho_jo_direct_gclid") or 18,
            "job_orders_click_linked_90d_sample": zm("zoho_jo_click_linked_90d_sample") or 69,
            "newest_30_enquiries_with_gclid": 0,
            "note": "After 5 Aug 2026 new enquiries stopped storing utm_gclid; .app not writing CRM",
        },
        "attribution_confidence": {
            "ads_to_zoho_jo_zapier": "ambiguous",
            "reason": "Zapier JO uploads (67 US / 36 AU) ≠ 782 CRM job orders; object mismatch",
        },
    }

    website = {
        "source": "GA4",
        "window": ga4.get("window"),
        "US": {
            "sessions": ga4_totals.get("sessions"),
            "users": ga4_totals.get("users"),
            "engaged_sessions": ga4_totals.get("engaged_sessions"),
            "engagement_rate_pct": ga4_totals.get("engagement_rate_pct"),
            "conversions_ga4": ga4_totals.get("conversions"),
        },
        "AU": {
            "sessions": au_ga4.get("sessions"),
            "users": au_ga4.get("users"),
            "engaged_sessions": au_ga4.get("engaged_sessions"),
            "engagement_rate_pct": au_ga4.get("engagement_rate_pct"),
            "note": (ga4.get("au") or {}).get("tags_live_since"),
        },
        "events": {
            "form_start": form_starts,
            "form_submit": form_submits,
            "phone_click": phone_clicks,
            "quiz_start": quiz_starts,
            "quiz_complete": quiz_completes,
            "chat_open": chat_opens,
            "popup_impression": popup_shows,
            "calendly_click": event_count(events_top, "calendly_click")
            + event_count(events_top, "calendly_cta_clicked"),
            "note": "Counts from GA4 top-events report — low-volume custom events may be missing from top-N",
        },
        "landing_pages": {
            "US": ga4.get("top_landing_pages") or [],
            "AU": (ga4.get("au") or {}).get("top_landing_pages") or [],
            "path_kind_sessions": ga4.get("path_kind_sessions"),
            "landing_compare": ga4.get("landing_compare"),
        },
        "device": {
            "paid_search_mobile": device.get("paid_search_mobile"),
            "paid_search_desktop": device.get("paid_search_desktop"),
            "paid_search_mobile_pct": mobile_pct,
            "verdict": device.get("verdict"),
            "note": device.get("note"),
        },
    }

    sales_ops = {
        "source": "Sales ops handoff (not Zoho join)",
        "US": {
            "window": early_us.get("label"),
            "enquiries": early_us.get("enquiries"),
            "sales_calls_booked": early_us.get("sales_calls_booked"),
            "junk_job_seeker": early_us.get("junk_job_seeker"),
            "not_a_fit": early_us.get("not_a_fit"),
            "spend_usd": early_us.get("spend_usd"),
            "cost_per_enquiry_usd": early_us.get("cost_per_enquiry_usd"),
            "cost_per_sales_call_booked_usd": early_us.get("cost_per_sales_call_booked_usd"),
            "caveat": early_us.get("caveat"),
        },
        "AU": {
            "status": early_au.get("status"),
            "enquiries": early_au.get("enquiries"),
            "spend_aud": early_au.get("spend_usd"),
            "caveat": early_au.get("caveat"),
        },
    }

    tiers = {
        "T0_click_session": {
            "ads_clicks_us_7d": us_stage.get("clicks"),
            "ads_clicks_au_7d": au_stage.get("clicks"),
            "ga4_sessions_us": ga4_totals.get("sessions"),
            "ga4_sessions_au": au_ga4.get("sessions"),
        },
        "T1_micro": {
            "form_start": form_starts,
            "quiz_start": quiz_starts,
            "chat_open": chat_opens,
            "popup_impression": popup_shows,
        },
        "T2_website_lead": {
            "form_submit": form_submits,
            "phone_click": phone_clicks,
            "sales_ops_enquiries_us": early_us.get("enquiries"),
            "note": "Phone click ≠ qualified call; form submit ≠ Ads Primary",
        },
        "T3_crm_qualified_employer": {
            "value": None,
            "status": "unavailable_for_paid",
            "note": ".app not in Zoho; human disposition required",
        },
        "T4_job_order": {
            "crm_all_sources_90d": zoho_block["last_90d"]["job_orders"],
            "click_linked_90d_sample": zoho_block["gclid"]["job_orders_click_linked_90d_sample"],
            "vc_star_campaigns": 0,
            "note": "Do not use 782 / Zapier 67 as VC_* truth",
        },
        "T5_placement": {
            "crm_all_sources_90d": zoho_block["last_90d"]["placements"],
            "click_linked": None,
            "note": "Deals have no click-id field",
        },
    }

    funnel = {
        "steps": [
            {"id": "ad_click", "label": "Ad click", "US": us_stage.get("clicks"), "AU": au_stage.get("clicks"), "source": "Google Ads"},
            {
                "id": "landing_session",
                "label": "Landing session",
                "US": ga4_totals.get("sessions"),
                "AU": au_ga4.get("sessions"),
                "source": "GA4",
            },
            {
                "id": "engaged",
                "label": "Engaged visitor",
                "US": ga4_totals.get("engaged_sessions"),
                "AU": au_ga4.get("engaged_sessions"),
                "source": "GA4",
            },
            {
                "id": "form_start",
                "label": "Form start",
                "US": form_starts,
                "AU": None,
                "source": "GA4",
            },
            {
                "id": "primary_cta",
                "label": "Phone click / form submit",
                "US": (phone_clicks or 0) + (form_submits or 0),
                "AU": None,
                "source": "GA4",
            },
            {
                "id": "sales_ops_enquiry",
                "label": "Sales-ops employer enquiry",
                "US": early_us.get("enquiries"),
                "AU": early_au.get("enquiries"),
                "source": "Sales ops",
            },
            {
                "id": "crm_enquiry",
                "label": "Zoho Sales Enquiry (all sources)",
                "US": None,
                "AU": None,
                "all": zoho_block["last_90d"]["sales_enquiries"],
                "source": "Zoho",
                "confidence": "unattributed_to_vc_star",
            },
            {
                "id": "job_order",
                "label": "Job order (all sources 90d)",
                "all": zoho_block["last_90d"]["job_orders"],
                "source": "Zoho",
                "confidence": "unattributed_to_vc_star",
            },
            {
                "id": "placement",
                "label": "Placement (all sources 90d)",
                "all": zoho_block["last_90d"]["placements"],
                "source": "Zoho",
                "confidence": "unattributed_to_vc_star",
            },
        ],
        "filters_note": "Per-campaign/query/device funnel join not yet available — needs scheduled gclid join store",
    }

    discrepancies = [
        {
            "id": "ads_clicks_vs_ga4_sessions",
            "left": {"label": "US Ads Stage-1 clicks (7d)", "value": us_stage.get("clicks"), "source": "Google Ads"},
            "right": {"label": "US GA4 sessions (7d)", "value": ga4_totals.get("sessions"), "source": "GA4"},
            "note": "Not 1:1 — multi-session, consent, Direct bleed, AU on separate property",
        },
        {
            "id": "ads_conv_vs_ga4_conv",
            "left": {"label": "VC_* Ads conversions", "value": 0, "source": "Google Ads"},
            "right": {"label": "GA4 conversions metric", "value": ga4_totals.get("conversions"), "source": "GA4"},
            "note": "Both near zero on Maximize Clicks — expected until pipe proven",
        },
        {
            "id": "ga4_leads_vs_zoho",
            "left": {"label": "GA4 form_submit (top events)", "value": form_submits, "source": "GA4"},
            "right": {
                "label": "Zoho Sales Enquiries 90d (all sources)",
                "value": zoho_block["last_90d"]["sales_enquiries"],
                "source": "Zoho",
            },
            "note": ".app not writing Zoho; CRM still WP/Zapier/humans",
        },
        {
            "id": "zoho_enquiry_vs_job_order",
            "left": {"label": "Sales Enquiries 90d", "value": 647, "source": "Zoho"},
            "right": {"label": "Job Orders 90d", "value": zoho_block["last_90d"]["job_orders"], "source": "Zoho"},
            "note": "Enquiry status “JO Submitted” ≠ Job Orders object",
        },
        {
            "id": "zapier_vs_crm_job_orders",
            "left": {"label": "Ads Zapier JO conversions US+AU", "value": 103, "source": "Google Ads"},
            "right": {"label": "CRM Job Orders all-time", "value": 782, "source": "Zoho"},
            "note": "Object mismatch — never use Zapier count as census",
        },
    ]

    ux_interference = {
        "status": "insufficient_volume",
        "label": "Observational only — not causal",
        "note": (
            "Need session-scoped popup_impression / chat_widget_impression flags in GA4 "
            "before comparing primary CTA rates. New events wired on site; await volume."
        ),
        "planned_compare": [
            "sessions with popup shown vs without",
            "primary CTA rate",
            "form completion rate",
            "phone click rate",
            "engagement",
        ],
    }

    us_clicks = int(us_stage.get("clicks") or 0)
    au_clicks = int(au_stage.get("clicks") or 0)
    alerts = build_alerts(
        us_clicks=us_clicks,
        au_clicks=au_clicks,
        form_starts=form_starts,
        form_submits=form_submits,
        phone_clicks=phone_clicks,
        mobile_pct=float(mobile_pct) if mobile_pct is not None else None,
        ads_conv_us=0,
        ga4_conv=ga4_totals.get("conversions"),
        zoho_app_write=False,
        search_terms=search_terms,
    )
    recommendations = build_recommendations(campaigns, alerts)

    sync = {
        "google_ads": sync_status(exec_snap.get("generated_at_utc")),
        "ga4": sync_status(ga4.get("generated_at_utc")),
        "impression_share": sync_status(is_snap.get("generated_at_utc")),
        "daily_watch": sync_status(daily.get("generated_at_utc")),
        "zoho": {
            "status": "delayed",
            "last_success_utc": "2026-08-13",
            "age_hours": None,
            "note": "Census + attribution recovery pack — not a live scheduled sync into xray/data",
        },
    }

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "read_only": True,
        "purpose": "Reconcile Google Ads → GA4 → website → Zoho without mutating campaigns",
        "clean_traffic_since": CLEAN_TRAFFIC_SINCE,
        "date_windows_note": "Never blend windows without labeling. USD and AUD stay separate.",
        "sync": sync,
        "spend": build_spend_windows(exec_snap),
        "campaigns": campaigns,
        "website": website,
        "sales_ops": sales_ops,
        "zoho": zoho_block,
        "conversion_tiers": tiers,
        "funnel": funnel,
        "search_terms": search_terms,
        "discrepancies": discrepancies,
        "alerts": alerts,
        "recommendations": recommendations,
        "ux_interference": ux_interference,
        "attribution_model": {
            "match_priority": [
                "gclid",
                "campaign_query_ids",
                "email",
                "normalized_phone",
                "timestamp_proximity",
                "landing_page_session",
            ],
            "confidence_labels": ["attributed", "likely_attributed", "unattributed", "ambiguous"],
            "live_join_status": "not_built",
            "live_join_note": (
                "Deterministic gclid join store not yet scheduled. "
                "Historical hash join: 18/18 JO UTM_Gclid matched enquiry utm_gclid (Aug 13)."
            ),
            "field_truth": {
                "zoho_enquiry_gclid": "utm_gclid",
                "zoho_job_order_gclid": "UTM_Gclid",
                "vision_default_was": "$gclid + VC_Submission_ID (missing in live CRM)",
            },
        },
        "recovery_audit_as_of": recovery.get("as_of") or recovery.get("generated_at_utc"),
        "inputs": {
            "executive_snapshot": bool(exec_snap),
            "ga4_snapshot": bool(ga4),
            "impression_share": bool(is_snap),
            "daily_watch": bool(daily),
            "attribution_numbers_csv": NUMBERS_CSV.exists(),
        },
        "honesty": (
            "This board explains the account. It does not invent paid→CRM winners. "
            "Secondary widgets are recovery — never Primary."
        ),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"Alerts: {len(alerts)} · Recommendations: {len(recommendations)} · Search terms: {len(search_terms)}")


if __name__ == "__main__":
    main()
