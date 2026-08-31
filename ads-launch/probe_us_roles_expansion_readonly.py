#!/usr/bin/env python3
"""Read-only US Roles expansion inventory probe.

Authorized by US Search Expansion mega-prompt (2026-08-21) for audit only.
- No mutate / upload / enable / pause / bid / URL / keyword changes
- Stop immediately on RESOURCE_EXHAUSTED — do not retry
- Cap: 8 GAQL calls
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
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reports" / "google-ads" / "us-role-expansion" / "account-inventory-readonly.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

MAX_CALLS = 8
CALLS = 0
STOPPED: str | None = None


def _enum(val: Any) -> str:
    name = getattr(val, "name", None)
    return str(name) if name else str(val or "")


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _num(val: Any) -> float:
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def run_q(client: Any, name: str, query: str) -> dict[str, Any]:
    global CALLS, STOPPED
    if STOPPED:
        return {"ok": False, "name": name, "error": STOPPED, "rows": []}
    if CALLS >= MAX_CALLS:
        STOPPED = "cap"
        return {"ok": False, "name": name, "error": "cap", "rows": []}
    CALLS += 1
    print(f"GAQL {CALLS}/{MAX_CALLS} {name}", flush=True)
    try:
        rows = list(run_gaql(client, US_ID, query))
    except QuotaExhaustedError as exc:
        STOPPED = "RESOURCE_EXHAUSTED"
        return {
            "ok": False,
            "name": name,
            "error": "RESOURCE_EXHAUSTED",
            "detail": str(exc)[:240],
            "rows": [],
        }
    except (ApiAccessError, SgGoogleAdsError) as exc:
        return {
            "ok": False,
            "name": name,
            "error": type(exc).__name__,
            "detail": str(exc)[:240],
            "rows": [],
        }
    return {"ok": True, "name": name, "row_count": len(rows), "raw": rows}


def main() -> int:
    settings = load_settings()
    client = build_client(settings)

    out: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "mutate": False,
        "customer_id": US_ID,
        "max_calls": MAX_CALLS,
        "api_calls_used": 0,
        "hard_stop": None,
        "campaigns": [],
        "ad_groups": [],
        "keywords": [],
        "enabled_rsas": [],
        "shared_sets": [],
        "search_terms_seed": [],
        "converting_landing_pages": [],
    }

    camp = run_q(
        client,
        "campaigns",
        """
      SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.bidding_strategy_type,
        campaign_budget.amount_micros,
        campaign.target_spend.cpc_bid_ceiling_micros,
        campaign.network_settings.target_google_search,
        campaign.network_settings.target_search_network,
        campaign.network_settings.target_content_network,
        campaign.geo_target_type_setting.positive_geo_target_type,
        campaign.final_url_suffix,
        campaign.tracking_url_template
      FROM campaign
      WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
        AND campaign.status != 'REMOVED'
      """,
    )
    for row in camp.get("raw") or []:
        c = row.campaign
        b = row.campaign_budget
        out["campaigns"].append(
            {
                "id": str(c.id),
                "name": c.name,
                "status": _enum(c.status),
                "bidding": _enum(c.bidding_strategy_type),
                "daily_budget_usd": _money(b.amount_micros),
                "cpc_ceiling_usd": _money(
                    getattr(getattr(c, "target_spend", None), "cpc_bid_ceiling_micros", None)
                ),
                "google_search": bool(c.network_settings.target_google_search),
                "search_partners": bool(c.network_settings.target_search_network),
                "display": bool(c.network_settings.target_content_network),
                "positive_geo": _enum(c.geo_target_type_setting.positive_geo_target_type),
                "final_url_suffix": c.final_url_suffix or "",
                "has_tracking_template": bool(c.tracking_url_template),
            }
        )

    ag = run_q(
        client,
        "ad_groups",
        """
      SELECT
        campaign.name,
        ad_group.id,
        ad_group.name,
        ad_group.status,
        ad_group.cpc_bid_micros
      FROM ad_group
      WHERE campaign.name = 'VC_US_S_ROLES'
        AND ad_group.status != 'REMOVED'
      ORDER BY ad_group.name
      """,
    )
    for row in ag.get("raw") or []:
        out["ad_groups"].append(
            {
                "campaign": row.campaign.name,
                "id": str(row.ad_group.id),
                "name": row.ad_group.name,
                "status": _enum(row.ad_group.status),
                "cpc_bid_usd": _money(row.ad_group.cpc_bid_micros),
            }
        )

    kw = run_q(
        client,
        "keywords_roles",
        """
      SELECT
        campaign.name,
        ad_group.name,
        ad_group.id,
        ad_group_criterion.criterion_id,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.status,
        ad_group_criterion.negative,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions
      FROM keyword_view
      WHERE campaign.name = 'VC_US_S_ROLES'
        AND ad_group_criterion.status != 'REMOVED'
        AND segments.date DURING LAST_30_DAYS
      """,
    )
    for row in kw.get("raw") or []:
        crit = row.ad_group_criterion
        out["keywords"].append(
            {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "ad_group_id": str(row.ad_group.id),
                "criterion_id": str(crit.criterion_id),
                "text": crit.keyword.text,
                "match": _enum(crit.keyword.match_type),
                "status": _enum(crit.status),
                "negative": bool(crit.negative),
                "impressions": int(_num(row.metrics.impressions)),
                "clicks": int(_num(row.metrics.clicks)),
                "cost_usd": _money(row.metrics.cost_micros),
                "conversions": _num(row.metrics.conversions),
            }
        )

    ads = run_q(
        client,
        "enabled_rsas",
        """
      SELECT
        campaign.name,
        ad_group.name,
        ad_group.id,
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.ad.final_urls,
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions
      FROM ad_group_ad
      WHERE campaign.name = 'VC_US_S_ROLES'
        AND ad_group_ad.status = 'ENABLED'
        AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
      """,
    )
    for row in ads.get("raw") or []:
        ad = row.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        headlines = [h.text for h in (rsa.headlines or [])]
        descs = [d.text for d in (rsa.descriptions or [])]
        out["enabled_rsas"].append(
            {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_id": str(ad.id),
                "final_urls": list(ad.final_urls or []),
                "headline_count": len(headlines),
                "description_count": len(descs),
                "has_dki": any("{KeyWord:" in h or "{keyword:" in h.lower() for h in headlines),
            }
        )

    shared = run_q(
        client,
        "shared_sets",
        """
      SELECT
        campaign.name,
        shared_set.name,
        shared_set.type,
        shared_set.status,
        campaign_shared_set.status
      FROM campaign_shared_set
      WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
        AND shared_set.type = 'NEGATIVE_KEYWORDS'
      """,
    )
    for row in shared.get("raw") or []:
        out["shared_sets"].append(
            {
                "campaign": row.campaign.name,
                "name": row.shared_set.name,
                "type": _enum(row.shared_set.type),
                "shared_set_status": _enum(row.shared_set.status),
                "attachment_status": _enum(row.campaign_shared_set.status),
            }
        )

    st = run_q(
        client,
        "search_terms_overlap",
        """
      SELECT
        campaign.name,
        ad_group.name,
        search_term_view.search_term,
        segments.keyword.info.text,
        segments.keyword.info.match_type,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions
      FROM search_term_view
      WHERE campaign.name = 'VC_US_S_ROLES'
        AND segments.date DURING LAST_14_DAYS
        AND metrics.impressions > 0
      ORDER BY metrics.impressions DESC
      LIMIT 200
      """,
    )
    for row in st.get("raw") or []:
        term = row.search_term_view.search_term.lower()
        if any(
            s in term
            for s in (
                "quickbook",
                "executive",
                "admin",
                "customer",
                "hr ",
                "recruit",
                "shopify",
                "ecommerce",
                "e-commerce",
                "property",
                "crm",
                "sales support",
            )
        ):
            out["search_terms_seed"].append(
                {
                    "campaign": row.campaign.name,
                    "ad_group": row.ad_group.name,
                    "search_term": row.search_term_view.search_term,
                    "keyword": row.segments.keyword.info.text,
                    "match": _enum(row.segments.keyword.info.match_type),
                    "impressions": int(_num(row.metrics.impressions)),
                    "clicks": int(_num(row.metrics.clicks)),
                    "cost_usd": _money(row.metrics.cost_micros),
                    "conversions": _num(row.metrics.conversions),
                }
            )

    lp = run_q(
        client,
        "landing_page_conv",
        """
      SELECT
        campaign.name,
        landing_page_view.unexpanded_final_url,
        metrics.clicks,
        metrics.conversions,
        metrics.cost_micros
      FROM landing_page_view
      WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
        AND segments.date DURING LAST_30_DAYS
        AND metrics.clicks > 0
      ORDER BY metrics.conversions DESC, metrics.clicks DESC
      LIMIT 50
      """,
    )
    for row in lp.get("raw") or []:
        out["converting_landing_pages"].append(
            {
                "campaign": row.campaign.name,
                "url": row.landing_page_view.unexpanded_final_url,
                "clicks": int(_num(row.metrics.clicks)),
                "conversions": _num(row.metrics.conversions),
                "cost_usd": _money(row.metrics.cost_micros),
            }
        )

    # Optional 8th: languages / locations summary via campaign criterion
    if CALLS < MAX_CALLS and not STOPPED:
        geo = run_q(
            client,
            "campaign_criteria",
            """
      SELECT
        campaign.name,
        campaign_criterion.type,
        campaign_criterion.negative,
        campaign_criterion.language.language_constant,
        campaign_criterion.location.geo_target_constant,
        campaign_criterion.status
      FROM campaign_criterion
      WHERE campaign.name = 'VC_US_S_ROLES'
        AND campaign_criterion.type IN ('LANGUAGE', 'LOCATION', 'AD_SCHEDULE')
      """,
        )
        out["campaign_criteria"] = []
        for row in geo.get("raw") or []:
            out["campaign_criteria"].append(
                {
                    "campaign": row.campaign.name,
                    "type": _enum(row.campaign_criterion.type),
                    "negative": bool(row.campaign_criterion.negative),
                    "status": _enum(row.campaign_criterion.status),
                    "language": str(
                        getattr(getattr(row.campaign_criterion, "language", None), "language_constant", "")
                        or ""
                    ),
                    "location": str(
                        getattr(getattr(row.campaign_criterion, "location", None), "geo_target_constant", "")
                        or ""
                    ),
                }
            )

    out["api_calls_used"] = CALLS
    out["hard_stop"] = STOPPED

    # Drop raw protobufs
    OUT.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT} calls={CALLS} stop={STOPPED}", flush=True)
    print(
        json.dumps(
            {
                "campaigns": len(out["campaigns"]),
                "ad_groups": len(out["ad_groups"]),
                "keywords": len(out["keywords"]),
                "enabled_rsas": len(out["enabled_rsas"]),
                "shared_sets": len(out["shared_sets"]),
                "search_terms_seed": len(out["search_terms_seed"]),
                "landing_pages": len(out["converting_landing_pages"]),
            },
            indent=2,
        )
    )
    return 0 if STOPPED != "RESOURCE_EXHAUSTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
