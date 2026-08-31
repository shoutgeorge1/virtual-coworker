#!/usr/bin/env python3
"""Read-only Search impression share for VC_* CORE/ROLES.

Pulls campaign-level Search IS for last 7 *complete* days (segments.date),
then aggregates last 2 / 3 / 7 complete-day windows in Python.

Competitor Auction Insights are NOT publicly available via Google Ads API
for this account — we never invent competitor findings.

Hard rules:
- No mutate / upload / enable
- On RESOURCE_EXHAUSTED or expired token: STOP, do not retry
- Max 2 GAQL calls (US + AU) unless George raises the cap

Usage:
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    /Users/george/Developer/virtual-coworker/ads-launch/pull_impression_share.py
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

US_ID = "4967151855"
AU_ID = "5735391940"
REPO = Path(__file__).resolve().parents[1]
OUT_IS = REPO / "xray" / "data" / "impression-share.json"
OUT_EXEC = REPO / "xray" / "data" / "executive-snapshot.json"
VC_ENV = SG_ROOT / "clients" / "virtual-coworker.env"

CAMPAIGN_IS_DAILY_Q = """
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
      metrics.search_impression_share,
      metrics.search_rank_lost_impression_share,
      metrics.search_budget_lost_impression_share,
      metrics.search_top_impression_share,
      metrics.search_absolute_top_impression_share
    FROM campaign
    WHERE campaign.name LIKE '{prefix}%'
      AND campaign.status != 'REMOVED'
      AND segments.date BETWEEN '{start}' AND '{end}'
