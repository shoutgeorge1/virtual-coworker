#!/usr/bin/env python3
"""Bake live X-ray pages from compiled JSON so dashboards never stick on Loading.

Writes:
  - xray/executive.html (US / AU / agency baseline — numbers inlined)
  - embeds JSON into experiments.html + recovery-audit.html
  - patches operator narrative in executive-snapshot.json to match API facts
  - xray/data/zoho-field-map-proposal.json (read-only draft)

No Ads/Zoho mutations. Run after pulls:

  python3 ads-launch/bake_xray_pages.py
"""

from __future__ import annotations

import html
import json
import re
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
ZOHO_DICT = REPO / "ads-launch" / "ATTRIBUTION-RECOVERY-2026-08-13" / "ZOHO-DICTIONARY.md"
OUT_ZOHO = DATA / "zoho-field-map-proposal.json"

# Locked scoreboard week: Monday–Sunday. Not Mon–Fri. Not “since ads started.”
SCOREBOARD_WEEK_START = "2026-08-10"
SCOREBOARD_WEEK_END = "2026-08-16"
SCOREBOARD_WEEK_LABEL = "Mon Aug 10 – Sun Aug 16"


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


def bake_au_zoho_scoreboard(exec_data: dict) -> None:
    """AU Executive scoreboard is Zoho for the week — not Holly's email, not unknown."""
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
            au["window_start"] = str(week.get("window_start") or "2026-08-10")[:10]
            end_ex = str(week.get("window_end_exclusive") or "2026-08-15")[:10]
            au["window_end"] = (
                date.fromisoformat(end_ex) - timedelta(days=1)
            ).isoformat()

    n_enq = census.get("au_sales_enquiries")
    n_disc = census.get("discovery_scheduled")
    n_jo = census.get("job_order_submitted")
    n_gclid = census.get("au_with_gclid")
    if n_enq is None:
        exec_data["sales_ops_au"] = au
        return

    dates = _iso_dates_inclusive(
        str(au.get("window_start") or "2026-08-10"),
        str(au.get("window_end") or "2026-08-14"),
    )
    metrics = au_stage1_spend_for_dates(exec_data, dates)
    spend = float(metrics["spend"])
    n_enq = int(n_enq)
    n_disc_i = int(n_disc) if n_disc is not None else None
    n_jo_i = int(n_jo) if n_jo is not None else None
    cpl = round(spend / n_enq, 2) if n_enq else None
    cost_call = round(spend / n_disc_i, 2) if n_disc_i else None
    cost_jo = round(spend / n_jo_i, 2) if n_jo_i else None
    label = _week_label_plain(
        str(au.get("window_start") or "2026-08-10"),
        str(au.get("window_end") or "2026-08-16"),
    )
    math_enq = f"A${spend:,.2f} spend ÷ {n_enq} enquiries = A${cpl:,.2f} per enquiry"
    math_call = (
        f"A${spend:,.2f} spend ÷ {n_disc_i} discovery scheduled = A${cost_call:,.2f} per booked call (estimated)"
        if n_disc_i and cost_call is not None
        else None
    )
    why = f"{n_enq} enquiries · {n_disc_i} discovery scheduled · {n_jo_i} job orders."

    au.update(
        {
            "market": "AU",
            "label": label,
            "scoreboard": "zoho",
            "source": "Zoho CRM (AU Sales Enquiries, same dates)",
            "enquiries": n_enq,
            "discovery_scheduled": n_disc_i,
            "job_order_submitted": n_jo_i,
            "sales_calls_booked": n_disc_i,
            "sales_calls_completed": None,
            "call_proxy": "discovery_scheduled",
            "call_proxy_estimated": True,
            "weekly_scoreboard": "zoho",
            "campaigns_for_spend": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
            "spend_usd": spend,
            "spend_note": (
                f"AU Core+Roles {'–'.join([dates[0][5:], dates[-1][5:]]) if dates else ''} "
                "from performance_au by_date (AUD). Friday may be incomplete."
            ),
            "impressions": metrics["impressions"],
            "clicks": metrics["clicks"],
            "avg_cpc_usd": metrics["avg_cpc"],
            "cost_per_enquiry_usd": cpl,
            "cost_per_sales_call_booked_usd": cost_call,
            "cost_per_sales_call_completed_usd": None,
            "cost_per_job_order_usd": cost_jo,
            "math_plain": math_enq,
            "math_booked_call": math_call,
            "holly_context": (
                "Holly: 1 call Fri; expects a job order next week — already in the Zoho week, not added."
            ),
            "ops_note": (
                f"Zoho CRM ({label}): {n_enq} enquiries · {n_disc_i} discovery scheduled · "
                f"{n_jo_i} job orders submitted. {math_enq}. "
                "Cost / call uses Discovery Scheduled as the closest stand-in for booked/completed — estimated. "
                "Holly: 1 call Fri; expects a job order next week — already in the week, not added."
            ),
            "caveat": "Zoho · same week. Working cost = Stage 1 spend ÷ concurrent Zoho counts.",
            "why_plain": why,
            "insight_plain": (
                f"AU Zoho ({label}): {n_enq} enquiries · {n_disc_i} discovery · "
                f"{n_jo_i} job orders · A${cpl:.2f}/enquiry (estimated)."
            ),
            "zoho_census": census,
            "gclid_count": n_gclid,
        }
    )
    exec_data["sales_ops_au"] = au


