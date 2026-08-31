#!/usr/bin/env python3
"""Build paused Google Ads Editor package: VC_US_S_COMP / VC_AU_S_COMP.

Checklist item 5. Exact competitor names people already typed. All Paused.
No Ads API. Does not touch CORE/ROLES. Does not revive LK/PM competitor campaigns.
Competitor names stay a shopping list — not Core/Roles negatives.

Usage:
  python3 ads-launch/competitor-2026-08-19/build_competitor_editor_package.py
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ADS = ROOT / "ads-launch"
XRAY = ROOT / "xray"

US_ACCOUNT = "496-715-1855"
AU_ACCOUNT = "573-539-1940"
HOST = "www.virtualcoworker.app"
LABEL = "VC_COMP_2026-08-19"
LP_VERSION = "stage1-v7"

SUFFIX_BASE = (
    "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"
    "&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}"
    "&utm_device={device}"
)
SUFFIX_US = SUFFIX_BASE
SUFFIX_AU = f"{SUFFIX_BASE}&lp_version={LP_VERSION}"
TRACK = "{lpurl}"

ST_FILES = [
    ADS / "_last7_search_terms.json",
    ADS / "_today_search_terms.json",
    ADS / "_tmp_search_terms_2026-08-08-to-14.json",
    ADS / "_evidence_search_terms.json",
    ADS / "_rsa_challenger_review.json",
]

FIELDS = [
    "Account",
    "Row Type",
    "Campaign",
    "Campaign Type",
    "Campaign Status",
    "Budget",
    "Budget type",
    "Bid Strategy Type",
    "Networks",
    "Languages",
    "Location",
    "Location options",
    "Tracking template",
    "Final URL suffix",
    "Ad Group",
    "Ad Group Status",
    "Maximum CPC bid limit",
    "Keyword",
    "Criterion Type",
    "Keyword Status",
    "Ad Status",
    "Ad type",
    "Final URL",
    "Path 1",
    "Path 2",
    "Headline 1",
    "Headline 2",
    "Headline 3",
    "Headline 4",
    "Headline 5",
    "Headline 6",
    "Headline 7",
    "Headline 8",
    "Headline 9",
    "Headline 10",
    "Headline 11",
    "Headline 12",
    "Headline 13",
    "Headline 14",
    "Headline 15",
    "Description 1",
    "Description 2",
    "Description 3",
    "Description 4",
    "Link Text",
    "Description Line 1",
    "Description Line 2",
    "Callout text",
    "Header",
    "Snippet Values",
    "Negative",
    "Comment",
]

NEG_MMC_FIELDS = [
    "Account",
    "Campaign",
    "Keyword",
    "Match type",
    "Comment",
]

JOB_SEEKER_PHRASE = (
    "job",
    "jobs",
    "career",
    "careers",
    "salary",
    "apply",
    "indeed",
    "onlinejobs",
)

# Brand keys people typed. A name must also appear in ST to become a keyword.
# bid_exact: Exact strings we will bid, keyed by market. Variants only if in ST.
BRANDS: list[dict] = [
    {
        "key": "24x7_direct",
        "label": "24x7 Direct",
        "ag": "Comp_24x7_Direct",
        "bid_exact": {
            "AU": ["24x7 direct", "24x7direct", "24 x 7 direct", "24 7 direct"],
        },
    },
    {
        "key": "outsourcing_angel",
        "label": "Outsourcing Angel",
        "ag": "Comp_Outsourcing_Angel",
        "bid_exact": {
            "AU": ["outsourcing angel", "outsourcing angel va"],
        },
    },
    {
        "key": "staffhouse",
        "label": "Staffhouse",
        "ag": "Comp_Staffhouse",
        "bid_exact": {"AU": ["staffhouse philippines"]},
    },
    {
        "key": "my_virtue_desk",
        "label": "My Virtue Desk",
        "ag": "Comp_My_Virtue_Desk",
        "bid_exact": {"AU": ["my virtue desk"]},
    },
    {
        "key": "coconut_va",
        "label": "Coconut VA",
        "ag": "Comp_Coconut_VA",
        "bid_exact": {"AU": ["coconut va"]},
    },
    {
        "key": "apello",
        "label": "Apello",
        "ag": "Comp_Apello",
        "bid_exact": {"AU": ["apello call centers"]},
    },
    {
        "key": "virtualstaff",
        "label": "VirtualStaff",
        "ag": "Comp_VirtualStaff",
        "bid_exact": {"US": ["virtualstaff", "virtualstaff ph"]},
    },
    {
        "key": "rippling",
        "label": "Rippling",
        "ag": "Comp_Rippling",
        "bid_exact": {
            "US": ["rippling philippines", "rippling philippines inc"],
        },
    },
    {
        "key": "iploy",
        "label": "iPloy",
        "ag": "Comp_iPloy",
        "bid_exact": {"US": ["iploy cebu"]},
    },
    {
        "key": "wing",
        "label": "Wing",
        "ag": "Comp_Wing",
        "bid_exact": {"US": ["wing assistant"]},
    },
    {
        "key": "myoutdesk",
        "label": "MyOutDesk",
        "ag": "Comp_MyOutDesk",
        "bid_exact": {
            "US": ["my outdesk va"],
            "AU": ["outdesk australia"],
        },
    },
    {
        "key": "belay",
        "label": "Belay",
        "ag": "Comp_Belay",
        "bid_exact": {"AU": ["belay va"]},
    },
]

# Hint-only names from rsa_challengers.py — never bid unless ST also has them.
RSA_CHALLENGER_HINTS = (
    "myoutdesk",
    "cherry assistant",
    "wing",
    "magic",
    "belay",
    "24x7 direct",
    "outsourcing angel",
    "staffhouse",
)

PARK_REASONS = {
    "24x7direct com au": "navigational / domain — parked",
    "outsourcing angel hiring": "job-seeker contaminated — parked",
    "virtualstaff365 review": "different product + review query — parked",
    "coconut va": "US hit is 1 impression; bid AU only",
    "24 7 virtual assistant": "generic 24/7 VA, not the 24x7 Direct brand — parked",
    "offshore 24 7": "generic hours language, not the brand — parked",
    "wow24 7": "unclear / different brand — parked",
    "pineappleva": "thin / not on the named chip list — parked",
    "pineapple va": "thin / not on the named chip list — parked",
    "pineapple virtual assistants": "thin / not on the named chip list — parked",
    "magic va": "thin / not on the named chip list — parked",
    "magic assistant": "thin / not on the named chip list — parked",
    "magic ph": "unclear — parked",
    "magic virtual assistant pricing": "pricing research — parked",
    "get magic virtual assistant": "thin / not on the named chip list — parked",
    "cherry assistant": "thin / not on the named chip list — parked",
    "eclaro philippines": "unclear PH recruiter — parked",
    "new horizons global partners philippines inc": "unclear PH recruiter — parked",
    "wise recruitment agency philippines": "unclear PH recruiter — parked",
    "agentsync australia": "unclear / thin — parked",
    "awesome cx davao": "unclear BPO — parked",
    "gobro ph outsourcing inc": "unclear BPO — parked",
    "convergys call center": "enterprise BPO, not a VA shop — parked",
    "resultscx call center": "enterprise BPO — parked",
    "resultscx company": "enterprise BPO — parked",
    "crewbloom recruitment": "thin / unclear — parked",
    "outsta recruitment": "thin / unclear — parked",
    "we work remotely": "job board — parked",
    "onlinejobs": "job board — also a COMP campaign negative",
    "onlinejobs ph": "job board — parked",
    "onlinejobs ph pricing": "job board — parked",
    "remote talent au": "job board / marketplace — parked",
    "remote talent australia": "job board / marketplace — parked",
    "remote talent com au": "job board / marketplace — parked",
    "remote talent agency": "generic / unclear — parked",
    "remote talent cloud": "generic / unclear — parked",
    "wingman recruitment": "different brand — parked",
}

# Extra patterns to catch brand-ish terms for the shopping list (not auto-bid).
WATCH_PATTERNS = (
    r"24\s*x?\s*7",
    r"outsourcing angel",
    r"staffhouse",
    r"virtue desk",
    r"coconut\s*va",
    r"\bapello\b",
    r"virtualstaff",
    r"virtual staff",
    r"\brippling\b",
    r"\biploy\b",
    r"\bbelay\b",
    r"outdesk",
    r"wing assistant",
    r"cherry assistant",
    r"\bmagic va\b",
    r"magic assistant",
    r"get magic",
    r"pineappleva",
    r"pineapple va",
    r"pineapple virtual",
    r"\beclaro\b",
    r"new horizons",
    r"wise recruitment",
    r"agentsync",
    r"awesome cx",
    r"\bgobro\b",
    r"we work remotely",
    r"onlinejobs",
    r"remote talent",
    r"convergys",
    r"resultscx",
    r"crewbloom",
    r"\boutsta\b",
    r"wow24",
)

FORBIDDEN_AD_NAMES = (
    "24x7",
    "24 x 7",
    "outsourcing angel",
    "staffhouse",
    "virtue desk",
    "coconut",
    "apello",
    "virtualstaff",
    "rippling",
    "iploy",
    "belay",
    "outdesk",
    "myoutdesk",
    "wing",
    "magic",
    "pineapple",
    "cherry",
    "eclaro",
)

FORBIDDEN_CHARS = (
    "\u2014",
    "\u2013",
    "\u2026",
    "...",
    "\u2018",
    "\u2019",
    "\u201c",
    "\u201d",
    "\u00a0",
)

RSA = {
    "US": (
        [
            "You Interview the Shortlist",
            "Dedicated Staff, Not a Bench",
            "Employers Only Since 2011",
            "Work Your US Hours",
            "Not a Freelance Marketplace",
            "Book a Hiring Consultation",
            "Hire a Virtual Assistant",
            "We Recruit. You Interview.",
            "Dedicated Remote Staff",
            "You Choose Who Joins",
            "Filipino Staff for Business",
            "Hire Dedicated Remote Staff",
            "Staff Who Work US Hours",
            "Not a Rotating Bench",
            "Vetted Hiring Shortlist",
        ],
        [
            "You interview the shortlist. Dedicated teammate, not a rotating bench.",
            "Hire a Virtual Assistant who works your US hours. Not a freelance marketplace.",
            "Employers only since 2011. We recruit and vet. You interview and choose.",
            "Book a hiring consultation. Dedicated remote staff, not a rotating bench.",
        ],
    ),
    "AU": (
        [
            "You Interview the Shortlist",
            "Dedicated Staff, Not a Bench",
            "Employers Only Since 2011",
            "Work Australian Hours",
            "Not a Freelance Marketplace",
            "Book a Hiring Consultation",
            "Hire a VA for Your Team",
            "We Recruit. You Interview.",
            "Dedicated Remote Staff",
            "You Choose Who Joins",
            "Filipino VA for Business",
            "Hire Dedicated Remote Staff",
            "Staff on Australian Hours",
            "Not a Rotating Bench",
            "Vetted Hiring Shortlist",
        ],
        [
            "You interview the shortlist. Dedicated teammate, not a rotating bench.",
            "Hire a VA who works Australian hours. Not a freelance marketplace.",
            "Employers only since 2011. We recruit and vet. You interview and choose.",
            "Book a hiring consultation. Dedicated remote staff, not a rotating bench.",
        ],
    ),
}

SERP = {
    "US": [
        (
            "You Interview the Shortlist · Dedicated Staff, Not a Bench · Book a Hiring Consultation",
            "You interview the shortlist. Dedicated teammate, not a rotating bench.",
        ),
        (
            "Hire a Virtual Assistant · Work Your US Hours · Not a Freelance Marketplace",
            "Hire a Virtual Assistant who works your US hours. Not a freelance marketplace.",
        ),
        (
            "Employers Only Since 2011 · We Recruit. You Interview. · Not a Rotating Bench",
            "Employers only since 2011. We recruit and vet. You interview and choose.",
        ),
    ],
    "AU": [
        (
            "You Interview the Shortlist · Dedicated Staff, Not a Bench · Book a Hiring Consultation",
            "You interview the shortlist. Dedicated teammate, not a rotating bench.",
        ),
        (
            "Hire a VA for Your Team · Work Australian Hours · Not a Freelance Marketplace",
            "Hire a VA who works Australian hours. Not a freelance marketplace.",
        ),
        (
            "Employers Only Since 2011 · We Recruit. You Interview. · Not a Rotating Bench",
            "Employers only since 2011. We recruit and vet. You interview and choose.",
        ),
    ],
}


def blank_row() -> dict[str, str]:
    return {h: "" for h in FIELDS}


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


def classify_brand(term: str) -> str | None:
    t = term.lower().strip()
    c = compact(t)
    if "outsourcing angel" in t:
        return "outsourcing_angel"
    if "staffhouse" in t:
        return "staffhouse"
    if "virtue desk" in t:
        return "my_virtue_desk"
    if "coconut va" in t or c == "coconutva":
        return "coconut_va"
    if "apello" in t:
        return "apello"
    if re.search(r"\bvirtualstaff\b", t) and "365" not in t:
        return "virtualstaff"
    if "rippling" in t:
        return "rippling"
    if "iploy" in t:
        return "iploy"
    if t == "wing assistant" or t.startswith("wing assistant "):
        return "wing"
    if "outdesk" in t:
        return "myoutdesk"
    if re.search(r"\bbelay\b", t):
        return "belay"
    if ("direct" in t) and (
        "24x7" in c or re.search(r"24\s*x\s*7", t) or re.search(r"\b24\s+7\b", t)
    ):
        if "virtual assistant" in t:
            return None
        return "24x7_direct"
    return None


def is_watch_term(term: str) -> bool:
    t = term.lower()
    return any(re.search(p, t) for p in WATCH_PATTERNS)


def walk_terms(obj, bag: list[dict], ctx: dict) -> None:
    if isinstance(obj, dict):
        nctx = dict(ctx)
        if obj.get("customer_id"):
            nctx["customer_id"] = str(obj["customer_id"])
        if obj.get("market") in ("US", "AU"):
            nctx["market"] = obj["market"]
        st = obj.get("search_term") or obj.get("term")
        if isinstance(st, str) and st.strip():
            market = None
            camp = str(obj.get("campaign") or obj.get("campaign_name") or "")
            if "_US_" in camp or camp.startswith("VC_US"):
                market = "US"
            elif "_AU_" in camp or camp.startswith("VC_AU"):
                market = "AU"
            cid = str(nctx.get("customer_id") or "").replace("-", "")
            if not market:
                if cid == "4967151855":
                    market = "US"
                elif cid == "5735391940":
                    market = "AU"
            if not market:
                market = nctx.get("market")
            usa = obj.get("usa_cost")
            au = obj.get("au_cost")
            if not market and usa is not None and au is not None:
                try:
                    market = "US" if float(usa or 0) >= float(au or 0) else "AU"
                except (TypeError, ValueError):
                    market = None
            bag.append(
                {
                    "term": st.strip(),
                    "market": market or "?",
                    "file": ctx["file"],
                    "clicks": float(obj.get("clicks") or 0),
                    "impressions": float(
                        obj.get("impressions") or obj.get("impr") or 0
                    ),
                    "campaign": camp,
                }
            )
        for key, val in obj.items():
            if key in ("US", "AU") and isinstance(val, dict):
                child = dict(nctx)
                child["market"] = key
                walk_terms(val, bag, child)
            else:
                walk_terms(val, bag, nctx)
    elif isinstance(obj, list):
        for item in obj:
            walk_terms(item, bag, ctx)


def load_search_terms() -> list[dict]:
    rows: list[dict] = []
    for path in ST_FILES:
        data = json.loads(path.read_text(encoding="utf-8"))
        walk_terms(data, rows, {"file": path.name})
    return rows


def validate_rsa(headlines: list[str], descs: list[str], where: str) -> None:
    if len(headlines) != 15:
        raise SystemExit(f"{where}: need 15 headlines, got {len(headlines)}")
    if len(descs) != 4:
        raise SystemExit(f"{where}: need 4 descriptions, got {len(descs)}")
    if len(set(headlines)) != 15:
        raise SystemExit(f"{where}: duplicate headlines")
    if len(set(descs)) != 4:
        raise SystemExit(f"{where}: duplicate descriptions")
    blob = " ".join(headlines + descs)
    low = blob.lower()
    if "{keyword:" in low:
        raise SystemExit(f"{where}: DKI forbidden on competitor RSAs (trademark)")
    for name in FORBIDDEN_AD_NAMES:
        if name in low:
            raise SystemExit(f"{where}: competitor name in ad copy: {name!r}")
    for ch in FORBIDDEN_CHARS:
        if ch in blob:
            raise SystemExit(f"{where}: forbidden character {ch!r}")
    if blob.count("!") > 1 or blob.count("?") > 1:
        raise SystemExit(f"{where}: too many ! or ?")
    if "!" in blob and "?" in blob:
        raise SystemExit(f"{where}: ! and ? in the same ad")
    for h in headlines:
        if not (1 <= len(h) <= 30):
            raise SystemExit(f"{where}: headline len {len(h)}: {h}")
    for d in descs:
        if not (1 <= len(d) <= 90):
            raise SystemExit(f"{where}: description len {len(d)}: {d}")


def account_for(mkt: str) -> str:
    return US_ACCOUNT if mkt == "US" else AU_ACCOUNT


def campaign_name(mkt: str) -> str:
    return f"VC_{mkt}_S_COMP"


def suffix_for(mkt: str) -> str:
    return SUFFIX_US if mkt == "US" else SUFFIX_AU


def campaign_row(mkt: str) -> dict[str, str]:
    r = blank_row()
    loc = "United States" if mkt == "US" else "Australia"
    budget = "25"
    cpc = "12" if mkt == "US" else "6"
    r.update(
        {
            "Account": account_for(mkt),
            "Row Type": "Campaign",
            "Campaign": campaign_name(mkt),
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget": budget,
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Languages": "en",
            "Location": loc,
            "Location options": "Presence",
            "Tracking template": TRACK,
            "Final URL suffix": suffix_for(mkt),
            "Maximum CPC bid limit": cpc,
            "Comment": (
                f"{LABEL} · new Paused competitor campaign · do not enable · "
                "do not revive LK/PM competitor campaigns"
            ),
        }
    )
    return r


def ag_row(mkt: str, ag: str, comment: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account_for(mkt),
            "Row Type": "Ad group",
            "Campaign": campaign_name(mkt),
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Ad Group": ag,
            "Ad Group Status": "Paused",
            "Comment": comment,
        }
    )
    return r


def kw_row(mkt: str, ag: str, keyword: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account_for(mkt),
            "Row Type": "Keyword",
            "Campaign": campaign_name(mkt),
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Ad Group": ag,
            "Keyword": keyword,
            "Criterion Type": "Exact",
            "Keyword Status": "Paused",
            "Comment": f"{LABEL} · Exact · typed in ST · {keyword}",
        }
    )
    return r


def rsa_row(mkt: str, ag: str) -> dict[str, str]:
    headlines, descs = RSA[mkt]
    r = blank_row()
    r.update(
        {
            "Account": account_for(mkt),
            "Row Type": "Ad",
            "Campaign": campaign_name(mkt),
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Ad Group": ag,
            "Ad Group Status": "Paused",
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": f"https://{HOST}/{mkt.lower()}",
            "Path 1": "hire",
            "Path 2": "staff",
            "Comment": (
                f"{LABEL} · RSA · no competitor names · no DKI · "
                f"Final URL=/{mkt.lower()}"
            ),
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    return r


def build_negatives(mkt: str) -> list[dict[str, str]]:
    rows = []
    for term in JOB_SEEKER_PHRASE:
        rows.append(
            {
                "Account": account_for(mkt),
                "Campaign": campaign_name(mkt),
                "Keyword": term,
                "Match type": "Phrase",
                "Comment": (
                    f"{LABEL} · COMP-only Phrase job-seeker junk · "
                    "MMC import only · not Core/Roles · not competitor names"
                ),
            }
        )
    return rows


def mine_inventory(st_rows: list[dict]) -> tuple[dict, list[dict]]:
    """Return bid map {(mkt, brand_key): [terms]} and shopping-list rows."""
    found: dict[tuple[str, str], dict] = {}
    for r in st_rows:
        term = r["term"].strip()
        low = term.lower()
        brand = classify_brand(term)
        watch = is_watch_term(term)
        if not brand and not watch:
            continue
        key = (r["market"], low)
        slot = found.setdefault(
            key,
            {
                "term": low,
                "display": term,
                "market": r["market"],
                "brand": brand,
                "files": set(),
                "clicks": 0.0,
                "impressions": 0.0,
            },
        )
        if brand:
            slot["brand"] = brand
        slot["files"].add(r["file"])
        slot["clicks"] += r["clicks"]
        slot["impressions"] += r["impressions"]

    bid_allow: dict[tuple[str, str], set[str]] = {}
    for brand in BRANDS:
        for mkt, kws in brand["bid_exact"].items():
            bid_allow[(mkt, brand["key"])] = {k.lower() for k in kws}

    seen_in_st: dict[tuple[str, str], set[str]] = defaultdict(set)
    shopping: list[dict] = []
    for slot in found.values():
        mkt = slot["market"]
        low = slot["term"]
        brand = slot["brand"]
        bid = False
        reason = ""
        if brand and mkt in ("US", "AU") and low in bid_allow.get((mkt, brand), set()):
            bid = True
            seen_in_st[(mkt, brand)].add(low)
            reason = "Exact keyword in COMP"
        else:
            reason = PARK_REASONS.get(low)
            if not reason:
                if "virtual staff" in low:
                    reason = "generic category, not the VirtualStaff brand — parked"
                elif brand and mkt in ("US", "AU"):
                    reason = "seen in ST — parked (variant / wrong market / thin)"
                elif mkt == "?":
                    reason = "seen in ST — market unclear — parked"
                else:
                    reason = "seen in ST — parked (too thin / job-board / unclear)"
        shopping.append(
            {
                "market": mkt,
                "term": low,
                "brand": brand or "",
                "bid": bid,
                "reason": reason,
                "files": sorted(slot["files"]),
                "clicks": slot["clicks"],
                "impressions": slot["impressions"],
            }
        )

    missing = []
    for brand in BRANDS:
        for mkt, kws in brand["bid_exact"].items():
            have = seen_in_st.get((mkt, brand["key"]), set())
            for kw in kws:
                if kw.lower() not in have:
                    missing.append(f"{mkt} {brand['label']}: {kw}")
    if missing:
        raise SystemExit(
            "Bid Exact strings missing from ST evidence:\n  " + "\n  ".join(missing)
        )

    shopping.sort(key=lambda x: (x["market"], not x["bid"], x["term"]))
    return seen_in_st, shopping


def build_package(seen_in_st: dict[tuple[str, str], set[str]]) -> dict[str, list]:
    validate_rsa(*RSA["US"], "US COMP RSA")
    validate_rsa(*RSA["AU"], "AU COMP RSA")

    out: dict[str, list] = {"US": [], "AU": []}
    for mkt in ("US", "AU"):
        rows = [campaign_row(mkt)]
        for brand in BRANDS:
            kws = sorted(seen_in_st.get((mkt, brand["key"]), set()))
            if not kws:
                continue
            rows.append(
                ag_row(
                    mkt,
                    brand["ag"],
                    f"{LABEL} · {brand['label']} · Exact only · Paused · "
                    f"Final URL=/{mkt.lower()}",
                )
            )
            for kw in kws:
                rows.append(kw_row(mkt, brand["ag"], kw))
            rows.append(rsa_row(mkt, brand["ag"]))
        out[mkt] = rows
    return out


def qa(rows_by_mkt: dict[str, list], negs_by_mkt: dict[str, list]) -> None:
    for mkt, rows in rows_by_mkt.items():
        camps = [r for r in rows if r["Row Type"] == "Campaign"]
        if len(camps) != 1:
            raise SystemExit(f"{mkt}: expected 1 campaign, got {len(camps)}")
        if camps[0]["Campaign"] != campaign_name(mkt):
            raise SystemExit(f"{mkt}: bad campaign name")
        if camps[0]["Campaign Status"] != "Paused":
            raise SystemExit(f"{mkt}: campaign not Paused")
        if any(
            (r.get("Criterion Type") or "").lower() == "campaign negative" for r in rows
        ):
            raise SystemExit(f"{mkt}: campaign negatives leaked into Account Import")
        for r in rows:
            for col in ("Campaign Status", "Ad Group Status", "Keyword Status", "Ad Status"):
                st = r.get(col) or ""
                if st and st != "Paused":
                    raise SystemExit(f"{mkt}: {col}={st} on {r['Row Type']}")
            if r["Row Type"] == "Keyword" and r["Criterion Type"] != "Exact":
                raise SystemExit(f"{mkt}: non-Exact positive {r['Keyword']}")
            if r["Row Type"] != "Campaign" and r.get("Maximum CPC bid limit"):
                raise SystemExit(f"{mkt}: CPC must live on campaign only")
            if r["Row Type"] == "Ad":
                blob = " ".join(r[f"Headline {i}"] for i in range(1, 16))
                blob += " " + " ".join(r[f"Description {i}"] for i in range(1, 5))
                if "{KeyWord:" in blob:
                    raise SystemExit("DKI in RSA")
                low = blob.lower()
                for name in FORBIDDEN_AD_NAMES:
                    if name in low:
                        raise SystemExit(f"competitor name in RSA: {name}")
        if len(negs_by_mkt[mkt]) != len(JOB_SEEKER_PHRASE):
            raise SystemExit(f"{mkt}: expected {len(JOB_SEEKER_PHRASE)} COMP negs")
        for n in negs_by_mkt[mkt]:
            if n["Match type"] != "Phrase":
                raise SystemExit("COMP negatives must be Phrase")
            if n["Campaign"] != campaign_name(mkt):
                raise SystemExit("neg campaign mismatch")


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="raise")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def write_shopping_list(path: Path, shopping: list[dict], seen_in_st: dict) -> None:
    lines = [
        "# Competitor shopping list — 19 Aug 2026",
        "",
        "Mined from local search-term dumps only. No Ads API.",
        "These names stay a shopping list. Do **not** add them as Core/Roles negatives.",
        "Do **not** revive old LK/PM competitor campaigns.",
        "",
        "Sources: `_last7_search_terms.json`, `_today_search_terms.json`,",
        "`_tmp_search_terms_2026-08-08-to-14.json`, `_evidence_search_terms.json`,",
        "`_rsa_challenger_review.json`, plus `rsa_challengers.py` COMPETITORS as a hint only.",
        "",
        "## Bid — Exact keywords in `VC_*_S_COMP` (Paused)",
        "",
    ]
    for mkt in ("US", "AU"):
        lines.append(f"### {mkt}")
        lines.append("")
        lines.append("| Brand | Ad group | Exact keyword |")
        lines.append("| --- | --- | --- |")
        for brand in BRANDS:
            kws = sorted(seen_in_st.get((mkt, brand["key"]), set()))
            for kw in kws:
                lines.append(f"| {brand['label']} | `{brand['ag']}` | `[{kw}]` |")
        lines.append("")

    lines += [
        "## Parked — seen in ST, not bid",
        "",
        "| Market | Term | Why |",
        "| --- | --- | --- |",
    ]
    parked = [s for s in shopping if not s["bid"]]
    for s in parked:
        lines.append(f"| {s['market']} | `{s['term']}` | {s['reason']} |")
    lines += [
        "",
        "## Hint names that did not become keywords",
        "",
        "`rsa_challengers.py` COMPETITORS is a hint only. A name must also appear in ST.",
        "Belay / MyOutDesk / Wing were **not invented** — they appear in ST, so they were bid.",
        "Cherry Assistant and Magic appear in ST but were parked (thin / not on the named chip list).",
        "",
        f"Hint list: {', '.join(RSA_CHALLENGER_HINTS)}.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def chips(kws: list[str]) -> str:
    return "".join(
        f'<span class="chip">[{html.escape(k)}]</span>' for k in kws
    )


def asset_list(items: list[str], limit: int) -> str:
    bits = []
    for text in items:
        n = len(text)
        cls = "ok" if n <= limit else "bad"
        bits.append(
            f"<li><span class='copy'>{html.escape(text)}</span> "
            f"<span class='len {cls}'>{n}</span></li>"
        )
    return "<ol class=\"assets\">" + "".join(bits) + "</ol>"


def serp_block(mkt: str) -> str:
    url = f"{HOST}/{mkt.lower()}"
    parts = []
    for title, desc in SERP[mkt]:
        parts.append(
            f"""
    <div class="serp">
      <p class="serp-label">Sponsored</p>
      <p class="serp-url">{html.escape(url)} <span>› hire › staff</span></p>
      <p class="serp-title">{html.escape(title)}</p>
      <p class="serp-desc">{html.escape(desc)}</p>
    </div>"""
        )
    return "".join(parts)


def write_xray(path: Path, seen_in_st: dict) -> None:
    toc = []
    articles = []
    for mkt in ("US", "AU"):
        headlines, descs = RSA[mkt]
        for brand in BRANDS:
            kws = sorted(seen_in_st.get((mkt, brand["key"]), set()))
            if not kws:
                continue
            slug = f"{mkt.lower()}-{brand['ag']}".replace("_", "-").lower()
            toc.append(f'<a href="#{slug}">{html.escape(brand["ag"])}</a>')
            hours = "US hours" if mkt == "US" else "Australian hours"
            articles.append(
                f"""
      <article class="ag" id="{slug}">
        <header>
          <p class="kicker">{html.escape(campaign_name(mkt))} · {mkt} · {html.escape(brand['label'])}</p>
          <h2>{html.escape(brand['ag'])}</h2>
          <p class="meta">Exact only. No Phrase. No Broad. · Paused · Max CPC {"$12" if mkt == "US" else "A$6"} · {hours}</p>
        </header>
        <p class="kicker">Keywords</p>
        <div class="chips">{chips(kws)}</div>
        <div class="rsa">
          <p class="kicker">RSA · no competitor names</p>
          <p class="tiny">Final URL <a href="https://{HOST}/{mkt.lower()}" target="_blank" rel="noopener">https://{HOST}/{mkt.lower()}</a> · paths <code>hire/staff</code></p>
          <p class="kicker">How it can look in Google</p>
          {serp_block(mkt)}
          <div class="cols">
            <div>
              <p class="kicker">15 headlines</p>
              {asset_list(headlines, 30)}
            </div>
            <div>
              <p class="kicker">4 descriptions</p>
              {asset_list(descs, 90)}
            </div>
          </div>
        </div>
      </article>"""
            )

    neg_chips = "".join(
        f'<span class="chip chip-neg">"{html.escape(t)}"</span>'
        for t in JOB_SEEKER_PHRASE
    )
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>Competitor ads · Virtual Coworker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    .banner {{ background:#1a1a1a; color:#fff; padding:1rem 1.2rem; border-radius:10px; border-left:6px solid #e8a317; margin:0 0 1.15rem; }}
    .banner strong {{ color:#ffd56a; }}
    .toc {{ display:flex; flex-wrap:wrap; gap:.5rem 1rem; margin:0 0 1rem; }}
    article.ag {{ background:#fff; border:1px solid var(--edge); border-radius:14px; padding:1.1rem 1.2rem 1.3rem; margin:0 0 1.2rem; }}
    article.ag h2 {{ margin:.1rem 0 .35rem; font-size:1.25rem; }}
    .meta, .tiny {{ color:var(--muted); }}
    .tiny {{ font-size:.78rem; }}
    .chips {{ display:flex; flex-wrap:wrap; gap:.35rem; margin:.2rem 0 .7rem; }}
    .chip {{ background:var(--tint-cool); border:1px solid var(--tint-cool-edge); font-size:.75rem; padding:.15rem .45rem; border-radius:4px; font-family:var(--mono); }}
    .chip-neg {{ background:var(--tint-rose); border-color:var(--tint-rose-edge); }}
    .rsa {{ background:var(--panel-inset); border:1px solid var(--edge-soft); border-radius:10px; padding:.85rem .95rem; }}
    .cols {{ display:grid; grid-template-columns:1fr 1fr; gap:.8rem; }}
    @media (max-width:700px) {{ .cols {{ grid-template-columns:1fr; }} }}
    .assets {{ font-family:var(--mono); font-size:.74rem; margin:.2rem 0 .4rem; padding-left:1.1rem; }}
    .assets .len {{ color:var(--dim); font-size:.66rem; }}
    .assets .len.bad {{ color:var(--bad); font-weight:700; }}
    .serp {{ border:1px solid #e8eaed; border-radius:8px; padding:.65rem .8rem; margin:0 0 .5rem; background:#fff; }}
    .serp-label {{ font-size:.68rem; color:#5f6368; margin:0 0 .15rem; }}
    .serp-url {{ color:#202124; font-size:.78rem; margin:0; }}
    .serp-url span {{ color:#4d5156; }}
    .serp-title {{ color:#1a0dab; font-size:1.05rem; line-height:1.3; margin:.1rem 0; font-weight:400; }}
    .serp-desc {{ color:#4d5156; font-size:.86rem; margin:0; }}
  </style>
</head>
<body data-page="competitor-ads.html" data-foot="Competitor ads<br />Paused — do not enable">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="page-head">
        <p class="kicker">US + AU · VC_*_S_COMP · 19 Aug 2026</p>
        <h1>Competitor ad groups and RSAs</h1>
        <p>New paused Search campaigns. Exact keywords only — the strings people already typed. Landing pages stay <a href="https://{HOST}/us" target="_blank" rel="noopener">/us</a> and <a href="https://{HOST}/au" target="_blank" rel="noopener">/au</a>. Competitor names are keywords, never ad copy.</p>
      </header>
      <div class="banner" role="status">
        <strong>Paused. Do not enable.</strong> New <code>VC_US_S_COMP</code> / <code>VC_AU_S_COMP</code> only. Does not touch Core or Roles. Does not revive old LK/PM competitor campaigns. Google mixes headlines, so the blue lines below are realistic combinations — not a promise of one exact ad.
      </div>
      <p class="kicker">COMP campaign negatives (Phrase) — this campaign only</p>
      <div class="chips">{neg_chips}</div>
      <nav class="toc">{"".join(toc)}</nav>
      {"".join(articles)}
    </main>
  </div>
  <script src="nav.js?v=20260819-comp"></script>
</body>
</html>
"""
    path.write_text(page, encoding="utf-8")


