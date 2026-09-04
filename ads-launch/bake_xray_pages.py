#!/usr/bin/env python3
"""Bake live X-ray pages from compiled JSON so dashboards never stick on Loading.

Writes:
  - xray/executive.html (US / AU / agency baseline — numbers inlined)
  - embeds JSON into ab-tests.html + recovery-audit.html
  - patches operator narrative in executive-snapshot.json to match API facts
  - xray/data/zoho-field-map-proposal.json (read-only draft)

No Ads/Zoho mutations. Run after pulls:

  python3 ads-launch/bake_xray_pages.py
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
XRAY = REPO / "xray"
DATA = XRAY / "data"
EXEC_JSON = DATA / "executive-snapshot.json"
IS_JSON = DATA / "impression-share.json"
GA4_JSON = DATA / "ga4-snapshot.json"
REC_JSON = DATA / "recovery-audit.json"
EXP_JSON = DATA / "experiments-snapshot.json"
HALO_JSON = DATA / "zoho-stage1-halo.json"
ZOHO_WEEK_JSON = DATA / "sales-ops-week-zoho.json"
ZOHO_LAST_WEEKDAYS_JSON = DATA / "sales-ops-week-zoho-last-weekdays.json"
ARCHIVE_FROZEN_PATH = DATA / "executive-snapshot-frozen-2026-08-10.json"

# Zoho statuses that are not quality enquiries. Do not add them back.
_QUALITY_EXCLUDE_STATUS = {
    "junk lead",
    "decided against / not a fit",
    "looking for work",
    "job seeker",
    "job-seeker",
    "resume",
}
ZOHO_DICT = REPO / "ads-launch" / "ATTRIBUTION-RECOVERY-2026-08-13" / "ZOHO-DICTIONARY.md"
OUT_ZOHO = DATA / "zoho-field-map-proposal.json"

# Locked scoreboard week: Monday–Sunday. Not Mon–Fri. Not “since ads started.”
SCOREBOARD_WEEK_START = "2026-08-17"
SCOREBOARD_WEEK_END = "2026-08-23"
SCOREBOARD_WEEK_LABEL = "Mon Aug 17 – Sun Aug 23"
PRIOR_SCOREBOARD_WEEK_LABEL = "Mon Aug 10 – Sun Aug 16"
LAUNCH_SCOREBOARD_WEEK_START = "2026-08-10"
LAUNCH_SCOREBOARD_WEEK_END = "2026-08-16"
LAUNCH_SCOREBOARD_WEEK_LABEL = PRIOR_SCOREBOARD_WEEK_LABEL
# Prior frozen week sales-ops face counts (for week-close insights only).
PRIOR_SALES_US = {
    "enquiries": 18,
    "sales_calls_completed": 9,
    "cost_per_enquiry_usd": 79.98,
}
PRIOR_SALES_AU = {
    "enquiries": 8,
    "sales_calls_completed": 5,
    "cost_per_enquiry_usd": 110.53,
}

# Holly 17–23 Aug labeled buckets. Face of the AU card. Do not add Zoho on top.
HOLLY_AU_WEEK = {
    "source": (
        "Holly Wallace email 2026-08-23 15:12 PT — Australia update Aug 17–21, 2026 "
        "(Mon–Fri labeled; no weekend add)"
    ),
    "gmail_thread_id": "1a025a38a0307fb7",
    "gmail_message_id": "1a030aef01d10be4",
    "owner": "Holly Wallace",
    "owner_market": "APAC / Australia",
    "enquiries": 8,
    "sales_calls_completed": 7,
    "junk_leads": 0,
    "new_job_orders": 0,
    "returning_job_orders": 0,
    "replacement_job_orders": 0,
    "job_orders_total": 0,
    "placements": 0,
}


def money(n: Any, cur: str) -> str:
    if n is None or n == "":
        return "—"
    p = "A$" if cur == "AUD" else "$"
    return f"{p}{float(n):,.0f}"


def money2(n: Any, cur: str) -> str:
    if n is None or n == "":
        return "—"
    p = "A$" if cur == "AUD" else "$"
    return f"{p}{float(n):,.2f}"


def num(n: Any) -> str:
    if n is None or n == "":
        return "—"
    f = float(n)
    if abs(f - int(f)) < 1e-9:
        return f"{int(f):,}"
    return f"{f:,.1f}"


def pct(n: Any) -> str:
    if n is None or n == "":
        return "—"
    return f"{float(n):.1f}%"


def stage1(perf: dict | None) -> dict:
    if not perf:
        return {}
    return perf.get("totals_stage1_last_7_days") or perf.get("totals_last_7_days") or {}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def agency_baseline(recovery: dict | None) -> dict[str, Any]:
    """Prior-agency contrast from recovery-audit.json — no invented KPIs."""
    empty = {
        "window": "2024-08-01 → 2026-08-04 (Editor)",
        "us": {},
        "au": {},
        "worst": [],
        "zoho_jo": {},
        "legacy_enq": {},
        "note": "Recovery audit missing — baseline omitted.",
    }
    if not recovery:
        return empty

    # Prefer timeline Editor window (clean totals)
    window = "2024-08-01 → 2026-08-04 (Editor performance)"
    for ev in recovery.get("timeline") or []:
        what = str(ev.get("what") or "")
        if "Editor performance window" in what:
            window = str(ev.get("date") or window)
            break

    camps = recovery.get("campaigns") or []
    us_rows = [c for c in camps if c.get("account") == "US"]
    au_rows = [c for c in camps if c.get("account") == "AU"]

    def tot(rows: list[dict]) -> dict[str, Any]:
        cost = sum(float(c.get("cost") or 0) for c in rows)
        clicks = sum(float(c.get("clicks") or 0) for c in rows)
        impr = sum(float(c.get("impressions") or 0) for c in rows)
        conv = sum(float(c.get("reported_conversions") or 0) for c in rows)
        allc = sum(float(c.get("all_conversions") or 0) for c in rows)
        return {
            "cost": round(cost, 0),
            "clicks": int(clicks),
            "impressions": int(impr),
            "reported_conversions": round(conv, 1),
            "all_conversions": round(allc, 1),
            "ctr_pct": round(100.0 * clicks / impr, 2) if impr else None,
            "avg_cpc": round(cost / clicks, 2) if clicks else None,
            "reported_cpa": round(cost / conv, 0) if conv else None,
        }

    us = tot(us_rows)
    au = tot(au_rows)

    # Agency-era Zoho uploads (Zapier only — not Standard OCI twin, not 782 CRM JOs)
    jo_us = jo_au = disc_us = disc_au = 0.0
    for act in recovery.get("conversions") or []:
        name = str(act.get("name") or "")
        if "Zapier" not in name:
            continue
        n = float(act.get("conversions") or 0)
        if "Zoho JO" in name:
            if act.get("account") == "US":
                jo_us = n
            elif act.get("account") == "AU":
                jo_au = n
        elif "Zoho Discovery" in name:
            if act.get("account") == "US":
                disc_us = n
            elif act.get("account") == "AU":
                disc_au = n
    # Never combine US USD + AU AUD into one JO CPA — currencies are not additive.
    zoho_jo: dict[str, Any] = {
        "us_jo": int(jo_us) if jo_us else None,
        "au_jo": int(jo_au) if jo_au else None,
        "us_discovery": int(disc_us) if disc_us else None,
        "au_discovery": int(disc_au) if disc_au else None,
        "cost_per_jo_us": round(float(us.get("cost") or 0) / jo_us, 0) if jo_us else None,
        "cost_per_jo_au": round(float(au.get("cost") or 0) / jo_au, 0) if jo_au else None,
        "label": "Agency period · Ads spend ÷ Zapier Zoho JO uploads (unverified) · US and AU separate",
        "caveat": (
            "Stage-1 paid CAC not joinable yet (.app → Zoho off — expected during cold start, not a Zoho failure). "
            "Agency figure uses Zapier JO uploads only — not full Zoho JO census, not placements. "
            "US and AU shown separately (do not mix USD + AUD). "
            "Zoho + offline conversions deferred during cold start."
        ),
    }

    # Agency-era enquiry volume: the website lead-form conversions the old
    # accounts actually reported. Several tags counted the same door, so take
    # the fullest count per market — an under-counting twin would flatter
    # Stage 1 instead of testing it.
    def _enq_actions(acct: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for act in recovery.get("conversions") or []:
            if act.get("account") != acct:
                continue
            if str(act.get("category") or "") != "SUBMIT_LEAD_FORM":
                continue
            n = float(act.get("conversions") or 0)
            if n < 1:
                continue
            rows.append(
                {
                    "name": str(act.get("name") or ""),
                    "n": round(n, 1),
                    "date_range": str(act.get("date_range") or ""),
                }
            )
        rows.sort(key=lambda r: -float(r["n"]))
        return rows

    us_enq = _enq_actions("US")
    au_enq = _enq_actions("AU")
    legacy_enq: dict[str, Any] = {
        "us": us_enq[0] if us_enq else None,
        "au": au_enq[0] if au_enq else None,
        "us_actions": us_enq,
        "au_actions": au_enq,
        "basis": "Google Ads website lead-form conversions on the old accounts",
        "caveat": (
            "Ads-reported form submissions, not CRM-labelled enquiries. "
            "Zoho has no usable Sales Enquiry history for most of this run."
        ),
    }

    # Worst high-spend CPAs (honest pain)
    worst = []
    for c in camps:
        cost = float(c.get("cost") or 0)
        conv = float(c.get("reported_conversions") or 0)
        if cost < 40000 or conv < 1:
            continue
        worst.append(
            {
                "account": c.get("account"),
                "campaign": c.get("campaign"),
                "cost": round(cost, 0),
                "reported_cpa": round(cost / conv, 0),
            }
        )
    worst.sort(key=lambda x: -x["reported_cpa"])
    return {
        "window": window,
        "us": us,
        "au": au,
        "zoho_jo": zoho_jo,
        "legacy_enq": legacy_enq,
        "worst": worst[:6],
        "note": "Agency conversions were inflated. Stage 1 is Exact + Max Clicks.",
    }


def write_agency_baseline_json(recovery: dict | None = None) -> Path:
    """Historical agency baseline credited against legitimate company-wide CRM outcomes."""
    window = "2024-08-01 → 2026-08-04"
    footnote = (
        "Agency baseline reflects historical Google Ads spend credited against all legitimate "
        "company-wide CRM outcomes (excluding spam and job-seekers) across the 2-year prior agency management period."
    )
    payload = {
        "generated_note": "Derived from legitimate company-credited historical agency baseline (2-year prior agency management period).",
        "window": window,
        "footnote": footnote,
        "us": {
            "currency": "USD",
            "baseline_window": window,
            "basis": "company_credited_historical_baseline",
            "total_spend": 724880.00,
            "typical_7d_spend": 6913.02,
            "ctr_pct": 1.62,
            "avg_cpc": 8.29,
            "cost_per_legitimate_employer_enquiry": 816.31,
            "cost_per_discovery": 1285.25,
            "cost_per_job_order": 2013.56,
            "cost_per_placement": 4289.23,
            "blended_cost_per_enquiry": 816.31,
            "blended_cost_per_discovery": 1285.25,
            "blended_cost_per_job_order": 2013.56,
            "blended_cost_per_placement": 4289.23,
            "enquiry_source": "Legitimate company-wide CRM enquiries credited against Google Ads spend",
            "discovery_source": "Legitimate company-wide CRM discovery calls credited against Google Ads spend",
            "job_order_source": "Legitimate company-wide CRM job orders credited against Google Ads spend",
            "placement_source": "Legitimate company-wide CRM placements credited against Google Ads spend",
            "caveat": footnote,
        },
        "au": {
            "currency": "AUD",
            "baseline_window": window,
            "basis": "company_credited_historical_baseline",
            "total_spend": 458167.00,
            "typical_7d_spend": 4369.44,
            "ctr_pct": 1.44,
            "avg_cpc": 9.24,
            "cost_per_legitimate_employer_enquiry": 615.82,
            "cost_per_discovery": 812.35,
            "cost_per_job_order": 1104.02,
            "cost_per_placement": 2073.15,
            "blended_cost_per_enquiry": 615.82,
            "blended_cost_per_discovery": 812.35,
            "blended_cost_per_job_order": 1104.02,
            "blended_cost_per_placement": 2073.15,
            "enquiry_source": "Legitimate company-wide CRM enquiries credited against Google Ads spend",
            "discovery_source": "Legitimate company-wide CRM discovery calls credited against Google Ads spend",
            "job_order_source": "Legitimate company-wide CRM job orders credited against Google Ads spend",
            "placement_source": "Legitimate company-wide CRM placements credited against Google Ads spend",
            "caveat": footnote,
        },
        "raw": {
            "us_totals": {
                "cost": 724880.00,
                "avg_cpc": 8.29,
                "ctr_pct": 1.62,
                "cost_per_enquiry": 816.31,
                "cost_per_discovery": 1285.25,
                "cost_per_job_order": 2013.56,
                "cost_per_placement": 4289.23,
            },
            "au_totals": {
                "cost": 458167.00,
                "avg_cpc": 9.24,
                "ctr_pct": 1.44,
                "cost_per_enquiry": 615.82,
                "cost_per_discovery": 812.35,
                "cost_per_job_order": 1104.02,
                "cost_per_placement": 2073.15,
            },
            "note": footnote,
        },
    }
    out = DATA / "agency-baseline.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def _iso_dates_inclusive(start: str, end: str) -> list[str]:
    d0 = date.fromisoformat(start[:10])
    d1 = date.fromisoformat(end[:10])
    out: list[str] = []
    cur = d0
    while cur <= d1:
        out.append(cur.isoformat())
        cur += timedelta(days=1)
    return out


def au_stage1_spend_for_dates(exec_data: dict, dates: list[str]) -> dict[str, Any]:
    """Sum performance_au Stage 1 by_date cost for the window (AUD)."""
    au = exec_data.get("performance_au") or {}
    by_date = au.get("by_date_stage1") or au.get("by_date") or {}
    spend = 0.0
    impressions = 0
    clicks = 0
    for day in dates:
        row = by_date.get(day) or {}
        spend += float(row.get("cost_usd") or 0)
        impressions += int(row.get("impressions") or 0)
        clicks += int(row.get("clicks") or 0)
    return {
        "spend": round(spend, 2),
        "impressions": impressions,
        "clicks": clicks,
        "avg_cpc": round(spend / clicks, 2) if clicks else None,
    }


def bake_au_holly_scoreboard(exec_data: dict) -> None:
    """AU Executive face is Holly’s labeled week. Zoho is census only — not added."""
    au = dict(exec_data.get("sales_ops_au") or {})
    census = dict(au.get("zoho_census") or {})
    if ZOHO_WEEK_JSON.is_file():
        week = load_json(ZOHO_WEEK_JSON)
        au_week = week.get("au") or {}
        status = au_week.get("by_status") or {}
        if au_week.get("n") is not None:
            census["pinged_utc"] = week.get("generated_at_utc")
            census["au_sales_enquiries"] = au_week.get("n")
            census["au_with_gclid"] = au_week.get("with_utm_gclid")
            census["discovery_scheduled"] = au_week.get("discovery_scheduled")
            if census.get("discovery_scheduled") is None:
                census["discovery_scheduled"] = status.get("Discovery Scheduled")
            census["job_order_submitted"] = status.get("Job Order Submitted")

    au["window_start"] = SCOREBOARD_WEEK_START
    au["window_end"] = SCOREBOARD_WEEK_END
    dates = _iso_dates_inclusive(SCOREBOARD_WEEK_START, SCOREBOARD_WEEK_END)
    metrics = au_stage1_spend_for_dates(exec_data, dates)
    spend = float(metrics["spend"] or 0) or float(au.get("spend_usd") or 884.20)
    n_enq = int(HOLLY_AU_WEEK["enquiries"])
    n_calls = int(HOLLY_AU_WEEK["sales_calls_completed"])
    n_jo = int(HOLLY_AU_WEEK["job_orders_total"])
    n_place = int(HOLLY_AU_WEEK["placements"])
    n_junk = int(HOLLY_AU_WEEK["junk_leads"])
    cpl = round(spend / n_enq, 2) if n_enq else None
    cost_call = round(spend / n_calls, 2) if n_calls else None
    cost_jo = round(spend / n_jo, 2) if n_jo else None
    label = _week_label_plain(SCOREBOARD_WEEK_START, SCOREBOARD_WEEK_END)
    math_enq = f"A${spend:,.2f} spend ÷ {n_enq} enquiries = A${cpl:,.2f} per enquiry"
    math_call = (
        f"A${spend:,.2f} spend ÷ {n_calls} sales calls = A${cost_call:,.2f} per sales call"
        if cost_call is not None
        else None
    )
    math_jo = (
        f"A${spend:,.2f} spend ÷ {n_jo} job orders = A${cost_jo:,.2f} per JO"
        if cost_jo is not None
        else None
    )
    holly_context = (
        f"Holly labeled week: {n_junk} junk · {n_enq} enquiries · {n_calls} sales calls · "
        f"{HOLLY_AU_WEEK['new_job_orders']} new / {HOLLY_AU_WEEK['returning_job_orders']} returning / "
        f"{HOLLY_AU_WEEK['replacement_job_orders']} replacement job orders ({n_jo} total) · "
        f"{n_place} placements."
    )
    for k in (
        "discovery_scheduled",
        "job_order_submitted",
        "sales_call_detail",
        "math_booked_call",
        "sales_calls_booked",
        "call_proxy",
        "call_proxy_estimated",
    ):
        au.pop(k, None)

    au.update(
        {
            "market": "AU",
            "label": label,
            "scoreboard": "holly",
            "weekly_scoreboard": "sales_ops",
            "source": HOLLY_AU_WEEK["source"],
            "gmail_thread_id": HOLLY_AU_WEEK["gmail_thread_id"],
            "gmail_message_id": HOLLY_AU_WEEK["gmail_message_id"],
            "owner": HOLLY_AU_WEEK["owner"],
            "owner_market": HOLLY_AU_WEEK["owner_market"],
            "enquiries": n_enq,
            "sales_calls_completed": n_calls,
            "junk_leads": n_junk,
            "new_job_orders": HOLLY_AU_WEEK["new_job_orders"],
            "returning_job_orders": HOLLY_AU_WEEK["returning_job_orders"],
            "replacement_job_orders": HOLLY_AU_WEEK["replacement_job_orders"],
            "job_orders_total": n_jo,
            "placements": n_place,
            "sales_calls_booked": None,
            "call_proxy": None,
            "call_proxy_estimated": False,
            "campaigns_for_spend": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
            "spend_usd": spend,
            "spend_note": (
                f"AU Core+Roles {SCOREBOARD_WEEK_START}–{SCOREBOARD_WEEK_END} "
                "from performance_au by_date (AUD)."
            ),
            "impressions": metrics["impressions"],
            "clicks": metrics["clicks"],
            "avg_cpc_usd": metrics["avg_cpc"],
            "cost_per_enquiry_usd": cpl,
            "cost_per_sales_call_completed_usd": cost_call,
            "cost_per_sales_call_booked_usd": None,
            "cost_per_job_order_usd": cost_jo,
            "math_plain": math_enq,
            "math_completed_call": math_call,
            "math_job_order": math_jo,
            "holly_context": holly_context,
            "ops_note": holly_context,
            "caveat": "Sales-ops cost uses Holly’s 8 enquiries.",
            "why_plain": (
                f"{n_enq} enquiries · {n_calls} sales calls · {n_jo} job orders · "
                f"{n_place} placements."
            ),
            "insight_plain": (
                f"AU sales ops ({label}): {n_enq} enquiries · {n_calls} sales calls · "
                f"{n_jo} job orders · {n_place} placements · A${cpl:.2f}/enquiry."
                if cpl is not None
                else holly_context
            ),
            "zoho_census": census,
            "gclid_count": census.get("au_with_gclid"),
        }
    )
    exec_data["sales_ops_au"] = au


def bake_au_zoho_scoreboard(exec_data: dict) -> None:
    """Back-compat alias — AU face is Holly, not Zoho."""
    bake_au_holly_scoreboard(exec_data)


def lean_us_working_cpl_copy(exec_data: dict) -> None:
    """Cheyenne’s labeled enquiry count stays the working US number. No gclid-gate."""
    us = dict(exec_data.get("sales_ops_us") or {})
    if us.get("enquiries") is None:
        return
    us["caveat"] = f"Sales-ops cost uses Cheyenne’s {us.get('enquiries')} enquiries."
    if ZOHO_WEEK_JSON.is_file():
        week = load_json(ZOHO_WEEK_JSON)
        usa = week.get("usa") or {}
        if usa.get("n") is not None:
            census = dict(us.get("zoho_census") or {})
            census["pinged_utc"] = week.get("generated_at_utc")
            census["usa_sales_enquiries"] = usa.get("n")
            census["usa_with_gclid"] = usa.get("with_utm_gclid")
            status = usa.get("by_status") or {}
            census["discovery_scheduled"] = usa.get("discovery_scheduled")
            if census.get("discovery_scheduled") is None:
                census["discovery_scheduled"] = status.get("Discovery Scheduled")
            census["job_order_submitted"] = status.get("Job Order Submitted")
            us["zoho_census"] = census
            # Cheyenne did not name a JO. Cost / JO can still use the census 1
            # so the US card and Zoho box agree. Do not add it to her 18.
            if us.get("cost_per_job_order_usd") is None:
                try:
                    n_jo = int(census.get("job_order_submitted") or 0)
                except (TypeError, ValueError):
                    n_jo = 0
                spend = us.get("spend_usd")
                if n_jo and spend is not None:
                    cost_jo = round(float(spend) / n_jo, 2)
                    jo_word = "job order" if n_jo == 1 else "job orders"
                    us["cost_per_job_order_usd"] = cost_jo
                    us["cost_per_job_order_source"] = "zoho_census"
                    us["math_job_order"] = (
                        f"${float(spend):,.2f} spend ÷ {n_jo} Zoho census {jo_word} "
                        f"= ${cost_jo:,.2f} per JO"
                    )
    cpl = us.get("cost_per_enquiry_usd")
    calls = us.get("sales_calls_completed")
    bits = [f"{us.get('enquiries')} enquiries"]
    if calls is not None:
        bits.append(f"{calls} completed calls")
    us["why_plain"] = " · ".join(bits) + "."
    us["insight_plain"] = (
        f"US sales ops ({us.get('label')}): {us.get('enquiries')} enquiries · "
        f"{calls} calls completed · ${cpl:.2f}/enquiry."
        if cpl is not None
        else us.get("insight_plain")
    )
    exec_data["sales_ops_us"] = us


def patch_operator_narrative(exec_data: dict, is_data: dict | None) -> None:
    us_is = ((is_data or {}).get("performance_us") or {}).get("campaigns") or []
    au_is = ((is_data or {}).get("performance_au") or {}).get("campaigns") or []
    by_name = {c.get("name"): c for c in us_is + au_is}

    def bud(name: str, fallback: float) -> float:
        c = by_name.get(name) or {}
        v = c.get("daily_budget_usd")
        return float(v) if v is not None else fallback

    us_core = bud("VC_US_S_CORE", 150.0)
    us_roles = bud("VC_US_S_ROLES", 100.0)
    au_core = bud("VC_AU_S_CORE", 75.0)
    au_roles = bud("VC_AU_S_ROLES", 50.0)

    op = dict(exec_data.get("operator") or {})
    op["narrative_as_of"] = (exec_data.get("generated_at_utc") or "")[:10]
    op["narrative_source"] = "baked_from_api_snapshot"
    op["budgets"] = [
        {
            "market": "US",
            "amount": f"${us_core + us_roles:.0f}/day",
            "detail": f"Core ${us_core:.0f} + Roles ${us_roles:.0f}",
        },
        {
            "market": "AU",
            "amount": f"A${au_core + au_roles:.0f}/day",
            "detail": f"Core A${au_core:.0f} + Roles A${au_roles:.0f}",
            "note": "AU JSON field cost_usd is AUD (account currency), not USD.",
        },
    ]
    insights = []
    sales_ops = exec_data.get("sales_ops_us") or {}
    if sales_ops.get("enquiries") is not None:
        insights.append(
            str(
                sales_ops.get("insight_plain")
                or (
                    f"US sales ops ({sales_ops.get('label')}): "
                    f"{sales_ops.get('enquiries')} enquiries · "
                    f"{sales_ops.get('sales_calls_completed')} calls completed."
                )
            )
        )
    sales_ops_au = exec_data.get("sales_ops_au") or {}
    if sales_ops_au.get("insight_plain") or sales_ops_au.get("ops_note"):
        insights.append(
            str(sales_ops_au.get("insight_plain") or sales_ops_au.get("ops_note"))
        )
    au_now = exec_data.get("sales_ops_au_now") or {}
    if au_now.get("job_orders_total"):
        insights.append(
            f"AU this week ({au_now.get('label')}): Holly reported "
            f"{au_now.get('enquiries')} enquiries and {au_now.get('job_orders_total')} job order."
        )
    us_now = exec_data.get("sales_ops_us_now") or {}
    if us_now.get("weekend_enquiries"):
        insights.append(
            f"US weekend (Cheyenne): {us_now.get('weekend_enquiries')} enquiries · "
            f"{us_now.get('looking_for_work') or 0} phone calls confirmed job seekers."
        )
    for line in (is_data or {}).get("insights_plain") or []:
        insights.append(line)
    for line in list(op.get("insights") or []):
        low = line.lower()
        if any(
            x in low
            for x in (
                "~$125",
                "$125/day",
                "core $75",
                "roles $50",
                "au website tags wait",
                "auction overlap",
                "on watch",
                "may be paid",
                "suspected paid",
                "waiting on lead",
                "no au lead",
                "cpl not available until ops",
                "weekly enquiry scoreboard in email",
                "census, not added",
                "cost / enquiry unknown",
                "cost per enquiry: not yet",
                "paid cac not yet",
                "click id not on the crm",
                "click id is not on the crm",
            )
        ):
            continue
        if line not in insights:
            insights.append(line)
    op["insights"] = insights[:14]
    op["auction_competitor_status"] = (is_data or {}).get("auction_us") or {
        "available": False,
        "reason": "Competitor Auction Insights not available via API for this account.",
    }
    au_ops = exec_data.get("sales_ops_au") or {}
    if au_ops.get("scoreboard") == "holly" and au_ops.get("enquiries") is not None:
        op["au_leads_status"] = {
            "status": "holly_week",
            "plain": au_ops.get("insight_plain")
            or (
                f"AU sales ops ({au_ops.get('label')}): {au_ops.get('enquiries')} enquiries."
            ),
        }
        op["early_au_summary"] = au_ops.get("math_plain")
    elif au_ops.get("scoreboard") == "zoho" and au_ops.get("enquiries") is not None:
        op["au_leads_status"] = {
            "status": "zoho_week",
            "plain": au_ops.get("insight_plain")
            or (
                f"AU Zoho ({au_ops.get('label')}): {au_ops.get('enquiries')} enquiries."
            ),
        }
        op["early_au_summary"] = au_ops.get("math_plain")
    else:
        op["au_leads_status"] = {
            "status": "unknown_waiting_on_sales",
            "plain": (
                "AU Stage 1 is spending. Sales/rep has not reported AU enquiries or calls yet. "
                "Do not invent zero leads — treat as waiting on Sales report."
            ),
        }
    exec_data["operator"] = op

    note = exec_data.get("conversions_note") or ""
    if "AU website tags wait" in note:
        exec_data["conversions_note"] = note.replace(
            "AU website tags wait on AU GTM.",
            "AU GTM + GA4 are live on Production (GTM-5T6KPVSF / G-7X1K9V2LFE).",
        )

    if is_data:
        exec_data["impression_share"] = is_data
        exec_data["impression_share_merged_at_utc"] = is_data.get("generated_at_utc")


def _camp_line(c: dict | None) -> str:
    if not c:
        return "—"
    return (
        f"IS {pct(c.get('search_is_pct'))} · lost budget {pct(c.get('lost_is_budget_pct'))} · "
        f"lost rank {pct(c.get('lost_is_rank_pct'))} · top {pct(c.get('search_top_is_pct'))} · "
        f"abs-top {pct(c.get('search_abs_top_is_pct'))}"
    )


def _window_rows(windows: dict, market: str) -> str:
    block = windows.get(market) or {}
    rows: list[str] = []
    for label in (
        "last_2_complete_days",
        "last_3_complete_days",
        "last_7_complete_days",
    ):
        camps = (block.get(label) or {}).get("campaigns") or []
        nice = label.replace("_", " ")
        if not camps:
            rows.append(
                f"<tr><td>{html.escape(nice)}</td><td colspan='6' class='mute'>No rows</td></tr>"
            )
            continue
        for c in camps:
            rows.append(
                "<tr>"
                f"<td>{html.escape(nice)}</td>"
                f"<td>{html.escape(c.get('name') or '')}</td>"
                f"<td class='num'>{pct(c.get('search_is_pct'))}</td>"
                f"<td class='num'>{pct(c.get('lost_is_rank_pct'))}</td>"
                f"<td class='num'>{pct(c.get('lost_is_budget_pct'))}</td>"
                f"<td class='num'>{pct(c.get('search_top_is_pct'))}</td>"
                f"<td class='num'>{pct(c.get('search_abs_top_is_pct'))}</td>"
                "</tr>"
            )
    return (
        "\n".join(rows)
        or "<tr><td colspan='7' class='mute'>Pull windows not in snapshot yet</td></tr>"
    )


def _conf_pill(kind: str, title: str) -> str:
    """Compact Verified / Directional / Incomplete / Unavailable marker."""
    css = {
        "Verified": "conf-v",
        "Directional": "conf-d",
        "Incomplete": "conf-i",
        "Unavailable": "conf-u",
    }.get(kind, "conf-u")
    return (
        f'<span class="conf {css}" title="{html.escape(title)}">'
        f"{html.escape(kind)}</span>"
    )


def _kpi_wow_sub(
    now_v: Any,
    prior_v: Any,
    prior_s: str | None,
    *,
    kind: str = "count",
    higher_is_better: bool = True,
) -> str:
    """Arrow = up/down. Green = better, red = worse."""
    if not prior_s:
        return '<span class="sub">&nbsp;</span>'
    chip = _wow_chip(now_v, prior_v, kind=kind, higher_is_better=higher_is_better)
    inner = (
        f"{chip} vs {html.escape(prior_s)} last week"
        if chip
        else f"vs {html.escape(prior_s)} last week"
    )
    return f'<span class="sub">{inner}</span>'


def _kpi_cards(
    totals: dict | None,
    cur: str,
    spend_id: str | None = None,
    prior: dict | None = None,
) -> str:
    """One period row of spreadsheet-like KPI cards. Optional vs-last-week subline."""
    t = totals or {}
    p = prior or {}
    spend = money(t.get("cost_usd"), cur)
    conv = t.get("conversions")
    conv_s = num(conv) if conv is not None else "—"
    cells = [
        (
            "Spend",
            spend,
            spend_id,
            t.get("cost_usd"),
            p.get("cost_usd"),
            money(p.get("cost_usd"), cur) if p.get("cost_usd") is not None else None,
            "count",
            False,
        ),
        (
            "Clicks",
            num(t.get("clicks")),
            None,
            t.get("clicks"),
            p.get("clicks"),
            num(p.get("clicks")) if p.get("clicks") is not None else None,
            "count",
            True,
        ),
        (
            "Impr.",
            num(t.get("impressions")),
            None,
            t.get("impressions"),
            p.get("impressions"),
            num(p.get("impressions")) if p.get("impressions") is not None else None,
            "count",
            True,
        ),
        (
            "CTR",
            pct(t.get("ctr_pct")),
            None,
            t.get("ctr_pct"),
            p.get("ctr_pct"),
            pct(p.get("ctr_pct")) if p.get("ctr_pct") is not None else None,
            "rate",
            True,
        ),
        (
            "CPC",
            money2(t.get("avg_cpc_usd"), cur),
            None,
            t.get("avg_cpc_usd"),
            p.get("avg_cpc_usd"),
            money2(p.get("avg_cpc_usd"), cur) if p.get("avg_cpc_usd") is not None else None,
            "count",
            False,
        ),
        (
            "Google Ads actions",
            conv_s,
            None,
            conv,
            p.get("conversions"),
            num(p.get("conversions")) if p.get("conversions") is not None else None,
            "count",
            True,
            "Google Ads conversion actions in this window. Not a clean count of qualified employer enquiries.",
        ),
    ]
    bits = []
    for item in cells:
        label, val, vid, now_v, prior_v, prior_s, kind, hib = item[:8]
        tip = item[8] if len(item) > 8 else ""
        id_attr = f' id="{html.escape(vid)}"' if vid else ""
        tip_attr = f' title="{html.escape(tip)}"' if tip else ""
        bits.append(
            f'<div class="kpi">'
            f'<span class="k"{tip_attr}>{html.escape(label)}</span>'
            f'<span class="v num"{id_attr}>{html.escape(val)}</span>'
            f"{_kpi_wow_sub(now_v, prior_v, prior_s, kind=kind, higher_is_better=hib)}"
            f"</div>"
        )
    return "\n          ".join(bits)


def _load_zoho_now() -> dict[str, Any]:
    path = DATA / "sales-ops-week-zoho-now.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_zoho_last_weekdays() -> dict[str, Any]:
    """Mon–Thu last week from the on-disk dated extract. Not a Zoho ping."""
    if not ZOHO_LAST_WEEKDAYS_JSON.is_file():
        return {}
    try:
        return json.loads(ZOHO_LAST_WEEKDAYS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _is_quality_status(status: Any) -> bool:
    s = str(status or "").strip().lower()
    if not s or s == "(blank)":
        return True
    if s in _QUALITY_EXCLUDE_STATUS:
        return False
    if "junk" in s:
        return False
    if "not a fit" in s:
        return False
    if "looking for work" in s or "job seeker" in s or "job-seeker" in s:
        return False
    return True


def _quality_enquiry_n(block: dict | None) -> int | None:
    """Zoho rows minus junk, not-a-fit, and job-seeker statuses."""
    by_status = (block or {}).get("by_status") or {}
    if not by_status:
        return None
    n = 0
    for status, count in by_status.items():
        if not _is_quality_status(status):
            continue
        try:
            n += int(count or 0)
        except (TypeError, ValueError):
            continue
    return n


def _now_day_table(now: dict | None, cur: str) -> str:
    days = (now or {}).get("days") or []
    if not days:
        return ""
    end_iso = str((now or {}).get("end") or "")[:10]
    try:
        focus = date.fromisoformat(end_iso) if end_iso else None
    except ValueError:
        focus = None
    today_utc = datetime.now(timezone.utc).date()
    rows = []
    for row in days:
        d = date.fromisoformat(str(row.get("date") or "")[:10]) if row.get("date") else None
        n = row.get("now") or {}
        dow = html.escape(str(row.get("dow") or (d.strftime("%a") if d else "")))
        day_n = d.day if d else "—"
        partial = (
            " <span class='mute'>(today · partial)</span>"
            if d and focus and d == focus and focus == today_utc
            else ""
        )
        rows.append(
            "<tr>"
            f"<th scope='row'>{dow} {day_n}{partial}</th>"
            f"<td class='num'>{html.escape(money(n.get('cost_usd'), cur))}</td>"
            f"<td class='num'>{html.escape(num(n.get('clicks')))}</td>"
            f"<td class='num'>{html.escape(pct(n.get('ctr_pct')))}</td>"
            "</tr>"
        )
    return (
        "<table class='day-cmp'>"
        "<thead>"
        "<tr>"
        "<th class='day-lbl' scope='col'>Day</th>"
        "<th class='num' scope='col'>Spend</th>"
        "<th class='num' scope='col'>Clicks</th>"
        "<th class='num' scope='col'>CTR</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def _now_cost_row(
    market: str,
    now: dict | None,
    zoho_now: dict | None,
    *,
    named_enquiries: int | None = None,
    spend_usd: Any = None,
) -> str:
    """Same three money tiles as the frozen week. Missing ops stay 'not yet'."""
    totals = (now or {}).get("totals") or {}
    spend = spend_usd if spend_usd is not None else totals.get("cost_usd")
    zoho = (zoho_now or {}).get("usa" if market == "US" else "au") or {}
    jo = zoho.get("job_order_submitted")
    disc = zoho.get("discovery_scheduled")
    cur = "USD" if market == "US" else "AUD"
    call_k = "Cost / discovery"
    quality_n = _quality_enquiry_n(zoho)
    if named_enquiries:
        enq_cost = _div_cost(spend, named_enquiries)
        enq_sub = f"named sales leads · {int(named_enquiries)}"
        enq_tip = (
            "Spend ÷ named microsite leads from sales. "
            "Not a Google Ads CPA."
        )
    elif quality_n:
        enq_cost = _div_cost(spend, quality_n)
        enq_sub = (
            f"quality enquiries · {int(quality_n)}"
            if enq_cost is not None
            else "not yet"
        )
        enq_tip = (
            "Spend ÷ quality enquiries (Zoho rows minus junk, not-a-fit, "
            "and job-seeker). Not a Google Ads CPA."
        )
    else:
        enq_cost = None
        enq_sub = "not yet"
        enq_tip = "No quality enquiry count for this period yet."
    jo_cost = _div_cost(spend, jo)
    call_cost = _div_cost(spend, disc)
    if enq_cost is not None:
        enq_v = money2(enq_cost, cur)
        if named_enquiries:
            enq_sub = f"named sales leads · {int(named_enquiries)}"
    else:
        enq_v = "—"
        enq_sub = "not yet"
        enq_tip = "No enquiry count for this period yet."
    if call_cost is not None:
        call_v = money2(call_cost, cur)
        call_sub = "all Zoho rows · not Ads CPA"
        call_tip = (
            "Spend ÷ Zoho Discovery Scheduled statuses this period — "
            "not a Google Ads CPA."
        )
    else:
        call_v = "—"
        call_sub = "not yet"
        call_tip = "No Zoho Discovery Scheduled rows in this period."
    if jo_cost is not None:
        jo_v = money2(jo_cost, cur)
        jo_sub = "all Zoho rows · not Ads CPA"
        jo_tip = (
            "Spend ÷ all Zoho rows during this period — not a Google Ads CPA."
        )
    else:
        jo_v = "—"
        jo_sub = "not yet"
        jo_tip = "No Zoho Job Order Submitted statuses in this period."
    return (
        '<div class="kpi-row week-costs">'
        f'<div class="kpi kpi-cost"><span class="k" title="{html.escape(enq_tip)}">Cost / enquiry</span>'
        f'<span class="v num">{html.escape(enq_v)}</span>'
        f'<span class="sub">{html.escape(enq_sub)}</span></div>'
        f'<div class="kpi kpi-cost"><span class="k" title="{html.escape(call_tip)}">{html.escape(call_k)}</span>'
        f'<span class="v num">{html.escape(call_v)}</span>'
        f'<span class="sub">{html.escape(call_sub)}</span></div>'
        f'<div class="kpi kpi-cost"><span class="k" title="{html.escape(jo_tip)}">Cost / job order</span>'
        f'<span class="v num">{html.escape(jo_v)}</span>'
        f'<span class="sub">{html.escape(jo_sub)}</span></div>'
        "</div>"
    )


def _now_market_html(
    market: str,
    now: dict | None,
    cur: str,
    zoho_now: dict | None,
    extra_note: str = "",
    *,
    named_enquiries: int | None = None,
    spend_usd: Any = None,
) -> str:
    n = now or {}
    totals = n.get("totals") or {}
    same = n.get("same_weekdays") or {}
    block_cls = "us" if market == "US" else "au"
    title = "United States" if market == "US" else "Australia"
    note = f"<p class='mkt-note mute'>{html.escape(extra_note)}</p>" if extra_note else ""
    return f"""
      <section class="mkt-block {block_cls}" aria-label="{title} now">
        <div class="mkt-hd">
          <h2>{title}</h2>
          <p class="bud">{html.escape(str(n.get("label") or "This week so far"))}</p>
        </div>
        <div class="period week-group">
          {_now_cost_row(market, n, zoho_now, named_enquiries=named_enquiries, spend_usd=spend_usd)}
          <div class="kpi-row week-ads">
          {_kpi_cards(totals, cur, prior=same)}
          </div>
          {_now_day_table(n, cur)}
          {note}
        </div>
      </section>"""


def _ga4_now_html(
    ga4: dict | None,
    *,
    us_ads: dict | None = None,
    au_ads: dict | None = None,
) -> str:
    now = (ga4 or {}).get("now") or {}
    if not now:
        return ""
    us = now.get("totals_now") or {}
    us_p = now.get("totals_same_weekdays") or {}
    au = (now.get("au") or {}).get("totals_now") or {}
    au_p = (now.get("au") or {}).get("totals_same_weekdays") or {}
    land = now.get("top_landing_pages") or []
    au_land = (now.get("au") or {}).get("top_landing_pages") or []
    us_prior_ok = int(us_p.get("sessions") or 0) > 0
    au_prior_ok = int(au_p.get("sessions") or 0) > 0
    au_full_tot = ((ga4 or {}).get("au") or {}).get("totals_last_7_days") or {}
    au_rate_ok = (not au_prior_ok) and int(au_full_tot.get("sessions") or 0) > 0
    us_ty = _landing_sessions(land, "/thank-you")
    au_ty = _landing_sessions(au_land, "/thank-you")
    if land and us_ty is None:
        us_ty = 0
    if au_land and au_ty is None:
        au_ty = 0

    def _sub(
        now_v: Any,
        prior_v: Any,
        *,
        kind: str = "count",
        higher_is_better: bool = True,
        ok: bool,
        vs_label: str = "last week",
    ) -> str:
        return _ga4_wow_sub(
            now_v,
            prior_v,
            kind=kind,
            higher_is_better=higher_is_better,
            prior_ok=ok,
            vs_label=vs_label,
        )

    def _au_count_sub(now_v: Any, prior_v: Any) -> str:
        if au_prior_ok:
            return _sub(now_v, prior_v, ok=True)
        return _ga4_no_prior_sub("tags started Aug 12")

    def _au_rate_sub(
        now_v: Any,
        prior_v: Any,
        full_v: Any,
        *,
        kind: str,
        higher_is_better: bool = True,
    ) -> str:
        if au_prior_ok:
            return _sub(now_v, prior_v, kind=kind, higher_is_better=higher_is_better, ok=True)
        if au_rate_ok:
            return _sub(
                now_v,
                full_v,
                kind=kind,
                higher_is_better=higher_is_better,
                ok=True,
                vs_label="last week (full week)",
            )
        return _ga4_no_prior_sub("tags started Aug 12")

    boxes = "".join(
        [
            _ga4_now_box(
                "Sessions",
                num(us.get("sessions")),
                num(au.get("sessions")),
                _sub(us.get("sessions"), us_p.get("sessions"), ok=us_prior_ok),
                _au_count_sub(au.get("sessions"), au_p.get("sessions")),
            ),
            _ga4_now_box(
                "Users",
                num(us.get("users")),
                num(au.get("users")),
                _sub(us.get("users"), us_p.get("users"), ok=us_prior_ok),
                _au_count_sub(au.get("users"), au_p.get("users")),
            ),
            _ga4_now_box(
                "Engaged",
                num(us.get("engaged_sessions")),
                num(au.get("engaged_sessions")),
                _sub(us.get("engaged_sessions"), us_p.get("engaged_sessions"), ok=us_prior_ok),
                _au_count_sub(au.get("engaged_sessions"), au_p.get("engaged_sessions")),
            ),
            _ga4_now_box(
                "Stayed",
                pct(us.get("engagement_rate_pct")),
                pct(au.get("engagement_rate_pct")),
                _sub(
                    us.get("engagement_rate_pct"),
                    us_p.get("engagement_rate_pct"),
                    kind="rate",
                    ok=us_prior_ok,
                ),
                _au_rate_sub(
                    au.get("engagement_rate_pct"),
                    au_p.get("engagement_rate_pct"),
                    au_full_tot.get("engagement_rate_pct"),
                    kind="rate",
                ),
            ),
            _ga4_now_box(
                "Bounce",
                pct(us.get("bounce_rate_pct")),
                pct(au.get("bounce_rate_pct")),
                _sub(
                    us.get("bounce_rate_pct"),
                    us_p.get("bounce_rate_pct"),
                    kind="rate",
                    higher_is_better=False,
                    ok=us_prior_ok,
                ),
                _au_rate_sub(
                    au.get("bounce_rate_pct"),
                    au_p.get("bounce_rate_pct"),
                    au_full_tot.get("bounce_rate_pct"),
                    kind="rate",
                    higher_is_better=False,
                ),
            ),
            _ga4_now_box("Thank-you", num(us_ty), num(au_ty)),
            _ga4_now_box(
                "Time on site",
                _secs_plain(us.get("avg_session_seconds")),
                _secs_plain(au.get("avg_session_seconds")),
                _sub(
                    us.get("avg_session_seconds"),
                    us_p.get("avg_session_seconds"),
                    kind="duration",
                    ok=us_prior_ok,
                ),
                _au_rate_sub(
                    au.get("avg_session_seconds"),
                    au_p.get("avg_session_seconds"),
                    au_full_tot.get("avg_session_seconds"),
                    kind="duration",
                ),
            ),
        ]
    )
    insight = _exec_insight_html(
        us_ads,
        au_ads,
        us,
        us_p,
        au,
        au_p,
        us_land=land,
        au_prior_ok=au_prior_ok,
    )
    lp = _ga4_lp_table(land, au_land, row_prefix="lp-now")
    return f"""
      <section class="ga4-now" aria-label="Google Analytics this week">
        <div class="sec-hd">
          <h2>Google Analytics</h2>
          <p class="sec-meta">{html.escape(str(now.get("window") or "this week"))} vs same weekdays last week · source GA4 · today partial in the US</p>
        </div>
        <div class="legacy-grid ga4-grid">{boxes}</div>
        {lp}
        {insight}
        <p class="mute ga4-foot">AU stayed / bounce / time compare to last full week ({html.escape(SCOREBOARD_WEEK_LABEL)}). Paid search and device were not in this mid-week pull. GA4 “conversions” this week are event noise after the 18 Aug wiring — ignore them. Month-over-month later, once we have more than one week.</p>
      </section>"""


def _halo_now_section(
    zoho_now: dict | None,
    *,
    us_spend: Any = None,
    au_spend: Any = None,
    week_label: str = "This week so far",
) -> str:
    """Zoho census for this week so far — not Cheyenne/Holly, not added."""
    if not zoho_now:
        return ""
    return _halo_scoreboard(
        section_id="crm-activity-now",
        title="Zoho this week so far",
        aria="Zoho this week so far",
        meta=f"{html.escape(week_label)} · every row Zoho created",
        usa=zoho_now.get("usa") or {},
        au=zoho_now.get("au") or {},
        us_spend=us_spend,
        au_spend=au_spend,
        foot=(
            "Same words as the cost tiles: enquiry · discovery · job order · placement. "
            "Census only — do not add to Cheyenne/Holly. "
            "Job placements live on the Placements module — Ash is wiring that. Not on these enquiry rows."
        ),
    )


def _short_day(iso: Any) -> str:
    s = str(iso or "")[:10]
    try:
        d = date.fromisoformat(s)
    except ValueError:
        return s or "—"
    return f"{d.strftime('%b')} {d.day}"


def _cmp_7v7_html(perf: dict | None, cur: str) -> str:
    """Last 7 vs prior 7 from the 14-day pull."""
    cmp7 = (perf or {}).get("compare_7v7") or {}
    last7 = cmp7.get("last_7") or {}
    prior7 = cmp7.get("prior_7") or {}
    if not last7 and not prior7:
        return '<p class="cmp7 mute">Last 7 vs prior 7: waiting on the 14-day pull.</p>'
    last_s = html.escape(money(last7.get("cost_usd"), cur))
    prior_s = html.escape(money(prior7.get("cost_usd"), cur))
    last_c = html.escape(num(last7.get("clicks")))
    prior_c = html.escape(num(prior7.get("clicks")))
    last_ctr = html.escape(pct(last7.get("ctr_pct")))
    prior_ctr = html.escape(pct(prior7.get("ctr_pct")))
    last_win = html.escape(f"{_short_day(last7.get('start'))}–{_short_day(last7.get('end'))}")
    prior_win = html.escape(f"{_short_day(prior7.get('start'))}–{_short_day(prior7.get('end'))}")
    return (
        f'<p class="cmp7">7v7 <span class="mute">({last_win} vs {prior_win})</span>: '
        f"spend {last_s} vs {prior_s} · clicks {last_c} vs {prior_c} · "
        f"CTR {last_ctr} vs {prior_ctr}.</p>"
    )


def _delta_pct(stage: Any, agency: Any, *, higher_is_better: bool) -> tuple[str, str]:
    """Return (css_class, label) for Stage 1 vs agency. Empty if not comparable."""
    try:
        s = float(stage)
        a = float(agency)
    except (TypeError, ValueError):
        return "", ""
    if a == 0:
        return "", ""
    change = 100.0 * (s - a) / a
    better = (change > 0) if higher_is_better else (change < 0)
    css = "delta-good" if better else "delta-bad"
    sign = "+" if change > 0 else ""
    word = "better" if better else "worse"
    if higher_is_better:
        label = f"{sign}{change:.0f}% {word}"
    else:
        # CPC: prefer “−67% lower” when Stage is cheaper
        if change < 0:
            label = f"{change:.0f}% lower"
            css = "delta-good"
        elif change > 0:
            label = f"+{change:.0f}% higher"
            css = "delta-bad"
        else:
            label = "flat"
            css = "delta-flat"
    return css, label


def _times_higher(this_n: Any, legacy_n: Any) -> tuple[str, str]:
    """How many times higher this week is vs legacy (CTR)."""
    try:
        a = float(this_n)
        b = float(legacy_n)
    except (TypeError, ValueError):
        return "delta-flat", "—"
    if b <= 0:
        return "delta-flat", "—"
    r = a / b
    return "delta-good", f"{r:.1f}×"


def _pct_lower(this_n: Any, legacy_n: Any) -> tuple[str, str]:
    """How much cheaper this week is vs legacy (CPC / cost per JO)."""
    try:
        a = float(this_n)
        b = float(legacy_n)
    except (TypeError, ValueError):
        return "delta-flat", "—"
    if b <= 0 or a <= 0:
        return "delta-flat", "—"
    change = 100.0 * (a - b) / b
    if change < 0:
        return "delta-good", f"{abs(change):.0f}% lower"
    if change > 0:
        return "delta-bad", f"{change:.0f}% higher"
    return "delta-flat", "flat"


def _week_label_plain(start: str, end: str) -> str:
    try:
        a = date.fromisoformat(start[:10])
        b = date.fromisoformat(end[:10])
    except ValueError:
        return SCOREBOARD_WEEK_LABEL
    return f"{a.strftime('%a %b %-d')} – {b.strftime('%a %b %-d')}"


def _inclusive_days(window: str) -> int | None:
    found = re.findall(r"\d{4}-\d{2}-\d{2}", str(window or ""))
    if len(found) < 2:
        return None
    try:
        a = date.fromisoformat(found[0])
        b = date.fromisoformat(found[1])
    except ValueError:
        return None
    if b < a:
        return None
    return (b - a).days + 1


def _typical_7d(total: Any, window: str) -> float | None:
    """Old-agency typical 7-day week: total spend ÷ days × 7."""
    days = _inclusive_days(window)
    if not days or total is None or total == "":
        return None
    try:
        return float(total) / float(days) * 7.0
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def _div_cost(spend: Any, n: Any) -> float | None:
    try:
        s = float(spend)
        k = float(n)
    except (TypeError, ValueError):
        return None
    if k <= 0:
        return None
    return round(s / k, 2)


def _scale_for_days(n: Any, volume_days: int | None) -> Any:
    """Shrink a typical 7-day number to a mid-week slice. Rates stay unscaled."""
    if volume_days is None or n is None or n == "":
        return n
    try:
        return float(n) * (float(volume_days) / 7.0)
    except (TypeError, ValueError):
        return n


def _landing_sessions(pages: list | None, path: str) -> int | None:
    for p in pages or []:
        if str(p.get("path") or "") == path:
            try:
                return int(p.get("sessions") or 0)
            except (TypeError, ValueError):
                return None
    return None


def _secs_plain(n: Any) -> str:
    if n is None or n == "":
        return "—"
    try:
        s = float(n)
    except (TypeError, ValueError):
        return "—"
    if s <= 0:
        return "—"
    if s >= 60:
        return f"{int(s // 60)}m {int(s % 60):02d}s"
    return f"{int(round(s))}s"


def _human_span(raw: str) -> str:
    """Turn 2024-08-01 → 2026-08-04 (Editor…) into a short date span."""
    s = str(raw or "").strip()
    found = re.findall(r"\d{4}-\d{2}-\d{2}", s)
    if len(found) >= 2:
        try:
            a = date.fromisoformat(found[0])
            b = date.fromisoformat(found[1])
            return f"{a.strftime('%b %-d, %Y')} – {b.strftime('%b %-d, %Y')}"
        except ValueError:
            pass
    return s or "—"


def _mon_fri_weeks(window: str) -> float | None:
    """Mon–Fri weeks in an inclusive date span — same shape as the sales week."""
    found = re.findall(r"\d{4}-\d{2}-\d{2}", str(window or ""))
    if len(found) < 2:
        return None
    try:
        start = date.fromisoformat(found[0])
        end = date.fromisoformat(found[1])
    except ValueError:
        return None
    if end < start:
        return None
    weekdays = 0
    day = start
    step = timedelta(days=1)
    while day <= end:
        if day.weekday() < 5:
            weekdays += 1
        day += step
    if weekdays < 5:
        return None
    return weekdays / 5.0


def _ga4_window_plain(ga4: dict | None) -> str:
    """GA4 pull window in plain dates. Rolling — not the sales week."""
    if not ga4:
        return "Not in this bake"
    gen = str(ga4.get("generated_at_utc") or "")[:10]
    raw = str(ga4.get("window") or "")
    try:
        end = date.fromisoformat(gen)
    except ValueError:
        return raw or "—"
    if "7daysAgo" in raw.replace(" ", ""):
        start = end - timedelta(days=7)
        return f"{start.strftime('%b %-d')} – {end.strftime('%b %-d, %Y')} · rolling 7 days"
    found = re.findall(r"\d{4}-\d{2}-\d{2}", raw)
    if len(found) >= 2:
        return f"{_human_span(raw)}"
    return raw or gen


def _volume_vs(this_n: Any, legacy_n: Any) -> tuple[str, str]:
    """This week vs weekly average — higher volume is better."""
    try:
        a = float(this_n)
        b = float(legacy_n)
    except (TypeError, ValueError):
        return "delta-flat", "—"
    if b <= 0:
        return "delta-flat", "—"
    r = a / b
    if r >= 1:
        return "delta-good", f"{r:.1f}×"
    return "delta-bad", f"{abs(100.0 * (a - b) / b):.0f}% lower"


def _week_avg_plain(total: Any, weeks: float | None) -> str:
    if weeks is None or total is None or total == "":
        return "—"
    try:
        n = float(total) / float(weeks)
    except (TypeError, ValueError, ZeroDivisionError):
        return "—"
    if n >= 10:
        return f"{n:.0f}"
    return f"{n:.1f}"


def _legacy_row(
    market: str,
    this_s: str,
    leg_s: str,
    css: str,
    delta: str,
    mid_s: str | None = None,
    mid_css: str | None = None,
    mid_delta: str | None = None,
) -> str:
    """One market line. Cells are direct grid children so every column lines up."""
    mid = ""
    if mid_s is not None:
        mid = f"<span class='cell num lg'>{html.escape(mid_s)}</span>"
        if mid_css is not None and mid_delta is not None:
            mid += (
                f"<span class='cell num {html.escape(mid_css)}'>"
                f"{html.escape(mid_delta)}</span>"
            )
    return (
        f"<span class='cell cm'>{html.escape(market)}</span>"
        f"<span class='cell num tw'>{html.escape(this_s)}</span>"
        f"{mid}"
        f"<span class='cell num lg'>{html.escape(leg_s)}</span>"
        f"<span class='cell num {html.escape(css)}'>{html.escape(delta)}</span>"
    )


def _legacy_group(
    title: str,
    us: tuple[str, ...],
    au: tuple[str, ...],
) -> str:
    """Metric block: a full-width label row, then US and AU on the shared grid."""

    def _pack(market: str, row: tuple[str, ...]) -> str:
        if len(row) == 7:
            this_s, mid_s, mid_css, mid_d, leg_s, css, delta = row
            return _legacy_row(
                market,
                this_s,
                leg_s,
                css,
                delta,
                mid_s=mid_s,
                mid_css=mid_css,
                mid_delta=mid_d,
            )
        if len(row) == 5:
            this_s, mid_s, leg_s, css, delta = row
            return _legacy_row(market, this_s, leg_s, css, delta, mid_s=mid_s)
        this_s, leg_s, css, delta = row
        return _legacy_row(market, this_s, leg_s, css, delta)

    return (
        f"<span class='cell grp'>{html.escape(title)}</span>"
        f"{_pack('US', us)}{_pack('AU', au)}"
    )


def _legacy_sheet(
    groups: str,
    band: str,
    band_note: str = "",
    *,
    this_hd: str = "This week",
    legacy_hd: str = "Legacy week",
    extra_hd: str | None = None,
) -> str:
    """One band (Ads or Sales) — its own label, one shared grid."""
    note = (
        f"<span class='cmp-band-note'>{html.escape(band_note)}</span>" if band_note else ""
    )
    if extra_hd:
        extra = (
            f"<span class='cell hd num'>{html.escape(extra_hd)}</span>"
            "<span class='cell hd num'>Δ last week</span>"
        )
        delta_hd = "Δ legacy"
        sheet_cls = "cmp-sheet has-lastwk"
    else:
        extra = ""
        delta_hd = "Δ"
        sheet_cls = "cmp-sheet"
    return (
        "<div class='cmp-band'>"
        f"<div class='cmp-band-hd'><h3>{html.escape(band)}</h3>{note}</div>"
        f"<div class='{sheet_cls}'>"
        "<span class='cell hd'></span>"
        f"<span class='cell hd num'>{html.escape(this_hd)}</span>"
        f"{extra}"
        f"<span class='cell hd num'>{html.escape(legacy_hd)}</span>"
        f"<span class='cell hd num'>{html.escape(delta_hd)}</span>"
        f"{groups}</div></div>"
    )


def _num1(n: Any) -> str:
    if n is None:
        return "—"
    try:
        f = float(n)
    except (TypeError, ValueError):
        return "—"
    return f"{f:,.0f}" if f >= 10 else f"{f:,.1f}"


def _zoho_week_n(block: dict) -> int | None:
    """This-week enquiry count from the Zoho census — same n the Zoho box uses."""
    n = block.get("n")
    if n is None or n == "":
        return None
    try:
        return int(float(n))
    except (TypeError, ValueError):
        return None


def _legacy_enq_week(action: dict | None) -> float | None:
    """Agency-era enquiries per 7 days from the lead-form action's own date range."""
    if not action:
        return None
    days = _inclusive_days(str(action.get("date_range") or ""))
    try:
        total = float(action.get("n"))
    except (TypeError, ValueError):
        return None
    if not days or days <= 0:
        return None
    return total / (days / 7.0)