def lean_us_working_cpl_copy(exec_data: dict) -> None:
    """Cheyenne 14 stays the working US number. No gclid-gate on the scoreboard."""
    us = dict(exec_data.get("sales_ops_us") or {})
    if us.get("enquiries") is None:
        return
    us["caveat"] = "Sales-ops cost uses Cheyenne’s 14 enquiries."
    if ZOHO_WEEK_JSON.is_file():
        week = load_json(ZOHO_WEEK_JSON)
        usa = week.get("usa") or {}
        if usa.get("n") is not None:
            census = dict(us.get("zoho_census") or {})
            census["pinged_utc"] = week.get("generated_at_utc")
            census["usa_sales_enquiries"] = usa.get("n")
            census["usa_with_gclid"] = usa.get("with_utm_gclid")
            us["zoho_census"] = census
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
    if au_ops.get("scoreboard") == "zoho" and au_ops.get("enquiries") is not None:
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


def _kpi_cards(totals: dict | None, cur: str, spend_id: str | None = None) -> str:
    """One period row of spreadsheet-like KPI cards."""
    t = totals or {}
    spend = money(t.get("cost_usd"), cur)
    conv = t.get("conversions")
    conv_s = num(conv) if conv is not None else "—"
    cells = [
        ("Spend", spend, spend_id),
        ("Clicks", num(t.get("clicks")), None),
        ("Impr.", num(t.get("impressions")), None),
        ("CTR", pct(t.get("ctr_pct")), None),
        ("CPC", money2(t.get("avg_cpc_usd"), cur), None),
        ("Ads conv", conv_s, None),
    ]
    bits = []
    for label, val, vid in cells:
        id_attr = f' id="{html.escape(vid)}"' if vid else ""
        bits.append(
            f'<div class="kpi">'
            f'<span class="k">{html.escape(label)}</span>'
            f'<span class="v num"{id_attr}>{html.escape(val)}</span>'
            f"</div>"
        )
    return "\n          ".join(bits)


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
    market: str, this_s: str, leg_s: str, css: str, delta: str
) -> str:
    """One market line. Cells are direct grid children so every column lines up."""
    return (
        f"<span class='cell cm'>{html.escape(market)}</span>"
        f"<span class='cell num tw'>{html.escape(this_s)}</span>"
        f"<span class='cell num lg'>{html.escape(leg_s)}</span>"
        f"<span class='cell num {html.escape(css)}'>{html.escape(delta)}</span>"
    )


def _legacy_group(
    title: str,
    us: tuple[str, str, str, str],
    au: tuple[str, str, str, str],
) -> str:
    """Metric block: a full-width label row, then US and AU on the shared grid."""
    return (
        f"<span class='cell grp'>{html.escape(title)}</span>"
        f"{_legacy_row('US', *us)}{_legacy_row('AU', *au)}"
    )


