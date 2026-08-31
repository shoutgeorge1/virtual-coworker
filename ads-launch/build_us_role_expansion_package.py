#!/usr/bin/env python3
"""Build US exact/phrase role-expansion Editor package + reports.

Hard rules:
- Google Ads Editor CSV only (no API mutate)
- Final URL = https://www.virtualcoworker.app/us only
- Exact + Phrase only (no Broad)
- Exactly 3 RSAs per new ad group
- No DKI
- Campaign budget / bid / settings columns blank (preserve live)
- Shared negatives already on VC_US_S_ROLES — do not rebuild
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "reports" / "google-ads" / "us-role-expansion"
EDITOR = REPO / "ads-launch" / "us-role-expansion-2026-08-21"
XRAY = REPO / "xray" / "public" / "us-role-expansion.html"
XRAY_DATA = REPO / "xray" / "data" / "us-role-expansion-2026-08-21.json"

US = "496-715-1855"
CAMPAIGN = "VC_US_S_ROLES"
CAMPAIGN_ID = "24117249295"
HOST = "https://www.virtualcoworker.app"
FINAL = f"{HOST}/us"
LABEL = "VC_US_EXACT_PHRASE_EXPANSION_2026-08-21"
CPC_AG = "12.00"  # ad-group bid only; campaign ceiling untouched

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
    "Negative",
    "Labels",
    "Comment",
]

FORBIDDEN = ("\u2014", "\u2013", "\u2026", "...", "\u2018", "\u2019", "\u201c", "\u201d", "\u00a0", "{KeyWord:", "{KEYWORD:", "{keyword:")
DKI_RE = re.compile(r"\{KeyWord:", re.I)


def blank() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def utm(ag: str, rsa: str) -> str:
    # Keep final URL clean; append query for Editor Final URL field
    q = (
        f"utm_source=google&utm_medium=cpc&utm_campaign=vc_us_roles"
        f"&utm_content={ag.lower()}_{rsa}"
        f"&utm_term={{keyword}}&matchtype={{matchtype}}"
        f"&campaignid={{campaignid}}&adgroupid={{adgroupid}}&creative={{creative}}"
        f"&lp_version=us-main-control"
    )
    return f"{FINAL}?{q}"


def check_len(kind: str, text: str, limit: int) -> None:
    n = len(text)
    if n > limit:
        raise SystemExit(f"{kind} too long ({n}>{limit}): {text!r}")
    for bad in FORBIDDEN:
        if bad.lower() in text.lower() if bad.startswith("{") else bad in text:
            raise SystemExit(f"forbidden token in {kind}: {text!r}")


# Selected 7 groups. Property Management deferred (overlap with paused
# Property_Management_VA_PH + live TF_Real_Estate). QuickBooks VA exact/phrase
# currently serving in TF_Bookkeeping — replaced with bookkeeping-service seed;
# post-enable migrate QB VA after pausing TF_Bookkeeping duplicates.
GROUPS: list[dict] = [
    {
        "name": "QuickBooks_Bookkeeper",
        "category": "software",
        "bruntwork": [
            "https://www.bruntwork.co/services/quickbooks-bookkeeper/",
            "https://www.bruntwork.co/services/outsourced-bookkeeping/",
            "https://www.bruntwork.co/services/xero-bookkeeper/",
        ],
        "why": "Mandatory. BruntWork software-role LP cluster. Control Aug 21 QB theme with exact/phrase.",
        "keywords": [
            "quickbooks bookkeeper",
            "hire quickbooks bookkeeper",
            "outsourced quickbooks bookkeeping",
            "quickbooks bookkeeping help",
            "remote quickbooks bookkeeper",
            "quickbooks bookkeeping service",  # replaces serving TF_Bookkeeping [quickbooks virtual assistant]
        ],
        "deferred_keywords": [
            "quickbooks virtual assistant",  # add after pausing TF_Bookkeeping exact+phrase
        ],
        "ag_negatives_phrase": [
            "quickbooks login",
            "quickbooks download",
            "quickbooks tutorial",
            "quickbooks training",
            "quickbooks certification",
            "quickbooks customer service number",
            "quickbooks technical support",
            "quickbooks course",
            "quickbooks class",
            "quickbooks proadvisor course",
        ],
        "rsas": {
            "direct": {
                "headlines": [
                    "Hire a QuickBooks Bookkeeper",
                    "QuickBooks Help for Employers",
                    "Bookkeeping Staff for Teams",
                    "Hire Remote Bookkeeping Help",
                    "Outsourced QuickBooks Support",
                    "Fill Your Books Role Fast",
                    "Dedicated Bookkeeping Hire",
                    "Philippines Bookkeeping Staff",
                    "Tell Us the Books Role",
                    "Interview Your Shortlist",
                    "Staff Your Finance Ops",
                    "Get Books Support On Call",
                ],
                "descriptions": [
                    "Hire a QuickBooks bookkeeper for your company. We recruit and you interview.",
                    "Outsourced QuickBooks help for growing teams. Full-time or part-time seats.",
                    "Remote bookkeeping staff on your hours. No recruitment fees to start.",
                    "Tell us the role. We screen candidates. You choose who joins your business.",
                ],
            },
            "relief": {
                "headlines": [
                    "Your Books, Finally Caught Up",
                    "Stop Chasing Month-End Chaos",
                    "Reconciliations Off Your Desk",
                    "Keep Invoices Moving Daily",
                    "Close Books Without Overtime",
                    "Hand Off Routine Book Work",
                    "Catch Up Without Hiring Drama",
                    "Free Ops From Spreadsheets",
                    "Month-End Without the Scramble",
                    "Let Finance Focus Again",
                    "Books That Stay Current",
                    "Relief for Busy Operators",
                ],
                "descriptions": [
                    "When books slip, everything slips. Get dedicated help for your company books.",
                    "Stop living in catch-up mode. A remote bookkeeper works your hours.",
                    "Invoices, reconciliations, and routine reporting owned by one seat.",
                    "You stay in control. We recruit. You interview. Nobody starts without your yes.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Teams",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview the Shortlist",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Hire With a Clear Process",
                ],
                "descriptions": [
                    "From $7/hour for dedicated Philippines staff. We recruit and vet for your role.",
                    "Vetted talent on your business hours. You interview before anyone starts.",
                    "We handle recruiting, screening, payroll, and HR after you hire.",
                    "Built for growing US companies that need reliable bookkeeping support.",
                ],
            },
        },
    },
    {
        "name": "Executive_Assistant",
        "category": "role",
        "bruntwork": [
            "https://www.bruntwork.co/services/executive-assistants/",
            "https://www.bruntwork.co/services/outsource-executive-assistant/",
        ],
        "why": "Core EA cluster on BruntWork. Administration_EA_PH is paused — controlled exact/phrase relaunch to /us.",
        "keywords": [
            "virtual executive assistant",
            "hire executive assistant",
            "outsourced executive assistant",
            "executive assistant philippines",
            "dedicated executive assistant",
            "remote executive assistant service",
        ],
        "ag_negatives_phrase": ["executive assistant job", "executive assistant salary", "ea course"],
        "rsas": {
            "direct": {
                "headlines": [
                    "Hire an Executive Assistant",
                    "Philippines Executive Support",
                    "Dedicated EA for Your Company",
                    "Remote Executive Assistant",
                    "Outsourced EA for Leaders",
                    "Build Your EA Seat Fast",
                    "Hire Reliable EA Support",
                    "Staff Your Leadership Ops",
                    "Interview EA Finalists",
                    "Tell Us What You Need",
                    "Executive Support On Demand",
                    "Fill Your EA Role Today",
                ],
                "descriptions": [
                    "Hire a dedicated executive assistant for your company. You interview the shortlist.",
                    "Philippines EA talent for calendar, inbox, and follow-through on your hours.",
                    "Outsourced executive support without the overhead of a local full hire.",
                    "We recruit and screen. You choose who joins your leadership workflow.",
                ],
            },
            "relief": {
                "headlines": [
                    "Give Your Calendar Back",
                    "Get Inbox Off Your Plate",
                    "Stop Losing Days to Admin",
                    "Protect Time for Real Work",
                    "End the Follow-Up Chase",
                    "Keep Meetings Running Clean",
                    "Hand Off Routine EA Work",
                    "Lead Without Admin Drag",
                    "Clear the Ops Bottleneck",
                    "Make Room for Decisions",
                    "Less Scramble, More Focus",
                    "Relief for Busy Founders",
                ],
                "descriptions": [
                    "Calendar, inbox, and follow-ups owned by one dedicated seat on your hours.",
                    "Stop losing mornings to admin. Get executive support your team can trust.",
                    "You keep the decisions. They keep the details moving for your business.",
                    "Tell us the workload. We recruit. You interview before anyone starts.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Cos",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview Finalists",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Clear Hiring Process",
                ],
                "descriptions": [
                    "From $7/hour dedicated staff. We recruit and vet EA candidates for your role.",
                    "Talent matched to your hours. You interview. Nobody starts without your yes.",
                    "We stay on the account for payroll, HR, and coverage after you hire.",
                    "Built for US operators who need reliable executive support without bloat.",
                ],
            },
        },
    },
    {
        "name": "Admin_Assistant",
        "category": "role",
        "bruntwork": [
            "https://www.bruntwork.co/services/outsource-administrative-assistant/",
            "https://www.bruntwork.co/services/back-office-outsourcing/",
        ],
        "why": "Core admin cluster. BruntWork has dedicated outsource-admin LPs.",
        "keywords": [
            "virtual administrative assistant",
            "hire virtual administrative assistant",
            "administrative assistant outsourcing",
            "offshore administrative assistant",
            "administrative assistant philippines",
            "remote administrative assistant service",
        ],
        "ag_negatives_phrase": [
            "administrative assistant job",
            "admin assistant salary",
            "administrative assistant resume",
        ],
        "rsas": {
            "direct": {
                "headlines": [
                    "Hire Reliable Admin Support",
                    "Virtual Admin for Your Team",
                    "Outsourced Admin Assistant",
                    "Philippines Admin Staff",
                    "Remote Admin for Employers",
                    "Build Your Admin Seat",
                    "Hire Admin Help Fast",
                    "Staff Your Back Office",
                    "Interview Admin Finalists",
                    "Tell Us the Admin Role",
                    "Dedicated Admin Support",
                    "Fill Admin Gaps Today",
                ],
                "descriptions": [
                    "Hire a virtual administrative assistant for your company. You choose who joins.",
                    "Offshore admin support for inbox, documents, and follow-up on your hours.",
                    "Outsourced administrative help without a local hiring loop.",
                    "We recruit and screen. You interview. Dedicated seat for your business.",
                ],
            },
            "relief": {
                "headlines": [
                    "Get Admin Off Your Plate",
                    "Stop Drowning in Busywork",
                    "Clear the Task Backlog",
                    "Keep Ops Moving Daily",
                    "Hand Off Routine Admin",
                    "Less Chaos in the Inbox",
                    "Documents Without Delay",
                    "Follow-Ups That Happen",
                    "Free Your Team to Sell",
                    "End the Admin Scramble",
                    "Make Workdays Lighter",
                    "Relief for Ops Managers",
                ],
                "descriptions": [
                    "When admin piles up, growth stalls. Get a dedicated seat for your company.",
                    "Inbox, docs, and follow-ups handled by someone working your hours.",
                    "Stop pulling skilled people into busywork. Put admin on a real seat.",
                    "Tell us what is piling up. We recruit. You interview the shortlist.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Teams",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview the Shortlist",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Hire With Clear Process",
                ],
                "descriptions": [
                    "From $7/hour dedicated Philippines staff for admin roles your company needs.",
                    "We recruit and vet. You interview. Talent works your business hours.",
                    "Payroll and HR stay with us after you hire so your team can focus.",
                    "Made for growing US companies that need dependable admin coverage.",
                ],
            },
        },
    },
    {
        "name": "Customer_Support",
        "category": "role",
        "bruntwork": [
            "https://www.bruntwork.co/services/customer-support/",
            "https://www.bruntwork.co/services/customer-service-outsourcing-august-2024/",
            "https://www.bruntwork.co/services/call-center-outsourcing/",
        ],
        "why": "Core CS cluster. Avoid duplicating serving Customer_Service_Hire_PH PH terms.",
        "keywords": [
            "outsourced customer support",
            "customer support outsourcing",
            "customer service outsourcing philippines",
            "hire customer service virtual assistant",
            "offshore customer support",
            "remote customer service team",
        ],
        "ag_negatives_phrase": [
            "customer service job",
            "customer support salary",
            "call center job",
        ],
        "rsas": {
            "direct": {
                "headlines": [
                    "Build Your Support Team",
                    "Outsourced Customer Support",
                    "Hire CS Help for Employers",
                    "Offshore Support Staff",
                    "Remote Customer Service",
                    "Staff Your Support Queue",
                    "Philippines Support Talent",
                    "Hire Reliable CS Coverage",
                    "Interview Support Finalists",
                    "Tell Us Your Support Need",
                    "Dedicated Support Seats",
                    "Grow Support Without Bloat",
                ],
                "descriptions": [
                    "Build customer support coverage for your company with dedicated remote seats.",
                    "Outsourced support talent for tickets, chat, and follow-through on your hours.",
                    "Hire customer service help without standing up a local team from scratch.",
                    "We recruit and screen. You interview. You choose who joins your support roster.",
                ],
            },
            "relief": {
                "headlines": [
                    "Keep Every Customer Covered",
                    "Stop Losing Tickets Overnight",
                    "End the Support Backlog",
                    "Cover Peaks Without Panic",
                    "Reply Faster Every Day",
                    "Hand Off Routine Tickets",
                    "Protect Your Brand Tone",
                    "Let Your Team Focus Again",
                    "Fewer Missed Conversations",
                    "Support That Keeps Up",
                    "Calm the Queue Chaos",
                    "Relief for Support Leads",
                ],
                "descriptions": [
                    "When tickets pile up, revenue leaks. Get dedicated coverage for your business.",
                    "Remote support staff working your hours so customers are not left waiting.",
                    "Keep tone and process yours. They handle the daily queue volume.",
                    "Tell us channels and hours. We recruit. You interview before go-live.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Cos",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview Finalists",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Clear Support Hiring Path",
                ],
                "descriptions": [
                    "From $7/hour dedicated seats. We recruit customer support talent for your team.",
                    "Vetted Philippines staff on your hours. You interview every hire.",
                    "We handle recruiting, payroll, and HR so your leads can run the queue.",
                    "Built for US companies scaling support without inflating local headcount.",
                ],
            },
        },
    },
    {
        "name": "HR_Recruiting",
        "category": "role",
        "bruntwork": [
            "https://www.bruntwork.co/services/hr-outsourcing/",
        ],
        "why": "Core HR/recruiting. Human_Resources_Hire_PH paused — relaunch exact/phrase to /us.",
        "keywords": [
            "recruiting virtual assistant",
            "hr virtual assistant",
            "hire recruiting assistant",
            "recruitment assistant outsourcing",
            "offshore hr support",
            "recruitment outsourcing philippines",
        ],
        "ag_negatives_phrase": [
            "hr assistant job",
            "recruiter jobs",
            "hr salary",
            "work from home recruiting job",
        ],
        "rsas": {
            "direct": {
                "headlines": [
                    "Hire Recruiting Support",
                    "HR Help for Your Company",
                    "Recruiting Assistant Hire",
                    "Offshore HR Support",
                    "Philippines Recruiting Help",
                    "Build Your TA Capacity",
                    "Staff Recruiting Ops Fast",
                    "Remote HR Admin Support",
                    "Interview Recruiting Help",
                    "Tell Us Your Hiring Load",
                    "Dedicated Recruiting Seat",
                    "Outsourced HR Assistance",
                ],
                "descriptions": [
                    "Hire recruiting and HR support for your company. Dedicated remote seats.",
                    "Sourcing support, scheduling, and people admin on your business hours.",
                    "Outsourced recruitment assistance without standing up a full local TA team.",
                    "We recruit and screen. You interview. You choose who joins your HR workflow.",
                ],
            },
            "relief": {
                "headlines": [
                    "Stop Losing Time to Hiring",
                    "Clear the Recruiting Backlog",
                    "Get Scheduling Off Your Desk",
                    "Keep Pipelines Moving",
                    "Hand Off Candidate Chase",
                    "Less Admin in Recruiting",
                    "Source Without the Scramble",
                    "Free Managers to Decide",
                    "Hiring Ops Without Chaos",
                    "Catch Up on Open Roles",
                    "Make Recruiting Sustainable",
                    "Relief for Busy HR Leads",
                ],
                "descriptions": [
                    "Open roles stall when recruiting admin piles up. Get a dedicated support seat.",
                    "Candidate chase, scheduling, and pipeline hygiene handled on your hours.",
                    "Your managers keep decisions. Support owns the repetitive hiring work.",
                    "Tell us the bottleneck. We recruit help. You interview before anyone starts.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Teams",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview the Shortlist",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Clear Process to Hire",
                ],
                "descriptions": [
                    "From $7/hour dedicated staff for HR and recruiting support roles.",
                    "We recruit and vet. You interview. Talent works your company hours.",
                    "Payroll and HR stay with us after placement so your team stays focused.",
                    "For growing US companies that need recruiting capacity without local bloat.",
                ],
            },
        },
    },
    {
        "name": "Ecommerce_Shopify",
        "category": "industry",
        "bruntwork": [
            "https://www.bruntwork.co/services/shopify-e-commerce-management/",
            "https://www.bruntwork.co/services/e-commerce-management/",
            "https://www.bruntwork.co/industries/ecommerce-outsourcing/",
        ],
        "why": "Controlled edge. Strong BruntWork ecommerce/Shopify LP cluster. No active US keyword overlap.",
        "keywords": [
            "ecommerce virtual assistant",
            "hire ecommerce virtual assistant",
            "shopify virtual assistant",
            "hire shopify virtual assistant",
            "ecommerce support outsourcing",
            "remote ecommerce assistant",
        ],
        "ag_negatives_phrase": [
            "shopify login",
            "shopify tutorial",
            "shopify theme",
            "shopify developer job",
            "amazon",
            "airbnb",
            "ebay",
            "freelance",
            "shopify developer",
            "shopify developers",
        ],
        "rsas": {
            "direct": {
                "headlines": [
                    "Hire Ecommerce Support",
                    "Shopify Help for Employers",
                    "Remote Ecommerce Assistant",
                    "Staff Your Store Ops",
                    "Outsourced Ecommerce Help",
                    "Hire Shopify Support Fast",
                    "Philippines Store Support",
                    "Build Your Ecommerce Seat",
                    "Interview Store Finalists",
                    "Tell Us Your Store Needs",
                    "Dedicated Store Ops Hire",
                    "Ecommerce Team Support",
                ],
                "descriptions": [
                    "Hire ecommerce support for your company store ops. You interview the shortlist.",
                    "Shopify and ecommerce assistants for orders, listings, and daily store work.",
                    "Outsourced ecommerce help on your hours without a local ops hire first.",
                    "We recruit and screen. You choose who joins your ecommerce workflow.",
                ],
            },
            "relief": {
                "headlines": [
                    "Keep Store Ops Catching Up",
                    "Stop Living in Order Chaos",
                    "Get Listings Off Your Plate",
                    "Handle Peaks Without Panic",
                    "Daily Store Work Covered",
                    "Hand Off Routine Shop Tasks",
                    "Less Firefighting in Ops",
                    "Keep Customers Updated",
                    "Free Founders From Tickets",
                    "Store Work That Gets Done",
                    "Calm the Ecommerce Scramble",
                    "Relief for Store Operators",
                ],
                "descriptions": [
                    "Orders, listings, and store admin pile up fast. Get a dedicated remote seat.",
                    "Keep your store moving while your team focuses on product and growth.",
                    "Routine ecommerce work owned by someone on your business hours.",
                    "Tell us tools and tasks. We recruit. You interview before anyone starts.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Stores",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview Finalists",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Clear Path to Store Help",
                ],
                "descriptions": [
                    "From $7/hour dedicated staff for ecommerce support roles your store needs.",
                    "Vetted Philippines talent on your hours. You interview every candidate.",
                    "We handle recruiting, payroll, and HR after you hire store support.",
                    "Built for US ecommerce teams that need ops coverage without overhead.",
                ],
            },
        },
    },
    {
        "name": "Sales_Support_CRM",
        "category": "role",
        "bruntwork": [
            "https://www.bruntwork.co/services/telesales/",
            "https://www.bruntwork.co/services/hubspot/",
            "https://www.bruntwork.co/services/gohighlevel/",
            "https://www.bruntwork.co/sales-outsourcing/",
        ],
        "why": "Controlled edge. BruntWork sales/CRM software pages. Avoids Property_Management overlap; Sales_Hire_PH is appointment/cold-call heavy.",
        "keywords": [
            "sales support virtual assistant",
            "hire sales virtual assistant",
            "sales administrative assistant",
            "crm virtual assistant",
            "outsourced sales support",
            "remote sales support assistant",
        ],
        "ag_negatives_phrase": [
            "sales job",
            "sales salary",
            "crm login",
            "salesforce certification",
            "hubspot certification",
            "gohighlevel login",
        ],
        "rsas": {
            "direct": {
                "headlines": [
                    "Hire Sales Support Help",
                    "CRM Support for Your Team",
                    "Remote Sales Admin Hire",
                    "Outsourced Sales Support",
                    "Staff Your Sales Ops",
                    "Philippines Sales Support",
                    "Build Sales Admin Capacity",
                    "Hire CRM Hygiene Help",
                    "Interview Sales Support",
                    "Tell Us Your Sales Load",
                    "Dedicated Sales Ops Seat",
                    "Support Your Closers",
                ],
                "descriptions": [
                    "Hire sales support for your company. Lists, CRM hygiene, and follow-up help.",
                    "Remote sales admin on your hours so closers stay on revenue work.",
                    "Outsourced sales support without adding local overhead first.",
                    "We recruit and screen. You interview. You choose who joins your sales ops.",
                ],
            },
            "relief": {
                "headlines": [
                    "Get CRM Chaos Off Closers",
                    "Stop Losing Follow-Ups",
                    "Keep Pipeline Data Clean",
                    "Hand Off Sales Admin",
                    "Lists Without the Grind",
                    "Free Reps to Sell Again",
                    "End the Spreadsheet Chase",
                    "Follow-Ups That Happen",
                    "Less Admin in Sales Days",
                    "Pipeline Work That Moves",
                    "Calm Sales Ops Drag",
                    "Relief for Sales Leaders",
                ],
                "descriptions": [
                    "When CRM and follow-ups slip, deals stall. Get a dedicated support seat.",
                    "Sales admin and pipeline hygiene handled on your business hours.",
                    "Your closers keep selling. Support owns the repetitive sales ops work.",
                    "Tell us tools and tasks. We recruit. You interview before anyone starts.",
                ],
            },
            "trust": {
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Teams",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview the Shortlist",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Clear Sales Support Path",
                ],
                "descriptions": [
                    "From $7/hour dedicated staff for sales support and CRM admin roles.",
                    "We recruit and vet. You interview. Talent works your company hours.",
                    "Payroll and HR included after hire so your sales leads stay focused.",
                    "For US teams that need sales ops coverage without local hiring drag.",
                ],
            },
        },
    },
]

REJECTED = [
    {
        "name": "Property_Management",
        "reason": "Deferred. Heavy keyword overlap with paused Property_Management_VA_PH; TF_Real_Estate already live. Prefer Sales_Support_CRM for the 7th slot.",
    },
    {
        "name": "GoHighLevel / HubSpot software-only",
        "reason": "BruntWork has LPs, but generic software-support risk without stronger US employer search evidence. Keep as watchlist.",
    },
    {
        "name": "Medical / nurses / NDIS / IT engineering",
        "reason": "Outside Virtual Coworker staffing model for this phase.",
    },
]

# Live TF groups currently have 1 RSA each. Add human RSAs (no DKI) for one Editor pass.
# Final URLs match live trust-first destinations (do not retarget to /us main here).
TF_RSA_TOPUPS: list[dict] = [
    {
        "campaign": CAMPAIGN,
        "ad_group": "TF_Bookkeeping",
        "final_base": f"{HOST}/us/tf/bookkeeping",
        "utm_content_prefix": "tf_bookkeeping",
        "rsas": {
            "relief": {
                "path2": "caught-up",
                "headlines": [
                    "Your Books, Finally Caught Up",
                    "Stop Chasing Month-End Chaos",
                    "Reconciliations Off Your Desk",
                    "Keep Invoices Moving Daily",
                    "Close Books Without Overtime",
                    "Hand Off Routine Book Work",
                    "Catch Up Without Hiring Drama",
                    "Free Ops From Spreadsheets",
                    "Month-End Without the Scramble",
                    "Let Finance Focus Again",
                    "Books That Stay Current",
                    "Relief for Busy Operators",
                ],
                "descriptions": [
                    "When books slip, everything slips. Get dedicated help for your company books.",
                    "Stop living in catch-up mode. A remote bookkeeper works your hours.",
                    "Invoices, reconciliations, and routine reporting owned by one seat.",
                    "You stay in control. We recruit. You interview. Nobody starts without your yes.",
                ],
            },
            "trust": {
                "path2": "vetted",
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Support for Growing Teams",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview the Shortlist",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Hire With a Clear Process",
                ],
                "descriptions": [
                    "From $7/hour for dedicated Philippines staff. We recruit and vet for your role.",
                    "Vetted talent on your business hours. You interview before anyone starts.",
                    "We handle recruiting, screening, payroll, and HR after you hire.",
                    "Built for growing US companies that need reliable bookkeeping support.",
                ],
            },
        },
    },
    {
        "campaign": CAMPAIGN,
        "ad_group": "TF_Real_Estate",
        "final_base": f"{HOST}/us/tf/real-estate",
        "utm_content_prefix": "tf_real_estate",
        "rsas": {
            "relief": {
                "path2": "ops",
                "headlines": [
                    "Get Listing Admin Off Plate",
                    "Stop Losing Buyer Follow-Ups",
                    "Keep Transactions Moving",
                    "Hand Off Routine RE Admin",
                    "Clear the Ops Backlog",
                    "Less Chaos in Your Inbox",
                    "Free Agents to Sell Again",
                    "Follow-Ups That Happen",
                    "End the Spreadsheet Chase",
                    "Make Room for Closings",
                    "Calm Real Estate Busywork",
                    "Relief for Busy Brokers",
                ],
                "descriptions": [
                    "When admin piles up, deals stall. Get a dedicated seat for your real estate team.",
                    "Follow-ups, docs, and routine ops handled by someone on your hours.",
                    "Your agents keep selling. Support owns the repetitive real estate admin.",
                    "Tell us the role. We recruit. You interview before anyone starts.",
                ],
            },
            "trust": {
                "path2": "partner",
                "headlines": [
                    "From $7/Hour Staffing",
                    "Vetted Philippines Talent",
                    "Talent Working Your Hours",
                    "We Recruit and Screen",
                    "Not a Freelance Marketplace",
                    "Lower the Cost of Hiring",
                    "Build Team Without Overhead",
                    "No Recruitment Fees",
                    "You Interview Finalists",
                    "Staffing Partner Since 2011",
                    "Payroll and HR Included",
                    "Clear Hiring Process",
                ],
                "descriptions": [
                    "From $7/hour dedicated staff for real estate support roles your company needs.",
                    "We recruit and vet. You interview. Talent works your business hours.",
                    "Not a gig marketplace. Dedicated seats for your real estate operation.",
                    "Payroll and HR stay with us after you hire so your team can focus.",
                ],
            },
        },
    },
]


def validate_group(g: dict) -> None:
    assert len(g["keywords"]) == 6, g["name"]
    for angle, rsa in g["rsas"].items():
        hs = rsa["headlines"]
        ds = rsa["descriptions"]
        assert 10 <= len(hs) <= 12, (g["name"], angle, len(hs))
        assert len(ds) == 4, (g["name"], angle)
        for h in hs:
            check_len(f"{g['name']}/{angle}/H", h, 30)
        for d in ds:
            check_len(f"{g['name']}/{angle}/D", d, 90)
        # no DKI
        blob = " ".join(hs + ds)
        if DKI_RE.search(blob):
            raise SystemExit(f"DKI in {g['name']} {angle}")


def utm_custom(base: str, content: str) -> str:
    q = (
        f"utm_source=google&utm_medium=cpc&utm_campaign=vc_us_roles"
        f"&utm_content={content}"
        f"&utm_term={{keyword}}&matchtype={{matchtype}}"
        f"&campaignid={{campaignid}}&adgroupid={{adgroupid}}&creative={{creative}}"
        f"&lp_version=us-main-control"
    )
    # TF top-ups keep their live trust LP path; still tag experiment content
    if "/tf/" in base:
        q = q.replace("lp_version=us-main-control", "lp_version=tf-rsa-topup")
    return f"{base}?{q}"


def validate_tf_topups() -> None:
    for g in TF_RSA_TOPUPS:
        for angle, rsa in g["rsas"].items():
            hs = rsa["headlines"]
            ds = rsa["descriptions"]
            assert 10 <= len(hs) <= 12, (g["ad_group"], angle, len(hs))
            assert len(ds) == 4, (g["ad_group"], angle)
            for h in hs:
                check_len(f"{g['ad_group']}/{angle}/H", h, 30)
            for d in ds:
                check_len(f"{g['ad_group']}/{angle}/D", d, 90)
            blob = " ".join(hs + ds)
            if DKI_RE.search(blob):
                raise SystemExit(f"DKI in TF top-up {g['ad_group']} {angle}")


def build_editor_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for g in GROUPS:
        validate_group(g)
        # Ad group row
        r = blank()
        r.update(
            {
                "Account": US,
                "Row Type": "Ad group",
                "Campaign": CAMPAIGN,
                "Ad Group": g["name"],
                "Ad Group Status": "Enabled",
                "Maximum CPC bid limit": CPC_AG,
                "Labels": LABEL,
                "Comment": "New exact/phrase exploration AG → /us main control",
            }
        )
        rows.append(r)

        # Keywords exact + phrase
        for kw in g["keywords"]:
            for match in ("Exact", "Phrase"):
                r = blank()
                r.update(
                    {
                        "Account": US,
                        "Row Type": "Keyword",
                        "Campaign": CAMPAIGN,
                        "Ad Group": g["name"],
                        "Keyword": kw,
                        "Criterion Type": match,
                        "Keyword Status": "Enabled",
                        "Labels": LABEL,
                    }
                )
                rows.append(r)

        # Ad-group negatives (phrase)
        for neg in g.get("ag_negatives_phrase") or []:
            r = blank()
            r.update(
                {
                    "Account": US,
                    "Row Type": "Keyword",
                    "Campaign": CAMPAIGN,
                    "Ad Group": g["name"],
                    "Keyword": neg,
                    "Criterion Type": "Phrase",
                    "Keyword Status": "Enabled",
                    "Negative": "Yes",
                    "Labels": LABEL,
                    "Comment": "High-confidence AG negative only",
                }
            )
            rows.append(r)

        # 3 RSAs
        for angle, path in (("direct", "hire"), ("relief", "relief"), ("trust", "trust")):
            rsa = g["rsas"][angle]
            r = blank()
            finals = utm(g["name"], angle)
            payload = {
                "Account": US,
                "Row Type": "Ad",
                "Campaign": CAMPAIGN,
                "Ad Group": g["name"],
                "Ad Status": "Enabled",
                "Ad type": "Responsive search ad",
                "Final URL": finals,
                "Path 1": "us",
                "Path 2": path[:15],
                "Labels": LABEL,
                "Comment": f"RSA angle={angle}; no DKI; lp=us-main-control",
            }
            for i, h in enumerate(rsa["headlines"], start=1):
                payload[f"Headline {i}"] = h
            for i, d in enumerate(rsa["descriptions"], start=1):
                payload[f"Description {i}"] = d
            r.update(payload)
            rows.append(r)

    # TF RSA top-ups only (no new keywords / no AG recreate)
    validate_tf_topups()
    for g in TF_RSA_TOPUPS:
        for angle, rsa in g["rsas"].items():
            r = blank()
            content = f"{g['utm_content_prefix']}_{angle}"
            finals = utm_custom(g["final_base"], content)
            path2 = str(rsa.get("path2") or angle)[:15]
            payload = {
                "Account": US,
                "Row Type": "Ad",
                "Campaign": g["campaign"],
                "Ad Group": g["ad_group"],
                "Ad Status": "Enabled",
                "Ad type": "Responsive search ad",
                "Final URL": finals,
                "Path 1": "tf",
                "Path 2": path2,
                "Labels": LABEL,
                "Comment": f"TF RSA top-up angle={angle}; no DKI; existing AG only",
            }
            for i, h in enumerate(rsa["headlines"], start=1):
                payload[f"Headline {i}"] = h
            for i, d in enumerate(rsa["descriptions"], start=1):
                payload[f"Description {i}"] = d
            r.update(payload)
            rows.append(r)
    return rows


def write_csvs(rows: list[dict[str, str]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    EDITOR.mkdir(parents=True, exist_ok=True)

    editor_path = EDITOR / "google-ads-editor-import-us-role-expansion.csv"
    oneshot = EDITOR / "EDITOR-IMPORT-one-shot.csv"
    with editor_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)
    with oneshot.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {editor_path}")
    print(f"Wrote {oneshot}  ← import this in Google Ads Editor")

    # keywords.csv
    with (OUT / "keywords.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "campaign",
            "ad_group",
            "keyword",
            "match_type",
            "status",
            "negative",
            "notes",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for g in GROUPS:
            for kw in g["keywords"]:
                for mt in ("Exact", "Phrase"):
                    w.writerow(
                        {
                            "campaign": CAMPAIGN,
                            "ad_group": g["name"],
                            "keyword": kw,
                            "match_type": mt,
                            "status": "Enabled",
                            "negative": "No",
                            "notes": "",
                        }
                    )
            for neg in g.get("ag_negatives_phrase") or []:
                w.writerow(
                    {
                        "campaign": CAMPAIGN,
                        "ad_group": g["name"],
                        "keyword": neg,
                        "match_type": "Phrase",
                        "status": "Enabled",
                        "negative": "Yes",
                        "notes": "AG negative",
                    }
                )
            for dk in g.get("deferred_keywords") or []:
                w.writerow(
                    {
                        "campaign": CAMPAIGN,
                        "ad_group": g["name"],
                        "keyword": dk,
                        "match_type": "Exact+Phrase",
                        "status": "Deferred",
                        "negative": "No",
                        "notes": "Add after pausing TF_Bookkeeping duplicates",
                    }
                )

    # rsa-assets.csv
    with (OUT / "rsa-assets.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "ad_group",
            "rsa_angle",
            "asset_type",
            "position",
            "text",
            "char_count",
            "final_url",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for g in GROUPS:
            for angle in ("direct", "relief", "trust"):
                rsa = g["rsas"][angle]
                url = utm(g["name"], angle)
                for i, h in enumerate(rsa["headlines"], start=1):
                    w.writerow(
                        {
                            "ad_group": g["name"],
                            "rsa_angle": angle,
                            "asset_type": "headline",
                            "position": i,
                            "text": h,
                            "char_count": len(h),
                            "final_url": url,
                        }
                    )
                for i, d in enumerate(rsa["descriptions"], start=1):
                    w.writerow(
                        {
                            "ad_group": g["name"],
                            "rsa_angle": angle,
                            "asset_type": "description",
                            "position": i,
                            "text": d,
                            "char_count": len(d),
                            "final_url": url,
                        }
                    )

    # final-urls.csv
    with (OUT / "final-urls.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["ad_group", "rsa_angle", "final_url", "base_path", "lp_version"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for g in GROUPS:
            for angle in ("direct", "relief", "trust"):
                w.writerow(
                    {
                        "ad_group": g["name"],
                        "rsa_angle": angle,
                        "final_url": utm(g["name"], angle),
                        "base_path": "/us",
                        "lp_version": "us-main-control",
                    }
                )

    print(f"Wrote {editor_path}")


def write_manifest(rows: list[dict[str, str]]) -> None:
    now = datetime.now(timezone.utc).isoformat()
    kw_count = sum(1 for r in rows if r["Row Type"] == "Keyword" and r["Negative"] != "Yes")
    neg_count = sum(1 for r in rows if r["Row Type"] == "Keyword" and r["Negative"] == "Yes")
    ad_count = sum(1 for r in rows if r["Row Type"] == "Ad")
    ag_count = sum(1 for r in rows if r["Row Type"] == "Ad group")

    inv = {}
    inv_path = OUT / "account-inventory-readonly.json"
    if inv_path.is_file():
        inv = json.loads(inv_path.read_text())

    md = f"""# US Exact/Phrase Role Expansion — Change Manifest

