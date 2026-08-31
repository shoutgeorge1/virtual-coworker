#!/usr/bin/env python3
"""Focused historical search-term mining pass for Virtual Coworker US and AU.

Analyzes raw Google Ads Editor search-term history (~2024-08-01 to 2026-08-04)
Cross-references with:
1. Current keyword inventory across US & AU accounts
2. Zoho forensic evidence & lead-to-placement pipeline records

Produces:
- Phase 1: Filtered & ranked historical search-term winners (CVR, CPA, Volume, Long-tail)
- Phase 2: Zoho quality validation (Verified employer / Junk / Job Seeker / JO / Placement)
- Phase 3: Coverage gap analysis vs current accounts
- Phase 4: Final executive assessment & finalist comparison table
"""

from __future__ import annotations

import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
PERF = ROOT / "audit-data" / "performance"
USA_ST = PERF / "search_terms_usa_4967151855_2026-08-05.csv"
AU_ST = PERF / "search_terms_au_5735391940_2026-08-05.csv"


def num(val: Any) -> float:
    if val is None:
        return 0.0
    s = str(val).strip().replace(",", "").replace("%", "").replace("$", "").replace("A$", "").replace("AU$", "")
    if s in ("", "--", " —", "—", "-"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def normalize_term(term: str) -> str:
    t = term.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def classify_intent(term: str) -> str:
    t = normalize_term(term)
    
    # 1. Brand terms
    if any(b in t for b in ["virtual coworker", "virtualcoworker", "virtual co worker", "vc virtual", "virtualco worker"]):
        return "brand"
        
    # 2. Job seeker / Employment / Freelancer looking for work
    job_seeker_patterns = [
        r"\bjob\b", r"\bjobs\b", r"\bsalary\b", r"\bsalaries\b", r"\bcareer\b", r"\bcareers\b",
        r"\bresume\b", r"\bapply\b", r"\bapplicant\b", r"\bhiring me\b", r"\blooking for work\b",
        r"\bi need a job\b", r"\bwork from home\b", r"\bwfh\b", r"\bhome based\b", r"\bhomebased\b",
        r"\bemployee\b", r"\bemployees\b", r"\bglassdoor\b", r"\bindeed\b", r"\binterview questions\b",
        r"\bpart time job\b", r"\bonline job\b", r"\bonline jobs\b", r"\bportal\b", r"\blogin\b",
        r"\bpayroll\b", r"\btraining\b", r"\bcourse\b", r"\bhow to become\b", r"\bhow to be a\b",
        r"\bjoin\b", r"\bemployment\b", r"\bvpn\b", r"\btimesheet\b"
    ]
    for pat in job_seeker_patterns:
        if re.search(pat, t):
            return "job_seeker"
            
    # 3. Competitors & Platforms
    competitor_patterns = [
        "upwork", "fiverr", "freelancer.com", "onlinejobs.ph", "online jobs ph", "bruntwork",
        "myoutdesk", "hellorache", "wing assistant", "belay", "time etc", "woodbows",
        "athena", "boldly", "magic", "double", "delegated", "fancy hands", "zirtual",
        "shequra", "remote cowoker", "taskbullet", "priority va"
    ]
    for comp in competitor_patterns:
        if comp in t:
            return "competitor_or_platform"
            
    # 4. Low intent / generic research / junk / irrelevant / wrong geo
    junk_patterns = [
        "free virtual assistant", "free va", "what is a virtual assistant", "what does a virtual assistant do",
        "asistente virtual", "asistente", "en español", "mexico", "colombia", "argentina", "brazil",
        "ai virtual assistant", "google virtual assistant", "alexa", "siri", "bixby",
        "virtual assistant app", "software", "virtual medical assistant", "medical billing",
        "dental virtual assistant", "chiropractic", "nursing", "hipaa", "doctor",
        "amazon alexa", "top 10", "reddit", "youtube"
    ]
    for junk in junk_patterns:
        if junk in t:
            return "junk_or_irrelevant"
            
    # 5. Core Employer Intent
    # Hiring / staffing / outsourcing / VA roles / business support
    return "employer_intent"


def load_search_terms(path: Path) -> Dict[str, Dict[str, Any]]:
    raw = path.read_bytes().decode("utf-16")
    lines = [l for l in raw.splitlines() if l.strip()]
    reader = csv.DictReader(lines, delimiter="\t")
    
    terms: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "impressions": 0.0,
        "clicks": 0.0,
        "cost": 0.0,
        "conversions": 0.0,
        "all_conversions": 0.0,
        "campaigns": set(),
        "adgroups": set(),
        "keywords": set(),
        "sources": set(),
    })
    
    seen_metric_tuples = set()
    
    for row in reader:
        term = normalize_term(row.get("Search term", ""))
        if not term:
            continue
        imp = num(row.get("Impressions", row.get("Impr.")))
        clk = num(row.get("Clicks"))
        cost = num(row.get("Cost"))
        conv = num(row.get("Conversions"))
        all_conv = num(row.get("All conv", row.get("All conversions")))
        camp = row.get("Campaign", "").strip()
        ag = row.get("Ad Group", "").strip()
        kw = row.get("Keyword", "").strip()
        src = row.get("Source", "").strip()
        
        # Dedupe identical rows
        dedupe_key = (term, camp, ag, kw, round(imp, 2), round(clk, 2), round(cost, 2), round(conv, 2), round(all_conv, 2))
        if dedupe_key in seen_metric_tuples:
            continue
        seen_metric_tuples.add(dedupe_key)
        
        tdata = terms[term]
        tdata["impressions"] += imp
        tdata["clicks"] += clk
        tdata["cost"] += cost
        tdata["conversions"] += conv
        tdata["all_conversions"] += all_conv
        if camp:
            tdata["campaigns"].add(camp)
        if ag:
            tdata["adgroups"].add(ag)
        if kw:
            tdata["keywords"].add(kw)
        if src:
            tdata["sources"].add(src)
            
    # Calculate computed rates
    for term, d in terms.items():
        clk = d["clicks"]
        imp = d["impressions"]
        cost = d["cost"]
        conv = d["conversions"]
        d["ctr"] = (clk / imp * 100.0) if imp > 0 else 0.0
        d["cvr"] = (conv / clk * 100.0) if clk > 0 else 0.0
        d["cpa"] = (cost / conv) if conv > 0 else 0.0
        d["all_cvr"] = (d["all_conversions"] / clk * 100.0) if clk > 0 else 0.0
        d["all_cpa"] = (cost / d["all_conversions"]) if d["all_conversions"] > 0 else 0.0
        d["intent"] = classify_intent(term)
        
    return terms