def _legacy_sheet(groups: str, band: str, band_note: str = "") -> str:
    """One band (Ads or Sales) — its own label, one shared four-column grid."""
    note = (
        f"<span class='cmp-band-note'>{html.escape(band_note)}</span>" if band_note else ""
    )
    return (
        "<div class='cmp-band'>"
        f"<div class='cmp-band-hd'><h3>{html.escape(band)}</h3>{note}</div>"
        "<div class='cmp-sheet'>"
        "<span class='cell hd'></span>"
        "<span class='cell hd num'>This week</span>"
        "<span class='cell hd num'>Legacy week</span>"
        "<span class='cell hd num'>Δ</span>"
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


def _cost_per_jo_note(zjo: dict) -> str:
    """Say out loud which job orders sit under the legacy cost / JO."""
    us_n = zjo.get("us_jo")
    au_n = zjo.get("au_jo")
    if us_n is None and au_n is None:
        return "Legacy cost / JO not available."
    return (
        "Legacy cost / JO is agency spend ÷ the job orders in the Zapier CRM extract "
        f"({html.escape(num(us_n))} US · {html.escape(num(au_n))} AU) — the whole extract "
        "we hold for those years, not a paid-only slice. US cost / JO this week is blank "
        "because ops did not name a US job order."
    )


def _sales_band_note(
    us_enq: Any,
    au_enq: Any,
    us_ops_enq: Any,
    legacy_enq: dict,
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
) -> str:
    """This week vs the full legacy-agency run — an Ads band and a Sales band."""
    us_ctr_css, us_ctr_d = _times_higher(us_week.get("ctr_pct"), bus.get("ctr_pct"))
    au_ctr_css, au_ctr_d = _times_higher(au_week.get("ctr_pct"), bau.get("ctr_pct"))
    us_cpc_css, us_cpc_d = _pct_lower(us_week.get("avg_cpc_usd"), bus.get("avg_cpc"))
    au_cpc_css, au_cpc_d = _pct_lower(au_week.get("avg_cpc_usd"), bau.get("avg_cpc"))
    au_jo = cpl_au.get("cost_per_job_order_usd")
    jo_us_leg = zjo.get("cost_per_jo_us")
    jo_au_leg = zjo.get("cost_per_jo_au")
    au_jo_css, au_jo_d = _pct_lower(au_jo, jo_au_leg) if au_jo is not None else ("delta-flat", "—")
    weeks = _inclusive_days(legacy_window)
    weeks7 = (weeks / 7.0) if weeks else None
    us_week_avg = _typical_7d(bus.get("cost"), legacy_window)
    au_week_avg = _typical_7d(bau.get("cost"), legacy_window)
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
    us_jo_avg = _week_avg_plain(zjo.get("us_jo"), weeks7)
    au_jo_avg = _week_avg_plain(zjo.get("au_jo"), weeks7)
    us_disc_avg = _week_avg_plain(zjo.get("us_discovery"), weeks7)
    au_disc_avg = _week_avg_plain(zjo.get("au_discovery"), weeks7)
    us_jo_vol_css, us_jo_vol_d = _volume_vs(
        us_jo_w, _typical_7d(zjo.get("us_jo"), legacy_window)
    )
    au_jo_vol_css, au_jo_vol_d = _volume_vs(
        au_jo_w, _typical_7d(zjo.get("au_jo"), legacy_window)
    )
    us_disc_vol_css, us_disc_vol_d = _volume_vs(
        us_disc_w, _typical_7d(zjo.get("us_discovery"), legacy_window)
    )
    au_disc_vol_css, au_disc_vol_d = _volume_vs(
        au_disc_w, _typical_7d(zjo.get("au_discovery"), legacy_window)
    )
    us_leg_enq = _legacy_enq_week((legacy_enq or {}).get("us"))
    au_leg_enq = _legacy_enq_week((legacy_enq or {}).get("au"))
    us_enq_css, us_enq_d = _volume_vs(us_enq, us_leg_enq)
    au_enq_css, au_enq_d = _volume_vs(au_enq, au_leg_enq)

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
                "Cost / JO",
                ("—", money(jo_us_leg, "USD") if jo_us_leg else "—", "delta-flat", "—"),
                (
                    money2(au_jo, "AUD") if au_jo is not None else "—",
                    money(jo_au_leg, "AUD") if jo_au_leg else "—",
                    au_jo_css,
                    au_jo_d,
                ),
            ),
        ]
    )
    sales = "".join(
        [
            _legacy_group(
                "Enquiries",
                (num(us_enq), _num1(us_leg_enq), us_enq_css, us_enq_d),
                (num(au_enq), _num1(au_leg_enq), au_enq_css, au_enq_d),
            ),
            _legacy_group(
                "Job orders",
                (num(us_jo_w), us_jo_avg, us_jo_vol_css, us_jo_vol_d),
                (num(au_jo_w), au_jo_avg, au_jo_vol_css, au_jo_vol_d),
            ),
            _legacy_group(
                "Discovery",
                (num(us_disc_w), us_disc_avg, us_disc_vol_css, us_disc_vol_d),
                (num(au_disc_w), au_disc_avg, au_disc_vol_css, au_disc_vol_d),
            ),
        ]
    )
    ads_note = _cost_per_jo_note(zjo)
    sales_note = _sales_band_note(
        us_enq, au_enq, cpl.get("enquiries"), (legacy_enq or {})
    )
    return f"""        {_legacy_sheet(boxes, "Ads", "Google Ads · both accounts")}
        <p class="cmp-note">{ads_note}</p>
        {_legacy_sheet(sales, "Sales", "Zoho rows · same week as the cards")}
        <p class="cmp-note">{sales_note}</p>
        <dl class="windows">
          <div><dt>This week</dt><dd>{html.escape(week_label)}</dd></div>
          <div><dt>Legacy agency</dt><dd>{html.escape(_human_span(legacy_window))}</dd></div>
          <div><dt>GA4</dt><dd>{html.escape(_ga4_window_plain(ga4))}</dd></div>
        </dl>"""


