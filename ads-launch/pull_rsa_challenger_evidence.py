#!/usr/bin/env python3
"""Read-only evidence pull for per-ad-group RSA challengers.

George authorized this research pass (2026-08-14): more than 1–2 GAQL
searches, VC_* CORE/ROLES only, Brand deferred.

Hard rules:
- No mutate / create / enable / pause
- On RESOURCE_EXHAUSTED: STOP, do not retry
- Mid-save after every successful call so a later failure is resumable

Windows:
- since_launch: 2026-08-04 → 2026-08-13 (complete days after Stage 1)
- last_2_complete: 2026-08-12 → 2026-08-13

Usage:
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    ads-launch/pull_rsa_challenger_evidence.py
  ... --resume
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SG_ROOT = Path(
    __import__("os").environ.get(
        "SHOUTGEORGE_ADS_ROOT", "/Users/george/Developer/shoutgeorge-ads"
    )
)
if (SG_ROOT / "src").is_dir():
    sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from sg_google_ads.client import build_client, run_gaql  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import (  # noqa: E402
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
US_CAMPS = ("VC_US_S_CORE", "VC_US_S_ROLES")
AU_CAMPS = ("VC_AU_S_CORE", "VC_AU_S_ROLES")
LAUNCH = "2026-08-04"
END = "2026-08-13"
LAST2_START = "2026-08-12"
MAX_CALLS = 12
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "ads-launch" / "_rsa_challenger_evidence.json"

CAMPS_SQL = {
    "US": ", ".join(f"'{c}'" for c in US_CAMPS),
    "AU": ", ".join(f"'{c}'" for c in AU_CAMPS),
}
CUSTOMERS = {"US": US_ID, "AU": AU_ID}


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _enum(val: Any) -> str:
    name = getattr(val, "name", None)
    if name:
        return str(name)
    return str(val or "")


def _pin(asset: Any) -> str:
    pin = getattr(asset, "pinned_field", None)
    name = getattr(pin, "name", None) if pin is not None else None
    return str(name or "UNSPECIFIED")


def _kw_text(crit: Any) -> str:
    kw = getattr(crit, "keyword", None)
    if kw is None:
        return ""
    return str(kw.text or "")


def _kw_match(crit: Any) -> str:
    kw = getattr(crit, "keyword", None)
    if kw is None:
        return ""
    return _enum(getattr(kw, "match_type", None))


def empty_payload() -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "windows": {
            "since_launch": {"start": LAUNCH, "end": END},
            "last_2_complete": {"start": LAST2_START, "end": END},
        },
        "scope": "VC_* CORE + ROLES only (Brand deferred)",
        "read_only": True,
        "api_calls": [],
        "api_calls_used": 0,
        "api_calls_max": MAX_CALLS,
        "hard_stop": None,
        "markets": {
            "US": {"customer_id": US_ID, "campaigns": list(US_CAMPS)},
            "AU": {"customer_id": AU_ID, "campaigns": list(AU_CAMPS)},
        },
        "inventory": {"US": [], "AU": []},
        "rsa_daily": {"US": [], "AU": []},
        "assets_daily": {"US": [], "AU": []},
        "keywords": {"US": [], "AU": []},
        "search_terms": {"US": [], "AU": []},
        "auction_insights": {"US": [], "AU": []},
        "partial": True,
    }


def save(payload: dict[str, Any]) -> None:
    payload["generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    payload["api_calls_used"] = len(payload.get("api_calls") or [])
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def already(payload: dict[str, Any], name: str) -> bool:
    return any(c.get("name") == name and c.get("ok") for c in payload.get("api_calls") or [])


def run_call(client: Any, payload: dict[str, Any], *, n: int, name: str, customer_id: str, query: str):
    if already(payload, name):
        print(f"skip {name} (already ok)")
        return True
    if len(payload["api_calls"]) >= MAX_CALLS:
        payload["hard_stop"] = "call cap reached"
        print(f"CALL CAP — skip {name}")
        return False
    print(f"GAQL {len(payload['api_calls']) + 1}/{MAX_CALLS}: {name}")
    try:
        rows = list(run_gaql(client, customer_id, query))
    except QuotaExhaustedError as exc:
        payload["api_calls"].append(
            {"n": n, "name": name, "ok": False, "error": "RESOURCE_EXHAUSTED", "detail": str(exc)}
        )
        payload["hard_stop"] = "RESOURCE_EXHAUSTED"
        save(payload)
        print(f"RESOURCE_EXHAUSTED on {name} — STOP.", file=sys.stderr)
        return False
    except SgGoogleAdsError as exc:
        payload["api_calls"].append(
            {"n": n, "name": name, "ok": False, "error": str(exc)}
        )
        save(payload)
        print(f"{name} failed: {exc}", file=sys.stderr)
        return False
    payload["_last_rows"] = rows
    payload["api_calls"].append(
        {"n": n, "name": name, "ok": True, "row_count": len(rows)}
    )
    print(f"  → {len(rows)} rows")
    return True


def parse_inventory(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        rsa = row.ad_group_ad.ad.responsive_search_ad
        out.append(
            {
                "campaign": row.campaign.name,
                "campaign_status": _enum(row.campaign.status),
                "ad_group": row.ad_group.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_group_status": _enum(row.ad_group.status),
                "ad_id": str(row.ad_group_ad.ad.id),
                "status": _enum(row.ad_group_ad.status),
                "final_urls": list(row.ad_group_ad.ad.final_urls),
                "path1": rsa.path1 or "",
                "path2": rsa.path2 or "",
                "headlines": [{"text": h.text, "pin": _pin(h)} for h in (rsa.headlines or [])],
                "descriptions": [
                    {"text": d.text, "pin": _pin(d)} for d in (rsa.descriptions or [])
                ],
            }
        )
    return out


def parse_rsa_daily(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "date": str(row.segments.date),
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "ad_id": str(row.ad_group_ad.ad.id),
                "status": _enum(row.ad_group_ad.status),
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "conversions": float(row.metrics.conversions or 0),
                "cost": _money(row.metrics.cost_micros),
            }
        )
    return out


def parse_assets(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        view = row.ad_group_ad_asset_view
        asset = row.asset
        text = ""
        if getattr(asset, "text_asset", None) and asset.text_asset.text:
            text = asset.text_asset.text
        out.append(
            {
                "date": str(row.segments.date),
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "ad_id": str(row.ad_group_ad.ad.id),
                "asset_id": str(asset.id),
                "field_type": _enum(view.field_type),
                "performance_label": _enum(view.performance_label),
                "text": text,
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "conversions": float(row.metrics.conversions or 0),
                "cost": _money(row.metrics.cost_micros),
            }
        )
    return out


def parse_keywords(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "criterion_id": str(row.ad_group_criterion.criterion_id),
                "status": _enum(row.ad_group_criterion.status),
                "keyword": _kw_text(row.ad_group_criterion),
                "match": _kw_match(row.ad_group_criterion),
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "conversions": float(row.metrics.conversions or 0),
                "cost": _money(row.metrics.cost_micros),
            }
        )
    return out


def parse_terms(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "date": str(row.segments.date),
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "search_term": (row.search_term_view.search_term or "").strip(),
                "status": _enum(row.search_term_view.status),
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "conversions": float(row.metrics.conversions or 0),
                "cost": _money(row.metrics.cost_micros),
            }
        )
    return out


def parse_auction(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        view = row.auction_insight_view
        out.append(
            {
                "campaign": row.campaign.name,
                "domain": getattr(view, "display_domain", "") or "",
                "impressions": int(row.metrics.impressions or 0),
                "impression_share": float(
                    getattr(row.metrics, "auction_insight_search_impression_share", 0) or 0
                ),
                "overlap_rate": float(
                    getattr(row.metrics, "auction_insight_search_overlap_rate", 0) or 0
                ),
                "outranking_share": float(
                    getattr(row.metrics, "auction_insight_outranking_share", 0) or 0
                ),
                "position_above_rate": float(
                    getattr(row.metrics, "auction_insight_position_above_rate", 0) or 0
                ),
                "top_impression_pct": float(
                    getattr(row.metrics, "auction_insight_top_impression_percentage", 0) or 0
                ),
                "abs_top_impression_pct": float(
                    getattr(
                        row.metrics,
                        "auction_insight_absolute_top_impression_percentage",
                        0,
                    )
                    or 0
                ),
            }
        )
    return out


def inventory_q(camps: str) -> str:
    return f"""
        SELECT
          campaign.name,
          campaign.status,
          ad_group.id,
          ad_group.name,
          ad_group.status,
          ad_group_ad.status,
          ad_group_ad.ad.id,
          ad_group_ad.ad.final_urls,
          ad_group_ad.ad.responsive_search_ad.headlines,
          ad_group_ad.ad.responsive_search_ad.descriptions,
          ad_group_ad.ad.responsive_search_ad.path1,
          ad_group_ad.ad.responsive_search_ad.path2
        FROM ad_group_ad
        WHERE campaign.name IN ({camps})
          AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
          AND ad_group_ad.status != REMOVED
          AND ad_group.status != REMOVED
          AND campaign.status != REMOVED
    """


def rsa_daily_q(camps: str) -> str:
    return f"""
        SELECT
          segments.date,
          campaign.name,
          ad_group.name,
          ad_group_ad.ad.id,
          ad_group_ad.status,
          metrics.impressions,
          metrics.clicks,
          metrics.conversions,
          metrics.cost_micros
        FROM ad_group_ad
        WHERE campaign.name IN ({camps})
          AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
          AND ad_group_ad.status != REMOVED
          AND campaign.status != REMOVED
          AND segments.date BETWEEN '{LAUNCH}' AND '{END}'
    """


def assets_q(camps: str) -> str:
    return f"""
        SELECT
          segments.date,
          campaign.name,
          ad_group.name,
          ad_group_ad.ad.id,
          asset.id,
          asset.text_asset.text,
          ad_group_ad_asset_view.field_type,
          ad_group_ad_asset_view.performance_label,
          metrics.impressions,
          metrics.clicks,
          metrics.conversions,
          metrics.cost_micros
        FROM ad_group_ad_asset_view
        WHERE campaign.name IN ({camps})
          AND ad_group_ad.status = ENABLED
          AND ad_group_ad_asset_view.field_type IN (HEADLINE, DESCRIPTION)
          AND campaign.status != REMOVED
          AND segments.date BETWEEN '{LAUNCH}' AND '{END}'
    """


def keywords_q(camps: str) -> str:
    return f"""
        SELECT
          campaign.name,
          ad_group.name,
          ad_group_criterion.criterion_id,
          ad_group_criterion.status,
          ad_group_criterion.keyword.text,
          ad_group_criterion.keyword.match_type,
          metrics.impressions,
          metrics.clicks,
          metrics.conversions,
          metrics.cost_micros
        FROM ad_group_criterion
        WHERE campaign.name IN ({camps})
          AND ad_group_criterion.type = KEYWORD
          AND ad_group_criterion.status = ENABLED
          AND ad_group.status = ENABLED
          AND campaign.status = ENABLED
          AND segments.date BETWEEN '{LAUNCH}' AND '{END}'
    """


def terms_q(camps: str) -> str:
    return f"""
        SELECT
          segments.date,
          campaign.name,
          ad_group.name,
          search_term_view.search_term,
          search_term_view.status,
          metrics.impressions,
          metrics.clicks,
          metrics.conversions,
          metrics.cost_micros
        FROM search_term_view
        WHERE campaign.name IN ({camps})
          AND campaign.status = ENABLED
          AND segments.date BETWEEN '{LAUNCH}' AND '{END}'
    """


def auction_q(camps: str) -> str:
    return f"""
        SELECT
          campaign.name,
          auction_insight_view.display_domain,
          metrics.impressions,
          metrics.auction_insight_search_impression_share,
          metrics.auction_insight_search_overlap_rate,
          metrics.auction_insight_outranking_share,
          metrics.auction_insight_position_above_rate,
          metrics.auction_insight_top_impression_percentage,
          metrics.auction_insight_absolute_top_impression_percentage
        FROM auction_insight_view
        WHERE campaign.name IN ({camps})
          AND campaign.status = ENABLED
          AND segments.date BETWEEN '{LAUNCH}' AND '{END}'
    """


def main() -> int:
    resume = "--resume" in sys.argv
    if resume and OUT.is_file():
        payload = json.loads(OUT.read_text(encoding="utf-8"))
        payload.setdefault("partial", True)
        print(f"Resuming from {OUT.name} ({len(payload.get('api_calls') or [])} calls so far)")
    else:
        payload = empty_payload()

    settings = load_settings()
    client = build_client(settings)
    n = 0

    plan: list[tuple[str, str, str, Any]] = []
    for market in ("US", "AU"):
        camps = CAMPS_SQL[market]
        cid = CUSTOMERS[market]
        plan.extend(
            [
                (market, f"{market.lower()}_rsa_inventory", cid, inventory_q(camps)),
                (market, f"{market.lower()}_rsa_daily", cid, rsa_daily_q(camps)),
                (market, f"{market.lower()}_assets_daily", cid, assets_q(camps)),
                (market, f"{market.lower()}_keywords", cid, keywords_q(camps)),
                (market, f"{market.lower()}_search_terms", cid, terms_q(camps)),
            ]
        )
    # Auction insights last — optional, more likely to fail / cost quota
    plan.append(("US", "us_auction_insights", US_ID, auction_q(CAMPS_SQL["US"])))
    plan.append(("AU", "au_auction_insights", AU_ID, auction_q(CAMPS_SQL["AU"])))

    parsers = {
        "rsa_inventory": ("inventory", parse_inventory),
        "rsa_daily": ("rsa_daily", parse_rsa_daily),
        "assets_daily": ("assets_daily", parse_assets),
        "keywords": ("keywords", parse_keywords),
        "search_terms": ("search_terms", parse_terms),
        "auction_insights": ("auction_insights", parse_auction),
    }

    for market, name, cid, query in plan:
        n += 1
        ok = run_call(client, payload, n=n, name=name, customer_id=cid, query=query)
        if payload.get("hard_stop") == "RESOURCE_EXHAUSTED":
            return 1
        if not ok:
            if payload.get("hard_stop") == "call cap reached":
                break
            continue
        rows = payload.pop("_last_rows", [])
        key_suffix = name.split("_", 1)[1]
        bucket, parser = parsers[key_suffix]
        payload[bucket][market] = parser(rows)
        save(payload)

    payload["partial"] = False
    save(payload)
    print(f"Wrote {OUT.relative_to(REPO)} · {payload['api_calls_used']} calls")
    for market in ("US", "AU"):
        print(
            f"  {market}: inventory {len(payload['inventory'][market])} · "
            f"rsa_daily {len(payload['rsa_daily'][market])} · "
            f"assets {len(payload['assets_daily'][market])} · "
            f"kws {len(payload['keywords'][market])} · "
            f"terms {len(payload['search_terms'][market])} · "
            f"auction {len(payload['auction_insights'][market])}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
