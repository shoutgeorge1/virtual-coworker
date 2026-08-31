#!/usr/bin/env python3
"""Build Paused US brand Search campaign for Google Ads Editor.

VC_US_S_BRAND — Target Impression Share, .com homepage, Exact+Phrase, no Broad.
Does not mutate Ads via API. Does not create AU. Does not rewrite CORE/ROLES
except a separate pause CSV for the live Brand_VC ad group.

Usage:
  python3 ads-launch/build_us_brand_campaign.py
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
MIRROR = OUT_DIR.parent / "xray" / "docs" / "ads-launch"
US = "496-715-1855"
HOST = "https://www.virtualcoworker.com"
CAMPAIGN = "VC_US_S_BRAND"
AG = "BRAND_CORE"
CORE = "VC_US_S_CORE"
CORE_BRAND_AG = "Brand_VC"

HL_MAX = 30
DESC_MAX = 90
PATH_MAX = 15
LINK_MAX = 25
SL_DESC_MAX = 35

HEADERS = [
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

NEG_HEADERS = ["Account", "Campaign", "Keyword", "Match type", "Comment"]

UTM = (
    "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"
    "&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}"
    "&utm_device={device}&lp=brand"
)

COMMENT = (
    "VC_US_S_BRAND 2026-08-13; Paused; TIS Top of page 85% — set location/"
    "percent in Editor after import if CSV does not apply them; Max CPC $12 "
    "(historical Brand avg CPC $11.33 on 1134 clicks; current Brand_VC $1.74 "
    "is 5 clicks); $15/day isolation placeholder (George sets before Post); "
    "Search only; Presence US; Exact+Phrase; no Broad; final URL=.com homepage; "
    "sitelink Contact=/contact-us/; do not Enable until .com tags verified; "
    "do not import the CORE Brand_VC pause CSV until Enable day"
)

HEADLINES = [
    "Virtual Coworker",
    "Official Virtual Coworker Site",
    "Dedicated Virtual Assistants",
    "Dedicated Filipino Staff",
    "Build Your Remote Team",
    "Serving Businesses Since 2011",
    "Full-Time or Part-Time",
    "Staff Work Your Time Zone",
    "Book Your Consultation",
    "Hire Philippines Talent",
    "Not a Freelancer Marketplace",
    "Recruitment and Support",
    "Build Your Philippines Team",
    "Find Your Next Remote Hire",
    "Virtual Coworker Staffing",
]

DESCRIPTIONS = [
    "Hire dedicated full-time or part-time Philippines staff. We recruit, vet, and support.",
    "Build your remote team with Virtual Coworker. Since 2011. Staff work your business hours.",
    "Tell us the role. We recruit and screen. You interview on video. Book a consultation.",
    "Not a freelancer marketplace. Dedicated Filipino staff. White-glove support.",
]

EXACT = [
    "virtual coworker",
    "virtualcoworker",
    "virtual coworker usa",
    "virtual coworker staffing",
    "virtual coworker reviews",
    "virtual coworker pricing",
]

PHRASE = ["virtual coworker"]

NEGATIVES = [
    "job",
    "jobs",
    "careers",
    "career",
    "login",
    "employee",
    "payroll portal",
    "application status",
    "salary",
    "salaries",
    "apply",
    "application",
    "resume",
    "cv",
    "vacancy",
    "vacancies",
    "work from home",
    "work from home jobs",
    "virtual assistant jobs",
    "philippines jobs",
    "remote jobs",
    "employee login",
    "applicant login",
    "bpo",
    "call center",
    "call centre",
    "callcenter",
    "va jobs",
    "job opening",
    "job openings",
    "i want a job",
    "looking for a job",
    "hiring jobs",
]

SITELINKS = [
    (
        "Book Consultation",
        "Employer enquiry form",
        "US businesses only",
        f"{HOST}/contact-us/",
    ),
    (
        "How It Works",
        "Recruit, vet, shortlist",
        "You interview talent",
        f"{HOST}/how-it-works/",
    ),
    (
        "Services",
        "Philippines staffing",
        "Roles we fill",
        f"{HOST}/services/",
    ),
    (
        "About Us",
        "Serving businesses since 2011",
        "Dedicated PH staff",
        f"{HOST}/about/",
    ),
]


def blank() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def check_copy() -> None:
    if len(HEADLINES) != 15:
        raise SystemExit(f"need 15 headlines, got {len(HEADLINES)}")
    if len(DESCRIPTIONS) != 4:
        raise SystemExit(f"need 4 descriptions, got {len(DESCRIPTIONS)}")
    seen: set[str] = set()
    for h in HEADLINES:
        if len(h) > HL_MAX:
            raise SystemExit(f"headline {len(h)} > {HL_MAX}: {h!r}")
        key = h.lower()
        if key in seen:
            raise SystemExit(f"duplicate headline: {h!r}")
        seen.add(key)
    for d in DESCRIPTIONS:
        if len(d) > DESC_MAX:
            raise SystemExit(f"description {len(d)} > {DESC_MAX}: {d!r}")
        low = d.lower()
        if any(bad in low for bad in ("$7", "guarantee", "450,000", "290,000")):
            raise SystemExit(f"forbidden claim in description: {d!r}")
    for text, d1, d2, url in SITELINKS:
        if len(text) > LINK_MAX:
            raise SystemExit(f"sitelink text {len(text)} > {LINK_MAX}: {text!r}")
        if len(d1) > SL_DESC_MAX:
            raise SystemExit(f"sitelink d1 {len(d1)} > {SL_DESC_MAX}: {d1!r}")
        if len(d2) > SL_DESC_MAX:
            raise SystemExit(f"sitelink d2 {len(d2)} > {SL_DESC_MAX}: {d2!r}")
        if not url.startswith(HOST):
            raise SystemExit(f"sitelink must be {HOST}: {url}")


def campaign_row() -> dict[str, str]:
    r = blank()
    r.update(
        {
            "Account": US,
            "Row Type": "Campaign",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget": "15",
            "Budget type": "Daily",
            "Bid Strategy Type": "Target impression share",
            "Networks": "Google Search",
            "Languages": "en",
            "Location": "United States",
            "Location options": "Presence",
            "Tracking template": "{lpurl}",
            "Final URL suffix": UTM,
            "Maximum CPC bid limit": "12",
            "Comment": COMMENT,
        }
    )
    return r


def ag_row() -> dict[str, str]:
    r = blank()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad group",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget type": "Daily",
            "Bid Strategy Type": "Target impression share",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": AG,
            "Ad Group Status": "Paused",
            "Comment": "Single brand AG at launch — split only when query volume justifies unique LP/copy",
        }
    )
    return r


def kw_row(term: str, match: str) -> dict[str, str]:
    r = blank()
    r.update(
        {
            "Account": US,
            "Row Type": "Keyword",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget type": "Daily",
            "Bid Strategy Type": "Target impression share",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": AG,
            "Ad Group Status": "Paused",
            "Keyword": term,
            "Criterion Type": match,
            "Keyword Status": "Paused",
            "Comment": "Brand Exact/Phrase only; no Broad",
        }
    )
    return r


def rsa_row() -> dict[str, str]:
    r = blank()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget type": "Daily",
            "Bid Strategy Type": "Target impression share",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": AG,
            "Ad Group Status": "Paused",
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": f"{HOST}/",
            "Path 1": "official",
            "Path 2": "brand",
            "Comment": "Unpinned RSA; homepage .com; no pricing/guarantees/counts",
        }
    )
    for i, h in enumerate(HEADLINES, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(DESCRIPTIONS, 1):
        r[f"Description {i}"] = d
    return r


def sitelink_row(text: str, d1: str, d2: str, url: str) -> dict[str, str]:
    r = blank()
    r.update(
        {
            "Account": US,
            "Row Type": "Sitelink",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Final URL": url,
            "Link Text": text,
            "Description Line 1": d1,
            "Description Line 2": d2,
            "Comment": "Brand sitelinks on .com; Campaign Status blank (campaign created Paused in same file)",
        }
    )
    return r


def pause_core_brand_ag() -> dict[str, str]:
    r = blank()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad group",
            "Campaign": CORE,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Languages": "en",
            "Location options": "Presence",
            "Ad Group": CORE_BRAND_AG,
            "Ad Group Status": "Paused",
            "Comment": (
                "ENABLE-DAY ONLY. Do not import during planning. Pause "
                "Brand_VC inside CORE so VC_US_S_BRAND is the only US brand "
                "bidder. Campaign Status blank — do not pause CORE."
            ),
        }
    )
    return r


def write_csv(path: Path, rows: list[dict[str, str]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=headers, extrasaction="raise")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def mirror(path: Path) -> None:
    MIRROR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, MIRROR / path.name)


def main() -> None:
    check_copy()
    if len("official") > PATH_MAX or len("brand") > PATH_MAX:
        raise SystemExit("display path too long")

    brand_rows = [campaign_row(), ag_row()]
    for term in EXACT:
        brand_rows.append(kw_row(term, "Exact"))
    for term in PHRASE:
        brand_rows.append(kw_row(term, "Phrase"))
    brand_rows.append(rsa_row())
    for text, d1, d2, url in SITELINKS:
        brand_rows.append(sitelink_row(text, d1, d2, url))

    brand_path = OUT_DIR / "google-ads-editor-brand-us.csv"
    write_csv(brand_path, brand_rows, HEADERS)

    neg_comment = (
        "VC_US_S_BRAND dedicated negatives; NOT PM_* mega list; "
        "MMC Keywords, Negative only; hiring/philippines omitted on purpose"
    )
    neg_rows = [
        {
            "Account": US,
            "Campaign": CAMPAIGN,
            "Keyword": term,
            "Match type": "Broad",
            "Comment": neg_comment,
        }
        for term in NEGATIVES
    ]
    neg_path = OUT_DIR / "google-ads-editor-brand-negatives-us.csv"
    write_csv(neg_path, neg_rows, NEG_HEADERS)

    pause_path = OUT_DIR / "google-ads-editor-brand-pause-core-ag-us.csv"
    write_csv(pause_path, [pause_core_brand_ag()], HEADERS)

    for p in (brand_path, neg_path, pause_path):
        mirror(p)

    print(f"wrote {brand_path.name} ({len(brand_rows)} rows)")
    print(f"wrote {neg_path.name} ({len(neg_rows)} negatives)")
    print(f"wrote {pause_path.name} (pause {CORE}/{CORE_BRAND_AG})")
    print("mirrored to xray/docs/ads-launch/")


if __name__ == "__main__":
    main()
