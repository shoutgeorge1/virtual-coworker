#!/usr/bin/env python3
"""Cheap read-only Ads pull for Executive ad-copy + buyer-signal sections.

Hard rules:
- No mutate / enable / pause
- On RESOURCE_EXHAUSTED: STOP, do not retry
- Cap: 2 GAQL searches (US RSAs + US search terms). AU terms reused from
  daily-watch.json when present (already pulled today) to save quota.
- Brand deferred — VC_* only

Writes into xray/data/executive-snapshot.json:
  operator.whats_working (live RSA themes + KPIs)
  operator.buyer_signals (live search terms)
  creative (raw rows for audit)

Usage:
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    ads-launch/pull_executive_creative.py
"""

from __future__ import annotations

import json
import re
import sys
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
REPO = Path(__file__).resolve().parents[1]
OUT_EXEC = REPO / "xray" / "data" / "executive-snapshot.json"
DAILY = REPO / "xray" / "data" / "daily-watch.json"
MAX_CALLS = 2

JOB_SEEKER_RE = re.compile(
    r"\b(jobs?|careers?|salary|resume|work\s+from\s+home|job\s*seekers?)\b",
    re.I,
)

# Theme buckets George still cares about — scored from live headlines
THEME_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "Hire Filipino / Philippines VA (employer)",
        re.compile(
            r"filipino|philippines|\bph\b|hire\s+(a\s+)?va|va\s+hire|staffing",
            re.I,
        ),
    ),
    (
        "You interview. You pick.",
        re.compile(r"interview|you\s+pick|you\s+choose|shortlist", re.I),
    ),
    (
        "Dedicated teammate, not a gig marketplace",
        re.compile(r"dedicated|not\s+gig|not\s+a\s+gig|marketplace|platform", re.I),
    ),
    (
        "Agency / firm / company",
        re.compile(r"agency|firm|company|staffing", re.I),
    ),
]


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _pct(ctr: Any) -> float | None:
    try:
        v = float(ctr)
    except (TypeError, ValueError):
        return None
    if v <= 1.0:
        return round(100.0 * v, 1)
    return round(v, 1)


def rsa_query() -> str:
    return """
        SELECT
          campaign.name,
          ad_group.name,
          ad_group_ad.ad.id,
          ad_group_ad.status,
          ad_group_ad.ad.responsive_search_ad.headlines,
          ad_group_ad.ad.responsive_search_ad.descriptions,
          metrics.impressions,
          metrics.clicks,
          metrics.ctr,
          metrics.cost_micros
        FROM ad_group_ad
        WHERE campaign.name LIKE 'VC_US_%'
          AND campaign.status != 'REMOVED'
          AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
          AND ad_group_ad.status = 'ENABLED'
          AND segments.date DURING LAST_7_DAYS
          AND metrics.impressions > 0
        ORDER BY metrics.impressions DESC
    """


def search_terms_query() -> str:
    return """
        SELECT
          campaign.name,
          ad_group.name,
          search_term_view.search_term,
          metrics.impressions,
          metrics.clicks,
          metrics.ctr,
          metrics.cost_micros
        FROM search_term_view
        WHERE campaign.name LIKE 'VC_US_%'
          AND campaign.status != 'REMOVED'
          AND segments.date DURING LAST_7_DAYS
          AND metrics.cost_micros > 0
        ORDER BY metrics.cost_micros DESC
    """


