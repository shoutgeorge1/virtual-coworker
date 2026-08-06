#!/usr/bin/env python3
"""Historical Google Ads Editor performance audit (local UTF-16 CSVs).

Window: ~2024-08-01 → 2026-08-04 (as exported 2026-08-05).
Dedupes Exact / close-variant duplicate ST rows when metrics identical.
Writes audits under ads-launch/ and audit-data/performance/.
No Ads API. No mutations.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERF = ROOT / "audit-data" / "performance"
OUT_DIR = ROOT / "ads-launch"
AUDIT_DIR = PERF

USA_ST = PERF / "search_terms_usa_4967151855_2026-08-05.csv"
AU_ST = PERF / "search_terms_au_5735391940_2026-08-05.csv"
USA_CAMP = PERF / "campaigns_metrics_usa_4967151855_2026-08-05.csv"
AU_CAMP = PERF / "campaigns_metrics_au_5735391940_2026-08-05.csv"


def read_utf16_tsv(path: Path) -> list[dict[str, str]]:
    raw = path.read_bytes()
    # Strip UTF-16 BOM if present
    text = raw.decode("utf-16")
    # Editor exports are tab-separated
    lines = text.splitlines()
    # Drop empty trailing
    lines = [ln for ln in lines if ln.strip()]
    if not lines:
        return []
    reader = csv.DictReader(lines, delimiter="\t")
    return [dict(row) for row in reader]


def num(val: str | None) -> float:
    if val is None:
        return 0.0
    s = str(val).strip().replace(",", "").replace("%", "")
    if s in ("", "--", " —", "—"):
        return 0.0
    # currency
    s = s.replace("$", "").replace("A$", "").replace("AU$", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def metric_key(row: dict[str, str]) -> tuple:
    cols = [
        "Impr.",
        "Impressions",
        "Clicks",
        "Cost",
        "Conversions",
        "All conv.",
        "All conversions",
        "Conv. value",
        "Conversion value",
    ]
    vals = []
    for c in cols:
        if c in row:
            vals.append(round(num(row.get(c)), 4))
    return tuple(vals)


def normalize_term(term: str) -> str:
    t = term.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def classify_term(term: str) -> str:
    t = normalize_term(term)
    if any(
        x in t
        for x in (
            "job",
            "salary",
            "career",
            "resume",
            "hiring me",
            "i need a job",
            "work from home",
            "wfh",
        )
    ):
        return "job_seeker_or_wfh"
    if any(
        x in t
        for x in (
            "asistente virtual",
            "español",
            "colombia",
            "argentina",
            "mexico",
            "latam",
        )
    ):
        return "spanish_latam"
    if any(
        x in t
        for x in (
            "medical",
            "nurse",
            "doctor",
            "dentist",
            "programmer",
            "developer",
            "coding",
            "web design",
        )
    ):
        return "excluded_vertical"
    if any(
        x in t
        for x in (
            "onlinejobs",
            "upwork",
            "fiverr",
            "bruntwork",
            "hellorache",
            "myoutdesk",
            "wishup",
        )
    ):
        return "marketplace_or_competitor"
    if any(x in t for x in ("review", "pricing", "cost", "how much", "top 10")):
        return "research_pricing"
    if "virtual coworker" in t or "virtualcoworker" in t:
        return "brand"
    if any(
        x in t
        for x in (
            "bookkeep",
            "accountant",
            "accounting",
            "social media",
            "digital marketing",
            "customer service",
            "recruit",
            "human resource",
            " hr ",
            "sales va",
            "appointment setter",
            "virtual assistant",
            "offshore va",
            "filipino va",
        )
    ):
        if any(x in t for x in ("hire", "hiring", "outsource", "philippines", "filipino", "offshore")):
            return "employer_intent_keep"
        return "possible_employer_generic"
    return "other"


def category_hint(term: str) -> str:
    t = normalize_term(term)
    rules = [
        ("digital-marketing", ("digital marketing", "marketing virtual assistant", "marketing va", "virtual marketing")),
        ("social-media", ("social media",)),
        ("accounting", ("accounting", "accountant")),
        ("bookkeeping", ("bookkeep", "book keeper")),
        ("customer-service", ("customer service", "customer support", "csr")),
        ("hr", ("human resource", "hr virtual", "hr va")),
        ("recruitment", ("recruitment", "recruiter", "recruiting")),
        ("sales", ("sales va", "sales virtual", "appointment setter", "lead generation virtual")),
        ("administrative-support", ("virtual assistant", "executive assistant", "admin assistant", "offshore va", "filipino va")),
    ]
    for slug, keys in rules:
        if any(k in t for k in keys):
            return slug
    return "unmapped"


def dedupe_search_terms(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], dict]:
    """Collapse Exact / close-variant duplicates when metrics identical.

    Method:
    1. Group by normalized search term (casefold, whitespace collapse).
    2. Within each group, if two+ rows have identical metric tuple, keep one.
    3. If metrics differ, keep all (different campaigns/match types may share term).
    4. Also collapse rows that only differ by 'Added/Excluded' when metrics identical
       for the same term+keyword pair.
    """
    raw_n = len(rows)
    by_term: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        term = normalize_term(r.get("Search term") or r.get("Search Term") or "")
        if not term:
            continue
        by_term[term].append(r)

    kept: list[dict[str, str]] = []
    dropped_identical = 0
    for term, group in by_term.items():
        seen_metric_keys: set[tuple] = set()
        for r in group:
            mk = metric_key(r) + (
                (r.get("Campaign") or "").strip().lower(),
                (r.get("Ad group") or r.get("Ad Group") or "").strip().lower(),
                (r.get("Keyword") or "").strip().lower(),
                (r.get("Match type") or r.get("Match Type") or "").strip().lower(),
            )
            # Identical metrics + same campaign/AG/keyword → Exact/CV duplicate row
            identity = metric_key(r) + (
                (r.get("Campaign") or "").strip().lower(),
                (r.get("Ad group") or r.get("Ad Group") or "").strip().lower(),
                normalize_term(r.get("Keyword") or ""),
            )
            if identity in seen_metric_keys:
                dropped_identical += 1
                continue
            # Also drop pure metric clones with empty campaign (export artifact)
            bare = metric_key(r) + (term,)
            camp = (r.get("Campaign") or "").strip()
            if not camp and bare in seen_metric_keys:
                dropped_identical += 1
                continue
            seen_metric_keys.add(identity)
            if not camp:
                seen_metric_keys.add(bare)
            kept.append(r)

    stats = {
        "raw_rows": raw_n,
        "deduped_rows": len(kept),
        "dropped_identical_metric_dupes": dropped_identical,
        "unique_normalized_terms": len(by_term),
        "method": (
            "Group by casefold+whitespace-normalized Search term; "
            "drop rows with identical (impressions,clicks,cost,conversions,all_conv) "
            "+ same Campaign + Ad group + normalized Keyword. "
            "Close-variant / Exact duplicates from Editor often share these fields."
        ),
    }
    return kept, stats


def aggregate_terms(rows: list[dict[str, str]]) -> list[dict]:
    agg: dict[str, dict] = {}
    for r in rows:
        term = normalize_term(r.get("Search term") or r.get("Search Term") or "")
        if not term:
            continue
        a = agg.setdefault(
            term,
            {
                "search_term": term,
                "clicks": 0.0,
                "cost": 0.0,
                "conversions": 0.0,
                "all_conversions": 0.0,
                "impressions": 0.0,
                "class": classify_term(term),
                "category_hint": category_hint(term),
            },
        )
        a["clicks"] += num(r.get("Clicks"))
        a["cost"] += num(r.get("Cost"))
        a["conversions"] += num(r.get("Conversions"))
        a["all_conversions"] += num(
            r.get("All conv") or r.get("All conv.") or r.get("All conversions")
        )
        a["impressions"] += num(r.get("Impr.") or r.get("Impressions"))
    out = list(agg.values())
    out.sort(key=lambda x: (-x["conversions"], -x["cost"], -x["clicks"]))
    return out


def campaign_summary(rows: list[dict[str, str]]) -> list[dict]:
    out = []
    for r in rows:
        name = (r.get("Campaign") or "").strip()
        if not name:
            continue
        cost = num(r.get("Cost"))
        clicks = num(r.get("Clicks"))
        conv = num(r.get("Conversions"))
        allc = num(r.get("All conv") or r.get("All conv.") or r.get("All conversions"))
        out.append(
            {
                "campaign": name,
                "campaign_type": r.get("Campaign type") or r.get("Campaign Type") or "",
                "status": r.get("Campaign status") or r.get("Campaign Status") or "",
                "cost": cost,
                "clicks": clicks,
                "conversions": conv,
                "all_conversions": allc,
                "cpa": (cost / conv) if conv > 0 else None,
                "note": "Conversions ≠ All conversions ≠ job orders",
            }
        )
    out.sort(key=lambda x: -(x["cost"] or 0))
    return out


def main() -> None:
    usa_raw = read_utf16_tsv(USA_ST)
    au_raw = read_utf16_tsv(AU_ST)
    usa_deduped, usa_stats = dedupe_search_terms(usa_raw)
    au_deduped, au_stats = dedupe_search_terms(au_raw)

    usa_agg = aggregate_terms(usa_deduped)
    au_agg = aggregate_terms(au_deduped)

    usa_camp = campaign_summary(read_utf16_tsv(USA_CAMP))
    au_camp = campaign_summary(read_utf16_tsv(AU_CAMP))

    # Prior v4 benchmarks (from FULL-BUILD-REPORT) for validation
    prior = {
        "usa_cost_approx": 724000,
        "usa_clicks_approx": 87000,
        "usa_conv_approx": 2597,
        "au_cost_approx": 457000,
        "au_clicks_approx": 49000,
        "au_conv_approx": 1413,
        "usa_st_raw_approx": 66900,
        "au_st_raw_approx": 26200,
    }

    def totals(camps: list[dict]) -> dict:
        return {
            "cost": round(sum(c["cost"] for c in camps), 2),
            "clicks": round(sum(c["clicks"] for c in camps), 2),
            "conversions": round(sum(c["conversions"] for c in camps), 2),
            "all_conversions": round(sum(c["all_conversions"] for c in camps), 2),
        }

    usa_t = totals(usa_camp)
    au_t = totals(au_camp)

    def delta(actual: float, approx: float) -> str:
        if approx == 0:
            return "n/a"
        pct = abs(actual - approx) / approx * 100
        return f"{pct:.1f}% vs prior cite"

    payload = {
        "window": "Editor export ~2024-08-01 to 2026-08-04 (files dated 2026-08-05)",
        "honesty": {
            "conversions_vs_all": "Conversions ≠ All conversions ≠ job orders/placements",
            "st_vs_campaign": "Search-term cost totals are typically < campaign totals (not every click has an ST row; PMax/DSA mix).",
            "no_fabricated_metrics": True,
        },
        "dedupe_method": usa_stats["method"],
        "usa": {
            "search_terms": usa_stats,
            "campaign_totals": usa_t,
            "prior_benchmark_check": {
                "cost": {"actual": usa_t["cost"], "prior_cite": prior["usa_cost_approx"], "delta": delta(usa_t["cost"], prior["usa_cost_approx"])},
                "clicks": {"actual": usa_t["clicks"], "prior_cite": prior["usa_clicks_approx"], "delta": delta(usa_t["clicks"], prior["usa_clicks_approx"])},
                "conversions": {"actual": usa_t["conversions"], "prior_cite": prior["usa_conv_approx"], "delta": delta(usa_t["conversions"], prior["usa_conv_approx"])},
                "st_raw_rows": {"actual": usa_stats["raw_rows"], "prior_cite": prior["usa_st_raw_approx"], "delta": delta(usa_stats["raw_rows"], prior["usa_st_raw_approx"])},
            },
            "top_employer_terms": [t for t in usa_agg if t["class"] == "employer_intent_keep"][:40],
            "top_waste_terms": [
                t
                for t in usa_agg
                if t["class"]
                in ("job_seeker_or_wfh", "marketplace_or_competitor", "spanish_latam", "research_pricing")
            ][:40],
            "class_counts": _class_counts(usa_agg),
            "worst_campaigns_by_cpa": [c for c in usa_camp if c["conversions"] > 0][:15],
        },
        "au": {
            "search_terms": au_stats,
            "campaign_totals": au_t,
            "prior_benchmark_check": {
                "cost": {"actual": au_t["cost"], "prior_cite": prior["au_cost_approx"], "delta": delta(au_t["cost"], prior["au_cost_approx"])},
                "clicks": {"actual": au_t["clicks"], "prior_cite": prior["au_clicks_approx"], "delta": delta(au_t["clicks"], prior["au_clicks_approx"])},
                "conversions": {"actual": au_t["conversions"], "prior_cite": prior["au_conv_approx"], "delta": delta(au_t["conversions"], prior["au_conv_approx"])},
                "st_raw_rows": {"actual": au_stats["raw_rows"], "prior_cite": prior["au_st_raw_approx"], "delta": delta(au_stats["raw_rows"], prior["au_st_raw_approx"])},
            },
            "top_employer_terms": [t for t in au_agg if t["class"] == "employer_intent_keep"][:40],
            "top_waste_terms": [
                t
                for t in au_agg
                if t["class"]
                in ("job_seeker_or_wfh", "marketplace_or_competitor", "spanish_latam", "research_pricing")
            ][:40],
            "class_counts": _class_counts(au_agg),
            "worst_campaigns_by_cpa": [c for c in au_camp if c["conversions"] > 0][:15],
        },
    }

    # Sort worst by CPA descending
    for mkt in ("usa", "au"):
        payload[mkt]["worst_campaigns_by_cpa"] = sorted(
            [c for c in (usa_camp if mkt == "usa" else au_camp) if (c["cpa"] or 0) > 0],
            key=lambda c: -(c["cpa"] or 0),
        )[:20]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "historical-performance-summary.json"
    json_path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {json_path}")
    print("USA ST", usa_stats)
    print("AU ST", au_stats)
    print("USA camp totals", usa_t)
    print("AU camp totals", au_t)


def _class_counts(agg: list[dict]) -> dict[str, int]:
    c: dict[str, int] = defaultdict(int)
    for t in agg:
        c[t["class"]] += 1
    return dict(sorted(c.items(), key=lambda x: -x[1]))


if __name__ == "__main__":
    main()