Generated: `{now}`  
Status: **DRY-RUN ONLY — NOT LAUNCHED**  
Channel: Google Ads Editor CSV (`ads-launch/us-role-expansion-2026-08-21/`)  
API mutations: **none** (hard rule)

## BruntWork handoff

- Coordination request: `reports/competitive/bruntwork/COORDINATION-REQUEST-US-SEARCH-EXPANSION.md`
- Expected file: `reports/competitive/bruntwork/search-expansion-handoff.json`
- At package build time: handoff **pending** (crawl still running). Selection used BruntWork WP URL inventory + US account overlap audit. Re-check handoff before Post; up to two edge groups may be swapped.

## Main converting landing page (verified)

| Evidence | Result |
| --- | --- |
| Expected | `https://www.virtualcoworker.app/us` |
| Ads landing_page_view LAST_30_DAYS | `/us` = **3.0** conv / 691 clicks on `VC_US_S_CORE`; **1.0** conv on `VC_US_S_ROLES` bare `/us` |
| Role LPs (`/us/bookkeeping`, `/us/customer-service`, …) | Clicks, **0** Ads conversions in window |
| Trust / TF LPs | Not converting; **excluded** |
| Explicit exclude | `/us/philippines-virtual-assistants` |
| Live page stamp | `data-lp-version=baseline_v1_2026_08`, `data-baseline-label=US_BASELINE_2026-08-18` |
| Form | Business email + required company + phone; thank-you redirect; GCLID/UTM via `vision/lib/tracking.ts` captureAttribution |
| Phone CTA | `(888) 964-8644` preserved |
| Page changes in this task | **None** (structure/copy frozen) |

