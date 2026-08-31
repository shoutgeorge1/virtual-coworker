#!/usr/bin/env python3
"""Read-only Aug 18 conversion forensic — US + AU.

George authorized extra Google Ads reads for this investigation (2026-08-20).

Hard rules:
- No mutate / upload / enable / pause / bid / URL / keyword changes
- Stop immediately on RESOURCE_EXHAUSTED — do not retry
- Do not print tokens
- Raw GCLIDs never written to xray/ — hashed only
"""

from __future__ import annotations

import hashlib
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
AU_ID = "5735391940"
REPO = Path(__file__).resolve().parents[1]
LOCAL_OUT = REPO / ".local" / "ads" / "aug18-forensic-ads.json"
PUB_OUT = REPO / "xray" / "data" / "aug18-forensic-ads.json"

WINDOW_START = "2026-08-17"
WINDOW_END = "2026-08-20"
FOCUS = "2026-08-18"
MAX_CALLS = 16
CALLS = 0
STOPPED: str | None = None

ACCOUNTS = {
    "US": {"id": US_ID, "prefix": "VC_US_%"},
    "AU": {"id": AU_ID, "prefix": "VC_AU_%"},
}


def _enum(val: Any) -> str:
    if val is None:
        return ""
    name = getattr(val, "name", None)
    if name:
        return str(name)
    return str(val or "")


def _num(val: Any) -> float:
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _hash_id(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def _rsa_texts(assets: Any) -> list[str]:
    out: list[str] = []
    for item in assets or []:
        text = getattr(item, "text", None)
        if text:
            out.append(str(text))
    return out


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


def campaign_date_q(prefix: str) -> str:
    return f"""
      SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        segments.date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.all_conversions,
        metrics.conversions_value,
        metrics.all_conversions_value,
        metrics.conversions_by_conversion_date,
        metrics.all_conversions_by_conversion_date
      FROM campaign
      WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        AND campaign.name LIKE '{prefix}'
        AND campaign.status != REMOVED
    """


def action_q(prefix: str) -> str:
    return f"""
      SELECT
        campaign.name,
        segments.date,
        segments.conversion_action,
        segments.conversion_action_name,
        segments.conversion_action_category,
        metrics.conversions,
        metrics.all_conversions,
        metrics.conversions_value,
        metrics.all_conversions_value,
        metrics.conversions_by_conversion_date,
        metrics.all_conversions_by_conversion_date
      FROM campaign
      WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        AND campaign.name LIKE '{prefix}'
        AND (
          metrics.all_conversions > 0
          OR metrics.all_conversions_by_conversion_date > 0
        )
    """


def keyword_q(prefix: str) -> str:
    return f"""
      SELECT
        campaign.name,
        ad_group.id,
        ad_group.name,
        ad_group_criterion.criterion_id,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        segments.date,
        segments.device,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.all_conversions,
        metrics.conversions_value,
        metrics.conversions_by_conversion_date,
        metrics.all_conversions_by_conversion_date
      FROM keyword_view
      WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        AND campaign.name LIKE '{prefix}'
        AND (
          metrics.clicks > 0
          OR metrics.conversions > 0
          OR metrics.all_conversions > 0
          OR metrics.conversions_by_conversion_date > 0
          OR metrics.all_conversions_by_conversion_date > 0
        )
    """


def search_term_q(prefix: str) -> str:
    return f"""
      SELECT
        campaign.name,
        ad_group.name,
        search_term_view.search_term,
        segments.keyword.info.text,
        segments.keyword.info.match_type,
        segments.search_term_match_type,
        segments.date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.all_conversions,
        metrics.conversions_by_conversion_date,
        metrics.all_conversions_by_conversion_date
      FROM search_term_view
      WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        AND campaign.name LIKE '{prefix}'
        AND (
          metrics.clicks > 0
          OR metrics.conversions > 0
          OR metrics.all_conversions > 0
          OR metrics.conversions_by_conversion_date > 0
        )
    """


def ad_q(prefix: str) -> str:
    return f"""
      SELECT
        campaign.name,
        ad_group.id,
        ad_group.name,
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.ad.final_urls,
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions,
        ad_group_ad.ad.responsive_search_ad.path1,
        ad_group_ad.ad.responsive_search_ad.path2,
        segments.date,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.all_conversions,
        metrics.conversions_by_conversion_date,
        metrics.all_conversions_by_conversion_date
      FROM ad_group_ad
      WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        AND campaign.name LIKE '{prefix}'
        AND ad_group_ad.status != REMOVED
        AND (
          metrics.clicks > 0
          OR metrics.conversions > 0
          OR metrics.all_conversions > 0
          OR metrics.conversions_by_conversion_date > 0
        )
    """


def geo_q(prefix: str) -> str:
    return f"""
      SELECT
        campaign.name,
        ad_group.name,
        geographic_view.country_criterion_id,
        geographic_view.location_type,
        segments.geo_target_region,
        segments.geo_target_city,
        segments.date,
        segments.device,
        metrics.clicks,
        metrics.conversions,
        metrics.all_conversions,
        metrics.conversions_by_conversion_date
      FROM geographic_view
      WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        AND campaign.name LIKE '{prefix}'
        AND (
          metrics.conversions > 0
          OR metrics.all_conversions > 0
          OR metrics.conversions_by_conversion_date > 0
        )
    """


def click_q(prefix: str) -> str:
    return f"""
      SELECT
        click_view.gclid,
        campaign.id,
        campaign.name,
        ad_group.id,
        ad_group.name,
        click_view.keyword,
        click_view.keyword_info.match_type,
        segments.date,
        segments.device,
        segments.ad_network_type
      FROM click_view
      WHERE segments.date = '{FOCUS}'
        AND campaign.name LIKE '{prefix}'
    """


def parse_campaign(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "campaign_id": str(row.campaign.id),
                "campaign": row.campaign.name,
                "status": _enum(row.campaign.status),
                "date": row.segments.date,
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "cost": _money(row.metrics.cost_micros),
                "conversions": _num(row.metrics.conversions),
                "all_conversions": _num(row.metrics.all_conversions),
                "conversions_value": _num(row.metrics.conversions_value),
                "all_conversions_value": _num(row.metrics.all_conversions_value),
                "conversions_by_conversion_date": _num(row.metrics.conversions_by_conversion_date),
                "all_conversions_by_conversion_date": _num(
                    row.metrics.all_conversions_by_conversion_date
                ),
            }
        )
    return out


