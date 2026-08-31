#!/usr/bin/env python3
"""Build Paused Google Ads Editor Exact keyword CSV for trust-first live /us URLs.

No Ads API. Import ≠ live. George Posts/enables in Editor.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "keyword-rollout-launch.csv"
HOST = "https://www.virtualcoworker.app"
ACCOUNT = "496-715-1855"
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
    "Employer Exact · job-seeker risk · Paused · do not enable until George Posts in Editor "
    "· live Final URL on virtualcoworker.app · no Brand · no generic virtual assistants head-term group"
)

# (campaign, ad_group, path, keywords)
CLUSTERS: list[tuple[str, str, str, list[str]]] = [
    (
        "VC_US_S_CORE",
        "Offshore_VA_PH",
        "/us/philippines-virtual-assistants",
        [
            "virtual assistant philippines",
            "philippines virtual assistant",
            "philippines virtual assistants",
            "virtual assistant in the philippines",
            "virtual assistants in the philippines",
            "hire a virtual assistant from the philippines",
            "hire a virtual assistant in the philippines",
            "hire virtual assistant philippines",
            "hire philippines virtual assistant",
            "hire a filipino virtual assistant",
            "hire filipino virtual assistant",
            "filipino virtual assistant",
            "filipino virtual assistants",
            "offshore virtual assistant",
            "offshore virtual assistants",
            "outsourcing virtual assistant",
            "virtual assistant overseas",
            "remote staff philippines",
            "philippines va",
            "filipino va",
            "hire filipino va",
            "hire a filipino va",
            "hire va philippines",
            "offshore va",
            "virtual assistant from the philippines",
            "dedicated filipino virtual assistant",
            "filipino remote virtual assistant",
            "philippines remote virtual assistant",
            "virtual assistant services philippines",
        ],
    ),
    (
        "VC_US_S_CORE",
        "Virtual_Staff_PH",
        "/us/philippines-virtual-assistants",
        [
            "virtual staff philippines",
            "philippines virtual staff",
            "hire virtual staff philippines",
            "filipino virtual staff",
            "offshore virtual staff",
            "remote virtual staff philippines",
            "virtual staffing philippines",
        ],
    ),
    (
        "VC_US_S_CORE",
        "VA_Agency_Firm_PH",
        "/us/virtual-assistant-agency",
        [
            "virtual assistant agency",
            "virtual assistant agencies",
            "virtual assistant company",
            "virtual assistant companies",
            "virtual assistant firm",
            "va company",
            "va firm",
            "va agency",
            "filipino va agency",
            "filipino virtual assistant agency",
            "filipino virtual assistant company",
            "philippines virtual assistant agency",
            "philippines va company",
            "philippines va agency",
            "virtual assistant company philippines",
            "dedicated virtual assistant agency",
            "virtual assistant outsourcing agency",
            "virtual assistant staffing company",
            "best virtual assistant agency",
            "virtual assistant agency philippines",
            "offshore virtual assistant agency",
            "remote virtual assistant agency",
            "hire virtual assistant agency",
        ],
    ),
    (
        "VC_US_S_CORE",
        "Staffing_Agency_PH",
        "/us/staffing",
        [
            "remote staffing agency",
            "remote staffing agencies",
            "virtual staffing agency",
            "virtual assistant staffing agency",
            "offshore staffing agency",
            "offshore staffing company",
            "philippines staffing agency",
            "philippines staffing company",
            "staffing firm philippines",
            "filipino staffing agency",
            "philippines virtual staffing agency",
            "philippines remote staffing agency",
            "virtual staffing company",
            "remote staffing company",
            "offshore staffing firm",
            "remote staffing partner",
            "philippines remote staffing",
            "filipino remote staffing agency",
            "best remote staffing agencies",
            "hire remote staffing agency",
        ],
    ),
    (
        "VC_US_S_CORE",
        "Agency_PH",
        "/us/staffing",
        [
            "philippines outsourcing agency",
            "outsourcing agency philippines",
            "outsourcing company philippines",
            "filipino outsourcing agency",
            "va outsourcing philippines",
            "philippines va outsourcing",
            "offshore va agency",
            "philippines outsourcing company",
            "bpo staffing philippines",
            "outsourcing firm philippines",
        ],
    ),
    (
        "VC_US_S_CORE",
        "Hire_VA_PH",
        "/us",
        [
            "hire a virtual assistant",
            "hire virtual assistant",
            "hire a dedicated virtual assistant",
            "dedicated virtual assistant",
            "remote virtual assistant for business",
            "hire remote virtual assistant",
            "hire a remote virtual assistant",
            "how to hire a virtual assistant",
            "virtual assistant for hire",
            "virtual assistants for hire",
            "looking for a virtual assistant",
            "hire offshore virtual assistant",
            "hire overseas virtual assistant",
            "full time virtual assistant",
            "dedicated remote virtual assistant",
            "hire a full time virtual assistant",
            "business virtual assistant",
            "virtual assistant for small business",
            "hire virtual assistant for business",
            "executive virtual assistant hire",
        ],
    ),
    (
        "VC_US_S_ROLES",
        "Bookkeeping_Hire_PH",
        "/us/bookkeeping",
        [
            "bookkeeping virtual assistant",
            "virtual assistant bookkeeping",
            "virtual assistant bookkeeper",
            "virtual bookkeeper",
            "virtual bookkeeping",
            "remote bookkeeper",
            "philippines bookkeepers",
            "bookkeeper philippines",
            "quickbooks virtual assistant",
            "hire a virtual bookkeeper",
            "hire virtual bookkeeper",
            "philippines bookkeeper",
            "filipino bookkeeper",
            "remote bookkeeping virtual assistant",
            "xero virtual assistant",
            "virtual assistant for bookkeeping",
            "hire bookkeeper philippines",
            "online bookkeeper philippines",
        ],
    ),
    (
        "VC_US_S_ROLES",
        "Customer_Service_Hire_PH",
        "/us/customer-service",
        [
            "virtual assistant customer service",
            "filipino customer service",
            "philippines customer service",
            "customer service philippines",
            "outsource customer service",
            "philippines customer service outsourcing",
            "customer support philippines",
            "virtual customer service",
            "hire customer service philippines",
            "filipino customer support",
            "remote customer service virtual assistant",
            "customer service virtual assistant",
            "philippines customer support",
            "hire filipino customer service",
            "virtual assistant for customer service",
        ],
    ),
    (
        "VC_US_S_ROLES",
        "Sales_Hire_PH",
        "/us/sales",
        [
            "sales virtual assistant",
            "virtual sales assistant",
            "virtual assistant for lead generation",
            "virtual assistant sales",
            "sales support virtual assistant",
            "crm virtual assistant",
            "hire sales virtual assistant",
            "filipino sales virtual assistant",
            "sales admin virtual assistant",
            "lead follow up virtual assistant",
        ],
    ),
    (
        "VC_US_S_ROLES",
        "Administration_EA_PH",
        "/us/administrative-support",
        [
            "virtual administrative assistant",
            "remote executive assistant",
            "virtual executive assistant philippines",
            "executive assistant philippines",
            "personal assistant philippines",
            "virtual executive assistant",
            "hire virtual administrative assistant",
            "filipino executive assistant",
            "administrative virtual assistant",
            "virtual assistant admin",
            "hire executive assistant philippines",
            "remote virtual executive assistant",
            "philippines executive assistant",
        ],
    ),
    (
        "VC_US_S_ROLES",
        "Digital_Marketing_Hire_PH",
        "/us/digital-marketing",
        [
            "digital marketing virtual assistant",
            "marketing virtual assistant",
            "remote marketing assistant",
            "virtual marketing assistant",
            "marketing virtual assistants",
            "digital marketing assistant",
            "hire digital marketing virtual assistant",
            "filipino marketing virtual assistant",
            "philippines digital marketing assistant",
            "campaign virtual assistant",
            "seo virtual assistant philippines",
            "content marketing virtual assistant",
        ],
    ),
    (
        "VC_US_S_ROLES",
        "Real_Estate_Hire_PH",
        "/us/real-estate",
        [
            "real estate virtual assistant",
            "real estate virtual assistants",
            "hire real estate virtual assistant",
            "real estate admin virtual assistant",
            "real estate administrative assistant",
            "transaction coordinator virtual assistant",
            "real estate transaction coordinator virtual assistant",
            "property management virtual assistant",
            "listing virtual assistant",
            "real estate crm virtual assistant",
            "hire real estate va",
            "filipino real estate virtual assistant",
        ],
    ),
]

REJECT = {
    "virtual assistant",
    "virtual assistants",
    "companies that hire remote workers",
    "customer service representative",
    "virtual assistant companies hiring",
    "what is a virtual assistant",
    "what is virtual assistance",
    "appointment setter from home",
    "va appointment setter",
    "virtual assistant cold calling",
}

JOBISH = (
    " job",
    "jobs",
    "salary",
    "career",
    "careers",
    "resume",
    "work from home",
    "from home",
    "hiring",
    "what is",
    "wfh",
)


def ok(term: str) -> bool:
    t = term.strip().lower()
    if not t or t in REJECT:
        return False
    if t in {"virtual assistant", "virtual assistants"}:
        return False
    if any(bad in f" {t} " for bad in (" jobs ", " job ", " salary ", " career ", " careers ")):
        return False
    if "work from home" in t or t.endswith(" hiring"):
        return False
    if t.startswith("what is"):
        return False
    if "appointment setter" in t:
        return False
    if "brand" in t and "virtual coworker" in t:
        return False
    words = t.split()
    if len(words) < 2:
        return False
    return True


def empty_row() -> dict[str, str]:
    return {k: "" for k in HEADER}


def main() -> None:
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    ags_written: set[str] = set()

    for campaign, ag, path, kws in CLUSTERS:
        new_ag = ag == "Real_Estate_Hire_PH"
        if new_ag and ag not in ags_written:
            row = empty_row()
            row.update(
                {
                    "Account": ACCOUNT,
                    "Row Type": "Ad group",
                    "Campaign": campaign,
                    "Campaign Type": "Search",
                    "Networks": "Google Search",
                    "Languages": "en",
                    "Location options": "Presence",
                    "Ad Group": ag,
                    "Ad Group Status": "Paused",
                    "Comment": (
                        "NEW Paused AG · Exact only · Final URL "
                        f"{HOST}{path} · do not enable until George Posts · no Brand"
                    ),
                }
            )
            rows.append(row)
            ags_written.add(ag)

        for kw in kws:
            if not ok(kw):
                continue
            key = (campaign, ag, kw.lower())
            if key in seen:
                continue
            seen.add(key)
            row = empty_row()
            risk = "medium"
            if ag in {"Bookkeeping_Hire_PH", "Digital_Marketing_Hire_PH", "Real_Estate_Hire_PH"}:
                risk = "low"
            if ag in {"Hire_VA_PH", "Customer_Service_Hire_PH", "Administration_EA_PH"}:
                risk = "medium"
            row.update(
                {
                    "Account": ACCOUNT,
                    "Row Type": "Keyword",
                    "Campaign": campaign,
                    "Campaign Type": "Search",
                    "Budget type": "Daily",
                    "Bid Strategy Type": "Maximize Clicks",
                    "Networks": "Google Search",
                    "Languages": "en",
                    "Location options": "Presence",
                    "Ad Group": ag,
                    "Keyword": kw,
                    "Criterion Type": "Exact",
                    "Keyword Status": "Paused",
                    "Final URL": f"{HOST}{path}",
                    "Comment": f"{COMMENT} · {ag} → {path} · job-seeker risk {risk}",
                }
            )
            rows.append(row)

    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    n_kw = sum(1 for r in rows if r["Row Type"] == "Keyword")
    n_ag = len({r["Ad Group"] for r in rows if r["Row Type"] == "Keyword"})
    n_new = sum(1 for r in rows if r["Row Type"] == "Ad group")
    print(f"wrote {OUT}")
    print(f"keyword rows {n_kw}")
    print(f"ad groups {n_ag}")
    print(f"new ad group rows {n_new}")


if __name__ == "__main__":
    main()