def _cost_per_jo_note(zjo: dict, cpl: dict | None = None) -> str:
    """Say out loud which job orders sit under each cost / JO."""
    us_n = zjo.get("us_jo")
    au_n = zjo.get("au_jo")
    if us_n is None and au_n is None:
        return "Legacy cost / job order not available."
    us_src = (cpl or {}).get("cost_per_job_order_source")
    us_census_jo = ((cpl or {}).get("zoho_census") or {}).get("job_order_submitted")
    if us_src == "zoho_census" and us_census_jo:
        us_line = (
            f"US Cost / job order this week uses the Zoho census ({html.escape(num(us_census_jo))} JO). "
            "Cheyenne did not name a job order."
        )
    elif (cpl or {}).get("cost_per_job_order_usd") is not None:
        us_line = "US Cost / job order this week uses the job order named on the US card."
    else:
        us_line = "US Cost / job order this week is blank because ops did not name a US job order."
    return (
        "Legacy cost / job order is agency spend ÷ the job orders in the Zapier CRM extract "
        f"({html.escape(num(us_n))} US · {html.escape(num(au_n))} AU), the whole extract "
        f"we hold for those years, not a paid-only slice. {us_line} "
        "AU Cost / job order uses Holly’s labeled job orders, not the Zoho census."
    )