"""


def _money(micros: Any) -> float:
    try:
        return float(micros) / 1_000_000.0
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


def _enum_name(val: Any) -> str | None:
    if val is None:
        return None
    if hasattr(val, "name"):
        return str(val.name)
    text = str(val).strip()
    return text or None


def fetch_rows(client: Any, customer_id: str, query: str) -> list[Any]:
    return list(run_gaql(client, customer_id, query))


def _row_metrics(row: Any) -> dict[str, Any]:
    impr = int(row.metrics.impressions or 0)
    clicks = int(row.metrics.clicks or 0)
    cost = _money(row.metrics.cost_micros)
    ts = getattr(row.campaign, "target_spend", None)
    mc = getattr(row.campaign, "maximize_conversions", None)
    return {
        "name": row.campaign.name,
        "status": _enum_name(row.campaign.status),
        "bidding_strategy_type": _enum_name(
            getattr(row.campaign, "bidding_strategy_type", None)
        ),
        "cpc_bid_ceiling_usd": round(
            _money(getattr(ts, "cpc_bid_ceiling_micros", None)), 2
        )
        if ts is not None
        else None,
        "max_conv_target_cpa_usd": round(
            _money(getattr(mc, "target_cpa_micros", None)), 2
        )
        if mc is not None
        else None,
        "daily_budget_usd": round(
            _money(getattr(row.campaign_budget, "amount_micros", None)), 2
        ),
        "date": str(row.segments.date),
        "impressions": impr,
        "clicks": clicks,
        "cost_usd": round(cost, 2),
        "conversions": float(getattr(row.metrics, "conversions", 0) or 0),
        "all_conversions": float(getattr(row.metrics, "all_conversions", 0) or 0),
        "search_is_pct": _share_pct(
            getattr(row.metrics, "search_impression_share", None)
        ),
        "lost_is_rank_pct": _share_pct(
            getattr(row.metrics, "search_rank_lost_impression_share", None)
        ),
        "lost_is_budget_pct": _share_pct(
            getattr(row.metrics, "search_budget_lost_impression_share", None)
        ),
        "search_top_is_pct": _share_pct(
            getattr(row.metrics, "search_top_impression_share", None)
        ),
        "search_abs_top_is_pct": _share_pct(
            getattr(row.metrics, "search_absolute_top_impression_share", None)
        ),
    }


def _avg_share(vals: list[float | None], weights: list[int]) -> float | None:
    """Impression-weighted average of share metrics; skip None days."""
    num = 0.0
    den = 0
    for v, w in zip(vals, weights):
        if v is None or w <= 0:
            continue
        num += float(v) * w
        den += w
    if den <= 0:
        return None
    return round(num / den, 1)


def aggregate_campaigns(
    daily_rows: list[dict[str, Any]], start: date, end: date
) -> list[dict[str, Any]]:
    by_name: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in daily_rows:
        d = date.fromisoformat(r["date"])
        if start <= d <= end:
            by_name[r["name"]].append(r)

    camps: list[dict[str, Any]] = []
    for name, rows in by_name.items():
        if "Brand" in name and not name.startswith(("VC_US_S_", "VC_AU_S_")):
            continue
        if not name.startswith(("VC_US_S_", "VC_AU_S_")):
            continue
        impr = sum(int(x["impressions"]) for x in rows)
        clicks = sum(int(x["clicks"]) for x in rows)
        cost = sum(float(x["cost_usd"]) for x in rows)
        conv = sum(float(x.get("conversions") or 0) for x in rows)
        all_conv = sum(float(x.get("all_conversions") or 0) for x in rows)
        weights = [int(x["impressions"]) for x in rows]
        camps.append(
            {
                "name": name,
                "status": rows[0].get("status"),
                "bidding_strategy_type": rows[0].get("bidding_strategy_type"),
                "cpc_bid_ceiling_usd": rows[0].get("cpc_bid_ceiling_usd"),
                "max_conv_target_cpa_usd": rows[0].get("max_conv_target_cpa_usd"),
                "daily_budget_usd": rows[0].get("daily_budget_usd"),
                "impressions": impr,
                "clicks": clicks,
                "cost_usd": round(cost, 2),
                "avg_cpc_usd": round(cost / clicks, 2) if clicks else None,
                "conversions": round(conv, 2),
                "all_conversions": round(all_conv, 2),
                "search_is_pct": _avg_share(
                    [x.get("search_is_pct") for x in rows], weights
                ),
                "lost_is_rank_pct": _avg_share(
                    [x.get("lost_is_rank_pct") for x in rows], weights
                ),
                "lost_is_budget_pct": _avg_share(
                    [x.get("lost_is_budget_pct") for x in rows], weights
                ),
                "search_top_is_pct": _avg_share(
                    [x.get("search_top_is_pct") for x in rows], weights
                ),
                "search_abs_top_is_pct": _avg_share(
                    [x.get("search_abs_top_is_pct") for x in rows], weights
                ),
            }
        )
    camps.sort(key=lambda c: -float(c.get("cost_usd") or 0))
    return camps


def bottleneck(camps: list[dict[str, Any]]) -> dict[str, Any]:
    if not camps:
        return {"verdict": "no_data", "plain": "No Stage 1 campaign rows in this pull."}
    core = next((c for c in camps if c["name"].endswith("_S_CORE")), None)
    roles = next((c for c in camps if c["name"].endswith("_S_ROLES")), None)
    core_budget = float((core or {}).get("lost_is_budget_pct") or 0)
    core_rank = float((core or {}).get("lost_is_rank_pct") or 0)
    roles_budget = float((roles or {}).get("lost_is_budget_pct") or 0)
    roles_rank = float((roles or {}).get("lost_is_rank_pct") or 0)
    if (
        core
        and roles
        and core_budget >= 20
        and roles_rank >= 20
        and core_budget > core_rank
        and roles_rank > roles_budget
    ):
        verdict = "mixed"
        plain = (
            f"Split by campaign: Core lost {core_budget:.0f}% of eligible impressions "
            f"to daily budget vs {core_rank:.0f}% to rank — a Core budget bump buys more "
            f"of the auctions Core already wins. Roles lost {roles_rank:.0f}% to rank vs "
            f"{roles_budget:.0f}% to budget — raising Roles budget will not rank money keywords."
        )
    else:
        max_rank = max(float(c.get("lost_is_rank_pct") or 0) for c in camps)
        max_budget = max(float(c.get("lost_is_budget_pct") or 0) for c in camps)
        if max_rank >= 20 and max_rank >= max_budget:
            verdict = "rank"
            plain = (
                "Lost IS (Rank) is the bigger hole — ads are eligible but often lose "
                "the auction (CPC cap / Quality / relevance), not because the daily "
                "budget ran out."
            )
        elif max_budget >= 20 and max_budget > max_rank:
            verdict = "budget"
            plain = (
                "Lost IS (Budget) is the bigger hole — campaigns are hitting the daily "
                "cap and stopping. Raising budget would buy more of the same auctions."
            )
        else:
            verdict = "mixed"
            plain = (
                "Mixed: some lost rank, some lost budget. Do not raise budget until "
                "Lost IS (Budget) is clearly the larger number."
            )
    return {
        "verdict": verdict,
        "plain": plain,
        "max_lost_is_rank_pct": max(
            float(c.get("lost_is_rank_pct") or 0) for c in camps
        ),
        "max_lost_is_budget_pct": max(
            float(c.get("lost_is_budget_pct") or 0) for c in camps
        ),
        "max_search_is_pct": max(float(c.get("search_is_pct") or 0) for c in camps),
        "core": "budget" if core and core_budget > core_rank else "rank",
        "roles": "rank" if roles and roles_rank > roles_budget else "budget",
    }


def build_market_block(
    market: str, daily: list[dict[str, Any]], end: date
) -> dict[str, Any]:
    windows: dict[str, Any] = {}
    for days, key in (
        (2, "last_2_complete_days"),
        (3, "last_3_complete_days"),
        (7, "last_7_complete_days"),
    ):
        start = end - timedelta(days=days - 1)
        camps = aggregate_campaigns(daily, start, end)
        windows[key] = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "campaigns": camps,
        }
    seven = windows["last_7_complete_days"]["campaigns"]
    return {
        "market": market,
        "window": "LAST_7_COMPLETE_DAYS",
        "complete_day_end": end.isoformat(),
        "campaigns": seven,
        "row_count": len(daily),
        "windows": windows,
        "currency_note": (
            "AU amounts are account currency (AUD). Field name cost_usd is historical."
            if market == "AU"
            else "US amounts are USD."
        ),
    }


def _plain_insights(
    us: dict[str, Any] | None,
    au: dict[str, Any] | None,
    bn_us: dict[str, Any] | None,
) -> list[str]:
    lines: list[str] = []
    for block, label in ((us, "US"), (au, "AU")):
        if not block:
            continue
        cur = "A$" if label == "AU" else "$"
        for c in block.get("campaigns") or []:
            nice = (
                (c.get("name") or "")
                .replace("VC_US_S_CORE", "US Core")
                .replace("VC_US_S_ROLES", "US Roles")
                .replace("VC_AU_S_CORE", "AU Core")
                .replace("VC_AU_S_ROLES", "AU Roles")
            )
            lines.append(
                f"{nice}: Search IS {c.get('search_is_pct') if c.get('search_is_pct') is not None else '—'}% · "
                f"lost rank {c.get('lost_is_rank_pct') if c.get('lost_is_rank_pct') is not None else '—'}% · "
                f"lost budget {c.get('lost_is_budget_pct') if c.get('lost_is_budget_pct') is not None else '—'}% "
                f"({int(c.get('impressions') or 0)} impr / {cur}{float(c.get('cost_usd') or 0):.0f} · last 7 complete days)."
            )
    if bn_us and bn_us.get("plain"):
        lines.append(bn_us["plain"])
    return lines


def merge_into_executive(payload: dict[str, Any]) -> None:
    if not OUT_EXEC.is_file():
        return
    exec_data = json.loads(OUT_EXEC.read_text(encoding="utf-8"))
    exec_data["impression_share"] = payload
    exec_data["impression_share_merged_at_utc"] = payload.get("generated_at_utc")
    op = exec_data.get("operator") or {}
    extra = payload.get("insights_plain") or []
    existing = [
        x
        for x in list(op.get("insights") or [])
        if "~$125" not in x and "Core $75" not in x and "auction overlap" not in x.lower()
    ]
    merged = extra + [x for x in existing if x not in extra]
    op["insights"] = merged[:12]
    op["impression_share_verdict"] = (payload.get("bottleneck_us") or {}).get("verdict")
    op["auction_competitor_status"] = payload.get("auction_us")
    exec_data["operator"] = op
    OUT_EXEC.write_text(json.dumps(exec_data, indent=2) + "\n", encoding="utf-8")


def run_call(
    client: Any,
    *,
    n: int,
    name: str,
    customer_id: str,
    query: str,
    api_calls: list[dict[str, Any]],
) -> list[Any] | None:
    try:
        print(f"API call {n}: {name} …", flush=True)
        rows = fetch_rows(client, customer_id, query)
        api_calls.append({"n": n, "name": name, "ok": True, "row_count": len(rows)})
        return rows
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call {n}: {exc}", file=sys.stderr)
        api_calls.append({"n": n, "name": name, "ok": False, "error": str(exc)})
        return None
    except ApiAccessError as exc:
        print(f"STOP API on call {n}: {exc}", file=sys.stderr)
        api_calls.append({"n": n, "name": name, "ok": False, "error": str(exc)})
        return None


def main() -> int:
    load_dotenv(SG_ROOT / ".env", override=False)
    if VC_ENV.is_file():
        load_dotenv(VC_ENV, override=True)

    started = datetime.now(timezone.utc).isoformat()
    api_calls: list[dict[str, Any]] = []
    hard_stop: str | None = None

    # Locked complete Mon–Sun scoreboard week. Monday does not roll to a new week.
    end = date(2026, 8, 16)
    start = date(2026, 8, 10)

    try:
        settings = load_settings(env_file=SG_ROOT / ".env")
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        print(f"ERROR building client: {exc}", file=sys.stderr)
        payload = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "pull_started_utc": started,
            "hard_stop": str(exc),
            "api_calls_used": 0,
            "token_status": "dead"
            if "invalid_grant" in str(exc).lower() or "expired" in str(exc).lower()
            else "client_fail",
            "auction_us": {
                "available": False,
                "reason": "Client failed before any GAQL; competitor Auction Insights not attempted.",
            },
        }
        OUT_IS.parent.mkdir(parents=True, exist_ok=True)
        OUT_IS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        merge_into_executive(payload)
        print(f"Wrote {OUT_IS} (client fail — 0 calls)")
        return 1

    us_block = au_block = None
    bn_us = None
    us_daily: list[dict[str, Any]] = []
    au_daily: list[dict[str, Any]] = []

    us_rows = run_call(
        client,
        n=1,
        name="us_campaign_is_last_7_complete_days",
        customer_id=US_ID,
        query=CAMPAIGN_IS_DAILY_Q.format(
            prefix="VC_US_", start=start.isoformat(), end=end.isoformat()
        ),
        api_calls=api_calls,
    )
    if us_rows is None:
        hard_stop = (api_calls[-1] or {}).get("error")
    else:
        us_daily = [_row_metrics(r) for r in us_rows]
        us_block = build_market_block("US", us_daily, end)
        bn_us = bottleneck(us_block.get("campaigns") or [])

    if hard_stop is None:
        au_rows = run_call(
            client,
            n=2,
            name="au_campaign_is_last_7_complete_days",
            customer_id=AU_ID,
            query=CAMPAIGN_IS_DAILY_Q.format(
                prefix="VC_AU_", start=start.isoformat(), end=end.isoformat()
            ),
            api_calls=api_calls,
        )
        if au_rows is None:
            hard_stop = (api_calls[-1] or {}).get("error")
        else:
            au_daily = [_row_metrics(r) for r in au_rows]
            au_block = build_market_block("AU", au_daily, end)

    # Competitor Auction Insights: not available via public API for this account.
    auction = {
        "available": False,
        "attempted": False,
        "reason": (
            "Competitor-domain Auction Insights metrics are allowlist-only in the "
            "Google Ads API and are not available for this account. Dashboard shows "
            "campaign Search IS / lost rank / lost budget / top / abs-top only. "
            "Do not invent competitor findings."
        ),
    }

    finished = datetime.now(timezone.utc).isoformat()
    insights = _plain_insights(us_block, au_block, bn_us)

    # Flat windows for Executive bake
    windows = {
        "US": (us_block or {}).get("windows") or {},
        "AU": (au_block or {}).get("windows") or {},
    }

    # Budgets from latest pull
    us_core_b = next(
        (
            c.get("daily_budget_usd")
            for c in (us_block or {}).get("campaigns") or []
            if c.get("name") == "VC_US_S_CORE"
        ),
        150,
    )
    us_roles_b = next(
        (
            c.get("daily_budget_usd")
            for c in (us_block or {}).get("campaigns") or []
            if c.get("name") == "VC_US_S_ROLES"
        ),
        100,
    )
    au_core_b = next(
        (
            c.get("daily_budget_usd")
            for c in (au_block or {}).get("campaigns") or []
            if c.get("name") == "VC_AU_S_CORE"
        ),
        75,
    )
    au_roles_b = next(
        (
            c.get("daily_budget_usd")
            for c in (au_block or {}).get("campaigns") or []
            if c.get("name") == "VC_AU_S_ROLES"
        ),
        50,
    )

    payload = {
        "generated_at_utc": finished,
        "pull_started_utc": started,
        "customer_ids": {"us": US_ID, "au": AU_ID},
        "filter": (
            f"VC_US_% + VC_AU_% segments.date BETWEEN {start} AND {end} "
            "(complete days; Brand deferred)"
        ),
        "api_calls_used": len(api_calls),
        "api_calls_max": 2,
        "api_calls": api_calls,
        "hard_stop": hard_stop,
        "read_only": True,
        "performance_us": us_block,
        "performance_au": au_block,
        "bottleneck_us": bn_us,
        "bottleneck_au": bottleneck((au_block or {}).get("campaigns") or [])
        if au_block
        else None,
        "windows": windows,
        "auction_us": auction,
        "insights_plain": insights,
        "cpc_caps_note": (
            "Operator-set CPC caps (not from this pull): US CORE $15 / ROLES $12 · "
            "AU CORE A$10 / ROLES A$8. "
            f"Daily budgets from API: US Core ${us_core_b} / Roles ${us_roles_b} · "
            f"AU Core A${au_core_b} / Roles A${au_roles_b}."
        ),
    }
    OUT_IS.parent.mkdir(parents=True, exist_ok=True)
    OUT_IS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    merge_into_executive(payload)
    print(f"Wrote {OUT_IS}")
    if bn_us:
        print(f"US bottleneck: {bn_us.get('verdict')} — {bn_us.get('plain')}")
    for line in insights:
        print(f"  • {line}")
    print(f"API calls used: {len(api_calls)} (max 2)")
    print("Auction competitor: not available via API — omitted (not a finding).")
    return 1 if hard_stop else 0


if __name__ == "__main__":
    raise SystemExit(main())