def parse_actions(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        resource = str(row.segments.conversion_action or "")
        action_id = resource.rsplit("/", 1)[-1] if resource else ""
        out.append(
            {
                "campaign": row.campaign.name,
                "date": row.segments.date,
                "action_id": action_id,
                "action": row.segments.conversion_action_name,
                "category": _enum(row.segments.conversion_action_category),
                "conversions": _num(row.metrics.conversions),
                "all_conversions": _num(row.metrics.all_conversions),
                "conversions_value": _num(row.metrics.conversions_value),
                "all_conversions_value": _num(row.metrics.all_conversions_value),
                "conversions_by_conversion_date": _num(row.metrics.conversions_by_conversion_date),
                "all_conversions_by_conversion_date": _num(
                    row.metrics.all_conversions_by_conversion_date
                ),
            }
        )
    return out


def parse_keywords(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "campaign": row.campaign.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_group": row.ad_group.name,
                "criterion_id": str(row.ad_group_criterion.criterion_id),
                "keyword": row.ad_group_criterion.keyword.text,
                "match": _enum(row.ad_group_criterion.keyword.match_type),
                "date": row.segments.date,
                "device": _enum(row.segments.device),
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "cost": _money(row.metrics.cost_micros),
                "conversions": _num(row.metrics.conversions),
                "all_conversions": _num(row.metrics.all_conversions),
                "conversions_value": _num(row.metrics.conversions_value),
                "conversions_by_conversion_date": _num(row.metrics.conversions_by_conversion_date),
                "all_conversions_by_conversion_date": _num(
                    row.metrics.all_conversions_by_conversion_date
                ),
            }
        )
    return out


def parse_terms(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "search_term": row.search_term_view.search_term,
                "keyword": row.segments.keyword.info.text,
                "keyword_match": _enum(row.segments.keyword.info.match_type),
                "search_term_match": _enum(row.segments.search_term_match_type),
                "date": row.segments.date,
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "cost": _money(row.metrics.cost_micros),
                "conversions": _num(row.metrics.conversions),
                "all_conversions": _num(row.metrics.all_conversions),
                "conversions_by_conversion_date": _num(row.metrics.conversions_by_conversion_date),
                "all_conversions_by_conversion_date": _num(
                    row.metrics.all_conversions_by_conversion_date
                ),
            }
        )
    return out


