#!/usr/bin/env python3
"""Read-only US real-estate vertical inspection. No mutate.

George authorized extra read-only queries in the 2026-08-18 vertical brief.
US customer only. Stop immediately on RESOURCE_EXHAUSTED.
Does not print developer tokens, refresh tokens, or client secrets.
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
ACCOUNT_DISPLAY = "496-715-1855"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "ads-launch" / "research" / "us-real-estate-account-inspect-2026-08-18.json"

CAMPAIGN_NAMES = ("VC_US_S_CORE", "VC_US_S_ROLES")
NEW_AGS = (
    "Real_Estate_VA_PH",
    "Real_Estate_Investors_VA_PH",
    "Property_Management_VA_PH",
)
WATCH_KW = (
    "virtual assistant for real estate investors",
    "virtual assistant agency in usa",
)
KW_NEEDLES = (
    "real estate",
    "realtor",
    "property management",
    "wholesaling",
    "agency in usa",
)


def _enum(val: Any) -> str:
    if val is None:
        return ""
    name = getattr(val, "name", None)
    if name:
        return str(name)
    return str(val)


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _micros(val: Any) -> int | None:
    try:
        n = int(val)
    except (TypeError, ValueError):
        return None
    return n if n > 0 else None


def _windows() -> dict[str, str]:
    today = date.today()
    end = today - timedelta(days=1)
    return {
        "end": end.isoformat(),
        "d7_start": (end - timedelta(days=6)).isoformat(),
        "d14_start": (end - timedelta(days=13)).isoformat(),
        "d30_start": (end - timedelta(days=29)).isoformat(),
    }


def main() -> int:
    windows = _windows()
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "mutate": False,
        "account_display": ACCOUNT_DISPLAY,
        "api_calls_used": 0,
        "hard_stop": None,
        "access_level": None,
        "windows": windows,
        "customer": None,
        "campaigns": [],
        "ad_groups": [],
        "new_ad_groups_present": [],
        "watch_keywords": [],
        "real_estate_keywords": [],
        "search_terms": [],
        "hire_va_ads": [],
        "rsa_windows": {"d7": {}, "d14": {}, "d30": {}},
        "shared_sets": [],
        "locations": [],
        "identity_ok": False,
        "notes": [],
    }
    try:
        settings = load_settings()
        payload["access_level"] = settings.access_level
        client = build_client(settings)
    except Exception as exc:  # noqa: BLE001
        payload["hard_stop"] = f"client_init: {type(exc).__name__}"
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + "\n")
        print(json.dumps({"ok": False, "error": payload["hard_stop"]}, indent=2))
        return 1

    def q(label: str, gaql: str) -> list[Any]:
        payload["api_calls_used"] += 1
        rows = list(run_gaql(client, US_ID, gaql))
        payload.setdefault("api_calls", []).append(
            {"n": payload["api_calls_used"], "label": label, "rows": len(rows)}
        )
        return rows

    try:
        cust_rows = q(
            "customer",
            """
            SELECT
              customer.id,
              customer.descriptive_name,
              customer.currency_code,
              customer.time_zone,
              customer.status
            FROM customer
            LIMIT 1
            """,
        )
        if cust_rows:
            c = cust_rows[0].customer
            payload["customer"] = {
                "descriptive_name": c.descriptive_name,
                "currency": c.currency_code,
                "time_zone": c.time_zone,
                "status": _enum(c.status),
                "id_matches_us_editor_account": True,
            }

        camp_rows = q(
            "campaigns",
            f"""
            SELECT
              campaign.id,
              campaign.name,
              campaign.status,
              campaign.bidding_strategy_type,
              campaign.advertising_channel_type,
              campaign_budget.amount_micros,
              campaign_budget.explicitly_shared,
              campaign.target_spend.cpc_bid_ceiling_micros,
              campaign.network_settings.target_google_search,
              campaign.network_settings.target_search_network,
              campaign.network_settings.target_content_network,
              campaign.geo_target_type_setting.positive_geo_target_type,
              campaign.tracking_url_template,
              campaign.final_url_suffix,
              campaign.payment_mode
            FROM campaign
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
            """,
        )
        for row in camp_rows:
            camp = row.campaign
            payload["campaigns"].append(
                {
                    "name": camp.name,
                    "status": _enum(camp.status),
                    "bidding_strategy_type": _enum(camp.bidding_strategy_type),
                    "channel": _enum(camp.advertising_channel_type),
                    "daily_budget_usd": _money(row.campaign_budget.amount_micros),
                    "budget_shared": bool(row.campaign_budget.explicitly_shared),
                    "cpc_ceiling_usd": _money(
                        camp.target_spend.cpc_bid_ceiling_micros
                    )
                    or None,
                    "google_search": bool(
                        camp.network_settings.target_google_search
                    ),
                    "search_partners": bool(
                        camp.network_settings.target_search_network
                    ),
                    "display": bool(camp.network_settings.target_content_network),
                    "positive_geo_target": _enum(
                        camp.geo_target_type_setting.positive_geo_target_type
                    ),
                    "final_url_suffix": camp.final_url_suffix or "",
                    "has_tracking_template": bool(camp.tracking_url_template),
                }
            )

        names = {c["name"] for c in payload["campaigns"]}
        payload["identity_ok"] = names == set(CAMPAIGN_NAMES)
        if not payload["identity_ok"]:
            payload["notes"].append(
                f"Campaign names mismatch. Found: {sorted(names)}"
            )

        ag_rows = q(
            "ad_groups",
            f"""
            SELECT
              campaign.name,
              ad_group.id,
              ad_group.name,
              ad_group.status,
              ad_group.cpc_bid_micros
            FROM ad_group
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
              AND ad_group.status != 'REMOVED'
            """,
        )
        for row in ag_rows:
            rec = {
                "campaign": row.campaign.name,
                "name": row.ad_group.name,
                "status": _enum(row.ad_group.status),
                "cpc_bid_usd": _money(row.ad_group.cpc_bid_micros) or None,
            }
            payload["ad_groups"].append(rec)
            if rec["name"] in NEW_AGS:
                payload["new_ad_groups_present"].append(rec)

        kw_rows = q(
            "keywords",
            f"""
            SELECT
              campaign.name,
              ad_group.name,
              ad_group_criterion.criterion_id,
              ad_group_criterion.keyword.text,
              ad_group_criterion.keyword.match_type,
              ad_group_criterion.status,
              ad_group_criterion.negative
            FROM ad_group_criterion
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
              AND ad_group_criterion.type = 'KEYWORD'
              AND ad_group_criterion.status != 'REMOVED'
              AND (
                ad_group.name IN ('{NEW_AGS[0]}', '{NEW_AGS[1]}', '{NEW_AGS[2]}')
                OR ad_group_criterion.keyword.text IN (
                  'virtual assistant for real estate investors',
                  'virtual assistant agency in usa'
                )
                OR ad_group_criterion.keyword.text REGEXP_MATCH
                  '(?i).*(real estate|realtor|property management|wholesaling).*'
              )
            """,
        )
        for row in kw_rows:
            text = (row.ad_group_criterion.keyword.text or "").lower()
            rec = {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "text": row.ad_group_criterion.keyword.text,
                "match": _enum(row.ad_group_criterion.keyword.match_type),
                "status": _enum(row.ad_group_criterion.status),
                "negative": bool(row.ad_group_criterion.negative),
            }
            if rec["text"].lower() in WATCH_KW:
                payload["watch_keywords"].append(rec)
            if any(n in text for n in KW_NEEDLES):
                payload["real_estate_keywords"].append(rec)

        st_rows = q(
            "search_terms_30d",
            f"""
            SELECT
              campaign.name,
              ad_group.name,
              search_term_view.search_term,
              search_term_view.status,
              segments.date,
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              metrics.conversions,
              metrics.ctr
            FROM search_term_view
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
              AND segments.date BETWEEN '{windows["d30_start"]}' AND '{windows["end"]}'
              AND search_term_view.search_term REGEXP_MATCH '(?i).*(real estate|realtor|property management|wholesaling).*'
            """,
        )
        st_agg: dict[tuple[str, str, str], dict[str, Any]] = {}
        for row in st_rows:
            key = (
                row.campaign.name,
                row.ad_group.name,
                row.search_term_view.search_term,
            )
            cur = st_agg.setdefault(
                key,
                {
                    "campaign": row.campaign.name,
                    "ad_group": row.ad_group.name,
                    "term": row.search_term_view.search_term,
                    "status": _enum(row.search_term_view.status),
                    "impr": 0,
                    "clicks": 0,
                    "cost": 0.0,
                    "conv": 0.0,
                    "dates": [],
                },
            )
            cur["impr"] += int(row.metrics.impressions or 0)
            cur["clicks"] += int(row.metrics.clicks or 0)
            cur["cost"] = round(cur["cost"] + _money(row.metrics.cost_micros), 2)
            cur["conv"] = round(cur["conv"] + float(row.metrics.conversions or 0), 2)
            cur["dates"].append(row.segments.date)
        payload["search_terms"] = sorted(
            st_agg.values(), key=lambda r: (-r["clicks"], -r["impr"], r["term"])
        )

        ad_rows = q(
            "hire_va_ads",
            """
            SELECT
              campaign.name,
              ad_group.name,
              ad_group_ad.status,
              ad_group_ad.ad.id,
              ad_group_ad.ad.type,
              ad_group_ad.ad.final_urls,
              ad_group_ad.ad.responsive_search_ad.headlines,
              ad_group_ad.ad.responsive_search_ad.descriptions,
              ad_group_ad.ad.responsive_search_ad.path1,
              ad_group_ad.ad.responsive_search_ad.path2,
              ad_group_ad.policy_summary.approval_status,
              ad_group_ad.policy_summary.review_status
            FROM ad_group_ad
            WHERE campaign.name = 'VC_US_S_CORE'
              AND ad_group.name = 'Hire_VA_PH'
              AND ad_group_ad.status != 'REMOVED'
            """,
        )
        for row in ad_rows:
            ad = row.ad_group_ad.ad
            rsa = ad.responsive_search_ad
            payload["hire_va_ads"].append(
                {
                    "ad_id": str(ad.id),
                    "status": _enum(row.ad_group_ad.status),
                    "type": _enum(ad.type),
                    "final_urls": list(ad.final_urls),
                    "path1": rsa.path1,
                    "path2": rsa.path2,
                    "headlines": [h.text for h in rsa.headlines],
                    "descriptions": [d.text for d in rsa.descriptions],
                    "approval": _enum(row.ad_group_ad.policy_summary.approval_status),
                    "review": _enum(row.ad_group_ad.policy_summary.review_status),
                }
            )

        perf_rows = q(
            "rsa_perf_30d",
            f"""
            SELECT
              campaign.name,
              ad_group.name,
              ad_group_ad.ad.id,
              ad_group_ad.status,
              segments.date,
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              metrics.conversions,
              metrics.ctr
            FROM ad_group_ad
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
              AND ad_group.name IN ('Hire_VA_PH', 'VA_Agency_Firm_PH')
              AND segments.date BETWEEN '{windows["d30_start"]}' AND '{windows["end"]}'
            """,
        )
        buckets = {
            "d7": defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0}),
            "d14": defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0}),
            "d30": defaultdict(lambda: {"impr": 0, "clicks": 0, "cost": 0.0, "conv": 0.0}),
        }
        d7, d14, d30 = windows["d7_start"], windows["d14_start"], windows["d30_start"]
        for row in perf_rows:
            day = row.segments.date
            key = f"{row.ad_group.name}|{row.ad_group_ad.ad.id}|{_enum(row.ad_group_ad.status)}"
            rec = {
                "impr": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "cost": _money(row.metrics.cost_micros),
                "conv": float(row.metrics.conversions or 0),
            }
            for name, start in (("d30", d30), ("d14", d14), ("d7", d7)):
                if day >= start:
                    b = buckets[name][key]
                    b["impr"] += rec["impr"]
                    b["clicks"] += rec["clicks"]
                    b["cost"] = round(b["cost"] + rec["cost"], 2)
                    b["conv"] = round(b["conv"] + rec["conv"], 2)
        for name, data in buckets.items():
            payload["rsa_windows"][name] = {
                k: {
                    **v,
                    "ctr_pct": round(100.0 * v["clicks"] / v["impr"], 2)
                    if v["impr"]
                    else 0.0,
                }
                for k, v in data.items()
            }

        shared_rows = q(
            "shared_sets",
            f"""
            SELECT
              campaign.name,
              shared_set.name,
              shared_set.type,
              campaign_shared_set.status
            FROM campaign_shared_set
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
            """,
        )
        for row in shared_rows:
            payload["shared_sets"].append(
                {
                    "campaign": row.campaign.name,
                    "name": row.shared_set.name,
                    "type": _enum(row.shared_set.type),
                    "status": _enum(row.campaign_shared_set.status),
                }
            )

        loc_rows = q(
            "locations",
            f"""
            SELECT
              campaign.name,
              campaign_criterion.location.geo_target_constant,
              campaign_criterion.negative,
              campaign_criterion.status
            FROM campaign_criterion
            WHERE campaign.name IN ('{CAMPAIGN_NAMES[0]}', '{CAMPAIGN_NAMES[1]}')
              AND campaign_criterion.type = 'LOCATION'
              AND campaign_criterion.status != 'REMOVED'
            """,
        )
        for row in loc_rows:
            payload["locations"].append(
                {
                    "campaign": row.campaign.name,
                    "geo": row.campaign_criterion.location.geo_target_constant,
                    "negative": bool(row.campaign_criterion.negative),
                    "status": _enum(row.campaign_criterion.status),
                }
            )

    except QuotaExhaustedError as exc:
        payload["hard_stop"] = f"RESOURCE_EXHAUSTED after {payload['api_calls_used']} calls"
        payload["notes"].append(str(exc))
    except (ApiAccessError, SgGoogleAdsError) as exc:
        payload["hard_stop"] = f"api_error after {payload['api_calls_used']} calls"
        payload["notes"].append(type(exc).__name__)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    summary = {
        "ok": payload["hard_stop"] is None,
        "identity_ok": payload["identity_ok"],
        "access_level": payload["access_level"],
        "api_calls_used": payload["api_calls_used"],
        "campaigns": [
            {
                "name": c["name"],
                "status": c["status"],
                "bid": c["bidding_strategy_type"],
                "budget": c["daily_budget_usd"],
            }
            for c in payload["campaigns"]
        ],
        "watch_keywords": payload["watch_keywords"],
        "new_ad_groups_present": payload["new_ad_groups_present"],
        "search_term_rows": len(payload["search_terms"]),
        "shared_sets": payload["shared_sets"],
        "hard_stop": payload["hard_stop"],
        "out": str(OUT),
    }
    print(json.dumps(summary, indent=2))
    return 0 if payload["hard_stop"] is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
