#!/usr/bin/env python3
"""Read-only budget + Maximize Conversions readiness probe (US + AU).

George authorized comprehensive read-only pulls for budget/bid analysis.
Data through yesterday (complete days only). No mutations.

Outputs: .local/ads/budget-bid-decision-2026-08-26.json
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
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

if (SG_ROOT / ".env").is_file():
    load_dotenv(SG_ROOT / ".env")
_vc_env = SG_ROOT / "clients" / "virtual-coworker.env"
if _vc_env.is_file():
    load_dotenv(_vc_env, override=True)

US_ID = "4967151855"
AU_ID = "5735391940"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local" / "ads" / "budget-bid-decision-2026-08-26.json"

# Complete through yesterday (Aug 25, 2026 PT calendar)
END = date(2026, 8, 25)
US_LAUNCH = date(2026, 8, 6)
AU_LAUNCH = date(2026, 8, 9)
PULL_START = date(2026, 8, 3)  # buffer before launch

TARGET_CAMPAIGNS = {
    "VC_US_S_CORE",
    "VC_US_S_ROLES",
    "VC_AU_S_CORE",
    "VC_AU_S_ROLES",
}

MAX_CALLS = 12
CALLS = 0
STOPPED: str | None = None


def _enum(val: Any) -> str:
    if val is None:
        return ""
    name = getattr(val, "name", None)
    return str(name) if name else str(val or "")


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _share_pct(val: Any) -> float | None:
    try:
        n = float(val)
    except (TypeError, ValueError):
        return None
    if n < 0:
        return None
    return round(100.0 * n, 1)


def run_q(client: Any, customer_id: str, name: str, query: str) -> dict[str, Any]:
    global CALLS, STOPPED
    if STOPPED:
        return {"ok": False, "name": name, "error": STOPPED, "rows": []}
    if CALLS >= MAX_CALLS:
        STOPPED = "cap"
        return {"ok": False, "name": name, "error": "cap", "rows": []}
    CALLS += 1
    print(f"GAQL {CALLS}/{MAX_CALLS} {name} {customer_id}", flush=True)
    try:
        rows = list(run_gaql(client, customer_id, query))
    except QuotaExhaustedError as exc:
        STOPPED = "RESOURCE_EXHAUSTED"
        return {"ok": False, "name": name, "error": "RESOURCE_EXHAUSTED", "detail": str(exc)[:240], "rows": []}
    except (ApiAccessError, SgGoogleAdsError) as exc:
        return {"ok": False, "name": name, "error": type(exc).__name__, "detail": str(exc)[:240], "rows": []}
    return {"ok": True, "name": name, "row_count": len(rows), "raw": rows}


CAMPAIGN_DAILY_Q = """
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.bidding_strategy_type,
      campaign.target_spend.cpc_bid_ceiling_micros,
      campaign.maximize_conversions.target_cpa_micros,
      campaign_budget.amount_micros,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.average_cpc,
      metrics.conversions,
      metrics.all_conversions,
      metrics.conversions_value,
      metrics.search_impression_share,
      metrics.search_rank_lost_impression_share,
      metrics.search_budget_lost_impression_share,
      metrics.search_top_impression_share,
      metrics.search_absolute_top_impression_share
    FROM campaign
    WHERE campaign.name IN ('VC_US_S_CORE','VC_US_S_ROLES','VC_AU_S_CORE','VC_AU_S_ROLES')
      AND campaign.status != REMOVED
      AND segments.date BETWEEN '{start}' AND '{end}'
"""

CONV_BY_ACTION_Q = """
    SELECT
      campaign.name,
      segments.date,
      segments.conversion_action,
      segments.conversion_action_name,
      segments.conversion_action_category,
      metrics.conversions,
      metrics.all_conversions,
      metrics.conversions_value
    FROM campaign
    WHERE campaign.name IN ('VC_US_S_CORE','VC_US_S_ROLES','VC_AU_S_CORE','VC_AU_S_ROLES')
      AND segments.date BETWEEN '{start}' AND '{end}'
"""

CONV_ACTION_SETTINGS_Q = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.status,
      conversion_action.type,
      conversion_action.category,
      conversion_action.origin,
      conversion_action.primary_for_goal,
      conversion_action.counting_type,
      conversion_action.include_in_conversions_metric
    FROM conversion_action
    WHERE conversion_action.status != REMOVED
"""

