#!/usr/bin/env python3
"""Read-only forensic Ads pulls for the recovery audit (13 Aug 2026).

George authorized extra reads for this audit. Still:
- No mutate / upload / enable
- On RESOURCE_EXHAUSTED or token errors: STOP, do not retry
- No keyword/ad dump, no auction-insights
- 8 GAQL calls max (4 per account)

Writes xray/data/recovery-ads-raw.json

Usage:
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    /Users/george/Developer/virtual-coworker/ads-launch/pull_forensic_recovery.py
"""

from __future__ import annotations

import json
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
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "xray" / "data" / "recovery-ads-raw.json"
VC_ENV = SG_ROOT / "clients" / "virtual-coworker.env"

WINDOW_START = "2024-08-01"
WINDOW_END = "2026-08-12"
MAX_CALLS = 8

CONV_ACTIONS_Q = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.status,
      conversion_action.type,
      conversion_action.category,
      conversion_action.origin,
      conversion_action.primary_for_goal,
      conversion_action.counting_type,
      conversion_action.include_in_conversions_metric,
      conversion_action.click_through_lookback_window_days,
      conversion_action.view_through_lookback_window_days,
      conversion_action.phone_call_duration_seconds,
      conversion_action.value_settings.default_value,
      conversion_action.value_settings.always_use_default_value
    FROM conversion_action
    WHERE conversion_action.status != 'REMOVED'
"""

CONV_ACTIONS_Q_FALLBACK = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.status,
      conversion_action.type,
      conversion_action.category,
      conversion_action.primary_for_goal,
      conversion_action.counting_type,
      conversion_action.include_in_conversions_metric
    FROM conversion_action
    WHERE conversion_action.status != 'REMOVED'
"""

CAMPAIGNS_Q = f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      campaign.bidding_strategy_type,
      campaign_budget.amount_micros,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.all_conversions,
      metrics.conversions_value,
      metrics.all_conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
      AND campaign.status != 'REMOVED'
"""

CONV_METRICS_Q = f"""
    SELECT
      segments.conversion_action_name,
      segments.conversion_action_category,
      metrics.conversions,
      metrics.all_conversions,
      metrics.conversions_value,
      metrics.all_conversions_value
    FROM customer
    WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
"""

LANDING_Q = f"""
    SELECT
      landing_page_view.unexpanded_final_url,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions,
      metrics.all_conversions
    FROM landing_page_view
    WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