def _ga4_now_box(title: str, us_s: str, au_s: str) -> str:
    return (
        '<div class="legacy-box">'
        f"<h3>{html.escape(title)}</h3>"
        "<table><tbody>"
        f"<tr><th scope='row'>US</th><td class='num this-w'>{html.escape(us_s)}</td></tr>"
        f"<tr><th scope='row'>AU</th><td class='num this-w'>{html.escape(au_s)}</td></tr>"
        "</tbody></table></div>"
    )


def _ga4_bottom_html(ga4: dict | None) -> str:
    """Our GA4 only — no old-agency property to compare."""
    if not ga4:
        return ""
    us = ga4.get("totals_last_7_days") or {}
    au = (ga4.get("au") or {}).get("totals_last_7_days") or {}
    us_paid, _ = _ga4_paid_sessions(ga4, "US")
    au_paid, _ = _ga4_paid_sessions(ga4, "AU")
    us_ty = (ga4.get("path_kind_sessions") or {}).get("thank_you")
    if us_ty is None:
        us_ty = (ga4.get("landing_compare") or {}).get("thank_you_sessions")
    au_ty = (ga4.get("au") or {}).get("thank_you_sessions")
    us_dev = {str(r.get("device")): r.get("sessions") for r in (ga4.get("devices") or [])}
    au_block = ga4.get("au") or {}
    au_dev = {str(r.get("device")): r.get("sessions") for r in (au_block.get("devices") or [])}
    boxes = "".join(
        [
            _ga4_now_box("Sessions", num(us.get("sessions")), num(au.get("sessions"))),
            _ga4_now_box("Users", num(us.get("users")), num(au.get("users"))),
            _ga4_now_box(
                "Stayed",
                pct(us.get("engagement_rate_pct")),
                pct(au.get("engagement_rate_pct")),
            ),
            _ga4_now_box(
                "Bounce",
                pct(us.get("bounce_rate_pct")),
                pct(au.get("bounce_rate_pct")),
            ),
            _ga4_now_box("Paid search", num(us_paid), num(au_paid)),
            _ga4_now_box("Thank-you", num(us_ty), num(au_ty)),
            _ga4_now_box("Mobile", num(us_dev.get("mobile")), num(au_dev.get("mobile"))),
            _ga4_now_box("Desktop", num(us_dev.get("desktop")), num(au_dev.get("desktop"))),
            _ga4_now_box(
                "Time on site",
                _secs_plain(us.get("avg_session_seconds")),
                _secs_plain(au.get("avg_session_seconds")),
            ),
        ]
    )
    return f"""
      <section class="ga4-now" id="ga4" aria-label="Google Analytics">
        <div class="sec-hd">
          <h2>Google Analytics</h2>
          <p class="sec-meta">{html.escape(_ga4_window_plain(ga4))}</p>
        </div>
        <div class="legacy-grid ga4-grid">{boxes}</div>
        <p class="mute ga4-foot">No old-agency GA4 to compare.</p>
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
        se_us = usa.get("n")
        se_au = au.get("n")
        se_total = zoho_week.get("leads_in_window")
        jo_us = _zoho_status(usa, "Job Order Submitted")
        jo_au = _zoho_status(au, "Job Order Submitted")
        jo_total = (jo_us or 0) + (jo_au or 0) if (jo_us is not None or jo_au is not None) else None
        disc_us = usa.get("discovery_scheduled")
        disc_au = au.get("discovery_scheduled")
        disc_total = (
            (disc_us or 0) + (disc_au or 0)
            if (disc_us is not None or disc_au is not None)
            else None
        )
        frame = f"{week_label} · every row Zoho created this week"
        se_sub = f"US {num(se_us)} · AU {num(se_au)}"
        jo_sub = f"US {num(jo_us)} · AU {num(jo_au)}"
        disc_sub = f"US {num(disc_us)} · AU {num(disc_au)}"
    else:
        se_total = se.get("total")
        jo_total = jo.get("total")
        disc_total = s1.get("discovery_scheduled")
        frame = f"{s1.get('start') or '?'} → {s1.get('end') or '?'} · every row Zoho created"
        se_sub = f"US {num(se.get('usa'))} · AU {num(se.get('au'))}"
        jo_sub = f"US {num(jo.get('usa'))} · AU {num(jo.get('au'))}"
        disc_sub = ""
    return f"""
      <section class="halo" id="crm-activity" aria-label="Zoho this week">
        <div class="sec-hd">
          <h2>Zoho this week</h2>
          <p class="sec-meta">{html.escape(frame)}</p>
        </div>
        <div class="kpi-row halo-kpi">
{_halo_metric_card("Sales Enquiries", se_total, sub=se_sub)}
{_halo_metric_card("Job Orders", jo_total, sub=jo_sub)}
{_halo_metric_card("Discovery scheduled", disc_total, sub=disc_sub)}
        </div>
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
                  <td>Sales Enquiries</td>
                  <td class="num">{html.escape(num(se.get("total")))}</td>
                  <td class="num mute">{html.escape(num(bse.get("total")))}</td>
                </tr>
                <tr>
                  <td>Job Orders</td>
                  <td class="num">{html.escape(num(jo.get("total")))}</td>
                  <td class="num mute">{html.escape(num(bjo.get("total")))}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </details>
      </section>
