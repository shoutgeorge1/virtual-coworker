#!/usr/bin/env python3
"""Build NEW Paused TF test ad groups for Google Ads Editor.

Creates only new AGs + paused keywords + paused RSAs.
Does not write into Hire_VA_PH, Offshore_VA_PH, Bookkeeping_Hire_PH,
or any other live ad-group name.

Campaigns stay existing (budget stays). Campaign Status blank.
Ad Group Status Paused. Keyword Status Paused. Ad Status Paused.

Do not import for George. No Ads API. Import ≠ live.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "keyword-rollout-narrow.csv"
HOST = "https://www.virtualcoworker.app"
ACCOUNT = "496-715-1855"
FORBIDDEN_AGS = {
    "Hire_VA_PH",
    "Offshore_VA_PH",
    "Bookkeeping_Hire_PH",
    "Real_Estate_Hire_PH",
    "Real_Estate_VA_PH",
}
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

COMMENT = (
    "new TF test AGs — do not touch existing groups · 2026-08-18 · "
    "NEW Paused AGs only · Campaign status blank · overlap with live AGs OK · "
    "no Brand · no CS · no setters · no Broad/DSA/PMax · "
    "Final URL on virtualcoworker.app"
)

# RSA copy: live US pull (_rsa_challenger_review.json) or RE draft.
# Original VC copy only — no competitor name.
RSA_PH = {
    "path1": "ph",
    "path2": "va",
    "headlines": [
        "Filipino Virtual Assistant",
        "VA Philippines Staffing",
        "Philippines VA Company",
        "US PH Remote Hire",
        "Offshore VA Partner",
        "Virtual Staff Philippines",
        "Dedicated PH VA Seat",
        "Outsource Admin to PH",
        "Not Gig Offshore VA",
        "Vetted Filipino Talent",
        "Remote Staff From PH",
        "Employer PH Hire Path",
        "Interview Before Place",
        "Staffing Not Freelance",
        "{KeyWord:Philippines Virtual Assistant}",
    ],
    "descriptions": [
        "Philippines VA and remote staff for US business ops capacity.",
        "Filipino talent shortlist — you interview; we recruit, vet, and support.",
        "Offshore staffing partner model. Not Upwork. Not a job board.",
        "Businesses only. An accepted form is not a hire or placement.",
    ],
}
RSA_HIRE = {
    "path1": "hire",
    "path2": "va",
    "headlines": [
        "Hire Virtual Assistant PH",
        "Hire Filipino VA",
        "US Employer VA Hire",
        "Philippines VA Staffing",
        "Dedicated Remote VA",
        "Vetted VA Shortlist",
        "Interview Before Hire",
        "Not Gig Platform VA",
        "How to Hire a VA",
        "Core VA Hire Process",
        "Hire PH Role Staff",
        "Remote Admin Capacity",
        "Clear Employer Process",
        "Staffing Partner Hire",
        "{KeyWord:Hire Virtual Assistant}",
    ],
    "descriptions": [
        "Hire dedicated Philippines VAs for your US business.",
        "Tell us who you need. We recruit and screen — you interview the shortlist.",
        "For businesses only. A form submit is not a hire or placement.",
        "Staffing partner for established businesses — not DIY training or job ads.",
    ],
}
RSA_RE = {
    "path1": "real-estate",
    "path2": "hire",
    "headlines": [
        "Hire a Real Estate VA",
        "Real Estate VA Philippines",
        "For Your Real Estate Team",
        "We Recruit. You Interview.",
        "Dedicated Staff, Your Hours",
        "Vetted Staff for Your Team",
        "Hire Remote Real Estate Staff",
        "Not a Freelance Marketplace",
        "Build Your Hiring Shortlist",
        "Filipino VA for Business",
        "You Interview and Choose",
        "Book a Hiring Consultation",
        "Dedicated Remote Staff",
        "Staff for US Real Estate",
        "Employers Hiring Staff",
    ],
    "descriptions": [
        "Tell us the role. We recruit and vet candidates. You interview and choose who joins.",
        "Hire dedicated Philippines staff who work your US hours, not marketplace freelancers.",
        "Virtual Coworker shortlists people for your real-estate team. You decide who starts.",
        "For companies hiring staff. Book a hiring consultation to start the shortlist.",
    ],
}
RSA_BOOKS = {
    "path1": "books",
    "path2": "va",
    "headlines": [
        "{KeyWord:Hire Bookkeeper}",
        "Philippines Books VA",
        "Remote Reconciliation Hire",
        "Filipino Books Specialist",
        "Weekly Close Support",
        "Transaction Coding VA",
        "Scale Bookkeeping Ops",
        "US SMBs Hiring",
        "Dedicated Books Talent",
        "Virtual Books Assistant",
        "Partner-Managed Hire",
        "Interview-Ready Bookkeepers",
        "Clear Employer Process",
        "Tools You Already Use",
        "Request Hiring Shortlist",
    ],
    "descriptions": [
        "Fill bookkeeping roles with vetted Philippines specialists.",
        "Support for categorization, reconciliations, and weekly books rhythm.",
        "Staffing support shaped for your US business books stack.",
        "We specialize in remote bookkeeping hires for employers.",
    ],
}

# (campaign, ad_group, path, exact_kws, phrase_kws, rsa)
CLUSTERS: list[tuple[str, str, str, list[str], list[str], dict]] = [
    (
        "VC_US_S_CORE",
        "TF_PH_VA",
        "/us/philippines-virtual-assistants",
        [
            "virtual assistant in the philippines",
            "philippines virtual assistant",
            "philippines virtual assistants",
            "virtual assistants in the philippines",
            "hire a virtual assistant from the philippines",
            "hire a virtual assistant in the philippines",
            "hire virtual assistant philippines",
            "hire philippines virtual assistant",
            "hire a filipino virtual assistant",
            "hire filipino virtual assistant",
            "filipino virtual assistant",
            "virtual assistant from the philippines",
            "dedicated filipino virtual assistant",
            "dedicated philippines virtual assistant",
        ],
        [],
        RSA_PH,
    ),
    (
        "VC_US_S_CORE",
        "TF_Hire_Dedicated",
        "/us/tf/hire",
        [
            "hire a virtual assistant",
            "hire virtual assistant",
            "looking for a virtual assistant",
            "dedicated virtual assistant",
            "remote virtual assistant for business",
            "hire a dedicated virtual assistant",
            "hire dedicated virtual assistant",
            "hire a virtual assistant for business",
            "dedicated virtual assistant for business",
            "hire a remote virtual assistant",
            "looking to hire a virtual assistant",
            "hire dedicated remote virtual assistant",
        ],
        [],
        RSA_HIRE,
    ),
    (
        "VC_US_S_ROLES",
        "TF_Real_Estate",
        "/us/tf/real-estate",
        [
            "real estate virtual assistant",
            "real estate virtual assistants",
            "hire real estate virtual assistant",
            "hire a real estate virtual assistant",
            "hire a real estate virtual assistant from the philippines",
            "filipino real estate virtual assistant",
            "philippines real estate virtual assistant",
            "dedicated real estate virtual assistant",
            "real estate admin virtual assistant",
            "hire filipino real estate virtual assistant",
            "virtual assistant for real estate",
            "real estate virtual assistant philippines",
        ],
        [],
        RSA_RE,
    ),
    (
        "VC_US_S_ROLES",
        "TF_Bookkeeping",
        "/us/tf/bookkeeping",
        [
            "bookkeeping virtual assistant",
            "virtual assistant bookkeeping",
            "virtual assistant bookkeeper",
            "hire a bookkeeping virtual assistant",
            "hire bookkeeping virtual assistant",
            "hire a virtual bookkeeper",
            "hire virtual bookkeeper",
            "filipino bookkeeping virtual assistant",
            "philippines bookkeeping virtual assistant",
            "virtual assistant for bookkeeping",
            "hire a filipino bookkeeper",
            "hire bookkeeper philippines",
            "quickbooks virtual assistant",
        ],
        [
            "virtual assistant bookkeeping",
            "bookkeeping virtual assistant",
        ],
        RSA_BOOKS,
    ),
]


def empty_row() -> dict[str, str]:
    return {h: "" for h in HEADER}


def base_fields(campaign: str, ag: str, path: str) -> dict[str, str]:
    return {
        "Account": ACCOUNT,
        "Campaign": campaign,
        "Campaign Type": "Search",
        "Networks": "Google Search",
        "Languages": "en",
        "Location options": "Presence",
        "Ad Group": ag,
        "Ad Group Status": "Paused",
        "Final URL": f"{HOST}{path}",
        "Comment": f"{COMMENT} · {ag} → {path}",
    }


def assert_rsa(ag: str, rsa: dict) -> None:
    heads = rsa["headlines"]
    descs = rsa["descriptions"]
    if len(heads) != 15 or len(descs) != 4:
        raise SystemExit(f"{ag} RSA needs 15 headlines and 4 descriptions")
    for i, h in enumerate(heads, 1):
        check = h
        if h.startswith("{KeyWord:") and h.endswith("}"):
            check = h[len("{KeyWord:") : -1]
        if len(check) > 30:
            raise SystemExit(f"{ag} H{i} is {len(check)} chars: {h}")
    for i, d in enumerate(descs, 1):
        if len(d) > 90:
            raise SystemExit(f"{ag} D{i} is {len(d)} chars: {d}")


def main() -> None:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for campaign, ag, path, exacts, phrases, rsa in CLUSTERS:
        if ag in FORBIDDEN_AGS:
            raise SystemExit(f"refusing live AG name {ag}")
        n = len(exacts) + len(phrases)
        if not (1 <= n <= 20):
            raise SystemExit(f"{ag} has {n} keywords; need 1–20")
        assert_rsa(ag, rsa)

        ag_row = empty_row()
        ag_row.update(base_fields(campaign, ag, path))
        ag_row["Row Type"] = "Ad group"
        ag_row["Comment"] = (
            f"{COMMENT} · NEW Paused AG {ag} → {path} · do not enable until George Posts"
        )
        rows.append(ag_row)

        ad_row = empty_row()
        ad_row.update(base_fields(campaign, ag, path))
        ad_row.update(
            {
                "Row Type": "Ad",
                "Ad Status": "Paused",
                "Ad type": "Responsive search ad",
                "Path 1": rsa["path1"],
                "Path 2": rsa["path2"],
            }
        )
        for i, h in enumerate(rsa["headlines"], 1):
            ad_row[f"Headline {i}"] = h
        for i, d in enumerate(rsa["descriptions"], 1):
            ad_row[f"Description {i}"] = d
        rows.append(ad_row)

        items: list[tuple[str, str]] = [(kw, "Exact") for kw in exacts] + [
            (kw, "Phrase") for kw in phrases
        ]
        for kw, match in items:
            key = (campaign, ag, kw.lower(), match)
            if key in seen:
                raise SystemExit(f"duplicate {key}")
            seen.add(key)
            row = empty_row()
            row.update(base_fields(campaign, ag, path))
            row.update(
                {
                    "Row Type": "Keyword",
                    "Keyword": kw,
                    "Criterion Type": match,
                    "Keyword Status": "Paused",
                }
            )
            rows.append(row)

    used_ags = {r["Ad Group"] for r in rows}
    clash = used_ags & FORBIDDEN_AGS
    if clash:
        raise SystemExit(f"output still names live AGs: {clash}")
    if any(r["Campaign Status"] for r in rows):
        raise SystemExit("Campaign Status must stay blank")

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    by_ag: dict[str, int] = {}
    keyword_rows = 0
    ad_rows = 0
    ag_rows = 0
    for r in rows:
        if r["Row Type"] == "Keyword":
            keyword_rows += 1
            by_ag[r["Ad Group"]] = by_ag.get(r["Ad Group"], 0) + 1
        elif r["Row Type"] == "Ad":
            ad_rows += 1
        elif r["Row Type"] == "Ad group":
            ag_rows += 1
    print(f"wrote {OUT}")
    print(f"rows {len(rows)} (AG {ag_rows} · ads {ad_rows} · keywords {keyword_rows})")
    for ag, n in by_ag.items():
        print(f"  {ag}: {n}")


if __name__ == "__main__":
    main()
