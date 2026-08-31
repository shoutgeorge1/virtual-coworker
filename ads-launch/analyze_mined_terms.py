#!/usr/bin/env python3
"""Detailed analysis of Phase 1 (Ranking), Phase 2 (Zoho Validation), Phase 3 (Coverage), Phase 4 (Executive Summary).
"""

import csv
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
PERF = ROOT / "audit-data" / "performance"
USA_ST = PERF / "search_terms_usa_4967151855_2026-08-05.csv"
AU_ST = PERF / "search_terms_au_5735391940_2026-08-05.csv"

from mine_historical_search_terms import (
    classify_intent,
    load_current_keywords,
    load_search_terms,
    normalize_term,
    num,
    check_coverage
)

def run_deep_analysis():
    us_terms = load_search_terms(USA_ST)
    au_terms = load_search_terms(AU_ST)
    current_kws = load_current_keywords()
    
    # Load winning path registry and any Zoho forensic caches if present
    registry_file = ROOT / "ads-launch/aug18-winners/winning-path-registry.json"
    registry_terms = {}
    if registry_file.exists():
        with open(registry_file) as f:
            reg_data = json.load(f)
            for hj in reg_data.get("human_journeys", []):
                st = normalize_term(hj.get("search_term", ""))
                if st:
                    registry_terms[st] = hj
                    
    print(f"Loaded {len(registry_terms)} human journeys from winning-path-registry")

    # Let's inspect each country separately
    for country, terms in [("US", us_terms), ("AU", au_terms)]:
        print(f"\n=======================================================")
        print(f"                   {country} ANALYSIS")
        print(f"=======================================================")
        
        # Filter for employer intent only (and note job seekers separately)
        emp_terms = {k: v for k, v in terms.items() if v["intent"] == "employer_intent"}
        js_terms = {k: v for k, v in terms.items() if v["intent"] == "job_seeker"}
        comp_terms = {k: v for k, v in terms.items() if v["intent"] == "competitor_or_platform"}
        
        # 1. High Volume Converting Terms (Clicks >= 10, Conv >= 2)
        print(f"\n--- {country} C. Highest-Volume Converting Employer-Intent Terms (Clicks >= 10, Conv >= 2) ---")
        high_vol = sorted(
            [t for t in emp_terms.items() if t[1]["clicks"] >= 10 and t[1]["conversions"] >= 2],
            key=lambda x: (x[1]["conversions"], x[1]["clicks"]),
            reverse=True
        )
        for term, d in high_vol[:20]:
            cov_status, cov_kw = check_coverage(term, current_kws[country])
            print(f"'{term}' | Clk: {d['clicks']:.0f} | Conv: {d['conversions']:.1f} | CVR: {d['cvr']:.1f}% | CPA: ${d['cpa']:.2f} | Cost: ${d['cost']:.2f} | Coverage: {cov_status} ({cov_kw})")
            
        # 2. Highest Conversion Rate with Meaningful Volume (Clicks >= 10, Conv >= 2)
        print(f"\n--- {country} A. Highest Conversion Rate with Meaningful Volume (Clicks >= 10, Conv >= 2) ---")
        high_cvr = sorted(
            [t for t in emp_terms.items() if t[1]["clicks"] >= 10 and t[1]["conversions"] >= 2],
            key=lambda x: (x[1]["cvr"], x[1]["conversions"]),
            reverse=True
        )
        for term, d in high_cvr[:15]:
            cov_status, cov_kw = check_coverage(term, current_kws[country])
            print(f"'{term}' | Clk: {d['clicks']:.0f} | Conv: {d['conversions']:.1f} | CVR: {d['cvr']:.1f}% | CPA: ${d['cpa']:.2f} | Coverage: {cov_status} ({cov_kw})")

        # 3. Best Cost per Conversion with Meaningful Volume (Clicks >= 10, Conv >= 2)
        print(f"\n--- {country} B. Best Cost per Conversion with Meaningful Volume (Clicks >= 10, Conv >= 2) ---")
        best_cpa = sorted(
            [t for t in emp_terms.items() if t[1]["clicks"] >= 10 and t[1]["conversions"] >= 2 and d["cpa"] > 0],
            key=lambda x: (x[1]["cpa"], -x[1]["conversions"])
        )
        for term, d in best_cpa[:15]:
            cov_status, cov_kw = check_coverage(term, current_kws[country])
            print(f"'{term}' | CPA: ${d['cpa']:.2f} | Conv: {d['conversions']:.1f} | Clk: {d['clicks']:.0f} | CVR: {d['cvr']:.1f}% | Coverage: {cov_status} ({cov_kw})")

        # 4. Interesting Long-Tail Converting Terms (Clicks 3 to 9, Conv >= 1, CVR >= 20%)
        print(f"\n--- {country} D. Interesting Long-Tail Strong CVR Terms (Clicks 3-9, Conv >= 1, CVR >= 20%) ---")
        long_tail = sorted(
            [t for t in emp_terms.items() if 3 <= t[1]["clicks"] < 10 and t[1]["conversions"] >= 1 and t[1]["cvr"] >= 20.0],
            key=lambda x: (x[1]["cvr"], x[1]["conversions"]),
            reverse=True
        )
        for term, d in long_tail[:20]:
            cov_status, cov_kw = check_coverage(term, current_kws[country])
            print(f"'{term}' | Clk: {d['clicks']:.0f} | Conv: {d['conversions']:.1f} | CVR: {d['cvr']:.1f}% | CPA: ${d['cpa']:.2f} | Coverage: {cov_status} ({cov_kw})")

        # 5. Check what converting terms are NOT covered by current keywords
        print(f"\n--- {country} Converting Terms NOT covered by Current Keywords (Conv >= 1) ---")
        uncovered = [
            (term, d, check_coverage(term, current_kws[country]))
            for term, d in emp_terms.items()
            if d["conversions"] >= 1
        ]
        missing_terms = [x for x in uncovered if "Missing" in x[2][0]]
        print(f"Total converting employer terms: {len([t for t in emp_terms.values() if t['conversions'] >= 1])}")
        print(f"Missing terms count: {len(missing_terms)}")
        for term, d, (cov_status, cov_kw) in sorted(missing_terms, key=lambda x: x[1]["conversions"], reverse=True)[:25]:
            print(f"  MISSING: '{term}' | Clk: {d['clicks']:.0f} | Conv: {d['conversions']:.1f} | CVR: {d['cvr']:.1f}% | CPA: ${d['cpa']:.2f} | Cost: ${d['cost']:.2f}")

        # 6. Historical Mirages (Job seekers / Platforms that had conversions)
        print(f"\n--- {country} Historical Mirages (Job Seeker / Platform terms with conversions) ---")
        mirages = sorted(
            [t for t in (list(js_terms.items()) + list(comp_terms.items())) if t[1]["conversions"] >= 1],
            key=lambda x: x[1]["conversions"],
            reverse=True
        )
        for term, d in mirages[:15]:
            print(f"  MIRAGE ({d['intent']}): '{term}' | Clk: {d['clicks']:.0f} | Conv: {d['conversions']:.1f} | Cost: ${d['cost']:.2f} | CPA: ${d['cpa']:.2f}")

if __name__ == "__main__":
    run_deep_analysis()