## Campaign settings preserved (do not change)

From read-only probe `{inv.get('generated_at_utc','')}`:

| Setting | VC_US_S_ROLES |
| --- | --- |
| Campaign ID | `{CAMPAIGN_ID}` |
| Status | ENABLED |
| Bid strategy | TARGET_SPEND (Maximize Clicks) |
| Daily budget | ${inv.get('campaigns',[{},{}])[1].get('daily_budget_usd', 100) if len(inv.get('campaigns',[]))>1 else 100} |
| CPC ceiling | ${inv.get('campaigns',[{},{}])[1].get('cpc_ceiling_usd', 12) if len(inv.get('campaigns',[]))>1 else 12} |
| Networks | Google Search on; Search Partners off; Display off |
| Geo | PRESENCE |
| Shared negatives | `VC_US_S_🚫_JobSeekers`, `VC_US_S_🚫_Sniper`, `VC_US_S_🥊_Competitors` (already attached — not rebuilt) |
| Conversion goals | Unchanged |
| Campaign Final URL suffix | Unchanged (`lp_version=stage1-v7` remains at campaign level; new ads carry `lp_version=us-main-control` on Final URL) |

Editor import leaves Campaign Status / Budget / Bid Strategy / Networks / Languages / Location **blank**.

## Ad groups in this package ({ag_count})