def parse_rsas(rows: list[Any]) -> list[dict[str, Any]]:
    """Aggregate segmented rows to one row per ad_id."""
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        ad = row.ad_group_ad.ad
        ad_id = str(ad.id)
        rsa = ad.responsive_search_ad
        headlines = [h.text for h in (rsa.headlines or []) if getattr(h, "text", None)]
        descriptions = [
            d.text for d in (rsa.descriptions or []) if getattr(d, "text", None)
        ]
        impr = int(row.metrics.impressions or 0)
        clicks = int(row.metrics.clicks or 0)
        cost = _money(row.metrics.cost_micros)
        slot = by_id.get(ad_id)
        if not slot:
            by_id[ad_id] = {
                "ad_id": ad_id,
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "headlines": headlines,
                "descriptions": descriptions,
                "headline_sample": headlines[:6],
                "impressions": impr,
                "clicks": clicks,
                "cost_usd": cost,
            }
        else:
            slot["impressions"] += impr
            slot["clicks"] += clicks
            slot["cost_usd"] = round(slot["cost_usd"] + cost, 2)
    out = list(by_id.values())
    for slot in out:
        impr = slot["impressions"]
        clicks = slot["clicks"]
        slot["ctr_pct"] = round(100.0 * clicks / impr, 1) if impr else None
        slot["avg_cpc_usd"] = (
            round(slot["cost_usd"] / clicks, 2) if clicks else None
        )
    out.sort(key=lambda x: (-x["impressions"], -x["clicks"]))
    return out


def score_themes(rsas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for label, pat in THEME_PATTERNS:
        matched = []
        impr = clicks = 0
        cost = 0.0
        for ad in rsas:
            blob = " | ".join(ad.get("headlines") or [])
            if not pat.search(blob):
                continue
            matched.append(ad)
            impr += int(ad.get("impressions") or 0)
            clicks += int(ad.get("clicks") or 0)
            cost += float(ad.get("cost_usd") or 0)
        if not matched:
            continue
        ctr = round(100.0 * clicks / impr, 1) if impr else None
        # Best headline snippet from top matched ad
        top = matched[0]
        sample = next(
            (h for h in (top.get("headlines") or []) if pat.search(h)),
            (top.get("headlines") or ["—"])[0],
        )
        scored.append(
            {
                "theme": label,
                "sample_headline": sample,
                "ads_matched": len(matched),
                "impressions": impr,
                "clicks": clicks,
                "ctr_pct": ctr,
                "cost_usd": round(cost, 2),
                "top_ad_group": top.get("ad_group"),
            }
        )
    scored.sort(key=lambda x: (-(x["impressions"] or 0), -(x["clicks"] or 0)))
    return scored


def aggregate_search_terms(rows: list[Any]) -> list[dict[str, Any]]:
    by_term: dict[str, dict[str, Any]] = {}
    for row in rows:
        term = (row.search_term_view.search_term or "").strip()
        if not term:
            continue
        key = term.lower()
        impr = int(row.metrics.impressions or 0)
        clicks = int(row.metrics.clicks or 0)
        cost = _money(row.metrics.cost_micros)
        slot = by_term.get(key)
        if not slot:
            by_term[key] = {
                "term": term,
                "market": "US",
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "impressions": impr,
                "clicks": clicks,
                "cost_usd": cost,
                "job_seeker_like": bool(JOB_SEEKER_RE.search(term)),
            }
        else:
            slot["impressions"] += impr
            slot["clicks"] += clicks
            slot["cost_usd"] = round(slot["cost_usd"] + cost, 2)
            if cost >= float(slot.get("_top_cost") or 0):
                slot["campaign"] = row.campaign.name
                slot["ad_group"] = row.ad_group.name
        by_term[key]["_top_cost"] = max(
            float(by_term[key].get("_top_cost") or 0), cost
        )
    out = []
    for slot in by_term.values():
        slot.pop("_top_cost", None)
        impr = slot["impressions"]
        clicks = slot["clicks"]
        slot["ctr_pct"] = round(100.0 * clicks / impr, 1) if impr else None
        out.append(slot)
    out.sort(key=lambda x: (-x["cost_usd"], -x["clicks"]))
    return out


def why_for_term(term: str, *, job_seeker: bool) -> str:
    t = term.lower()
    if job_seeker:
        return "Job-seeker junk — watch / exclude"
    if "agency" in t or "firm" in t or "company" in t:
        return "Employer shopping for a provider"
    if "outsource" in t or "outsourcing" in t:
        return "Outsourcing language — B2B"
    if "staffing" in t or "remote staff" in t:
        return "Staffing language buyers use"
    if "filipino" in t or "philippines" in t or t.endswith(" ph") or " ph " in f" {t} ":
        return "PH / Filipino hire intent"
    if "virtual assistant" in t or t.startswith("va ") or " va" in t:
        return "VA hire search"
    return "Buyer search with spend"


def buyer_signals_from_terms(terms: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, Any]]:
    """Prefer employer signals; keep one junk watch if spendy."""
    employer = [t for t in terms if not t.get("job_seeker_like")]
    junk = [t for t in terms if t.get("job_seeker_like") and float(t.get("cost_usd") or 0) >= 5]
    picks = employer[: max(limit - 1, 1)]
    if junk and len(picks) < limit:
        picks.append(junk[0])
    signals = []
    for t in picks[:limit]:
        signals.append(
            {
                "term": t["term"],
                "why": why_for_term(t["term"], job_seeker=bool(t.get("job_seeker_like"))),
                "market": t.get("market") or "US",
                "clicks": t.get("clicks"),
                "impressions": t.get("impressions"),
                "ctr_pct": t.get("ctr_pct"),
                "cost_usd": t.get("cost_usd"),
                "campaign": t.get("campaign"),
            }
        )
    return signals