def load_current_keywords() -> Dict[str, Dict[str, Set[str]]]:
    current_kws: Dict[str, Dict[str, Set[str]]] = {
        "US": {"exact": set(), "phrase": set(), "broad": set()},
        "AU": {"exact": set(), "phrase": set(), "broad": set()}
    }
    
    files = [
        ("US", ROOT / "ads-launch/google-ads-editor-import-us.csv"),
        ("AU", ROOT / "ads-launch/google-ads-editor-import-au.csv"),
        ("US", ROOT / "ads-launch/us-role-expansion-2026-08-21/google-ads-editor-import-us-role-expansion.csv"),
        ("US", ROOT / "ads-launch/real-estate-2026-08-18/01-adgroups-keywords-rsas-us.csv"),
        ("US", ROOT / "ads-launch/competitor-2026-08-19/google-ads-editor-import-us.csv"),
        ("AU", ROOT / "ads-launch/competitor-2026-08-19/google-ads-editor-import-au.csv"),
        ("US", ROOT / "ads-launch/google-ads-editor-agency-intent-keywords-add.csv"),
        ("AU", ROOT / "ads-launch/aug18-winners/03-au-smm-exact-enable.csv"),
    ]
    
    for country, fpath in files:
        if not fpath.exists():
            continue
        with open(fpath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                kw = row.get("Keyword", "").strip().lower()
                mtype = row.get("Criterion Type", row.get("Match type", "")).strip().lower()
                status = row.get("Status", "").strip().lower()
                if kw and status != "paused":
                    clean = kw.strip("[]\"")
                    clean = normalize_term(clean)
                    if "exact" in mtype or (kw.startswith("[") and kw.endswith("]")):
                        current_kws[country]["exact"].add(clean)
                    elif "phrase" in mtype or (kw.startswith("\"") and kw.endswith("\"")):
                        current_kws[country]["phrase"].add(clean)
                    elif "broad" in mtype or mtype == "":
                        current_kws[country]["broad"].add(clean)
                        
    return current_kws


def check_coverage(term: str, country_kws: Dict[str, Set[str]]) -> Tuple[str, str]:
    t = normalize_term(term)
    
    # 1. Exact match check
    if t in country_kws["exact"]:
        return "Already directly covered by current exact match", f"Exact: [{t}]"
        
    # Check normalized close-variants (plurals, minor words)
    t_singular = re.sub(r"\bassistants\b", "assistant", t)
    t_singular = re.sub(r"\bva's\b|\bvas\b", "va", t_singular)
    t_singular = re.sub(r"\bbookkeepers\b", "bookkeeper", t_singular)
    t_singular = re.sub(r"\bmanagers\b", "manager", t_singular)
    if t_singular in country_kws["exact"]:
        return "Already directly covered by current exact match", f"Exact variant: [{t_singular}]"
        
    # 2. Phrase match check (does any phrase keyword match the search term)
    matched_phrases = []
    for pkw in country_kws["phrase"]:
        # Phrase match requires whole words in order
        pattern = r"\b" + re.escape(pkw) + r"\b"
        if re.search(pattern, t):
            matched_phrases.append(pkw)
            
    if matched_phrases:
        # Pick the longest / most specific matching phrase
        best_phrase = max(matched_phrases, key=len)
        return "Already substantially covered by current phrase match", f"Phrase: \"{best_phrase}\""
        
    # Check if phrase keyword matches singular version
    for pkw in country_kws["phrase"]:
        pkw_sing = re.sub(r"\bassistants\b", "assistant", pkw)
        pattern = r"\b" + re.escape(pkw_sing) + r"\b"
        if re.search(pattern, t_singular):
            return "Already substantially covered by current phrase match", f"Phrase variant: \"{pkw}\""
            
    # Check broad
    for bkw in country_kws["broad"]:
        if bkw in t:
            return "Probably covered, but worth watching as a search term", f"Broad: +{bkw}"
            
    return "Missing / potential keyword opportunity", "None"


def main():
    print("Loading historical search terms...")
    us_terms = load_search_terms(USA_ST)
    au_terms = load_search_terms(AU_ST)
    
    print("Loading current active keyword inventory...")
    current_kws = load_current_keywords()
    
    print("\n--- Summary Stats ---")
    print(f"US: {len(us_terms)} unique search terms")
    print(f"AU: {len(au_terms)} unique search terms")
    
    for cname, terms in [("US", us_terms), ("AU", au_terms)]:
        intent_counts = Counter(d["intent"] for d in terms.values())
        print(f"\n{cname} Intent Distribution (all terms):")
        for k, v in intent_counts.most_common():
            print(f"  {k}: {v} terms ({v/len(terms)*100:.1f}%)")
            
        conv_terms = [t for t in terms.values() if t["conversions"] > 0]
        conv_intent = Counter(d["intent"] for d in conv_terms)
        print(f"{cname} Converting Terms Intent Distribution ({len(conv_terms)} converting terms):")
        for k, v in conv_intent.most_common():
            print(f"  {k}: {v} terms ({v/len(conv_terms)*100:.1f}%)")


if __name__ == "__main__":
    from collections import Counter
    main()