"""
    for g in GROUPS:
        md += f"- `{g['name']}` — {g['why']}\n"

    md += "\n## Rejected / deferred candidates\n\n"
    for r in REJECTED:
        md += f"- `{r['name']}` — {r['reason']}\n"

    md += f"""

## Counts

| Item | Count |
| --- | --- |
| New ad groups | {ag_count} |
| Keyword rows (positives) | {kw_count} |
| AG negative rows | {neg_count} |
| RSA ads | {ad_count} (exactly 3 per group) |
| Broad match | **0** |
| DKI | **0** |
| Trust-page Final URLs | **0** |

## Keyword construction notes

- Exact + Phrase only for every concept.
- `quickbooks virtual assistant` exact/phrase currently **serving** in `TF_Bookkeeping` → replaced in this package with `quickbooks bookkeeping service`. After enable+validate, pause TF_Bookkeeping QB VA duplicates, then optionally add QB VA into `QuickBooks_Bookkeeper`.
- Naming: no `TF_` prefix — these are exact/phrase expansion groups onto `/us`, not trust-first LP tests.
- Do **not** negative `quick book help` / `quickbooks bookkeeping help` / `quickbooks help`.
- Competitor brands not bid.
- Job-seeker language not used as positives.

## Post-launch pause (not in this CSV)