def parse_ads(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        ad = row.ad_group_ad.ad
        rsa = ad.responsive_search_ad
        out.append(
            {
                "campaign": row.campaign.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_group": row.ad_group.name,
                "ad_id": str(ad.id),
                "status": _enum(row.ad_group_ad.status),
                "final_urls": list(ad.final_urls or []),
                "path1": rsa.path1,
                "path2": rsa.path2,
                "headlines": _rsa_texts(rsa.headlines),
                "descriptions": _rsa_texts(rsa.descriptions),
                "date": row.segments.date,
                "impressions": int(row.metrics.impressions or 0),
                "clicks": int(row.metrics.clicks or 0),
                "cost": _money(row.metrics.cost_micros),
                "conversions": _num(row.metrics.conversions),
                "all_conversions": _num(row.metrics.all_conversions),
                "conversions_by_conversion_date": _num(row.metrics.conversions_by_conversion_date),
                "all_conversions_by_conversion_date": _num(
                    row.metrics.all_conversions_by_conversion_date
                ),
            }
        )
    return out


def parse_geo(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "country_criterion_id": str(row.geographic_view.country_criterion_id),
                "location_type": _enum(row.geographic_view.location_type),
                "region_criterion_id": str(row.segments.geo_target_region or ""),
                "city_criterion_id": str(row.segments.geo_target_city or ""),
                "date": row.segments.date,
                "device": _enum(row.segments.device),
                "clicks": int(row.metrics.clicks or 0),
                "conversions": _num(row.metrics.conversions),
                "all_conversions": _num(row.metrics.all_conversions),
                "conversions_by_conversion_date": _num(row.metrics.conversions_by_conversion_date),
            }
        )
    return out