def main() -> int:
    st_rows = load_search_terms()
    seen_in_st, shopping = mine_inventory(st_rows)
    rows_by_mkt = build_package(seen_in_st)
    negs_by_mkt = {"US": build_negatives("US"), "AU": build_negatives("AU")}
    qa(rows_by_mkt, negs_by_mkt)

    write_csv(HERE / "google-ads-editor-import-us.csv", FIELDS, rows_by_mkt["US"])
    write_csv(HERE / "google-ads-editor-import-au.csv", FIELDS, rows_by_mkt["AU"])
    write_csv(
        HERE / "google-ads-editor-campaign-negatives-us.csv",
        NEG_MMC_FIELDS,
        negs_by_mkt["US"],
    )
    write_csv(
        HERE / "google-ads-editor-campaign-negatives-au.csv",
        NEG_MMC_FIELDS,
        negs_by_mkt["AU"],
    )
    write_shopping_list(HERE / "shopping-list.md", shopping, seen_in_st)
    write_xray(XRAY / "competitor-ads.html", seen_in_st)

    def counts(mkt: str) -> tuple[int, int]:
        brands = sum(1 for b in BRANDS if seen_in_st.get((mkt, b["key"])))
        kws = sum(len(seen_in_st.get((mkt, b["key"]), set())) for b in BRANDS)
        return brands, kws

    us_b, us_k = counts("US")
    au_b, au_k = counts("AU")
    parked = [s for s in shopping if not s["bid"]]
    print(f"Wrote {HERE}")
    print(f"  US brands={us_b} exact={us_k} rows={len(rows_by_mkt['US'])}")
    print(f"  AU brands={au_b} exact={au_k} rows={len(rows_by_mkt['AU'])}")
    print(f"  parked ST terms={len(parked)}")
    print(f"  xray {XRAY / 'competitor-ads.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
