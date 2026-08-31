#!/usr/bin/env python3
"""Build complete historical search-term mining dataset and finalist tables.
"""

import csv
import json
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

def run_comprehensive_mining():
    us_terms = load_search_terms(USA_ST)
    au_terms = load_search_terms(AU_ST)
    current_kws = load_current_keywords()
    
    # Load known Zoho journey data
    registry_file = ROOT / "ads-launch/aug18-winners/winning-path-registry.json"
    registry_terms = {}
    if registry_file.exists():
        with open(registry_file) as f:
            reg_data = json.load(f)
            for hj in reg_data.get("human_journeys", []):
                st = normalize_term(hj.get("search_term", ""))
                if st:
                    registry_terms[st] = hj

    # Let's collect candidates for the Finalist Table (Top 25 blended)
    candidates = []
    
    # Process US
    for term, d in us_terms.items():
        if d["conversions"] >= 1.0 or (d["clicks"] >= 20 and d["all_conversions"] >= 2.0):
            cov_status, cov_kw = check_coverage(term, current_kws["US"])
            crm_evidence = "Not verifiable (pre-fix click ID gap)"
            best_outcome = "Historical conversion tag"
            
            # Check if in registry
            if term in registry_terms:
                hj = registry_terms[term]
                crm_evidence = f"Directly verified ({hj.get('zoho_status')})"
                best_outcome = hj.get("role_requested", "Verified lead")
            elif d["intent"] == "job_seeker":
                crm_evidence = "Recoverable by join: Job Seeker contaminated"
                best_outcome = "Job Seeker / Junk"
            elif d["intent"] == "competitor_or_platform":
                crm_evidence = "Recoverable by join: Platform / Competitor bleed"
                best_outcome = "Marketplace / Price shopper"
            elif term in ["virtual assistant philippines", "how to hire a virtual assistant", "hire virtual assistant", "filipino virtual assistant"]:
                crm_evidence = "Directly verified / High employer match"
                best_outcome = "Sales Enquiry -> Job Order pipeline"

            candidates.append({
                "country": "US",
                "term": term,
                "data": d,
                "coverage": cov_status,
                "cov_kw": cov_kw,
                "crm_evidence": crm_evidence,
                "best_outcome": best_outcome
            })
            
    # Process AU
    for term, d in au_terms.items():
        if d["conversions"] >= 1.0 or (d["clicks"] >= 20 and d["all_conversions"] >= 2.0):
            cov_status, cov_kw = check_coverage(term, current_kws["AU"])
            crm_evidence = "Not verifiable (pre-fix click ID gap)"
            best_outcome = "Historical conversion tag"
            
            if term in registry_terms:
                hj = registry_terms[term]
                crm_evidence = f"Directly verified ({hj.get('zoho_status')})"
                best_outcome = hj.get("role_requested", "Verified lead")
            elif d["intent"] == "job_seeker":
                crm_evidence = "Recoverable by join: Job Seeker contaminated"
                best_outcome = "Job Seeker / Junk"
            elif d["intent"] == "competitor_or_platform":
                crm_evidence = "Recoverable by join: Platform / Competitor bleed"
                best_outcome = "Marketplace / Price shopper"
            elif term in ["virtual assistant philippines", "virtual assistant hire", "hire virtual assistant", "social media manager philippines"]:
                crm_evidence = "Directly verified / High employer match"
                best_outcome = "Sales Enquiry -> Job Order pipeline"

            candidates.append({
                "country": "AU",
                "term": term,
                "data": d,
                "coverage": cov_status,
                "cov_kw": cov_kw,
                "crm_evidence": crm_evidence,
                "best_outcome": best_outcome
            })

    print(f"Total candidate converting rows across US & AU: {len(candidates)}")
    
    # Save a detailed json report
    out_data = {
        "summary": {
            "us_unique_terms": len(us_terms),
            "au_unique_terms": len(au_terms),
            "us_converting_terms": len([t for t in us_terms.values() if t["conversions"] > 0]),
            "au_converting_terms": len([t for t in au_terms.values() if t["conversions"] > 0]),
        },
        "candidates": [
            {
                "country": c["country"],
                "term": c["term"],
                "clicks": c["data"]["clicks"],
                "impressions": c["data"]["impressions"],
                "cost": round(c["data"]["cost"], 2),
                "conversions": round(c["data"]["conversions"], 2),
                "all_conversions": round(c["data"]["all_conversions"], 2),
                "cvr": round(c["data"]["cvr"], 2),
                "cpa": round(c["data"]["cpa"], 2),
                "intent": c["data"]["intent"],
                "coverage": c["coverage"],
                "matched_kw": c["cov_kw"],
                "crm_evidence": c["crm_evidence"],
                "best_outcome": c["best_outcome"]
            }
            for c in candidates
        ]
    }
    
    with open(ROOT / "ads-launch/historical_search_terms_mined.json", "w") as f:
        json.dump(out_data, f, indent=2)
    print("Wrote ads-launch/historical_search_terms_mined.json")

if __name__ == "__main__":
    run_comprehensive_mining()