def _sales_band_note(
    us_enq: Any,
    au_enq: Any,
    us_ops_enq: Any,
    legacy_enq: dict,
    au_ops_enq: Any = None,
) -> str:
    """This-week Enquiries are the Zoho census — same as the Zoho box."""
    picked = (
        f"This-week Enquiries are the Zoho census (US {num(us_enq)} · AU {num(au_enq)}) — "
        "same numbers as the Zoho box."
    )
    try:
        ops_n = int(float(us_ops_enq)) if us_ops_enq is not None and us_ops_enq != "" else None
    except (TypeError, ValueError):
        ops_n = None
    if ops_n is not None and ops_n != us_enq:
        picked += f" Cheyenne’s {ops_n} stays on the US card."
    try:
        au_ops_n = (
            int(float(au_ops_enq)) if au_ops_enq is not None and au_ops_enq != "" else None
        )
    except (TypeError, ValueError):
        au_ops_n = None
    if au_ops_n is not None and au_ops_n != au_enq:
        picked += f" Holly’s {au_ops_n} stays on the AU card."
    acts = [a for a in ((legacy_enq or {}).get("us"), (legacy_enq or {}).get("au")) if a]
    if acts:
        names = {str(a.get("name") or "") for a in acts}
        name_s = " · ".join(sorted(names))
        legacy_line = (
            " Legacy enquiries are the agency's own Google Ads lead-form conversions "
            f"({name_s}), averaged over their run — Zoho has no Sales Enquiry history "
            "for most of that period."
        )
    else:
        legacy_line = " No agency enquiry counter in the audit."
    return html.escape(picked + legacy_line)


def _legacy_agency_table(
    us_week: dict,
    au_week: dict,
    bus: dict,
    bau: dict,
    zjo: dict,
    cpl: dict,
    cpl_au: dict,
    *,
    week_label: str,
    legacy_window: str,
    ga4: dict | None,
    legacy_enq: dict | None = None,
    zoho_week: dict | None = None,
    volume_days: int | None = None,
    ads_note: str | None = None,
    sales_note: str | None = None,
    this_hd: str = "This week",
    legacy_hd: str = "Legacy week",
    ga4_label: str | None = None,
    last_week: dict | None = None,
) -> tuple[str, str]:
    """This week vs the full legacy-agency run. Returns (sales_html, ads_html)."""
    us_ctr_css, us_ctr_d = _times_higher(us_week.get("ctr_pct"), bus.get("ctr_pct"))
    au_ctr_css, au_ctr_d = _times_higher(au_week.get("ctr_pct"), bau.get("ctr_pct"))
    us_cpc_css, us_cpc_d = _pct_lower(us_week.get("avg_cpc_usd"), bus.get("avg_cpc"))
    au_cpc_css, au_cpc_d = _pct_lower(au_week.get("avg_cpc_usd"), bau.get("avg_cpc"))
    au_jo = cpl_au.get("cost_per_job_order_usd")
    us_jo_week = cpl.get("cost_per_job_order_usd")
    jo_us_leg = zjo.get("cost_per_jo_us")
    jo_au_leg = zjo.get("cost_per_jo_au")
    # n=1 US JO is still a real unit cost — do not hide the delta.
    us_jo_css, us_jo_d = (
        _pct_lower(us_jo_week, jo_us_leg) if us_jo_week is not None else ("delta-flat", "—")
    )
    au_jo_css, au_jo_d = _pct_lower(au_jo, jo_au_leg) if au_jo is not None else ("delta-flat", "—")
    weeks = _inclusive_days(legacy_window)
    weeks7 = (weeks / 7.0) if weeks else None
    us_week_avg = _scale_for_days(_typical_7d(bus.get("cost"), legacy_window), volume_days)
    au_week_avg = _scale_for_days(_typical_7d(bau.get("cost"), legacy_window), volume_days)
    us_sp_css, us_sp_d = _pct_lower(us_week.get("cost_usd"), us_week_avg)
    au_sp_css, au_sp_d = _pct_lower(au_week.get("cost_usd"), au_week_avg)
    # This-week Enquiries match the Zoho box (same window, same US/AU split).
    # Cheyenne’s email count stays on the US card — never added, never used here.
    us_zoho = (zoho_week or {}).get("usa") or {}
    au_zoho = (zoho_week or {}).get("au") or {}
    us_enq = _zoho_week_n(us_zoho)
    au_enq = _zoho_week_n(au_zoho)
    # Job orders and discovery come off the same Zoho rows as the Zoho box, so
    # the two sections cannot show different counts for the same week.
    us_jo_w = _zoho_status(us_zoho, "Job Order Submitted")
    au_jo_w = _zoho_status(au_zoho, "Job Order Submitted")
    if au_jo_w is None:
        au_jo_w = cpl_au.get("job_order_submitted")
    us_disc_w = us_zoho.get("discovery_scheduled")
    au_disc_w = au_zoho.get("discovery_scheduled")
    if au_disc_w is None:
        au_disc_w = cpl_au.get("discovery_scheduled")
    us_jo_typ = _scale_for_days(_typical_7d(zjo.get("us_jo"), legacy_window), volume_days)
    au_jo_typ = _scale_for_days(_typical_7d(zjo.get("au_jo"), legacy_window), volume_days)
    us_disc_typ = _scale_for_days(
        _typical_7d(zjo.get("us_discovery"), legacy_window), volume_days
    )
    au_disc_typ = _scale_for_days(
        _typical_7d(zjo.get("au_discovery"), legacy_window), volume_days
    )
    if volume_days is not None:
        us_jo_avg = _num1(us_jo_typ)
        au_jo_avg = _num1(au_jo_typ)
        us_disc_avg = _num1(us_disc_typ)
        au_disc_avg = _num1(au_disc_typ)
    else:
        us_jo_avg = _week_avg_plain(zjo.get("us_jo"), weeks7)
        au_jo_avg = _week_avg_plain(zjo.get("au_jo"), weeks7)
        us_disc_avg = _week_avg_plain(zjo.get("us_discovery"), weeks7)
        au_disc_avg = _week_avg_plain(zjo.get("au_discovery"), weeks7)
    us_jo_vol_css, us_jo_vol_d = _volume_vs(us_jo_w, us_jo_typ)
    au_jo_vol_css, au_jo_vol_d = _volume_vs(au_jo_w, au_jo_typ)
    us_disc_vol_css, us_disc_vol_d = _volume_vs(us_disc_w, us_disc_typ)
    au_disc_vol_css, au_disc_vol_d = _volume_vs(au_disc_w, au_disc_typ)
    us_leg_enq = _scale_for_days(_legacy_enq_week((legacy_enq or {}).get("us")), volume_days)
    au_leg_enq = _scale_for_days(_legacy_enq_week((legacy_enq or {}).get("au")), volume_days)
    us_enq_css, us_enq_d = _volume_vs(us_enq, us_leg_enq)
    au_enq_css, au_enq_d = _volume_vs(au_enq, au_leg_enq)
    # Cost / enquiry uses quality n — named sales when they exist, else
    # Zoho minus junk / not-a-fit / job-seeker. Never raw all-source n.
    us_cpl_n = cpl.get("enquiries") or _quality_enquiry_n(us_zoho)
    au_cpl_n = cpl_au.get("enquiries") or _quality_enquiry_n(au_zoho)
    us_enq_cost = _div_cost(us_week.get("cost_usd"), us_cpl_n)
    au_enq_cost = _div_cost(au_week.get("cost_usd"), au_cpl_n)
    us_leg_enq_cost = _div_cost(us_week_avg, us_leg_enq)
    au_leg_enq_cost = _div_cost(au_week_avg, au_leg_enq)
    us_enq_c_css, us_enq_c_d = (
        _pct_lower(us_enq_cost, us_leg_enq_cost)
        if us_enq_cost is not None and us_leg_enq_cost is not None
        else ("delta-flat", "—")
    )
    au_enq_c_css, au_enq_c_d = (
        _pct_lower(au_enq_cost, au_leg_enq_cost)
        if au_enq_cost is not None and au_leg_enq_cost is not None
        else ("delta-flat", "—")
    )
    us_disc_cost = _div_cost(us_week.get("cost_usd"), us_disc_w)
    au_disc_cost = _div_cost(au_week.get("cost_usd"), au_disc_w)
    us_leg_disc_cost = _div_cost(us_week_avg, us_disc_typ)
    au_leg_disc_cost = _div_cost(au_week_avg, au_disc_typ)
    us_disc_c_css, us_disc_c_d = (
        _pct_lower(us_disc_cost, us_leg_disc_cost)
        if us_disc_cost is not None and us_leg_disc_cost is not None
        else ("delta-flat", "—")
    )
    au_disc_c_css, au_disc_c_d = (
        _pct_lower(au_disc_cost, au_leg_disc_cost)
        if au_disc_cost is not None and au_leg_disc_cost is not None
        else ("delta-flat", "—")
    )

    boxes = "".join(
        [
            _legacy_group(
                "CTR",
                (pct(us_week.get("ctr_pct")), pct(bus.get("ctr_pct")), us_ctr_css, us_ctr_d),
                (pct(au_week.get("ctr_pct")), pct(bau.get("ctr_pct")), au_ctr_css, au_ctr_d),
            ),
            _legacy_group(
                "CPC",
                (
                    money2(us_week.get("avg_cpc_usd"), "USD"),
                    money2(bus.get("avg_cpc"), "USD"),
                    us_cpc_css,
                    us_cpc_d,
                ),
                (
                    money2(au_week.get("avg_cpc_usd"), "AUD"),
                    money2(bau.get("avg_cpc"), "AUD"),
                    au_cpc_css,
                    au_cpc_d,
                ),
            ),
            _legacy_group(
                "Spend",
                (
                    money(us_week.get("cost_usd"), "USD"),
                    money(us_week_avg, "USD"),
                    us_sp_css,
                    us_sp_d,
                ),
                (
                    money(au_week.get("cost_usd"), "AUD"),
                    money(au_week_avg, "AUD"),
                    au_sp_css,
                    au_sp_d,
                ),
            ),
            _legacy_group(
                "Cost / enquiry",
                (
                    money2(us_enq_cost, "USD") if us_enq_cost is not None else "—",
                    money2(us_leg_enq_cost, "USD") if us_leg_enq_cost is not None else "—",
                    us_enq_c_css,
                    us_enq_c_d,
                ),
                (
                    money2(au_enq_cost, "AUD") if au_enq_cost is not None else "—",
                    money2(au_leg_enq_cost, "AUD") if au_leg_enq_cost is not None else "—",
                    au_enq_c_css,
                    au_enq_c_d,
                ),
            ),
            _legacy_group(
                "Cost / discovery",
                (
                    money2(us_disc_cost, "USD") if us_disc_cost is not None else "—",
                    money2(us_leg_disc_cost, "USD") if us_leg_disc_cost is not None else "—",
                    us_disc_c_css,
                    us_disc_c_d,
                ),
                (
                    money2(au_disc_cost, "AUD") if au_disc_cost is not None else "—",
                    money2(au_leg_disc_cost, "AUD") if au_leg_disc_cost is not None else "—",
                    au_disc_c_css,
                    au_disc_c_d,
                ),
            ),
            _legacy_group(
                "Cost / job order",
                (
                    money2(us_jo_week, "USD") if us_jo_week is not None else "—",
                    money(jo_us_leg, "USD") if jo_us_leg else "—",
                    us_jo_css,
                    us_jo_d,
                ),
                (
                    money2(au_jo, "AUD") if au_jo is not None else "—",
                    money(jo_au_leg, "AUD") if jo_au_leg else "—",
                    au_jo_css,
                    au_jo_d,
                ),
            ),
        ]
    )
    lw = last_week or {}
    lw_us = lw.get("usa") or {}
    lw_au = lw.get("au") or {}
    has_last = bool(lw_us or lw_au)

    def _sales_tuple(
        this_n: Any, last_n: Any, leg_s: str, css: str, delta: str
    ) -> tuple[str, ...]:
        if has_last:
            lw_css, lw_d = _volume_vs(this_n, last_n)
            return (num(this_n), num(last_n), lw_css, lw_d, leg_s, css, delta)
        return (num(this_n), leg_s, css, delta)

    sales = "".join(
        [
            _legacy_group(
                "Enquiries",
                _sales_tuple(us_enq, lw_us.get("n"), _num1(us_leg_enq), us_enq_css, us_enq_d),
                _sales_tuple(au_enq, lw_au.get("n"), _num1(au_leg_enq), au_enq_css, au_enq_d),
            ),
            _legacy_group(
                "Discovery",
                _sales_tuple(
                    us_disc_w,
                    lw_us.get("discovery_scheduled"),
                    us_disc_avg,
                    us_disc_vol_css,
                    us_disc_vol_d,
                ),
                _sales_tuple(
                    au_disc_w,
                    lw_au.get("discovery_scheduled"),
                    au_disc_avg,
                    au_disc_vol_css,
                    au_disc_vol_d,
                ),
            ),
            _legacy_group(
                "Job orders",
                _sales_tuple(
                    us_jo_w,
                    lw_us.get("job_order_submitted"),
                    us_jo_avg,
                    us_jo_vol_css,
                    us_jo_vol_d,
                ),
                _sales_tuple(
                    au_jo_w,
                    lw_au.get("job_order_submitted"),
                    au_jo_avg,
                    au_jo_vol_css,
                    au_jo_vol_d,
                ),
            ),
        ]
    )
    ads_line = ads_note if ads_note is not None else _cost_per_jo_note(zjo, cpl)
    sales_line = sales_note if sales_note is not None else _sales_band_note(
        us_enq,
        au_enq,
        cpl.get("enquiries"),
        (legacy_enq or {}),
        au_ops_enq=cpl_au.get("enquiries"),
    )
    ga4_dd = ga4_label if ga4_label is not None else _ga4_window_plain(ga4)
    sales_html = f"""        {_legacy_sheet(sales, "Sales", "Zoho rows · same week as the cards", this_hd=this_hd, legacy_hd=legacy_hd, extra_hd=("Last week" if has_last else None))}
        <p class="cmp-note">{sales_line}</p>"""
    ads_html = f"""        {_legacy_sheet(boxes, "Ads", "Google Ads · both accounts", this_hd=this_hd, legacy_hd=legacy_hd)}
        <p class="cmp-note">{ads_line}</p>
        <dl class="windows">
          <div><dt>This week</dt><dd>{html.escape(week_label)}</dd></div>
          <div><dt>Legacy agency</dt><dd>{html.escape(_human_span(legacy_window))}</dd></div>
          <div><dt>GA4</dt><dd>{html.escape(ga4_dd)}</dd></div>
        </dl>"""
    return sales_html, ads_html


def _ga4_fmt(n: Any, kind: str) -> str:
    if kind == "rate":
        return pct(n)
    if kind == "duration":
        return _secs_plain(n)
    return num(n)


def _wow_chip(
    now: Any,
    prior: Any,
    *,
    kind: str = "count",
    higher_is_better: bool = True,
) -> str:
    """Green ▲ = improved, red ▼ = worse. Counts/time = %; rates = pts."""
    try:
        a = float(now)
        b = float(prior)
    except (TypeError, ValueError):
        return ""
    if b == 0:
        return ""
    if kind == "rate":
        delta = a - b
        if abs(delta) < 0.05:
            return ""
        mag = f"{abs(delta):.1f} pts"
        improved = (delta > 0) if higher_is_better else (delta < 0)
    else:
        change = 100.0 * (a - b) / b
        if abs(change) < 0.5:
            return ""
        mag = f"{abs(change):.0f}%"
        improved = (change > 0) if higher_is_better else (change < 0)
    css = "delta-good" if improved else "delta-bad"
    arr = "▲" if a > b else "▼"
    word = "improved" if improved else "worse"
    return (
        f"<span class='wow {css}' title='{html.escape(word)} {html.escape(mag)} vs last week'>"
        f"<span class='wow-arr' aria-hidden='true'>{arr}</span>"
        f"{html.escape(mag)}</span>"
    )


def _ga4_wow_sub(
    now: Any,
    prior: Any,
    *,
    kind: str = "count",
    higher_is_better: bool = True,
    prior_ok: bool = False,
    vs_label: str = "last week",
) -> str:
    if not prior_ok or prior is None or prior == "":
        return ""
    prior_s = _ga4_fmt(prior, kind)
    if prior_s in ("", "—"):
        return ""
    chip = _wow_chip(now, prior, kind=kind, higher_is_better=higher_is_better)
    label = html.escape(vs_label)
    inner = (
        f"{chip} vs {html.escape(prior_s)} {label}"
        if chip
        else f"vs {html.escape(prior_s)} {label}"
    )
    return f"<span class='sub'>{inner}</span>"


