#!/usr/bin/env python3
"""Resume remaining read-only queries after the first inspect pass.

Does not repeat customer / campaign / ad-group calls.
Stops on RESOURCE_EXHAUSTED. No mutate.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
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
OUT = (
    Path(__file__).resolve().parents[1]
    / "ads-launch"
    / "research"
    / "us-real-estate-account-inspect-2026-08-18.json"
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
    return str(name) if name else str(val)


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def main() -> int:
    payload = json.loads(OUT.read_text())
    windows = payload["windows"]
    payload["resume_at_utc"] = datetime.now(timezone.utc).isoformat()
    payload["hard_stop"] = None

    try:
        settings = load_settings()
        client = build_client(settings)
    except Exception as exc:  # noqa: BLE001
        payload["hard_stop"] = f"client_init: {type(exc).__name__}"
        OUT.write_text(json.dumps(payload, indent=2) + "\n")
        print(json.dumps({"ok": False, "error": payload["hard_stop"]}))
        return 1

    def q(label: str, gaql: str) -> list[Any]:
        payload["api_calls_used"] += 1
        rows = list(run_gaql(client, US_ID, gaql))
        payload.setdefault("api_calls", []).append(
            {"n": payload["api_calls_used"], "label": label, "rows": len(rows)}
        )
        return rows

    try:
        watch_rows = q(
            "watch_keywords",
            """
            SELECT
              campaign.name,
              ad_group.name,
              ad_group_criterion.keyword.text,
              ad_group_criterion.keyword.match_type,
              ad_group_criterion.status,
              ad_group_criterion.negative
            FROM ad_group_criterion
            WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
              AND ad_group_criterion.type = KEYWORD
              AND ad_group_criterion.keyword.text IN (
                'virtual assistant for real estate investors',
                'virtual assistant agency in usa'
              )
            """,
        )
        payload["watch_keywords"] = []
        for row in watch_rows:
            payload["watch_keywords"].append(
                {
                    "campaign": row.campaign.name,
                    "ad_group": row.ad_group.name,
                    "text": row.ad_group_criterion.keyword.text,
                    "match": _enum(row.ad_group_criterion.keyword.match_type),
                    "status": _enum(row.ad_group_criterion.status),
                    "negative": bool(row.ad_group_criterion.negative),
                }
            )

        re_rows = q(
            "re_keywords",
            """
            SELECT
              campaign.name,
              ad_group.name,
              ad_group_criterion.keyword.text,
              ad_group_criterion.keyword.match_type,
              ad_group_criterion.status,
              ad_group_criterion.negative
            FROM ad_group_criterion
            WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
              AND ad_group_criterion.type = KEYWORD
              AND ad_group_criterion.status != REMOVED
              AND ad_group_criterion.keyword.text REGEXP_MATCH
                '(?i).*(real estate|realtor|property management|wholesaling).*'
            """,
        )
        payload["real_estate_keywords"] = []
        for row in re_rows:
            rec = {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "text": row.ad_group_criterion.keyword.text,
                "match": _enum(row.ad_group_criterion.keyword.match_type),
                "status": _enum(row.ad_group_criterion.status),
                "negative": bool(row.ad_group_criterion.negative),
            }
            payload["real_estate_keywords"].append(rec)
            if rec["text"].lower() in WATCH_KW and rec not in payload["watch_keywords"]:
                payload["watch_keywords"].append(rec)

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
              metrics.conversions
            FROM search_term_view
            WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
              AND segments.date BETWEEN '{windows["d30_start"]}' AND '{windows["end"]}'
              AND search_term_view.search_term REGEXP_MATCH
                '(?i).*(real estate|realtor|property management|wholesaling).*'
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
              AND ad_group_ad.status != REMOVED
            """,
        )
        payload["hire_va_ads"] = []
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
              metrics.conversions
            FROM ad_group_ad
            WHERE campaign.name = 'VC_US_S_CORE'
              AND ad_group.name = 'Hire_VA_PH'
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
        payload["rsa_windows"] = {
            name: {
                k: {
                    **v,
                    "ctr_pct": round(100.0 * v["clicks"] / v["impr"], 2)
                    if v["impr"]
                    else 0.0,
                }
                for k, v in data.items()
            }
            for name, data in buckets.items()
        }

        shared_rows = q(
            "shared_sets",
            """
            SELECT
              campaign.name,
              shared_set.name,
              shared_set.type,
              campaign_shared_set.status
            FROM campaign_shared_set
            WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
            """,
        )
        payload["shared_sets"] = []
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
            """
            SELECT
              campaign.name,
              campaign_criterion.location.geo_target_constant,
              campaign_criterion.negative,
              campaign_criterion.status
            FROM campaign_criterion
            WHERE campaign.name IN ('VC_US_S_CORE', 'VC_US_S_ROLES')
              AND campaign_criterion.type = LOCATION
              AND campaign_criterion.status != REMOVED
            """,
        )
        payload["locations"] = []
        for row in loc_rows:
            payload["locations"].append(
                {
                    "campaign": row.campaign.name,
                    "geo": row.campaign_criterion.location.geo_target_constant,
                    "negative": bool(row.campaign_criterion.negative),
                    "status": _enum(row.campaign_criterion.status),
                }
            )

    except QuotaExhaustedError:
        payload["hard_stop"] = (
            f"RESOURCE_EXHAUSTED after {payload['api_calls_used']} calls"
        )
    except (ApiAccessError, SgGoogleAdsError) as exc:
        payload["hard_stop"] = f"api_error after {payload['api_calls_used']} calls"
        payload["notes"] = payload.get("notes") or []
        payload["notes"].append(type(exc).__name__)

    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(
        json.dumps(
            {
                "ok": payload["hard_stop"] is None,
                "api_calls_used": payload["api_calls_used"],
                "watch_keywords": payload.get("watch_keywords"),
                "re_keyword_count": len(payload.get("real_estate_keywords") or []),
                "search_term_rows": len(payload.get("search_terms") or []),
                "hire_va_ads": [
                    {"id": a.get("ad_id"), "status": a.get("status"), "urls": a.get("final_urls")}
                    for a in (payload.get("hire_va_ads") or [])
                ],
                "shared_sets": payload.get("shared_sets"),
                "location_count": len(payload.get("locations") or []),
                "hard_stop": payload["hard_stop"],
            },
            indent=2,
        )
    )
    return 0 if payload["hard_stop"] is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