def au_terms_from_daily() -> list[dict[str, Any]]:
    if not DAILY.is_file():
        return []
    try:
        data = json.loads(DAILY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    top = (
        ((data.get("markets") or {}).get("AU") or {})
        .get("search_terms", {})
        .get("top_by_spend")
        or []
    )
    out = []
    for t in top[:5]:
        term = t.get("search_term") or ""
        if not term:
            continue
        out.append(
            {
                "term": term,
                "why": why_for_term(
                    term, job_seeker=bool(t.get("job_seeker_like"))
                ),
                "market": "AU",
                "clicks": t.get("clicks"),
                "cost_usd": t.get("cost_usd"),
                "campaign": t.get("campaign"),
            }
        )
    return out


def themes_as_copy_lines(themes: list[dict[str, Any]]) -> list[str]:
    lines = []
    for th in themes:
        bits = [th["theme"]]
        if th.get("sample_headline"):
            bits.append(f'e.g. “{th["sample_headline"]}”')
        kpi = []
        if th.get("impressions") is not None:
            kpi.append(f"{th['impressions']:,} impr")
        if th.get("clicks") is not None:
            kpi.append(f"{th['clicks']:,} clicks")
        if th.get("ctr_pct") is not None:
            kpi.append(f"{th['ctr_pct']}% CTR")
        if kpi:
            bits.append("· " + " · ".join(kpi))
        lines.append(" — ".join(bits[:2]) + (" " + bits[2] if len(bits) > 2 else ""))
    return lines


def main() -> int:
    settings = load_settings()
    client = build_client(settings)
    api_calls: list[dict[str, Any]] = []
    rsas: list[dict[str, Any]] = []
    terms: list[dict[str, Any]] = []

    try:
        print("GAQL 1/2: US VC_* RSA performance LAST_7_DAYS…")
        rows = list(run_gaql(client, US_ID, rsa_query()))
        api_calls.append(
            {"n": 1, "name": "us_rsa_performance_7d", "ok": True, "row_count": len(rows)}
        )
        rsas = parse_rsas(rows)
        print(f"  → {len(rsas)} unique RSAs with impressions")
    except QuotaExhaustedError as exc:
        print(f"RESOURCE_EXHAUSTED on RSA pull — STOP. {exc}", file=sys.stderr)
        api_calls.append({"n": 1, "name": "us_rsa_performance_7d", "ok": False, "error": str(exc)})
        return 1
    except SgGoogleAdsError as exc:
        print(f"RSA pull failed: {exc}", file=sys.stderr)
        api_calls.append({"n": 1, "name": "us_rsa_performance_7d", "ok": False, "error": str(exc)})
        return 1

    if len(api_calls) >= MAX_CALLS:
        print("Call cap reached before search terms — stop.")
    else:
        try:
            print("GAQL 2/2: US VC_* search terms LAST_7_DAYS…")
            rows = list(run_gaql(client, US_ID, search_terms_query()))
            api_calls.append(
                {
                    "n": 2,
                    "name": "us_search_terms_7d",
                    "ok": True,
                    "row_count": len(rows),
                }
            )
            terms = aggregate_search_terms(rows)
            print(f"  → {len(terms)} unique terms with spend")
        except QuotaExhaustedError as exc:
            print(f"RESOURCE_EXHAUSTED on search terms — STOP. {exc}", file=sys.stderr)
            api_calls.append(
                {"n": 2, "name": "us_search_terms_7d", "ok": False, "error": str(exc)}
            )
            # Keep RSA results; still merge what we have
        except SgGoogleAdsError as exc:
            print(f"Search-term pull failed: {exc}", file=sys.stderr)
            api_calls.append(
                {"n": 2, "name": "us_search_terms_7d", "ok": False, "error": str(exc)}
            )

    themes = score_themes(rsas)
    top_rsas = rsas[:8]
    signals = buyer_signals_from_terms(terms, limit=7)
    # Append a couple AU employer terms from today's daily-watch (no extra Ads call)
    for au in au_terms_from_daily():
        if len(signals) >= 9:
            break
        if any(s["term"].lower() == au["term"].lower() for s in signals):
            continue
        if "job-seeker" in (au.get("why") or "").lower():
            continue
        signals.append(au)

    copy_lines = themes_as_copy_lines(themes)
    # Fallback: if theme regex missed, show top RSA headline samples with KPIs
    if not copy_lines and top_rsas:
        for ad in top_rsas[:4]:
            h = (ad.get("headline_sample") or ["(no headline)"])[0]
            copy_lines.append(
                f"“{h}” — {ad.get('ad_group')} · "
                f"{ad.get('impressions', 0):,} impr · {ad.get('clicks', 0)} clicks · "
                f"{ad.get('ctr_pct')}% CTR"
            )

    note = (
        f"Live US RSAs · last 7 days · pulled "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC. "
        "Themes scored from headlines that actually served."
    )

    creative = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "api_calls": api_calls,
        "api_calls_used": len(api_calls),
        "api_calls_max": MAX_CALLS,
        "window": "LAST_7_DAYS",
        "top_rsas": top_rsas,
        "themes": themes,
        "top_search_terms": terms[:20],
        "buyer_signals": signals,
        "au_terms_source": "daily-watch.json (no extra Ads call)" if DAILY.is_file() else None,
    }

    if OUT_EXEC.is_file():
        snap = json.loads(OUT_EXEC.read_text(encoding="utf-8"))
    else:
        snap = {"generated_at_utc": creative["generated_at_utc"]}

    op = snap.get("operator") or {}
    op["whats_working"] = {
        "ad_copy_themes": copy_lines,
        "note": note,
        "source": "live_rsa_performance",
        "themes_detail": themes,
        "top_rsas": [
            {
                "ad_group": a.get("ad_group"),
                "sample": (a.get("headline_sample") or [""])[0],
                "impressions": a.get("impressions"),
                "clicks": a.get("clicks"),
                "ctr_pct": a.get("ctr_pct"),
            }
            for a in top_rsas[:5]
        ],
    }
    if signals:
        op["buyer_signals"] = signals
    snap["operator"] = op
    snap["creative"] = creative
    snap["creative_merged_at_utc"] = creative["generated_at_utc"]

    OUT_EXEC.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    print(f"Merged creative → {OUT_EXEC.relative_to(REPO)}")
    print("Themes:")
    for line in copy_lines:
        print(f"  · {line}")
    print("Buyer signals:")
    for s in signals:
        print(f"  · [{s.get('market')}] {s['term']} — {s['why']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