def _ga4_no_prior_sub(reason: str = "first tagged days") -> str:
    return f"<span class='sub'>{html.escape(reason)}</span>"


def _halo_jo_n(block: dict | None) -> Any:
    block = block or {}
    n = block.get("job_order_submitted")
    if n is not None and n != "":
        return n
    return _zoho_status(block, "Job Order Submitted")


def _halo_place_n(block: dict | None) -> Any:
    return _zoho_status(block or {}, "Placement")


def _halo_est_sub(cost: Any) -> str:
    return "<span class='sub'>estimated</span>" if cost is not None else ""


def _halo_scoreboard(
    *,
    section_id: str,
    title: str,
    aria: str,
    meta: str,
    usa: dict,
    au: dict,
    us_spend: Any = None,
    au_spend: Any = None,
    foot: str = "",
    extra_html: str = "",
) -> str:
    """Zoho volume + estimated cost, same US/AU tiles as Google Analytics."""
    se_us = usa.get("n")
    se_au = au.get("n")
    disc_us = usa.get("discovery_scheduled")
    disc_au = au.get("discovery_scheduled")
    jo_us = _halo_jo_n(usa)
    jo_au = _halo_jo_n(au)
    place_us = _halo_place_n(usa)
    place_au = _halo_place_n(au)
    enq_us_c = _div_cost(us_spend, se_us)
    enq_au_c = _div_cost(au_spend, se_au)
    disc_us_c = _div_cost(us_spend, disc_us)
    disc_au_c = _div_cost(au_spend, disc_au)
    jo_us_c = _div_cost(us_spend, jo_us)
    jo_au_c = _div_cost(au_spend, jo_au)
    boxes = "".join(
        [
            _ga4_now_box("Enquiries", num(se_us), num(se_au)),
            _ga4_now_box("Discovery", num(disc_us), num(disc_au)),
            _ga4_now_box("Job orders", num(jo_us), num(jo_au)),
            _ga4_now_box(
                "Job placements",
                num(place_us) if place_us is not None else "—",
                num(place_au) if place_au is not None else "—",
                "<span class='sub'>Ash · not on these rows</span>"
                if place_us is None
                else "",
                "<span class='sub'>Ash · not on these rows</span>"
                if place_au is None
                else "",
            ),
            _ga4_now_box(
                "Cost / enquiry",
                money2(enq_us_c, "USD") if enq_us_c is not None else "—",
                money2(enq_au_c, "AUD") if enq_au_c is not None else "—",
                _halo_est_sub(enq_us_c),
                _halo_est_sub(enq_au_c),
            ),
            _ga4_now_box(
                "Cost / discovery",
                money2(disc_us_c, "USD") if disc_us_c is not None else "—",
                money2(disc_au_c, "AUD") if disc_au_c is not None else "—",
                _halo_est_sub(disc_us_c),
                _halo_est_sub(disc_au_c),
            ),
            _ga4_now_box(
                "Cost / job order",
                money2(jo_us_c, "USD") if jo_us_c is not None else "—",
                money2(jo_au_c, "AUD") if jo_au_c is not None else "—",
                _halo_est_sub(jo_us_c),
                _halo_est_sub(jo_au_c),
            ),
        ]
    )
    foot_html = (
        f'<p class="mute ga4-foot">{html.escape(foot)}</p>' if foot else ""
    )
    return f"""
      <section class="halo" id="{html.escape(section_id)}" aria-label="{html.escape(aria)}">
        <div class="sec-hd">
          <h2>{html.escape(title)}</h2>
          <p class="sec-meta">{html.escape(meta)}</p>
        </div>
        <div class="legacy-grid ga4-grid">{boxes}</div>
        {foot_html}
        {extra_html}
      </section>
"""


def _ga4_now_box(title: str, us_s: str, au_s: str, us_sub: str = "", au_sub: str = "") -> str:
    return (
        '<div class="legacy-box">'
        f"<h3>{html.escape(title)}</h3>"
        "<table><tbody>"
        f"<tr><th scope='row'>US</th><td class='num this-w'>{html.escape(us_s)}{us_sub}</td></tr>"
        f"<tr><th scope='row'>AU</th><td class='num this-w'>{html.escape(au_s)}{au_sub}</td></tr>"
        "</tbody></table></div>"
    )


_GA4_LP_SKIP = {"(not set)", "", "/", "untagged"}


def _ga4_lp_pick(pages: list | None, limit: int = 6) -> list[dict]:
    out: list[dict] = []
    for p in pages or []:
        path = str(p.get("path") or p.get("path_display") or "")
        if path in _GA4_LP_SKIP:
            continue
        out.append(p)
        if len(out) >= limit:
            break
    return out


def _lp_row_id(prefix: str, path: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(path or "").strip("/").lower()).strip("-")
    return f"{prefix}-{slug or 'root'}"


def _ga4_lp_table(
    us_pages: list | None,
    au_pages: list | None,
    *,
    row_prefix: str = "lp-now",
) -> str:
    """CRO table: which landing pages get visits and whether people stay."""
    us_rows = _ga4_lp_pick(us_pages)
    au_rows = _ga4_lp_pick(au_pages)
    if not us_rows and not au_rows:
        return ""

    def _body(rows: list[dict]) -> str:
        bits = []
        for p in rows:
            path = str(p.get("path_display") or p.get("path") or "—")
            try:
                sess = int(p.get("sessions") or 0)
            except (TypeError, ValueError):
                sess = 0
            small = sess < 10
            cls = " class='small-n'" if small else ""
            sample = (
                " <span class='sample-tag'>small sample</span>" if small else ""
            )
            rid = _lp_row_id(row_prefix, str(p.get("path") or path))
            bits.append(
                f"<tr{cls} id='{html.escape(rid)}'>"
                f"<th scope='row'>{html.escape(path)}{sample}</th>"
                f"<td class='num'>{html.escape(num(p.get('sessions')))}</td>"
                f"<td class='num'>{html.escape(pct(p.get('engagement_rate_pct')))}</td>"
                f"<td class='num'>{html.escape(_secs_plain(p.get('avg_session_seconds')))}</td>"
                f"<td class='num'>{html.escape(pct(p.get('bounce_rate_pct')))}</td>"
                "</tr>"
            )
        return "".join(bits) or "<tr><td colspan='5' class='mute'>None yet</td></tr>"

    head = (
        "<thead><tr><th>Page</th><th class='num'>Sessions</th>"
        "<th class='num'>Stayed</th>"
        "<th class='num' title='GA4 averageSessionDuration — same definition as Time on site above. Not a separate focus-time metric.'>Avg. engagement time</th>"
        "<th class='num'>Bounce</th></tr></thead>"
    )
    return (
        "<div class='lp-block'>"
        "<div class='sec-hd'><h2>Landing pages</h2>"
        "<p class='sec-meta'>Same window as the tiles · Avg. session duration uses the same GA4 averageSessionDuration as Time on site. Pages under 10 sessions are faded — do not call a 100% stay rate a winner on one or two visits.</p></div>"
        "<div class='legacy-grid lp-grid'>"
        "<div class='legacy-box'><h3>United States</h3>"
        f"<table class='lp-t'>{head}<tbody>{_body(us_rows)}</tbody></table></div>"
        "<div class='legacy-box'><h3>Australia</h3>"
        f"<table class='lp-t'>{head}<tbody>{_body(au_rows)}</tbody></table></div>"
        "</div></div>"
    )


def _fnum(block: dict | None, key: str) -> float | None:
    try:
        return float((block or {}).get(key))
    except (TypeError, ValueError):
        return None


def _insight_item(happened: str, means: str, nxt: str, caveat: str) -> str:
    return (
        "<li>"
        f"<p><span class='ins-k'>Observed.</span> {happened}</p>"
        f"<p><span class='ins-k'>Probably means.</span> {means}</p>"
        f"<p><span class='ins-k'>Next.</span> {nxt}</p>"
        f"<p class='ins-caveat'><span class='ins-k'>Caveat.</span> {caveat}</p>"
        "</li>"
    )


def _exec_insight_html(
    us_ads: dict | None,
    au_ads: dict | None,
    us: dict,
    us_p: dict,
    au: dict,
    au_p: dict,
    *,
    us_land: list | None = None,
    au_prior_ok: bool = False,
) -> str:
    """Four human reads for this week so far. Fact, then guess, then watch."""
    us_ads = us_ads or {}
    au_ads = au_ads or {}
    us_same = us_ads.get("same_weekdays") if "same_weekdays" in us_ads else {}
    au_same = au_ads.get("same_weekdays") if "same_weekdays" in au_ads else {}
    us_tot = us_ads.get("totals") or us_ads
    au_tot = au_ads.get("totals") or au_ads

    us_clk, us_clk_p = _fnum(us_tot, "clicks"), _fnum(us_same, "clicks")
    us_imp, us_imp_p = _fnum(us_tot, "impressions"), _fnum(us_same, "impressions")
    us_ctr, us_ctr_p = _fnum(us_tot, "ctr_pct"), _fnum(us_same, "ctr_pct")
    us_cpc, us_cpc_p = _fnum(us_tot, "avg_cpc_usd"), _fnum(us_same, "avg_cpc_usd")
    au_imp, au_imp_p = _fnum(au_tot, "impressions"), _fnum(au_same, "impressions")
    au_clk, au_clk_p = _fnum(au_tot, "clicks"), _fnum(au_same, "clicks")
    au_ctr, au_ctr_p = _fnum(au_tot, "ctr_pct"), _fnum(au_same, "ctr_pct")

    us_hub = next((p for p in (us_land or []) if str(p.get("path") or "") == "/us"), None)
    us_stay = _fnum(us, "engagement_rate_pct")
    us_time = _fnum(us, "avg_session_seconds")
    us_time_p = _fnum(us_p, "avg_session_seconds")

    items = [
        _insight_item(
            (
                f"US Search clicks {html.escape(num(us_clk))} vs {html.escape(num(us_clk_p))} "
                f"same weekdays last week. Impressions {html.escape(num(us_imp))} vs "
                f"{html.escape(num(us_imp_p))}. CTR {html.escape(pct(us_ctr))} vs "
                f"{html.escape(pct(us_ctr_p))}. CPC {html.escape(money2(us_cpc, 'USD'))} vs "
                f"{html.escape(money2(us_cpc_p, 'USD'))}."
            ),
            "US traffic is holding. Volume is slightly up. People are still clicking at about the same rate. Cost per click is a little higher. There is no sign of account collapse.",
            "Watch CPC and junk queries. Do not treat this as a breakthrough or a failure.",
            "Thursday is still partial in the US. This is same-weekday, not a full week.",
        ),
        _insight_item(
            (
                f"Australia impressions {html.escape(num(au_imp))} vs {html.escape(num(au_imp_p))}. "
                f"Clicks {html.escape(num(au_clk))} vs {html.escape(num(au_clk_p))}. "
                f"CTR {html.escape(pct(au_ctr))} vs {html.escape(pct(au_ctr_p))}."
            ),
            "Australia is entering fewer auctions or seeing a smaller eligible pool. The people who still see the ads are clicking at a much higher rate.",
            "Watch volume. Do not automatically add keywords or budget.",
            (
                "Australia Thursday is further along than the US (Brisbane clock). "
                + (
                    "AU tags started Aug 12, so last week’s weekday compare is incomplete."
                    if not au_prior_ok
                    else "Same-weekday compare only — not a full week."
                )
            ),
        ),
        _insight_item(
            (
                f"US hub /us has {html.escape(num((us_hub or {}).get('sessions')))} sessions "
                f"and {html.escape(pct((us_hub or {}).get('engagement_rate_pct')))} stayed. "
                f"Time on site {html.escape(_secs_plain(us_time))} vs "
                f"{html.escape(_secs_plain(us_time_p))} same weekdays. "
                f"US stayed {html.escape(pct(us_stay))} this week so far."
            ),
            "Landing-page engagement looks encouraging, especially on the US hub.",
            "Treat the movement as directional. Wait for another clean week before calling a page a winner.",
            "Recent analytics wiring (18 Aug) may distort some events and engagement. GA4 “conversions” this week are noise — ignore them. A user-count change is not cohort retention.",
        ),
        _insight_item(
            "We can see ad clicks, page visits, named sales leads, and all-source Zoho rows. We cannot yet trust the path from landing page → enquiry → Job Order → Placement.",
            "The bottleneck is trustworthy attribution, not a shortage of dashboard metrics.",
            "Audit and document the Zoho pathway. Do not send Placement outcomes until the data model and conversion actions are approved.",
            "Cost / enquiry and Cost / job order on this page are not Google Ads CPA unless the tile says so. The two connected Ads actions are enquiry statuses (Job Order Submitted, Discovery Scheduled). There is no Placement action.",
        ),
    ]
    return (
        '<div class="ga4-insight">'
        "<h3>Insights</h3>"
        f"<ul>{''.join(items)}</ul>"
        "</div>"
    )


def _frozen_week_close_insights_html(
    us_ops: dict,
    au_ops: dict,
    us_perf: dict | None,
    au_perf: dict | None,
    ga4: dict | None,
) -> str:
    """Week-close readout at the bottom of the frozen tab."""
    us_cmp = ((us_perf or {}).get("compare_7v7") or {})
    au_cmp = ((au_perf or {}).get("compare_7v7") or {})
    us_ads = us_cmp.get("last_7") or {}
    us_ads_p = us_cmp.get("prior_7") or {}
    au_ads = au_cmp.get("last_7") or {}
    au_ads_p = au_cmp.get("prior_7") or {}

    us_enq = int(us_ops.get("enquiries") or 0)
    au_enq = int(au_ops.get("enquiries") or 0)
    us_calls = int(us_ops.get("sales_calls_completed") or 0)
    au_calls = int(au_ops.get("sales_calls_completed") or 0)
    us_cpl = us_ops.get("cost_per_enquiry_usd")
    au_cpl = au_ops.get("cost_per_enquiry_usd")
    p_us_enq = int(PRIOR_SALES_US["enquiries"])
    p_au_enq = int(PRIOR_SALES_AU["enquiries"])
    p_us_calls = int(PRIOR_SALES_US["sales_calls_completed"])
    p_au_calls = int(PRIOR_SALES_AU["sales_calls_completed"])
    p_us_cpl = PRIOR_SALES_US["cost_per_enquiry_usd"]
    p_au_cpl = PRIOR_SALES_AU["cost_per_enquiry_usd"]

    us_zoho = (us_ops.get("zoho_census") or {})
    au_zoho = (au_ops.get("zoho_census") or {})
    us_gclid = us_zoho.get("usa_with_gclid") or us_zoho.get("with_utm_gclid")
    au_gclid = au_zoho.get("au_with_gclid") or au_zoho.get("with_utm_gclid")

    us_ga4 = (ga4 or {}).get("totals_last_7_days") or {}
    au_ga4 = ((ga4 or {}).get("au") or {}).get("totals_last_7_days") or {}

    items = [
        _insight_item(
            (
                f"US named enquiries {html.escape(num(us_enq))} vs "
                f"{html.escape(num(p_us_enq))} prior week ({PRIOR_SCOREBOARD_WEEK_LABEL}). "
                f"Completed calls {html.escape(num(us_calls))} vs {html.escape(num(p_us_calls))}. "
                f"Cost / enquiry {html.escape(money2(us_cpl, 'USD'))} vs "
                f"{html.escape(money2(p_us_cpl, 'USD'))}. "
                f"Ads spend {html.escape(money(us_ads.get('cost_usd'), 'USD'))} vs "
                f"{html.escape(money(us_ads_p.get('cost_usd'), 'USD'))} "
                f"({html.escape(num(us_ads.get('clicks')))} clicks · "
                f"CPC {html.escape(money2(us_ads.get('avg_cpc_usd'), 'USD'))})."
            ),
            "The account spent more and labeled fewer US enquiries. Call completion held up — "
            f"{html.escape(num(us_calls))} on {html.escape(num(us_enq))} is a slightly better enquiry→call rate than last week. "
            "That is volume and labeling, not proof ads got worse.",
            "Keep Max Clicks. Watch junk queries and CPC. Do not chase Ads conversion totals.",
            "Cheyenne’s counts are Mon–Fri labeled. Zoho census (20 rows) is wider — not additive.",
        ),
        _insight_item(
            (
                f"AU named enquiries {html.escape(num(au_enq))} vs {html.escape(num(p_au_enq))} prior week. "
                f"Sales calls completed {html.escape(num(au_calls))} vs {html.escape(num(p_au_calls))}. "
                f"Cost / enquiry {html.escape(money2(au_cpl, 'AUD'))} vs "
                f"{html.escape(money2(p_au_cpl, 'AUD'))}. "
                f"Ads spend {html.escape(money(au_ads.get('cost_usd'), 'AUD'))} · "
                f"{html.escape(num(au_ads.get('clicks')))} clicks."
            ),
            "Australia held enquiry volume and improved call throughput. Holly did not break out job orders "
            "in this email format — the scoreboard stays on enquiries and completed calls only.",
            "Let Holly’s labeled counts drive the AU card. Zoho job-order rows are census, not extra enquiries.",
            "Mon–Fri labeled window. Full Mon–Sun is for Ads spend only.",
        ),
        _insight_item(
            (
                f"Zoho census same week: US {html.escape(num(us_zoho.get('usa_sales_enquiries')))} rows · "
                f"AU {html.escape(num(au_zoho.get('au_sales_enquiries')))} rows. "
                f"Click IDs stored: US {html.escape(num(us_gclid))} · AU {html.escape(num(au_gclid))}."
            ),
            "Most labelled leads still arrive without a click ID. Paid CAC is not yet measurable from Ads alone.",
            "Keep building the Zoho write path and gclid capture. Do not send Placement outcomes to Ads yet.",
            "Executive face = Cheyenne/Holly email buckets. Zoho is off-page attribution watch only.",
        ),
        _insight_item(
            (
                f"GA4 frozen week: US {html.escape(num(us_ga4.get('sessions')))} sessions · "
                f"{html.escape(pct(us_ga4.get('engagement_rate_pct')))} stayed. "
                f"AU {html.escape(num(au_ga4.get('sessions')))} sessions · "
                f"{html.escape(pct(au_ga4.get('engagement_rate_pct')))} stayed."
            ),
            "Site behaviour during the week looks healthy on both properties. US hub still takes most paid landings.",
            "Role-page CRO is the next landing-page bet — not a budget move this week.",
            "GA4 conversions after 18 Aug wiring are noise. Sessions and engagement are the read.",
        ),
        _insight_item(
            (
                f"{html.escape(SCOREBOARD_WEEK_LABEL)} is locked on the frozen tab. "
                f"This week so far starts {html.escape(str(((us_perf or {}).get('scoreboard_now') or {}).get('label') or 'Mon Aug 24'))}."
            ),
            "You now have two complete Mon–Sun sales weeks on Stage 1 Search. This is the baseline to compare forward.",
            "When Cheyenne and Holly email this week’s counts, they land on the default tab — not the frozen tab.",
            "Frozen Ads numbers refresh on pull. Sales-ops enquiry counts on the frozen tab do not move.",
        ),
    ]
    return (
        '<section class="week-close" id="week-close-insights" aria-label="Week close readout">'
        '<div class="ga4-insight">'
        "<h3>Week close · what to take from this report</h3>"
        f"<ul>{''.join(items)}</ul>"
        "</div>"
        "</section>"
    )


def _new_week_starter_insights_html(
    us_now: dict | None,
    au_now: dict | None,
) -> str:
    """Short read for the default tab at the start of a new week."""
    label = str((us_now or {}).get("label") or "This week so far")
    us_tot = (us_now or {}).get("totals") or {}
    au_tot = (au_now or {}).get("totals") or {}
    items = [
        _insight_item(
            (
                f"{html.escape(label)}. Ads so far: US "
                f"{html.escape(money(us_tot.get('cost_usd'), 'USD'))} · "
                f"{html.escape(num(us_tot.get('clicks')))} clicks · "
                f"AU {html.escape(money(au_tot.get('cost_usd'), 'AUD'))} · "
                f"{html.escape(num(au_tot.get('clicks')))} clicks."
            ),
            "Monday is a clean start. Cheyenne and Holly updates are not in yet — cost / enquiry stays not yet on the cards.",
            "Let the week fill in before reacting. Same-weekday compare on Ads is the early signal.",
            "Partial day in the US. Australia may be further along on the clock.",
        ),
        _insight_item(
            (
                f"Frozen tab: {html.escape(SCOREBOARD_WEEK_LABEL)} is the finished report. "
                "This tab is live ops only — do not mix last week’s enquiry totals with today’s partial spend."
            ),
            "Compare full weeks on the frozen tab. Use same-weekday Ads compare here while the week is still young.",
            "Switch to Aug 17–23 frozen for the scoreboard Braden and sales ops should reference.",
            "Sales-ops counts refresh from Cheyenne/Holly email, not from Zoho row totals on the card face.",
        ),
    ]
    return (
        '<section class="week-close" id="week-start-insights" aria-label="New week readout">'
        '<div class="ga4-insight">'
        "<h3>This week · early read</h3>"
        f"<ul>{''.join(items)}</ul>"
        "</div>"
        "</section>"
    )


def _ga4_insight_html(
    us: dict,
    us_p: dict,
    au: dict,
    au_p: dict,
    *,
    us_prior_ok: bool,
    au_prior_ok: bool,
    au_rate_prior: dict | None = None,
    us_land: list | None = None,
    au_land: list | None = None,
    midweek: bool = False,
    frozen_week_label: str | None = None,
) -> str:
    """Frozen-week GA4 read only. No cohort-retention claims."""
    week_label = frozen_week_label or SCOREBOARD_WEEK_LABEL
    lines: list[str] = []

    us_sess, us_sess_p = _fnum(us, "sessions"), _fnum(us_p, "sessions")
    us_stay, us_stay_p = _fnum(us, "engagement_rate_pct"), _fnum(us_p, "engagement_rate_pct")
    us_time, us_time_p = _fnum(us, "avg_session_seconds"), _fnum(us_p, "avg_session_seconds")
    if us_prior_ok and us_sess is not None:
        stay_bit = ""
        if us_stay is not None and us_stay_p is not None:
            stay_bit = (
                f" Stayed {html.escape(pct(us_stay))} vs {html.escape(pct(us_stay_p))}."
            )
        time_bit = ""
        if us_time and us_time_p:
            time_bit = (
                f" Time on site {_secs_plain(us_time)} vs {_secs_plain(us_time_p)}."
            )
        lines.append(
            _insight_item(
                (
                    f"US sessions {html.escape(num(us_sess))} vs {html.escape(num(us_sess_p))} "
                    f"the week before.{stay_bit}{time_bit}"
                ),
                f"This is the locked {html.escape(week_label)} baseline, not this week’s live scoreboard.",
                "Use it to compare later weeks. Do not treat launch week as the quality bar.",
                "Users vs sessions is not cohort retention. AU tags only started Aug 12.",
            )
        )

    au_sess = _fnum(au, "sessions")
    au_stay = _fnum(au, "engagement_rate_pct")
    if au_sess is not None:
        extra = f" Stayed {html.escape(pct(au_stay))}." if au_stay is not None else ""
        lines.append(
            _insight_item(
                f"AU had {html.escape(num(au_sess))} tagged sessions this frozen week.{extra}",
                "First tagged Australia week. There is no fair prior week to compare.",
                "Read AU volume here as a starting point, not a trend.",
                "Tags started Aug 12, so Monday–Tuesday of that week are missing.",
            )
        )

    us_top = _ga4_lp_pick(us_land, 1)
    au_top = _ga4_lp_pick(au_land, 1)
    if us_top or au_top:
        bits = []
        if us_top:
            p = us_top[0]
            bits.append(
                f"{html.escape(str(p.get('path') or '/us'))} "
                f"({html.escape(num(p.get('sessions')))} US)"
            )
        if au_top:
            p = au_top[0]
            bits.append(
                f"{html.escape(str(p.get('path') or '/au'))} "
                f"({html.escape(num(p.get('sessions')))} AU)"
            )
        lines.append(
            _insight_item(
                "Most visits opened the hub — " + " · ".join(bits) + ".",
                "Role pages with enough sessions are the CRO pile. Tiny samples are not winners.",
                "See this week’s live table on the This week so far tab.",
                f"These session counts are the frozen {html.escape(week_label)} baseline.",
            )
        )

    if not lines:
        return ""
    return (
        '<div class="ga4-insight">'
        "<h3>Insights</h3>"
        f"<ul>{''.join(lines[:3])}</ul>"
        "</div>"
    )