def parse_clicks(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        gclid = str(row.click_view.gclid or "")
        kw = row.click_view.keyword
        out.append(
            {
                "gclid_hash": _hash_id(gclid),
                "has_gclid": bool(gclid),
                "campaign_id": str(row.campaign.id),
                "campaign": row.campaign.name,
                "ad_group_id": str(row.ad_group.id),
                "ad_group": row.ad_group.name,
                "keyword_resource": str(kw or ""),
                "match": _enum(row.click_view.keyword_info.match_type),
                "date": row.segments.date,
                "device": _enum(row.segments.device),
                "network": _enum(row.segments.ad_network_type),
            }
        )
    return out


def public_ads(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop bulky creative copy from the public snapshot except converting rows."""
    slim = []
    for row in rows:
        keep_copy = (
            _num(row.get("conversions")) > 0
            or _num(row.get("all_conversions")) > 0
            or _num(row.get("conversions_by_conversion_date")) > 0
        )
        item = dict(row)
        if not keep_copy:
            item.pop("headlines", None)
            item.pop("descriptions", None)
        slim.append(item)
    return slim


def pull_account(client: Any, market: str) -> dict[str, Any]:
    cfg = ACCOUNTS[market]
    cid = cfg["id"]
    prefix = cfg["prefix"]
    calls: list[dict[str, Any]] = []

    camp = run_q(client, cid, f"{market}_campaign_date", campaign_date_q(prefix))
    calls.append({k: camp[k] for k in camp if k != "raw"})
    actions = run_q(client, cid, f"{market}_actions", action_q(prefix))
    calls.append({k: actions[k] for k in actions if k != "raw"})
    kws = run_q(client, cid, f"{market}_keywords", keyword_q(prefix))
    calls.append({k: kws[k] for k in kws if k != "raw"})
    terms = run_q(client, cid, f"{market}_search_terms", search_term_q(prefix))
    calls.append({k: terms[k] for k in terms if k != "raw"})
    ads = run_q(client, cid, f"{market}_ads", ad_q(prefix))
    calls.append({k: ads[k] for k in ads if k != "raw"})
    geo = run_q(client, cid, f"{market}_geo", geo_q(prefix))
    calls.append({k: geo[k] for k in geo if k != "raw"})
    clicks = run_q(client, cid, f"{market}_clicks_aug18", click_q(prefix))
    calls.append({k: clicks[k] for k in clicks if k != "raw"})

    campaign_rows = parse_campaign(camp.get("raw") or []) if camp.get("ok") else []
    action_rows = parse_actions(actions.get("raw") or []) if actions.get("ok") else []
    keyword_rows = parse_keywords(kws.get("raw") or []) if kws.get("ok") else []
    term_rows = parse_terms(terms.get("raw") or []) if terms.get("ok") else []
    ad_rows = parse_ads(ads.get("raw") or []) if ads.get("ok") else []
    geo_rows = parse_geo(geo.get("raw") or []) if geo.get("ok") else []
    click_rows = parse_clicks(clicks.get("raw") or []) if clicks.get("ok") else []

    converting_kws = [
        r
        for r in keyword_rows
        if r["date"] == FOCUS
        and (
            r["conversions"] > 0
            or r["all_conversions"] > 0
            or r["conversions_by_conversion_date"] > 0
        )
    ]
    converting_terms = [
        r
        for r in term_rows
        if r["date"] == FOCUS
        and (
            r["conversions"] > 0
            or r["all_conversions"] > 0
            or r["conversions_by_conversion_date"] > 0
        )
    ]
    converting_ads = [
        r
        for r in ad_rows
        if r["date"] == FOCUS
        and (
            r["conversions"] > 0
            or r["all_conversions"] > 0
            or r["conversions_by_conversion_date"] > 0
        )
    ]

    return {
        "customer_id": cid,
        "ok": all(c.get("ok") for c in calls if not STOPPED),
        "calls": calls,
        "campaigns": campaign_rows,
        "actions": action_rows,
        "keywords": keyword_rows,
        "search_terms": term_rows,
        "ads": ad_rows,
        "geo": geo_rows,
        "clicks_aug18": click_rows,
        "converting_keywords_aug18": converting_kws,
        "converting_terms_aug18": converting_terms,
        "converting_ads_aug18": converting_ads,
        "focus_campaigns": [r for r in campaign_rows if r["date"] == FOCUS],
        "focus_actions": [r for r in action_rows if r["date"] == FOCUS],
    }


def main() -> int:
    settings = load_settings()
    client = build_client(settings)
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": true_flag(),
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
        "focus_day": FOCUS,
        "timezone_note": (
            "Google Ads account time. US account America/Los_Angeles. "
            "AU account Australia/Sydney. segments.date follows each account timezone."
        ),
        "api": "Google Ads API GAQL via shoutgeorge-ads",
        "api_calls_max": MAX_CALLS,
        "hard_stop": None,
        "US": None,
        "AU": None,
    }
    payload["US"] = pull_account(client, "US")
    if STOPPED == "RESOURCE_EXHAUSTED":
        payload["hard_stop"] = "US RESOURCE_EXHAUSTED — did not call AU"
    else:
        payload["AU"] = pull_account(client, "AU")
        if STOPPED == "RESOURCE_EXHAUSTED":
            payload["hard_stop"] = "AU RESOURCE_EXHAUSTED after US"
    payload["api_calls_used"] = CALLS
    payload["hard_stop"] = payload["hard_stop"] or STOPPED

    LOCAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    public = {
        **{k: payload[k] for k in payload if k not in {"US", "AU"}},
        "US": slim_market(payload.get("US")),
        "AU": slim_market(payload.get("AU")),
    }
    PUB_OUT.parent.mkdir(parents=True, exist_ok=True)
    PUB_OUT.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {LOCAL_OUT}", flush=True)
    print(f"wrote {PUB_OUT}", flush=True)
    print(f"calls={CALLS} stop={STOPPED}", flush=True)
    for market in ("US", "AU"):
        block = payload.get(market) or {}
        print(
            f"{market} campaigns={len(block.get('campaigns') or [])} "
            f"kw={len(block.get('converting_keywords_aug18') or [])} "
            f"st={len(block.get('converting_terms_aug18') or [])} "
            f"ads={len(block.get('converting_ads_aug18') or [])}",
            flush=True,
        )
    return 0


def true_flag() -> bool:
    return True


def slim_market(block: dict[str, Any] | None) -> dict[str, Any] | None:
    if not block:
        return block
    return {
        "customer_id": block.get("customer_id"),
        "ok": block.get("ok"),
        "calls": block.get("calls"),
        "campaigns": block.get("campaigns"),
        "actions": block.get("actions"),
        "converting_keywords_aug18": block.get("converting_keywords_aug18"),
        "converting_terms_aug18": block.get("converting_terms_aug18"),
        "converting_ads_aug18": public_ads(block.get("converting_ads_aug18") or []),
        "geo": block.get("geo"),
        "focus_campaigns": block.get("focus_campaigns"),
        "focus_actions": block.get("focus_actions"),
        "click_count_aug18": len(block.get("clicks_aug18") or []),
        "keyword_rows_window": len(block.get("keywords") or []),
        "search_term_rows_window": len(block.get("search_terms") or []),
        "watched_terms": [
            r
            for r in (block.get("search_terms") or [])
            if r.get("date") == FOCUS
            and (
                "virtual assistant hiring in australia" in (r.get("search_term") or "").lower()
                or "virtual assistant for real estate" in (r.get("search_term") or "").lower()
                or "australia virtual assistant" in (r.get("search_term") or "").lower()
                or "real estate investor" in (r.get("search_term") or "").lower()
            )
        ],
        "watched_keywords": [
            r
            for r in (block.get("keywords") or [])
            if r.get("date") == FOCUS
            and (
                (r.get("keyword") or "").lower()
                in {
                    "australia virtual assistant",
                    "virtual assistant for real estate investors",
                }
            )
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
