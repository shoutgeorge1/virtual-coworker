#!/usr/bin/env python3
"""Build Google Ads Editor RSA challengers — 2026-08-19.

Read-only toward the live account. Emits Ad rows only.
Does not change budgets, bids, keywords, negatives, geos, or campaign shells.

Campaign / Ad group Status left blank on purpose (live-safe).
No Ads API. Brand deferred.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "ads-launch"
BANNED_PATH = ROOT / "vision" / "lib" / "public-copy-banned.json"

ACCOUNT = {"US": "496-715-1855", "AU": "573-539-1940"}
HOST = "https://www.virtualcoworker.app"
LP_VERSION = "trust_rsa_20260819"
SUFFIX = (
    "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"
    "&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}"
    f"&utm_device={{device}}&lp_version={LP_VERSION}"
)

HL_MAX = 30
DESC_MAX = 90
PATH_MAX = 15

FIELDNAMES = [
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
    *[f"Headline {i}" for i in range(1, 16)],
    *[f"Description {i}" for i in range(1, 5)],
    "Link Text",
    "Description Line 1",
    "Description Line 2",
    "Callout text",
    "Header",
    "Snippet Values",
    "Negative",
    "Comment",
]

JOB_SEEKER_RE = re.compile(
    r"\b(jobs|job seekers?|careers?|salary|resume|work\s+from\s+home|wfh|"
    r"remote jobs?|va jobs?|apply now|hiring now)\b",
    re.I,
)
JUNK_RE = re.compile(
    r"\b(va solutions|va support|ph va|scale with vas?|top va|"
    r"best ph va|va experts|affordable va pros|scale fast with va)\b",
    re.I,
)
CLAIM_RE = re.compile(
    r"top\s*1%|\$\d+\s*/?\s*hr|80%\s*|save\s*\d+%|guaranteed|cheapest|\$7|\$8|\$10",
    re.I,
)
CONSULT_RE = re.compile(r"\bconsult\b|book a demo|schedule a demo", re.I)
DKI_RE = re.compile(r"\{KeyWord:(.+?)\}")
ABBREV_RE = re.compile(r"\b(SMM|PPC|SEO|CS|TA|AP\/AR|PH VA)\b")


def rsa_len(text: str) -> int:
    """Count Editor-facing length. DKI counts the default text only."""
    m = re.fullmatch(r"\{KeyWord:(.+)\}$", text)
    if m:
        return len(m.group(1))
    return len(text)


def validate_rsa(headlines: list[str], descs: list[str], where: str) -> None:
    if not (12 <= len(headlines) <= 15):
        raise SystemExit(f"{where}: need 12–15 headlines, got {len(headlines)}")
    if len(descs) != 4:
        raise SystemExit(f"{where}: need 4 descriptions, got {len(descs)}")
    if len(set(headlines)) != len(headlines):
        raise SystemExit(f"{where}: duplicate headlines")
    if len(set(descs)) != 4:
        raise SystemExit(f"{where}: duplicate descriptions")
    for i, h in enumerate(headlines, 1):
        n = rsa_len(h)
        if not (1 <= n <= HL_MAX):
            raise SystemExit(f"{where} H{i} len {n}: {h!r}")
        if h != h.strip():
            raise SystemExit(f"{where} H{i} has edge whitespace")
    for i, d in enumerate(descs, 1):
        n = rsa_len(d)
        if not (1 <= n <= DESC_MAX):
            raise SystemExit(f"{where} D{i} len {n}: {d!r}")
    blob = " ".join(headlines + descs)
    if JOB_SEEKER_RE.search(blob):
        raise SystemExit(f"{where}: job-seeker language: {JOB_SEEKER_RE.search(blob).group(0)}")
    if JUNK_RE.search(blob):
        raise SystemExit(f"{where}: junk phrase: {JUNK_RE.search(blob).group(0)}")
    if CLAIM_RE.search(blob):
        raise SystemExit(f"{where}: forbidden claim: {CLAIM_RE.search(blob).group(0)}")
    if CONSULT_RE.search(blob):
        raise SystemExit(f"{where}: consult/demo language")
    dki = DKI_RE.findall(blob)
    if len(dki) > 1:
        raise SystemExit(f"{where}: more than one DKI")
    banned = json.loads(BANNED_PATH.read_text(encoding="utf-8")).get("phrases") or []
    blob_l = blob.lower()
    for phrase in banned:
        if phrase and phrase.lower() in blob_l:
            raise SystemExit(f"{where}: banned public-copy phrase {phrase!r}")


# ---------------------------------------------------------------------------
# RSA catalog
# Each entry: market, campaign, ad_group, bucket, angle, url_path, p1, p2,
# headlines, descs, why
# bucket: trust | weak | semantic | low_data_skip
# ---------------------------------------------------------------------------


def catalog() -> list[dict]:
    rows: list[dict] = []

    def add(
        *,
        market: str,
        campaign: str,
        ad_group: str,
        bucket: str,
        angle: str,
        url_path: str,
        p1: str,
        p2: str,
        headlines: list[str],
        descs: list[str],
        why: str,
    ) -> None:
        where = f"{market}/{campaign}/{ad_group}/{angle}"
        validate_rsa(headlines, descs, where)
        if rsa_len(p1) > PATH_MAX or rsa_len(p2) > PATH_MAX:
            raise SystemExit(f"{where}: path too long {p1!r} {p2!r}")
        rows.append(
            {
                "market": market,
                "campaign": campaign,
                "ad_group": ad_group,
                "bucket": bucket,
                "angle": angle,
                "url_path": url_path,
                "p1": p1,
                "p2": p2,
                "headlines": headlines,
                "descs": descs,
                "why": why,
            }
        )

    # ===== US TRUST-MAPPED =====
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Hire_VA_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us",
        p1="hire",
        p2="va",
        headlines=[
            "Hire a Virtual Assistant",
            "How to Hire a VA",
            "Hire Dedicated Remote Staff",
            "Tell Us Who You Need",
            "You Interview. You Decide.",
            "Dedicated Filipino Assistants",
            "Not a Gig Marketplace",
            "Add Support Without the Drag",
            "Find Skilled Remote Talent",
            "We Shortlist. You Choose.",
            "For Growing US Businesses",
            "Spend Less Time Hiring",
            "A Named Teammate, Not Tasks",
            "Get the Seat You Actually Need",
            "{KeyWord:Hire a Virtual Assistant}",
        ],
        descs=[
            "Tell us who you need. We recruit and screen. You interview before anyone starts.",
            "Hire a dedicated virtual assistant in the Philippines for your US hours.",
            "This is a staffing company, not a freelance app. You keep the hire decision.",
            "Built for businesses adding staff — not for people looking for work.",
        ],
        why="Intent+clarity for hire-a-VA searches. Matches /us H1 and winning 'you interview' theme.",
    )
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Hire_VA_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us",
        p1="staffing",
        p2="hire",
        headlines=[
            "Staffing Company Since 2011",
            "Hire Proven Remote Talent",
            "Screened People. You Decide.",
            "Trusted Hiring, Less Friction",
            "Build Your Team With Less Drag",
            "You Meet Finalists First",
            "Dedicated Seat, Not a Bench",
            "We Handle Payroll After Hire",
            "US Hours. One Named Person.",
            "Growing Teams Hire This Way",
            "Talk to Our Staffing Team",
            "Real Shortlist. Real Company.",
            "Skip Sorting Applicants",
            "Keep Overhead Off This Seat",
            "A Partner, Not a Platform",
        ],
        descs=[
            "Virtual Coworker has recruited dedicated Filipino staff for businesses since 2011.",
            "We shortlist. You interview. After you hire, we handle payroll and stay on support.",
            "A staffing company with US and Australia offices — not a freelance marketplace.",
            "Tell us the seat. We'll help you find the person. Nobody starts until you say yes.",
        ],
        why="Trust+employer outcome. Uses substantiated since-2011 / you-interview / we-employ proof.",
    )

    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Offshore_VA_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us",
        p1="philippines",
        p2="va",
        headlines=[
            "Philippines Virtual Assistant",
            "Filipino Virtual Assistants",
            "Hire Remote Staff Overseas",
            "Virtual Assistant Philippines",
            "Dedicated Philippines Staff",
            "Offshore Help You Interview",
            "One Person. Your US Hours.",
            "Not Rotating Freelancers",
            "Outsource the Seat. You Pick.",
            "Remote Talent for US Teams",
            "Tell Us the Role You Need",
            "Staffing, Not a Marketplace",
            "Hire Filipino Remote Support",
            "A Dedicated Offshore Seat",
            "Get Philippines Staff On Hours",
        ],
        descs=[
            "Hire a dedicated virtual assistant in the Philippines who works your US hours.",
            "We recruit and vet Filipino staff. You interview. Nobody starts without your yes.",
            "Offshore help with a named person — not a rotating freelance bench.",
            "Tell us the role. We shortlist. You decide who joins your team.",
        ],
        why="Direct-response for philippines/filipino VA terms that historically convert.",
    )
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Offshore_VA_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us",
        p1="offshore",
        p2="trust",
        headlines=[
            "Recruited Since 2011",
            "Screened Filipino Talent",
            "You Interview the Shortlist",
            "Established Staffing Partner",
            "Dedicated, Not Freelance",
            "We Employ Them After You Hire",
            "Trusted Offshore Hiring",
            "Reduce Hiring Friction",
            "Named Teammate on Your Hours",
            "A Company Behind the Hire",
            "Talk Through the Role First",
            "Not a Freelance Marketplace",
            "Scale the Team, Not Overhead",
            "Philippines Staff You Choose",
            "Real Offices. Real Recruiting.",
        ],
        descs=[
            "An established staffing company. Philippines recruiting. You keep the hire decision.",
            "Screened Filipino talent for US hours. You meet them before they join.",
            "After you hire, we employ them and handle payroll. You manage the work.",
            "Growing teams use this when they want a person, not a gig listing.",
        ],
        why="Trust challenger against robotic 'Offshore VA PH' / 'Staffing Seat Evidence' incumbents.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Bookkeeping_Hire_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us/bookkeeping",
        p1="bookkeeping",
        p2="hire",
        headlines=[
            "Hire a Philippines Bookkeeper",
            "Hire a Dedicated Bookkeeper",
            "Bookkeeping Support for Hire",
            "Invoices, Bills, Reconciles",
            "QuickBooks or Xero Support",
            "Day-to-Day Books Support",
            "You Interview the Bookkeeper",
            "Not a Books Freelance Bench",
            "Tell Us Your Books Stack",
            "Dedicated Books Seat",
            "Month-End Without the Scramble",
            "Remote Bookkeeper, Your Hours",
            "Hire Books Help, Keep Your CPA",
            "Get a Bookkeeping Shortlist",
            "Routine Reconciles Covered",
        ],
        descs=[
            "Hire a dedicated Filipino bookkeeper for invoices, records, and reconciliations.",
            "Tell us QuickBooks, Xero, or what you use. You interview before anyone starts.",
            "Day-to-day books support on your US hours — not licensed accounting advice.",
            "We recruit against the seat. You keep your CPA for judgment work.",
        ],
        why="Role-specific books language aligned to live /us/bookkeeping H1.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Bookkeeping_Hire_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us/bookkeeping",
        p1="books",
        p2="team",
        headlines=[
            "Screened Bookkeeping Talent",
            "Staffing for Your Books Seat",
            "You Meet Them First",
            "Trusted Books Support",
            "Recruited for Your Tools",
            "We Handle Payroll After Hire",
            "A Person Who Owns the Books",
            "Support, Not Licensed Advice",
            "Talk to Our Staffing Team",
            "Growing Teams Add Books Help",
            "Keep Your CPA. Add Capacity.",
            "Real Company Behind the Seat",
            "Skip the Books Freelance Hunt",
            "Dedicated Bookkeeper Hiring",
            "Your Hours. Named Bookkeeper.",
        ],
        descs=[
            "We recruit and vet bookkeeping support. You interview. We handle payroll after you hire.",
            "A staffing company since 2011 — not a rotating freelance books bench.",
            "One dedicated person on your hours so month-end is not a scramble.",
            "Tell us the tools and the close rhythm. We'll help you find the seat.",
        ],
        why="Trust+continuity for the strongest role URL in recent GA4 notes.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Customer_Service_Hire_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us/customer-service",
        p1="support",
        p2="hire",
        headlines=[
            "Hire Customer Service Staff",
            "Dedicated Support Seat",
            "Email, Chat, or Tickets",
            "Hire Philippines Support Staff",
            "Customer Service for US Hours",
            "You Interview Support Staff",
            "Not a Call-Center Dump",
            "Someone Who Knows Your Product",
            "Tell Us the Channels You Cover",
            "Dedicated Inbox and Chat Help",
            "Hire Support, Keep Your Voice",
            "Get a Support Shortlist",
            "Remote Customer Care Staff",
            "A Named Person on the Queue",
            "Order Updates That Don't Sit",
        ],
        descs=[
            "Hire dedicated Filipino customer service staff for email, chat, or tickets.",
            "One named person on your US hours — not a rotating freelance roster.",
            "Tell us the channels. We shortlist. You interview before anyone starts.",
            "Support that sounds like your team. You keep the hire decision.",
        ],
        why="Queue/channel language matches live CS LP and customer-service VA search terms.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Customer_Service_Hire_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us/customer-service",
        p1="care",
        p2="team",
        headlines=[
            "Screened Support Talent",
            "Trusted Customer Care Hiring",
            "Meet Them Before They Start",
            "Dedicated Seat, Not a Roster",
            "Staffing for Your Support Desk",
            "We Employ Them After You Hire",
            "Consistent Replies, Your Hours",
            "Talk Through the Support Seat",
            "Growing Teams Add Support Here",
            "Not Freelance Ticket Hopping",
            "Real Recruiting for Care Roles",
            "A Company Behind the Queue",
            "You Choose Who Joins Support",
            "Reduce Queue Backlog",
            "Screened Agents. Your Voice.",
        ],
        descs=[
            "We recruit customer service staff. You interview. After you hire, we handle payroll.",
            "Consistent replies from a dedicated seat — not a freelance ticket hop.",
            "Staffing since 2011 for US businesses that want someone they have met.",
            "Tell us the product and the hours. We'll help you find the person.",
        ],
        why="Trust challenger; CS LP already shows stronger engagement than other role pages.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Sales_Hire_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us/sales",
        p1="sales",
        p2="support",
        headlines=[
            "Hire Sales Support Staff",
            "CRM Follow-Up for Hire",
            "Sales Admin, Not Cold Calling",
            "Pipeline Follow-Up Support",
            "Hire a Sales Support Seat",
            "Research and CRM Hygiene",
            "You Interview Sales Support",
            "Lists, Notes, Next Steps",
            "Not a Dialer Farm",
            "Tell Us the Sales Seat",
            "Dedicated Follow-Up Help",
            "Closers Stay With Buyers",
            "Remote Sales Admin Staff",
            "Get a Sales Support Shortlist",
            "Hire Help for the Pipeline",
        ],
        descs=[
            "Hire sales support for CRM hygiene, research, and follow-up — not a cold-call farm.",
            "A dedicated Filipino teammate so closers spend time with buyers, not the CRM.",
            "You interview before anyone starts. Appointment setting only if that is the brief.",
            "Tell us the pipeline work. We shortlist. You decide who joins.",
        ],
        why="Follow-up/CRM language from the sales trust page. Avoids setter-only pitch.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Sales_Hire_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us/sales",
        p1="pipeline",
        p2="hire",
        headlines=[
            "Screened Sales Support Talent",
            "Trusted Pipeline Admin Hiring",
            "You Meet Them Before Outreach",
            "Dedicated CRM Owner",
            "Staffing for Follow-Up Work",
            "We Stay On After You Hire",
            "Support Seat, Not a Closer",
            "Talk Through the Sales Brief",
            "Growing Teams Add Follow-Up",
            "Not Appointment-Setter Only",
            "Real Company. Real Shortlist.",
            "Reduce Follow-Up Drop-Off",
            "Your CRM. Your Hours.",
            "Hire Support Around Closers",
            "Skip the Freelance SDR Shuffle",
        ],
        descs=[
            "We recruit sales support staff. You interview. We handle payroll after you hire.",
            "Follow-up and CRM owned by one person — not a rotating setter bench.",
            "An established staffing company. You keep the hire decision.",
            "Tell us the CRM and the work. We'll help you find the seat.",
        ],
        why="Trust+employer outcome; keeps setter groups from leaking into this RSA.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Administration_EA_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us/administrative-support",
        p1="admin",
        p2="hire",
        headlines=[
            "Hire an Executive Assistant",
            "Hire Admin Support Staff",
            "Inbox and Calendar Help",
            "Dedicated Filipino Assistant",
            "Virtual Assistant for Admin",
            "Follow-Ups That Don't Slip",
            "You Interview Your Assistant",
            "Documents, Scheduling, Inbox",
            "Tell Us the Admin Seat",
            "A Named Assistant, Your Hours",
            "Not a Vague VA Promise",
            "Get an Admin Shortlist",
            "Hire Help for the Inbox",
            "Remote Executive Support",
            "Leadership Hours Back to Work",
        ],
        descs=[
            "Hire a dedicated Filipino assistant for inbox, calendar, documents, and follow-ups.",
            "Clear admin work on your US hours. You interview before anyone starts.",
            "Tell us whether you need an EA or day-to-day admin. We recruit for that seat.",
            "A named person so leadership time goes back to customers and decisions.",
        ],
        why="Inbox/calendar language matches admin trust H1. Replaces '{KeyWord:Hire Virtual EA}'.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Administration_EA_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us/administrative-support",
        p1="ea",
        p2="team",
        headlines=[
            "Screened Admin Talent",
            "Trusted Assistant Hiring",
            "You Meet Them Before Day One",
            "Dedicated Inbox Owner",
            "Staffing for EA and Admin",
            "We Employ After You Hire",
            "Clear Admin Work, Named Person",
            "Talk Through the Admin Brief",
            "Growing Teams Hire Assistants",
            "Not Marketplace Admin Tasks",
            "Calendar That Doesn't Bounce",
            "Real Recruiting Since 2011",
            "Skip Sorting EA Applicants",
            "A Partner for Your Ops Load",
            "Reduce the Admin Drag",
        ],
        descs=[
            "We recruit and vet admin and EA talent. You interview. We stay on after you hire.",
            "Staffing since 2011 for US teams that want a person, not task-marketplace admin.",
            "Inbox and calendar owned by someone you have met — not a shared freelancer.",
            "Tell us the day-to-day. We'll help you find the assistant.",
        ],
        why="Trust rescue for the weakest role LP engagement and robotic EA DKI.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Digital_Marketing_Hire_PH",
        bucket="trust",
        angle="A_intent",
        url_path="/us/digital-marketing",
        p1="marketing",
        p2="hire",
        headlines=[
            "Hire Marketing Support Staff",
            "Campaign Ops for Hire",
            "Reporting and Content Ops",
            "Hire a Marketing Coordinator",
            "Digital Marketing Support",
            "You Interview Marketing Staff",
            "Not a Strategy Retainer Shop",
            "Tell Us the Marketing Seat",
            "Campaign Checklists Owned",
            "Content Ops Without the Fire",
            "Dedicated Marketing Seat",
            "Get a Marketing Shortlist",
            "Hire Execution, Keep Strategy",
            "Remote Campaign Support",
            "Tools You Already Use",
        ],
        descs=[
            "Hire dedicated marketing support for campaigns, reporting, and content ops.",
            "Execution work with an owner — not a strategy retainers pitch.",
            "Tell us the tools. We shortlist. You interview before anyone starts.",
            "Strategists stay on judgment. This seat owns the day-to-day.",
        ],
        why="Execution/ops language from the marketing trust page, not 'Scale Marketing Bandwidth'.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Digital_Marketing_Hire_PH",
        bucket="trust",
        angle="B_trust",
        url_path="/us/digital-marketing",
        p1="marketing",
        p2="team",
        headlines=[
            "Screened Marketing Talent",
            "Trusted Marketing Hiring",
            "You Meet Them Before Campaigns",
            "Dedicated Channel Support",
            "Staffing for Marketing Ops",
            "We Stay On After You Hire",
            "Execution Seat, Your Tools",
            "Talk Through Marketing Work",
            "Growing Teams Add Ops Help",
            "Not Freelance Campaign Churn",
            "Reporting Pulls, Not Rebuilds",
            "Real Company Behind the Seat",
            "Hire Help for Content Ops",
            "Reduce Marketing Busywork",
            "A Partner for Campaign Ops",
        ],
        descs=[
            "We recruit marketing support staff. You interview. We handle payroll after you hire.",
            "Campaign coordination and reporting owned by one person you have met.",
            "An established staffing company — not a freelance campaign bench.",
            "Tell us the work. We'll help you find the seat.",
        ],
        why="Trust+continuity for a role page with softer engagement and robotic DKI incumbents.",
    )

    # ===== US WEAK CREATIVE (not already in trust set) =====
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Social_Media_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/us/social-media",
        p1="social",
        p2="hire",
        headlines=[
            "Hire a Social Media Manager",
            "Instagram Scheduling Support",
            "LinkedIn Outreach Support",
            "Community Management Hire",
            "Social Posting and Replies",
            "Hire Social Media Staff",
            "You Interview Social Finalists",
            "Content Calendar Ownership",
            "Facebook and Instagram Help",
            "LinkedIn Inbox and Follow-Up",
            "Tell Us the Channels You Run",
            "Dedicated Social Seat",
            "Get a Social Shortlist",
            "Reporting on What You Posted",
            "Not Random Freelance Posts",
        ],
        descs=[
            "Hire a dedicated social media manager for scheduling, replies, and community work.",
            "Instagram, Facebook, LinkedIn — tell us the channels. You interview the shortlist.",
            "A named person owns the calendar so posting does not fall behind.",
            "Staffing for US teams. Not a caption marketplace and not a job board.",
        ],
        why="Role-specific Instagram/LinkedIn/community language. Replaces 'Filipino SMM' / DKI junk.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Social_Media_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/us/social-media",
        p1="social",
        p2="team",
        headlines=[
            "Screened Social Media Talent",
            "Trusted Social Hiring",
            "You Meet Them Before They Post",
            "Dedicated Community Manager",
            "Staffing for Social Channels",
            "We Employ Them After You Hire",
            "Consistent Posting, Your Hours",
            "Talk Through the Social Brief",
            "Growing Teams Add Social Help",
            "Not a Caption Marketplace",
            "Instagram, LinkedIn, or Both",
            "Real Recruiting for Social",
            "Engagement Without the Chase",
            "A Partner for Channel Ops",
            "Your Voice. A Named Person.",
        ],
        descs=[
            "We recruit social media staff. You interview. After you hire, we handle payroll.",
            "Scheduling, engagement, and reporting owned by someone you have met.",
            "Staffing since 2011. Dedicated seat on your hours — not freelance post batches.",
            "Tell us Instagram, LinkedIn, or the mix. We'll help you find the person.",
        ],
        why="Trust challenger for a live role page with robotic incumbents and real buyer searches.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Accounting_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/us/accounting",
        p1="accounting",
        p2="hire",
        headlines=[
            "Hire an Accountant Overseas",
            "Hire Philippines Accounting",
            "AP and AR Support for Hire",
            "Dedicated Accounting Staff",
            "Ledger and Payroll Admin",
            "You Interview Accounting Staff",
            "Not Freelance Finance Mix",
            "Tell Us the Accounting Seat",
            "Accounts Payable Support",
            "Remote Staff Accountant",
            "Get an Accounting Shortlist",
            "Hire Finance Ops Support",
            "Day-to-Day Accounting Help",
            "Your Stack. Your Hours.",
            "Dedicated AP Capacity",
        ],
        descs=[
            "Hire dedicated Filipino accounting staff for AP, AR, and day-to-day finance ops.",
            "You interview before anyone starts. Licensed advice stays with your accountant.",
            "Tell us the stack. We shortlist a named person for your US hours.",
            "Staffing for finance ops — not a freelance bookkeeping mix.",
        ],
        why="Human replacement for '{KeyWord:Hire Accountant}' and 'Scale Finance Bandwidth'.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Accounting_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/us/accounting",
        p1="finance",
        p2="hire",
        headlines=[
            "Screened Accounting Talent",
            "Trusted Finance Seat Hiring",
            "You Meet Them Before Close",
            "Dedicated Accounting Seat",
            "Staffing for Finance Ops",
            "We Stay On After You Hire",
            "Not a Contractor Bench",
            "Talk Through the Finance Brief",
            "Growing Teams Add Finance Help",
            "Real Company Behind the Books",
            "Payroll Admin, Not Advice",
            "Reduce the Close Scramble",
            "Named Person on the Ledger",
            "Skip Freelance Accounting Hunt",
            "Recruited Against Your Tools",
        ],
        descs=[
            "We recruit accounting support. You interview. We handle payroll after you hire.",
            "A staffing company since 2011. Continuity through close, not contractor churn.",
            "Day-to-day finance ops on your hours. Judgment work stays with your controller.",
            "Tell us AP, AR, or payroll admin. We'll help you find the seat.",
        ],
        why="Trust challenger; accounting outsourcing is a proven historical employer term.",
    )

    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Accounting_Outsource_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/us/accounting",
        p1="outsource",
        p2="acct",
        headlines=[
            "Outsource Accounting Work",
            "Philippines Accounting Help",
            "Outsource AP and AR",
            "Dedicated Outsourced Finance",
            "You Interview First",
            "Not a Rotating Finance Bench",
            "Outsource Finance. You Decide.",
            "Tell Us What to Hand Off",
            "Ongoing Accounting Capacity",
            "Remote Accounting Partner",
            "Get an Outsourcing Shortlist",
            "Keep the Controller. Add Help.",
            "Staff Outsourced Finance Seats",
            "Dedicated Accounting Seat",
            "Outsource the Ledger Work",
        ],
        descs=[
            "Outsource day-to-day accounting support to a dedicated Philippines teammate.",
            "You interview first. We recruit and vet. You keep review authority.",
            "AP, AR, and routine finance ops — not a rotating contractor bench.",
            "Tell us what to hand off. We'll help you find the person.",
        ],
        why="Matches historical 'philippines accounting outsourcing' buyer language.",
    )
    add(
        market="US",
        campaign="VC_US_S_ROLES",
        ad_group="Accounting_Outsource_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/us/accounting",
        p1="outsource",
        p2="trust",
        headlines=[
            "Screened Finance Talent",
            "Trusted Accounting Outsourcing",
            "We Employ After You Hire",
            "Reduce US Finance Overhead",
            "Talk Through What to Outsource",
            "Firms Outsource Finance Here",
            "Not Marketplace Bookkeepers",
            "Real Agency Behind the Seat",
            "Named Accountant on Your Hours",
            "Continuity Through Close",
            "A Partner, Not a Temp Desk",
            "You Keep Review Authority",
            "Staffing Company Since 2011",
            "Dedicated Seat You Can Keep",
            "Outsource. Keep the Control.",
        ],
        descs=[
            "An established staffing company. You meet the person. We stay on after you hire.",
            "Outsource the seat without giving up the hire decision.",
            "Dedicated finance ops on your hours — not marketplace bookkeepers.",
            "Talk through the work. We'll help you find a teammate you can keep.",
        ],
        why="Trust challenger for outsourcing-intent searches already proven in account history.",
    )

    # ===== US SEMANTIC / AGENCY (only post if those AGs already exist) =====
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Staffing_Agency_PH",
        bucket="semantic",
        angle="A_intent",
        url_path="/us",
        p1="staffing",
        p2="agency",
        headlines=[
            "Remote Staffing Agency",
            "Philippines Staffing Agency",
            "Hire Through a Staffing Firm",
            "Dedicated Remote Staffing",
            "Staffing for US Employers",
            "You Interview Every Hire",
            "Not a Temp Job Board",
            "Tell Us How Many Seats",
            "Offshore Staffing Partner",
            "Dedicated Filipino Staff",
            "We Recruit. You Decide.",
            "Staffing, Not Gig Work",
            "Add a Team Without US Payroll",
            "Remote Staff You Can Keep",
            "Get a Staffing Shortlist",
        ],
        descs=[
            "A Philippines remote staffing partner for US businesses that want dedicated seats.",
            "We recruit and vet. You interview. After you hire, we handle payroll.",
            "Staffing company, not a temp board and not a freelance marketplace.",
            "Tell us how many people you need. We'll help you find them.",
        ],
        why="Intent match for remote/PH staffing agency searches. Lands live /us, not preview.",
    )
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Staffing_Agency_PH",
        bucket="semantic",
        angle="B_trust",
        url_path="/us",
        p1="staffing",
        p2="trust",
        headlines=[
            "Staffing Company Since 2011",
            "A Partner for Growing Teams",
            "Screened Talent, Your Hours",
            "We Stay On After You Hire",
            "Trusted Remote Staffing",
            "You Keep the Hire Decision",
            "Dedicated Seats, Not Temps",
            "US and Australia Offices",
            "Reduce the Hiring Load",
            "Talk to Our Staffing Team",
            "Built for Employers",
            "Not a Marketplace Listing",
            "Hire a Small Remote Pod",
            "Payroll Stays With Us",
            "Real Recruiting. Real Support.",
        ],
        descs=[
            "Virtual Coworker has staffed dedicated Filipino teammates for businesses since 2011.",
            "You interview. If it is not the right person, they do not join your team.",
            "US and Australia offices. Philippines recruiting. We stay on after you hire.",
            "Use this when you want a staffing company, not a personal concierge app.",
        ],
        why="Trust language for staffing-agency buyers. Watch temp/job bleed in search terms.",
    )

    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="VA_Agency_Firm_PH",
        bucket="semantic",
        angle="A_intent",
        url_path="/us",
        p1="agency",
        p2="va",
        headlines=[
            "Virtual Assistant Agency",
            "Hire a VA Agency, Not a Gig",
            "Filipino Assistant Agency",
            "VA Company for Businesses",
            "Virtual Assistant Firm",
            "Agency Recruiting for You",
            "You Meet the Shortlist",
            "Not a Job Board",
            "Dedicated Assistants On Staff",
            "Tell Us the Seat You Need",
            "Agency Model. You Decide.",
            "Hire Through the Agency",
            "One Dedicated Assistant",
            "Skip Marketplace Guesswork",
            "An Agency You Meet First",
        ],
        descs=[
            "A virtual assistant agency that recruits dedicated Filipino staff. You interview first.",
            "We are the agency. You meet the shortlist. After you hire, we employ them.",
            "For businesses hiring a seat — not a job board and not a freelance listing.",
            "Tell us the role. We'll help you find the person.",
        ],
        why="Agency/firm/company are live buyer terms. Copy reads as a firm, not VA jobs.",
    )
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="VA_Agency_Firm_PH",
        bucket="semantic",
        angle="B_trust",
        url_path="/us",
        p1="agency",
        p2="trust",
        headlines=[
            "An Agency, Not a Listing",
            "Staffing Agency Since 2011",
            "You Interview. We Employ.",
            "Trusted VA Hiring Partner",
            "Screened Assistants Ready",
            "Growing Firms Hire This Way",
            "We Recruit Against Your Brief",
            "Nobody Starts Without You",
            "Dedicated Seat Through Us",
            "Talk to the Agency First",
            "Payroll and HR Stay With Us",
            "Real Company Behind the Hire",
            "Not Freelance Task Work",
            "Build the Seat, Keep Control",
            "Established Hiring Process",
        ],
        descs=[
            "Agency recruiting against your brief. You keep the hire decision.",
            "Staffing since 2011. Dedicated assistants, not a pile of random resumes.",
            "After you hire, payroll and HR stay with us. You manage the work.",
            "Talk to the agency first. We'll help you find the right seat.",
        ],
        why="Trust+agency proof. Differentiates from Magic-style concierge and marketplace listings.",
    )

    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Agency_PH",
        bucket="semantic",
        angle="A_intent",
        url_path="/us",
        p1="outsource",
        p2="agency",
        headlines=[
            "Philippines Outsourcing Agency",
            "Outsourcing Agency for Hire",
            "Hire an Outsourcing Partner",
            "Dedicated Outsourced Staff",
            "Outsource a Role Overseas",
            "You Interview Outsourced Staff",
            "Not a Freelance Bench",
            "Agency-Led Outsourcing",
            "Tell Us What to Outsource",
            "Dedicated Seat, Not a Pool",
            "Remote Ops Without US Hire",
            "Staffing for Outsourced Roles",
            "Keep Control of the Hire",
            "Outsource Work, Keep Quality",
            "Get an Outsourcing Shortlist",
        ],
        descs=[
            "A Philippines outsourcing agency for dedicated seats — not a freelance bench.",
            "You interview the person. We recruit and vet. You keep control of the hire.",
            "Tell us the role to hand off. We'll help you find a teammate, not a task pool.",
            "Built for businesses outsourcing work, not for people looking for work.",
        ],
        why="Matches 'philippines outsourcing agency' buyer signal from the live account.",
    )
    add(
        market="US",
        campaign="VC_US_S_CORE",
        ad_group="Agency_PH",
        bucket="semantic",
        angle="B_trust",
        url_path="/us",
        p1="outsource",
        p2="firm",
        headlines=[
            "Outsourcing Partner Since 2011",
            "A Staffing Firm, Not a Gig",
            "Screened People You Meet",
            "Trusted Outsourcing Partner",
            "We Employ After You Hire",
            "Reduce US Overhead on the Seat",
            "Dedicated Outsourced Teammate",
            "You Choose Who Joins",
            "Talk Through the Role",
            "Real Agency. Real Support.",
            "Not a Contractor Roulette",
            "Growing Teams Outsource Here",
            "Named Person on Your Hours",
            "US and Australia Offices",
            "Keep the Work. Share the Hire.",
        ],
        descs=[
            "Established staffing firm. You meet the person. We employ them after you hire.",
            "Outsource a dedicated seat without turning the work into contractor roulette.",
            "US and Australia offices. Philippines recruiting. You keep the hire decision.",
            "Talk through the role. We'll help you find someone you can keep.",
        ],
        why="Trust challenger for outsourcing-agency intent already seen in search terms.",
    )

    # ===== AU WEAK RESCUE (no US trust pages; same live role URLs) =====
    add(
        market="AU",
        campaign="VC_AU_S_CORE",
        ad_group="Hire_VA_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au",
        p1="hire",
        p2="va",
        headlines=[
            "Hire a Virtual Assistant",
            "Hire Help for Your Team",
            "Dedicated Filipino Staff",
            "You Interview. You Decide.",
            "Tell Us Who You Need",
            "Not a Freelance Marketplace",
            "How to Hire a VA",
            "Find Skilled Remote Talent",
            "We Shortlist. You Choose.",
            "For Australian Businesses",
            "Spend Less Time Hiring",
            "A Named Teammate, Not Tasks",
            "Get the Seat You Actually Need",
            "Add Support Without the Drag",
            "Hire Dedicated Remote Staff",
        ],
        descs=[
            "Tell us who you need. We recruit and screen. You interview before anyone starts.",
            "Hire a dedicated virtual assistant in the Philippines for Australian hours.",
            "A staffing company, not a freelance app. You keep the hire decision.",
            "For Australian businesses adding staff — not for people looking for work.",
        ],
        why="AU hire-intent challenger. Replaces robotic 'Hire Virtual Assistant PH' incumbents.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_CORE",
        ad_group="Hire_VA_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au",
        p1="staffing",
        p2="hire",
        headlines=[
            "Staffing Company Since 2011",
            "Hire Proven Remote Talent",
            "Screened People. You Decide.",
            "Trusted Hiring, Less Friction",
            "You Meet Finalists First",
            "Dedicated Seat, Not a Bench",
            "We Handle Payroll After Hire",
            "Your Hours. One Named Person.",
            "Talk to Our Staffing Team",
            "Real Shortlist. Real Company.",
            "Skip Sorting Applicants",
            "A Partner, Not a Platform",
            "A Sydney Office Behind You",
            "Build the Team With Less Drag",
            "Growing Teams Hire This Way",
        ],
        descs=[
            "Virtual Coworker has recruited dedicated Filipino staff for businesses since 2011.",
            "We shortlist. You interview. After you hire, we handle payroll and stay on support.",
            "Sydney and US offices. Philippines recruiting. Not a freelance marketplace.",
            "Tell us the seat. We'll help you find the person. Nobody starts until you say yes.",
        ],
        why="AU trust challenger. Same process proof, quieter B2B tone.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_CORE",
        ad_group="Offshore_VA_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au",
        p1="philippines",
        p2="va",
        headlines=[
            "Philippines Virtual Assistant",
            "Filipino Virtual Assistants",
            "Hire Remote Staff Overseas",
            "Virtual Assistant Philippines",
            "Dedicated Philippines Staff",
            "Offshore Help You Interview",
            "One Person. Your Hours.",
            "Not Rotating Freelancers",
            "Outsource the Seat. You Pick.",
            "Remote Talent for AU Teams",
            "Tell Us the Role You Need",
            "Staffing, Not a Marketplace",
            "Hire Filipino Remote Support",
            "A Dedicated Offshore Seat",
            "Philippines Staff on AU Hours",
        ],
        descs=[
            "Hire a dedicated virtual assistant in the Philippines who works Australian hours.",
            "We recruit and vet. You interview. Nobody starts without your yes.",
            "Offshore help with a named person — not a rotating freelance bench.",
            "Tell us the role. We shortlist. You decide who joins.",
        ],
        why="AU offshore intent. Same winning PH/Filipino terms, Australian hours.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_CORE",
        ad_group="Offshore_VA_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au",
        p1="offshore",
        p2="trust",
        headlines=[
            "Recruited Since 2011",
            "Screened Filipino Talent",
            "You Interview the Shortlist",
            "Established Staffing Partner",
            "Dedicated, Not Freelance",
            "We Employ Them After You Hire",
            "Trusted Offshore Hiring",
            "Reduce Hiring Friction",
            "Named Teammate on Your Hours",
            "A Company Behind the Hire",
            "Talk Through the Role First",
            "Not a Freelance Marketplace",
            "Scale the Team, Not Overhead",
            "Philippines Staff You Choose",
            "Sydney Office. Real Support.",
        ],
        descs=[
            "An established staffing company. Philippines recruiting. You keep the hire decision.",
            "Screened Filipino talent for Australian hours. You meet them before they join.",
            "After you hire, we employ them and handle payroll. You manage the work.",
            "For Australian businesses that want a person, not a gig listing.",
        ],
        why="AU trust challenger for robotic offshore incumbents.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Social_Media_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au/social-media",
        p1="social",
        p2="hire",
        headlines=[
            "Hire a Social Media Manager",
            "Instagram Scheduling Support",
            "LinkedIn Outreach Support",
            "Community Management Hire",
            "Social Posting and Replies",
            "Hire Social Media Staff",
            "You Interview Social Finalists",
            "Content Calendar Ownership",
            "Facebook and Instagram Help",
            "LinkedIn Inbox and Follow-Up",
            "Tell Us the Channels You Run",
            "Dedicated Social Seat",
            "Get a Social Shortlist",
            "Reporting on What You Posted",
            "Not Random Freelance Posts",
        ],
        descs=[
            "Hire a dedicated social media manager for scheduling, replies, and community work.",
            "Instagram, Facebook, LinkedIn — tell us the channels. You interview the shortlist.",
            "A named person owns the calendar so posting does not fall behind.",
            "For Australian businesses. Not a caption marketplace and not a job board.",
        ],
        why="AU social rescue. Same role language as US, Australian employer frame.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Social_Media_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au/social-media",
        p1="social",
        p2="team",
        headlines=[
            "Screened Social Media Talent",
            "Trusted Social Hiring",
            "You Meet Them Before They Post",
            "Dedicated Community Manager",
            "Staffing for Social Channels",
            "We Employ Them After You Hire",
            "Consistent Posting, Your Hours",
            "Talk Through the Social Brief",
            "Growing Teams Add Social Help",
            "Not a Caption Marketplace",
            "Instagram, LinkedIn, or Both",
            "Real Recruiting for Social",
            "Engagement Without the Chase",
            "A Partner for Channel Ops",
            "Your Voice. A Named Person.",
        ],
        descs=[
            "We recruit social media staff. You interview. After you hire, we handle payroll.",
            "Scheduling, engagement, and reporting owned by someone you have met.",
            "Staffing since 2011. Dedicated seat on Australian hours.",
            "Tell us Instagram, LinkedIn, or the mix. We'll help you find the person.",
        ],
        why="AU social trust challenger.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Administration_EA_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au/administrative-support",
        p1="admin",
        p2="hire",
        headlines=[
            "Hire an Executive Assistant",
            "Hire Admin Support Staff",
            "Inbox and Calendar Help",
            "Dedicated Filipino Assistant",
            "Virtual Assistant for Admin",
            "Follow-Ups That Don't Slip",
            "You Interview Your Assistant",
            "Documents, Scheduling, Inbox",
            "Tell Us the Admin Seat",
            "A Named Assistant, Your Hours",
            "Not a Vague VA Promise",
            "Get an Admin Shortlist",
            "Hire Help for the Inbox",
            "Remote Executive Support",
            "Leadership Hours Back to Work",
        ],
        descs=[
            "Hire a dedicated Filipino assistant for inbox, calendar, documents, and follow-ups.",
            "Clear admin work on Australian hours. You interview before anyone starts.",
            "Tell us whether you need an EA or day-to-day admin. We recruit for that seat.",
            "A named person so leadership time goes back to customers and decisions.",
        ],
        why="AU admin rescue. Same inbox/calendar message as the live role page.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Administration_EA_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au/administrative-support",
        p1="ea",
        p2="team",
        headlines=[
            "Screened Admin Talent",
            "Trusted Assistant Hiring",
            "You Meet Them Before Day One",
            "Dedicated Inbox Owner",
            "Staffing for EA and Admin",
            "We Employ After You Hire",
            "Clear Admin Work, Named Person",
            "Talk Through the Admin Brief",
            "Growing Teams Hire Assistants",
            "Not Marketplace Admin Tasks",
            "Calendar That Doesn't Bounce",
            "Real Recruiting Since 2011",
            "Skip Sorting EA Applicants",
            "A Partner for Your Ops Load",
            "Reduce the Admin Drag",
        ],
        descs=[
            "We recruit and vet admin and EA talent. You interview. We stay on after you hire.",
            "Staffing since 2011 for Australian teams that want a person, not task-marketplace admin.",
            "Inbox and calendar owned by someone you have met — not a shared freelancer.",
            "Tell us the day-to-day. We'll help you find the assistant.",
        ],
        why="AU admin trust challenger.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Bookkeeping_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au/bookkeeping",
        p1="bookkeeping",
        p2="hire",
        headlines=[
            "Hire a Philippines Bookkeeper",
            "Hire a Dedicated Bookkeeper",
            "Bookkeeping Support for Hire",
            "Invoices, Bills, Reconciles",
            "Xero or QuickBooks Support",
            "Day-to-Day Books Support",
            "You Interview the Bookkeeper",
            "Not a Books Freelance Bench",
            "Tell Us Your Books Stack",
            "Dedicated Books Seat",
            "Month-End Without the Scramble",
            "Remote Bookkeeper, Your Hours",
            "Hire Books Help, Keep Your CPA",
            "Get a Bookkeeping Shortlist",
            "Routine Reconciles Covered",
        ],
        descs=[
            "Hire a dedicated Filipino bookkeeper for invoices, records, and reconciliations.",
            "Tell us Xero, QuickBooks, or what you use. You interview before anyone starts.",
            "Day-to-day books support on Australian hours — not licensed accounting advice.",
            "We recruit against the seat. You keep your accountant for judgment work.",
        ],
        why="AU books intent. Xero first — Australian default.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Bookkeeping_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au/bookkeeping",
        p1="books",
        p2="team",
        headlines=[
            "Screened Bookkeeping Talent",
            "Staffing for Your Books Seat",
            "You Meet Them First",
            "Trusted Books Support",
            "Recruited for Your Tools",
            "We Handle Payroll After Hire",
            "A Person Who Owns the Books",
            "Support, Not Licensed Advice",
            "Talk to Our Staffing Team",
            "Growing Teams Add Books Help",
            "Keep Your CPA. Add Capacity.",
            "Real Company Behind the Seat",
            "Skip the Books Freelance Hunt",
            "Dedicated Bookkeeper Hiring",
            "Your Hours. Named Bookkeeper.",
        ],
        descs=[
            "We recruit and vet bookkeeping support. You interview. We handle payroll after you hire.",
            "A staffing company since 2011 — not a rotating freelance books bench.",
            "One dedicated person on Australian hours so month-end is not a scramble.",
            "Tell us the tools and the close rhythm. We'll help you find the seat.",
        ],
        why="AU books trust challenger.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Customer_Service_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au/customer-service",
        p1="support",
        p2="hire",
        headlines=[
            "Hire Customer Service Staff",
            "Dedicated Support Seat",
            "Email, Chat, or Tickets",
            "Hire Philippines Support Staff",
            "Customer Service, Your Hours",
            "You Interview Support Staff",
            "Not a Call-Center Dump",
            "Someone Who Knows Your Product",
            "Tell Us the Channels You Cover",
            "Dedicated Inbox and Chat Help",
            "Hire Support, Keep Your Voice",
            "Get a Support Shortlist",
            "Remote Customer Care Staff",
            "A Named Person on the Queue",
            "Order Updates That Don't Sit",
        ],
        descs=[
            "Hire dedicated Filipino customer service staff for email, chat, or tickets.",
            "One named person on Australian hours — not a rotating freelance roster.",
            "Tell us the channels. We shortlist. You interview before anyone starts.",
            "Support that sounds like your team. You keep the hire decision.",
        ],
        why="AU CS intent.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Customer_Service_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au/customer-service",
        p1="care",
        p2="team",
        headlines=[
            "Screened Support Talent",
            "Trusted Customer Care Hiring",
            "Meet Them Before They Start",
            "Dedicated Seat, Not a Roster",
            "Staffing for Your Support Desk",
            "We Employ Them After You Hire",
            "Consistent Replies, Your Hours",
            "Talk Through the Support Seat",
            "Growing Teams Add Support Here",
            "Not Freelance Ticket Hopping",
            "Real Recruiting for Care Roles",
            "A Company Behind the Queue",
            "You Choose Who Joins Support",
            "Reduce Queue Backlog",
            "Screened Agents. Your Voice.",
        ],
        descs=[
            "We recruit customer service staff. You interview. After you hire, we handle payroll.",
            "Consistent replies from a dedicated seat — not a freelance ticket hop.",
            "Staffing since 2011 for Australian businesses that want someone they have met.",
            "Tell us the product and the hours. We'll help you find the person.",
        ],
        why="AU CS trust challenger.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Sales_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au/sales",
        p1="sales",
        p2="support",
        headlines=[
            "Hire Sales Support Staff",
            "CRM Follow-Up for Hire",
            "Sales Admin, Not Cold Calling",
            "Pipeline Follow-Up Support",
            "Hire a Sales Support Seat",
            "Research and CRM Hygiene",
            "You Interview Sales Support",
            "Lists, Notes, Next Steps",
            "Not a Dialer Farm",
            "Tell Us the Sales Seat",
            "Dedicated Follow-Up Help",
            "Closers Stay With Buyers",
            "Remote Sales Admin Staff",
            "Get a Sales Support Shortlist",
            "Hire Help for the Pipeline",
        ],
        descs=[
            "Hire sales support for CRM hygiene, research, and follow-up — not a cold-call farm.",
            "A dedicated Filipino teammate so closers spend time with buyers, not the CRM.",
            "You interview before anyone starts. Appointment setting only if that is the brief.",
            "Tell us the pipeline work. We shortlist. You decide who joins.",
        ],
        why="AU sales intent. Same no-dialer stance.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Sales_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au/sales",
        p1="pipeline",
        p2="hire",
        headlines=[
            "Screened Sales Support Talent",
            "Trusted Pipeline Admin Hiring",
            "You Meet Them Before Outreach",
            "Dedicated CRM Owner",
            "Staffing for Follow-Up Work",
            "We Stay On After You Hire",
            "Support Seat, Not a Closer",
            "Talk Through the Sales Brief",
            "Growing Teams Add Follow-Up",
            "Not Appointment-Setter Only",
            "Real Company. Real Shortlist.",
            "Reduce Follow-Up Drop-Off",
            "Your CRM. Your Hours.",
            "Hire Support Around Closers",
            "Skip the Freelance SDR Shuffle",
        ],
        descs=[
            "We recruit sales support staff. You interview. We handle payroll after you hire.",
            "Follow-up and CRM owned by one person — not a rotating setter bench.",
            "An established staffing company. You keep the hire decision.",
            "Tell us the CRM and the work. We'll help you find the seat.",
        ],
        why="AU sales trust challenger.",
    )

    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Digital_Marketing_Hire_PH",
        bucket="weak",
        angle="A_intent",
        url_path="/au/digital-marketing",
        p1="marketing",
        p2="hire",
        headlines=[
            "Hire Marketing Support Staff",
            "Campaign Ops for Hire",
            "Reporting and Content Ops",
            "Hire a Marketing Coordinator",
            "Digital Marketing Support",
            "You Interview Marketing Staff",
            "Not a Strategy Retainer Shop",
            "Tell Us the Marketing Seat",
            "Campaign Checklists Owned",
            "Content Ops Without the Fire",
            "Dedicated Marketing Seat",
            "Get a Marketing Shortlist",
            "Hire Execution, Keep Strategy",
            "Remote Campaign Support",
            "Tools You Already Use",
        ],
        descs=[
            "Hire dedicated marketing support for campaigns, reporting, and content ops.",
            "Execution work with an owner — not a strategy retainers pitch.",
            "Tell us the tools. We shortlist. You interview before anyone starts.",
            "Strategists stay on judgment. This seat owns the day-to-day.",
        ],
        why="AU marketing intent.",
    )
    add(
        market="AU",
        campaign="VC_AU_S_ROLES",
        ad_group="Digital_Marketing_Hire_PH",
        bucket="weak",
        angle="B_trust",
        url_path="/au/digital-marketing",
        p1="marketing",
        p2="team",
        headlines=[
            "Screened Marketing Talent",
            "Trusted Marketing Hiring",
            "You Meet Them Before Campaigns",
            "Dedicated Channel Support",
            "Staffing for Marketing Ops",
            "We Stay On After You Hire",
            "Execution Seat, Your Tools",
            "Talk Through Marketing Work",
            "Growing Teams Add Ops Help",
            "Not Freelance Campaign Churn",
            "Reporting Pulls, Not Rebuilds",
            "Real Company Behind the Seat",
            "Hire Help for Content Ops",
            "Reduce Marketing Busywork",
            "A Partner for Campaign Ops",
        ],
        descs=[
            "We recruit marketing support staff. You interview. We handle payroll after you hire.",
            "Campaign coordination and reporting owned by one person you have met.",
            "An established staffing company — not a freelance campaign bench.",
            "Tell us the work. We'll help you find the seat.",
        ],
        why="AU marketing trust challenger.",
    )

    return rows


def ad_row(item: dict) -> dict:
    r = {k: "" for k in FIELDNAMES}
    r["Account"] = ACCOUNT[item["market"]]
    r["Row Type"] = "Ad"
    r["Campaign"] = item["campaign"]
    r["Campaign Type"] = "Search"
    r["Networks"] = "Google Search"
    r["Location options"] = "Presence"
    r["Final URL suffix"] = SUFFIX
    r["Ad Group"] = item["ad_group"]
    r["Ad Status"] = "Enabled"
    r["Ad type"] = "Responsive search ad"
    r["Final URL"] = HOST + item["url_path"]
    r["Path 1"] = item["p1"]
    r["Path 2"] = item["p2"]
    headlines = item["headlines"]
    descs = item["descs"]
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    r["Comment"] = (
        f"RSA Challenger {item['angle']} · {item['bucket']} · {LP_VERSION} · "
        "Ad row only · Campaign/AG Status blank (live-safe) · "
        "Brand deferred · no budget/bid/keyword change · "
        f"{item['why']}"
    )
    return r


def write_csv(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        w.writeheader()
        for item in items:
            w.writerow(ad_row(item))


def cross_checks(items: list[dict]) -> None:
    by_ag: dict[tuple[str, str, str], list[dict]] = {}
    for item in items:
        key = (item["market"], item["campaign"], item["ad_group"])
        by_ag.setdefault(key, []).append(item)
    for key, group in by_ag.items():
        if len(group) != 2:
            raise SystemExit(f"{key}: expected 2 RSAs, got {len(group)}")
        a, b = group
        shared = set(a["headlines"]) & set(b["headlines"])
        if len(shared) > 2:
            raise SystemExit(f"{key}: A/B share too many headlines: {shared}")
        dki_count = sum(1 for it in group for h in it["headlines"] if DKI_RE.search(h))
        if dki_count > 1:
            raise SystemExit(f"{key}: more than one DKI across the pair")
    # No preview trust URLs
    for item in items:
        if "/preview/" in item["url_path"]:
            raise SystemExit(f"Preview URL leaked: {item}")
        if item["market"] == "US" and not item["url_path"].startswith("/us"):
            raise SystemExit(f"US ad not on /us: {item}")
        if item["market"] == "AU" and not item["url_path"].startswith("/au"):
            raise SystemExit(f"AU ad not on /au: {item}")


def summarize(items: list[dict]) -> dict:
    summary: dict = {"count": len(items), "by_bucket": {}, "ad_groups": []}
    for item in items:
        summary["by_bucket"][item["bucket"]] = (
            summary["by_bucket"].get(item["bucket"], 0) + 1
        )
        summary["ad_groups"].append(
            {
                "market": item["market"],
                "campaign": item["campaign"],
                "ad_group": item["ad_group"],
                "angle": item["angle"],
                "bucket": item["bucket"],
                "final_url": HOST + item["url_path"],
                "why": item["why"],
                "dki": any(DKI_RE.search(h) for h in item["headlines"]),
                "headline_count": len(item["headlines"]),
            }
        )
    return summary


def main() -> int:
    items = catalog()
    cross_checks(items)
    us_main = [i for i in items if i["market"] == "US" and i["bucket"] != "semantic"]
    us_sem = [i for i in items if i["market"] == "US" and i["bucket"] == "semantic"]
    au = [i for i in items if i["market"] == "AU"]
    write_csv(OUT_DIR / "google-ads-editor-rsa-challengers-us.csv", us_main)
    write_csv(OUT_DIR / "google-ads-editor-rsa-challengers-semantic-us.csv", us_sem)
    write_csv(OUT_DIR / "google-ads-editor-rsa-challengers-au.csv", au)
    summary = summarize(items)
    (OUT_DIR / "_rsa_challengers_2026_08_19.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(f"RSAs: {len(items)}")
    print(f"  US main: {len(us_main)}")
    print(f"  US semantic (optional): {len(us_sem)}")
    print(f"  AU: {len(au)}")
    print("Wrote:")
    print("  ads-launch/google-ads-editor-rsa-challengers-us.csv")
    print("  ads-launch/google-ads-editor-rsa-challengers-semantic-us.csv")
    print("  ads-launch/google-ads-editor-rsa-challengers-au.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