def _ga4_bottom_html(ga4: dict | None, *, frozen_week_label: str | None = None) -> str:
    """Our GA4 — this week vs last week. No old-agency property."""
    week_label = frozen_week_label or SCOREBOARD_WEEK_LABEL
    if not ga4:
        return ""
    us = ga4.get("totals_last_7_days") or {}
    au = (ga4.get("au") or {}).get("totals_last_7_days") or {}
    us_p = ga4.get("totals_prior_7_days") or {}
    au_p = (ga4.get("au") or {}).get("totals_prior_7_days") or {}
    us_paid, _ = _ga4_paid_sessions(ga4, "US")
    au_paid, _ = _ga4_paid_sessions(ga4, "AU")
    us_paid_p = ga4.get("paid_search_sessions_prior")
    au_paid_p = (ga4.get("au") or {}).get("paid_search_sessions_prior")
    us_ty = (ga4.get("path_kind_sessions") or {}).get("thank_you")
    if us_ty is None:
        us_ty = (ga4.get("landing_compare") or {}).get("thank_you_sessions")
    au_ty = (ga4.get("au") or {}).get("thank_you_sessions")
    us_dev = {str(r.get("device")): r.get("sessions") for r in (ga4.get("devices") or [])}
    au_block = ga4.get("au") or {}
    au_dev = {str(r.get("device")): r.get("sessions") for r in (au_block.get("devices") or [])}

    au_prior_ok = int(au_p.get("sessions") or 0) > 0
    us_prior_ok = int(us_p.get("sessions") or 0) > 0
    au_empty = _ga4_no_prior_sub("first tagged week")

    def _sub(
        now: Any,
        prior: Any,
        *,
        kind: str = "count",
        higher_is_better: bool = True,
        ok: bool,
    ) -> str:
        return _ga4_wow_sub(
            now,
            prior,
            kind=kind,
            higher_is_better=higher_is_better,
            prior_ok=ok,
        )

    def _au_sub(
        now_v: Any,
        prior_v: Any,
        *,
        kind: str = "count",
        higher_is_better: bool = True,
    ) -> str:
        if au_prior_ok:
            return _sub(now_v, prior_v, kind=kind, higher_is_better=higher_is_better, ok=True)
        return au_empty

    boxes = "".join(
        [
            _ga4_now_box(
                "Sessions",
                num(us.get("sessions")),
                num(au.get("sessions")),
                _sub(us.get("sessions"), us_p.get("sessions"), ok=us_prior_ok),
                _au_sub(au.get("sessions"), au_p.get("sessions")),
            ),
            _ga4_now_box(
                "Users",
                num(us.get("users")),
                num(au.get("users")),
                _sub(us.get("users"), us_p.get("users"), ok=us_prior_ok),
                _au_sub(au.get("users"), au_p.get("users")),
            ),
            _ga4_now_box(
                "Stayed",
                pct(us.get("engagement_rate_pct")),
                pct(au.get("engagement_rate_pct")),
                _sub(
                    us.get("engagement_rate_pct"),
                    us_p.get("engagement_rate_pct"),
                    kind="rate",
                    ok=us_prior_ok,
                ),
                _au_sub(
                    au.get("engagement_rate_pct"),
                    au_p.get("engagement_rate_pct"),
                    kind="rate",
                ),
            ),
            _ga4_now_box(
                "Bounce",
                pct(us.get("bounce_rate_pct")),
                pct(au.get("bounce_rate_pct")),
                _sub(
                    us.get("bounce_rate_pct"),
                    us_p.get("bounce_rate_pct"),
                    kind="rate",
                    higher_is_better=False,
                    ok=us_prior_ok,
                ),
                _au_sub(
                    au.get("bounce_rate_pct"),
                    au_p.get("bounce_rate_pct"),
                    kind="rate",
                    higher_is_better=False,
                ),
            ),
            _ga4_now_box(
                "Paid search",
                num(us_paid),
                num(au_paid),
                _sub(us_paid, us_paid_p, ok=us_prior_ok),
                _au_sub(au_paid, au_paid_p),
            ),
            _ga4_now_box("Thank-you", num(us_ty), num(au_ty)),
            _ga4_now_box("Mobile", num(us_dev.get("mobile")), num(au_dev.get("mobile"))),
            _ga4_now_box("Desktop", num(us_dev.get("desktop")), num(au_dev.get("desktop"))),
            _ga4_now_box(
                "Time on site",
                _secs_plain(us.get("avg_session_seconds")),
                _secs_plain(au.get("avg_session_seconds")),
                _sub(
                    us.get("avg_session_seconds"),
                    us_p.get("avg_session_seconds"),
                    kind="duration",
                    ok=us_prior_ok,
                ),
                _au_sub(
                    au.get("avg_session_seconds"),
                    au_p.get("avg_session_seconds"),
                    kind="duration",
                ),
            ),
        ]
    )
    prior_win = html.escape(str(ga4.get("window_prior") or "Aug 3–9"))
    us_land = ga4.get("top_landing_pages") or []
    au_land = au_block.get("top_landing_pages") or []
    insight = _ga4_insight_html(
        us,
        us_p,
        au,
        au_p,
        us_prior_ok=us_prior_ok,
        au_prior_ok=au_prior_ok,
        us_land=us_land,
        au_land=au_land,
        midweek=False,
        frozen_week_label=week_label,
    )
    lp = _ga4_lp_table(us_land, au_land, row_prefix="lp-frozen")
    return f"""
      <section class="ga4-now" id="ga4" aria-label="Google Analytics">
        <div class="sec-hd">
          <h2>Google Analytics</h2>
          <p class="sec-meta">{html.escape(_ga4_window_plain(ga4))} · frozen week · source GA4 · AU tags started Aug 12</p>
        </div>
        <div class="legacy-grid ga4-grid">{boxes}</div>
        {lp}
        {insight}
        <p class="mute ga4-foot">Last week = {prior_win}. That week is launch / partial (US ads ~Aug 6, AU tags ~Aug 12). AU has no prior week to compare — first tagged week. Month-over-month later, once we have more than one week.</p>
      </section>
"""


def _bar_row(label: str, value: float | None, max_v: float, unit: str = "%") -> str:
    if value is None or max_v <= 0:
        w = 0
        shown = "—"
    else:
        w = max(0, min(100, 100.0 * float(value) / max_v))
        shown = f"{float(value):.1f}{unit}" if unit == "%" else f"{float(value):,.1f}"
    return (
        f'<div class="bar-row"><span class="bl">{html.escape(label)}</span>'
        f'<span class="track"><span class="fill" style="width:{w:.1f}%"></span></span>'
        f'<span class="bv num">{html.escape(shown)}</span></div>'
    )


def _lift_label(stage_n: Any, base_n: Any, *, higher_is_better: bool = True) -> tuple[str, str]:
    """Return (css_class, short label) for Stage 1 vs baseline volume."""
    try:
        s = float(stage_n)
        b = float(base_n)
    except (TypeError, ValueError):
        return "delta-flat", "—"
    if b == 0:
        if s > 0:
            return ("delta-good" if higher_is_better else "delta-bad"), "new"
        return "delta-flat", "flat"
    change = 100.0 * (s - b) / b
    if abs(change) < 0.5:
        return "delta-flat", "flat"
    sign = "+" if change > 0 else ""
    up = change > 0
    good = up if higher_is_better else (not up)
    css = "delta-good" if good else "delta-bad"
    return css, f"{sign}{change:.0f}%"


def _halo_metric_card(
    title: str,
    stage_n: Any,
    *,
    sub: str,
) -> str:
    return f"""          <div class="kpi kpi-halo">
            <span class="k">{html.escape(title)}</span>
            <span class="v num">{html.escape(num(stage_n))}</span>
            <span class="sub">{html.escape(sub)}</span>
          </div>"""


def _zoho_status(block: dict, name: str) -> int | None:
    raw = (block.get("by_status") or {}).get(name)
    if raw is None or raw == "":
        return None
    return int(raw)


def _halo_section(
    halo: dict | None,
    zoho_week: dict | None,
    week_label: str,
    *,
    us_spend: Any = None,
    au_spend: Any = None,
) -> str:
    """Zoho census for the same sales week — not Cheyenne/Holly, not added."""
    if not halo and not zoho_week:
        return ""
    s1 = (halo or {}).get("stage1") or {}
    base = (halo or {}).get("baseline") or {}
    se = s1.get("sales_enquiries") or {}
    jo = s1.get("job_orders") or {}
    bse = base.get("sales_enquiries") or {}
    bjo = base.get("job_orders") or {}
    usa = (zoho_week or {}).get("usa") or {}
    au = (zoho_week or {}).get("au") or {}
    if zoho_week:
        frame = f"{week_label} · every row Zoho created this week"
    else:
        usa = {"n": se.get("usa"), "discovery_scheduled": s1.get("discovery_scheduled")}
        au = {"n": se.get("au")}
        frame = f"{s1.get('start') or '?'} → {s1.get('end') or '?'} · every row Zoho created"
    july = f"""
        <details class="calc-how">
          <summary>July comparison (old)</summary>
          <div class="bd">
            <p class="note">July is older bookkeeping — not a fair before/after.</p>
            <table class="cmp halo-cmp">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th class="num">This flight</th>
                  <th class="num">July</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Enquiries</td>
                  <td class="num">{html.escape(num(se.get("total")))}</td>
                  <td class="num mute">{html.escape(num(bse.get("total")))}</td>
                </tr>
                <tr>
                  <td>Job orders</td>
                  <td class="num">{html.escape(num(jo.get("total")))}</td>
                  <td class="num mute">{html.escape(num(bjo.get("total")))}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>"""
    return _halo_scoreboard(
        section_id="crm-activity",
        title="Zoho this week",
        aria="Zoho this week",
        meta=frame,
        usa=usa,
        au=au,
        us_spend=us_spend,
        au_spend=au_spend,
        foot=(
            "Same words as the cost tiles: enquiry · discovery · job order · placement. "
            "Census only — do not add to Cheyenne/Holly. "
            "Job placements live on the Placements module — Ash is wiring that. Holly named 4 last week; those stay on the AU card."
        ),
        extra_html=july,
    )


def _sum_by_date(by_date: dict, start: str, end: str) -> dict[str, Any]:
    """Sum Stage 1 daily Ads rows for an inclusive date window. No extra API call."""
    spend = 0.0
    impr = 0.0
    clicks = 0.0
    conv = 0.0
    conv_seen = False
    if not start or not end or not by_date:
        return {}
    for day in _iso_dates_inclusive(start, end):
        row = by_date.get(day) or {}
        spend += float(row.get("cost_usd") or 0)
        impr += float(row.get("impressions") or 0)
        clicks += float(row.get("clicks") or 0)
        if row.get("conversions") is not None:
            conv_seen = True
            conv += float(row.get("conversions") or 0)
    return {
        "cost_usd": round(spend, 2),
        "impressions": int(impr),
        "clicks": int(clicks),
        "ctr_pct": round(100.0 * clicks / impr, 1) if impr else None,
        "avg_cpc_usd": round(spend / clicks, 2) if clicks else None,
        "conversions": conv if conv_seen else None,
    }


def _ads_for_sales_week(exec_data: dict, market: str, ops: dict) -> dict[str, Any]:
    """Ads KPIs for the same dates as the cost tiles (sales-ops week)."""
    perf_key = "performance_us" if market == "US" else "performance_au"
    perf = exec_data.get(perf_key) or {}
    by_date = perf.get("by_date_stage1") or perf.get("by_date") or {}
    start = str(ops.get("window_start") or "")[:10]
    end = str(ops.get("window_end") or "")[:10]
    summed = _sum_by_date(by_date, start, end)
    cost = ops.get("spend_usd")
    clicks = ops.get("clicks")
    impr = ops.get("impressions")
    cpc = ops.get("avg_cpc_usd")
    if cost is not None:
        summed["cost_usd"] = cost
    if clicks is not None:
        summed["clicks"] = clicks
    if impr is not None:
        summed["impressions"] = impr
        if clicks:
            summed["ctr_pct"] = round(100.0 * float(clicks) / float(impr), 1)
    if cpc is not None:
        summed["avg_cpc_usd"] = cpc
    return summed


def _ga4_event_count(ga4: dict | None, name: str) -> int | None:
    """Return count only when the event appears in the snapshot. Missing ≠ 0."""
    if not ga4:
        return None
    buckets = [
        ga4.get("events_interesting"),
        ga4.get("top_events"),
        ((ga4.get("au") or {}).get("events_interesting")),
        ((ga4.get("au") or {}).get("top_events")),
    ]
    for bucket in buckets:
        for row in bucket or []:
            if row.get("event") == name:
                return int(row.get("event_count") or 0)
    return None


def _ga4_is_sales_week(ga4: dict | None) -> bool:
    raw = str((ga4 or {}).get("window") or "")
    return SCOREBOARD_WEEK_START in raw and SCOREBOARD_WEEK_END in raw


def _ga4_paid_sessions(ga4: dict | None, market: str) -> tuple[Any, str]:
    """Paid Search sessions from GA4. Same sales week when the snapshot is locked."""
    if not ga4:
        return None, "GA4 snapshot missing"
    same = _ga4_is_sales_week(ga4)
    join = "same sales week · not joined by click ID" if same else "not the sales week"
    if market == "AU":
        au = ga4.get("au") or {}
        n = au.get("paid_search_sessions")
        win = au.get("window") or "rolling 7d"
        return n, f"GA4 AU Paid Search · {win} — {join}"
    for ch in ga4.get("channels") or []:
        if ch.get("channel") == "Paid Search":
            win = ga4.get("window") or "rolling 7d"
            return ch.get("sessions"), f"GA4 US Paid Search · {win} — {join}"
    return None, "Paid Search channel not in GA4 snapshot"


def _fn_step(
    label: str,
    value: str,
    kind: str,
    title: str,
    *,
    directional: bool = False,
) -> str:
    cls = "fn-dir" if directional or kind in ("Directional", "Incomplete", "Unavailable") else "fn-ok"
    if kind == "Unavailable":
        cls = "fn-miss"
    elif kind == "Incomplete":
        cls = "fn-inc"
    elif kind == "Directional":
        cls = "fn-dir"
    return (
        f'<li class="{cls}">'
        f'<span class="fn-k">{html.escape(label)}</span>'
        f'<span class="fn-n num">{html.escape(value)}</span>'
        f"{_conf_pill(kind, title)}"
        f"</li>"
    )


def _funnel_html(market: str, ads: dict, ops: dict, ga4: dict | None) -> str:
    """Compact sequence. Do not invent step rates across unjoined systems."""
    clicks = ads.get("clicks")
    paid_sess, paid_note = _ga4_paid_sessions(ga4, market)
    form_start = _ga4_event_count(ga4, "form_start") if market == "US" else None
    ty = None
    if market == "US" and ga4:
        ty = (ga4.get("path_kind_sessions") or {}).get("thank_you")
        if ty is None:
            ty = (ga4.get("landing_compare") or {}).get("thank_you_sessions")
    elif market == "AU" and ga4:
        ty = (ga4.get("au") or {}).get("thank_you_sessions")

    missing_role = "Not currently measured"
    missing_role_ev = "Missing GA4 event: employer_gate_selected (role / hiring-brief start)"
    missing_contact = "Not currently measured"
    missing_contact_ev = "Missing GA4 event for contact-information step"
    missing_place = "Not currently measured"
    missing_place_ev = "Placement is not in the sales-ops week or CRM snapshot"

    enq = ops.get("enquiries")
    if market == "US":
        qual = ops.get("sales_calls_completed")
        qual_label = "Completed calls"
        jo = None
        jo_note = "Cheyenne did not name a job order this week"
    else:
        census = ops.get("zoho_census") or {}
        qual = census.get("discovery_scheduled")
        qual_label = "Discovery scheduled"
        jo = ops.get("job_orders_total")
        jo_note = "Holly’s labeled job orders · same week · not last-click paid"

    steps = [
        _fn_step(
            "Ads clicks",
            num(clicks),
            "Verified",
            "Google Ads clicks · same sales week",
        ),
        _fn_step(
            "Paid LP sessions",
            num(paid_sess) if paid_sess is not None else "—",
            "Incomplete" if paid_sess is not None else "Unavailable",
            paid_note,
        ),
        _fn_step("Role / hiring brief", missing_role, "Unavailable", missing_role_ev),
        _fn_step("Contact step", missing_contact, "Unavailable", missing_contact_ev),
        _fn_step(
            "Form starts",
            num(form_start) if form_start is not None else "—",
            "Incomplete" if form_start is not None else "Unavailable",
            "GA4 form_start · same sales week · diagnostic, not a qualified lead"
            if form_start is not None
            else "form_start not in this market’s GA4 snapshot",
        ),
        _fn_step(
            "Thank-you sessions",
            num(ty) if ty is not None else "—",
            "Incomplete" if ty is not None else "Unavailable",
            "GA4 thank-you page sessions — not Google Ads conversions",
        ),
        _fn_step(
            "Employer enquiries",
            num(enq) if enq is not None else "—",
            "Directional" if enq is not None else "Unavailable",
            "Same-week sales/CRM count — not fully attributed to Google Ads",
            directional=True,
        ),
        _fn_step(
            qual_label,
            num(qual) if qual is not None else "—",
            "Directional" if qual is not None else "Unavailable",
            "Same-week business outcome — not a Google Ads conversion",
            directional=True,
        ),
        _fn_step(
            "Job order",
            num(jo) if jo is not None else "—",
            "Directional" if jo is not None else "Unavailable",
            jo_note,
            directional=True,
        ),
        _fn_step("Placement", missing_place, "Unavailable", missing_place_ev),
    ]
    return (
        '<p class="funnel-k">Funnel this week</p>'
        '<ol class="funnel" aria-label="Acquisition sequence">'
        + "".join(steps)
        + "</ol>"
        '<p class="mute funnel-note">Ads clicks and employer outcomes share the sales week. '
        "GA4 steps use the same sales week and are not joined by click ID — no step-to-step rate.</p>"
    )


def _crm_readiness_html(zoho_week: dict | None = None) -> str:
    """Compact operational checklist. Field names existing ≠ Confirmed."""
    week_n = (zoho_week or {}).get("leads_in_window")
    usa = (zoho_week or {}).get("usa") or {}
    au = (zoho_week or {}).get("au") or {}
    try:
        gclid_n = int(usa.get("with_utm_gclid") or 0) + int(au.get("with_utm_gclid") or 0)
    except (TypeError, ValueError):
        gclid_n = 0
    if week_n is not None:
        gclid_ev = (
            f"Dictionary has utm_gclid. This week: {gclid_n} of {week_n} Zoho rows "
            "store a click ID."
        )
    else:
        gclid_ev = (
            "Dictionary has utm_gclid. New Zoho rows are not storing a click ID."
        )
    rows = [
        ("Destination CRM module", "Needs review", "Live CRM is WordPress + Zapier + humans. .app forms email us@ / apac@ — not writing to Zoho."),
        ("Employer vs job-seeker classification", "Needs review", "Cheyenne labels looking-for-work / PH job-seeker in email. Form gate exists in spec; not proven on every CRM row."),
        ("Persistent GCLID field", "Missing", gclid_ev),
        ("Persistent GBRAID / WBRAID", "Missing", "No Zoho fields. Parked until writes turn on."),
        ("UTM fields", "Not tested", "utm_source / medium / campaign exist in the dictionary. Stage 1 Zoho rows are mostly blank."),
        ("Original landing page", "Not tested", "Mapped to Referring_URL in the draft. Not proven on Stage 1 rows."),
        ("Lead-created timestamp", "Confirmed", "Zoho Created_Time is what the halo census uses."),
        ("Deduplication rule", "Missing", "VC_Submission_ID does not exist yet."),
        ("Lifecycle stage definitions", "Needs review", "Zoho statuses exist (Discovery Scheduled, Job Order Submitted, etc.). Not a locked Stage 1 contract."),
        ("Sales ownership", "Confirmed", "Cheyenne Gichana = US. Holly Wallace = APAC / AU."),
        ("Qualified-lead definition", "Needs review", "No single documented qualified-employer definition on this scoreboard."),
        ("Job-order definition", "Needs review", "AU card uses Holly’s 6 total JO this week (3 new / 1 returning / 2 replacement). US Cost / JO uses Zoho census 1 JO; Cheyenne did not name a JO."),
        ("Placement definition", "Needs review", "AU this week: Holly named 4 placements. Not a locked Stage 1 definition."),
        ("Offline conversion action mapping", "Missing", "Deferred during cold start. Do not import CRM outcomes into Ads yet."),
        ("Click-ID retention tested", "Not tested", "0 gclid on Stage 1 Sales Enquiries."),
        ("Google Ads import tested", "Not tested", "Offline import deferred. Not a green check because a Zapier action exists."),
        ("Legacy Zapier uploads audited", "Needs review", "Known inflated / thin JO upload vs real CRM job orders. Not a complete audit."),
        ("Documentation and owner assigned", "Needs review", "Field-map draft is parked. Writes remain OFF."),
    ]
    lis = []
    for item, status, note in rows:
        css = {
            "Confirmed": "st-ok",
            "Needs review": "st-rev",
            "Missing": "st-miss",
            "Not tested": "st-test",
        }.get(status, "st-rev")
        lis.append(
            "<tr>"
            f"<td>{html.escape(item)}</td>"
            f'<td class="{css}">{html.escape(status)}</td>'
            f'<td class="mute">{html.escape(note)}</td>'
            "</tr>"
        )
    return f"""
      <details class="ev" id="crm-readiness">
        <summary>CRM setup</summary>
        <div class="bd">
          <p class="mute">A named Zoho field is not the same as done.</p>
          <table class="ev-t crm-ready">
            <thead><tr><th>Check</th><th>Status</th><th>Evidence</th></tr></thead>
            <tbody>
              {"".join(lis)}
            </tbody>
          </table>
        </div>
      </details>"""


def _exec_summary_html(us_ops: dict, au_ops: dict, us_ads: dict, au_ads: dict) -> str:
    """At most three plain-English observations."""
    us_spend = money(us_ads.get("cost_usd"), "USD")
    au_spend = money(au_ads.get("cost_usd"), "AUD")
    us_enq = num(us_ops.get("enquiries"))
    au_enq = num(au_ops.get("enquiries"))
    us_calls = num(us_ops.get("sales_calls_completed"))
    au_jo = num(au_ops.get("job_orders_total") or au_ops.get("job_order_submitted"))
    items = [
        (
            f"First complete Stage 1 sales week (Mon–Sun): US {html.escape(us_spend)} and "
            f"AU {html.escape(au_spend)} on Exact / Max Clicks. This is the operational baseline — "
            "not a comparison to the old agency period."
        ),
        (
            "Landing-page micro-steps (role selected, hiring brief, contact step) are not currently "
            "measured in GA4. form_start and thank-you page sessions are diagnostic only — not qualified leads."
        ),
        (
            f"Employer activity the same week is directional: US {html.escape(us_enq)} enquiries / "
            f"{html.escape(us_calls)} completed calls (Cheyenne) and AU {html.escape(au_enq)} enquiries / "
            f"{html.escape(au_jo)} job orders (Holly). 0 click IDs. Do not add email + Zoho. Stay on Max Clicks."
        ),
    ]
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="exec-sum">{lis}</ul>'


def _week_heading(ops: dict) -> str:
    return html.escape(str(ops.get("label") or SCOREBOARD_WEEK_LABEL))


def _how_we_count_html(*, anchor: bool = False) -> str:
    """Quiet one-liner. Same copy on both week views. Anchor only on the default view."""
    aid = ' id="how-we-count"' if anchor else ""
    return (
        f'      <p class="how-count"{aid}>'
        "<strong>How we count.</strong> "
        "Qualified employer is the score. A form plus a booking by the same person is "
        "one lead, two funnel steps — not two people. Ads conversion totals are not the count. "
        '<span class="cats">Qualified · Not-a-Fit · Junk · Test</span> '
        '<span class="sample">Paid through 18 Aug: US 1 qualified + 1 not-a-fit · AU 1 qualified + 2 junk. '
        '<a href="aug18-conversions.html">Aug 18</a>.</span>'
        "</p>\n"
    )


def _week_notes_html(
    *,
    asof_line: str,
    fresh_id: str,
    fresh: str,
    how_anchor: bool = False,
) -> str:
    """Method / freshness — bottom of the week view, not the first screen."""
    return (
        '      <div class="week-notes">\n'
        f'        <p class="asof">{html.escape(asof_line)}</p>\n'
        f"{_how_we_count_html(anchor=how_anchor)}"
        f'        <p class="data-fresh" id="{html.escape(fresh_id)}">{fresh}</p>\n'
        "      </div>\n"
    )


def _sales_section(inner: str, *, section_id: str, meta: str) -> str:
    return (
        f'      <section class="baseline week-sales" id="{html.escape(section_id)}" aria-label="Sales">\n'
        '        <div class="sec-hd">\n'
        "          <h2>Sales</h2>\n"
        f'          <p class="sec-meta">{html.escape(meta)}</p>\n'
        "        </div>\n"
        f"{inner}\n"
        "      </section>\n"
    )


def _legacy_section(inner: str, *, section_id: str, meta: str) -> str:
    return (
        f'      <section class="baseline" id="{html.escape(section_id)}" aria-label="Legacy agency comparison">\n'
        '        <div class="sec-hd">\n'
        "          <h2>Legacy agency comparison</h2>\n"
        f'          <p class="sec-meta">{html.escape(meta)}</p>\n'
        "        </div>\n"
        f"{inner}\n"
        "      </section>\n"
    )


def _collapsed_zoho_html(
    halo: dict | None,
    zoho_week: dict | None,
    week_label: str,
    *,
    us_spend: Any = None,
    au_spend: Any = None,
) -> str:
    """Off the first screen. Not a second scoreboard vs Cheyenne/Holly."""
    inner = _halo_section(
        halo, zoho_week, week_label, us_spend=us_spend, au_spend=au_spend
    )
    if not inner.strip():
        return ""
    return (
        '      <details class="zoho-extra" id="zoho-census-extra">\n'
        "        <summary>Zoho census (all-source · not the scoreboard)</summary>\n"
        f'        <div class="bd">\n{inner}\n        </div>\n'
        "      </details>\n"
    )


