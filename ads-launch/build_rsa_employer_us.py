#!/usr/bin/env python3
"""Employer-first US RSA upgrade — Editor CSV only (2026-08-27).

Stronger employer language for US businesses hiring Filipino virtual assistants.
CTAs: fill the form · book a consultation / strategy call · call US sales.
Brand deferred. No Ads API. New ads Paused. Spell out every word (no VA/EA/PH).

Usage:
  python3 ads-launch/build_rsa_employer_us.py
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
XRAY = HERE.parent / "xray"
sys.path.insert(0, str(HERE))

from build_rsa_admin_rewrite_us import HEADERS, HOST, US  # noqa: E402

OUT_CSV = HERE / "google-ads-editor-rsa-add-employer-us.csv"
OUT_MD = HERE / "RSA-EMPLOYER-US-2026-08-27.md"
OUT_JSON = HERE / "_rsa_employer_us.json"
OUT_HTML = XRAY / "employer-rsa-us.html"
OUT_HTML_PUBLIC = XRAY / "public" / "employer-rsa-us.html"

ABBREV_RE = re.compile(
    r"\b(EA|VA|PH|RSA|DKI|SMM|WFH|CRM|TA|CS|HR|PPC|SEO|FB)\b", re.IGNORECASE
)
DKI_RE = re.compile(r"\{(KeyWord|KEYWORD|Location|LOCATION)", re.IGNORECASE)
SLUDGE = re.compile(
    r"clear employer process|request hiring shortlist|partner-managed|"
    r"employer hiring path|scale .+ bandwidth|employer-only intake|"
    r"dedicated seat continuity|staffing partner model|interview-ready|"
    r"ongoing capacity|ops capacity|hire path",
    re.IGNORECASE,
)

# Job-seeker bait — fail the build if copy reads as a job ad
JOB_SEEKER = re.compile(
    r"\b(apply now|we are hiring|join our team|open positions|"
    r"work from home job|remote job|looking for work)\b",
    re.IGNORECASE,
)


def blank_row() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def validate(headlines: list[str], descs: list[str], where: str) -> None:
    if len(headlines) != 15 or len(descs) != 4:
        raise SystemExit(f"{where}: need 15 headlines + 4 descriptions")
    if len(set(headlines)) != 15 or len(set(descs)) != 4:
        raise SystemExit(f"{where}: duplicates")
    for h in headlines:
        if len(h) > 30:
            raise SystemExit(f"{where}: headline {len(h)}: {h!r}")
        if DKI_RE.search(h) or ABBREV_RE.search(h):
            raise SystemExit(f"{where}: abbrev/DKI: {h!r}")
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: desc {len(d)}: {d!r}")
        if DKI_RE.search(d) or ABBREV_RE.search(d):
            raise SystemExit(f"{where}: abbrev/DKI: {d!r}")
    blob = " ".join(headlines + descs)
    if SLUDGE.search(blob):
        raise SystemExit(f"{where}: sludge: {SLUDGE.search(blob)!r}")
    if JOB_SEEKER.search(blob):
        raise SystemExit(f"{where}: job-seeker bait: {JOB_SEEKER.search(blob)!r}")
    if blob.count("?") > 1 or blob.count("!") > 1:
        raise SystemExit(f"{where}: too many ? or !")
    if "?" in blob and "!" in blob:
        raise SystemExit(f"{where}: ? and ! together")
    for ch in ("\u2014", "\u2013", "\u2026", "...", "\u2018", "\u2019", "\u201c", "\u201d"):
        if ch in blob:
            raise SystemExit(f"{where}: fancy punctuation")


# ---------------------------------------------------------------------------
# Copy thesis
# Employers hiring Filipino teammates — not people looking for jobs.
# Steal MOD/Wing energy: strategy call, dedicated not marketplace, you interview.
# Align CTAs with form /us/book sitelink / call sales.
# ---------------------------------------------------------------------------

RSAS: list[dict] = [
    # ===== CORE =====
    {
        "label": "hire_employer_direct",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Hire_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "hire",
        "path2": "employers",
        "keywords_note": "hire virtual assistant · Filipino virtual assistant (employer)",
        "headlines": [
            "For US Employers Hiring",
            "Filipino Virtual Assistants",
            "Hire for Your Business",
            "Book a Consultation",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Interview. You Hire.",
            "Dedicated Not Freelance",
            "On Your Business Hours",
            "We Handle the Payroll",
            "Not a Job Board",
            "Ready in Days Not Weeks",
            "Tell Us the Role You Need",
            "Employers Hire Through Us",
            "Skip Job Board Chaos",
        ],
        "descs": [
            "US employers: hire a dedicated Filipino virtual assistant for your team.",
            "Fill out the form or book a consultation. You meet them. We handle payroll.",
            "Not freelancers. Not a job board. One teammate on your hours, on your work.",
            "Prefer to talk first? Call our US sales team. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "hire_employer_book",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Hire_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "hire",
        "path2": "team",
        "keywords_note": "hire a virtual assistant · looking for a virtual assistant",
        "headlines": [
            "Looking to Hire Help?",
            "Hire a Filipino Teammate",
            "Book a Free Strategy Call",
            "Built for US Employers",
            "You Meet Them First",
            "We Recruit. You Decide.",
            "Not Marketplace Freelancers",
            "On Your US Hours",
            "Someone Who Sticks Around",
            "Reduce Admin Overload",
            "Start With One Person",
            "Tell Us Who You Need",
            "Real People. Real Work.",
            "Employers Only Path",
            "Get Your Time Back",
        ],
        "descs": [
            "Looking to hire help. Dedicated Filipino teammates for US employers - not job seekers.",
            "Book a free strategy call. We shortlist. You interview. We handle payroll.",
            "One person on your hours. Not rotating freelancers who disappear mid-week.",
            "Or fill out the form. Or call sales. You stay in control of every hire.",
        ],
    },
    {
        "label": "agency_employer",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "agency",
        "path2": "hire",
        "keywords_note": "virtual assistant agency · Philippines staffing agency",
        "headlines": [
            "Virtual Assistant Agency",
            "For Employers Building Teams",
            "Hire Filipino Staff",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Interview. You Decide.",
            "We Handle Payroll",
            "Not a Freelance Bench",
            "On Your US Hours",
            "Ready in Days",
            "Start With One Person",
            "Tell Us What You Need",
            "Real Help for Busy Teams",
            "Skip Marketplace Guesswork",
        ],
        "descs": [
            "Agency path for US employers: dedicated Filipino staff, not a freelance bench.",
            "Book a strategy call or fill out the form. You interview. We handle payroll.",
            "Build a team that works without the local hiring headache.",
            "Call our US sales team when you want to talk roles before you hire.",
        ],
    },
    {
        "label": "agency_employer_book",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "team",
        "path2": "build",
        "keywords_note": "outsourcing agency Philippines · remote staffing agency",
        "headlines": [
            "Build a Team That Works",
            "Philippines Staffing Partner",
            "Book a Consultation",
            "Employers Hire With Us",
            "You Keep Hire Control",
            "We Do the Recruiting",
            "Dedicated Staff Who Stay",
            "Reduce Admin Overload",
            "On Your Business Hours",
            "Not Upwork Staffing",
            "Ready When You Are",
            "Tell Us the Roles",
            "Someone You Can Rely On",
            "Get Your Time Back",
            "Talk to US Sales First",
        ],
        "descs": [
            "US employers build remote teams with dedicated Filipino staff who stay.",
            "Book a consultation. Tell us the roles. Meet people before anyone starts.",
            "We recruit and handle payroll. You keep the final say on every hire.",
            "Prefer the phone? Call US sales. Or fill out the form on our site.",
        ],
    },
    {
        "label": "offshore_employer",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Offshore_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "offshore",
        "path2": "hire",
        "keywords_note": "offshore virtual assistant · hire Philippines virtual assistant",
        "headlines": [
            "Hire Offshore Help That Stays",
            "Filipino Teammate for US Work",
            "For Employers Going Offshore",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "Not Freelance Chaos",
            "On Your Hours",
            "We Handle Payroll",
            "Someone Who Owns the Work",
            "Ready in Days",
            "Skip DIY Overseas Hiring",
            "Real Remote Staff",
            "You Keep the Final Say",
        ],
        "descs": [
            "Offshore help for US employers - a dedicated Filipino teammate who stays.",
            "Book a free strategy call. You meet them before anyone starts.",
            "We handle recruiting and payroll. You keep the final say.",
            "Fill out the form or call sales. Get admin off your plate without chaos.",
        ],
    },
    {
        "label": "offshore_employer_book",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Offshore_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "philippines",
        "path2": "hire",
        "keywords_note": "Philippines virtual assistant · Filipino virtual assistant hire",
        "headlines": [
            "Philippines Virtual Assistants",
            "Hire From the Philippines",
            "Book a Consultation",
            "Built for US Employers",
            "Dedicated Filipino Staff",
            "You Interview Every Hire",
            "On Your Business Hours",
            "Not a Gig Marketplace",
            "We Recruit. You Pick.",
            "Help That Shows Up Daily",
            "Tell Us the Role",
            "Employers Only Hiring",
            "Get Admin Off Your Plate",
            "Start With One Seat",
            "Talk Through the Role",
        ],
        "descs": [
            "Hire from the Philippines without building your own recruiting desk.",
            "Book a consultation. Dedicated Filipino staff for US employer hours.",
            "Not freelance chaos. One person who owns the work and sticks around.",
            "Form, book a call, or phone sales - pick the path that fits you.",
        ],
    },
    {
        "label": "staffing_employer",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Staffing_Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "staff",
        "path2": "hire",
        "keywords_note": "Philippines staffing agency · remote staffing for business",
        "headlines": [
            "Need Staff Without the Mess?",
            "Hire Filipino Team Members",
            "For US Employers Staffing",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Interview Every Hire",
            "We Do the Recruiting",
            "Not Upwork Staffing",
            "On Your US Hours",
            "People Who Stick Around",
            "Ready in Days",
            "Tell Us the Roles",
            "Start With One Seat",
            "Skip DIY Philippines Hiring",
        ],
        "descs": [
            "Need staff without building your own Philippines recruiting desk.",
            "Book a strategy call or fill the form. Meet people first. We handle payroll.",
            "Dedicated teammates - not Upwork staffing or freelance churn.",
            "Call US sales when you want to talk roles before you commit.",
        ],
    },
    {
        "label": "staffing_employer_book",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Staffing_Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "staffing",
        "path2": "team",
        "keywords_note": "virtual staffing agency · offshore staffing US",
        "headlines": [
            "Remote Staffing for Employers",
            "Philippines Staffing Fixed",
            "Book a Consultation",
            "Employers Hire Through Us",
            "You Keep the Final Say",
            "Dedicated Seats Who Stay",
            "Reduce Admin Overload",
            "On Your Business Hours",
            "We Handle Payroll",
            "Real Help. Real Continuity.",
            "Tell Us Who You Need",
            "Not a Freelance Marketplace",
            "Get Your Time Back",
            "Ready When You Are",
            "Talk to Hiring Specialists",
        ],
        "descs": [
            "Remote staffing for US employers who want dedicated Filipino teammates.",
            "Book a consultation. Tell us the roles. Interview before anyone starts.",
            "We recruit. You decide. Continuity - not a rotating freelance bench.",
            "Or call our US sales team. Or fill out the hiring form online.",
        ],
    },
    {
        "label": "firm_employer",
        "campaign": "VC_US_S_CORE",
        "ad_group": "VA_Agency_Firm_PH",
        "final_url": f"{HOST}/us",
        "path1": "agency",
        "path2": "firm",
        "keywords_note": "Filipino virtual assistant agency · VA firm hire",
        "headlines": [
            "Virtual Assistant Firm",
            "For Employers Not Job Seekers",
            "Hire Filipino Assistants",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Interview Each Person",
            "Firm Not Marketplace",
            "On Your Hours Daily",
            "Payroll Handled for You",
            "Dedicated Assistants Who Stay",
            "Ready in Days",
            "Tell Us the Role",
            "Clear Your Week Fast",
            "Employers Hire Here",
        ],
        "descs": [
            "Looking for a virtual assistant firm? Built for US employers hiring help.",
            "Book a strategy call. We recruit and screen. You interview before anyone joins.",
            "Agency staffing - not freelance task gigs that vanish mid-project.",
            "Fill the form or call US sales. You decide who joins your business.",
        ],
    },
    {
        "label": "virtual_staff_employer",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Virtual_Staff_PH",
        "final_url": f"{HOST}/us",
        "path1": "staff",
        "path2": "virtual",
        "keywords_note": "virtual staff Philippines · hire virtual staff",
        "headlines": [
            "Hire Virtual Staff Today",
            "Filipino Virtual Staff",
            "For US Employers Hiring",
            "Book a Consultation",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "Dedicated Staff Who Stay",
            "On Your Business Hours",
            "We Handle the Payroll",
            "Not Freelance Virtual Staff",
            "Ready in Days",
            "Tell Us What You Need",
            "Real Continuity on Staff",
            "Skip DIY Overseas Hiring",
        ],
        "descs": [
            "Hire virtual staff for your US business - dedicated Filipino teammates.",
            "Book a consultation or fill out the form. You meet them. We handle payroll.",
            "Not freelance virtual staff who churn. One seat you can keep.",
            "Call our US sales team to talk roles before you hire.",
        ],
    },
    # ===== ROLES =====
    {
        "label": "admin_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Administration_EA_PH",
        "final_url": f"{HOST}/us/administrative-support",
        "path1": "admin",
        "path2": "hire",
        "keywords_note": "hire executive assistant · administrative virtual assistant",
        "headlines": [
            "Hire an Executive Assistant",
            "For Employers Needing Admin",
            "Filipino Admin Who Stays",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "Get Your Calendar Back",
            "On Your US Hours",
            "We Handle Payroll",
            "Not a Freelance Assistant",
            "Follow-Ups Actually Done",
            "Ready in Days",
            "Tell Us What You Need",
            "Reduce Admin Overload",
        ],
        "descs": [
            "Employers: hire a dedicated Filipino executive assistant for your admin load.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Not a freelance assistant. Someone who learns your rhythm and stays.",
            "Call US sales if you want to talk the role before you hire.",
        ],
    },
    {
        "label": "admin_employer_book",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Administration_EA_PH",
        "final_url": f"{HOST}/us/administrative-support",
        "path1": "admin",
        "path2": "help",
        "keywords_note": "virtual assistant for admin · hire administrative support",
        "headlines": [
            "Inbox Eating Your Week?",
            "Hire Admin Help That Stays",
            "Book a Consultation",
            "Built for US Employers",
            "You Interview. You Pick.",
            "Dedicated Filipino Admin",
            "On Your Business Hours",
            "Calendar Stops Owning You",
            "Not a Gig Marketplace",
            "We Recruit. You Decide.",
            "Someone Who Learns You",
            "Employers Hire Admin Here",
            "Clear Admin Off Your Desk",
            "Ready When You Are",
            "Talk Through the Role",
        ],
        "descs": [
            "Inbox and calendar eating your week. Hire dedicated Filipino admin help.",
            "Book a consultation. You interview. Nobody starts until you say yes.",
            "One admin who stays - not marketplace freelancers bouncing between gigs.",
            "Fill out the form or call our US sales team. Employers only.",
        ],
    },
    {
        "label": "appt_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Appointment_Setter_Hire_PH",
        "final_url": f"{HOST}/us/sales",
        "path1": "sales",
        "path2": "appointments",
        "keywords_note": "hire appointment setter · appointment setting virtual assistant",
        "headlines": [
            "Hire an Appointment Setter",
            "For Employers Filling Calls",
            "Filipino Setter Who Stays",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Dialers",
            "Ready in Days",
            "Tell Us Your Sales Flow",
            "Get More Meetings Booked",
            "Dedicated Setter Seat",
            "Employers Hire Setters Here",
        ],
        "descs": [
            "US employers: hire a dedicated Filipino appointment setter for your pipeline.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Not freelance dialers. One setter on your hours who owns the calendar.",
            "Call US sales to talk volume and tools before you hire.",
        ],
    },
    {
        "label": "appt_employer_book",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Appointment_Setter_Hire_PH",
        "final_url": f"{HOST}/us/sales",
        "path1": "meetings",
        "path2": "hire",
        "keywords_note": "appointment setter Philippines · hire remote appointment setter",
        "headlines": [
            "Calendars Too Empty?",
            "Hire Setter Help That Stays",
            "Book a Consultation",
            "Built for US Sales Teams",
            "You Interview. You Hire.",
            "Dedicated Filipino Setter",
            "On Your Business Hours",
            "Not a Rotating Dial Desk",
            "We Recruit. You Decide.",
            "Someone Who Owns Outreach",
            "Ready When You Are",
            "Tell Us Your Ideal Client",
            "Real Continuity on Sales",
            "Skip Freelance Dial Chaos",
            "Talk Through the Role",
        ],
        "descs": [
            "Calendars too empty. Hire a dedicated Filipino appointment setter who stays.",
            "Book a consultation. You interview. Nobody starts until you say yes.",
            "One person on your outreach - not a rotating freelance dial desk.",
            "Or fill out the form. Or call our US sales team first.",
        ],
    },
    {
        "label": "support_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Customer_Service_Hire_PH",
        "final_url": f"{HOST}/us/customer-service",
        "path1": "support",
        "path2": "hire",
        "keywords_note": "hire customer service · Filipino customer support",
        "headlines": [
            "Hire Customer Support Help",
            "For Employers With Queues",
            "Filipino Support Who Stays",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Rotating Agents",
            "Chat and Email Covered",
            "Ready in Days",
            "Get Queues Under Control",
            "Real People on Your Brand",
            "Tell Us Your Support Needs",
        ],
        "descs": [
            "Employers: hire dedicated Filipino customer support on your business hours.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Chat and email covered by someone who stays - not rotating agents.",
            "Call US sales to talk channels and volume before you hire.",
        ],
    },
    {
        "label": "social_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Hire_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "social",
        "path2": "hire",
        "keywords_note": "hire social media manager · Filipino social media assistant",
        "headlines": [
            "Hire Social Media Help",
            "For Employers Behind on Social",
            "Filipino Social Teammate",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Posters",
            "Keep Your Brand Voice",
            "Ready in Days",
            "Get Posting Done Daily",
            "Someone Who Owns the Feed",
            "Tell Us What You Need",
        ],
        "descs": [
            "Employers: hire a dedicated Filipino teammate for your social channels.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Keep your brand voice. Not freelancers who post and vanish.",
            "Call US sales if you want to talk channels before you hire.",
        ],
    },
    {
        "label": "books_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Hire_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "books",
        "path2": "hire",
        "keywords_note": "hire bookkeeper · Filipino bookkeeper virtual",
        "headlines": [
            "Hire a Bookkeeper",
            "For Employers Behind on Books",
            "Filipino Books Teammate",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "Same Person Every Week",
            "We Handle Payroll",
            "Not Freelance Book Tasks",
            "On Your Close Calendar",
            "Ready in Days",
            "Get Reconciliation Done",
            "Someone Who Owns the Books",
            "Tell Us Your Tools",
        ],
        "descs": [
            "Employers: hire a dedicated Filipino bookkeeper who stays week after week.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Same person every week - not freelance bookkeeping task bundles.",
            "Call US sales to talk tools and close timing before you hire.",
        ],
    },
    {
        "label": "recruit_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Recruitment_Hire_PH",
        "final_url": f"{HOST}/us/recruitment",
        "path1": "recruit",
        "path2": "hire",
        "keywords_note": "hire recruiter · recruitment virtual assistant",
        "headlines": [
            "Hire Recruitment Help",
            "For Employers Filling Roles",
            "Filipino Recruiter Who Stays",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Recruiters",
            "Ready in Days",
            "Tell Us Your Open Roles",
            "Get Pipelines Moving",
            "Dedicated Recruiting Seat",
            "Employers Hire Recruiters",
        ],
        "descs": [
            "US employers: hire a dedicated Filipino recruiter to keep your pipeline moving.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Not freelance recruiters bouncing between clients. One seat you keep.",
            "Call US sales to talk volume and tools before you hire.",
        ],
    },
    {
        "label": "sales_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Sales_Hire_PH",
        "final_url": f"{HOST}/us/sales",
        "path1": "sales",
        "path2": "hire",
        "keywords_note": "hire sales assistant · sales support virtual assistant",
        "headlines": [
            "Hire Sales Support Help",
            "For Employers Growing Sales",
            "Filipino Sales Teammate",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Sales Help",
            "Ready in Days",
            "Tell Us Your Sales Stack",
            "Keep Follow-Ups Moving",
            "Dedicated Sales Seat",
            "Employers Hire Sales Help",
        ],
        "descs": [
            "Employers: hire dedicated Filipino sales support on your business hours.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Follow-ups and pipeline work that sticks - not freelance sales gigs.",
            "Call US sales to map the role before anyone starts.",
        ],
    },
    {
        "label": "marketing_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Digital_Marketing_Hire_PH",
        "final_url": f"{HOST}/us/digital-marketing",
        "path1": "marketing",
        "path2": "hire",
        "keywords_note": "hire digital marketing assistant · marketing virtual assistant",
        "headlines": [
            "Hire Marketing Help",
            "For Employers Behind on Ads",
            "Filipino Marketing Teammate",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Marketers",
            "Ready in Days",
            "Tell Us Your Channels",
            "Keep Campaigns Moving",
            "Dedicated Marketing Seat",
            "Employers Hire Marketers",
        ],
        "descs": [
            "Employers: hire a dedicated Filipino marketing teammate for your channels.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Campaign help that stays - not freelance marketers who vanish mid-sprint.",
            "Call US sales to talk channels and tools before you hire.",
        ],
    },
    {
        "label": "people_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Human_Resources_Hire_PH",
        "final_url": f"{HOST}/us/hr",
        "path1": "people",
        "path2": "hire",
        "keywords_note": "hire human resources assistant · people ops virtual assistant",
        "headlines": [
            "Hire People Ops Help",
            "For Employers Adding People",
            "Filipino People Teammate",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance People Help",
            "Ready in Days",
            "Tell Us Your People Needs",
            "Keep Hiring Moving",
            "Dedicated People Seat",
            "Employers Hire People Help",
        ],
        "descs": [
            "Employers: hire dedicated Filipino people-ops help on your business hours.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Hiring and people work that sticks - not freelance task hoppers.",
            "Call US sales to talk the role before anyone starts.",
        ],
    },
    {
        "label": "accounting_employer",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Accounting_Hire_PH",
        "final_url": f"{HOST}/us/accounting",
        "path1": "accounting",
        "path2": "hire",
        "keywords_note": "hire accounting assistant · Filipino accounting support",
        "headlines": [
            "Hire Accounting Support",
            "For Employers at Month-End",
            "Filipino Accounting Help",
            "Book a Free Strategy Call",
            "Fill Out the Hiring Form",
            "Call Our US Sales Team",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Accounting",
            "Ready in Days",
            "Tell Us Your Close Needs",
            "Keep Month-End Moving",
            "Dedicated Accounting Seat",
            "Employers Hire Accounting",
        ],
        "descs": [
            "Employers: hire dedicated Filipino accounting support on your close calendar.",
            "Book a strategy call or fill the form. You meet them. We handle payroll.",
            "Extra capacity for transactions and reporting prep - not licensed advice.",
            "Call US sales to talk tools and timing before you hire.",
        ],
    },
]


def append_add(rows: list[dict[str, str]], rsa: dict) -> None:
    where = f"{rsa['ad_group']}/{rsa['label']}"
    validate(rsa["headlines"], rsa["descs"], where)
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
                "Employer RSA 2026-08-27; Paused; no abbrev; "
                f"angle={rsa['label']}; form/book/call CTAs"
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


def write_md() -> None:
    by_ag: dict[str, list[dict]] = {}
    for rsa in RSAS:
        by_ag.setdefault(rsa["ad_group"], []).append(rsa)
    lines = [
        "# Employer RSA upgrade — US · 2026-08-27",
        "",
        "Stronger employer language for US businesses hiring Filipino virtual assistants.",
        "CTAs: fill the form · book consultation / strategy call · call US sales.",
        "**Editor CSV only. Brand deferred. No Ads API.** New ads ship **Paused**.",
        "",
        "## Thesis",
        "",
        "- Who it's for: employers / US businesses — not job seekers",
        "- Steal (meaning only): MyOutDesk strategy-call CTA · Wing dedicated-not-marketplace",
        "- Align with book sitelink: `/us/book` · `google-ads-editor-sitelink-book-us.csv`",
        "- Spell out Virtual Assistant, Philippines, Filipino (no abbreviations)",
        "- George adds, then pauses older RSAs so ~2 remain per ad group",
        "",
        "## Import (when ready — show X-ray first)",
        "",
        "1. Editor → USA → Get recent changes",
        "2. Import `google-ads-editor-rsa-add-employer-us.csv` (Paused RSAs)",
        "3. Optionally same pass: `google-ads-editor-sitelink-book-us.csv`",
        "4. Preview → Post. Import ≠ live until Post. Enable after a couple days of CTR.",
        "",
        f"## Ad groups ({len(by_ag)}) · RSAs ({len(RSAS)})",
        "",
        "| Campaign | Ad group | RSAs | Sample |",
        "|----------|----------|------|--------|",
    ]
    for ag, items in by_ag.items():
        camp = items[0]["campaign"]
        sample = items[0]["headlines"][0]
        lines.append(f"| `{camp}` | `{ag}` | {len(items)} | {sample} |")
    lines += [
        "",
        "## Files",
        "",
        f"- CSV: `{OUT_CSV.name}`",
        f"- X-ray: https://vc-xray.vercel.app/employer-rsa-us.html",
        f"- Book sitelink CSV (still present): `google-ads-editor-sitelink-book-us.csv`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def _esc(s: str) -> str:
    return html.escape(s, quote=True)


def write_html() -> None:
    """X-ray SERP mock + full copy + book sitelink context."""
    by_ag: dict[tuple[str, str], list[dict]] = {}
    for rsa in RSAS:
        by_ag.setdefault((rsa["campaign"], rsa["ad_group"]), []).append(rsa)

    articles = []
    toc = []
    idx = 0
    for (camp, ag), items in by_ag.items():
        idx += 1
        aid = f"ag-{idx}"
        toc.append(
            f'<li><a href="#{aid}">{_esc(ag)}</a> '
            f'<em>{_esc(camp)} · {len(items)} RSA</em></li>'
        )
        blocks = [
            f'<article class="ag" id="{aid}">',
            f"<h2>{_esc(ag)}</h2>",
            f'<p class="meta">{_esc(camp)} · Final URL: '
            f'<a href="{_esc(items[0]["final_url"])}" target="_blank" rel="noopener">'
            f'{_esc(items[0]["final_url"])}</a></p>',
            f'<p class="tiny">Keywords context: {_esc(items[0].get("keywords_note", ""))}</p>',
        ]
        for n, rsa in enumerate(items, 1):
            h = rsa["headlines"]
            d = rsa["descs"]
            path = f'{rsa["path1"]}/{rsa["path2"]}'
            # Sample SERP combos + sitelinks on first RSA of each AG
            combos = [
                (h[0], h[1], h[3], d[0]),
                (h[0], h[3], h[5], d[1]),
                (h[1], h[6], h[8], d[2]),
                (h[3], h[4], h[2], d[1]),
            ]
            blocks.append(f'<div class="rsa">')
            blocks.append(
                f'<h3>RSA {n} · {_esc(rsa["label"])} '
                f'<span class="badge">Paused</span></h3>'
            )
            blocks.append(
                f'<p class="tiny">Paths: {_esc(path)} · angle={_esc(rsa["label"])}</p>'
            )
            for ci, (a, b, c, desc) in enumerate(combos, 1):
                title = f"{a} · {b} · {c}"
                blocks.append('<div class="serp">')
                blocks.append(
                    '<div class="serp-cite">'
                    '<span class="serp-favicon">VC</span>'
                    '<div class="serp-cite-meta">'
                    '<p class="serp-site">Virtual Coworker '
                    '<span class="serp-ad">Sponsored</span></p>'
                    f'<p class="serp-url">https://www.virtualcoworker.app › '
                    f"{_esc(path)}</p>"
                    "</div></div>"
                )
                blocks.append(f'<p class="serp-title">{_esc(title)}</p>')
                blocks.append(f'<p class="serp-desc">{_esc(desc)}</p>')
                if n == 1 and ci == 1:
                    blocks.append(
                        '<div class="serp-links">'
                        '<a href="https://www.virtualcoworker.app/us/book" target="_blank" rel="noopener">'
                        "<strong>Book a Consultation</strong>"
                        "<span>Skip the form · Pick a time with our team</span></a>"
                        '<a href="https://www.virtualcoworker.app/how-it-works?market=us" target="_blank" rel="noopener">'
                        "<strong>How Hiring Works</strong>"
                        "<span>Recruit, vet, shortlist</span></a>"
                        '<a href="https://www.virtualcoworker.app/us/quiz" target="_blank" rel="noopener">'
                        "<strong>Take the Role Quiz</strong>"
                        "<span>Find the right hire</span></a>"
                        '<a href="https://www.virtualcoworker.app/services?market=us" target="_blank" rel="noopener">'
                        "<strong>Hire by Role</strong>"
                        "<span>Admin, books, marketing</span></a>"
                        "</div>"
                    )
                blocks.append("</div>")
            blocks.append('<details><summary>All 15 headlines · 4 descriptions</summary>')
            blocks.append('<ol class="assets">')
            for hi in h:
                bad = " bad" if len(hi) > 30 else ""
                blocks.append(
                    f"<li>{_esc(hi)} <span class=\"len{bad}\">{len(hi)}</span></li>"
                )
            blocks.append("</ol><ul class=\"assets\">")
            for di in d:
                bad = " bad" if len(di) > 90 else ""
                blocks.append(
                    f"<li>{_esc(di)} <span class=\"len{bad}\">{len(di)}</span></li>"
                )
            blocks.append("</ul></details></div>")
        blocks.append("</article>")
        articles.append("\n".join(blocks))

    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>Employer RSAs · US · Virtual Coworker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    .main {{ max-width: 980px; }}
    .note {{
      background: var(--tint-green);
      border: 2px solid var(--tint-green-edge);
      border-radius: 8px;
      padding: 1rem 1.15rem;
      margin: 0 0 1.25rem;
      font-size: 1.05rem;
      line-height: 1.45;
    }}
    .thesis {{
      background: var(--tint-cool);
      border: 1px solid var(--tint-cool-edge);
      border-radius: 8px;
      padding: .9rem 1.05rem;
      margin: 0 0 1.25rem;
    }}
    .thesis ul {{ margin: .35rem 0 0; padding-left: 1.2rem; }}
    .stats {{ display:flex; flex-wrap:wrap; gap:.7rem; margin:0 0 1.25rem; }}
    .stat {{ background:#fff; border:1px solid var(--edge); padding:.7rem 1rem; border-radius:10px; min-width:7rem; }}
    .stat b {{ display:block; font-size:1.35rem; }}
    .toc {{ display:flex; flex-wrap:wrap; gap:.35rem .9rem; font-size:.88rem; margin:0 0 1.25rem; }}
    .toc a {{ color:var(--ink); }}
    .toc em {{ font-style:normal; color:var(--muted); font-size:.72rem; }}
    article.ag {{
      background:#fff; border:1px solid var(--edge); border-radius:14px;
      padding:1.1rem 1.2rem 1.3rem; margin:0 0 1.15rem;
    }}
    article.ag h2 {{ margin:.1rem 0 .35rem; font-size:1.25rem; }}
    .rsa {{ margin:1rem 0 0; padding-top:.85rem; border-top:1px solid var(--edge-soft); }}
    .rsa h3 {{ margin:0 0 .35rem; font-size:1.05rem; }}
    .badge {{
      display:inline-block; font-size:.68rem; font-weight:700;
      letter-spacing:.03em; padding:.18rem .5rem; border-radius:4px;
      color:#fff; background:#8a5a00; vertical-align:middle;
    }}
    .meta, .tiny {{ color:var(--muted); }}
    .tiny {{ font-size:.8rem; }}
    .serp {{
      font-family: Arial, Helvetica, sans-serif;
      border: 1px solid #dadce0; border-radius: 8px;
      padding: 0.85rem 1rem 0.95rem; margin: 0 0 0.55rem; background: #fff;
    }}
    .serp-cite {{ display:flex; align-items:center; gap:0.55rem; margin:0 0 0.28rem; }}
    .serp-favicon {{
      width:26px; height:26px; border-radius:50%;
      background:#188038; color:#fff; font-size:0.7rem; font-weight:700;
      display:inline-flex; align-items:center; justify-content:center; flex-shrink:0;
    }}
    .serp-site {{ margin:0; font-size:0.875rem; color:#202124; }}
    .serp-ad {{ color:#70757a; font-size:0.75rem; }}
    .serp-url {{
      margin:0; font-size:0.72rem; color:#4d5156;
      white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }}
    .serp-title {{
      color:#1a0dab; font-size:1.25rem; font-weight:600;
      line-height:1.28; margin:0.12rem 0 0.22rem;
    }}
    .serp-desc {{ color:#4d5156; font-size:0.875rem; line-height:1.55; margin:0; }}
    .serp-links {{
      display:grid; grid-template-columns:1fr 1fr; gap:0.55rem 1.1rem; margin-top:0.75rem;
    }}
    .serp-links a {{ color:#1a0dab; text-decoration:none; font-size:0.88rem; }}
    .serp-links strong {{ display:block; font-weight:600; }}
    .serp-links span {{ display:block; color:#4d5156; font-size:0.78rem; margin-top:0.1rem; }}
    .assets {{ font-family:var(--mono); font-size:.78rem; margin:.35rem 0; padding-left:1.15rem; }}
    .assets .len {{ color:var(--dim); font-size:.68rem; }}
    .assets .len.bad {{ color:var(--bad); font-weight:700; }}
    details {{ margin-top:.45rem; }}
    details summary {{ cursor:pointer; color:var(--muted); font-size:.85rem; }}
    @media (max-width:700px) {{ .serp-links {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body data-page="employer-rsa-us.html" data-foot="Employer RSAs · US · Paused Editor CSV<br />Show before import">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="page-head">
        <p class="kicker">Ads · US RSA upgrade · employers only</p>
        <h1>Employer RSAs + book sitelink</h1>
        <p>
          New US responsive search ads with stronger employer language.
          For businesses hiring Filipino virtual assistants — not job seekers.
          Sample SERPs below include the new Book a Consultation sitelink.
        </p>
      </header>

      <div class="note" role="status">
        <strong>Preview only — not live.</strong>
        {len(RSAS)} new RSAs ship <strong>Paused</strong> in Editor.
        Import ≠ live until you Post. Enable after a couple days, then pause older ads so ~2 remain per ad group.
        Book sitelink CSV still ready: <code>google-ads-editor-sitelink-book-us.csv</code>.
      </div>

      <div class="thesis">
        <strong>Copy thesis</strong>
        <ul>
          <li>Who it's for, in the headline: US employers / businesses hiring</li>
          <li>CTAs: fill the form · book a consultation / strategy call · call US sales</li>
          <li>Meaning stolen from competitors (not their claims): strategy call, dedicated not marketplace, you interview</li>
          <li>No abbreviations. Spell out Virtual Assistant, Philippines, Filipino</li>
          <li>Campaigns: <code>VC_US_S_CORE</code> + <code>VC_US_S_ROLES</code> only — Brand deferred</li>
        </ul>
      </div>

      <div class="stats">
        <div class="stat"><b>{len(RSAS)}</b> new RSAs</div>
        <div class="stat"><b>{len(by_ag)}</b> ad groups</div>
        <div class="stat"><b>Paused</b> until you enable</div>
        <div class="stat"><b>/us/book</b> sitelink ready</div>
      </div>

      <p class="tiny" style="margin:0 0 .5rem">Jump to ad group</p>
      <ol class="toc">{"".join(toc)}</ol>

      {"".join(articles)}

      <section style="margin:1.5rem 0 2rem">
        <h2 style="font-size:1.15rem">Editor files (when you ask)</h2>
        <p class="tiny">
          RSA add: <code>ads-launch/google-ads-editor-rsa-add-employer-us.csv</code><br />
          Book sitelink: <code>ads-launch/google-ads-editor-sitelink-book-us.csv</code><br />
          Account USA <code>496-715-1855</code> · Campaign Status blank · no budget/bid changes
        </p>
      </section>
    </main>
  </div>
  <script src="nav.js"></script>
</body>
</html>
"""
    OUT_HTML.write_text(body, encoding="utf-8")
    OUT_HTML_PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML_PUBLIC.write_text(body, encoding="utf-8")


def main() -> None:
    rows: list[dict[str, str]] = []
    for rsa in RSAS:
        append_add(rows, rsa)
    write_csv(OUT_CSV, rows)
    write_md()
    write_html()
    OUT_JSON.write_text(
        json.dumps(
            {
                "generated": "2026-08-27",
                "rsa_count": len(RSAS),
                "ad_groups": sorted({r["ad_group"] for r in RSAS}),
                "csv": OUT_CSV.name,
                "sitelink_csv": "google-ads-editor-sitelink-book-us.csv",
                "xray": "https://vc-xray.vercel.app/employer-rsa-us.html",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"ADD  {OUT_CSV.name} ({len(rows)} Paused RSAs)")
    print(f"NOTE {OUT_MD.name}")
    print(f"HTML {OUT_HTML.name}")
    print(f"JSON {OUT_JSON.name}")


if __name__ == "__main__":
    main()
