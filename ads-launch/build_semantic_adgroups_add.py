#!/usr/bin/env python3
"""Build ADD-only Google Ads Editor CSV for new US semantic Exact ad groups.

Live-US-safe:
- Does NOT touch campaign status/budget (Campaign Status blank on child rows)
- New ad groups ship Paused (George enables after review)
- Exact match only (Phrase later)
- No campaign negatives in this file (prevents Unkown/Broad dual-write)
- Companion pause-dupes CSV pauses overlapping Exact keywords in old AGs

Usage:
  python3 ads-launch/build_semantic_adgroups_add.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
ADD_CSV = OUT_DIR / "google-ads-editor-semantic-adgroups-add-us.csv"
PAUSE_CSV = OUT_DIR / "google-ads-editor-semantic-adgroups-pause-dupes-us.csv"
US = "496-715-1855"
HOST = "https://www.virtualcoworker.app"

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
        # Keyword insertion pin can exceed 30 in Editor; pin text after colon must fit.
        body = h
        if h.startswith("{KeyWord:") and h.endswith("}"):
            body = h[len("{KeyWord:") : -1]
        if len(body) > 30:
            raise SystemExit(f"{where}: headline too long ({len(body)}): {h}")
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: description too long ({len(d)}): {d}")


# Evidence: LAST_7_DAYS search_term_view pull 2026-08-09 (_last7_search_terms.json)
# Clusters with employer language that were leaking into Hire_VA_PH / wrong role AGs.
AD_GROUPS: list[dict] = [
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "Staffing_Agency_PH",
        "final_url": f"{HOST}/us",
        "hypothesis": (
            "Employers shopping a remote/offshore staffing agency deserve "
            "agency RSAs + Exact family, not generic hire-VA copy."
        ),
        "evidence": "remote staffing agency/agencies ~$15 / 6 clicks / 32 impr (7d)",
        "keywords": [
            "remote staffing agency",
            "remote staffing agencies",
            "virtual staffing agency",
            "offshore staffing agency",
            "philippines staffing agency",
            "filipino staffing agency",
            "remote staffing company",
            "offshore staffing company",
            "philippines staffing company",
            "virtual assistant staffing agency",
            "philippines remote staffing agency",
            "philippines virtual staffing agency",
            "staffing firm philippines",
            "online staffing agency",
        ],
        "rsas": [
            {
                "angle": "agency",
                "path1": "staffing",
                "path2": "agency",
                "headlines": [
                    "Remote Staffing Agency",
                    "Philippines Staffing Agency",
                    "Hire Remote Staff PH",
                    "Offshore Staffing Partner",
                    "US Employer Staffing",
                    "Dedicated Remote Seats",
                    "Vetted Filipino Staff",
                    "Interview Before Hire",
                    "Not a Gig Marketplace",
                    "Staffing Not Job Board",
                    "Build Your PH Team",
                    "Remote Ops Capacity",
                    "Clear Employer Process",
                    "Talk to a Specialist",
                    "{KeyWord:Remote Staffing Agency}",
                ],
                "descs": [
                    "Philippines remote staffing for US businesses that need dedicated seats.",
                    "We recruit and screen. You interview the shortlist before anyone joins.",
                    "Staffing partner model — not freelance gigs or a job board.",
                    "For employers only. An inquiry is not a hire or placement.",
                ],
            },
            {
                "angle": "offshore_team",
                "path1": "offshore",
                "path2": "staff",
                "headlines": [
                    "Build Offshore Staff Team",
                    "Philippines Remote Team",
                    "Offshore Staffing Agency",
                    "Filipino Staffing Partner",
                    "Dedicated Seat Staffing",
                    "Screened PH Finalists",
                    "You Keep Hire Control",
                    "Not Upwork Staffing",
                    "US Hours Remote Staff",
                    "Staff Agency for SMBs",
                    "Skip DIY Recruiting",
                    "Remote Team From PH",
                    "Employer Staffing Path",
                    "Request Staff Options",
                    "{KeyWord:Offshore Staffing Agency}",
                ],
                "descs": [
                    "Need offshore staff without building your own PH recruiting desk?",
                    "Tell us the roles. We shortlist vetted Filipino professionals.",
                    "Dedicated teammates for US ops — continuity, not rotating freelancers.",
                    "Businesses only. We do not place job seekers from this form.",
                ],
            },
            {
                "angle": "risk_reduce",
                "path1": "hire",
                "path2": "staff",
                "headlines": [
                    "Staff Without Hiring Risk",
                    "Vetted Remote Staff PH",
                    "Shortlist Then Interview",
                    "Philippines Hire Support",
                    "Staffing Specialist Path",
                    "Remote Staff Pre-Screened",
                    "No Job Board Hunting",
                    "Employer Screening First",
                    "PH Talent With Support",
                    "Hire Capacity Faster",
                    "Clear Next Staff Step",
                    "Dedicated Not Freelance",
                    "US Business Staffing",
                    "Get Staffing Options",
                    "{KeyWord:Philippines Staffing Agency}",
                ],
                "descs": [
                    "Reduce hiring risk: we recruit and vet; you interview before placement.",
                    "Remote staffing agency path for US managers who need capacity now.",
                    "Dedicated Philippines seats with a staffing partner — not DIY ads.",
                    "Speak with a specialist. No obligation from a first conversation.",
                ],
            },
        ],
    },
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "VA_Agency_Firm_PH",
        "final_url": f"{HOST}/us",
        "hypothesis": (
            "VA agency/firm/company queries are provider-shopping; "
            "message-match beats generic hire-VA RSA language."
        ),
        "evidence": "virtual assistant agency (+usa) impressions; agency-intent spine",
        "keywords": [
            "virtual assistant agency",
            "virtual assistant agencies",
            "virtual assistant firm",
            "virtual assistant company",
            "va agency",
            "va firm",
            "va company",
            "philippines virtual assistant agency",
            "filipino virtual assistant agency",
            "philippines va agency",
            "filipino va agency",
            "virtual assistant agency philippines",
            "philippines virtual assistant firm",
            "filipino virtual assistant firm",
            "virtual assistant outsourcing agency",
            "dedicated virtual assistant agency",
            "hire virtual assistant agency",
            "virtual assistant company philippines",
        ],
        "rsas": [
            {
                "angle": "agency",
                "path1": "va",
                "path2": "agency",
                "headlines": [
                    "Virtual Assistant Agency",
                    "Philippines VA Agency",
                    "Filipino VA Firm",
                    "VA Company for US Biz",
                    "Hire Through a VA Agency",
                    "Dedicated VA Seats",
                    "Vetted VA Shortlist",
                    "Interview VA Finalists",
                    "Not a VA Marketplace",
                    "Staffing VA Partner",
                    "Employer VA Agency",
                    "Skip DIY VA Hiring",
                    "US Hours VA Support",
                    "Talk VA Staffing",
                    "{KeyWord:Virtual Assistant Agency}",
                ],
                "descs": [
                    "Looking for a VA agency? Hire dedicated Philippines talent for US work.",
                    "We recruit and screen Filipino VAs — you interview before anyone joins.",
                    "Agency staffing model for businesses — not freelance task gigs.",
                    "Employers only. An accepted form is not a hire or placement.",
                ],
            },
            {
                "angle": "firm_quality",
                "path1": "va",
                "path2": "firm",
                "headlines": [
                    "VA Firm Philippines",
                    "Quality Filipino VAs",
                    "Screened VA Candidates",
                    "VA Agency Not Gig App",
                    "Dedicated Remote VA",
                    "Business VA Partner",
                    "You Decide Who Joins",
                    "PH VA Recruiting Desk",
                    "Managed VA Staffing",
                    "Clear VA Hire Path",
                    "Remote VA Continuity",
                    "Not Job Board VA Hire",
                    "Request VA Options",
                    "US Employer VA Firm",
                    "{KeyWord:Virtual Assistant Firm}",
                ],
                "descs": [
                    "A VA firm path: role brief → vetted shortlist → you interview.",
                    "Filipino virtual assistants for US businesses that want dedicated seats.",
                    "We handle recruiting and screening. You keep hire authority.",
                    "For established businesses — not candidates searching for VA jobs.",
                ],
            },
            {
                "angle": "simplicity",
                "path1": "hire",
                "path2": "va",
                "headlines": [
                    "Simple VA Agency Path",
                    "Tell Us the VA Role",
                    "Get VA Candidates Fast",
                    "Filipino VA Shortlist",
                    "Hire VA Without Chaos",
                    "One Dedicated VA Seat",
                    "VA Staffing Specialist",
                    "No Marketplace Sorting",
                    "Employer VA Process",
                    "PH VA Hire Support",
                    "Clear Next VA Step",
                    "VA Options for SMBs",
                    "Interview Then Place",
                    "Start VA Staffing",
                    "{KeyWord:VA Agency}",
                ],
                "descs": [
                    "Need a VA without running your own Philippines recruiting process?",
                    "Share the role. Review screened finalists. Interview who fits.",
                    "Dedicated VA seating with support — simpler than DIY hiring.",
                    "No obligation chat with a staffing specialist after you inquire.",
                ],
            },
        ],
    },
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "Virtual_Staff_PH",
        "final_url": f"{HOST}/us",
        "hypothesis": (
            "virtual staff / virtualstaff language is a distinct employer shorthand "
            "cluster (exclude va workers ph watch term)."
        ),
        "evidence": "virtual staff / virtualstaff ph ~$8.9 / 4 clicks (7d)",
        "keywords": [
            "virtual staff",
            "hire virtual staff",
            "virtual staff philippines",
            "philippines virtual staff",
            "filipino virtual staff",
            "virtual staff ph",
            "hire philippines virtual staff",
            "hire filipino virtual staff",
            "virtual staffing philippines",
            "philippines virtual staffing",
            "dedicated virtual staff",
            "remote virtual staff",
        ],
        "rsas": [
            {
                "angle": "virtual_staff",
                "path1": "virtual",
                "path2": "staff",
                "headlines": [
                    "Hire Virtual Staff PH",
                    "Philippines Virtual Staff",
                    "Filipino Virtual Staff",
                    "Dedicated Virtual Staff",
                    "US Employer Virtual Staff",
                    "Vetted Remote Staff",
                    "Interview Staff Finalists",
                    "Not Freelance Staffing",
                    "Virtual Staff Partner",
                    "Remote Ops From PH",
                    "Clear Staff Hire Path",
                    "Skip DIY Staff Search",
                    "Virtual Staff Shortlist",
                    "Talk Staffing Options",
                    "{KeyWord:Hire Virtual Staff}",
                ],
                "descs": [
                    "Hire Philippines virtual staff for dedicated US business seats.",
                    "We recruit and screen. You interview before anyone joins your team.",
                    "Virtual staffing partner — not a gig board or job marketplace.",
                    "For employers only. Inquiry ≠ hire or placement.",
                ],
            },
            {
                "angle": "capacity",
                "path1": "staff",
                "path2": "ph",
                "headlines": [
                    "Add Virtual Staff Capacity",
                    "PH Virtual Staff Seats",
                    "Remote Staff You Keep",
                    "Screened Filipino Staff",
                    "Virtual Staff Continuity",
                    "Employer Staffing Path",
                    "Not Rotating Freelancers",
                    "US Hours Virtual Staff",
                    "Role Brief to Shortlist",
                    "Virtual Staff Support",
                    "Hire Capacity From PH",
                    "Staffing Not Job Ads",
                    "Get Virtual Staff Help",
                    "Build Remote Capacity",
                    "{KeyWord:Philippines Virtual Staff}",
                ],
                "descs": [
                    "Need virtual staff capacity without US full-time overhead?",
                    "Dedicated Filipino teammates for ongoing work — you keep hire control.",
                    "We shortlist. You interview. Support continues after placement.",
                    "Businesses only — this is not a careers or job-seeker page.",
                ],
            },
            {
                "angle": "partner",
                "path1": "hire",
                "path2": "team",
                "headlines": [
                    "Virtual Staffing Partner",
                    "PH Team Hire Support",
                    "Trusted Remote Staff",
                    "Virtual Staff Specialists",
                    "Employer Hire Process",
                    "Pre-Screened PH Staff",
                    "You Decide Who Joins",
                    "Remote Team Partner",
                    "Clear Next Hire Step",
                    "Staff Without Chaos",
                    "Filipino Staff Pipeline",
                    "Not Marketplace Hiring",
                    "Request Staff Shortlist",
                    "Speak With Specialist",
                    "{KeyWord:Virtual Staff Philippines}",
                ],
                "descs": [
                    "A staffing partner for US managers hiring Philippines virtual staff.",
                    "Tell us who you need. Review vetted finalists. Interview who fits.",
                    "Dedicated seats with continuity — not one-off freelance tasks.",
                    "No obligation from the first conversation with our team.",
                ],
            },
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Appointment_Setter_Hire_PH",
        "final_url": f"{HOST}/us/sales",
        "hypothesis": (
            "Appointment-setter demand is real but polluted by WFH/job queries in "
            "Sales_Hire_PH — isolate employer Exact + sales LP message match."
        ),
        "evidence": "appointment setter cluster ~$18 / 5 clicks; mostly WFH junk mixed in",
        "keywords": [
            "hire appointment setter",
            "hire remote appointment setter",
            "appointment setter philippines",
            "filipino appointment setter",
            "offshore appointment setter",
            "virtual appointment setter",
            "outsourced appointment setter",
            "hire filipino appointment setter",
            "hire appointment setter philippines",
            "remote appointment setter philippines",
            "virtual assistant appointment setter",
            "va appointment setter",
            "appointment setting services philippines",
            "hire outsourced appointment setter",
        ],
        "rsas": [
            {
                "angle": "hire_setter",
                "path1": "sales",
                "path2": "setter",
                "headlines": [
                    "Hire Appointment Setter",
                    "PH Appointment Setter",
                    "Filipino Appointment Setter",
                    "Remote Setter for US Sales",
                    "Offshore Appointment Setter",
                    "Dedicated Setter Seat",
                    "Vetted Sales Support",
                    "Interview Setter Finalists",
                    "Not a Job Board Hire",
                    "Sales Staffing Partner",
                    "US Hours Setter Support",
                    "Skip DIY Setter Hiring",
                    "Clear Setter Hire Path",
                    "Talk Sales Staffing",
                    "{KeyWord:Hire Appointment Setter}",
                ],
                "descs": [
                    "Hire a Philippines appointment setter for US sales follow-up work.",
                    "We recruit and screen. You interview before anyone joins your team.",
                    "For employers hiring setters — not candidates seeking WFH jobs.",
                    "Staffing partner model. An inquiry is not a hire or placement.",
                ],
            },
            {
                "angle": "pipeline",
                "path1": "sales",
                "path2": "hire",
                "headlines": [
                    "Fill Your Setter Seat",
                    "Appointment Setting PH",
                    "Outbound Setter Support",
                    "Sales Pipeline Capacity",
                    "Screened Setter Talent",
                    "Dedicated Not Freelance",
                    "You Keep Hire Control",
                    "PH Sales Support Staff",
                    "Setter Shortlist Fast",
                    "Employer Setter Path",
                    "Remote Sales Capacity",
                    "Not Gig Setter Work",
                    "Request Setter Options",
                    "Build Sales Bandwidth",
                    "{KeyWord:Appointment Setter Philippines}",
                ],
                "descs": [
                    "Need appointment-setting capacity without another US full-time seat?",
                    "Role brief → vetted Filipino shortlist → you interview finalists.",
                    "Dedicated sales support seating — continuity for your pipeline.",
                    "Businesses only. Job seekers should use careers, not this form.",
                ],
            },
            {
                "angle": "risk_reduce",
                "path1": "hire",
                "path2": "sales",
                "headlines": [
                    "Setter Hire With Vetting",
                    "Pre-Screened Sales Staff",
                    "Interview Before Place",
                    "Filipino Sales Support",
                    "Appointment Hire Partner",
                    "Reduce Setter Hire Risk",
                    "Clear Sales Hire Step",
                    "Staffing Not Job Ads",
                    "US Sales Hours Ready",
                    "Offshore Sales Support",
                    "Vetted Remote Setters",
                    "Employer Screening First",
                    "Get Sales Hire Options",
                    "Speak With Specialist",
                    "{KeyWord:Filipino Appointment Setter}",
                ],
                "descs": [
                    "Reduce setter hiring risk: we recruit and vet; you interview.",
                    "Philippines sales support for US teams that need booked conversations.",
                    "Dedicated seat staffing — not rotating freelancers or job boards.",
                    "No obligation from a first talk with a staffing specialist.",
                ],
            },
        ],
    },
]


# Exact keywords to pause in old AGs after the new themed AGs exist (avoid cannibalization).
PAUSE_DUPES: list[tuple[str, str, str]] = [
    # (campaign, old_ad_group, keyword)
    ("VC_US_S_CORE", "Hire_VA_PH", "remote staffing agency"),
    ("VC_US_S_CORE", "Hire_VA_PH", "remote staffing agencies"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual staffing agency"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual staffing firm"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual assistant staffing agency"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual assistant agency"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual assistant firm"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual assistant company"),
    ("VC_US_S_CORE", "Hire_VA_PH", "va agency"),
    ("VC_US_S_CORE", "Hire_VA_PH", "va firm"),
    ("VC_US_S_CORE", "Hire_VA_PH", "virtual assistant outsourcing agency"),
    ("VC_US_S_CORE", "Hire_VA_PH", "dedicated virtual assistant agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "offshore staffing agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines staffing agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "filipino staffing agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines staffing company"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "staffing firm philippines"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines remote staffing agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines virtual staffing agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines virtual assistant agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "filipino virtual assistant agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines va agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "filipino va agency"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "virtual assistant agency philippines"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines virtual assistant firm"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "virtual staff philippines"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "virtual staff ph"),
    ("VC_US_S_CORE", "Offshore_VA_PH", "philippines virtual staffing"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "appointment setter philippines"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "filipino appointment setter"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "virtual appointment setter"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "virtual assistant appointment setter"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "va appointment setter"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "hire appointment setter philippines"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "hire filipino appointment setter"),
    ("VC_US_S_ROLES", "Sales_Hire_PH", "remote appointment setter philippines"),
    ("VC_US_S_ROLES", "Sales_Outsource_PH", "hire outsourced appointment setter"),
]


def append_ad_group(rows: list[dict[str, str]], camp: str, ag: str) -> None:
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad group",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            # Languages blank — VC_* campaigns already use campaign-level
            # location+language targeting; AG-level "en" causes Editor errors.
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Group Status": "Paused",
            "Comment": (
                "Semantic Exact AG add 2026-08-09 · Paused until George enables · "
                "Exact-only; Campaign Status blank on purpose (live-US-safe)"
            ),
        }
    )
    rows.append(r)


def append_keyword(
    rows: list[dict[str, str]], camp: str, ag: str, keyword: str, *, status: str, comment: str
) -> None:
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Keyword",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Keyword": keyword,
            "Criterion Type": "Exact",
            "Keyword Status": status,
            "Comment": comment,
        }
    )
    rows.append(r)


def append_rsa(
    rows: list[dict[str, str]],
    *,
    camp: str,
    ag: str,
    final_url: str,
    path1: str,
    path2: str,
    headlines: list[str],
    descs: list[str],
    angle: str,
) -> None:
    validate_rsa(headlines, descs, f"{camp}/{ag}/{angle}")
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": final_url,
            "Path 1": path1,
            "Path 2": path2,
            "Comment": f"Semantic RSA {angle} 2026-08-09; Exact AG add; Paused",
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    rows.append(r)


def build_add_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for ag in AD_GROUPS:
        append_ad_group(rows, ag["campaign"], ag["ad_group"])
        for kw in ag["keywords"]:
            append_keyword(
                rows,
                ag["campaign"],
                ag["ad_group"],
                kw,
                status="Paused",
                comment=(
                    f"Semantic Exact add → {ag['ad_group']} · {ag['evidence']} · "
                    "Paused until George enables with the new AG"
                ),
            )
        for rsa in ag["rsas"]:
            append_rsa(
                rows,
                camp=ag["campaign"],
                ag=ag["ad_group"],
                final_url=ag["final_url"],
                path1=rsa["path1"],
                path2=rsa["path2"],
                headlines=rsa["headlines"],
                descs=rsa["descs"],
                angle=rsa["angle"],
            )
    return rows


def build_pause_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for camp, ag, kw in PAUSE_DUPES:
        append_keyword(
            rows,
            camp,
            ag,
            kw,
            status="Paused",
            comment=(
                "Pause dupe Exact after semantic AG add 2026-08-09 · "
                "keeps keyword only in themed Exact AG · Campaign/Ad Group Status blank"
            ),
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    add_rows = build_add_rows()
    pause_rows = build_pause_rows()
    write_csv(ADD_CSV, add_rows)
    write_csv(PAUSE_CSV, pause_rows)

    ag_n = sum(1 for r in add_rows if r["Row Type"] == "Ad group")
    kw_n = sum(1 for r in add_rows if r["Row Type"] == "Keyword")
    ad_n = sum(1 for r in add_rows if r["Row Type"] == "Ad")
    print(f"Wrote {ADD_CSV}")
    print(f"  Ad groups={ag_n} Exact keywords={kw_n} RSAs={ad_n} total_rows={len(add_rows)}")
    print(f"Wrote {PAUSE_CSV}")
    print(f"  Pause-dupe Exact rows={len(pause_rows)}")
    print("Landing pages: CORE AGs → /us · Appointment_Setter_Hire_PH → /us/sales")
    print("No new LP required for v1 (reuse existing).")


if __name__ == "__main__":
    main()
