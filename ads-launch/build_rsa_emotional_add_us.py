#!/usr/bin/env python3
"""Build ADD-only Google Ads Editor CSV: 1 emotional RSA per US VC_* ad group.

Live-US-safe:
- Campaign Status / Budget / Ad Group Status blank (do not rewrite live campaigns)
- New RSAs ship Paused (George enables after pausing the worst existing RSA)
- Same Final URL + existing Path 1/2 per AG — no new landing pages
- No Brand. No campaign negatives. No Ads API.

Inventory source: local Editor CSVs only
  ads-launch/google-ads-editor-import-us.csv
  ads-launch/google-ads-editor-semantic-adgroups-add-us.csv

Usage:
  python3 ads-launch/build_rsa_emotional_add_us.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
OUT_CSV = OUT_DIR / "google-ads-editor-rsa-add-emotional-us.csv"
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


def headline_body(h: str) -> str:
    if h.startswith("{KeyWord:") and h.endswith("}"):
        return h[len("{KeyWord:") : -1]
    if h.startswith("{LOCATION(City):") and h.endswith("}"):
        return h[len("{LOCATION(City):") : -1]
    return h


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
        body = headline_body(h)
        if len(body) > 30:
            raise SystemExit(f"{where}: headline too long ({len(body)}): {h}")
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: description too long ({len(d)}): {d}")


# Voice: /us PainGain + sell block. $8 only where LP supports admin rate (/us hub + admin).
# No f-bombs, no "desperate", no Fortune 500, no fake placement counts, no fake scarcity.
RSAS: list[dict] = [
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "Hire_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "hire",
        "path2": "va",
        "allow_8": True,
        "headlines": [
            "Your Week Is Full",
            "Dedicated Filipino VA",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Free Hiring Consult",
            "Admin VA ~$8 an Hour",
            "They Want This Work",
            "Not Another SaaS Tool",
            "Talk to a Specialist",
            "We Recruit. You Decide.",
            "Filipino Teammate Seat",
            "Hire Without Payroll Drag",
            "Nobody Starts Till You Say",
            "{KeyWord:Hire a VA}",
        ],
        "descs": [
            "You don't need another tool. You need a dedicated Filipino teammate on your hours.",
            "Free consult. We recruit. You interview. We handle payroll and paperwork.",
            "Typical admin VA ~$8/hr. Dedicated seat — not a freelance marketplace.",
            "Talk to a specialist. No obligation. You pick who joins your business.",
        ],
    },
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "Offshore_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "offshore",
        "path2": "ph",
        "allow_8": True,
        "headlines": [
            "Offshore Filipino Team",
            "Dedicated PH Teammate",
            "On Your Hours Offshore",
            "You Interview Finalists",
            "We Handle PH Payroll",
            "Free Offshore Consult",
            "Admin Capacity ~$8/hr",
            "Not Freelance Offshore",
            "They Watch Your Back",
            "Talk Offshore Staffing",
            "We Find Them. You Pick.",
            "US Hours From PH",
            "Hire Offshore Without Chaos",
            "Dedicated Not Rotating",
            "{KeyWord:Offshore VA}",
        ],
        "descs": [
            "Dedicated Filipino teammates offshore — on your hours, not rotating freelancers.",
            "Free consult. We recruit in the Philippines. You interview. We handle payroll.",
            "Typical admin VA ~$8/hr. Serious capacity without US payroll weight.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "Staffing_Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "staffing",
        "path2": "agency",
        "allow_8": True,
        "headlines": [
            "Remote Staffing That Fits",
            "Dedicated Filipino Staff",
            "Agency Hire. You Pick.",
            "On Your Business Hours",
            "We Handle the Payroll",
            "Free Staffing Consult",
            "Admin Seats ~$8 an Hour",
            "Not a Gig Staffing App",
            "You Interview the Team",
            "Talk to a Specialist",
            "PH Staffing for US Ops",
            "We Find. You Choose.",
            "Staff Without US Overhead",
            "Employers Only Staffing",
            "{KeyWord:Virtual Staffing Agency}",
        ],
        "descs": [
            "A staffing agency path: dedicated Filipino teammates for US businesses.",
            "Free consult. We recruit and screen. You interview. We handle payroll.",
            "Typical admin capacity ~$8/hr — dedicated seats, not freelance gigs.",
            "You pick who joins your team. No obligation from the first conversation.",
        ],
    },
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "VA_Agency_Firm_PH",
        "final_url": f"{HOST}/us",
        "path1": "va",
        "path2": "agency",
        "allow_8": True,
        "headlines": [
            "VA Agency. You Decide.",
            "Dedicated Filipino VAs",
            "On Your Hours Daily",
            "You Interview Each VA",
            "Payroll Handled for You",
            "Free VA Agency Consult",
            "Admin VA ~$8 an Hour",
            "Firm Not Marketplace",
            "They Want the Seat",
            "Talk VA Staffing",
            "We Recruit. You Pick.",
            "US Hours VA Agency",
            "Hire a VA Without DIY",
            "Clear Your Week Fast",
            "{KeyWord:Filipino VA Agency}",
        ],
        "descs": [
            "Looking for a VA agency? Dedicated Filipino teammates for US work.",
            "Free consult. We recruit and screen. You interview before anyone joins.",
            "Typical admin VA ~$8/hr. Agency staffing — not freelance task gigs.",
            "You decide who joins. Employers only. No obligation from a first talk.",
        ],
    },
    {
        "campaign": "VC_US_S_CORE",
        "ad_group": "Virtual_Staff_PH",
        "final_url": f"{HOST}/us",
        "path1": "virtual",
        "path2": "staff",
        "allow_8": True,
        "headlines": [
            "Virtual Staff You Keep",
            "Dedicated PH Teammates",
            "On Your Clock Daily",
            "You Interview Staff",
            "We Handle Payroll",
            "Free Staff Consult",
            "Admin Staff ~$8/hr",
            "Not Rotating Staff",
            "Your Week Gets Lighter",
            "Talk Virtual Staffing",
            "We Find. You Hire.",
            "Filipino Virtual Staff",
            "Staff Without Headcount",
            "Employers Hire Here",
            "{KeyWord:Dedicated Virtual Staff}",
        ],
        "descs": [
            "Hire Philippines virtual staff — dedicated teammates on your hours.",
            "Free consult. We recruit. You interview. We handle payroll after you hire.",
            "Typical admin staff ~$8/hr. Continuity — not rotating freelance gigs.",
            "You pick who joins your team. Businesses only, not a job board.",
        ],
    },
    {
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
            "Free Marketing Consult",
            "Campaigns Stop Slipping",
            "Not Freelance Marketing",
            "You Pick the Marketer",
            "Talk Marketing Hire",
            "We Recruit. You Decide.",
            "PH Digital Marketing VA",
            "Keep the Machine Moving",
            "Hire Marketing Capacity",
            "{KeyWord:Digital Marketing VA}",
        ],
        "descs": [
            "Campaigns, reporting, and content ops stall without an owner. Hire dedicated help.",
            "Free consult. We shortlist Filipino marketers. You interview before anyone joins.",
            "Dedicated marketing seat on your hours — we handle payroll after you hire.",
            "Strategists stay on judgment work. We recruit the day-to-day owner.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Digital_Marketing_Outsource_PH",
        "final_url": f"{HOST}/us/digital-marketing",
        "path1": "outsource",
        "path2": "mkt",
        "allow_8": False,
        "headlines": [
            "Outsource Marketing PH",
            "Dedicated Marketing Seat",
            "On Your Hours Offshore",
            "You Interview Then Hire",
            "Payroll? We Handle It",
            "Free Outsource Consult",
            "Marketing Ops Continuity",
            "Not Rotating Freelancers",
            "Filipino Marketing Team",
            "Talk Offshore Marketing",
            "We Find Them. You Pick.",
            "PH Marketing Capacity",
            "Outsource Without Chaos",
            "Keep Campaigns Moving",
            "{KeyWord:Outsource Marketing}",
        ],
        "descs": [
            "Outsource digital marketing support to a dedicated Filipino teammate.",
            "Free consult. We shortlist. You interview. We handle payroll after you hire.",
            "Day-to-day campaign, content, and reporting capacity — you keep hire control.",
            "Not a freelance bench. Dedicated marketing seat on your hours.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Hire_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "social",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Brand Going Quiet?",
            "Dedicated Social VA",
            "On Your Hours Social",
            "You Interview SMM",
            "We Handle Payroll",
            "Free Social Consult",
            "Channels Stay Active",
            "Not Gig Social Posting",
            "You Pick Your SMM",
            "Talk Social Hire",
            "Filipino Social Manager",
            "Stop the Content Firefight",
            "Hire Social Capacity",
            "We Recruit. You Decide.",
            "{KeyWord:Hire Social Manager}",
        ],
        "descs": [
            "Posting and replies falling behind? Hire a dedicated Filipino social teammate.",
            "Free consult. We shortlist. You interview before anyone joins your brand.",
            "Dedicated social seat on your hours. We handle payroll after you hire.",
            "Channels stay active without turning your week into a content firefight.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Outsource_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "outsource",
        "path2": "smm",
        "allow_8": False,
        "headlines": [
            "Outsource Social to PH",
            "Dedicated SMM Seat",
            "On Your Brand Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Free SMM Consult",
            "Posting Stops Falling Behind",
            "Not Freelance Social",
            "Filipino Social Seat",
            "Talk Offshore Social",
            "We Find. You Choose.",
            "Community Replies Covered",
            "Outsource Social Ops",
            "Channels Don't Go Quiet",
            "{KeyWord:Outsource Social}",
        ],
        "descs": [
            "Outsource social media ops to a dedicated Filipino teammate — not gig posters.",
            "Free consult. We recruit. You interview. We handle payroll after you hire.",
            "Scheduling, community replies, and asset coordination on your hours.",
            "You pick who owns the channels. No obligation from the first conversation.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Administration_EA_PH",
        "final_url": f"{HOST}/us/administrative-support",
        "path1": "ea",
        "path2": "hire",
        "allow_8": True,
        "headlines": [
            "Inbox Eating Your Week",
            "Dedicated Filipino EA",
            "On Your Admin Hours",
            "You Interview Your EA",
            "We Handle Payroll",
            "Free Admin Consult",
            "Admin VA ~$8 an Hour",
            "Not a Freelance EA",
            "Follow-Ups Actually Done",
            "Talk Admin Hire",
            "We Recruit. You Pick.",
            "Hire a Filipino VA",
            "Calendar Stops Slipping",
            "They Learn Your Rhythm",
            "{KeyWord:Hire Admin VA}",
        ],
        "descs": [
            "Inbox, scheduling, and follow-ups eating your week? Hire a dedicated Filipino EA.",
            "Free consult. We recruit and vet. You interview. We handle payroll.",
            "Typical admin VA ~$8/hr. Dedicated seat that learns your rhythms.",
            "Your managers get time back. Nobody starts until you say yes.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Admin_City_Test",
        "final_url": f"{HOST}/us/administrative-support",
        "path1": "hire",
        "path2": "local",
        "allow_8": True,
        "headlines": [
            "{LOCATION(City):Dedicated VA}",
            "Your Week Is Full",
            "Dedicated Filipino VA",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Free Admin Consult",
            "Admin VA ~$8 an Hour",
            "Inbox Stops Eating You",
            "Talk to a Specialist",
            "They Learn Your Rhythm",
            "Hire Without Payroll Drag",
            "Not a Freelance VA",
            "Nobody Starts Till You Say",
            "Clear the Admin Work",
        ],
        "descs": [
            "Your week is full. A dedicated Filipino teammate on your hours clears it.",
            "Free consult. We recruit. You interview. We handle payroll and paperwork.",
            "Typical admin VA ~$8/hr. City-aware hire path — same employer admin LP.",
            "Talk to a specialist. No obligation. You pick who joins.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Accounting_Hire_PH",
        "final_url": f"{HOST}/us/accounting",
        "path1": "accounting",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Month-End Piling Up?",
            "Dedicated Accounting Seat",
            "On Your Finance Hours",
            "You Interview Finalists",
            "We Handle Payroll",
            "Free Accounting Consult",
            "Recurring Books Support",
            "Not Freelance Accounting",
            "You Pick Who Joins",
            "Talk Accounting Hire",
            "We Recruit. You Decide.",
            "PH Accounting Support",
            "Month-End Help From PH",
            "Capacity for Month-End",
            "{KeyWord:Accounting Support}",
        ],
        "descs": [
            "Recurring accounting support stacking up? Add a dedicated Filipino seat.",
            "Free consult. We shortlist. You interview before anyone starts.",
            "Extra capacity for transactions, schedules, and reporting prep — not licensed advice.",
            "We handle payroll after you hire. You keep hire authority.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Accounting_Outsource_PH",
        "final_url": f"{HOST}/us/accounting",
        "path1": "outsource",
        "path2": "acct",
        "allow_8": False,
        "headlines": [
            "Outsource Accounting PH",
            "Dedicated Finance Seat",
            "On Your Close Calendar",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Free Outsource Consult",
            "Reporting Prep Support",
            "Not Rotating Freelancers",
            "Filipino Accounting Ops",
            "Talk Offshore Finance",
            "We Find Them. You Pick.",
            "PH Accounting Capacity",
            "Outsource Recurring Work",
            "Keep Month-End Moving",
            "{KeyWord:Outsource Accounting}",
        ],
        "descs": [
            "Outsource recurring accounting support to a dedicated Filipino teammate.",
            "Free consult. We shortlist. You interview. We handle payroll after you hire.",
            "Help with transactions, schedules, and reporting prep — not licensed advice.",
            "Dedicated seat continuity. You keep hire control before anyone starts.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Hire_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "books",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Invoices Stacking Up?",
            "Dedicated PH Bookkeeper",
            "On Your Books Hours",
            "You Interview Bookkeepers",
            "We Handle Payroll",
            "Free Books Consult",
            "Reconciliations Covered",
            "Not Freelance Books",
            "You Pick Your Bookkeeper",
            "Talk Bookkeeping Hire",
            "We Recruit. You Decide.",
            "Filipino Bookkeeper",
            "Day-to-Day Books Owner",
            "Hire Books Capacity",
            "{KeyWord:Filipino Bookkeeper}",
        ],
        "descs": [
            "Invoices and reconciliations waiting on you? Hire a dedicated Filipino bookkeeper.",
            "Free consult. We recruit. You interview. We handle payroll after you hire.",
            "A dedicated books seat owns day-to-day support — not a freelance marketplace.",
            "Your finance owner spends less time catching up. You pick who joins.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Outsource_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "outsource",
        "path2": "books",
        "allow_8": False,
        "headlines": [
            "Outsource Bookkeeping PH",
            "Dedicated Books Seat",
            "On Your Finance Hours",
            "You Interview Then Hire",
            "Payroll? We Handle It",
            "Free Bookkeeping Consult",
            "Invoices Stop Waiting",
            "Not Rotating Bookkeepers",
            "Filipino Books Support",
            "Talk Offshore Books",
            "We Find. You Choose.",
            "PH Bookkeeping Ops",
            "Outsource Routine Books",
            "Your Finance Owner Breathes",
            "{KeyWord:Outsource Bookkeeping}",
        ],
        "descs": [
            "Outsource day-to-day bookkeeping to a dedicated Filipino teammate.",
            "Free consult. We shortlist. You interview. We handle payroll after you hire.",
            "Invoices, records, and reconciliations stop stacking on your desk.",
            "Dedicated books seat — continuity, not rotating freelance help.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Customer_Service_Hire_PH",
        "final_url": f"{HOST}/us/customer-service",
        "path1": "support",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Customers Waiting Too Long",
            "Dedicated CS Teammate",
            "On Your Support Hours",
            "You Interview Support",
            "We Handle Payroll",
            "Free CS Hire Consult",
            "Queue Stops Building",
            "Not Freelance Support",
            "You Pick Who Answers",
            "Talk CS Hire",
            "Filipino Support Seat",
            "Brand Sounds Looked After",
            "Hire Support Capacity",
            "We Recruit. You Decide.",
            "{KeyWord:Hire Support Staff}",
        ],
        "descs": [
            "Customer questions sitting too long? Add a dedicated Filipino support seat.",
            "Free consult. We shortlist. You interview before anyone joins your team.",
            "Dedicated support on your hours — inquiries, tickets, and status updates.",
            "We handle payroll after you hire. More consistent customer communication.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Customer_Service_Outsource_PH",
        "final_url": f"{HOST}/us/customer-service",
        "path1": "outsource",
        "path2": "cs",
        "allow_8": False,
        "headlines": [
            "Outsource Support to PH",
            "Dedicated CS Seat",
            "On Your Customer Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Free Support Consult",
            "Tickets Stop Piling Up",
            "Not Rotating CS Gigs",
            "Filipino Support Team",
            "Talk Offshore Support",
            "We Find Them. You Pick.",
            "PH Customer Service",
            "Outsource the Queue",
            "Coverage Without Chaos",
            "{KeyWord:Outsource Support}",
        ],
        "descs": [
            "Outsource customer service to a dedicated Filipino teammate on your hours.",
            "Free consult. We recruit. You interview. We handle payroll after you hire.",
            "Inquiries, tickets, and status updates stop sitting unanswered.",
            "Dedicated support seat — not rotating freelance gigs. You pick who joins.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Human_Resources_Hire_PH",
        "final_url": f"{HOST}/us/hr",
        "path1": "hr",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "People Admin Stacking Up",
            "Dedicated HR Support",
            "On Your HR Hours",
            "You Interview HR Staff",
            "We Handle Payroll",
            "Free HR Hire Consult",
            "Onboarding Stops Stalling",
            "Not Freelance HR Help",
            "You Pick Your HR Seat",
            "Talk HR Support Hire",
            "Filipino HR Teammate",
            "Managers Get Time Back",
            "Hire HR Capacity",
            "We Recruit. You Decide.",
            "{KeyWord:Filipino HR}",
        ],
        "descs": [
            "People admin and onboarding stacking up? Hire dedicated Filipino HR support.",
            "Free consult. We shortlist. You interview before anyone joins — businesses only.",
            "Records, checklists, and interview scheduling on your hours. We handle payroll.",
            "Managers stop being the default ops desk. You pick who joins.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Human_Resources_Outsource_PH",
        "final_url": f"{HOST}/us/hr",
        "path1": "outsource",
        "path2": "hr",
        "allow_8": False,
        "headlines": [
            "Outsource HR Admin PH",
            "Dedicated HR Seat",
            "On Your People Hours",
            "You Interview Then Hire",
            "Payroll? We Handle It",
            "Free HR Consult",
            "Records and Checklists",
            "Not Rotating HR Gigs",
            "Filipino HR Ops",
            "Talk Offshore HR",
            "We Find. You Choose.",
            "PH HR Administration",
            "Outsource People Admin",
            "Leaders Run the Business",
            "{KeyWord:Outsource HR}",
        ],
        "descs": [
            "Outsource HR administration to a dedicated Filipino teammate.",
            "Free consult. We recruit. You interview. We handle payroll after you hire.",
            "Onboarding checklists, records, and scheduling stop defaulting to managers.",
            "Dedicated HR support seat — businesses only. You keep hire control.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Recruitment_Hire_PH",
        "final_url": f"{HOST}/us/recruitment",
        "path1": "recruit",
        "path2": "hire",
        "allow_8": False,
        "headlines": [
            "Hiring Pipeline Slowing",
            "Dedicated Recruiting VA",
            "On Your TA Hours",
            "You Interview TA Staff",
            "We Handle Payroll",
            "Free Recruiting Consult",
            "Screens Stop Stalling",
            "Not a Job Board Hire",
            "You Pick Your TA Seat",
            "Talk Recruiting Hire",
            "Filipino TA Teammate",
            "Managers Just Decide",
            "Hire Recruiting Support",
            "We Recruit. You Decide.",
            "{KeyWord:TA Support}",
        ],
        "descs": [
            "Sourcing and interview scheduling slowing your pipeline? Hire recruiting support.",
            "Free consult. We shortlist Filipino TA help. You interview before anyone joins.",
            "Dedicated recruiting seat on your hours. We handle payroll after you hire.",
            "Hiring managers spend time deciding — not chasing calendars. Businesses only.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Recruitment_Outsource_PH",
        "final_url": f"{HOST}/us/recruitment",
        "path1": "outsource",
        "path2": "ta",
        "allow_8": False,
        "headlines": [
            "Outsource Recruiting PH",
            "Dedicated TA Seat",
            "On Your Hiring Hours",
            "You Interview Then Hire",
            "Payroll Handled for You",
            "Free TA Consult",
            "Calendar Chasing Stops",
            "Not Freelance Recruiting",
            "Filipino TA Support",
            "Talk Offshore TA",
            "We Find Them. You Pick.",
            "PH Recruiting Ops",
            "Outsource Sourcing Work",
            "Pipeline Hygiene Covered",
            "{KeyWord:Outsource Recruiting}",
        ],
        "descs": [
            "Outsource sourcing, screens, and interview coordination to a dedicated TA seat.",
            "Free consult. We shortlist. You interview. We handle payroll after you hire.",
            "Your hiring managers spend time deciding — not chasing resumes and calendars.",
            "Staffing partner for businesses hiring recruiting support — not a job board.",
        ],
    },
    {
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
            "You Interview Setters",
            "We Handle Payroll",
            "Free Sales Consult",
            "Pipeline Basics Covered",
            "Not Freelance Sales Gigs",
            "You Pick Your Setter",
            "Talk Sales Hire",
            "Filipino Sales Teammate",
            "Sellers Talk to Buyers",
            "Hire Sales Capacity",
            "We Recruit. You Decide.",
            "{KeyWord:Sales Support}",
        ],
        "descs": [
            "Prospect research, CRM hygiene, and follow-ups slipping? Hire dedicated help.",
            "Free consult. We shortlist Filipino sales support. You interview before they join.",
            "Dedicated setter or sales-support seat on your hours. We handle payroll.",
            "Sellers spend more time talking to buyers. Staffing — not a job board.",
        ],
    },
    {
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
            "Payroll? We Handle It",
            "Free Sales Consult",
            "CRM Stops Getting Messy",
            "Not Rotating Freelancers",
            "Filipino Sales Ops",
            "Talk Offshore Sales",
            "We Find Them. You Pick.",
            "PH Sales Support",
            "Outsource Follow-Ups",
            "Protect the Pipeline",
            "{KeyWord:Outsource Sales}",
        ],
        "descs": [
            "Outsource appointment setting and sales support to a dedicated Filipino seat.",
            "Free consult. We recruit. You interview. We handle payroll after you hire.",
            "Research, CRM hygiene, and follow-ups stop slipping while closers stay buried.",
            "Sellers talk to buyers. You pick who joins. Staffing partner — not a job board.",
        ],
    },
    {
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
            "Free Setter Consult",
            "Booked Conversations",
            "Not a WFH Job Ad",
            "You Pick Who Sets",
            "Talk Setter Staffing",
            "They Watch the Pipeline",
            "Hire Without US Overhead",
            "Appointment Setting PH",
            "We Recruit. You Decide.",
            "{KeyWord:Appointment Setting}",
        ],
        "descs": [
            "Need an appointment setter without another US full-time hire? Dedicated Filipino seat.",
            "Free consult. We shortlist. You interview before anyone joins your sales team.",
            "On your hours. We handle payroll. You pick who books the conversations.",
            "For employers hiring setters — not candidates looking for WFH jobs.",
        ],
    },
]


FORBIDDEN_MONEY_AGS = {
    "Sales_Hire_PH",
    "Sales_Outsource_PH",
    "Appointment_Setter_Hire_PH",
    "Digital_Marketing_Hire_PH",
    "Digital_Marketing_Outsource_PH",
    "Social_Media_Hire_PH",
    "Social_Media_Outsource_PH",
    "Accounting_Hire_PH",
    "Accounting_Outsource_PH",
    "Bookkeeping_Hire_PH",
    "Bookkeeping_Outsource_PH",
    "Customer_Service_Hire_PH",
    "Customer_Service_Outsource_PH",
    "Human_Resources_Hire_PH",
    "Human_Resources_Outsource_PH",
    "Recruitment_Hire_PH",
    "Recruitment_Outsource_PH",
}


def assert_copy_rules(rsa: dict) -> None:
    ag = rsa["ad_group"]
    blob = " ".join(rsa["headlines"] + rsa["descs"])
    low = blob.lower()
    if any(w in low for w in ("fuck", "shit", "desperate", "fortune 500", "fortune500")):
        raise SystemExit(f"{ag}: forbidden tone/claim")
    if rsa["allow_8"]:
        if "~$8" not in blob and "~$8/hr" not in blob:
            raise SystemExit(f"{ag}: expected ~$8 on admin/hub LP RSA")
    else:
        if "$8" in blob:
            raise SystemExit(f"{ag}: do not put $8 on this LP ({rsa['final_url']})")
    if ag in FORBIDDEN_MONEY_AGS and "$8" in blob:
        raise SystemExit(f"{ag}: $8 leaked onto non-admin LP")
    for p in (rsa["path1"], rsa["path2"]):
        if len(p) > 15:
            raise SystemExit(f"{ag}: path too long ({len(p)}): {p}")


def append_rsa(rows: list[dict[str, str]], rsa: dict) -> None:
    validate_rsa(rsa["headlines"], rsa["descs"], f"{rsa['campaign']}/{rsa['ad_group']}")
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
                "Emotional RSA add 2026-08-09; Paused; Campaign Status blank "
                "(live-US-safe); same Final URL as existing AG RSAs"
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
    if len({(x["campaign"], x["ad_group"]) for x in RSAS}) != len(RSAS):
        raise SystemExit("duplicate AG in RSAS list")
    rows: list[dict[str, str]] = []
    for rsa in RSAS:
        append_rsa(rows, rsa)
    write_csv(OUT_CSV, rows)

    by_lp: dict[str, list[str]] = {}
    for rsa in RSAS:
        by_lp.setdefault(rsa["final_url"].replace(HOST, ""), []).append(rsa["ad_group"])
    print(f"Wrote {OUT_CSV}")
    print(f"  AGs={len(RSAS)} RSAs={len(rows)} (1:1, all Paused)")
    print("  Campaign Status blank · Brand excluded · no negatives")
    for lp, ags in by_lp.items():
        print(f"  {lp}: {len(ags)} AGs — {', '.join(ags)}")


if __name__ == "__main__":
    main()