"""


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


def _ga4_paid_sessions(ga4: dict | None, market: str) -> tuple[Any, str]:
    """Paid Search sessions from GA4. Window is rolling — not the sales week."""
    if not ga4:
        return None, "GA4 snapshot missing"
    if market == "AU":
        au = ga4.get("au") or {}
        n = au.get("paid_search_sessions")
        win = au.get("window") or "rolling 7d"
        return n, f"GA4 AU Paid Search · {win} — not the sales week"
    for ch in ga4.get("channels") or []:
        if ch.get("channel") == "Paid Search":
            win = ga4.get("window") or "rolling 7d"
            return ch.get("sessions"), f"GA4 US Paid Search · {win} — not the sales week"
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
        qual = ops.get("discovery_scheduled")
        qual_label = "Discovery scheduled"
        jo = ops.get("job_order_submitted")
        jo_note = "Zoho Job Order Submitted · same week · not last-click paid"

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
            "GA4 form_start · rolling window · diagnostic, not a qualified lead"
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
        "GA4 steps use a rolling window and are not joined by click ID — no step-to-step rate.</p>"
    )


def _crm_readiness_html() -> str:
    """Compact operational checklist. Field names existing ≠ Confirmed."""
    rows = [
        ("Destination CRM module", "Needs review", "Live CRM is WordPress + Zapier + humans. .app forms email us@ / apac@ — not writing to Zoho."),
        ("Employer vs job-seeker classification", "Needs review", "Cheyenne labels looking-for-work / PH job-seeker in email. Form gate exists in spec; not proven on every CRM row."),
        ("Persistent GCLID field", "Missing", "Dictionary has utm_gclid. Stage 1: 0 of 51 Sales Enquiries store a click ID. After ~5 Aug new Zoho rows stopped storing it."),
        ("Persistent GBRAID / WBRAID", "Missing", "No Zoho fields. Parked until writes turn on."),
        ("UTM fields", "Not tested", "utm_source / medium / campaign exist in the dictionary. Stage 1 Zoho rows are mostly blank."),
        ("Original landing page", "Not tested", "Mapped to Referring_URL in the draft. Not proven on Stage 1 rows."),
        ("Lead-created timestamp", "Confirmed", "Zoho Created_Time is what the halo census uses."),
        ("Deduplication rule", "Missing", "VC_Submission_ID does not exist yet."),
        ("Lifecycle stage definitions", "Needs review", "Zoho statuses exist (Discovery Scheduled, Job Order Submitted, etc.). Not a locked Stage 1 contract."),
        ("Sales ownership", "Confirmed", "Cheyenne Gichana = US. Holly Wallace = APAC / AU."),
        ("Qualified-lead definition", "Needs review", "No single documented qualified-employer definition on this scoreboard."),
        ("Job-order definition", "Needs review", "AU uses Zoho Job Order Submitted for the week. US JO was not named this week."),
        ("Placement definition", "Missing", "Not on the scoreboard. Do not treat JO as placement."),
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
    au_jo = num(au_ops.get("job_order_submitted"))
    items = [
        (
            f"First complete Stage 1 sales week (Mon–Fri): US {html.escape(us_spend)} and "
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
            f"{html.escape(au_jo)} job orders (Zoho). 0 click IDs. Do not add email + Zoho. Stay on Max Clicks."
        ),
    ]
    lis = "".join(f"<li>{item}</li>" for item in items)
    return f'<ul class="exec-sum">{lis}</ul>'


def _week_heading(ops: dict) -> str:
    return html.escape(str(ops.get("label") or SCOREBOARD_WEEK_LABEL))


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
    crm_ready = _crm_readiness_html()

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
        """US only: quiet CRM count. AU Zoho is the scoreboard — not a footnote."""
        if market == "AU" or data.get("scoreboard") == "zoho":
            return ""
        census = data.get("zoho_census") or (data.get("attribution_watch") or {}).get("zoho") or {}
        if not census:
            return ""
        n_se = census.get("usa_sales_enquiries")
        if n_se is None:
            return ""
        return (
            f"<p class='mute zoho-census'>Zoho census, same dates: "
            f"{html.escape(num(n_se))} rows — a wider net over the same people, "
            "not extra enquiries.</p>"
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
        zoho_board = market == "AU" and (
            data.get("scoreboard") == "zoho" or data.get("cost_per_enquiry_usd") is not None
        )
        enq = data.get("cost_per_enquiry_usd")
        booked = data.get("cost_per_sales_call_completed_usd")
        call_word = "completed call"
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
            if zoho_board:
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
                    quality.append(f"{data.get('philippines_job_seekers')} PH job-seeker")
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
        call_k = f"Cost / {call_word}"
        enq_est = enq is not None
        call_sub = (
            '<span class="sub">estimated</span>'
            if booked is not None
            else '<span class="sub">&nbsp;</span>'
        )
        enq_sub = (
            '<span class="sub">estimated</span>' if enq_est else '<span class="sub">&nbsp;</span>'
        )
        jo_cost = data.get("cost_per_job_order_usd") if zoho_board else None
        if jo_cost is not None:
            jo_v = money2(jo_cost, cur)
            jo_sub = '<span class="sub">estimated</span>'
        else:
            jo_v = "—"
            jo_sub = '<span class="sub">&nbsp;</span>'
        cards = (
            f'<div class="kpi kpi-emph"><span class="k">Cost / enquiry</span>'
            f'<span class="v num">{html.escape(enq_v)}</span>{enq_sub}</div>\n'
            f'          <div class="kpi kpi-emph"><span class="k">{html.escape(call_k)}</span>'
            f'<span class="v num">{html.escape(booked_v)}</span>{call_sub}</div>\n'
            f'          <div class="kpi kpi-emph"><span class="k">Cost / JO</span>'
            f'<span class="v num">{html.escape(jo_v)}</span>{jo_sub}</div>'
        )
        footer = f'<p class="mkt-note mute">{note}</p>\n          {extra}'
        return cards, footer

    us_cost, us_cost_foot = _lead_cost_parts("US", cpl, "USD", us_week.get("conversions"))
    au_cost, au_cost_foot = _lead_cost_parts("AU", cpl_au, "AUD", au_week.get("conversions"))

    bus = baseline.get("us") or {}
    bau = baseline.get("au") or {}
    zjo = baseline.get("zoho_jo") or {}

    legacy_html = _legacy_agency_table(
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
    body[data-page="executive.html"] .main {{
      max-width: 1120px;
      font-variant-numeric: tabular-nums;
    }}
    .dash-head {{ margin: 0 0 0.65rem; }}
    .dash-head h1 {{ margin: 0; font-size: 1.3rem; }}
    .dash-head .asof {{ margin: 0.25rem 0 0; font-size: 0.8rem; color: var(--muted); }}
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
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .mkt-block .bud {{
      margin: 0;
      font-size: 0.82rem;
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
    .kpi.kpi-emph {{
      border: 2px solid var(--accent-hot);
      background: var(--tint-teal);
      box-shadow: inset 3px 0 0 var(--accent-hot);
      padding: 0.55rem 0.55rem 0.5rem;
    }}
    .kpi.kpi-emph .k {{
      font-size: 0.74rem;
      color: var(--accent-hot);
    }}
    .kpi.kpi-emph .v {{
      font-size: 1.48rem;
    }}
    .kpi .k {{
      display: block;
      font-size: 0.68rem;
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
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      line-height: 1.15;
      color: var(--ink);
    }}
    .kpi .sub {{
      display: block;
      margin-top: 0.22rem;
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--muted);
      line-height: 1.3;
      white-space: normal;
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
    .week-costs .kpi,
    .week-ads .kpi {{
      min-height: 4.85rem;
    }}
    .week-costs .kpi-emph .k {{ font-size: 0.68rem; }}
    .week-costs .kpi-emph .v {{ font-size: 1.35rem; }}
    .week-ads .kpi .v {{ font-size: 1.18rem; }}
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
    .ga4-grid .legacy-box table {{ font-size: 0.92rem; font-variant-numeric: tabular-nums; }}
    .ga4-grid .legacy-box th,
    .ga4-grid .legacy-box td {{ padding: 0.16rem 0; border-bottom: none; }}
    .ga4-grid .legacy-box tr + tr th,
    .ga4-grid .legacy-box tr + tr td {{ border-top: 1px solid rgba(0,0,0,0.06); }}
    .ga4-grid .legacy-box th[scope="row"] {{
      font-size: 0.68rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
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
  </style>
</head>
<body data-page="executive.html" data-foot="US · AU · baseline · baked">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="dash-head">
        <h1>Executive</h1>
        <p class="asof" id="asof">{html.escape(str(cpl.get("label") or SCOREBOARD_WEEK_LABEL))} · US $ · AU A$</p>
      </header>

      <section class="mkt-block us" id="market-us" aria-label="United States">
        <div class="mkt-hd">
          <h2>United States</h2>
          <p class="bud">Core ${(core_us.get("daily_budget_usd") or 150):.0f} + Roles ${(roles_us.get("daily_budget_usd") or 100):.0f}/day · Exact/Phrase · Max Clicks</p>
        </div>
        <div class="period week-group">
          <h3>{_week_heading(cpl)}</h3>
          <div class="kpi-row week-costs">
          {us_cost}
          </div>
          <div class="kpi-row week-ads">
          {_kpi_cards(us_week, "USD", spend_id="us-spend")}
          </div>
          {us_cost_foot}
        </div>
      </section>

      <section class="mkt-block au" id="market-au" aria-label="Australia">
        <div class="mkt-hd">
          <h2>Australia</h2>
          <p class="bud">Core A${(core_au.get("daily_budget_usd") or 75):.0f} + Roles A${(roles_au.get("daily_budget_usd") or 50):.0f}/day</p>
        </div>
        <div class="period week-group">
          <h3>{_week_heading(cpl_au)}</h3>
          <div class="kpi-row week-costs">
          {au_cost}
          </div>
          <div class="kpi-row week-ads">
          {_kpi_cards(au_week, "AUD", spend_id="au-spend")}
          </div>
          {au_cost_foot}
        </div>
      </section>

{_halo_section(halo, zoho_week, str(cpl.get("label") or SCOREBOARD_WEEK_LABEL))}
{crm_ready}

      <section class="baseline" id="agency-baseline">
        <div class="sec-hd">
          <h2>Legacy agency comparison</h2>
          <p class="sec-meta">This week vs their typical 7-day week</p>
        </div>
{legacy_html}
      </section>
{ga4_html}
      <p class="mute"><a href="launch-control.html">Checklist → Launch steps</a></p>

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
    """Cheap bake checks — fail loud if a stakeholder-facing lie sneaks in."""
    html_text = path.read_text(encoding="utf-8")
    forbidden = (
        "Google Ads CPL",
        "attributed CPA",
        "paid-search job-order cost",
        "+512% better",
        "+809% better",
        "last 7 days primary",
    )
    for phrase in forbidden:
        if phrase in html_text:
            raise SystemExit(f"executive.html contains forbidden phrase: {phrase}")
    required = (
        "US $",
        "AU A$",
        "id=\"us-spend\"",
        "id=\"au-spend\"",
        "Cost / enquiry",
        "estimated",
    )
    for phrase in required:
        if phrase not in html_text:
            raise SystemExit(f"executive.html missing required phrase: {phrase}")
    # Cost tiles and Ads spend must share the sales-week US figure, not rolling $1,116.
    if 'id="us-spend">$1,116<' in html_text:
        raise SystemExit("US hero spend still shows rolling last-7 $1,116")
    if "delta-bad" in html_text and "Baseline 53" in html_text:
        raise SystemExit("July halo still uses red/green judgment")
    print("executive.html verify ok")


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

    bake_au_zoho_scoreboard(exec_data)
    lean_us_working_cpl_copy(exec_data)
    patch_operator_narrative(exec_data, is_data)
    EXEC_JSON.write_text(json.dumps(exec_data, indent=2) + "\n", encoding="utf-8")

    (XRAY / "executive.html").write_text(
        bake_executive(exec_data, is_data, ga4, recovery, halo, zoho_week), encoding="utf-8"
    )
    print(f"Wrote {XRAY / 'executive.html'}")
    verify_executive_html(XRAY / "executive.html")
    if halo:
        print(
            "CRM during flight: Stage 1 SE "
            f"{((halo.get('stage1') or {}).get('sales_enquiries') or {}).get('total')} · "
            f"baseline {((halo.get('baseline') or {}).get('sales_enquiries') or {}).get('total')}"
        )

    for name, jpath in (
        ("recovery-audit.html", REC_JSON),
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

    # experiments.html is a static parked page — do not re-inject KPI theater

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