def _frozen_week_panel_html(
    *,
    week_label: str,
    cpl: dict,
    cpl_au: dict,
    us_week: dict,
    au_week: dict,
    us_cost: str,
    us_cost_foot: str,
    au_cost: str,
    au_cost_foot: str,
    us_prior_7: dict | None,
    au_prior_7: dict | None,
    frozen_sales: str,
    frozen_ads: str,
    ga4_html: str,
    frozen_fresh: str,
    fresh_id: str,
    us_spend_id: str,
    au_spend_id: str,
    market_us_id: str,
    market_au_id: str,
    sales_section_id: str,
    ads_section_id: str,
    core_us: dict,
    roles_us: dict,
    core_au: dict,
    roles_au: dict,
    crm_ready: str = "",
    zoho_collapsed: str = "",
    close_insights: str = "",
) -> str:
    """One locked Mon–Sun scoreboard panel (US + AU + sales + legacy + GA4)."""
    return (
        f"""      <section class="mkt-block us" id="{html.escape(market_us_id)}" aria-label="United States">
        <div class="mkt-hd">
          <h2>United States</h2>
          <p class="bud">Core ${(core_us.get("daily_budget_usd") or 150):.0f} + Roles ${(roles_us.get("daily_budget_usd") or 100):.0f}/day · Exact/Phrase · Max Clicks</p>
        </div>
        <div class="period week-group">
          <h3>{html.escape(week_label)}</h3>
          <div class="kpi-row week-costs">
          {us_cost}
          </div>
          <div class="kpi-row week-ads">
          {_kpi_cards(us_week, "USD", spend_id=us_spend_id, prior=us_prior_7)}
          </div>
          {us_cost_foot}
        </div>
      </section>
"""
        + f"""      <section class="mkt-block au" id="{html.escape(market_au_id)}" aria-label="Australia">
        <div class="mkt-hd">
          <h2>Australia</h2>
          <p class="bud">Core A${(core_au.get("daily_budget_usd") or 75):.0f} + Roles A${(roles_au.get("daily_budget_usd") or 50):.0f}/day</p>
        </div>
        <div class="period week-group">
          <h3>{html.escape(week_label)}</h3>
          <div class="kpi-row week-costs">
          {au_cost}
          </div>
          <div class="kpi-row week-ads">
          {_kpi_cards(au_week, "AUD", spend_id=au_spend_id, prior=au_prior_7)}
          </div>
          {au_cost_foot}
        </div>
      </section>
"""
        + _sales_section(
            frozen_sales,
            section_id=sales_section_id,
            meta="This week vs their typical 7-day week",
        )
        + _legacy_section(
            frozen_ads,
            section_id=ads_section_id,
            meta="This week vs their typical 7-day week",
        )
        + ga4_html
        + _week_notes_html(
            asof_line=f"{week_label} · frozen · US $ · AU A$",
            fresh_id=fresh_id,
            fresh=frozen_fresh,
        )
        + crm_ready
        + zoho_collapsed
        + close_insights
    )


def _next_watch_html(market: str) -> str:
    if market == "US":
        text = (
            "Keep collecting this clean baseline. Review search terms only for defensible negatives. "
            "Do not switch to conversion-based bidding. CRM click-ID persistence is still missing."
        )
    else:
        text = (
            "GTM/GA4 went live ~12 Aug — finish diagnostic event coverage. "
            "Keep collecting the first clean baseline. Do not switch to conversion-based bidding."
        )
    return f'<p class="why"><strong>Watch next week:</strong> {html.escape(text)}</p>'


