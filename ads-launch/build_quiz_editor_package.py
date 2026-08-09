#!/usr/bin/env python3
"""Build Paused Google Ads Editor CSVs for the quiz LP funnel.

VC_US_S_QUIZ / VC_AU_S_QUIZ — exploratory “Take the quiz / What kind of VA?”
Final URLs: /us/quiz and /au/quiz only. Exact match. Brand deferred.
No Ads API. Import → review → Post (still Paused) → Enable only when George says.

Usage:
  python3 ads-launch/build_quiz_editor_package.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
US = "496-715-1855"
AU = "573-539-1940"
HOST = "https://www.virtualcoworker.app"
LP_VERSION = "stage1-v8"

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

NEG_MMC_FIELDS = ["Account", "Campaign", "Keyword", "Match type", "Comment"]

UTM_SUFFIX = (
    "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"
    "&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}"
    f"&utm_device={{device}}&lp_version={LP_VERSION}"
)

# Cloned from CORE/ROLES employer themes — exploratory / “what VA do I need” spine.
# Exact only (live US convention). No job-seeker bait. No Brand.
AD_GROUPS = [
    {
        "name": "What_Kind_Of_VA",
        "cloned_from": "VC_*_S_CORE / Hire_VA_PH exploratory shape",
        "keywords": [
            "what kind of virtual assistant do i need",
            "what type of virtual assistant do i need",
            "what virtual assistant do i need",
            "what va do i need",
            "which virtual assistant do i need",
            "types of virtual assistants",
            "kinds of virtual assistants",
            "virtual assistant quiz",
            "hiring quiz virtual assistant",
            "what kind of va should i hire",
        ],
        "path1": "quiz",
        "path2": "what-va",
    },
    {
        "name": "Hire_VA_Explore",
        "cloned_from": "VC_*_S_CORE / Hire_VA_PH",
        "keywords": [
            "hire virtual assistant",
            "hire a virtual assistant",
            "hiring a virtual assistant",
            "how to hire a virtual assistant",
            "where to hire a virtual assistant",
            "hire virtual assistant philippines",
            "hire filipino virtual assistant",
            "hire a filipino virtual assistant",
            "how to hire filipino va",
        ],
        "path1": "quiz",
        "path2": "hire",
    },
    {
        "name": "VA_Small_Business",
        "cloned_from": "VC_*_S_ROLES small-business Exact themes",
        "keywords": [
            "virtual assistant for small business",
            "virtual assistant small business",
            "hire virtual assistant small business",
            "virtual assistant for small businesses",
            "va for small business",
            "virtual assistant for startup",
            "virtual assistant for startups",
            "small business virtual assistant",
        ],
        "path1": "quiz",
        "path2": "smb",
    },
    {
        "name": "Admin_VA_Quiz",
        "cloned_from": "VC_*_S_ROLES / Admin_*",
        "keywords": [
            "hire administrative assistant",
            "hire admin assistant",
            "virtual assistant for admin",
            "administrative virtual assistant",
            "virtual executive assistant",
            "hire virtual administrative assistant",
            "admin virtual assistant",
        ],
        "path1": "quiz",
        "path2": "admin",
    },
    {
        "name": "Bookkeeping_VA_Quiz",
        "cloned_from": "VC_*_S_ROLES / bookkeeping",
        "keywords": [
            "hire virtual bookkeeper",
            "virtual bookkeeper",
            "hire bookkeeper",
            "virtual assistant bookkeeping",
            "outsource bookkeeping",
            "hire virtual bookkeeping assistant",
        ],
        "path1": "quiz",
        "path2": "books",
    },
]

US_HEADLINES = [
    "What kind of VA do you need?",
    "Take the hiring quiz",
    "Find the right VA",
    "What should you hire first?",
    "A few taps. Clear answer.",
    "Quiz: admin, sales, books",
    "Find your first hire",
    "Employer hiring quiz",
    "Not a job board",
    "Dedicated Filipino VA",
    "Virtual assistant quiz",
    "See which seat to hire",
    "Who should you hire first?",
    "Filipino VA for SMBs",
    "Shortlist after the quiz",
]

AU_HEADLINES = [
    "What kind of VA do you need?",
    "Take the hiring quiz",
    "Find the right assistant",
    "Who should you hire first?",
    "A few taps. Clear answer.",
    "Quiz: admin, sales, books",
    "A starting point not a pitch",
    "For Australian businesses",
    "Not a job board",
    "Dedicated Filipino staff",
    "Virtual assistant quiz",
    "See which role to hire",
    "Have a chat after the quiz",
    "Filipino VA for SMBs",
    "Employer quiz, not jobs",
]

US_DESCS = [
    "Take the quiz. We’ll name the seat that buys back your week — then talk or leave a brief.",
    "Exploratory hiring quiz for US employers. Not a job board. Dedicated Filipino teammates.",
    "Admin, sales, books, support, or marketing? A few taps. A clear first hire.",
    "You interview the shortlist. Nobody starts until you say yes. Free chat after the quiz.",
]

AU_DESCS = [
    "Take the quiz. We’ll name the role that takes the load — then have a short chat.",
    "Hiring quiz for Australian businesses. Not a job board. Dedicated Filipino staff.",
    "Admin, sales, books, support or marketing? A few taps. A clear first hire.",
    "You interview the shortlist. Nobody starts until you say yes. No obligation.",
]


def blank_row() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def validate_rsa(headlines: list[str], descs: list[str], where: str) -> None:
    if len(headlines) != 15:
        raise SystemExit(f"{where}: need 15 headlines, got {len(headlines)}")
    if len(descs) != 4:
        raise SystemExit(f"{where}: need 4 descriptions, got {len(descs)}")
    if len(set(headlines)) != 15:
        raise SystemExit(f"{where}: duplicate headlines")
    if len(set(descs)) != 4:
        raise SystemExit(f"{where}: duplicate descriptions")
    for h in headlines:
        if len(h) > 30:
            raise SystemExit(f"{where}: headline too long ({len(h)}): {h}")
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: description too long ({len(d)}): {d}")


def campaign_row(*, account: str, camp: str, location: str, budget: str, cpc: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Campaign",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget": budget,
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Languages": "en",
            "Location": location,
            "Location options": "Presence",
            "Tracking template": "{lpurl}",
            "Final URL suffix": UTM_SUFFIX,
            "Maximum CPC bid limit": cpc,
            "Comment": (
                f"Quiz LP test {LP_VERSION} · Paused · Brand deferred · "
                "Final URL=/us/quiz or /au/quiz · Enable only when George says"
            ),
        }
    )
    return r


def ag_row(*, account: str, camp: str, ag: str, cloned: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Ad group",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Group Status": "Paused",
            "Comment": f"Quiz AG · cloned themes from {cloned} · Exact · Paused",
        }
    )
    return r


def kw_row(*, account: str, camp: str, ag: str, keyword: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Keyword",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Keyword": keyword,
            "Criterion Type": "Exact",
            "Keyword Status": "Paused",
            "Comment": "Quiz Exact · cloned employer-intent theme · Paused until Enable",
        }
    )
    return r


def rsa_row(
    *,
    account: str,
    camp: str,
    ag: str,
    final_url: str,
    path1: str,
    path2: str,
    headlines: list[str],
    descs: list[str],
) -> dict[str, str]:
    validate_rsa(headlines, descs, f"{camp}/{ag}")
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Ad",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": final_url,
            "Path 1": path1,
            "Path 2": path2,
            "Comment": "Quiz RSA · exploratory take-the-quiz · Paused · not hire-specialist hard sell",
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    return r


def build_market(
    *,
    account: str,
    camp: str,
    location: str,
    budget: str,
    cpc: str,
    final_url: str,
    headlines: list[str],
    descs: list[str],
) -> list[dict[str, str]]:
    rows = [campaign_row(account=account, camp=camp, location=location, budget=budget, cpc=cpc)]
    for ag in AD_GROUPS:
        rows.append(ag_row(account=account, camp=camp, ag=ag["name"], cloned=ag["cloned_from"]))
        for kw in ag["keywords"]:
            rows.append(kw_row(account=account, camp=camp, ag=ag["name"], keyword=kw))
        rows.append(
            rsa_row(
                account=account,
                camp=camp,
                ag=ag["name"],
                final_url=final_url,
                path1=ag["path1"],
                path2=ag["path2"],
                headlines=headlines,
                descs=descs,
            )
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_core_negatives(path: Path, campaign_filter: str) -> list[tuple[str, str]]:
    """(keyword, match_type) from existing MMC campaign-negatives file."""
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("Campaign") or "").strip() != campaign_filter:
                continue
            kw = (row.get("Keyword") or "").strip()
            mt = (row.get("Match type") or "Broad").strip() or "Broad"
            if not kw:
                continue
            key = (kw.lower(), mt.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append((kw, mt))
    return out


def build_negatives(
    *,
    account: str,
    camp: str,
    source_negs: list[tuple[str, str]],
    comment: str,
) -> list[dict[str, str]]:
    rows = []
    for kw, mt in source_negs:
        rows.append(
            {
                "Account": account,
                "Campaign": camp,
                "Keyword": kw,
                "Match type": mt,
                "Comment": comment,
            }
        )
    return rows


def main() -> None:
    us_rows = build_market(
        account=US,
        camp="VC_US_S_QUIZ",
        location="United States",
        budget="40",
        cpc="10",
        final_url=f"{HOST}/us/quiz",
        headlines=US_HEADLINES,
        descs=US_DESCS,
    )
    au_rows = build_market(
        account=AU,
        camp="VC_AU_S_QUIZ",
        location="Australia",
        budget="40",
        cpc="6",
        final_url=f"{HOST}/au/quiz",
        headlines=AU_HEADLINES,
        descs=AU_DESCS,
    )

    out_us = OUT_DIR / "google-ads-editor-quiz-import-us.csv"
    out_au = OUT_DIR / "google-ads-editor-quiz-import-au.csv"
    write_csv(out_us, us_rows, HEADERS)
    write_csv(out_au, au_rows, HEADERS)

    us_negs_src = load_core_negatives(OUT_DIR / "google-ads-editor-campaign-negatives-us.csv", "VC_US_S_CORE")
    au_negs_src = load_core_negatives(OUT_DIR / "google-ads-editor-campaign-negatives-au.csv", "VC_AU_S_CORE")
    if not us_negs_src:
        raise SystemExit("Missing US CORE campaign negatives to clone")
    if not au_negs_src:
        raise SystemExit("Missing AU CORE campaign negatives to clone")

    out_neg_us = OUT_DIR / "google-ads-editor-quiz-campaign-negatives-us.csv"
    out_neg_au = OUT_DIR / "google-ads-editor-quiz-campaign-negatives-au.csv"
    write_csv(
        out_neg_us,
        build_negatives(
            account=US,
            camp="VC_US_S_QUIZ",
            source_negs=us_negs_src,
            comment="Quiz campaign neg · cloned from VC_US_S_CORE Stage1 list · MMC only",
        ),
        NEG_MMC_FIELDS,
    )
    write_csv(
        out_neg_au,
        build_negatives(
            account=AU,
            camp="VC_AU_S_QUIZ",
            source_negs=au_negs_src,
            comment="Quiz campaign neg · cloned from VC_AU_S_CORE Stage1 list · MMC only",
        ),
        NEG_MMC_FIELDS,
    )

    print(f"US import: {out_us.name} ({len(us_rows)} rows)")
    print(f"AU import: {out_au.name} ({len(au_rows)} rows)")
    print(f"US negs MMC: {out_neg_us.name} ({len(us_negs_src)} rows)")
    print(f"AU negs MMC: {out_neg_au.name} ({len(au_negs_src)} rows)")
    print("Campaigns: VC_US_S_QUIZ · VC_AU_S_QUIZ — all Paused. No API mutate.")


if __name__ == "__main__":
    main()