"""


def _money(micros: Any) -> float:
    try:
        return round(float(micros) / 1_000_000.0, 2)
    except (TypeError, ValueError):
        return 0.0


def _enum(val: Any) -> str | None:
    if val is None:
        return None
    if hasattr(val, "name"):
        return str(val.name)
    text = str(val).strip()
    return text or None


def _num(val: Any) -> float:
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def parse_conversion_actions(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        ca = row.conversion_action
        vs = getattr(ca, "value_settings", None)
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
                "include_in_conversions_metric": bool(
                    getattr(ca, "include_in_conversions_metric", False)
                ),
                "click_window_days": int(
                    getattr(ca, "click_through_lookback_window_days", 0) or 0
                ),
                "view_window_days": int(
                    getattr(ca, "view_through_lookback_window_days", 0) or 0
                ),
                "phone_call_duration_seconds": int(
                    getattr(ca, "phone_call_duration_seconds", 0) or 0
                ),
                "default_value": _num(getattr(vs, "default_value", 0) if vs else 0),
                "always_use_default_value": bool(
                    getattr(vs, "always_use_default_value", False) if vs else False
                ),
            }
        )
    out.sort(key=lambda r: r["name"].lower())
    return out


def parse_campaigns(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        c = row.campaign
        m = row.metrics
        clicks = int(m.clicks or 0)
        cost = _money(m.cost_micros)
        conv = _num(m.conversions)
        all_conv = _num(m.all_conversions)
        out.append(
            {
                "id": str(c.id),
                "name": c.name,
                "status": _enum(c.status),
                "channel": _enum(c.advertising_channel_type),
                "bidding": _enum(c.bidding_strategy_type),
                "daily_budget": _money(getattr(row.campaign_budget, "amount_micros", 0)),
                "impressions": int(m.impressions or 0),
                "clicks": clicks,
                "cost": cost,
                "avg_cpc": round(cost / clicks, 2) if clicks else None,
                "conversions": round(conv, 2),
                "all_conversions": round(all_conv, 2),
                "conversions_value": round(_num(m.conversions_value), 2),
                "all_conversions_value": round(_num(m.all_conversions_value), 2),
                "ctr_pct": round(100.0 * clicks / int(m.impressions or 0), 2)
                if int(m.impressions or 0)
                else None,
                "cpa": round(cost / conv, 2) if conv > 0 else None,
                "all_cpa": round(cost / all_conv, 2) if all_conv > 0 else None,
            }
        )
    out.sort(key=lambda r: -float(r["cost"] or 0))
    return out


def parse_conv_metrics(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        conv = _num(row.metrics.conversions)
        all_conv = _num(row.metrics.all_conversions)
        if conv == 0 and all_conv == 0:
            continue
        out.append(
            {
                "name": row.segments.conversion_action_name,
                "category": _enum(row.segments.conversion_action_category),
                "conversions": round(conv, 2),
                "all_conversions": round(all_conv, 2),
                "conversions_value": round(_num(row.metrics.conversions_value), 2),
                "all_conversions_value": round(
                    _num(row.metrics.all_conversions_value), 2
                ),
            }
        )
    out.sort(key=lambda r: -float(r["all_conversions"] or 0))
    return out


def parse_landings(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        url = row.landing_page_view.unexpanded_final_url
        clicks = int(row.metrics.clicks or 0)
        cost = _money(row.metrics.cost_micros)
        conv = _num(row.metrics.conversions)
        all_conv = _num(row.metrics.all_conversions)
        if clicks == 0 and cost == 0 and conv == 0:
            continue
        out.append(
            {
                "url": url,
                "impressions": int(row.metrics.impressions or 0),
                "clicks": clicks,
                "cost": cost,
                "conversions": round(conv, 2),
                "all_conversions": round(all_conv, 2),
                "cpa": round(cost / conv, 2) if conv > 0 else None,
            }
        )
    out.sort(key=lambda r: -float(r["cost"] or 0))
    return out


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
        print(f"API call {n}/{MAX_CALLS}: {name} …", flush=True)
        rows = list(run_gaql(client, customer_id, query))
        api_calls.append({"n": n, "name": name, "ok": True, "row_count": len(rows)})
        return rows
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call {n}: {exc}", file=sys.stderr)
        api_calls.append(
            {"n": n, "name": name, "ok": False, "error": str(exc), "stop": True}
        )
        return None
    except ApiAccessError as exc:
        print(f"API error on call {n}: {exc}", file=sys.stderr)
        stop = "RESOURCE_EXHAUSTED" in str(exc).upper() or "invalid_grant" in str(exc).lower()
        api_calls.append(
            {"n": n, "name": name, "ok": False, "error": str(exc), "stop": stop}
        )
        return None


def pull_account(
    client: Any,
    *,
    market: str,
    customer_id: str,
    start_n: int,
    api_calls: list[dict[str, Any]],
    skip_conversion_actions: bool = False,
    existing: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int, str | None]:
    n = start_n
    block: dict[str, Any] = dict(existing or {})
    block["market"] = market
    block["customer_id"] = customer_id

    if skip_conversion_actions and block.get("conversion_actions"):
        print(f"Skip {market} conversion_actions (already pulled)", flush=True)
    else:
        rows = run_call(
        client,
        n=n,
        name=f"{market.lower()}_conversion_actions",
        customer_id=customer_id,
        query=CONV_ACTIONS_Q,
        api_calls=api_calls,
    )
    if rows is None:
        err = (api_calls[-1] or {}).get("error") or ""
        if api_calls[-1].get("stop"):
            return block, n, err
        n += 1
        if n > MAX_CALLS:
            return block, n, "max calls"
        print(f"Retrying conversion_actions with fallback fields for {market}", flush=True)
        rows = run_call(
            client,
            n=n,
            name=f"{market.lower()}_conversion_actions_fallback",
            customer_id=customer_id,
            query=CONV_ACTIONS_Q_FALLBACK,
            api_calls=api_calls,
        )
        if rows is None:
            return block, n, (api_calls[-1] or {}).get("error")
    block["conversion_actions"] = parse_conversion_actions(rows)
    n += 1

    if n > MAX_CALLS:
        return block, n - 1, "max calls"
    rows = run_call(
        client,
        n=n,
        name=f"{market.lower()}_campaigns_{WINDOW_START}_{WINDOW_END}",
        customer_id=customer_id,
        query=CAMPAIGNS_Q,
        api_calls=api_calls,
    )
    if rows is None:
        return block, n, (api_calls[-1] or {}).get("error")
    block["campaigns"] = parse_campaigns(rows)
    n += 1

    if n > MAX_CALLS:
        return block, n - 1, "max calls"
    rows = run_call(
        client,
        n=n,
        name=f"{market.lower()}_conversion_metrics_{WINDOW_START}_{WINDOW_END}",
        customer_id=customer_id,
        query=CONV_METRICS_Q,
        api_calls=api_calls,
    )
    if rows is None:
        err = (api_calls[-1] or {}).get("error") or ""
        if api_calls[-1].get("stop"):
            return block, n, err
        block["conversion_metrics_error"] = err
    else:
        block["conversion_metrics"] = parse_conv_metrics(rows)
    n += 1

    if n > MAX_CALLS:
        return block, n - 1, "max calls"
    rows = run_call(
        client,
        n=n,
        name=f"{market.lower()}_landing_pages_{WINDOW_START}_{WINDOW_END}",
        customer_id=customer_id,
        query=LANDING_Q,
        api_calls=api_calls,
    )
    if rows is None:
        err = (api_calls[-1] or {}).get("error") or ""
        if api_calls[-1].get("stop"):
            return block, n, err
        block["landing_pages_error"] = err
    else:
        block["landing_pages"] = parse_landings(rows)
    return block, n, None


def main() -> int:
    load_dotenv(SG_ROOT / ".env", override=False)
    if VC_ENV.is_file():
        load_dotenv(VC_ENV, override=True)

    started = datetime.now(timezone.utc).isoformat()
    api_calls: list[dict[str, Any]] = []
    hard_stop: str | None = None

    try:
        settings = load_settings(env_file=SG_ROOT / ".env")
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        payload = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "pull_started_utc": started,
            "read_only": True,
            "hard_stop": str(exc),
            "api_calls_used": 0,
            "window": f"{WINDOW_START} to {WINDOW_END}",
            "note": "Client failed. Dashboard uses on-disk Editor history + prior snapshots.",
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {OUT} (client fail — 0 calls)")
        return 1

    us_block, n, hard_stop = pull_account(
        client, market="US", customer_id=US_ID, start_n=1, api_calls=api_calls
    )
    au_block: dict[str, Any] | None = None
    if hard_stop is None:
        au_block, n, hard_stop = pull_account(
            client,
            market="AU",
            customer_id=AU_ID,
            start_n=n + 1,
            api_calls=api_calls,
        )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pull_started_utc": started,
        "read_only": True,
        "window": f"{WINDOW_START} to {WINDOW_END}",
        "customer_ids": {"us": US_ID, "au": AU_ID},
        "api_calls_used": len(api_calls),
        "api_calls_max": MAX_CALLS,
        "api_calls": api_calls,
        "hard_stop": hard_stop,
        "us": us_block,
        "au": au_block,
        "honesty": (
            "metrics.conversions and metrics.all_conversions are Ads-reported. "
            "They are not job orders or confirmed employer leads."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(api_calls)} calls)")
    return 0 if hard_stop is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
