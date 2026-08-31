#!/usr/bin/env python3
"""Build ADD-only Google Ads Editor CSV: new human RSAs for US ROLES AGs.

Live-US-safe:
- Campaign Status / Budget / Ad Group Status blank (do not rewrite live campaigns)
- New RSAs ship Paused (George enables after review)
- No Brand. No keywords. No Ads API. No DKI.
- No VA / EA / PH / SMM / TA / CS / HR / WFH abbreviations in ad copy.
- $8 only on the admin LP (already states typical admin rate).

Merges Administration_EA_PH from build_rsa_admin_rewrite_us.py (do not duplicate
that CSV on import). One new RSA per other VC_US_S_ROLES AG that still only has
the old abbreviated / DKI set.

CORE AGs skipped: they already have enabled RSAs (some are winners).
Admin_City_Test skipped: geo DKI test already has an RSA.

Usage:
  python3 ads-launch/build_rsa_human_add_us.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_rsa_admin_rewrite_us import (  # noqa: E402
    HEADERS,
    HOST,
    US,
    RSAS as ADMIN_RSAS,
)

OUT_CSV = HERE / "google-ads-editor-rsa-add-human-us.csv"
PUNCT_FIX_CSV = HERE / "google-ads-editor-rsa-add-human-us-punct-fix.csv"
# Extra ? in a description while a headline already has one. The 3 densest
# (headline ? + description ? + two "X. Y." headlines) plus 3 more with the
# same double-? trap so one re-import clears every Editor punctuation red.
PUNCT_FIX_LABELS = (
    "accounting_hire",
    "bookkeeping_hire",
    "social_media_hire",
    "executive_assistant",
    "virtual_assistant",
    "appointment_setter",
)

ABBREV_RE = re.compile(
    r"\b(EA|VA|PH|RSA|DKI|SMM|WFH|CRM|TA|CS|HR)\b", re.IGNORECASE
)
DKI_RE = re.compile(r"\{(KeyWord|KEYWORD|Location|LOCATION)", re.IGNORECASE)

ADMIN_AG = "Administration_EA_PH"
ADMIN_LP = f"{HOST}/us/administrative-support"


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
        if DKI_RE.search(h):
            raise SystemExit(f"{where}: DKI not allowed: {h}")
        if ABBREV_RE.search(h):
            raise SystemExit(f"{where}: abbreviation in headline: {h}")
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: description too long ({len(d)}): {d}")
        if DKI_RE.search(d):
            raise SystemExit(f"{where}: DKI not allowed: {d}")
        if ABBREV_RE.search(d):
            raise SystemExit(f"{where}: abbreviation in description: {d}")
    blob = " ".join(headlines + descs)
    if blob.count("!") > 1:
        raise SystemExit(f"{where}: more than one ! in the ad (Editor punctuation red)")
    if blob.count("?") > 1:
        raise SystemExit(f"{where}: more than one ? in the ad (Editor punctuation red)")
    if "!" in blob and "?" in blob:
        raise SystemExit(f"{where}: ! and ? in the same ad (Editor punctuation red)")
    for ch, name in (
        ("\u2014", "em dash"),
        ("\u2013", "en dash"),
        ("\u2026", "ellipsis"),
        ("...", "ellipsis"),
        ("\u2018", "curly quote"),
        ("\u2019", "curly quote"),
        ("\u201c", "curly quote"),
        ("\u201d", "curly quote"),
        ("\u00a0", "nbsp"),
    ):
        if ch in blob:
            raise SystemExit(f"{where}: forbidden {name} in RSA copy")


# One RSA per remaining ROLES AG. Voice matches live role LPs:
# dedicated Filipino teammate, you interview, payroll handled,
# Book a Free Strategy Call, US hours. No marketplace / job-board framing.
ROLE_RSAS: list[dict] = [
    {
        "label": "accounting_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Accounting_Hire_PH",
        "final_url": f"{HOST}/us/accounting",
        "path1": "accounting",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Month-End Piling Up?",
            "Dedicated Accounting Seat",
            "Filipino Accounting Support",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Reporting Prep Support",
            "Not Freelance Accounting",
            "You Pick Who Joins",
            "We Recruit. You Decide.",
            "Keep Month-End Moving",
            "Extra Close Capacity",
            "Not Licensed Advice",
            "Talk Through the Role",
        ],
        "descs": [
            "Month-end piling up. Hire dedicated Filipino accounting support on your hours.",
            "Book a free strategy call. We shortlist. You interview. We handle payroll.",
            "Extra capacity for transactions, schedules, and reporting prep - not licensed advice.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "accounting_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Accounting_Outsource_PH",
        "final_url": f"{HOST}/us/accounting",
        "path1": "outsource",
        "path2": "finance",
        "allow_8": False,
        "headlines": [
            "Outsource Accounting Work",
            "Dedicated Finance Seat",
            "On Your Close Calendar",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Filipino Accounting Help",
            "Not Rotating Freelancers",
            "We Find Them. You Pick.",
            "Keep Month-End Moving",
            "Outsource Recurring Work",
            "Dedicated Not a Bench",
            "On Your US Hours",
            "You Keep Hire Control",
            "Talk Offshore Accounting",
        ],
        "descs": [
            "Outsource recurring accounting support to a dedicated Filipino teammate.",
            "Free strategy call. We shortlist. You interview. We handle payroll after you hire.",
            "Help with transactions, schedules, and reporting prep - not licensed advice.",
            "Dedicated seat continuity. You keep hire control before anyone starts.",
        ],
    },
    {
        "label": "bookkeeping_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Hire_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "books",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Invoices Stacking Up?",
            "Dedicated Filipino Bookkeeper",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Reconciliations Covered",
            "Not Freelance Bookkeeping",
            "You Pick Your Bookkeeper",
            "We Recruit. You Decide.",
            "Day-to-Day Books Owner",
            "Hire Bookkeeping Capacity",
            "Your Finance Owner Breathes",
            "One Person for the Books",
            "Skip the Marketplace Hunt",
        ],
        "descs": [
            "Invoices stacking up. Hire a dedicated Filipino bookkeeper on your hours.",
            "Book a free strategy call. We recruit. You interview. We handle payroll.",
            "A dedicated books seat owns day-to-day support - not a freelance marketplace.",
            "Your finance owner spends less time catching up. You pick who joins.",
        ],
    },
    {
        "label": "bookkeeping_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Outsource_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "outsource",
        "path2": "books",
        "allow_8": False,
        "headlines": [
            "Outsource the Bookkeeping",
            "Dedicated Books Seat",
            "On Your Finance Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Invoices Stop Waiting",
            "Not Rotating Bookkeepers",
            "Filipino Books Support",
            "We Find. You Choose.",
            "Outsource Routine Books",
            "Dedicated Not Freelance",
            "On Your US Hours",
            "You Keep Hire Control",
            "Talk Through the Books",
        ],
        "descs": [
            "Outsource day-to-day bookkeeping to a dedicated Filipino teammate.",
            "Free strategy call. We shortlist. You interview. We handle payroll after you hire.",
            "Invoices, records, and reconciliations stop stacking on your desk.",
            "Dedicated books seat - continuity, not rotating freelance help.",
        ],
    },
    {
        "label": "customer_service_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Customer_Service_Hire_PH",
        "final_url": f"{HOST}/us/customer-service",
        "path1": "support",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Customers Waiting Too Long",
            "Dedicated Support Teammate",
            "On Your Support Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Queue Stops Building",
            "Not Freelance Support",
            "You Pick Who Answers",
            "Filipino Support Seat",
            "Brand Sounds Looked After",
            "Hire Support Capacity",
            "We Recruit. You Decide.",
            "On Your US Hours",
            "Tickets Stop Piling Up",
        ],
        "descs": [
            "Customers waiting too long? Add a dedicated Filipino support seat on your hours.",
            "Book a free strategy call. We shortlist. You interview before anyone joins.",
            "Dedicated support for inquiries, tickets, and status updates. We handle payroll.",
            "More consistent customer communication. You pick who answers.",
        ],
    },
    {
        "label": "customer_service_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Customer_Service_Outsource_PH",
        "final_url": f"{HOST}/us/customer-service",
        "path1": "outsource",
        "path2": "support",
        "allow_8": False,
        "headlines": [
            "Outsource Customer Support",
            "Dedicated Support Seat",
            "On Your Customer Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Tickets Stop Piling Up",
            "Not Rotating Support Gigs",
            "Filipino Support Team",
            "We Find Them. You Pick.",
            "Outsource the Queue",
            "Coverage Without Chaos",
            "On Your US Hours",
            "You Keep Hire Control",
            "Questions Get Answered",
        ],
        "descs": [
            "Outsource customer service to a dedicated Filipino teammate on your hours.",
            "Free strategy call. We recruit. You interview. We handle payroll after you hire.",
            "Inquiries, tickets, and status updates stop sitting unanswered.",
            "Dedicated support seat - not rotating freelance gigs. You pick who joins.",
        ],
    },
    {
        "label": "digital_marketing_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Digital_Marketing_Hire_PH",
        "final_url": f"{HOST}/us/digital-marketing",
        "path1": "marketing",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Your Marketing Is Stalled",
            "Dedicated Filipino Marketer",
            "On Your US Hours",
            "You Interview Marketers",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Campaigns Stop Slipping",
            "Not Freelance Marketing",
            "You Pick the Marketer",
            "We Recruit. You Decide.",
            "Keep the Machine Moving",
            "Hire Marketing Capacity",
            "Day-to-Day Marketing Owner",
            "Strategists Stay on Strategy",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Campaigns, reporting, and content work stall without an owner. Hire dedicated help.",
            "Book a free strategy call. We shortlist Filipino marketers. You interview first.",
            "Dedicated marketing seat on your hours - we handle payroll after you hire.",
            "Strategists stay on judgment work. We recruit the day-to-day owner.",
        ],
    },
    {
        "label": "digital_marketing_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Digital_Marketing_Outsource_PH",
        "final_url": f"{HOST}/us/digital-marketing",
        "path1": "outsource",
        "path2": "marketing",
        "allow_8": False,
        "headlines": [
            "Outsource Marketing Work",
            "Dedicated Marketing Seat",
            "On Your Hours Offshore",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Marketing Work Continuity",
            "Not Rotating Freelancers",
            "Filipino Marketing Team",
            "We Find Them. You Pick.",
            "Keep Campaigns Moving",
            "Outsource Without Chaos",
            "On Your US Hours",
            "You Keep Hire Control",
            "Content Stops Stalling",
        ],
        "descs": [
            "Outsource digital marketing support to a dedicated Filipino teammate.",
            "Free strategy call. We shortlist. You interview. We handle payroll after you hire.",
            "Day-to-day campaign, content, and reporting capacity - you keep hire control.",
            "Not a freelance bench. Dedicated marketing seat on your hours.",
        ],
    },
    {
        "label": "social_media_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Hire_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "social",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Brand Going Quiet?",
            "Dedicated Social Teammate",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Channels Stay Active",
            "Not Gig Social Posting",
            "You Pick Who Posts",
            "Filipino Social Manager",
            "Stop the Content Firefight",
            "Hire Social Capacity",
            "We Recruit. You Decide.",
            "Replies Stop Falling Behind",
            "One Person Owns Channels",
        ],
        "descs": [
            "Brand going quiet. Hire a dedicated Filipino social teammate on your hours.",
            "Book a free strategy call. We shortlist. You interview before anyone joins.",
            "Dedicated social seat. We handle payroll after you hire.",
            "Channels stay active without turning your week into a content firefight.",
        ],
    },
    {
        "label": "social_media_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Outsource_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "outsource",
        "path2": "social",
        "allow_8": False,
        "headlines": [
            "Outsource Social Media",
            "Dedicated Social Seat",
            "On Your Brand Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Posting Stops Falling Behind",
            "Not Freelance Social",
            "Filipino Social Seat",
            "We Find. You Choose.",
            "Community Replies Covered",
            "Channels Don't Go Quiet",
            "On Your US Hours",
            "You Keep Hire Control",
            "Outsource the Channels",
        ],
        "descs": [
            "Outsource social media work to a dedicated Filipino teammate - not gig posters.",
            "Free strategy call. We recruit. You interview. We handle payroll after you hire.",
            "Scheduling, community replies, and asset coordination on your hours.",
            "You pick who owns the channels. No obligation from the first conversation.",
        ],
    },
    {
        "label": "hr_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Human_Resources_Hire_PH",
        "final_url": f"{HOST}/us/hr",
        "path1": "people",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "People Admin Stacking Up",
            "Dedicated People Support",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Onboarding Stops Stalling",
            "Not Freelance People Help",
            "You Pick Your People Seat",
            "Filipino People Teammate",
            "Managers Get Time Back",
            "Hire People Capacity",
            "We Recruit. You Decide.",
            "Records and Checklists",
            "Human Resources Support",
        ],
        "descs": [
            "People admin stacking up? Hire dedicated Filipino human resources support.",
            "Book a free strategy call. We shortlist. You interview - businesses only.",
            "Records, checklists, and interview scheduling on your hours. We handle payroll.",
            "Managers stop being the default admin desk. You pick who joins.",
        ],
    },
    {
        "label": "hr_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Human_Resources_Outsource_PH",
        "final_url": f"{HOST}/us/hr",
        "path1": "outsource",
        "path2": "people",
        "allow_8": False,
        "headlines": [
            "Outsource People Admin",
            "Dedicated People Seat",
            "On Your People Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Records and Checklists",
            "Not Rotating People Gigs",
            "Filipino People Support",
            "We Find. You Choose.",
            "Outsource Onboarding Work",
            "Leaders Run the Business",
            "On Your US Hours",
            "You Keep Hire Control",
            "Human Resources Capacity",
        ],
        "descs": [
            "Outsource human resources administration to a dedicated Filipino teammate.",
            "Free strategy call. We recruit. You interview. We handle payroll after you hire.",
            "Onboarding checklists, records, and scheduling stop defaulting to managers.",
            "Dedicated people-support seat - businesses only. You keep hire control.",
        ],
    },
    {
        "label": "recruitment_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Recruitment_Hire_PH",
        "final_url": f"{HOST}/us/recruitment",
        "path1": "recruit",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Hiring Pipeline Slowing",
            "Dedicated Recruiting Help",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Screens Stop Stalling",
            "Not a Job Board Hire",
            "You Pick Your Recruiting Seat",
            "Filipino Recruiting Help",
            "Managers Just Decide",
            "Hire Recruiting Support",
            "We Recruit. You Decide.",
            "Calendars Stop Eating You",
            "You Keep Final Decisions",
        ],
        "descs": [
            "Hiring pipeline slowing? Hire dedicated Filipino recruiting support.",
            "Book a free strategy call. We shortlist. You interview before anyone joins.",
            "Dedicated recruiting seat on your hours. We handle payroll after you hire.",
            "Hiring managers spend time deciding - not chasing calendars. Businesses only.",
        ],
    },
    {
        "label": "recruitment_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Recruitment_Outsource_PH",
        "final_url": f"{HOST}/us/recruitment",
        "path1": "outsource",
        "path2": "recruit",
        "allow_8": False,
        "headlines": [
            "Outsource Recruiting Work",
            "Dedicated Recruiting Seat",
            "On Your Hiring Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Calendar Chasing Stops",
            "Not Freelance Recruiting",
            "Filipino Recruiting Help",
            "We Find Them. You Pick.",
            "Outsource Sourcing Work",
            "Pipeline Hygiene Covered",
            "On Your US Hours",
            "You Keep Hire Control",
            "Staffing Not a Job Board",
        ],
        "descs": [
            "Outsource sourcing, screens, and interview coordination to a dedicated seat.",
            "Free strategy call. We shortlist. You interview. We handle payroll after you hire.",
            "Your hiring managers spend time deciding - not chasing resumes and calendars.",
            "Staffing partner for businesses hiring recruiting support - not a job board.",
        ],
    },
    {
        "label": "sales_hire",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Sales_Hire_PH",
        "final_url": f"{HOST}/us/sales",
        "path1": "sales",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Follow-Ups Keep Slipping",
            "Dedicated Sales Support",
            "On Your Sales Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Pipeline Basics Covered",
            "Not Freelance Sales Gigs",
            "You Pick Your Setter",
            "Filipino Sales Teammate",
            "Sellers Talk to Buyers",
            "Hire Sales Capacity",
            "We Recruit. You Decide.",
            "On Your US Hours",
            "Research Stops Slipping",
        ],
        "descs": [
            "Follow-ups slipping? Hire dedicated Filipino sales support on your hours.",
            "Book a free strategy call. We shortlist. You interview before they join.",
            "Dedicated setter or sales-support seat. We handle payroll after you hire.",
            "Sellers spend more time talking to buyers. Staffing - not a job board.",
        ],
    },
    {
        "label": "sales_outsource",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Sales_Outsource_PH",
        "final_url": f"{HOST}/us/sales",
        "path1": "outsource",
        "path2": "sales",
        "allow_8": False,
        "headlines": [
            "Outsource Sales Support",
            "Dedicated Setter Seat",
            "On Your Pipeline Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Follow-Ups Stop Slipping",
            "Not Rotating Freelancers",
            "Filipino Sales Support",
            "We Find Them. You Pick.",
            "Outsource Follow-Ups",
            "Protect the Pipeline",
            "On Your US Hours",
            "You Keep Hire Control",
            "Closers Stay on Closers",
        ],
        "descs": [
            "Outsource appointment setting and sales support to a dedicated Filipino seat.",
            "Free strategy call. We recruit. You interview. We handle payroll after you hire.",
            "Research and follow-ups stop slipping while closers stay buried.",
            "Sellers talk to buyers. You pick who joins. Staffing partner - not a job board.",
        ],
    },
    {
        "label": "appointment_setter",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Appointment_Setter_Hire_PH",
        "final_url": f"{HOST}/us/sales",
        "path1": "sales",
        "path2": "setter",
        "allow_8": False,
        "headlines": [
            "Calendar Still Empty?",
            "Dedicated Filipino Setter",
            "On Your Sales Hours",
            "You Interview Your Setter",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Booked Conversations",
            "Not a Work-From-Home Ad",
            "You Pick Who Sets",
            "They Watch the Pipeline",
            "Hire Without US Overhead",
            "Appointment Setting Help",
            "We Recruit. You Decide.",
            "On Your US Hours",
            "Employers Hiring Setters",
        ],
        "descs": [
            "Need an appointment setter without another US full-time hire. Dedicated Filipino seat.",
            "Book a free strategy call. We shortlist. You interview before anyone joins.",
            "On your hours. We handle payroll. You pick who books the conversations.",
            "For employers hiring setters - not candidates looking for remote jobs.",
        ],
    },
]


def assert_copy_rules(rsa: dict) -> None:
    ag = rsa["ad_group"]
    blob = " ".join(rsa["headlines"] + rsa["descs"])
    low = blob.lower()
    if any(w in low for w in ("fuck", "shit", "desperate", "fortune 500", "fortune500")):
        raise SystemExit(f"{ag}: forbidden tone/claim")
    if rsa.get("allow_8"):
        if "$8" not in blob:
            raise SystemExit(f"{ag}: expected $8 on admin LP RSA")
        if "~$8" in blob:
            raise SystemExit(f"{ag}: tilde $8 is PROHIBITED")
    else:
        if "$8" in blob:
            raise SystemExit(f"{ag}: do not put $8 on this LP ({rsa['final_url']})")
    for p in (rsa["path1"], rsa["path2"]):
        if len(p) > 15:
            raise SystemExit(f"{ag}: path too long ({len(p)}): {p}")
        if ABBREV_RE.search(p):
            raise SystemExit(f"{ag}: abbreviation in path: {p}")
    if not rsa["final_url"].startswith(f"{HOST}/us"):
        raise SystemExit(f"{ag}: Final URL must be a live /us LP")


def append_rsa(rows: list[dict[str, str]], rsa: dict) -> None:
    where = f"{rsa['campaign']}/{rsa['ad_group']}/{rsa['label']}"
    validate_rsa(rsa["headlines"], rsa["descs"], where)
    assert_copy_rules(rsa)
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad",
            "Campaign": rsa["campaign"],
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": rsa["ad_group"],
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": rsa["final_url"],
            "Path 1": rsa["path1"],
            "Path 2": rsa["path2"],
            "Comment": (
                "Human RSA add 2026-08-12; Paused; Campaign Status blank "
                "(live-US-safe); no abbreviations; no DKI; "
                f"angle={rsa['label']}"
            ),
        }
    )
    for i, h in enumerate(rsa["headlines"], 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(rsa["descs"], 1):
        r[f"Description {i}"] = d
    rows.append(r)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    combined: list[dict] = []
    for rsa in ADMIN_RSAS:
        item = dict(rsa)
        item["allow_8"] = True
        combined.append(item)
    combined.extend(ROLE_RSAS)

    keys = [(x["campaign"], x["ad_group"], x["label"]) for x in combined]
    if len(set(keys)) != len(keys):
        raise SystemExit("duplicate campaign/ad_group/label")

    rows: list[dict[str, str]] = []
    for rsa in combined:
        append_rsa(rows, rsa)

    write_csv(OUT_CSV, rows)
    punct_rows = [
        r
        for r, rsa in zip(rows, combined)
        if rsa["label"] in PUNCT_FIX_LABELS
    ]
    if len(punct_rows) != 6:
        raise SystemExit(f"punct-fix CSV expected 6 rows, got {len(punct_rows)}")
    write_csv(PUNCT_FIX_CSV, punct_rows)

    by_ag: dict[str, int] = {}
    by_lp: dict[str, list[str]] = {}
    for rsa in combined:
        by_ag[rsa["ad_group"]] = by_ag.get(rsa["ad_group"], 0) + 1
        lp = rsa["final_url"].replace(HOST, "")
        if rsa["ad_group"] not in by_lp.get(lp, []):
            by_lp.setdefault(lp, []).append(rsa["ad_group"])

    print(f"Wrote {OUT_CSV}")
    print(f"Wrote {PUNCT_FIX_CSV} ({len(punct_rows)} punctuation-fix ads)")
    print(f"  RSAs={len(rows)} · AGs={len(by_ag)} · all Paused")
    print("  Campaign Status blank · Brand excluded · no negatives")
    print("  Admin ads merged from build_rsa_admin_rewrite_us.py (do not also import that CSV)")
    for ag, n in by_ag.items():
        print(f"  {ag}: {n} RSA(s)")
    print("  LPs:")
    for lp, ags in by_lp.items():
        print(f"    {lp}: {', '.join(ags)}")


if __name__ == "__main__":
    main()