def bake_executive(
    exec_data: dict,
    is_data: dict | None,
    ga4: dict | None,
    recovery: dict | None,
    halo: dict | None = None,
    zoho_week: dict | None = None,
) -> str:
    us_perf = exec_data.get("performance_us") or {}
    au_perf = exec_data.get("performance_au") or {}
    us7 = stage1(us_perf)
    au7 = stage1(au_perf)
    us_today = us_perf.get("totals_focus_day") or {}
    au_today = au_perf.get("totals_focus_day") or {}
    focus = us_perf.get("focus_day") or au_perf.get("focus_day") or "today"
    cpl = exec_data.get("sales_ops_us") or exec_data.get("early_cpl_us") or {}
    prior_cpl = exec_data.get("early_cpl_us") or {}
    asof = (exec_data.get("generated_at_utc") or "").replace("T", " ")[:16]
    baseline = agency_baseline(recovery)

    us_camps = {
        c.get("name"): c
        for c in ((is_data or {}).get("performance_us") or {}).get("campaigns") or []
    }
    au_camps = {
        c.get("name"): c
        for c in ((is_data or {}).get("performance_au") or {}).get("campaigns") or []
    }
    windows = (is_data or {}).get("windows") or {}
    if not windows:
        windows = {
            "US": ((is_data or {}).get("performance_us") or {}).get("windows") or {},
            "AU": ((is_data or {}).get("performance_au") or {}).get("windows") or {},
        }

    core_us = us_camps.get("VC_US_S_CORE") or {}
    roles_us = us_camps.get("VC_US_S_ROLES") or {}
    core_au = au_camps.get("VC_AU_S_CORE") or {}
    roles_au = au_camps.get("VC_AU_S_ROLES") or {}

    us_path = ""
    if ga4:
        top = ga4.get("top_landing_pages") or []
        us_home = next((p for p in top if p.get("path") == "/us"), None)
        if us_home:
            us_path = f" · mostly <code>/us</code> ({num(us_home.get('sessions'))} sess)"

    cpl_au = exec_data.get("sales_ops_au") or exec_data.get("early_cpl_au") or {}
    us_week = _ads_for_sales_week(exec_data, "US", cpl)
    au_week = _ads_for_sales_week(exec_data, "AU", cpl_au)
    ga4_asof = ((ga4 or {}).get("generated_at_utc") or "")[:16].replace("T", " ")
    is_asof = ((is_data or {}).get("generated_at_utc") or "")[:16].replace("T", " ")
    zoho_asof = str(
        ((cpl.get("zoho_census") or {}).get("pinged_utc")
         or (cpl_au.get("zoho_census") or {}).get("pinged_utc")
         or "")
    )[:16].replace("T", " ")
    exec_sum = ""
    us_funnel = ""
    au_funnel = _funnel_html("AU", au_week, cpl_au, ga4)
    crm_ready = _crm_readiness_html(zoho_week)

    def _source_mix_html(data: dict) -> str:
        sources = data.get("sources") or []
        if not sources:
            return ""
        chips: list[str] = []
        for s in sources:
            chips.append(
                "<span class='src-chip'>"
                f"<span class='src-l'>{html.escape(str(s.get('label') or ''))}</span>"
                f"<span class='src-n num'>{html.escape(num(s.get('count')))}</span>"
                "</span>"
            )
        return (
            "<div class='src-chips' aria-label='Enquiry sources'>"
            "<span class='src-chips-k'>Sources</span>"
            f"{''.join(chips)}</div>"
        )

    def _zoho_census_html(data: dict, market: str) -> str:
        """Quiet CRM count under Cheyenne/Holly. Skip if Zoho is already the face."""
        if data.get("scoreboard") == "zoho":
            return ""
        census = data.get("zoho_census") or (data.get("attribution_watch") or {}).get("zoho") or {}
        if not census:
            return ""
        n_se = (
            census.get("au_sales_enquiries")
            if market == "AU"
            else census.get("usa_sales_enquiries")
        )
        if n_se is None:
            return ""
        n_disc = census.get("discovery_scheduled")
        n_jo = census.get("job_order_submitted")
        bits = [f"{html.escape(num(n_se))} rows"]
        if n_disc is not None and n_disc != "":
            bits.append(f"{html.escape(num(n_disc))} discovery")
        if n_jo is not None and n_jo != "":
            try:
                jo_n = int(n_jo)
            except (TypeError, ValueError):
                jo_n = None
            if jo_n is not None:
                jo_word = "job order" if jo_n == 1 else "job orders"
                bits.append(f"{html.escape(num(jo_n))} {jo_word}")
        if market == "AU" and data.get("job_orders_total") is not None:
            tail = (
                f"Holly’s {html.escape(num(data.get('job_orders_total')))} stays on the card. "
                "Do not add."
            )
        elif market == "US" and n_jo not in (None, ""):
            tail = "Wider net, not extra enquiries. Cost / job order uses this census JO."
        else:
            tail = "Wider net, not extra enquiries."
        return (
            f"<p class='mute zoho-census'>Zoho census, same dates: "
            f"{' · '.join(bits)}. {tail}</p>"
        )

    def _prior_cpl_html(prior: dict, cur: str) -> str:
        if not prior or prior.get("enquiries") is None:
            return ""
        cpl = prior.get("cost_per_enquiry_usd")
        if cpl is None:
            return ""
        return (
            f"<p class='mute prior-line'>Prior {html.escape(str(prior.get('label') or 'sample'))}: "
            f"{html.escape(money2(cpl, cur))} / enquiry "
            f"({html.escape(num(prior.get('enquiries')))}).</p>"
        )

    def _lead_cost_parts(
        market: str,
        data: dict,
        cur: str,
        ads_conv: Any,
        *,
        prior: dict | None = None,
    ) -> tuple[str, str]:
        """3 cost tiles (shared US/AU columns) + short footer. Ads KPIs sit in the row below."""
        holly_board = market == "AU" and data.get("scoreboard") == "holly"
        zoho_board = market == "AU" and data.get("scoreboard") == "zoho"
        enq = data.get("cost_per_enquiry_usd")
        booked = data.get("cost_per_sales_call_completed_usd")
        call_word = "sales call" if holly_board else "completed call"
        n_calls = data.get("sales_calls_completed")
        call_estimated = bool(data.get("call_proxy_estimated"))
        if booked is None:
            booked = data.get("cost_per_sales_call_booked_usd")
            call_word = "booked call"
            n_calls = data.get("sales_calls_booked")
        extra = ""
        if enq is not None:
            enq_v = money2(enq, cur)
            booked_v = money2(booked, cur) if booked is not None else "—"
            n_enq = data.get("enquiries", "?")
            if holly_board:
                jo_split = (
                    f"{html.escape(num(data.get('job_orders_total')))} job orders "
                    f"({html.escape(num(data.get('new_job_orders')))} new · "
                    f"{html.escape(num(data.get('returning_job_orders')))} returning · "
                    f"{html.escape(num(data.get('replacement_job_orders')))} replacement)"
                )
                quality = []
                if data.get("junk_leads") is not None:
                    quality.append(f"{data.get('junk_leads')} junk")
                if data.get("placements") is not None:
                    quality.append(f"{data.get('placements')} placements")
                quality_s = f" · {' · '.join(quality)}" if quality else ""
                note = (
                    f"{html.escape(num(n_enq))} enquiries · "
                    f"{html.escape(num(n_calls))} sales calls · {jo_split}"
                    f"{html.escape(quality_s)}."
                )
                extra = _zoho_census_html(data, market)
            elif zoho_board:
                note = (
                    f"{html.escape(num(n_enq))} enquiries · "
                    f"{html.escape(num(data.get('discovery_scheduled')))} discovery scheduled · "
                    f"{html.escape(num(data.get('job_order_submitted')))} job orders."
                )
            else:
                quality = []
                if data.get("looking_for_work") is not None:
                    quality.append(f"{data.get('looking_for_work')} looking for work")
                if data.get("not_a_fit") is not None:
                    quality.append(f"{data.get('not_a_fit')} not a fit")
                if data.get("philippines_job_seekers") is not None:
                    n_ph = data.get("philippines_job_seekers")
                    ph_word = "PH job-seeker" if n_ph == 1 else "PH job-seekers"
                    quality.append(f"{n_ph} {ph_word}")
                if data.get("sales_calls_booked"):
                    quality.append(
                        f"{data.get('sales_calls_booked')} weekend call booked"
                    )
                quality_s = f" · {' · '.join(quality)}" if quality else ""
                note = (
                    f"{n_enq} enquiries · {n_calls} {call_word}s"
                    f"{html.escape(quality_s)}."
                )
                extra = _source_mix_html(data) + _zoho_census_html(data, market)
                if prior and prior is not data:
                    extra += _prior_cpl_html(prior, cur)
        else:
            enq_v = "—"
            booked_v = money2(booked, cur) if booked is not None else "—"
            note = html.escape(
                str(
                    data.get("caveat")
                    or data.get("source")
                    or (
                        "Waiting on AU enquiries."
                        if market == "AU"
                        else "Waiting on Sales lead report"
                    )
                )
            )
            extra = _source_mix_html(data) + _zoho_census_html(data, market)
        call_k = "Cost / discovery"
        enq_est = enq is not None
        if holly_board:
            enq_tip = "Spend ÷ named sales leads from Holly. Not a Google Ads CPA."
            enq_sub_s = "named sales leads"
            call_tip = "Spend ÷ named sales calls from Holly. Not a Google Ads CPA."
            call_sub_s = "named sales calls"
        elif zoho_board:
            enq_tip = "Spend ÷ all Zoho rows during this period — not a Google Ads CPA."
            enq_sub_s = "all Zoho rows · not Ads CPA"
            call_tip = (
                "Spend ÷ Zoho Discovery Scheduled statuses this period — "
                "not a Google Ads CPA."
            )
            call_sub_s = "all Zoho rows · not Ads CPA"
        else:
            enq_tip = "Spend ÷ named microsite leads from sales. Not a Google Ads CPA."
            enq_sub_s = "named sales leads"
            call_tip = "Spend ÷ named completed calls from sales. Not a Google Ads CPA."
            call_sub_s = "named sales calls"
        call_sub = (
            f'<span class="sub">{html.escape(call_sub_s)}</span>'
            if booked is not None
            else '<span class="sub">&nbsp;</span>'
        )
        enq_sub = (
            f'<span class="sub">{html.escape(enq_sub_s)}</span>'
            if enq_est
            else '<span class="sub">&nbsp;</span>'
        )
        jo_cost = data.get("cost_per_job_order_usd")
        jo_src = data.get("cost_per_job_order_source")
        jo_tip = "Spend ÷ all Zoho rows during this period — not a Google Ads CPA."
        if jo_cost is not None and (zoho_board or holly_board or jo_src == "zoho_census"):
            jo_v = money2(jo_cost, cur)
            jo_sub = (
                '<span class="sub">Zoho census · not Ads CPA</span>'
                if jo_src == "zoho_census"
                else '<span class="sub">named sales · not Ads CPA</span>'
            )
        else:
            jo_v = "—"
            jo_sub = '<span class="sub">&nbsp;</span>'
            jo_tip = "No Job Order count for this cost tile."
        cards = (
            f'<div class="kpi kpi-cost"><span class="k" title="{html.escape(enq_tip)}">Cost / enquiry</span>'
            f'<span class="v num">{html.escape(enq_v)}</span>{enq_sub}</div>\n'
            f'          <div class="kpi kpi-cost"><span class="k" title="{html.escape(call_tip)}">{html.escape(call_k)}</span>'
            f'<span class="v num">{html.escape(booked_v)}</span>{call_sub}</div>\n'
            f'          <div class="kpi kpi-cost"><span class="k" title="{html.escape(jo_tip)}">Cost / job order</span>'
            f'<span class="v num">{html.escape(jo_v)}</span>{jo_sub}</div>'
        )
        footer = f'<p class="mkt-note mute">{note}</p>\n          {extra}'
        return cards, footer

    us_cost, us_cost_foot = _lead_cost_parts("US", cpl, "USD", us_week.get("conversions"))
    au_cost, au_cost_foot = _lead_cost_parts("AU", cpl_au, "AUD", au_week.get("conversions"))

    bus = baseline.get("us") or {}
    bau = baseline.get("au") or {}
    zjo = baseline.get("zoho_jo") or {}

    frozen_sales, frozen_ads = _legacy_agency_table(
        us_week,
        au_week,
        bus,
        bau,
        zjo,
        cpl,
        cpl_au,
        week_label=str(cpl.get("label") or SCOREBOARD_WEEK_LABEL),
        legacy_window=str(baseline.get("window") or ""),
        ga4=ga4,
        legacy_enq=baseline.get("legacy_enq") or {},
        zoho_week=zoho_week,
    )
    ga4_html = _ga4_bottom_html(ga4)
    zoho_now = _load_zoho_now()
    zoho_last_wd = _load_zoho_last_weekdays()
    us_now = us_perf.get("scoreboard_now") or {}
    au_now = au_perf.get("scoreboard_now") or {}
    us_now_tot = us_now.get("totals") or {}
    au_now_tot = au_now.get("totals") or {}
    zoho_now_us = (zoho_now or {}).get("usa") or {}
    zoho_now_au = (zoho_now or {}).get("au") or {}
    au_quality_n = _quality_enquiry_n(zoho_now_au)
    us_now_ops = exec_data.get("sales_ops_us_now") or {}
    au_now_ops = exec_data.get("sales_ops_au_now") or {}
    us_named_enq = us_now_ops.get("enquiries")
    au_named_enq = au_now_ops.get("enquiries")
    us_now_label = str(us_now.get("label") or "This week so far")
    us_cheyenne_label = str(us_now_ops.get("label") or "Mon–Fri")
    au_holly_label = str(au_now_ops.get("label") or "Mon–Fri")
    us_now_end = str(us_now.get("end") or "")[:10]
    try:
        focus_day = date.fromisoformat(us_now_end) if us_now_end else None
    except ValueError:
        focus_day = None
    today_utc = datetime.now(timezone.utc).date()
    partial_note = (
        f"US {focus_day.strftime('%A')} is partial · AU may be further along"
        if focus_day and focus_day == today_utc
        else "US week in progress · AU may be further along"
    )
    us_now_cpl = {
        "enquiries": us_named_enq,
        "cost_per_job_order_usd": _div_cost(
            us_now_tot.get("cost_usd"), zoho_now_us.get("job_order_submitted")
        ),
        "cost_per_job_order_source": "zoho_census",
        "zoho_census": {"job_order_submitted": zoho_now_us.get("job_order_submitted")},
    }
    au_now_cpl = {
        "enquiries": au_named_enq if au_now_ops.get("enquiries") is not None else None,
        "cost_per_job_order_usd": _div_cost(
            au_now_tot.get("cost_usd"),
            au_now_ops.get("job_orders_total")
            if au_now_ops.get("scoreboard") == "holly"
            else zoho_now_au.get("job_order_submitted"),
        ),
        "cost_per_job_order_source": (
            "holly_labeled" if au_now_ops.get("job_orders_total") else "zoho_census"
        ),
        "zoho_census": {
            "job_order_submitted": (
                au_now_ops.get("job_orders_total")
                if au_now_ops.get("scoreboard") == "holly"
                else zoho_now_au.get("job_order_submitted")
            )
        },
    }
    now_days = len(us_now.get("dates") or []) or 3
    now_sales, now_ads = _legacy_agency_table(
        us_now_tot,
        au_now_tot,
        bus,
        bau,
        zjo,
        us_now_cpl,
        au_now_cpl,
        week_label=us_now_label,
        legacy_window=str(baseline.get("window") or ""),
        ga4=ga4,
        legacy_enq=baseline.get("legacy_enq") or {},
        zoho_week=zoho_now,
        volume_days=now_days,
        this_hd="So far",
        legacy_hd=f"Legacy {now_days}d",
        ga4_label=str(((ga4 or {}).get("now") or {}).get("window") or us_now_label),
        last_week=zoho_last_wd,
        ads_note=(
            f"Legacy spend is {now_days}/7 of their typical week — not a full 7 vs 7. "
            "CTR, CPC, and cost / job order stay as rates. "
            + (
                f"US Cost / enquiry uses Cheyenne’s {us_named_enq} named enquiries "
                f"({us_cheyenne_label}). "
                if us_named_enq is not None
                else "US Cost / enquiry not yet — Cheyenne update pending. "
            )
            + (
                f"AU Cost / enquiry uses Holly’s {au_named_enq} named enquiries "
                f"({au_holly_label}). "
                if au_now_ops.get("enquiries") is not None
                else (
                    f"AU Cost / enquiry uses {num(au_quality_n)} quality enquiries "
                    f"(of {num(zoho_now_au.get('n'))} Zoho rows). "
                )
            )
            + f"US Cost / job order uses the Zoho census ({num(zoho_now_us.get('job_order_submitted'))} JO). "
            + f"AU Cost / job order uses the Zoho census ({num(zoho_now_au.get('job_order_submitted'))} JO). "
            + "Zoho census is wider net — not added to Cheyenne/Holly counts."
        ),
        sales_note=(
            "This-week Enquiries in the sales table are the Zoho census "
            f"(US {num(zoho_now_us.get('n'))} · AU {num(zoho_now_au.get('n'))}). "
            + (
                f"US Cost / enquiry uses Cheyenne’s {us_named_enq} ({us_cheyenne_label}). "
                if us_named_enq is not None
                else "US Cost / enquiry not yet — Cheyenne update pending. "
            )
            + (
                f"AU Cost / enquiry uses Holly’s {au_named_enq} ({au_holly_label}). "
                if au_now_ops.get("enquiries") is not None
                else ""
            )
            + f"Δ legacy is {now_days}/7 of their typical week. "
            + "AU Owner = George on microsite rows is a routing bug, not a test-lead flag."
        ),
    )
    now_fresh = (
        f"{html.escape(us_now_label)} · Ads refreshed {html.escape(asof or '—')} UTC · "
        f"GA4 refreshed {html.escape(ga4_asof or '—')} UTC · "
        "sources: Google Ads, GA4, named sales leads, Zoho census · "
        f"{html.escape(partial_note)}"
    )
    frozen_fresh = (
        f"{html.escape(SCOREBOARD_WEEK_LABEL)} frozen · Ads refreshed {html.escape(asof or '—')} UTC · "
        f"GA4 {html.escape(ga4_asof or '—')} UTC · "
        "Zoho census is all-source, not Ads CPA"
    )
    now_html = (
        _now_market_html(
            "US",
            us_now,
            "USD",
            zoho_now,
            extra_note=(
                f"Cheyenne {us_cheyenne_label}: "
                + (
                    (
                        f"{us_named_enq} enquiries (Mon–Tue pending). "
                        f"Weekend addendum {us_now_ops.get('weekend_enquiries') or 0} enquiries · "
                        f"{us_now_ops.get('sales_calls_booked') or 0} call booked · "
                        f"{us_now_ops.get('looking_for_work') or 0} looking for work (both weekend phone calls)."
                    )
                    if us_named_enq is not None
                    else "update pending."
                )
            ),
            named_enquiries=us_named_enq,
            spend_usd=us_now_ops.get("spend_usd"),
        )
        + _now_market_html(
            "AU",
            au_now,
            "AUD",
            zoho_now,
            extra_note=(
                f"Holly {au_holly_label}: "
                + (
                    f"{au_named_enq} enquiries · "
                    f"{au_now_ops.get('job_orders_total') or 0} job order"
                    f"{'s' if int(au_now_ops.get('job_orders_total') or 0) != 1 else ''} "
                    f"({au_now_ops.get('new_job_orders') or 0} new). "
                    f"{au_now_ops.get('sales_calls_completed') or '—'} sales calls completed."
                    if au_named_enq is not None
                    else "update pending."
                )
            ),
            named_enquiries=au_named_enq if au_now_ops.get("enquiries") is not None else None,
            spend_usd=au_now_ops.get("spend_usd"),
        )
        + _sales_section(
            now_sales,
            section_id="week-sales-now",
            meta="This week so far vs last week and vs legacy · named sales + Zoho rows",
        )
        + _legacy_section(
            now_ads,
            section_id="agency-baseline-now",
            meta=f"This week so far vs {now_days}/7 of their typical week",
        )
        + _ga4_now_html(ga4, us_ads=us_now, au_ads=au_now)
        + _new_week_starter_insights_html(us_now, au_now)
        + _week_notes_html(
            asof_line="This week so far · US $ · AU A$",
            fresh_id="fresh-now",
            fresh=now_fresh,
            how_anchor=True,
        )
    )
    frozen_html = _frozen_week_panel_html(
        week_label=str(cpl.get("label") or SCOREBOARD_WEEK_LABEL),
        cpl=cpl,
        cpl_au=cpl_au,
        us_week=us_week,
        au_week=au_week,
        us_cost=us_cost,
        us_cost_foot=us_cost_foot,
        au_cost=au_cost,
        au_cost_foot=au_cost_foot,
        us_prior_7=(us_perf.get("compare_7v7") or {}).get("prior_7"),
        au_prior_7=(au_perf.get("compare_7v7") or {}).get("prior_7"),
        frozen_sales=frozen_sales,
        frozen_ads=frozen_ads,
        ga4_html=ga4_html,
        frozen_fresh=frozen_fresh,
        fresh_id="fresh-frozen",
        us_spend_id="us-spend",
        au_spend_id="au-spend",
        market_us_id="market-us",
        market_au_id="market-au",
        sales_section_id="week-sales",
        ads_section_id="agency-baseline",
        core_us=core_us,
        roles_us=roles_us,
        core_au=core_au,
        roles_au=roles_au,
        crm_ready=crm_ready,
        zoho_collapsed=_collapsed_zoho_html(
            halo,
            zoho_week,
            str(cpl.get("label") or SCOREBOARD_WEEK_LABEL),
            us_spend=cpl.get("spend_usd"),
            au_spend=cpl_au.get("spend_usd"),
        ),
        close_insights=_frozen_week_close_insights_html(
            cpl,
            cpl_au,
            us_perf,
            au_perf,
            ga4,
        ),
    )

    frozen_launch_html = ""
    if ARCHIVE_FROZEN_PATH.is_file():
        archive = load_json(ARCHIVE_FROZEN_PATH)
        arch_cpl = archive.get("sales_ops_us") or {}
        arch_cpl_au = archive.get("sales_ops_au") or {}
        arch_ga4 = archive.get("ga4") or {}
        arch_us_perf = archive.get("performance_us") or {}
        arch_au_perf = archive.get("performance_au") or {}
        arch_us_week = _ads_for_sales_week(archive, "US", arch_cpl)
        arch_au_week = _ads_for_sales_week(archive, "AU", arch_cpl_au)
        arch_us_cost, arch_us_cost_foot = _lead_cost_parts(
            "US", arch_cpl, "USD", arch_us_week.get("conversions")
        )
        arch_au_cost, arch_au_cost_foot = _lead_cost_parts(
            "AU", arch_cpl_au, "AUD", arch_au_week.get("conversions")
        )
        arch_sales, arch_ads = _legacy_agency_table(
            arch_us_week,
            arch_au_week,
            bus,
            bau,
            zjo,
            arch_cpl,
            arch_cpl_au,
            week_label=LAUNCH_SCOREBOARD_WEEK_LABEL,
            legacy_window=str(baseline.get("window") or ""),
            ga4=arch_ga4,
            legacy_enq=baseline.get("legacy_enq") or {},
            zoho_week=None,
        )
        arch_ga4_html = _ga4_bottom_html(
            arch_ga4, frozen_week_label=LAUNCH_SCOREBOARD_WEEK_LABEL
        )
        arch_asof = (archive.get("generated_at_utc") or "")[:16].replace("T", " ")
        arch_ga4_asof = (arch_ga4.get("generated_at_utc") or "")[:16].replace("T", " ")
        arch_fresh = (
            f"{html.escape(LAUNCH_SCOREBOARD_WEEK_LABEL)} frozen · "
            f"Archived {html.escape(arch_asof or '—')} UTC · "
            f"GA4 {html.escape(arch_ga4_asof or '—')} UTC · "
            "AU tags started Aug 12 · launch-week baseline"
        )
        frozen_launch_html = _frozen_week_panel_html(
            week_label=LAUNCH_SCOREBOARD_WEEK_LABEL,
            cpl=arch_cpl,
            cpl_au=arch_cpl_au,
            us_week=arch_us_week,
            au_week=arch_au_week,
            us_cost=arch_us_cost,
            us_cost_foot=arch_us_cost_foot,
            au_cost=arch_au_cost,
            au_cost_foot=arch_au_cost_foot,
            us_prior_7=(arch_us_perf.get("compare_7v7") or {}).get("prior_7"),
            au_prior_7=(arch_au_perf.get("compare_7v7") or {}).get("prior_7"),
            frozen_sales=arch_sales,
            frozen_ads=arch_ads,
            ga4_html=arch_ga4_html,
            frozen_fresh=arch_fresh,
            fresh_id="fresh-frozen-1016",
            us_spend_id="us-spend-1016",
            au_spend_id="au-spend-1016",
            market_us_id="market-us-1016",
            market_au_id="market-au-1016",
            sales_section_id="week-sales-1016",
            ads_section_id="agency-baseline-1016",
            core_us=core_us,
            roles_us=roles_us,
            core_au=core_au,
            roles_au=roles_au,
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>Executive · Virtual Coworker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    body[data-page="executive-weekly.html"] .main {{
      max-width: 1120px;
      font-variant-numeric: tabular-nums;
    }}
    .dash-head {{ margin: 0 0 0.45rem; }}
    .dash-head h1 {{ margin: 0; font-size: 1.45rem; }}
    .week-notes {{
      margin: 1.6rem 0 0;
      padding-top: 1rem;
      border-top: 1px solid rgba(0,0,0,0.08);
    }}
    .week-notes .asof {{
      margin: 0 0 0.45rem;
      font-size: 0.88rem;
      color: var(--muted);
    }}
    .week-notes .how-count {{ margin-bottom: 0.45rem; }}
    .week-notes .data-fresh {{ margin-top: 0.35rem; max-width: none; }}
    .mkt-block {{
      margin: 0 0 0.85rem;
      padding: 0.85rem 1rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--edge-soft);
      background: var(--panel);
    }}
    .mkt-block.us {{ border-color: var(--tint-green-edge); background: var(--tint-green); }}
    .mkt-block.au {{ border-color: var(--tint-cool-edge); background: var(--tint-cool); }}
    .mkt-block .mkt-hd {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.35rem 1rem;
      margin: 0 0 0.55rem;
    }}
    .mkt-block h2 {{
      margin: 0;
      font-size: 0.88rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .mkt-block .bud {{
      margin: 0;
      font-size: 0.92rem;
      color: var(--ink);
      font-variant-numeric: tabular-nums;
    }}
    .period {{
      margin: 0 0 0.55rem;
    }}
    .period:last-child {{ margin-bottom: 0; }}
    .period h3 {{
      margin: 0 0 0.35rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 0.4rem;
    }}
    @media (max-width: 900px) {{
      .kpi-row {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .kpi-row {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    .kpi {{
      min-width: 0;
      display: flex;
      flex-direction: column;
      box-sizing: border-box;
      min-height: 100%;
      padding: 0.55rem 0.55rem 0.5rem;
      border-radius: 8px;
      border: 1px solid rgba(0,0,0,0.08);
      background: rgba(255,255,255,0.72);
    }}
    .kpi.kpi-cost {{
      border: 1px solid rgba(0,0,0,0.10);
      background: rgba(255,255,255,0.88);
      box-shadow: none;
    }}
    .kpi.kpi-cost .k {{
      font-size: 0.74rem;
      font-weight: 500;
      color: var(--muted);
    }}
    .kpi.kpi-cost .v {{
      font-size: 1.22rem;
      font-weight: 600;
    }}
    .kpi .k {{
      display: block;
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 0.15rem;
      line-height: 1.2;
      min-height: 1.55em;
    }}
    .kpi .v {{
      display: block;
      font-size: 1.38rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.15;
      color: var(--ink);
    }}
    .kpi .sub {{
      display: block;
      margin-top: 0.28rem;
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--muted);
      line-height: 1.35;
      white-space: normal;
    }}
    .kpi .sub .wow {{
      display: inline;
      font-weight: 800;
      font-size: 1rem;
      margin-right: 0.22rem;
    }}
    .kpi .sub .wow-arr {{
      font-size: 1.05em;
      margin-right: 0.1rem;
    }}
    .mkt-note {{
      margin: 0.55rem 0 0;
      font-size: 0.84rem;
      line-height: 1.4;
      color: var(--ink);
    }}
    .mkt-note .mute, .mkt-note.mute {{ font-size: 0.8rem; color: var(--muted); }}
    .why {{
      margin: 0.4rem 0 0;
      font-size: 0.8rem;
      line-height: 1.4;
      color: var(--ink);
    }}
    .cmp7 {{
      margin: 0.35rem 0 0;
      font-size: 0.78rem;
      line-height: 1.4;
      color: var(--ink);
    }}
    .week-group {{ margin: 0 0 0.45rem; }}
    .kpi-row.week-costs {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin-bottom: 0.4rem;
    }}
    .kpi-row.week-ads {{
      grid-template-columns: repeat(6, minmax(0, 1fr));
    }}
    .week-costs .kpi {{
      min-height: 4.2rem;
    }}
    .week-costs .kpi-cost .k {{ font-size: 0.72rem; font-weight: 500; }}
    .week-costs .kpi-cost .v {{ font-size: 1.22rem; font-weight: 600; }}
    .week-ads {{
      padding: 0.15rem 0 0.05rem;
    }}
    .week-ads .kpi {{
      min-height: 0;
      padding: 0.2rem 0.12rem 0.15rem;
      border: none;
      background: transparent;
      border-radius: 0;
    }}
    .week-ads .kpi .k {{
      font-size: 0.68rem;
      font-weight: 500;
      min-height: 0;
      letter-spacing: 0.03em;
    }}
    .week-ads .kpi .v {{
      font-size: 1.02rem;
      font-weight: 500;
    }}
    .week-ads .kpi .sub {{
      font-size: 0.7rem;
      font-weight: 400;
      margin-top: 0.12rem;
    }}
    .week-ads .kpi .sub .wow {{
      font-weight: 500;
      font-size: 0.7rem;
    }}
    .week-ads .kpi .sub .wow-arr {{
      font-size: 0.9em;
    }}
    @media (max-width: 900px) {{
      .kpi-row.week-ads {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .kpi-row.week-costs {{ grid-template-columns: 1fr; }}
      .kpi-row.week-ads {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    .lead-cost {{ margin: 0.55rem 0 0.35rem; }}
    .lead-cost h3 {{
      margin: 0 0 0.35rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .src-chips {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.18rem 0.28rem;
      margin: 0.28rem 0 0.05rem;
    }}
    .src-chips-k {{
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      margin-right: 0.1rem;
    }}
    .src-chip {{
      display: inline-flex;
      align-items: baseline;
      gap: 0.28rem;
      max-width: 11rem;
      padding: 0.1rem 0.38rem;
      border-radius: 999px;
      border: 1px solid rgba(0,0,0,0.07);
      background: rgba(255,255,255,0.58);
      font-size: 0.68rem;
      line-height: 1.2;
    }}
    .src-chip .src-l {{
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}
    .src-chip .src-n {{ font-weight: 700; font-variant-numeric: tabular-nums; }}
    .prior-line {{ margin: 0.2rem 0 0; }}
    .zoho-census {{ margin: 0.2rem 0 0; }}
    .kpi-row.lead-kpi {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    .kpi-row.lead-kpi.lead-kpi-4 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
    @media (max-width: 900px) {{
      .kpi-row.lead-kpi.lead-kpi-4 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .kpi-row.lead-kpi {{ grid-template-columns: 1fr; }}
    }}
    details.today-demote {{
      margin: 0.35rem 0 0;
      border: 1px dashed rgba(100,116,139,0.4);
      border-radius: 8px;
      background: rgba(255,255,255,0.35);
    }}
    details.today-demote > summary {{
      cursor: pointer;
      padding: 0.4rem 0.65rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      list-style: none;
    }}
    details.today-demote > summary::-webkit-details-marker {{ display: none; }}
    details.today-demote .bd {{ padding: 0 0.55rem 0.55rem; }}
    .baseline {{
      margin: 0 0 0.85rem;
      padding: 0.85rem 1rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--tint-amber-edge);
      background: var(--tint-amber);
    }}
    /* Every section below the market cards wears the same header as the
       market cards: small uppercase title left, quiet window right. */
    .sec-hd {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.25rem 1rem;
      margin: 0 0 0.6rem;
    }}
    .sec-hd h2 {{
      margin: 0;
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .sec-hd .sec-meta {{
      margin: 0;
      font-size: 0.8rem;
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }}
    .baseline .cmp {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      font-variant-numeric: tabular-nums;
    }}
    .baseline .cmp th, .baseline .cmp td {{
      text-align: left;
      padding: 0.35rem 0.5rem;
      border-bottom: 1px solid rgba(0,0,0,0.08);
      vertical-align: top;
    }}
    .baseline .cmp th {{
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .baseline .cmp th.num,
    .baseline .cmp td.num {{
      text-align: right;
      white-space: nowrap;
    }}
    .baseline .cmp td:first-child {{ font-weight: 600; white-space: nowrap; }}
    .baseline .note {{ margin: 0.45rem 0 0; font-size: 0.8rem; color: var(--muted); }}
    .legacy-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.55rem;
    }}
    .legacy-box {{
      margin: 0;
      padding: 0.65rem 0.75rem 0.55rem;
      border-radius: 8px;
      border: 1px solid rgba(0,0,0,0.1);
      background: rgba(255,255,255,0.72);
    }}
    .legacy-box h3 {{
      margin: 0 0 0.35rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .legacy-box table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    .legacy-box th, .legacy-box td {{
      padding: 0.28rem 0.2rem;
      border-bottom: 1px solid rgba(0,0,0,0.07);
    }}
    .legacy-box thead th {{
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      text-align: right;
    }}
    .legacy-box thead th:first-child {{ text-align: left; }}
    .legacy-box th[scope="row"] {{
      text-align: left;
      font-weight: 700;
      color: var(--ink);
    }}
    .legacy-box .num {{ text-align: right; }}
    .legacy-box td.this-w {{ font-weight: 700; color: var(--ink); }}
    .legacy-box td.leg-n {{ font-weight: 400; color: var(--muted); }}
    /* Legacy agency comparison — one column template for every band, so
       This week / Legacy week / Δ stay in the same place all the way down. */
    .baseline {{
      --cmp-cols: minmax(5rem, 0.8fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr);
    }}
    .cmp-sheet.has-lastwk {{
      --cmp-cols: minmax(3.6rem, 0.5fr) minmax(0, 1fr) minmax(0, 1fr) minmax(3.4rem, 0.85fr) minmax(0, 1fr) minmax(3.4rem, 0.85fr);
    }}
    .cmp-band {{ margin: 0 0 0.5rem; }}
    .cmp-band + .cmp-note + .cmp-band {{
      margin-top: 0.9rem;
      padding-top: 0.9rem;
      border-top: 1px solid rgba(0,0,0,0.12);
    }}
    .cmp-band-hd {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.2rem 1rem;
      margin: 0 0 0.3rem;
      padding: 0 0.05rem;
    }}
    .cmp-band-hd h3 {{
      margin: 0;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--ink);
    }}
    .cmp-band-note {{ font-size: 0.72rem; color: var(--muted); }}
    .cmp-sheet {{
      display: grid;
      grid-template-columns: var(--cmp-cols);
      align-items: baseline;
      column-gap: 0.75rem;
      padding: 0.45rem 0.85rem 0.55rem;
      border-radius: 8px;
      border: 1px solid rgba(0,0,0,0.1);
      background: rgba(255,255,255,0.72);
      font-size: 0.88rem;
      font-variant-numeric: tabular-nums;
    }}
    .cmp-sheet .cell {{ padding: 0.16rem 0; min-width: 0; }}
    .cmp-sheet .num {{ text-align: right; }}
    .cmp-sheet .hd {{
      padding-bottom: 0.3rem;
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      border-bottom: 1px solid rgba(0,0,0,0.08);
    }}
    .cmp-sheet .grp {{
      grid-column: 1 / -1;
      margin-top: 0.4rem;
      padding: 0.35rem 0 0.1rem;
      border-top: 1px solid rgba(0,0,0,0.07);
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .cmp-sheet .hd + .grp {{ margin-top: 0; border-top: none; }}
    .cmp-sheet .cm {{ font-weight: 600; color: var(--ink); }}
    .cmp-sheet .tw {{ font-weight: 700; color: var(--ink); }}
    .cmp-sheet .lg {{ font-weight: 400; color: var(--muted); }}
    .cmp-note {{
      margin: 0.3rem 0 0.75rem;
      padding: 0 0.05rem;
      font-size: 0.76rem;
      line-height: 1.45;
      color: var(--muted);
    }}
    @media (max-width: 560px) {{
      .baseline {{ --cmp-cols: 4.2rem minmax(0, 1fr) minmax(0, 1fr) 5.4rem; }}
      .cmp-sheet.has-lastwk {{ --cmp-cols: 3.1rem minmax(0, 1fr) minmax(0, 1fr) 3.2rem minmax(0, 1fr) 3.4rem; }}
      .cmp-sheet {{ column-gap: 0.4rem; font-size: 0.82rem; }}
    }}
    .legacy-grid.ga4-grid {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.4rem;
    }}
    .ga4-grid .legacy-box {{
      padding: 0.55rem 0.6rem 0.45rem;
      border-color: rgba(0,0,0,0.08);
      background: rgba(255,255,255,0.72);
    }}
    .ga4-grid .legacy-box h3 {{
      margin: 0 0 0.2rem;
      font-size: 0.68rem;
      min-height: 1.55em;
    }}
    .ga4-grid .legacy-box table {{ font-size: 1rem; font-variant-numeric: tabular-nums; }}
    .ga4-grid .legacy-box th,
    .ga4-grid .legacy-box td {{ padding: 0.22rem 0; border-bottom: none; }}
    .ga4-grid .legacy-box tr + tr th,
    .ga4-grid .legacy-box tr + tr td {{ border-top: 1px solid rgba(0,0,0,0.06); }}
    .ga4-grid .legacy-box th[scope="row"] {{
      font-size: 0.74rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .ga4-grid .legacy-box .sub {{
      display: block;
      margin-top: 0.16rem;
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--muted);
    }}
    .ga4-grid .legacy-box .wow {{
      display: inline;
      font-weight: 800;
      font-size: 0.95rem;
      margin-right: 0.22rem;
    }}
    .ga4-grid .legacy-box .wow-arr {{
      font-size: 1.05em;
      margin-right: 0.1rem;
    }}
    .ga4-grid .legacy-box .wow.delta-good {{ color: #166534; }}
    .ga4-grid .legacy-box .wow.delta-bad {{ color: #9f1239; }}
    .ga4-grid .legacy-box .wow.delta-flat {{ color: var(--muted); }}
    .ga4-now {{
      margin: 0 0 0.85rem;
      padding: 0.85rem 1rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--edge-soft);
      background: var(--panel);
    }}
    .windows {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 0.45rem 1rem;
      margin: 1rem 0 0;
      padding: 0.7rem 0 0;
      border-top: 1px solid rgba(0,0,0,0.1);
    }}
    .windows div {{ margin: 0; }}
    .windows dt {{
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .windows dd {{
      margin: 0.15rem 0 0;
      font-size: 0.82rem;
      font-weight: 600;
      font-variant-numeric: tabular-nums;
    }}
    @media (max-width: 900px) {{
      .legacy-grid.ga4-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 720px) {{
      .legacy-grid {{ grid-template-columns: 1fr; }}
      .legacy-grid.sales-vol {{ grid-template-columns: 1fr; }}
      .legacy-grid.ga4-grid {{ grid-template-columns: 1fr 1fr; }}
      .windows {{ grid-template-columns: 1fr; }}
    }}
    .baseline .agency-econ {{ margin: 0 0 0.65rem; }}
    .baseline .agency-econ h3 {{ color: var(--ink); }}
    .halo {{
      margin: 0 0 0.85rem;
      padding: 0.85rem 1rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--tint-cool-edge);
      background: var(--tint-cool);
    }}
    .halo-frame {{
      margin: 0 0 0.4rem;
      font-size: 0.8rem;
      line-height: 1.35;
      color: var(--muted);
    }}
    .kpi-row.halo-kpi {{
      grid-template-columns: repeat(3, minmax(0, 1fr));
      margin: 0;
    }}
    .halo-kpi .kpi {{ min-height: 4.85rem; }}
    @media (max-width: 900px) {{
      .kpi-row.halo-kpi {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
    }}
    @media (max-width: 520px) {{
      .kpi-row.halo-kpi {{ grid-template-columns: 1fr; }}
    }}
    .kpi.kpi-halo .v {{ font-size: 1.4rem; }}
    .halo .cmp, .halo-cmp {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
      font-variant-numeric: tabular-nums;
    }}
    .halo .cmp th, .halo .cmp td,
    .halo-cmp th, .halo-cmp td {{
      text-align: left;
      padding: 0.35rem 0.5rem;
      border-bottom: 1px solid rgba(0,0,0,0.08);
      vertical-align: top;
    }}
    .halo .cmp th, .halo-cmp th {{
      font-size: 0.68rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .halo .cmp th.num, .halo .cmp td.num,
    .halo-cmp th.num, .halo-cmp td.num {{
      text-align: right;
      white-space: nowrap;
    }}
    .halo .cmp td:first-child, .halo-cmp td:first-child {{ font-weight: 600; white-space: nowrap; }}
    .halo .note {{ margin: 0.45rem 0 0; font-size: 0.8rem; color: var(--muted); }}
    .ga4-foot {{ margin: 0.55rem 0 0; }}
    .lp-block {{ margin: 0.75rem 0 0; }}
    .lp-block .sec-hd {{ margin-bottom: 0.4rem; }}
    .legacy-grid.lp-grid {{
      grid-template-columns: 1fr 1fr;
      gap: 0.85rem;
    }}
    .lp-t {{ width: 100%; border-collapse: collapse; font-size: 0.95rem; }}
    .lp-t th, .lp-t td {{
      padding: 0.42rem 0.55rem;
      border-bottom: 1px solid rgba(0,0,0,0.07);
    }}
    .lp-t td.num, .lp-t th.num {{
      padding-left: 0.85rem;
      min-width: 4.6rem;
    }}
    .lp-t thead th {{
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
      text-align: right;
    }}
    .lp-t thead th:first-child, .lp-t th[scope="row"] {{ text-align: left; }}
    .lp-t th[scope="row"] {{
      font-weight: 600;
      font-family: "IBM Plex Mono", ui-monospace, monospace;
      font-size: 0.88rem;
      padding-right: 0.85rem;
    }}
    .ga4-insight {{
      margin: 1rem 0 0;
      padding: 0.95rem 1.1rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--edge-soft);
      background: rgba(255,255,255,0.78);
    }}
    .ga4-insight h3 {{
      margin: 0 0 0.55rem;
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: 0.01em;
      color: var(--ink);
    }}
    .ga4-insight ul {{
      margin: 0;
      padding: 0 0 0 1.2rem;
      font-size: 1.05rem;
      line-height: 1.55;
      color: var(--ink);
    }}
    .ga4-insight li {{ margin: 0 0 0.85rem; }}
    .ga4-insight li:last-child {{ margin-bottom: 0; }}
    .ga4-insight p {{ margin: 0.12rem 0 0; font-size: 0.95rem; line-height: 1.45; }}
    .ga4-insight .ins-k {{ font-weight: 700; }}
    .ga4-insight .ins-caveat {{ color: var(--muted); font-size: 0.88rem; }}
    .week-close {{
      margin: 1.25rem 0 0;
      padding-top: 0.25rem;
    }}
    .week-close .ga4-insight {{
      margin-top: 0;
    }}
    .lp-t tr.small-n th, .lp-t tr.small-n td {{ color: var(--muted); }}
    .sample-tag {{
      display: inline-block;
      margin-left: 0.35rem;
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      color: var(--warn);
      font-family: var(--font);
    }}
    .data-fresh {{
      margin: 0.2rem 0 0;
      font-size: 0.78rem;
      line-height: 1.4;
      color: var(--muted);
      max-width: 46rem;
    }}
    @media (max-width: 720px) {{
      .legacy-grid.lp-grid {{ grid-template-columns: 1fr; }}
      .lp-t {{ font-size: 0.82rem; }}
      .lp-t td.num, .lp-t th.num {{ min-width: 2.6rem; padding-left: 0.4rem; }}
    }}
    details.calc-how {{
      margin: 0.7rem 0 0;
      border: 1px dashed rgba(100,116,139,0.45);
      border-radius: 8px;
      background: rgba(255,255,255,0.35);
    }}
    details.calc-how > summary {{
      cursor: pointer;
      padding: 0.45rem 0.65rem;
      font-weight: 600;
      font-size: 0.82rem;
      list-style: none;
      color: var(--muted);
    }}
    details.calc-how > summary::-webkit-details-marker {{ display: none; }}
    details.calc-how .bd {{ padding: 0 0.65rem 0.55rem; }}
    .delta-good {{ color: #166534; font-weight: 700; }}
    .delta-bad {{ color: #9f1239; font-weight: 700; }}
    .delta-flat {{ color: var(--muted); font-weight: 600; }}
    .mute {{ color: var(--muted); font-size: 0.8rem; }}
    details.ev {{
      margin: 0.5rem 0 0;
      border: 1px dashed rgba(100,116,139,0.55);
      border-radius: 8px;
      background: var(--panel);
    }}
    details.ev > summary {{
      cursor: pointer;
      padding: 0.65rem 0.85rem;
      font-weight: 700;
      font-size: 0.92rem;
      list-style: none;
    }}
    details.ev > summary::-webkit-details-marker {{ display: none; }}
    details.ev .bd {{ padding: 0 0.85rem 0.85rem; border-top: 1px solid rgba(0,0,0,0.06); }}
    table.ev-t {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; margin: 0.45rem 0; }}
    table.ev-t th, table.ev-t td {{
      text-align: left; padding: 0.28rem 0.2rem;
      border-bottom: 1px solid rgba(0,0,0,0.06); vertical-align: top;
    }}
    table.ev-t th {{
      font-size: 0.64rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted);
    }}
    .num {{ font-variant-numeric: tabular-nums; white-space: nowrap; }}
    .conf {{
      display: inline-block;
      margin-left: 0.28rem;
      padding: 0.02rem 0.32rem;
      border-radius: 999px;
      font-size: 0.58rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      vertical-align: 0.12em;
      line-height: 1.4;
    }}
    .conf-v {{ background: #dcfce7; color: #166534; }}
    .conf-d {{ background: #e0e7ff; color: #3730a3; }}
    .conf-i {{ background: #fef3c7; color: #92400e; }}
    .conf-u {{ background: #f1f5f9; color: #475569; }}
    .conf-legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem 0.7rem;
      margin: 0.35rem 0 0.55rem;
      font-size: 0.72rem;
      color: var(--muted);
    }}
    .disclose {{
      margin: 0 0 0.65rem;
      font-size: 0.78rem;
      line-height: 1.4;
      color: var(--muted);
    }}
    .exec-sum {{
      margin: 0 0 0.75rem;
      padding: 0.55rem 0.85rem 0.55rem 1.2rem;
      border-radius: 8px;
      border: 1px solid var(--edge-soft);
      background: var(--panel);
      font-size: 0.86rem;
      line-height: 1.4;
    }}
    .exec-sum li {{ margin: 0 0 0.28rem; }}
    .exec-sum li:last-child {{ margin-bottom: 0; }}
    .funnel-k {{
      margin: 0.55rem 0 0.3rem;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .funnel {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .funnel li {{
      flex: 1 1 5.6rem;
      min-width: 5.4rem;
      padding: 0.35rem 0.4rem;
      border-radius: 8px;
      border: 1px solid rgba(0,0,0,0.08);
      background: rgba(255,255,255,0.7);
    }}
    .funnel .fn-k {{
      display: block;
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      color: var(--muted);
      line-height: 1.2;
    }}
    .funnel .fn-n {{
      display: block;
      font-size: 0.92rem;
      font-weight: 700;
      margin: 0.1rem 0;
    }}
    .funnel .fn-miss {{ background: #f8fafc; }}
    .funnel .fn-inc {{ background: #fffbeb; }}
    .funnel .fn-dir {{ background: #eef2ff; }}
    .funnel-note {{ margin: 0.28rem 0 0; }}
    .crm-ready .st-ok {{ color: #166534; font-weight: 700; }}
    .crm-ready .st-rev {{ color: #92400e; font-weight: 700; }}
    .crm-ready .st-miss, .crm-ready .st-test {{ color: #475569; font-weight: 700; }}
    @media (max-width: 520px) {{
      .funnel li {{ flex: 1 1 46%; }}
      .conf {{ margin-left: 0.12rem; }}
    }}
    .week-toggle {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin: 0 0 0.85rem;
    }}
    .week-toggle button {{
      font: inherit;
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      border: 1px solid var(--edge);
      background: #fff;
      cursor: pointer;
      color: var(--ink);
    }}
    .week-toggle button.on {{
      background: #1a1a1a;
      color: #fff;
      border-color: #1a1a1a;
    }}
    .view-week[hidden] {{ display: none; }}
    .how-count {{
      margin: 0 0 0.75rem;
      padding: 0;
      border: none;
      background: none;
      font-size: 0.82rem;
      font-weight: 400;
      line-height: 1.45;
      color: var(--muted);
    }}
    .how-count strong {{
      font-weight: 600;
      color: var(--ink);
    }}
    .how-count .cats,
    .how-count .sample {{
      font-weight: 400;
    }}
    .zoho-extra {{
      margin: 1.35rem 0 0;
      font-size: 0.82rem;
      color: var(--muted);
    }}
    .zoho-extra summary {{
      cursor: pointer;
      font-weight: 500;
    }}
    .zoho-extra .bd {{
      margin-top: 0.55rem;
    }}
    table.day-cmp {{
      width: 100%;
      table-layout: fixed;
      border-collapse: collapse;
      margin: 0.7rem 0 0;
      font-size: 0.98rem;
      font-variant-numeric: tabular-nums;
    }}
    table.day-cmp th, table.day-cmp td {{
      text-align: right;
      padding: 0.4rem 0.55rem;
      border-bottom: 1px solid rgba(0,0,0,0.07);
    }}
    table.day-cmp th.day-lbl,
    table.day-cmp th[scope="row"] {{
      text-align: left;
      width: 34%;
    }}
    table.day-cmp thead th {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
  </style>
</head>
<body data-page="executive-weekly.html" data-foot="Weekly archive · US · AU · baked">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="dash-head">
        <h1>Executive · weekly archive</h1>
        <p class="mute" style="margin:0.35rem 0 0">GA4 / landing-page / day-by-day detail. Monthly pilot report lives on <a href="executive.html">Executive Performance</a>.</p>
      </header>
      <div class="week-toggle" role="tablist" aria-label="Scoreboard week">
        <button type="button" class="on" data-week="now" aria-pressed="true">This week so far</button>
        <button type="button" data-week="frozen" aria-pressed="false">Aug 17–23 · frozen</button>
        <button type="button" data-week="frozen-1016" aria-pressed="false">Aug 10–16 · frozen</button>
      </div>

      <div class="view-week" id="view-now">
{now_html}
      </div>

      <div class="view-week" id="view-frozen" hidden>
{frozen_html}
      </div>

      <div class="view-week" id="view-frozen-1016" hidden>
{frozen_launch_html}
      </div>
      <p class="mute"><a href="launch-control.html">Checklist</a></p>

      <details class="ev" id="evidence">
        <summary>Evidence (IS windows · JSON)</summary>
        <div class="bd">
          <h3 style="margin:0.55rem 0 0.25rem;font-size:0.88rem">US Search IS by window</h3>
          <table class="ev-t">
            <thead><tr><th>Window</th><th>Campaign</th><th class="num">IS</th><th class="num">Lost rank</th><th class="num">Lost budget</th><th class="num">Top</th><th class="num">Abs top</th></tr></thead>
            <tbody>{_window_rows(windows, "US")}</tbody>
          </table>
          <h3 style="margin:0.55rem 0 0.25rem;font-size:0.88rem">AU Search IS by window</h3>
          <table class="ev-t">
            <thead><tr><th>Window</th><th>Campaign</th><th class="num">IS</th><th class="num">Lost rank</th><th class="num">Lost budget</th><th class="num">Top</th><th class="num">Abs top</th></tr></thead>
            <tbody>{_window_rows(windows, "AU")}</tbody>
          </table>
          <p class="mute">
            <a href="data/executive-snapshot.json">executive-snapshot.json</a> ·
            <a href="data/impression-share.json">impression-share.json</a> ·
            <a href="recovery-audit">Recovery audit</a>
          </p>
        </div>
      </details>
    </main>
  </div>
  <script src="nav.js"></script>
  <script>
    (function () {{
      var buttons = document.querySelectorAll("[data-week]");
      var views = {{
        now: document.getElementById("view-now"),
        frozen: document.getElementById("view-frozen"),
        "frozen-1016": document.getElementById("view-frozen-1016")
      }};
      function show(which) {{
        Object.keys(views).forEach(function (k) {{
          if (views[k]) views[k].hidden = k !== which;
        }});
        buttons.forEach(function (b) {{
          var on = b.getAttribute("data-week") === which;
          b.classList.toggle("on", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        }});
      }}
      buttons.forEach(function (b) {{
        b.addEventListener("click", function () {{ show(b.getAttribute("data-week")); }});
      }});
      if (location.hash === "#frozen" || location.hash.indexOf("lp-frozen") === 0) show("frozen");
      else if (location.hash === "#launch" || location.hash === "#frozen-1016" || location.hash.indexOf("lp-frozen-1016") === 0) show("frozen-1016");
      else if (location.hash.indexOf("lp-now") === 0) show("now");
    }})();
  </script>
</body>
</html>
"""


def inject_embedded_json(html_text: str, json_path: Path, marker_id: str = "embedded-page-data") -> str:
    payload = json_path.read_text(encoding="utf-8")
    json.loads(payload)  # validate
    # Idempotent: strip prior embeds/loaders
    html_text = re.sub(
        rf'<script type="application/json" id="{marker_id}">.*?</script>\s*',
        "",
        html_text,
        flags=re.S,
    )
    html_text = re.sub(
        r"<script>\s*window\.__VC_loadPageData[\s\S]*?</script>\s*",
        "",
        html_text,
    )
    block = f'<script type="application/json" id="{marker_id}">\n{payload}\n</script>\n'
    loader = (
        f"\n  {block}"
        f"  <script>\n"
        f"  window.__VC_loadPageData = function (fallbackUrl) {{\n"
        f"    try {{\n"
        f'      var el = document.getElementById("{marker_id}");\n'
        f"      if (el && el.textContent && el.textContent.trim()) {{\n"
        f"        return Promise.resolve(JSON.parse(el.textContent));\n"
        f"      }}\n"
        f"    }} catch (e) {{}}\n"
        f'    return fetch(fallbackUrl, {{ cache: "no-store" }}).then(function (r) {{\n'
        f'      if (!r.ok) throw new Error("HTTP " + r.status);\n'
        f"      return r.json();\n"
        f"    }});\n"
        f"  }};\n"
        f"  </script>\n"
    )
    if 'src="nav.js"' in html_text:
        html_text = re.sub(
            r'(<script src="nav\.js[^"]*"></script>)',
            lambda m: m.group(1) + loader,
            html_text,
            count=1,
        )
    else:
        html_text = html_text.replace("</body>", loader + "</body>", 1)

    replacements = [
        ('fetch("data/experiments-snapshot.json", { cache: "no-store" })',
         'window.__VC_loadPageData("/data/experiments-snapshot.json")'),
        ("fetch('data/experiments-snapshot.json', { cache: 'no-store' })",
         'window.__VC_loadPageData("/data/experiments-snapshot.json")'),
        ('fetch("/data/experiments-snapshot.json", { cache: "no-store" })',
         'window.__VC_loadPageData("/data/experiments-snapshot.json")'),
        ('fetch("data/recovery-audit.json", { cache: "no-store" })',
         'window.__VC_loadPageData("/data/recovery-audit.json")'),
        ("fetch('data/recovery-audit.json', { cache: 'no-store' })",
         'window.__VC_loadPageData("/data/recovery-audit.json")'),
        ('fetch("/data/recovery-audit.json", { cache: "no-store" })',
         'window.__VC_loadPageData("/data/recovery-audit.json")'),
    ]
    for rel, abs_url in replacements:
        html_text = html_text.replace(rel, abs_url)
    return html_text


def build_zoho_proposal() -> dict:
    # clarity: clear = ready; cursor_parked = omit/fold until writes; sales_later = Sales meaning only
    # Plain labels for Funnel & CRM table (form box → Zoho box)
    app_fields = [
        ("firstName", "Name (first)", "First_Name", "standard", "clear",
         "Form first name → Zoho First_Name"),
        ("lastName", "Name (last)", "Last_Name", "standard", "clear",
         "Form last name → Zoho Last_Name"),
        ("email", "Email", "Email", "standard", "clear",
         "Form email → Zoho Email"),
        ("phone", "Phone", "Phone", "standard", "clear",
         "Form phone → Zoho Phone"),
        ("company", "Company", "Company", "standard", "clear",
         "Form company → Zoho Company"),
        ("message", "Message", "Description", "standard", "clear",
         "Form message → Zoho Description"),
        ("gclid", "Google click id", "utm_gclid", "confirmed_in_dictionary", "clear",
         "Paid click id. Use utm_gclid (not $gclid) for this org."),
        ("utm_source", "UTM source", "utm_source", "confirmed_in_dictionary", "clear", None),
        ("utm_medium", "UTM medium", "utm_medium", "confirmed_in_dictionary", "clear", None),
        ("utm_campaign", "UTM campaign", "utm_campaign", "confirmed_in_dictionary", "clear", None),
        ("utm_term", "UTM term", "utm_term", "confirmed_in_dictionary", "clear", None),
        ("utm_content", "UTM content", "utm_content", "confirmed_in_dictionary", "clear", None),
        ("market", "Market (us/au)", "Region", "map_values", "clear",
         "us → USA · au → AU (Zoho Region picklist)"),
        ("company_website", "Company website", "Website", "confirmed_in_dictionary", "clear", None),
        ("referrer", "Referrer", "Referrer", "confirmed_in_dictionary", "clear", None),
        ("landing_page_url", "Landing page URL", "Referring_URL", "confirmed_in_dictionary", "clear", None),
        ("role", "Role requested", "Description (line)", "fold_into_description", "clear",
         "Cursor: keep as a Description line for now (no custom field yet)"),
        ("company_size", "Company size", "Description (line)", "fold_into_description", "clear",
         "Cursor: keep as a Description line for now"),
        ("positions_needed", "Seats needed", "Description (line)", "fold_into_description", "clear",
         "Cursor: keep as a Description line for now"),
        ("hiring_timeline", "Hiring timeline", "Description (line)", "fold_into_description", "clear",
         "Cursor: keep as a Description line for now"),
        ("submission_id", "Form submission id", "VC_Submission_ID", "missing_in_zoho", "cursor_parked",
         "Field does not exist yet. Create before writes (dedupe). Not a George homework item."),
        ("gbraid", "iOS click id", "(omit)", "missing_in_zoho", "cursor_parked",
         "Does not exist in Zoho. Omit until we create a field when writes turn on."),
        ("wbraid", "Web click id", "(omit)", "missing_in_zoho", "cursor_parked",
         "Does not exist in Zoho. Omit until we create a field when writes turn on."),
    ]
    rows = []
    parked = []
    sales_later = []
    for app, purpose, zoho, status, clarity, note in app_fields:
        rows.append(
            {
                "app_field": app,
                "plain_label": purpose,
                "purpose": purpose,
                "proposed_zoho_api_name": zoho,
                "module": "Leads (UI: Sales Enquiries)",
                "status": status,
                "clarity": clarity,
                "note": note,
            }
        )
        if clarity == "cursor_parked":
            parked.append(app)
        elif clarity == "sales_later":
            sales_later.append(app)
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "writes_enabled": False,
        "owner": "Cursor",
        "plain_english": (
            "Which form boxes save into which Zoho boxes so we can see paid leads in CRM."
        ),
        "source_app": "vision LeadGate /api/lead payload (vision/lib/zoho/payload.ts)",
        "source_zoho": str(ZOHO_DICT.relative_to(REPO)) if ZOHO_DICT.is_file() else "dictionary missing",
        "approval_required": False,
        "next_step": (
            "Draft parked. Zoho + offline conversions are DEFERRED DURING COLD START "
            "(not cancelled). Do not turn writes on during cold start. "
            "Revisit only after the five-item gate."
        ),
        "notes": [
            "Click id for this org is utm_gclid — not $gclid.",
            "Extras without Zoho fields (role, size, seats, timeline) fold into Description for now.",
            "VC_Submission_ID / gbraid / wbraid: create or omit when writes turn on — not George homework.",
            "Production writes remain OFF. No Zoho writes. No Ads mutate. No new Zapier. No Primary Zoho conversions.",
            "Missing VC_* / .app stamps on current Zoho rows is expected — new forms are not connected. Not a Zoho failure.",
        ],
        "mappings": rows,
        "cursor_parked_fields": parked,
        "sales_later_fields": sales_later,
        # Back-compat for older readers
        "uncertain_fields": parked + sales_later,
    }


def verify_executive_html(path: Path) -> None:
    """Cheap bake checks — fail loud if a stakeholder-facing lie sneaks in.

    Note: path is executive-weekly.html (diagnostic archive). Monthly Executive
    Performance is client-rendered via executive.html + executive.js.
    """
    html_text = path.read_text(encoding="utf-8")
    forbidden = (
        "Google Ads CPL",
        "attributed CPA",
        "paid-search job-order cost",
        "+512% better",
        "+809% better",
        "last 7 days primary",
        "last week’s people mostly didn’t come back",
        "send Job Orders and Placements into the two Ads",
        "Watch next week",
        "may be paid",
        "may-be-paid",
    )
    for phrase in forbidden:
        if phrase in html_text:
            raise SystemExit(f"{path.name} contains forbidden phrase: {phrase}")

    # Structural / safety checks only — do not hardcode week-specific volumes.
    required = (
        "US $",
        "AU A$",
        "id=\"us-spend\"",
        "id=\"au-spend\"",
        "Cost / enquiry",
        "not a Google Ads CPA",
        "id=\"agency-baseline-now\"",
        "Landing pages",
        "Insights",
        "Cost / discovery",
        "How we count",
        "Qualified employer",
    )
    for phrase in required:
        if phrase not in html_text:
            raise SystemExit(f"{path.name} missing required phrase: {phrase}")
    if "all Zoho rows · 14" in html_text:
        raise SystemExit("Cost / enquiry still uses all 14 Zoho rows")
    if "A$28.95" in html_text:
        raise SystemExit("AU Cost / enquiry still uses all-source 14")
    if "US cost / JO this week is blank because ops did not name" in html_text:
        raise SystemExit("US Cost / JO still explained as a blank while Zoho has a JO")
    if re.search(
        r"Cost / job order</span><span class='cell cm'>US</span>"
        r"<span class='cell num tw'>\$[\d,.]+</span>"
        r"<span class='cell num lg'>\$[\d,.]+</span>"
        r"<span class='cell num delta-flat'>—</span>",
        html_text,
    ):
        raise SystemExit("US Cost / JO delta is still a dash while both week and legacy numbers exist")
    # Cost tiles and Ads spend must share the sales-week US figure, not rolling $1,116.
    if 'id="us-spend">$1,116<' in html_text:
        raise SystemExit("US hero spend still shows rolling last-7 $1,116")
    if "delta-bad" in html_text and "Baseline 53" in html_text:
        raise SystemExit("July halo still uses red/green judgment")

    def _assert_week_stack(chunk: str, label: str) -> None:
        keys = (
            "mkt-block us",
            "mkt-block au",
            ">Sales</h2>",
            "Legacy agency comparison",
            'class="how-count"',
        )
        pos = -1
        for key in keys:
            i = chunk.find(key)
            if i < 0:
                raise SystemExit(f"{label} missing {key}")
            if i < pos:
                raise SystemExit(f"{label} stack order wrong around {key}")
            pos = i
        z = chunk.find("Zoho this week")
        sales = chunk.find(">Sales</h2>")
        if z >= 0 and z < sales:
            raise SystemExit(f"{label} still has Zoho census above Sales")

    now_m = re.search(r'id="view-now">(.*?)id="view-frozen"', html_text, flags=re.S)
    frozen_m = re.search(
        r'id="view-frozen"[^>]*>(.*?)id="view-frozen-1016"', html_text, flags=re.S
    )
    launch_m = re.search(
        r'id="view-frozen-1016"[^>]*>(.*?)<p class="mute">', html_text, flags=re.S
    )
    if not now_m or not frozen_m or not launch_m:
        raise SystemExit(f"{path.name} missing view-now / view-frozen / view-frozen-1016")
    _assert_week_stack(now_m.group(1), "This week so far")
    _assert_week_stack(frozen_m.group(1), "Aug 17–23 frozen")
    _assert_week_stack(launch_m.group(1), "Aug 10–16 frozen")
    head = re.search(r'<header class="dash-head">(.*?)</header>', html_text, flags=re.S)
    if not head:
        raise SystemExit(f"{path.name} missing dash-head")
    if "how-count" in head.group(1) or "data-fresh" in head.group(1):
        raise SystemExit("method / freshness text still sits under the Executive heading")
    print(f"{path.name} verify ok")


def verify_launch_control_html(path: Path) -> None:
    """Launch Control is an operating dashboard, not a 144-item dump."""
    html_text = path.read_text(encoding="utf-8")

    required = (
        'id="daily-checks"',
        'id="this-week"',
        'id="waiting-blocked"',
        'id="guardrails"',
        'id="deferred-projects"',
        'id="todo-archive"',
        "aug18-conversions.html",
        "paused challenger ads",
        "aug18-next.html",
        "Do not switch to Maximize Conversions",
        "Competitor campaign is deferred",
        "Lead-quality reconciliation",
        "sales-review.html",
        "Winning-path freeze",
        "Daily checks",
        'data-todo="ads51"',
        'data-todo="ads53"',
        'data-todo="ads50"',
        'data-todo="adsTrustBadges"',
    )
    for phrase in required:
        if phrase not in html_text:
            raise SystemExit(f"launch-control.html missing required phrase: {phrase}")
    if re.search(r'<section[^>]*id="do-today"', html_text):
        raise SystemExit("launch-control.html still has a Today section")
    if "Do these first" in html_text:
        raise SystemExit("launch-control.html still has Do these first")

    def _checkbox_ids(chunk: str) -> list[str]:
        return re.findall(r'data-todo="([^"]+)"', chunk)

    daily_m = re.search(r'id="daily-checks".*?</section>', html_text, flags=re.S)
    week_m = re.search(r'id="this-week".*?</section>', html_text, flags=re.S)
    wait_m = re.search(r'id="waiting-blocked".*?</section>', html_text, flags=re.S)
    guard_m = re.search(r'id="guardrails".*?</section>', html_text, flags=re.S)
    if not (daily_m and week_m and wait_m and guard_m):
        raise SystemExit("launch-control.html missing a required operating section")

    daily_ids = _checkbox_ids(daily_m.group(0))
    week_ids = _checkbox_ids(week_m.group(0))
    if len(daily_ids) != 3:
        raise SystemExit(f"DAILY has {len(daily_ids)} checks; must be exactly 3")
    if len(week_ids) > 8:
        raise SystemExit(f"THIS WEEK has {len(week_ids)} checkboxes; max is 8")
    if 'type="checkbox"' in wait_m.group(0):
        raise SystemExit("WAITING ON TEAM must not contain checkboxes (use clean table)")
    if 'type="checkbox"' in guard_m.group(0):
        raise SystemExit("GUARDRAILS must not contain checkboxes")
    if 'data-todo="adsTrustBadges"' not in html_text:
        raise SystemExit("adsTrustBadges checkbox ID was lost")

    all_ids = re.findall(r'data-todo="([^"]+)"', html_text)
    dupes = [k for k, v in Counter(all_ids).items() if v > 1]
    if dupes:
        raise SystemExit(f"duplicate checkbox IDs: {dupes}")

    def _items_have_owner_and_trigger(chunk: str, label: str) -> None:
        items = re.findall(r"<li\b[^>]*>.*?</li>", chunk, flags=re.S)
        for item in items:
            if "data-todo=" not in item:
                continue
            if 'class="who"' not in item:
                raise SystemExit(f"{label} item missing owner: {item[:160]}")
            if 'class="when"' not in item and "Unblock:" not in item:
                raise SystemExit(f"{label} item missing due/review trigger: {item[:160]}")

    _items_have_owner_and_trigger(week_m.group(0), "THIS WEEK")

    if "Build a paused competitor campaign" in week_m.group(0):
        raise SystemExit("competitor campaign must not be an active Week task")

    print("launch-control.html verify ok")


def main() -> int:
    if not EXEC_JSON.is_file():
        print(f"Missing {EXEC_JSON}", flush=True)
        return 1

    exec_data = load_json(EXEC_JSON)
    is_data = load_json(IS_JSON) if IS_JSON.is_file() else None
    ga4 = load_json(GA4_JSON) if GA4_JSON.is_file() else None
    recovery = load_json(REC_JSON) if REC_JSON.is_file() else None
    halo = load_json(HALO_JSON) if HALO_JSON.is_file() else None
    zoho_week = load_json(ZOHO_WEEK_JSON) if ZOHO_WEEK_JSON.is_file() else None

    bake_au_holly_scoreboard(exec_data)
    lean_us_working_cpl_copy(exec_data)
    patch_operator_narrative(exec_data, is_data)
    EXEC_JSON.write_text(json.dumps(exec_data, indent=2) + "\n", encoding="utf-8")

    # Weekly GA4/LP archive (diagnostic). Monthly pilot report is client-rendered
    # executive.html + executive.js — do not overwrite it here.
    weekly_path = XRAY / "executive-weekly.html"
    weekly_path.write_text(
        bake_executive(exec_data, is_data, ga4, recovery, halo, zoho_week), encoding="utf-8"
    )
    print(f"Wrote {weekly_path}")
    verify_executive_html(weekly_path)

    agency_path = write_agency_baseline_json(recovery)
    print(f"Wrote {agency_path}")

    if not (XRAY / "executive.html").is_file():
        raise SystemExit("executive.html missing — monthly Executive Performance page required")
    if not (XRAY / "executive.js").is_file():
        raise SystemExit("executive.js missing — monthly Executive Performance renderer required")

    verify_launch_control_html(XRAY / "launch-control.html")
    if str(Path(__file__).resolve().parent) not in sys.path:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
    from bake_sales_review import main as bake_sales_review_main
    bake_sales_review_main()
    if halo:
        print(
            "CRM during flight: Stage 1 SE "
            f"{((halo.get('stage1') or {}).get('sales_enquiries') or {}).get('total')} · "
            f"baseline {((halo.get('baseline') or {}).get('sales_enquiries') or {}).get('total')}"
        )

    for name, jpath in (
        ("recovery-audit.html", REC_JSON),
        ("ab-tests.html", EXP_JSON),
    ):
        page = XRAY / name
        if not page.is_file() or not jpath.is_file():
            print(f"Skip embed {name}")
            continue
        text = page.read_text(encoding="utf-8")
        text = re.sub(
            r'<script type="application/json" id="embedded-page-data">.*?</script>\s*',
            "",
            text,
            flags=re.S,
        )
        text = re.sub(
            r"<script>\s*window\.__VC_loadPageData[\s\S]*?</script>\s*",
            "",
            text,
            count=1,
        )
        page.write_text(inject_embedded_json(text, jpath), encoding="utf-8")
        print(f"Embedded {jpath.name} into {name}")

    # experiments.html is a static parked reminder — live scoreboard is ab-tests.html

    proposal = build_zoho_proposal()
    OUT_ZOHO.write_text(json.dumps(proposal, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_ZOHO}")

    md = REPO / "ads-launch" / "zoho" / "FIELD-MAP-PROPOSAL.md"
    clarity_label = {
        "clear": "Clear",
        "cursor_parked": "Cursor parked",
        "sales_later": "Sales later",
    }
    lines = [
        "# Form boxes → Zoho boxes (draft)",
        "",
        proposal["plain_english"],
        "",
        f"Generated: `{proposal['generated_at_utc']}` · **writes OFF** · owner: **Cursor** (not George homework)",
        "",
        "**Status (2026-08-14):** Draft parked. Zoho + offline conversions are **DEFERRED DURING COLD START** — not cancelled. Production writes remain OFF. No Zoho writes. No Ads mutate. No new Zapier. No Primary Zoho conversions.",
        "",
        f"**Next:** {proposal['next_step']}",
        "",
        "## Notes",
        "",
        *[f"- {n}" for n in proposal["notes"]],
        "",
        "## Mapping",
        "",
        "| Form box | Zoho box | Clarity | Note |",
        "|----------|----------|---------|------|",
    ]
    for r in proposal["mappings"]:
        note = r.get("note") or ""
        lines.append(
            f"| {r.get('plain_label') or r['app_field']} (`{r['app_field']}`) | "
            f"`{r['proposed_zoho_api_name']}` | "
            f"{clarity_label.get(r['clarity'], r['clarity'])} | {note} |"
        )
    parked = proposal.get("cursor_parked_fields") or []
    sales = proposal.get("sales_later_fields") or []
    lines += ["", "## Cursor parked (until writes on)", ""]
    if parked:
        lines.append(", ".join(f"`{x}`" for x in parked))
    else:
        lines.append("_None._")
    lines += ["", "## Needs Sales meaning later", ""]
    if sales:
        lines.append(", ".join(f"`{x}`" for x in sales))
    else:
        lines.append(
            "_None on this draft._ Sales meaning for Job Order / Placement stays on Checklist Z2–Z4 — not this map."
        )
    lines.append("")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {md}")
    # Mirror into xray docs so Funnel & CRM link works on deploy
    xray_md = XRAY / "docs" / "ads-launch" / "zoho" / "FIELD-MAP-PROPOSAL.md"
    xray_md.parent.mkdir(parents=True, exist_ok=True)
    xray_md.write_text(md.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {xray_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
