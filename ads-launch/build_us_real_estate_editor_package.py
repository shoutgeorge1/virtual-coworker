#!/usr/bin/env python3
"""Build Google Ads Editor import package: US real-estate VA vertical.

Live-US-safe:
- No campaign status/budget/bid-strategy rewrite (those columns blank)
- US account only
- Does not reactivate paused ad groups
- Does not delete anything
- API mutations are not used (Editor-only hard rule)

Usage:
  python3 ads-launch/build_us_real_estate_editor_package.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "real-estate-2026-08-18"
US = "496-715-1855"
HOST = "https://www.virtualcoworker.app"
FINAL = f"{HOST}/us/real-estate"
LABEL = "VC_REAL_ESTATE_TEST_2026-08-18"
CAMPAIGN = "VC_US_S_ROLES"
CORE = "VC_US_S_CORE"
HIRE_VA = "Hire_VA_PH"
CPC = "12.00"

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
    "Labels",
    "Comment",
]

DKI_RE = re.compile(r"^\{KeyWord:(.+)\}$")
FORBIDDEN = (
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


def blank_row() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def parse_kw(raw: str) -> tuple[str, str]:
    text = raw.strip()
    if text.startswith("[") and text.endswith("]"):
        return text[1:-1].strip(), "Exact"
    if text.startswith('"') and text.endswith('"'):
        return text[1:-1].strip(), "Phrase"
    return text, "Broad"


def headline_len(text: str) -> int:
    m = DKI_RE.match(text)
    return len(m.group(1)) if m else len(text)


def validate_rsa(headlines: list[str], descs: list[str], where: str, *, allow_dki: bool) -> None:
    if len(headlines) != 15:
        raise SystemExit(f"{where}: need 15 headlines, got {len(headlines)}")
    if len(descs) != 4:
        raise SystemExit(f"{where}: need 4 descriptions, got {len(descs)}")
    if len(set(headlines)) != 15:
        raise SystemExit(f"{where}: duplicate headlines")
    if len(set(descs)) != 4:
        raise SystemExit(f"{where}: duplicate descriptions")
    dki = [h for h in headlines if DKI_RE.match(h)]
    if allow_dki:
        if len(dki) != 1:
            raise SystemExit(f"{where}: challenger must have exactly one DKI, got {len(dki)}")
        if headlines[0] in dki:
            # Unpinned: do not place DKI first as a pin signal; keep it mid-list.
            pass
    elif dki:
        raise SystemExit(f"{where}: DKI not allowed")
    for d in descs:
        if DKI_RE.match(d):
            raise SystemExit(f"{where}: DKI in description")
    for h in headlines:
        n = headline_len(h)
        if n > 30:
            raise SystemExit(f"{where}: headline too long ({n}): {h}")
        if n < 1:
            raise SystemExit(f"{where}: empty headline")
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: description too long ({len(d)}): {d}")
        if len(d) < 1:
            raise SystemExit(f"{where}: empty description")
    blob = " ".join(headlines + descs)
    if blob.count("!") > 1 or blob.count("?") > 1:
        raise SystemExit(f"{where}: too many ! or ?")
    if "!" in blob and "?" in blob:
        raise SystemExit(f"{where}: ! and ? in the same ad")
    low = blob.lower()
    for bad in ("looking for a va?", "va seat", "hiring path", "scale smarter", "unlock growth"):
        if bad in low:
            raise SystemExit(f"{where}: banned phrase {bad!r}")
    for ch in FORBIDDEN:
        if ch in blob:
            raise SystemExit(f"{where}: forbidden character {ch!r}")
    for p in ("path1", "path2"):
        pass


def ag_row(name: str, comment: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad group",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Languages": "en",
            "Location options": "Presence",
            "Ad Group": name,
            "Ad Group Status": "Enabled",
            "Maximum CPC bid limit": CPC,
            "Labels": LABEL,
            "Comment": comment,
        }
    )
    return r


def kw_row(
    ag: str,
    keyword: str,
    match: str,
    *,
    status: str = "Enabled",
    negative: str = "",
    campaign: str = CAMPAIGN,
    comment: str = "",
) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Keyword",
            "Campaign": campaign,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Languages": "en",
            "Location options": "Presence",
            "Ad Group": ag,
            "Keyword": keyword,
            "Criterion Type": match,
            "Keyword Status": status,
            "Negative": negative,
            "Labels": LABEL if not negative else LABEL,
            "Comment": comment,
        }
    )
    return r


def rsa_row(ag: str, path1: str, path2: str, headlines: list[str], descs: list[str], comment: str) -> dict[str, str]:
    if len(path1) > 15 or len(path2) > 15:
        raise SystemExit(f"{ag}: path too long {path1!r}/{path2!r}")
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad",
            "Campaign": CAMPAIGN,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Languages": "en",
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Status": "Enabled",
            "Ad type": "Responsive search ad",
            "Final URL": FINAL,
            "Path 1": path1,
            "Path 2": path2,
            "Labels": LABEL,
            "Comment": comment,
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    return r


JOB_SEEKER_EXACT = [
    "real estate virtual assistant hiring",
    "property management virtual assistant jobs",
    "property management virtual assistant job description",
    "become a real estate virtual assistant",
    "freelance real estate assistant",
    "real estate assistant remote",
    "remote real estate assistant",
]

AG1_POS = """
[virtual assistant real estate]
"virtual assistant real estate"
[realtor virtual assistant]
"realtor virtual assistant"
[real estate agent virtual assistant]
"real estate agent virtual assistant"
[real estate virtual assistant services]
"real estate virtual assistant services"
[virtual assistant services for realtors]
"virtual assistant services for realtors"
[real estate virtual assistant companies]
"real estate virtual assistant companies"
[hire a virtual assistant real estate]
"hire a virtual assistant real estate"
[best real estate virtual assistant]
"best real estate virtual assistant"
""".strip().splitlines()

AG2_POS = """
[virtual assistant for real estate investors]
"virtual assistant for real estate investors"
virtual assistant for real estate investors
[best virtual assistants for real estate investors]
"best virtual assistants for real estate investors"
[virtual assistant for wholesaling real estate]
"virtual assistant for wholesaling real estate"
[wholesaling virtual assistant]
"wholesaling virtual assistant"
""".strip().splitlines()

AG3_POS = """
[property management virtual assistant]
"property management virtual assistant"
[virtual assistant property management]
"virtual assistant property management"
[virtual assistant for property management]
"virtual assistant for property management"
[virtual property management assistant]
"virtual property management assistant"
[property manager virtual assistant]
"property manager virtual assistant"
[property management virtual assistant companies]
"property management virtual assistant companies"
[best virtual assistant for property management]
"best virtual assistant for property management"
""".strip().splitlines()

REAL_ESTATE_A = (
    [
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
    [
        "Tell us the role. We recruit and vet candidates. You interview and choose who joins.",
        "Hire dedicated Philippines staff who work your US hours, not marketplace freelancers.",
        "Virtual Coworker shortlists people for your real-estate team. You decide who starts.",
        "For companies hiring staff. Book a hiring consultation to start the shortlist.",
    ],
)

REAL_ESTATE_B = (
    [
        "Lead Follow-Up Support",
        "CRM and Marketing Support",
        "Listing and Admin Support",
        "For Brokerages and Teams",
        "{KeyWord:Hire Real Estate VA}",
        "Follow Up on Your Leads",
        "Keep the CRM Current",
        "Listings and Paperwork",
        "Marketing Support Staff",
        "Appointment Setting Help",
        "Work Your US Hours",
        "You Interview Finalists",
        "Dedicated Staff, Not Gigs",
        "Hire for Your Workflow",
        "Book a Hiring Consult",
    ],
    [
        "Build support around lead follow-up, CRM, marketing, listings and administration.",
        "Hire dedicated Philippines staff who work your US hours. We recruit. You interview.",
        "Tell us the workflow. We shortlist people for your real-estate team. You choose.",
        "Book a hiring consultation. Dedicated staff, not one-off freelance task work.",
    ],
)

INVESTOR_A = (
    [
        "VA for Real Estate Investors",
        "Hire Investor Support Staff",
        "For Real Estate Investors",
        "We Recruit. You Interview.",
        "Dedicated Staff, Your Hours",
        "Vetted Staff for Your Team",
        "Not a Freelance Marketplace",
        "You Interview and Choose",
        "Filipino VA for Business",
        "Build Your Hiring Shortlist",
        "Work Your US Hours",
        "Dedicated Remote Staff",
        "Book a Hiring Consultation",
        "Staff for Investor Teams",
        "Hire Remote Investor Staff",
    ],
    [
        "Tell us the role. We recruit and vet candidates. You interview and choose who joins.",
        "Hire dedicated Philippines staff who work your US hours, not marketplace freelancers.",
        "Virtual Coworker shortlists people for investor support. You decide who starts.",
        "For companies hiring staff. Book a hiring consultation to start the shortlist.",
    ],
)

INVESTOR_B = (
    [
        "Lead Follow-Up Support",
        "CRM and List Support",
        "Investor Admin Support",
        "Follow Up on Your Leads",
        "Keep the CRM Current",
        "Deal Admin Support",
        "Listings and Paperwork",
        "For Investor Workflows",
        "Dedicated Staff, Not Gigs",
        "You Interview Finalists",
        "Work Your US Hours",
        "Not a Gig Marketplace",
        "Book a Hiring Consult",
        "Hire Investor Admin Help",
        "You Choose Who Joins",
    ],
    [
        "Build support around lead follow-up, CRM, lists and administration for investors.",
        "Hire dedicated Philippines staff who work your US hours. We recruit. You interview.",
        "Tell us the workflow. We shortlist people for your investor team. You choose.",
        "Book a hiring consultation. Dedicated staff, not one-off freelance task work.",
    ],
)

PM_A = (
    [
        "Property Management VA",
        "Hire Property Admin Staff",
        "For Property Managers",
        "We Recruit. You Interview.",
        "Dedicated Staff, Your Hours",
        "Vetted Staff for Your Team",
        "Not a Freelance Marketplace",
        "You Interview and Choose",
        "Filipino VA for Business",
        "Build Your Hiring Shortlist",
        "Work Your US Hours",
        "Tenant Communication Help",
        "Lease and Admin Support",
        "Book a Hiring Consultation",
        "Dedicated Remote Staff",
    ],
    [
        "Tell us the role. We recruit and vet candidates. You interview and choose who joins.",
        "Hire dedicated Philippines staff who work your US hours, not marketplace freelancers.",
        "Virtual Coworker shortlists people for property-management support. You decide.",
        "For companies hiring staff. Book a hiring consultation to start the shortlist.",
    ],
)

PM_B = (
    [
        "Tenant Communication Help",
        "Maintenance Admin Support",
        "Lease File Admin Support",
        "Owner Update Support",
        "Property Admin Support",
        "Keep the CRM Current",
        "Follow Up with Tenants",
        "Listing and Admin Support",
        "Dedicated Staff, Not Gigs",
        "You Interview Finalists",
        "Work Your US Hours",
        "Not a Gig Marketplace",
        "Book a Hiring Consult",
        "Hire Property Admin Help",
        "You Choose Who Joins",
    ],
    [
        "Build support around tenant messages, lease files, CRM and day-to-day admin.",
        "Hire dedicated Philippines staff who work your US hours. We recruit. You interview.",
        "Tell us the workflow. We shortlist people for your property team. You choose.",
        "Book a hiring consultation. Dedicated staff, not one-off freelance task work.",
    ],
)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS, extrasaction="raise")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> int:
    validate_rsa(*REAL_ESTATE_A, "Real_Estate_VA_PH A", allow_dki=False)
    validate_rsa(*REAL_ESTATE_B, "Real_Estate_VA_PH B", allow_dki=True)
    validate_rsa(*INVESTOR_A, "Real_Estate_Investors_VA_PH A", allow_dki=False)
    validate_rsa(*INVESTOR_B, "Real_Estate_Investors_VA_PH B", allow_dki=False)
    validate_rsa(*PM_A, "Property_Management_VA_PH A", allow_dki=False)
    validate_rsa(*PM_B, "Property_Management_VA_PH B", allow_dki=False)

    groups = [
        (
            "Real_Estate_VA_PH",
            AG1_POS,
            "real-estate",
            "hire",
            REAL_ESTATE_A,
            REAL_ESTATE_B,
            "Core realtor/real-estate cluster. Exact+Phrase only.",
        ),
        (
            "Real_Estate_Investors_VA_PH",
            AG2_POS,
            "investors",
            "hire",
            INVESTOR_A,
            INVESTOR_B,
            "Investor cluster. One Broad only: virtual assistant for real estate investors.",
        ),
        (
            "Property_Management_VA_PH",
            AG3_POS,
            "property",
            "hire",
            PM_A,
            PM_B,
            "Property-management cluster. Exact+Phrase only.",
        ),
    ]

    add_rows: list[dict[str, str]] = []
    seen_kw: set[tuple[str, str, str]] = set()
    for ag, positives, p1, p2, rsa_a, rsa_b, note in groups:
        add_rows.append(
            ag_row(
                ag,
                f"{LABEL} · {note} · Final URL=/us/real-estate · Campaign Status blank (live-US-safe)",
            )
        )
        for raw in positives:
            text, match = parse_kw(raw)
            key = (ag, text.lower(), match)
            if key in seen_kw:
                raise SystemExit(f"duplicate keyword {key}")
            seen_kw.add(key)
            if match == "Broad" and text.lower() != "virtual assistant for real estate investors":
                raise SystemExit(f"unexpected Broad: {text}")
            add_rows.append(
                kw_row(
                    ag,
                    text,
                    match,
                    comment=f"{LABEL} · +{match} · {text}",
                )
            )
        for raw in JOB_SEEKER_EXACT:
            add_rows.append(
                kw_row(
                    ag,
                    raw,
                    "Exact",
                    negative="Yes",
                    comment=f"{LABEL} · ad-group exact negative · job-seeker query",
                )
            )
        add_rows.append(
            rsa_row(
                ag,
                p1,
                p2,
                rsa_a[0],
                rsa_a[1],
                f"{LABEL} · RSA A static employer control · no DKI",
            )
        )
        add_rows.append(
            rsa_row(
                ag,
                p1,
                "staff" if p2 == "hire" else p2,
                rsa_b[0],
                rsa_b[1],
                f"{LABEL} · RSA B task challenger"
                + (" · one unpinned DKI" if ag == "Real_Estate_VA_PH" else " · no DKI"),
            )
        )

    # Unique path2 per RSA in same AG: hire vs staff already.
    cross_rows: list[dict[str, str]] = []
    for ag in ("Real_Estate_VA_PH", "Real_Estate_Investors_VA_PH"):
        cross_rows.append(
            kw_row(
                ag,
                "property management",
                "Phrase",
                negative="Yes",
                comment=f"{LABEL} · STEP 2 cross-negative · import after all 3 AGs eligible",
            )
        )
    for ag in ("Real_Estate_VA_PH", "Property_Management_VA_PH"):
        for term in ("investor", "wholesaling"):
            cross_rows.append(
                kw_row(
                    ag,
                    term,
                    "Phrase",
                    negative="Yes",
                    comment=f"{LABEL} · STEP 2 cross-negative · import after all 3 AGs eligible",
                )
            )

    pause_rows = [
        kw_row(
            HIRE_VA,
            "virtual assistant for real estate investors",
            "Broad",
            status="Paused",
            campaign=CORE,
            comment=(
                f"{LABEL} · STEP 3 pause original converting Broad in Hire_VA_PH "
                "after investor AG ads are eligible. Do not delete. "
                "Do not pause the Hire_VA_PH_offer_LP copy unless George says so."
            ),
        )
    ]

    rollback_rows = [
        ag_row("Real_Estate_VA_PH", f"{LABEL} · ROLLBACK · pause new AG"),
        ag_row("Real_Estate_Investors_VA_PH", f"{LABEL} · ROLLBACK · pause new AG"),
        ag_row("Property_Management_VA_PH", f"{LABEL} · ROLLBACK · pause new AG"),
        kw_row(
            HIRE_VA,
            "virtual assistant for real estate investors",
            "Broad",
            status="Enabled",
            campaign=CORE,
            comment=f"{LABEL} · ROLLBACK · re-enable original converting Broad",
        ),
    ]
    rollback_rows[0]["Ad Group Status"] = "Paused"
    rollback_rows[1]["Ad Group Status"] = "Paused"
    rollback_rows[2]["Ad Group Status"] = "Paused"

    optional_overlap = [
        kw_row(
            HIRE_VA,
            "best real estate virtual assistant",
            "Exact",
            status="Paused",
            campaign=CORE,
            comment=f"{LABEL} · OPTIONAL overlap pause · George review only",
        ),
        kw_row(
            "Offshore_VA_PH",
            "real estate virtual assistant",
            "Exact",
            status="Paused",
            campaign=CORE,
            comment=f"{LABEL} · OPTIONAL overlap pause · George review only",
        ),
        kw_row(
            "Offshore_VA_PH",
            "real estate virtual assistant",
            "Phrase",
            status="Paused",
            campaign=CORE,
            comment=f"{LABEL} · OPTIONAL overlap pause · George review only",
        ),
    ]

    write_csv(OUT / "01-adgroups-keywords-rsas-us.csv", add_rows)
    write_csv(OUT / "02-cross-negatives-us.csv", cross_rows)
    write_csv(OUT / "03-pause-original-broad-hire-va-ph-us.csv", pause_rows)
    write_csv(OUT / "99-rollback-us.csv", rollback_rows)
    write_csv(OUT / "optional-overlap-pauses-george-review-us.csv", optional_overlap)

    readme = OUT / "README.md"
    readme.write_text(
        f"""# US real-estate VA Editor package — 18 Aug 2026

