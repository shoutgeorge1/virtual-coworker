#!/usr/bin/env python3
"""Read-only AU RSA inventory + US/AU VC_* asset links. Cap: 3 GAQL searches.

Hard rules:
- No mutate / create / enable / pause
- On RESOURCE_EXHAUSTED: STOP, do not retry
- Brand deferred — VC_* CORE/ROLES only

Usage:
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    /Users/george/Developer/virtual-coworker/ads-launch/probe_au_rsa_assets_readonly.py
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402
from google.ads.googleads.errors import GoogleAdsException  # noqa: E402

from sg_google_ads.client import build_client  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import QuotaExhaustedError  # noqa: E402

load_dotenv(SG_ROOT / ".env")
load_dotenv(SG_ROOT / "clients" / "virtual-coworker.env", override=True)

US = "4967151855"
AU = "5735391940"
OUT = Path(__file__).resolve().parent / "_au_rsa_assets_probe.json"

AU_CAMPS = ("VC_AU_S_CORE", "VC_AU_S_ROLES")
US_CAMPS = ("VC_US_S_CORE", "VC_US_S_ROLES")
# campaign_asset.field_type — IMAGE is not valid here (use AD_IMAGE elsewhere).
ASSET_TYPES = (
    "SITELINK",
    "CALLOUT",
    "STRUCTURED_SNIPPET",
    "CALL",
)


def _quota(exc: BaseException) -> bool:
    t = str(exc).upper()
    return "RESOURCE_EXHAUSTED" in t or ("QUOTA" in t and "EXHAUST" in t)


def _pin(asset) -> str:
    pin = getattr(asset, "pinned_field", None)
    name = getattr(pin, "name", None) if pin is not None else None
    return str(name or "")


def _asset_detail(asset) -> dict:
    t = asset.type_.name
    detail: dict = {"asset_id": str(asset.id), "type": t, "name": asset.name or ""}
    if t == "SITELINK" and asset.sitelink_asset:
        s = asset.sitelink_asset
        detail.update(
            {
                "text": s.link_text,
                "desc1": s.description1,
                "desc2": s.description2,
                "final_urls": list(asset.final_urls),
            }
        )
    elif t == "CALLOUT" and asset.callout_asset:
        detail["text"] = asset.callout_asset.callout_text
    elif t == "STRUCTURED_SNIPPET" and asset.structured_snippet_asset:
        s = asset.structured_snippet_asset
        detail["header"] = s.header
        detail["values"] = list(s.values)
    elif t == "CALL" and asset.call_asset:
        c = asset.call_asset
        detail["phone"] = c.phone_number
        detail["country"] = c.country_code
    return detail


def search(ga, customer_id: str, query: str):
    try:
        yield from ga.search(customer_id=customer_id, query=query)
    except GoogleAdsException as exc:
        if _quota(exc):
            raise QuotaExhaustedError("STOP quota — do not retry") from exc
        raise


def main() -> int:
    settings = load_settings()
    client = build_client(settings)
    ga = client.get_service("GoogleAdsService")
    calls = 0
    notes: list[str] = []
    resume = "--resume" in sys.argv
    prior = {}
    if resume and OUT.exists():
        prior = json.loads(OUT.read_text(encoding="utf-8"))
        notes.append(f"Resumed from {OUT.name} (skipping RSA/metrics if present).")

    rsas: list[dict] = prior.get("rsas") or []
    ag_metrics: dict[str, dict] = {}
    if prior.get("ad_groups") and resume:
        for s in prior["ad_groups"]:
            ag_metrics[s["ad_group"]] = {
                "campaign": s.get("campaign", ""),
                "id": s.get("ad_group_id", ""),
                "status": s.get("ad_group_status", ""),
                "impr": s.get("impr", 0),
                "clicks": s.get("clicks", 0),
                "ctr": s.get("ctr", 0.0),
                "cost": s.get("cost", 0.0),
            }

    if not rsas:
        # --- API 1: AU RSA inventory (no date segment — full inventory) ---
        print("API · AU VC_* RSA inventory (no metrics segment)")
        calls += 1
        rsa_q = f"""
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
          WHERE campaign.name IN ('{"', '".join(AU_CAMPS)}')
            AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
            AND ad_group_ad.status != REMOVED
            AND ad_group.status != REMOVED
            AND campaign.status != REMOVED
        """
        for row in search(ga, AU, rsa_q):
            rsa = row.ad_group_ad.ad.responsive_search_ad
            rsas.append(
                {
                    "campaign": row.campaign.name,
                    "campaign_status": row.campaign.status.name,
                    "ad_group": row.ad_group.name,
                    "ad_group_id": str(row.ad_group.id),
                    "ad_group_status": row.ad_group.status.name,
                    "ad_id": str(row.ad_group_ad.ad.id),
                    "status": row.ad_group_ad.status.name,
                    "final_urls": list(row.ad_group_ad.ad.final_urls),
                    "path1": rsa.path1 or "",
                    "path2": rsa.path2 or "",
                    "headlines": [{"text": h.text, "pin": _pin(h)} for h in rsa.headlines],
                    "descriptions": [{"text": d.text, "pin": _pin(d)} for d in rsa.descriptions],
                }
            )
        # Mid-save so a later asset failure does not burn RSA again
        OUT.write_text(
            json.dumps(
                {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "api_calls_so_far": calls,
                    "mutations": 0,
                    "partial": True,
                    "rsas": rsas,
                    "ad_groups": [],
                    "assets": {},
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    if not ag_metrics:
        # --- API 2: AU AG metrics LAST_30_DAYS (cheap signal) ---
        print("API · AU VC_* ad group metrics LAST_30_DAYS")
        calls += 1
        ag_q = f"""
          SELECT
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            metrics.impressions,
            metrics.clicks,
            metrics.ctr,
            metrics.cost_micros
          FROM ad_group
          WHERE campaign.name IN ('{"', '".join(AU_CAMPS)}')
            AND ad_group.status != REMOVED
            AND campaign.status != REMOVED
            AND segments.date DURING LAST_30_DAYS
        """
        for row in search(ga, AU, ag_q):
            name = row.ad_group.name
            prev = ag_metrics.get(name)
            impr = int(row.metrics.impressions)
            clicks = int(row.metrics.clicks)
            cost = int(row.metrics.cost_micros)
            if prev and "cost_micros" in prev:
                prev["impr"] += impr
                prev["clicks"] += clicks
                prev["cost_micros"] += cost
            elif prev and "cost" in prev and "cost_micros" not in prev:
                # resumed already-finalized metrics — leave alone
                pass
            else:
                ag_metrics[name] = {
                    "campaign": row.campaign.name,
                    "id": str(row.ad_group.id),
                    "status": row.ad_group.status.name,
                    "impr": impr,
                    "clicks": clicks,
                    "cost_micros": cost,
                }
        for m in ag_metrics.values():
            if "cost_micros" in m:
                m["cost"] = round(m.pop("cost_micros") / 1_000_000, 2)
                m["ctr"] = (m["clicks"] / m["impr"]) if m["impr"] else 0.0

    print("API · VC_* campaign assets AU + US")
    asset_q_tpl = """
      SELECT
        campaign.name,
        campaign.status,
        campaign_asset.status,
        campaign_asset.field_type,
        asset.id,
        asset.name,
        asset.type,
        asset.final_urls,
        asset.sitelink_asset.link_text,
        asset.sitelink_asset.description1,
        asset.sitelink_asset.description2,
        asset.callout_asset.callout_text,
        asset.structured_snippet_asset.header,
        asset.structured_snippet_asset.values,
        asset.call_asset.phone_number,
        asset.call_asset.country_code
      FROM campaign_asset
      WHERE campaign.name IN ({camps})
        AND campaign_asset.field_type IN ({types})
        AND campaign.status != REMOVED
    """
    types_sql = ", ".join(ASSET_TYPES)
    assets_by_market: dict[str, list[dict]] = {"AU": [], "US": []}

    calls += 1
    au_asset_q = asset_q_tpl.format(
        camps=", ".join(f"'{c}'" for c in AU_CAMPS),
        types=types_sql,
    )
    for row in search(ga, AU, au_asset_q):
        detail = _asset_detail(row.asset)
        assets_by_market["AU"].append(
            {
                "campaign": row.campaign.name,
                "campaign_status": row.campaign.status.name,
                "link_status": row.campaign_asset.status.name,
                "field_type": row.campaign_asset.field_type.name,
                **detail,
            }
        )

    calls += 1
    us_asset_q = asset_q_tpl.format(
        camps=", ".join(f"'{c}'" for c in US_CAMPS),
        types=types_sql,
    )
    for row in search(ga, US, us_asset_q):
        detail = _asset_detail(row.asset)
        assets_by_market["US"].append(
            {
                "campaign": row.campaign.name,
                "campaign_status": row.campaign.status.name,
                "link_status": row.campaign_asset.status.name,
                "field_type": row.campaign_asset.field_type.name,
                **detail,
            }
        )

    notes.append(
        "Customer-level / AG-level assets not queried this pass — campaign_asset only."
    )
    notes.append(
        "Image assets not queried (campaign_asset.field_type IMAGE invalid) — check Ads UI if needed."
    )
    notes.append(
        f"Session API Search calls this run: {calls} (prior failed IMAGE attempt burned ~2 earlier)."
    )

    by_ag: dict[str, list[dict]] = defaultdict(list)
    for r in rsas:
        by_ag[r["ad_group"]].append(r)

    # Union of AG names from RSAs + metrics
    all_ags = sorted(set(by_ag) | set(ag_metrics), key=lambda n: (by_ag.get(n, [{}])[0].get("campaign", ag_metrics.get(n, {}).get("campaign", "")), n))

    summary = []
    for name in all_ags:
        ads = by_ag.get(name, [])
        enabled = [a for a in ads if a["status"] == "ENABLED"]
        paused = [a for a in ads if a["status"] == "PAUSED"]
        sample = ads[0] if ads else None
        m = ag_metrics.get(name, {})
        total = len(ads)
        # Google max ~3 RSAs per AG; open enabled slot if enabled < 3
        open_enabled_slot = max(0, 3 - len(enabled))
        room_to_create = max(0, 3 - total)
        summary.append(
            {
                "campaign": (sample or {}).get("campaign") or m.get("campaign", ""),
                "campaign_status": (sample or {}).get("campaign_status", ""),
                "ad_group": name,
                "ad_group_id": (sample or {}).get("ad_group_id") or m.get("id", ""),
                "ad_group_status": (sample or {}).get("ad_group_status") or m.get("status", ""),
                "impr": m.get("impr", 0),
                "clicks": m.get("clicks", 0),
                "ctr": m.get("ctr", 0.0),
                "cost": m.get("cost", 0.0),
                "rsa_count": total,
                "enabled_rsas": len(enabled),
                "paused_rsas": len(paused),
                "open_enabled_slot": open_enabled_slot,
                "room_to_create": room_to_create,
                "needs_draft": open_enabled_slot > 0,
                "create_vs_update": (
                    "create"
                    if room_to_create > 0 and open_enabled_slot > 0
                    else ("update_paused" if open_enabled_slot > 0 and paused else "full")
                ),
                "final_urls": sorted({u for a in ads for u in a.get("final_urls", [])}),
                "paths": sorted(
                    {
                        f"{a.get('path1', '')}/{a.get('path2', '')}".strip("/")
                        for a in ads
                        if a.get("path1") or a.get("path2")
                    }
                ),
                "enabled_sample_headlines": [
                    h["text"] for h in (enabled[0]["headlines"] if enabled else [])
                ][:5],
                "paused_ads": [
                    {
                        "ad_id": a["ad_id"],
                        "ctr_note": "inventory only",
                        "h1": a["headlines"][0]["text"] if a["headlines"] else "",
                    }
                    for a in paused
                ],
                "rsas": ads,
            }
        )

    def asset_rollup(rows: list[dict]) -> dict:
        by_type: dict[str, dict] = defaultdict(lambda: {"enabled": [], "paused": [], "other": []})
        for r in rows:
            bucket = "enabled" if r["link_status"] == "ENABLED" else (
                "paused" if r["link_status"] == "PAUSED" else "other"
            )
            by_type[r["type"]][bucket].append(r)
        return {k: dict(v) for k, v in by_type.items()}

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api_calls": calls,
        "mutations": 0,
        "window_metrics": "LAST_30_DAYS",
        "accounts": {"AU": AU, "US": US},
        "notes": notes,
        "ad_groups": summary,
        "rsas": rsas,
        "assets": {
            "AU": assets_by_market["AU"],
            "US": assets_by_market["US"],
            "AU_rollup": asset_rollup(assets_by_market["AU"]),
            "US_rollup": asset_rollup(assets_by_market["US"]),
        },
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"API calls={calls} · mutations=0 · AGs={len(summary)} · RSAs={len(rsas)}")
    print("\n=== AU AG RSA slots ===")
    for s in summary:
        print(
            f"{s['ad_group']:32} {s['campaign'][-5:]:6} "
            f"en={s['enabled_rsas']} pa={s['paused_rsas']} total={s['rsa_count']} "
            f"open={s['open_enabled_slot']} create_room={s['room_to_create']} "
            f"action={s['create_vs_update']} "
            f"impr={s['impr']} clk={s['clicks']} ctr={s['ctr']*100:.1f}%"
        )
    for mkt in ("AU", "US"):
        print(f"\n=== {mkt} ENABLED campaign assets ===")
        for r in assets_by_market[mkt]:
            if r["link_status"] != "ENABLED":
                continue
            label = r.get("text") or r.get("phone") or r.get("header") or r.get("name") or r["asset_id"]
            print(f"  {r['campaign']} · {r['type']} · {label}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QuotaExhaustedError as exc:
        print(f"QUOTA STOP: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