DEVICE_Q = """
    SELECT
      campaign.name,
      segments.device,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.all_conversions
    FROM campaign
    WHERE campaign.name IN ('VC_US_S_CORE','VC_US_S_ROLES','VC_AU_S_CORE','VC_AU_S_ROLES')
      AND segments.date BETWEEN '{start}' AND '{end}'
      AND metrics.clicks > 0
"""

LANDING_Q = """
    SELECT
      campaign.name,
      landing_page_view.unexpanded_final_url,
      segments.date,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.all_conversions
    FROM landing_page_view
    WHERE campaign.name IN ('VC_US_S_CORE','VC_US_S_ROLES','VC_AU_S_CORE','VC_AU_S_ROLES')
      AND segments.date BETWEEN '{start}' AND '{end}'
      AND metrics.clicks > 0
"""


def parse_campaign_daily(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        ts = getattr(row.campaign, "target_spend", None)
        mc = getattr(row.campaign, "maximize_conversions", None)
        out.append(
            {
                "campaign": row.campaign.name,
                "status": _enum(row.campaign.status),
                "bidding_strategy_type": _enum(getattr(row.campaign, "bidding_strategy_type", None)),
                "cpc_bid_ceiling": _money(getattr(ts, "cpc_bid_ceiling_micros", None)) if ts else None,
                "max_conv_target_cpa": _money(getattr(mc, "target_cpa_micros", None)) if mc else None,
                "daily_budget": _money(getattr(row.campaign_budget, "amount_micros", None)),
                "date": str(row.segments.date),
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "cost": _money(row.metrics.cost_micros),
                "avg_cpc": _money(getattr(row.metrics, "average_cpc", None)),
                "conversions": float(row.metrics.conversions or 0),
                "all_conversions": float(row.metrics.all_conversions or 0),
                "conversions_value": float(row.metrics.conversions_value or 0),
                "search_is_pct": _share_pct(getattr(row.metrics, "search_impression_share", None)),
                "lost_is_rank_pct": _share_pct(getattr(row.metrics, "search_rank_lost_impression_share", None)),
                "lost_is_budget_pct": _share_pct(getattr(row.metrics, "search_budget_lost_impression_share", None)),
                "search_top_is_pct": _share_pct(getattr(row.metrics, "search_top_impression_share", None)),
                "search_abs_top_is_pct": _share_pct(getattr(row.metrics, "search_absolute_top_impression_share", None)),
            }
        )
    return out


def parse_conv_actions(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        resource = str(row.segments.conversion_action or "")
        action_id = resource.rsplit("/", 1)[-1] if resource else ""
        out.append(
            {
                "campaign": row.campaign.name,
                "date": str(row.segments.date),
                "action_id": action_id,
                "action": row.segments.conversion_action_name,
                "category": _enum(row.segments.conversion_action_category),
                "conversions": float(row.metrics.conversions or 0),
                "all_conversions": float(row.metrics.all_conversions or 0),
                "value": float(row.metrics.conversions_value or 0),
            }
        )
    return out


def parse_conv_settings(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        ca = row.conversion_action
        out.append(
            {
                "id": str(getattr(ca, "id", "") or ""),
                "name": ca.name,
                "status": _enum(ca.status),
                "type": _enum(ca.type_),
                "category": _enum(ca.category),
                "origin": _enum(getattr(ca, "origin", None)),
                "primary_for_goal": bool(getattr(ca, "primary_for_goal", False)),
                "counting_type": _enum(ca.counting_type),
                "include_in_conversions_metric": bool(getattr(ca, "include_in_conversions_metric", False)),
            }
        )
    return out


def _avg_share(vals: list[float | None], weights: list[int]) -> float | None:
    num = den = 0
    for v, w in zip(vals, weights):
        if v is None or w <= 0:
            continue
        num += float(v) * w
        den += w
    return round(num / den, 1) if den else None


def aggregate_window(
    daily: list[dict[str, Any]], start: date, end: date, launch: date | None = None
) -> dict[str, dict[str, Any]]:
    eff_start = max(start, launch) if launch else start
    by_camp: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in daily:
        d = date.fromisoformat(r["date"])
        if eff_start <= d <= end:
            by_camp[r["campaign"]].append(r)

    out: dict[str, dict[str, Any]] = {}
    days_in_window = (end - eff_start).days + 1
    for camp, rows in by_camp.items():
        impr = sum(r["impressions"] for r in rows)
        clicks = sum(r["clicks"] for r in rows)
        cost = sum(r["cost"] for r in rows)
        conv = sum(r["conversions"] for r in rows)
        all_conv = sum(r["all_conversions"] for r in rows)
        weights = [r["impressions"] for r in rows]
        days_with_spend = len({r["date"] for r in rows if r["cost"] > 0})
        out[camp] = {
            "window_start": eff_start.isoformat(),
            "window_end": end.isoformat(),
            "days": days_in_window,
            "days_with_spend": days_with_spend,
            "status": rows[0]["status"] if rows else None,
            "bidding_strategy_type": rows[0]["bidding_strategy_type"] if rows else None,
            "cpc_bid_ceiling": rows[0].get("cpc_bid_ceiling") if rows else None,
            "max_conv_target_cpa": rows[0].get("max_conv_target_cpa") if rows else None,
            "daily_budget": rows[-1].get("daily_budget") if rows else None,
            "impressions": impr,
            "clicks": clicks,
            "ctr_pct": round(100 * clicks / impr, 2) if impr else None,
            "cost": round(cost, 2),
            "avg_cpc": round(cost / clicks, 2) if clicks else None,
            "avg_daily_spend": round(cost / days_with_spend, 2) if days_with_spend else 0,
            "budget_utilization_pct": round(100 * (cost / days_with_spend) / rows[-1]["daily_budget"], 1)
            if rows and rows[-1].get("daily_budget")
            else None,
            "conversions": round(conv, 2),
            "all_conversions": round(all_conv, 2),
            "cost_per_conversion": round(cost / conv, 2) if conv else None,
            "search_is_pct": _avg_share([r.get("search_is_pct") for r in rows], weights),
            "lost_is_rank_pct": _avg_share([r.get("lost_is_rank_pct") for r in rows], weights),
            "lost_is_budget_pct": _avg_share([r.get("lost_is_budget_pct") for r in rows], weights),
            "search_top_is_pct": _avg_share([r.get("search_top_is_pct") for r in rows], weights),
            "search_abs_top_is_pct": _avg_share([r.get("search_abs_top_is_pct") for r in rows], weights),
        }
    return out


def classify_action(name: str) -> str:
    n = (name or "").lower()
    if "thank" in n or "form" in n and "submit" in n:
        return "thank_you_form"
    if "calendly" in n or "book" in n and "call" in n:
        return "calendly"
    if "phone" in n and "click" in n:
        return "phone_click"
    if "phone" in n and ("website" in n or "from website" in n or "web" in n):
        return "verified_phone_call_website"
    if "call" in n and ("ad" in n or "ads" in n):
        return "call_from_ad"
    if "discovery" in n and "sched" in n:
        return "zoho_discovery_scheduled"
    if "job order" in n:
        return "zoho_job_order"
    if "placement" in n:
        return "zoho_placement"
    if any(x in n for x in ("page_view", "scroll", "session", "engagement", "time on")):
        return "engagement"
    if "zoho" in n:
        return "zoho_other"
    return "other"


def rollup_conv_by_action(rows: list[dict[str, Any]], start: date, end: date) -> dict[str, Any]:
    by_camp: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    by_class: dict[str, float] = defaultdict(float)
    for r in rows:
        d = date.fromisoformat(r["date"])
        if not (start <= d <= end):
            continue
        camp = r["campaign"]
        cls = classify_action(r["action"])
        by_camp[camp][r["action"]] += r["conversions"]
        by_camp[camp][f"__class_{cls}"] += r["conversions"]
        by_class[cls] += r["conversions"]
    return {"by_campaign": dict(by_camp), "by_class": dict(by_class)}


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    api_log: list[dict[str, Any]] = []

    try:
        settings = load_settings(env_file=SG_ROOT / ".env")
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        print(f"Client fail: {exc}", file=sys.stderr)
        return 1

    date_range = f"{PULL_START.isoformat()}..{END.isoformat()}"

    def do_call(cid: str, label: str, q: str) -> list[Any]:
        res = run_q(client, cid, label, q)
        api_log.append({"name": label, "customer": cid, **{k: res[k] for k in ("ok", "error", "row_count") if k in res}})
        return res.get("raw") or []

    # US pulls
    us_daily_raw = do_call(US_ID, "us_campaign_daily", CAMPAIGN_DAILY_Q.format(start=PULL_START, end=END))
    us_conv_raw = do_call(US_ID, "us_conv_by_action", CONV_BY_ACTION_Q.format(start=PULL_START, end=END))
    us_settings_raw = do_call(US_ID, "us_conv_settings", CONV_ACTION_SETTINGS_Q)
    us_device_raw = do_call(US_ID, "us_device", DEVICE_Q.format(start=PULL_START, end=END))
    us_lp_raw = do_call(US_ID, "us_landing", LANDING_Q.format(start=PULL_START, end=END))

    # AU pulls (use AU campaign names in query — same names work per account)
    au_daily_raw = do_call(AU_ID, "au_campaign_daily", CAMPAIGN_DAILY_Q.format(start=PULL_START, end=END))
    au_conv_raw = do_call(AU_ID, "au_conv_by_action", CONV_BY_ACTION_Q.format(start=PULL_START, end=END))
    au_settings_raw = do_call(AU_ID, "au_conv_settings", CONV_ACTION_SETTINGS_Q)
    au_device_raw = do_call(AU_ID, "au_device", DEVICE_Q.format(start=PULL_START, end=END))
    au_lp_raw = do_call(AU_ID, "au_landing", LANDING_Q.format(start=PULL_START, end=END))

    us_daily = parse_campaign_daily(us_daily_raw)
    au_daily = parse_campaign_daily(au_daily_raw)
    us_conv = parse_conv_actions(us_conv_raw)
    au_conv = parse_conv_actions(au_conv_raw)

    windows = {
        "last_7": (END - timedelta(days=6), END),
        "last_14": (END - timedelta(days=13), END),
        "last_30": (END - timedelta(days=29), END),
        "since_launch_us": (US_LAUNCH, END),
        "since_launch_au": (AU_LAUNCH, END),
    }

    def build_market(daily: list[dict[str, Any]], conv: list[dict[str, Any]], launch: date, market: str) -> dict[str, Any]:
        agg: dict[str, Any] = {}
        for key, (ws, we) in windows.items():
            if market == "US" and key == "since_launch_au":
                continue
            if market == "AU" and key == "since_launch_us":
                continue
            launch_date = launch if "since_launch" in key else None
            agg[key] = aggregate_window(daily, ws, we, launch_date)
        conv_rollup = {}
        for key, (ws, we) in windows.items():
            if market == "US" and key == "since_launch_au":
                continue
            if market == "AU" and key == "since_launch_us":
                continue
            conv_rollup[key] = rollup_conv_by_action(conv, ws, we)
        return {"daily_row_count": len(daily), "windows": agg, "conversions": conv_rollup}

    # AU budget increase ~Aug 20 — split pre/post
    au_core_pre = aggregate_window(
        au_daily, date(2026, 8, 9), date(2026, 8, 19), AU_LAUNCH
    ).get("VC_AU_S_CORE")
    au_core_post = aggregate_window(
        au_daily, date(2026, 8, 20), END, AU_LAUNCH
    ).get("VC_AU_S_CORE")

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pull_started_utc": started,
        "complete_through": END.isoformat(),
        "excluded": "2026-08-26 (today incomplete)",
        "customer_ids": {"us": US_ID, "au": AU_ID},
        "target_campaigns": sorted(TARGET_CAMPAIGNS),
        "api_calls_used": CALLS,
        "api_calls_max": MAX_CALLS,
        "api_calls": api_log,
        "hard_stop": STOPPED,
        "read_only": True,
        "US": {
            **build_market(us_daily, us_conv, US_LAUNCH, "US"),
            "conv_action_settings": parse_conv_settings(us_settings_raw),
            "conversion_actions_detail": us_conv,
        },
        "AU": {
            **build_market(au_daily, au_conv, AU_LAUNCH, "AU"),
            "conv_action_settings": parse_conv_settings(au_settings_raw),
            "conversion_actions_detail": au_conv,
            "au_core_budget_change": {
                "pre_increase": {"start": "2026-08-09", "end": "2026-08-19", "metrics": au_core_pre},
                "post_increase": {"start": "2026-08-20", "end": END.isoformat(), "metrics": au_core_post},
                "note": "AU Core budget raised A$75→A$100 around Aug 20 — compare pre/post separately.",
            },
        },
        "current_budgets_verified": {
            c: next((r["daily_budget"] for r in reversed(us_daily + au_daily) if r["campaign"] == c), None)
            for c in TARGET_CAMPAIGNS
        },
        "current_bid_strategies": {
            c: next((r["bidding_strategy_type"] for r in reversed(us_daily + au_daily) if r["campaign"] == c), None)
            for c in TARGET_CAMPAIGNS
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"API calls: {CALLS}/{MAX_CALLS} stop={STOPPED}")
    for c in TARGET_CAMPAIGNS:
        print(f"  {c}: budget={payload['current_budgets_verified'].get(c)} bid={payload['current_bid_strategies'].get(c)}")
    return 0 if not STOPPED else 1


if __name__ == "__main__":
    raise SystemExit(main())
