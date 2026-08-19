#!/usr/bin/env python3
"""Build a paused USA Editor add-on for Social / Marketing VA groups.

NEW ad groups only. Does not rewrite VC_US_S_ROLES, Social_Media_Hire_PH,
Digital_Marketing_Hire_PH, or any live campaign.

No Ads API. Import = local Editor draft. Post still leaves Status=Paused.
Enable is a George decision.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ads-launch" / "google-ads-editor-social-marketing-va-us.csv"
NEG_OUT = ROOT / "ads-launch" / "google-ads-editor-social-marketing-va-negatives-us.csv"

ACCOUNT = "496-715-1855"
CAMPAIGN = "VC_US_S_ROLES"
HOST = "https://www.virtualcoworker.app"
HL_MAX = 30
DESC_MAX = 90
PATH_MAX = 15

COLUMNS = [
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

COMMENT = (
    "Social/Marketing VA expansion 2026-08-19 · NEW paused AG · "
    "do not edit Social_Media_Hire_PH or Digital_Marketing_Hire_PH · "
    "Final URL = live category LP (preview slug not an Ads destination)"
)

# Exact-only on short heads that leak job-seeker / course traffic on Phrase.
SOCIAL_EXACT_ONLY = [
    "social media va",
]
SOCIAL_EXACT_AND_PHRASE = [
    "social media virtual assistant",
    "hire social media virtual assistant",
    "hire social media va",
    "virtual assistant for social media",
    "virtual assistant social media",
    "virtual social media assistant",
    "social media management virtual assistant",
    "social media marketing virtual assistant",
    "instagram virtual assistant",
    "hire instagram virtual assistant",
]

DIGITAL_EXACT_ONLY = [
    "marketing va",
    "digital marketing va",
]
DIGITAL_EXACT_AND_PHRASE = [
    "digital marketing virtual assistant",
    "marketing virtual assistant",
    "virtual marketing assistant",
    "hire marketing virtual assistant",
    "hire digital marketing virtual assistant",
    "virtual assistant for digital marketing",
    "virtual assistant digital marketing",
    "remote marketing assistant",
]

SOCIAL_RSA = {
    "headlines": [
        "Hire a Social Media VA",
        "Philippines Social Media VA",
        "Dedicated Social Media Seat",
        "Social Media VA Hire",
        "You Interview the Shortlist",
        "Scheduling and Community",
        "Filipino Social Media VA",
        "Staffing, Not a Gig App",
        "Keep Channels Moving",
        "Content Calendar Support",
        "Not a Freelance Roster",
        "Social VA for US Hours",
        "Hire Social Media Support",
        "Book a Strategy Call",
        "Hire From the Philippines",
    ],
    "descriptions": [
        "Hire a dedicated social media virtual assistant from the Philippines. You interview first.",
        "Scheduling, community replies, and weekly reporting owned by one person on your hours.",
        "Virtual Coworker recruits and vets. Nobody starts until you say yes. We handle payroll.",
        "For businesses hiring staff. Looking for a job? Use the careers link, not this form.",
    ],
    "path1": "social",
    "path2": "va",
    "final": f"{HOST}/us/social-media",
}

DIGITAL_RSA = {
    "headlines": [
        "Hire a Marketing VA",
        "Virtual Marketing Assistant",
        "Digital Marketing VA Hire",
        "Philippines Marketing VA",
        "Campaign and Reporting Help",
        "You Interview Finalists",
        "Dedicated Marketing Seat",
        "Email and CRM Support",
        "Execution, Not Strategy",
        "Staffing, Not a Retainer",
        "Filipino Marketing VA",
        "Hire Marketing Support",
        "Content Ops Support",
        "Book a Strategy Call",
        "Hire From the Philippines",
    ],
    "descriptions": [
        "Hire a dedicated digital marketing virtual assistant from the Philippines. You interview.",
        "Campaign support, email, CRM updates, and reporting. Execution help, not a retainers shop.",
        "We recruit and vet. You meet the shortlist. After you hire, we handle payroll.",
        "For US businesses hiring staff. This form is not a job application.",
    ],
    "path1": "marketing",
    "path2": "va",
    "final": f"{HOST}/us/digital-marketing",
}

# Phrase campaign negatives not already covered well by Stage1 Broad jobs/course/training.
SOCIAL_EXTRA_NEGATIVES = [
    "interview questions",
    "become a social media manager",
    "become a social media va",
    "become a virtual assistant",
    "social media portfolio",
    "freelance social media manager",
    "pinterest va training",
    "canva course",
]


def blank() -> dict[str, str]:
    return {k: "" for k in COLUMNS}


def check_rsa(name: str, rsa: dict) -> None:
    assert len(rsa["headlines"]) == 15, name
    assert len(rsa["descriptions"]) == 4, name
    assert len(rsa["path1"]) <= PATH_MAX
    assert len(rsa["path2"]) <= PATH_MAX
    seen: set[str] = set()
    for h in rsa["headlines"]:
        if len(h) > HL_MAX:
            raise SystemExit(f"{name} headline too long ({len(h)}): {h}")
        if "{" in h:
            raise SystemExit(f"{name} has DKI: {h}")
        key = h.casefold()
        if key in seen:
            raise SystemExit(f"{name} duplicate headline: {h}")
        seen.add(key)
    for d in rsa["descriptions"]:
        if len(d) > DESC_MAX:
            raise SystemExit(f"{name} description too long ({len(d)}): {d}")
        if "{" in d:
            raise SystemExit(f"{name} description has DKI: {d}")


def keyword_rows(ad_group: str, exact_only: list[str], both: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for text in exact_only + both:
        row = blank()
        row.update(
            {
                "Account": ACCOUNT,
                "Row Type": "Keyword",
                "Campaign": CAMPAIGN,
                "Campaign Type": "Search",
                "Budget type": "Daily",
                "Bid Strategy Type": "Maximize Clicks",
                "Networks": "Google Search",
                "Location options": "Presence",
                "Ad Group": ad_group,
                "Keyword": text,
                "Criterion Type": "Exact",
                "Keyword Status": "Paused",
                "Comment": COMMENT,
            }
        )
        rows.append(row)
    for text in both:
        row = blank()
        row.update(
            {
                "Account": ACCOUNT,
                "Row Type": "Keyword",
                "Campaign": CAMPAIGN,
                "Campaign Type": "Search",
                "Budget type": "Daily",
                "Bid Strategy Type": "Maximize Clicks",
                "Networks": "Google Search",
                "Location options": "Presence",
                "Ad Group": ad_group,
                "Keyword": text,
                "Criterion Type": "Phrase",
                "Keyword Status": "Paused",
                "Comment": COMMENT + " · Phrase on 3+ word employer phrase only",
            }
        )
        rows.append(row)
    return rows


def ad_group_row(name: str) -> dict[str, str]:
    row = blank()
    row.update(
        {
            "Account": ACCOUNT,
            "Row Type": "Ad group",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": name,
            "Ad Group Status": "Paused",
            "Comment": COMMENT,
        }
    )
    return row


def ad_row(ad_group: str, rsa: dict, note: str) -> dict[str, str]:
    row = blank()
    payload = {
        "Account": ACCOUNT,
        "Row Type": "Ad",
        "Campaign": CAMPAIGN,
        "Campaign Type": "Search",
        "Budget type": "Daily",
        "Bid Strategy Type": "Maximize Clicks",
        "Networks": "Google Search",
        "Location options": "Presence",
        "Ad Group": ad_group,
        "Ad Group Status": "Paused",
        "Ad Status": "Paused",
        "Ad type": "Responsive search ad",
        "Final URL": rsa["final"],
        "Path 1": rsa["path1"],
        "Path 2": rsa["path2"],
        "Comment": f"{COMMENT} · {note}",
    }
    for i, h in enumerate(rsa["headlines"], 1):
        payload[f"Headline {i}"] = h
    for i, d in enumerate(rsa["descriptions"], 1):
        payload[f"Description {i}"] = d
    row.update(payload)
    return row


def main() -> None:
    check_rsa("social", SOCIAL_RSA)
    check_rsa("digital", DIGITAL_RSA)

    rows = [
        ad_group_row("Social_Media_VA_PH"),
        *keyword_rows("Social_Media_VA_PH", SOCIAL_EXACT_ONLY, SOCIAL_EXACT_AND_PHRASE),
        ad_row("Social_Media_VA_PH", SOCIAL_RSA, "1 RSA experiment"),
        ad_group_row("Digital_Marketing_VA_PH"),
        *keyword_rows("Digital_Marketing_VA_PH", DIGITAL_EXACT_ONLY, DIGITAL_EXACT_AND_PHRASE),
        ad_row("Digital_Marketing_VA_PH", DIGITAL_RSA, "1 RSA experiment"),
    ]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    with NEG_OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["Account", "Campaign", "Keyword", "Match type", "Comment"])
        for term in SOCIAL_EXTRA_NEGATIVES:
            writer.writerow(
                [
                    ACCOUNT,
                    CAMPAIGN,
                    term,
                    "Phrase",
                    "Social/Marketing VA extra job-seeker Phrase · optional · "
                    "do not add remote or work · Stage1 Broad jobs/course/training already cover most",
                ]
            )

    print(f"wrote {OUT} ({len(rows)} rows)")
    print(f"wrote {NEG_OUT} ({len(SOCIAL_EXTRA_NEGATIVES)} negatives)")


if __name__ == "__main__":
    main()
