#!/usr/bin/env python3
"""Read-only Brand_VC probe — max 2 GAQL. No mutate.

Temporary Brand ad group inside VC_US_S_CORE only.
Does not dump inventory. Does not retry auction-insight fields.
On RESOURCE_EXHAUSTED: STOP.
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

if (SG_ROOT / ".env").is_file():
    load_dotenv(SG_ROOT / ".env")
_vc_env = SG_ROOT / "clients" / "virtual-coworker.env"
if _vc_env.is_file():
    load_dotenv(_vc_env, override=True)

US_ID = "4967151855"
AG_ID = "205906384984"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "ads-launch" / "_us_brand_ag_readonly.json"

AG_Q = f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      ad_group.id,
      ad_group.name,
      ad_group.status,
      metrics.impressions,
      metrics.clicks,
      metrics.ctr,
      metrics.average_cpc,
      metrics.cost_micros,
      metrics.conversions
    FROM ad_group
    WHERE ad_group.id = {AG_ID}
      AND segments.date DURING LAST_7_DAYS
"""

ST_Q = f"""
    SELECT
      campaign.name,
      ad_group.name,
      search_term_view.search_term,
      search_term_view.status,
      metrics.impressions,
      metrics.clicks,
      metrics.cost_micros,
      metrics.conversions
    FROM search_term_view
    WHERE ad_group.id = {AG_ID}
      AND segments.date DURING LAST_7_DAYS
"""


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


def _enum_name(val: Any) -> str:
    if val is None:
        return ""
    name = getattr(val, "name", None)
    if name:
        return str(name)
    return str(val)


def main() -> int:
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "scope": "Brand_VC inside VC_US_S_CORE only",
        "ad_group_id": AG_ID,
        "window": "LAST_7_DAYS",
        "api_calls_used": 0,
        "api_calls_max": 2,
        "api_calls": [],
        "hard_stop": None,
        "ad_group": None,
        "search_terms": [],
        "ag_is_note": None,
    }
    try:
        settings = load_settings()
        client = build_client(settings)
    except Exception as exc:
        payload["hard_stop"] = f"client_init: {exc}"
        OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    try:
        rows = list(run_gaql(client, US_ID, AG_Q))
        payload["api_calls_used"] += 1
        payload["api_calls"].append(
            {"n": 1, "name": "brand_vc_ag_last_7_days", "ok": True, "row_count": len(rows)}
        )
        if rows:
            row = rows[0]
            clicks = int(row.metrics.clicks or 0)
            cost = _money(row.metrics.cost_micros)
            payload["ad_group"] = {
                "campaign": row.campaign.name,
                "campaign_status": _enum_name(row.campaign.status),
                "ad_group": row.ad_group.name,
                "ad_group_status": _enum_name(row.ad_group.status),
                "impressions": int(row.metrics.impressions or 0),
                "clicks": clicks,
                "ctr_pct": round(float(row.metrics.ctr or 0) * 100, 2),
                "avg_cpc_usd": round(cost / clicks, 2) if clicks else None,
                "cost_usd": cost,
                "conversions": float(row.metrics.conversions or 0),
                "search_is_pct": None,
                "search_top_is_pct": None,
                "search_abs_top_is_pct": None,
                "lost_is_rank_pct": None,
                "lost_is_budget_pct": None,
            }
            payload["ag_is_note"] = (
                "AG-level Search IS / lost rank / lost budget are not available "
                "on ad_group (API rejects search_budget_lost_impression_share). "
                "Use campaign-mixed CORE IS only. Do not retry those fields."
            )
    except QuotaExhaustedError as exc:
        payload["hard_stop"] = f"RESOURCE_EXHAUSTED on call 1: {exc}"
        payload["api_calls"].append({"n": 1, "name": "brand_vc_ag_last_7_days", "ok": False, "error": str(exc)})
        OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2
    except (ApiAccessError, SgGoogleAdsError, Exception) as exc:
        payload["api_calls_used"] += 1
        payload["api_calls"].append(
            {"n": 1, "name": "brand_vc_ag_last_7_days", "ok": False, "error": str(exc)}
        )
        payload["ag_is_note"] = (
            "AG-level IS/metrics query failed. Use campaign-mixed CORE IS caveat. "
            "Not retrying IS fields. Search-term query still attempted if quota remains."
        )

    if payload["hard_stop"]:
        OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2

    try:
        rows = list(run_gaql(client, US_ID, ST_Q))
        payload["api_calls_used"] += 1
        payload["api_calls"].append(
            {"n": 2, "name": "brand_vc_search_terms_last_7_days", "ok": True, "row_count": len(rows)}
        )
        terms: dict[str, dict[str, Any]] = {}
        for row in rows:
            term = (row.search_term_view.search_term or "").strip()
            if not term:
                continue
            slot = terms.setdefault(
                term,
                {
                    "search_term": term,
                    "status": _enum_name(row.search_term_view.status),
                    "impressions": 0,
                    "clicks": 0,
                    "cost_usd": 0.0,
                    "conversions": 0.0,
                },
            )
            slot["impressions"] += int(row.metrics.impressions or 0)
            slot["clicks"] += int(row.metrics.clicks or 0)
            slot["cost_usd"] = round(slot["cost_usd"] + _money(row.metrics.cost_micros), 2)
            slot["conversions"] = round(slot["conversions"] + float(row.metrics.conversions or 0), 2)
        payload["search_terms"] = sorted(
            terms.values(), key=lambda t: (-t["cost_usd"], -t["clicks"], t["search_term"])
        )
    except QuotaExhaustedError as exc:
        payload["hard_stop"] = f"RESOURCE_EXHAUSTED on call 2: {exc}"
        payload["api_calls"].append(
            {"n": 2, "name": "brand_vc_search_terms_last_7_days", "ok": False, "error": str(exc)}
        )
        OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 2
    except (ApiAccessError, SgGoogleAdsError, Exception) as exc:
        payload["api_calls_used"] += 1
        payload["api_calls"].append(
            {"n": 2, "name": "brand_vc_search_terms_last_7_days", "ok": False, "error": str(exc)}
        )

    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