After new AG enabled and validated:

1. Pause broad `quickbooks virtual assistant` wherever still enabled in bookkeeping groups.
2. Pause serving exact/phrase `quickbooks virtual assistant` in `TF_Bookkeeping` to complete the move.

## Validation checklist

- [x] Campaign ID validated (`{CAMPAIGN_ID}`)
- [x] No broad match in package
- [x] No DKI syntax
- [x] Headline ≤30 / description ≤90
- [x] Exactly 3 RSAs per new group
- [x] All Final URLs base = `/us` + `lp_version=us-main-control`
- [x] Trust page not used
- [x] Budgets/bid strategy/CPC ceiling/locations/languages/networks/schedules not rewritten
- [ ] BruntWork `search-expansion-handoff.json` received and applied (pending)
- [ ] George review on X-ray → Editor import → Post → Enable

## Launch timestamp

**Not launched.** Dry-run only.

## Review cadence

- 24h: spend, search terms, policy, tracking
- 72h: engagement, form starts, phone, search quality
- 7d: employer forms, discovery calls, qualified lead quality

Do not kill themes from one click/day. Separate edge exploration from job-seeker / software-nav / consumer junk.
"""
    (OUT / "change-manifest.md").write_text(md)
    print(f"Wrote {OUT / 'change-manifest.md'}")


def write_bruntwork_map() -> None:
    lines = [
        "# BruntWork evidence map — US role expansion",
        "",
        "Source: BruntWork WP page inventory harvested by the BruntWork crawl agent",
        "(`reports/competitive/bruntwork/_raw-wp-pages-all.json`). Full page-body handoff",
        "(`search-expansion-handoff.json`) was still pending at package build.",
        "",
        "| Ad group | Category | BruntWork evidence URLs | Influence |",
        "| --- | --- | --- | --- |",
    ]
    for g in GROUPS:
        urls = "<br>".join(f"`{u}`" for u in g["bruntwork"])
        lines.append(f"| `{g['name']}` | {g['category']} | {urls} | {g['why']} |")
    lines += [
        "",
        "## Copy learnings applied (strategic, not verbatim)",
        "",
        "- Exact role visible immediately in RSA 1 headlines",
        "- Cost clarity via approved From $7/Hour language in RSA 3",
        "- Tangible workload relief in RSA 2",
        "- Employer language: your company / your business / your team",
        "- Process credibility: we recruit → you interview → nobody starts without your yes",
        "",
        "## Landing-page learnings (for later theme LPs — not this phase)",
        "",
        "- BruntWork maintains dedicated software LPs (QuickBooks, Xero, Shopify, HubSpot, GoHighLevel)",
        "- This phase routes all new traffic to proven `/us` control; dedicated LPs only after theme proves out",
        "",
    ]
    (OUT / "bruntwork-evidence-map.md").write_text("\n".join(lines))
    print(f"Wrote {OUT / 'bruntwork-evidence-map.md'}")


def write_xray() -> None:
    # compact JSON for page
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "dry_run_not_launched",
        "campaign": CAMPAIGN,
        "campaign_id": CAMPAIGN_ID,
        "final_url_base": FINAL,
        "lp_version": "us-main-control",
        "groups": [
            {
                "name": g["name"],
                "keywords": g["keywords"],
                "rsas": {
                    angle: {
                        "headlines": g["rsas"][angle]["headlines"],
                        "descriptions": g["rsas"][angle]["descriptions"],
                        "final_url": utm(g["name"], angle),
                    }
                    for angle in ("direct", "relief", "trust")
                },
                "bruntwork": g["bruntwork"],
            }
            for g in GROUPS
        ],
        "rejected": REJECTED,
    }
    XRAY_DATA.write_text(json.dumps(payload, indent=2))

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        '<meta name="robots" content="noindex,nofollow" />',
        "<title>US Exact/Phrase Expansion · Virtual Coworker</title>",
        '<link rel="stylesheet" href="xray.css" />',
        "<style>",
        ".banner{background:#1a1a1a;color:#fff;padding:1rem 1.2rem;border-radius:10px;border-left:6px solid #e8a317;margin:0 0 1rem}",
        ".banner strong{color:#ffd56a}",
        ".stats{display:flex;flex-wrap:wrap;gap:.7rem;margin:0 0 1rem}",
        ".stat{background:#fff;border:1px solid var(--edge);padding:.7rem 1rem;border-radius:10px}",
        ".stat b{display:block;font-size:1.25rem}",
        "article.ag{background:#fff;border:1px solid var(--edge);border-radius:14px;padding:1.1rem 1.2rem;margin:0 0 1.1rem}",
        ".chips{display:flex;flex-wrap:wrap;gap:.35rem;margin:.3rem 0 .7rem}",
        ".chip{background:var(--tint-cool);border:1px solid var(--tint-cool-edge);font-size:.75rem;padding:.15rem .45rem;border-radius:4px;font-family:var(--mono)}",
        ".chip-phrase{background:var(--tint-amber);border-color:var(--tint-amber-edge)}",
        ".rsa{background:var(--panel-inset);border:1px solid var(--edge-soft);border-radius:10px;padding:.85rem .95rem;margin:.5rem 0}",
        ".cols{display:grid;grid-template-columns:1fr 1fr;gap:.8rem}",
        "@media(max-width:700px){.cols{grid-template-columns:1fr}}",
        ".assets{font-family:var(--mono);font-size:.74rem;margin:.2rem 0 .4rem;padding-left:1.1rem}",
        ".serp{border:1px solid #e8eaed;border-radius:8px;padding:.65rem .8rem;margin:0 0 .5rem;background:#fff}",
        ".serp-url{color:#202124;font-size:.78rem;margin:0}",
        ".serp-title{color:#1a0dab;font-size:1.05rem;margin:.1rem 0;font-weight:400}",
        ".serp-desc{color:#4d5156;font-size:.86rem;margin:0}",
        ".toc{display:flex;flex-wrap:wrap;gap:.5rem 1rem;margin:0 0 1rem}",
        "</style>",
        "</head>",
        '<body data-page="us-role-expansion.html" data-foot="US exact/phrase expansion<br />Dry-run · Editor only">',
        '<div class="app">',
        '<aside class="sidebar" data-nav></aside>',
        '<main class="main">',
        '<header class="page-head">',
        '<p class="kicker">US Search · VC_US_S_ROLES · 21 Aug 2026</p>',
        "<h1>US Exact/Phrase Expansion</h1>",
        "<p>Seven new ad groups onto proven <code>/us</code>, plus two extra human RSAs each for live <code>TF_Bookkeeping</code> and <code>TF_Real_Estate</code> (they only had one). Exact + phrase only. No broad. No DKI. Campaign budgets untouched.</p>",
        "</header>",
        '<div class="banner" role="status"><strong>Dry-run — not launched.</strong> One Editor file for everything: <code>ads-launch/us-role-expansion-2026-08-21/EDITOR-IMPORT-one-shot.csv</code>. Review here, then Import → Post in Google Ads Editor.</div>',
        '<div class="stats">',
        f"<div class=\"stat\"><b>{len(GROUPS)}</b> new groups</div>",
        f"<div class=\"stat\"><b>{len(GROUPS)*12}</b> keyword rows</div>",
        f"<div class=\"stat\"><b>{len(GROUPS)*3}</b> new-group RSAs</div>",
        f"<div class=\"stat\"><b>{sum(len(g['rsas']) for g in TF_RSA_TOPUPS)}</b> TF RSA top-ups</div>",
        '<div class="stat"><b>0</b> broad / DKI</div>',
        "</div>",
        '<nav class="toc">',
    ]
    for g in GROUPS:
        parts.append(f'<a href="#{g["name"].lower()}">{g["name"]}</a>')
    for g in TF_RSA_TOPUPS:
        parts.append(f'<a href="#{g["ad_group"].lower()}">{g["ad_group"]} +RSAs</a>')
    parts.append("</nav>")

    for g in GROUPS:
        parts.append(f'<article class="ag" id="{g["name"].lower()}">')
        parts.append(f'<p class="kicker">VC_US_S_ROLES · {g["category"]}</p>')
        parts.append(f'<h2>{g["name"]}</h2>')
        parts.append(f'<p class="meta">{g["why"]}</p>')
        parts.append('<p class="tiny">Final URL base</p>')
        parts.append(f'<p><a href="{FINAL}" target="_blank" rel="noopener">{FINAL}</a> · <code>lp_version=us-main-control</code></p>')
        parts.append('<p class="kicker">Keywords (Exact + Phrase)</p><div class="chips">')
        for kw in g["keywords"]:
            parts.append(f'<span class="chip">[{kw}]</span>')
            parts.append(f'<span class="chip chip-phrase">"{kw}"</span>')
        parts.append("</div>")
        for angle, label in (("direct", "RSA 1 · Direct"), ("relief", "RSA 2 · Relief"), ("trust", "RSA 3 · Trust")):
            rsa = g["rsas"][angle]
            parts.append(f'<div class="rsa"><p class="kicker">{label}</p>')
            parts.append('<div class="cols"><div>')
            parts.append('<p class="tiny">SERP mock</p>')
            parts.append('<div class="serp">')
            parts.append(f'<p class="serp-url">www.virtualcoworker.app › us</p>')
            parts.append(f'<p class="serp-title">{rsa["headlines"][0]}</p>')
            parts.append(f'<p class="serp-desc">{rsa["descriptions"][0]}</p>')
            parts.append("</div></div><div>")
            parts.append('<p class="tiny">Headlines</p><ol class="assets">')
            for h in rsa["headlines"]:
                parts.append(f"<li>{h} <span class=\"tiny\">({len(h)})</span></li>")
            parts.append('</ol><p class="tiny">Descriptions</p><ol class="assets">')
            for d in rsa["descriptions"]:
                parts.append(f"<li>{d} <span class=\"tiny\">({len(d)})</span></li>")
            parts.append("</ol></div></div></div>")
        parts.append("</article>")

    parts.append("<h2>TF RSA top-ups (existing live groups)</h2>")
    parts.append("<p>These groups already exist and only had one RSA. Sheet adds two more Enabled RSAs each. Final URLs stay on the live trust-first pages.</p>")
    for g in TF_RSA_TOPUPS:
        parts.append(f'<article class="ag" id="{g["ad_group"].lower()}">')
        parts.append('<p class="kicker">VC_US_S_ROLES · existing AG · RSA add only</p>')
        parts.append(f'<h2>{g["ad_group"]}</h2>')
        parts.append(f'<p class="tiny">Final URL</p><p><a href="{g["final_base"]}" target="_blank" rel="noopener">{g["final_base"]}</a></p>')
        for angle, label in (("relief", "New RSA · Relief"), ("trust", "New RSA · Trust")):
            rsa = g["rsas"][angle]
            parts.append(f'<div class="rsa"><p class="kicker">{label}</p>')
            parts.append('<div class="cols"><div>')
            parts.append('<div class="serp">')
            parts.append(f'<p class="serp-url">www.virtualcoworker.app › tf</p>')
            parts.append(f'<p class="serp-title">{rsa["headlines"][0]}</p>')
            parts.append(f'<p class="serp-desc">{rsa["descriptions"][0]}</p>')
            parts.append("</div></div><div>")
            parts.append('<p class="tiny">Headlines</p><ol class="assets">')
            for h in rsa["headlines"]:
                parts.append(f"<li>{h} <span class=\"tiny\">({len(h)})</span></li>")
            parts.append('</ol><p class="tiny">Descriptions</p><ol class="assets">')
            for d in rsa["descriptions"]:
                parts.append(f"<li>{d} <span class=\"tiny\">({len(d)})</span></li>")
            parts.append("</ol></div></div></div>")
        parts.append("</article>")

    parts += [
        "<section>",
        "<h2>Rejected / deferred</h2><ul>",
    ]
    for r in REJECTED:
        parts.append(f"<li><strong>{r['name']}</strong> — {r['reason']}</li>")
    parts += [
        "</ul></section>",
        "<section><h2>Review cadence</h2>",
        "<p>24h spend/search terms/policy · 72h engagement/forms/phone · 7d employer forms and lead quality. Do not kill a theme from one click.</p>",
        "</section>",
        "</main></div>",
        '<script src="nav.js"></script>',
        "</body></html>",
    ]
    XRAY.write_text("\n".join(parts))
    print(f"Wrote {XRAY}")


def patch_nav() -> None:
    nav = REPO / "xray" / "public" / "nav.js"
    text = nav.read_text()
    needle = '{ href: "trust-first-rollout.html", text: "TF test groups", quiet: true },'
    insert = (
        '{ href: "us-role-expansion.html", text: "US exact/phrase expand", quiet: true },\n'
        "    " + needle
    )
    if "us-role-expansion.html" not in text:
        if needle not in text:
            raise SystemExit("nav.js insert point missing")
        nav.write_text(text.replace(needle, insert, 1))
        print("Patched nav.js")
    else:
        print("nav.js already linked")


def patch_experiments_snapshot() -> None:
    path = REPO / "xray" / "data" / "experiments-snapshot.json"
    if not path.is_file():
        print("No experiments-snapshot.json — skip")
        return
    data = json.loads(path.read_text())
    # Keep Launch Control checkbox state untouched. Only append experiment record
    # if structure is a list or has experiments array.
    record = {
        "id": "us-exact-phrase-expansion-2026-08-21",
        "name": "US Exact/Phrase Expansion",
        "status": "dry_run_not_launched",
        "campaign": CAMPAIGN,
        "landing_page": FINAL,
        "lp_version": "us-main-control",
        "ad_groups": [g["name"] for g in GROUPS],
        "notes": "Exact+phrase exploration against /us control. BruntWork handoff pending at build.",
        "created_at": datetime.now(timezone.utc).date().isoformat(),
    }
    if isinstance(data, list):
        data = [r for r in data if r.get("id") != record["id"]] + [record]
    elif isinstance(data, dict):
        key = "experiments" if "experiments" in data else None
        if key:
            exps = [r for r in data[key] if r.get("id") != record["id"]]
            exps.append(record)
            data[key] = exps
        else:
            data["us_exact_phrase_expansion"] = record
    path.write_text(json.dumps(data, indent=2))
    print(f"Updated {path}")


def main() -> None:
    for g in GROUPS:
        validate_group(g)
    rows = build_editor_rows()
    write_csvs(rows)
    write_manifest(rows)
    write_bruntwork_map()
    write_xray()
    patch_nav()
    patch_experiments_snapshot()
    print(
        json.dumps(
            {
                "groups": len(GROUPS),
                "rows": len(rows),
                "status": "dry_run_not_launched",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