Label: `{LABEL}`
Account: USA `{US}` only. Do not import into Australia.
Campaign: `{CAMPAIGN}` (do not create a new campaign).
Final URL: `{FINAL}`
Bidding / budget / geo: unchanged. Campaign Status, Budget, and Bid Strategy columns are blank.

API mutations were not used. Access is Basic, but the permanent Editor-only rule still applies.

## Already on the campaign (do not duplicate)

`VC_US_S_ROLES` already has these shared negative lists Enabled:

- `VC_US_S_🚫_Sniper`
- `VC_US_S_🥊_Competitors`
- `VC_US_S_🚫_JobSeekers`

Do not attach copies at ad-group level.

## Import order

1. Google Ads Editor → USA account → **Account → Import from file** → `01-adgroups-keywords-rsas-us.csv`
2. Review: 3 new ad groups Enabled, keywords, 2 RSAs each, job-seeker Exact negatives, label `{LABEL}`.
3. **Post**. Wait until all 3 ad groups show Eligible (or Eligible limited) and RSAs are serving.
4. Import `02-cross-negatives-us.csv` (Phrase cross-negatives). Post.
5. Import `03-pause-original-broad-hire-va-ph-us.csv`. This pauses **only** Broad `virtual assistant for real estate investors` in `VC_US_S_CORE` / `Hire_VA_PH`. Post.

Do not import `optional-overlap-pauses-george-review-us.csv` unless George approves. That file would pause overlapping Exact/Phrase terms still living in `Hire_VA_PH` and `Offshore_VA_PH`.

## Rollback

Import `99-rollback-us.csv`: pauses the three new ad groups and re-enables the original Broad keyword in `Hire_VA_PH`. Does not delete ads, keywords, or the landing page.

## What this package does not do

- Does not change Maximize Clicks, $150/$100 budgets, $30 CPC ceiling, US Presence, or conversion goals
- Does not reactivate paused ad groups
- Does not pause `virtual assistant agency in usa` (still Enabled Exact+Phrase in Hire_VA_PH; job-seeker conversion)
- Does not pause the same Broad keyword inside `Hire_VA_PH_offer_LP` (George call)
- Does not add US/USA/remote/hire/hiring/assistant/virtual assistant as negatives
- Does not touch Australia or Brand
""",
        encoding="utf-8",
    )
    print(f"Wrote {OUT}")
    print(f"  add rows: {len(add_rows)}")
    print(f"  cross-neg: {len(cross_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
