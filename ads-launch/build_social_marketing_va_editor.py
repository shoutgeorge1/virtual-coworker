#!/usr/bin/env python3
"""Build a live-safe Google Ads Editor add-on for Social / Marketing VA.

NEW paused ad groups only. Does not emit Campaign rows.
Campaign / existing Ad Group Status fields stay blank so a live VC_US_S_ROLES
campaign is not paused or rewritten.

No Ads API. Brand deferred. No Broad.
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path(__file__).with_name("google-ads-editor-social-marketing-va-us.csv")
ACCOUNT = "496-715-1855"
CAMPAIGN = "VC_US_S_ROLES"
COMMENT = (
    "Social/Marketing VA expansion 2026-08-19 · NEW paused only · "
    "do not enable with overlapping Social_Media_Hire_PH / Digital_Marketing_Hire_PH terms · "
    "Campaign/Ad Group Status blank on purpose (live US-safe)"
)

HEADER = [
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

SOCIAL_HEADLINES = [
    "Hire a Social Media VA",
    "Social Media VA Philippines",
    "Hire Social Media Assistant",
    "Filipino Social Media VA",
    "Dedicated Social Media Seat",
    "You Interview the Shortlist",
    "Staffing Not Freelance",
    "US Hours Social Media VA",
    "Social Calendar and Inbox",
    "Community Replies Covered",
    "Hire From the Philippines",
    "Not a Gig Marketplace",
    "Vetted Social Media Hire",
    "Keep Channels Active",
    "Book a Strategy Call",
]

SOCIAL_DESCS = [
    "Hire a dedicated Filipino social media VA. We recruit and vet. You interview first.",
    "Scheduling, replies, and reporting on your US hours. You meet them before they start.",
    "For employers only. This is a staffing hire, not a job ad and not a freelance gig.",
    "Tell us the seat. We shortlist. You decide who joins your social channels.",
]

MARKETING_HEADLINES = [
    "Hire a Marketing VA",
    "Digital Marketing VA Hire",
    "Marketing VA Philippines",
    "Hire Marketing Support",
    "Filipino Marketing VA",
    "Campaigns and Reporting",
    "You Interview Finalists",
    "Execution Not Strategy",
    "Dedicated Marketing Seat",
    "US Hours Marketing Hire",
    "Content Ops Support",
    "Staffing Not Freelance",
    "Vetted Marketing Shortlist",
    "Hire From the Philippines",
    "Book a Strategy Call",
]

MARKETING_DESCS = [
    "Hire a dedicated Filipino marketing VA. We recruit and vet. You interview first.",
    "Campaign support, reporting, and content ops on your hours. You keep the hire call.",
    "For employers only. Staffing hire, not a job ad, not a freelance marketing gig.",
    "Tell us the seat. We shortlist. You decide who joins your marketing work.",
]

SOCIAL_EXACT = [
    "social media virtual assistant",
    "hire social media virtual assistant",
    "social media va",
    "hire social media va",
    "virtual assistant for social media",
    "social media management virtual assistant",
    "virtual social media assistant",
    "virtual assistant social media",
    "social media manager virtual assistant",
    "social media marketing virtual assistant",
    "va for social media",
    "virtual social media manager",
]

SOCIAL_PHRASE = [
    "social media virtual assistant",
    "hire social media virtual assistant",
    "social media va",
    "virtual social media assistant",
    "social media management virtual assistant",
]

MARKETING_EXACT = [
    "digital marketing virtual assistant",
    "marketing virtual assistant",
    "virtual marketing assistant",
    "hire marketing virtual assistant",
    "marketing va",
    "virtual assistant for digital marketing",
    "digital marketing va",
    "virtual assistant digital marketing",
    "marketing virtual assistants",
    "hire digital marketing va",
    "remote marketing assistant",
]

MARKETING_PHRASE = [
    "digital marketing virtual assistant",
    "marketing virtual assistant",
    "virtual marketing assistant",
    "hire marketing virtual assistant",
    "digital marketing va",
]

# Already covered on VC_US_S_ROLES: job, jobs, salary, course, training,
# certification, how to become, upwork, fiverr, resume, work from home, indeed.
# Add only incremental social/marketing job-seeker roots.
NEW_NEGATIVES = [
    "interview questions",
    "become a virtual assistant",
    "become a social media va",
    "become a social media manager",
    "social media interview questions",
    "social media va salary",
    "pinterest va jobs",
    "instagram va jobs",
    "tiktok va jobs",
    "youtube va jobs",
]


def blank() -> dict[str, str]:
    return {k: "" for k in HEADER}


def check_rsa(headlines: list[str], descs: list[str], label: str) -> None:
    assert len(headlines) == 15, f"{label}: need 15 headlines, got {len(headlines)}"
    assert len(descs) == 4, f"{label}: need 4 descriptions, got {len(descs)}"
    for h in headlines:
        assert 1 <= len(h) <= 30, f"{label} headline {len(h)} chars: {h!r}"
        assert "{KeyWord" not in h and "{keyword" not in h, f"{label} DKI: {h!r}"
    for d in descs:
        assert 1 <= len(d) <= 90, f"{label} desc {len(d)} chars: {d!r}"


def ad_group_row(name: str) -> dict[str, str]:
    row = blank()
    row.update(
        {
            "Account": ACCOUNT,
            "Row Type": "Ad group",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": name,
            "Ad Group Status": "Paused",
            "Comment": COMMENT,
        }
    )
    return row


def keyword_row(group: str, term: str, match: str) -> dict[str, str]:
    row = blank()
    row.update(
        {
            "Account": ACCOUNT,
            "Row Type": "Keyword",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": group,
            "Keyword": term,
            "Criterion Type": match,
            "Keyword Status": "Paused",
            "Comment": COMMENT,
        }
    )
    return row


def ad_row(
    group: str,
    url: str,
    path1: str,
    path2: str,
    headlines: list[str],
    descs: list[str],
) -> dict[str, str]:
    row = blank()
    row.update(
        {
            "Account": ACCOUNT,
            "Row Type": "Ad",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": group,
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": url,
            "Path 1": path1,
            "Path 2": path2,
            "Comment": COMMENT,
        }
    )
    for i, h in enumerate(headlines, 1):
        row[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        row[f"Description {i}"] = d
    return row


def negative_row(term: str) -> dict[str, str]:
    row = blank()
    row.update(
        {
            "Account": ACCOUNT,
            "Row Type": "Keyword",
            "Campaign": CAMPAIGN,
            "Keyword": term,
            "Criterion Type": "Campaign negative",
            "Comment": (
                "VC_Neg_SocialMarketing_VA · incremental job-seeker roots "
                "2026-08-19 · not remote/work · existing Job Seekers/Competitors/Sniper unchanged"
            ),
        }
    )
    return row


def main() -> None:
    check_rsa(SOCIAL_HEADLINES, SOCIAL_DESCS, "social")
    check_rsa(MARKETING_HEADLINES, MARKETING_DESCS, "marketing")

    rows: list[dict[str, str]] = []
    rows.append(ad_group_row("Social_Media_VA_PH"))
    for term in SOCIAL_EXACT:
        rows.append(keyword_row("Social_Media_VA_PH", term, "Exact"))
    for term in SOCIAL_PHRASE:
        rows.append(keyword_row("Social_Media_VA_PH", term, "Phrase"))
    rows.append(
        ad_row(
            "Social_Media_VA_PH",
            "https://www.virtualcoworker.app/us/social-media",
            "social",
            "va",
            SOCIAL_HEADLINES,
            SOCIAL_DESCS,
        )
    )

    rows.append(ad_group_row("Digital_Marketing_VA_PH"))
    for term in MARKETING_EXACT:
        rows.append(keyword_row("Digital_Marketing_VA_PH", term, "Exact"))
    for term in MARKETING_PHRASE:
        rows.append(keyword_row("Digital_Marketing_VA_PH", term, "Phrase"))
    rows.append(
        ad_row(
            "Digital_Marketing_VA_PH",
            "https://www.virtualcoworker.app/us/digital-marketing",
            "marketing",
            "va",
            MARKETING_HEADLINES,
            MARKETING_DESCS,
        )
    )

    for term in NEW_NEGATIVES:
        rows.append(negative_row(term))

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
