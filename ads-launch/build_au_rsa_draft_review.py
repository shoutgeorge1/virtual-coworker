#!/usr/bin/env python3
"""Build AU RSA draft review HTML + machine-readable JSON. DRAFT ONLY — no Ads API mutate.

Reads: ads-launch/_au_rsa_assets_probe.json
Writes:
  ads-launch/_au_rsa_draft.json
  xray/au-rsa-review.html
"""

from __future__ import annotations

import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "ads-launch" / "_au_rsa_assets_probe.json"
OUT_JSON = ROOT / "ads-launch" / "_au_rsa_draft.json"
OUT_HTML = ROOT / "xray" / "au-rsa-review.html"

AU_PHONE = "1300 886 740"
US_PHONE = "888-964-8644"
H_MAX = 30
D_MAX = 90


def chk(texts: list[str], limit: int, label: str) -> None:
    for t in texts:
        if len(t) > limit:
            raise SystemExit(f"{label}: {len(t)}>{limit}: {t!r}")


# --- Must-fill drafts (one new human RSA per open-slot AG) ---
# AU voice: spell out words, employment admin (not US payroll), Australian hours, no ~$8.

DRAFTS: dict[str, dict] = {
    "Hire_VA_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "va",
        "why": "Top CORE clicks (20 / 10.6% CTR). Enabled set still abbreviation-heavy; fill open slot after pause with AU hub LP voice.",
        "headlines": [
            "Your Week Is Full",
            "Hire a Virtual Assistant",
            "Dedicated Filipino Teammate",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Not a Gig Marketplace",
            "Talk to a Specialist",
            "They Want This Work",
            "Clear the Admin Pile",
            "Not a Job Board Hire",
            "Nobody Starts Till You Say",
            "We Recruit. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Your week is full. A dedicated Filipino virtual assistant on Australian hours clears it.",
            "Obligation-free chat. We recruit and screen. You interview. We handle employment admin.",
            "Dedicated teammate seat for Australian businesses — not a freelance marketplace.",
            "Talk to a specialist. You pick who joins. Nobody starts until you say yes.",
        ],
    },
    "Offshore_VA_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "ph",
        "why": "Only 1 enabled RSA; room to create. 13.6% CTR on thin volume — keep dedicated/offshore angle, human AU copy.",
        "headlines": [
            "Offshore Without the Chaos",
            "Dedicated Filipino Seat",
            "On Australian Hours Daily",
            "You Interview Finalists",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Not Freelance Offshore",
            "One Teammate. Not a Bench.",
            "Talk Offshore Staffing",
            "They Watch Your Back",
            "We Find Them. You Pick.",
            "Hire Without the DIY Chase",
            "Employers Hiring Only",
            "Serious Help. Steady Seat.",
            "Nobody Starts Till You Say",
        ],
        "descriptions": [
            "Dedicated Filipino teammates offshore — on Australian hours, not rotating freelancers.",
            "Obligation-free chat. We recruit in the Philippines. You interview. Admin handled.",
            "One accountable seat for your business. Not a gig bench or job board hire.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    "Accounting_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "acct",
        "why": "Open slots after pauses; LP is month-end / capacity support (not licensed advice). Human dedicated-seat angle.",
        "headlines": [
            "Month-End Still a Scramble?",
            "Dedicated Accounting Support",
            "Filipino Finance Teammate",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Extra Capacity. Steady Seat.",
            "Not Licensed Advice Claim",
            "Talk to a Specialist",
            "Reporting Prep Without Panic",
            "Not a Freelance Books Gig",
            "Nobody Starts Till You Say",
            "We Shortlist. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Month-end still a scramble? Add dedicated Filipino accounting support on Australian hours.",
            "Obligation-free chat. We shortlist. You interview. We handle employment admin.",
            "Extra capacity for recurring work — not a substitute for your accountant.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    "Admin_City_Test": {
        "priority": "must_fill",
        "path1": "hire",
        "path2": "local",
        "why": "Only 1 RSA (LOCATION test). Create a fully human RSA with no dynamic keyword insertion.",
        "headlines": [
            "Still Doing Admin Yourself?",
            "Hire a Virtual Assistant",
            "Dedicated Filipino Assistant",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Inbox Stops Eating Time",
            "Not a Freelance Assistant",
            "Talk to a Specialist",
            "They Learn Your Rhythm",
            "Calendar Stops Owning You",
            "Clear the Admin Work",
            "Nobody Starts Till You Say",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Still doing the admin yourself? Hire a dedicated Filipino teammate for Australian hours.",
            "Obligation-free chat. We recruit. You interview. We handle employment admin.",
            "Inbox, scheduling and follow-ups — a steady seat, not a freelance marketplace.",
            "Talk to a specialist. No lock-in from the first chat. You choose who joins.",
        ],
    },
    "Administration_EA_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "ea",
        "why": "Strong CTR (13.7%, 7 clicks). Replace paused DKI with human executive-assistant / admin LP voice.",
        "headlines": [
            "Inbox Eating Your Week?",
            "Hire an Executive Assistant",
            "Dedicated Filipino Admin",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Follow-Ups Actually Done",
            "Not a Freelance Assistant",
            "Talk to a Specialist",
            "Managers Get Time Back",
            "They Learn Your Rhythm",
            "Calendar Under Control",
            "Nobody Starts Till You Say",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Inbox and follow-ups still on you? Hire dedicated Filipino admin support.",
            "Obligation-free chat. We recruit. You interview. We handle employment admin.",
            "A dedicated seat for Australian businesses — not a freelance personal-assistant gig.",
            "Talk to a specialist. Nobody starts until you say yes.",
        ],
    },
    "Bookkeeping_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "books",
        "why": "Open slot; enabled copy leans tool jargon. LP: books falling behind, Xero/QuickBooks match in chat — keep human.",
        "headlines": [
            "Books Falling Behind?",
            "Dedicated Filipino Bookkeeper",
            "Outsource Day-to-Day Books",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Invoices Stop Stacking Up",
            "Not a Freelance Books Gig",
            "Talk to a Specialist",
            "Reconciliations Without Chase",
            "Steady Books Support Seat",
            "Nobody Starts Till You Say",
            "We Recruit. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Books falling behind? Hire a dedicated Filipino bookkeeper for Australian hours.",
            "Obligation-free chat. We recruit. You interview. We handle employment admin.",
            "Invoices, reconciliations and routine reporting — a dedicated seat, not a gig bench.",
            "Mention your tools when you talk with us. Nobody starts until you say yes.",
        ],
    },
    "Customer_Service_Hire_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "cs",
        "why": "Best CTR in ROLES sample (25%, 3 clicks). Swap paused DKI for human support-hire angle.",
        "headlines": [
            "Customers Waiting on Replies?",
            "Hire Customer Support Staff",
            "Dedicated Filipino Support",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Queue Stops Piling Up",
            "Not Freelance Support Gigs",
            "Talk to a Specialist",
            "Tickets Get an Owner",
            "Consistent Brand Replies",
            "Nobody Starts Till You Say",
            "We Shortlist. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Customers waiting on replies? Add dedicated Filipino support on Australian hours.",
            "Obligation-free chat. We shortlist. You interview. We handle employment admin.",
            "A dedicated support seat owns inquiries and status updates — not rotating freelancers.",
            "You pick who joins your team. Nobody starts until you say yes.",
        ],
    },
    "Customer_Service_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "cs",
        "why": "Open slot after pause; dedicated outsource path on customer-service LP.",
        "headlines": [
            "Support Queue Still Growing?",
            "Dedicated Support Seat",
            "Outsource Customer Service",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Reliable Remote Support",
            "Not a Gig Support Bench",
            "Talk to a Specialist",
            "One Owner for the Queue",
            "Australian Teams Prefer This",
            "Nobody Starts Till You Say",
            "We Find Them. You Pick.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Need dedicated customer support without building your own Philippines desk?",
            "Obligation-free chat. We recruit. You interview. We handle employment admin.",
            "Reliable remote support seats for Australian teams — not freelance gigs.",
            "You keep brand control. Nobody starts until you say yes.",
        ],
    },
    "Digital_Marketing_Hire_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "mkt",
        "why": "Open slot; LP: marketing still slipping / campaigns need an owner. Spell out marketing (no VA junk).",
        "headlines": [
            "Marketing Still Slipping?",
            "Hire a Filipino Marketer",
            "Dedicated Marketing Support",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Campaigns Need an Owner",
            "Not a Gig Marketing App",
            "Talk to a Specialist",
            "Reporting Stops Stalling",
            "Content Ops Keep Moving",
            "Nobody Starts Till You Say",
            "We Shortlist. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Marketing still slipping? Hire dedicated Filipino marketing support for Australian hours.",
            "Obligation-free chat. We shortlist. You interview. We handle employment admin.",
            "Campaigns, reporting and content ops get an owner — strategists stay on judgment work.",
            "You interview before anyone joins. Nobody starts until you say yes.",
        ],
    },
    "Digital_Marketing_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "mkt",
        "why": "Open slot; dedicated marketing seat angle matched to outsource path + LP.",
        "headlines": [
            "Need a Marketing Seat Filled?",
            "Dedicated Filipino Marketer",
            "Outsource Marketing Ops",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Day-to-Day Work Covered",
            "Not Rotating Freelancers",
            "Talk to a Specialist",
            "Keep Strategy In-House",
            "Execution Without Chaos",
            "Nobody Starts Till You Say",
            "We Recruit. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "A dedicated Filipino marketer for Australian hours — you choose who joins.",
            "Obligation-free chat. We recruit the day-to-day owner. You interview first.",
            "Keep strategists on judgment work. Dedicated execution seat, not a freelancer bench.",
            "We handle employment admin after you hire. Nobody starts until you say yes.",
        ],
    },
    "Human_Resources_Hire_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "hr",
        "why": "Open slot; LP: people ops still on managers. Spell out human resources / people ops.",
        "headlines": [
            "People Ops on Managers?",
            "Hire Human Resources Help",
            "Dedicated People Ops Seat",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Onboarding Stops Slipping",
            "Not Freelance People Ops",
            "Talk to a Specialist",
            "Records Stay Organised",
            "Scheduling Without Chase",
            "Nobody Starts Till You Say",
            "We Shortlist. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "People ops still on managers? Hire dedicated Filipino human resources support.",
            "Obligation-free chat. We shortlist. You interview. Businesses only.",
            "Records, onboarding and scheduling get a dedicated owner on Australian hours.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    "Human_Resources_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "hr",
        "why": "Open slot; dedicated outsource path on /au/hr.",
        "headlines": [
            "Outsource People Ops Work",
            "Dedicated People Ops Seat",
            "Filipino People Ops Help",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Managers Get Time Back",
            "Not a Gig People Ops Bench",
            "Talk to a Specialist",
            "Steady Remote People Capacity",
            "Businesses Hiring Only",
            "Nobody Starts Till You Say",
            "We Find Them. You Pick.",
            "Clear Seat. Clear Owner.",
        ],
        "descriptions": [
            "Offshore human resources capacity — Australian hours, you choose who joins.",
            "Obligation-free chat. Tell us the role. We recruit. You interview.",
            "Dedicated people-ops support for Australian businesses — not freelance gigs.",
            "Nobody starts until you say yes.",
        ],
    },
    "Recruitment_Hire_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "ta",
        "why": "Highest ROLES clicks (10 / 28.6% CTR). Keep winners; fill paused slot with human recruiting-ops angle.",
        "headlines": [
            "Hiring Slowing You Down?",
            "Hire Recruiting Support",
            "Dedicated Recruiting Help",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Screens Without the Chase",
            "Not Freelance Recruiters",
            "Talk to a Specialist",
            "They Schedule Interviews",
            "Sourcing Help You Keep",
            "Managers Spend Time Deciding",
            "Nobody Starts Till You Say",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Sourcing and interview scheduling slowing hiring? Dedicated Filipino recruiting support.",
            "Obligation-free chat. Dedicated recruiting help. You interview. Employment admin handled.",
            "Hiring managers spend time deciding — not chasing calendars and resumes.",
            "Employers only. Nobody starts until you say yes.",
        ],
    },
    "Recruitment_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "ta",
        "why": "Open slot; dedicated recruiting ops seat on /au/recruitment.",
        "headlines": [
            "Need Recruiting Ops Help?",
            "Dedicated Recruiting Seat",
            "Outsource Recruiting Support",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Pipeline Stays Moving",
            "Not a Gig Recruiter Bench",
            "Talk to a Specialist",
            "Coordination Without Chaos",
            "Keep Final Say In-House",
            "Nobody Starts Till You Say",
            "We Recruit. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Dedicated Filipino recruiting operations support on Australian hours.",
            "Obligation-free chat. We shortlist. You interview who joins your team.",
            "Keep final hiring decisions in-house. We handle employment admin after you hire.",
            "Nobody starts until you say yes.",
        ],
    },
    "Sales_Hire_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "sales",
        "why": "Open slot; LP sales support / appointment setting. Spell out lead generation — no abbreviation spam.",
        "headlines": [
            "Follow-Ups Still Slipping?",
            "Hire Sales Support Staff",
            "Dedicated Filipino Sales Help",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Appointment Setting Help",
            "Not Freelance Lead Lists",
            "Talk to a Specialist",
            "They Book the Meetings",
            "Closers Get Time Back",
            "Research and Reminders",
            "Nobody Starts Till You Say",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Appointment setting, research and follow-ups slipping while closers stay buried?",
            "Obligation-free chat. Filipino sales support. You interview. We handle employment admin.",
            "Dedicated seat for Australian teams — not freelance list-pull gigs.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    "Sales_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "sales",
        "why": "Open slot; dedicated sales / lead-gen outsource path.",
        "headlines": [
            "Need a Sales Seat Filled?",
            "Dedicated Lead Gen Seat",
            "Outsource Sales Support",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Pipeline Work Gets Owned",
            "Not a Gig Sales Bench",
            "Talk to a Specialist",
            "Steady Remote Sales Help",
            "Keep Closing In-House",
            "Nobody Starts Till You Say",
            "We Find Them. You Pick.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Dedicated Filipino sales support on Australian hours — you choose who joins.",
            "Obligation-free chat. We recruit. You interview. We handle employment admin.",
            "Pipeline research and follow-ups get an owner. Closers stay on closing.",
            "Nobody starts until you say yes.",
        ],
    },
    "Social_Media_Hire_PH": {
        "priority": "must_fill",
        "path1": "shortlist",
        "path2": "smm",
        "why": "Open slot; LP: social gone quiet. Spell out social media — avoid SMM abbreviation in headlines.",
        "headlines": [
            "Social Gone Quiet?",
            "Hire Social Media Support",
            "Dedicated Filipino Social Seat",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Channels Stay Active",
            "Not a Gig Poster App",
            "Talk to a Specialist",
            "Scheduling Without Scramble",
            "Community Replies Covered",
            "Nobody Starts Till You Say",
            "We Shortlist. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Social gone quiet? A dedicated Filipino teammate can run the channels on Australian hours.",
            "Obligation-free chat. We shortlist. You interview. We handle employment admin.",
            "Scheduling, community and asset coordination — staffing, not a gig platform.",
            "You keep brand voice control. Nobody starts until you say yes.",
        ],
    },
    "Social_Media_Outsource_PH": {
        "priority": "must_fill",
        "path1": "dedicated",
        "path2": "smm",
        "why": "Has clicks (2 / 11.8% CTR). Fill paused slot with dedicated outsource human angle.",
        "headlines": [
            "Brand Going Quiet Again?",
            "Dedicated Social Media Seat",
            "Outsource Social Channels",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "They Run the Calendar",
            "Not Rotating Freelancers",
            "Talk to a Specialist",
            "Community Stays Warm",
            "Hire Social Without Chaos",
            "Nobody Starts Till You Say",
            "We Recruit. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Channels going quiet? Hire a dedicated Filipino social teammate for Australian hours.",
            "Obligation-free chat. We shortlist. You interview. We handle employment admin.",
            "Posting and community replies stop falling behind when you are busy.",
            "You keep brand voice control. Nobody starts until you say yes.",
        ],
    },
}

# Optional — AGs already at 3 enabled RSAs (no open slot). Clearly not must-fill.
ALSO_CONSIDER: dict[str, dict] = {
    "Agency_PH": {
        "priority": "also_consider",
        "path1": "shortlist",
        "path2": "va",
        "why": "FULL (3 enabled). 8 clicks / 10.4% CTR. Only consider if George pauses one abbreviation-heavy RSA first.",
        "blocker": "No open slot — 3 enabled RSAs.",
        "headlines": [
            "Looking for an Agency?",
            "Dedicated Filipino Staff",
            "Agency Hire. You Pick.",
            "On Australian Hours",
            "You Interview the Team",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Not a Gig Staffing App",
            "Talk to a Specialist",
            "We Find. You Choose.",
            "Staff Without Local Overhead",
            "Your Week Is Full",
            "Filipino Teammate Hire",
            "Nobody Starts Till You Say",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "A staffing agency path: dedicated Filipino teammates for Australian businesses.",
            "Obligation-free chat. We recruit and screen. You interview. We handle employment admin.",
            "Dedicated seats — not freelance gigs or a job board.",
            "You pick who joins your team. No obligation from the first conversation.",
        ],
    },
    "Accounting_Hire_PH": {
        "priority": "also_consider",
        "path1": "shortlist",
        "path2": "acct",
        "why": "FULL (3 enabled). Thin traffic. Optional human rewrite only after pausing one existing RSA.",
        "blocker": "No open slot — 3 enabled RSAs.",
        "headlines": [
            "Month-End Piling Up?",
            "Hire Accounting Support",
            "Filipino Accounting Hire",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Extra Capacity for Close",
            "Not Licensed Advice Claim",
            "Talk to a Specialist",
            "Recurring Work Gets Owned",
            "Not a Freelance Finance Gig",
            "Nobody Starts Till You Say",
            "We Shortlist. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Month-end still a scramble? Hire dedicated Filipino accounting support.",
            "Obligation-free chat. We shortlist. You interview. Australian hours.",
            "Extra capacity for the work — not a claim of licensed advice.",
            "You interview the shortlist before anyone starts.",
        ],
    },
    "Bookkeeping_Hire_PH": {
        "priority": "also_consider",
        "path1": "shortlist",
        "path2": "books",
        "why": "FULL (3 enabled). 2 clicks / 9.5% CTR. Optional only if George pauses one RSA to free a slot.",
        "blocker": "No open slot — 3 enabled RSAs.",
        "headlines": [
            "Invoices Stacking Up?",
            "Hire a Filipino Bookkeeper",
            "Dedicated Books Support",
            "On Australian Hours",
            "You Interview. You Pick.",
            "We Handle Employment Admin",
            "Obligation-Free Chat",
            "Day-to-Day Books Covered",
            "Not a Freelance Books Gig",
            "Talk to a Specialist",
            "Reconciliations Get Done",
            "Finance Owner Gets Time Back",
            "Nobody Starts Till You Say",
            "We Recruit. You Decide.",
            "Employers Hiring Only",
        ],
        "descriptions": [
            "Books falling behind? Hire a dedicated Filipino bookkeeper for Australian hours.",
            "Obligation-free chat. We recruit. You interview. We handle employment admin.",
            "A dedicated bookkeeper owns day-to-day books support — not a gig marketplace.",
            "You interview before anyone joins. Rates discussed for the role.",
        ],
    },
}


def validate_all() -> None:
    for name, d in {**DRAFTS, **ALSO_CONSIDER}.items():
        if len(d["headlines"]) != 15:
            raise SystemExit(f"{name}: need 15 headlines, got {len(d['headlines'])}")
        if len(d["descriptions"]) != 4:
            raise SystemExit(f"{name}: need 4 descriptions, got {len(d['descriptions'])}")
        chk(d["headlines"], H_MAX, f"{name} H")
        chk(d["descriptions"], D_MAX, f"{name} D")
        # Soft ban: no USD pricing, no wrong phones
        blob = " ".join(d["headlines"] + d["descriptions"])
        for bad in ("$8", "888", "954", "964", "310", "VA PH", "SMM", "DKI"):
            if bad in blob and bad not in ("VA",):  # allow "Virtual Assistant"
                # Allow nothing with phone digits in RSA body for AU drafts
                if bad in ("$8", "888", "954", "964", "310"):
                    raise SystemExit(f"{name}: forbidden token {bad!r} in copy")


def asset_gap_report(probe: dict) -> dict:
    def enabled(mkt: str, typ: str) -> list[dict]:
        return [
            r
            for r in probe["assets"][mkt]
            if r["link_status"] == "ENABLED" and r["type"] == typ
        ]

    au_call = enabled("AU", "CALL")
    us_call = enabled("US", "CALL")
    au_snip = enabled("AU", "STRUCTURED_SNIPPET")
    us_snip = enabled("US", "STRUCTURED_SNIPPET")
    au_sl = enabled("AU", "SITELINK")
    us_sl = enabled("US", "SITELINK")
    au_co = enabled("AU", "CALLOUT")
    us_co = enabled("US", "CALLOUT")

    suggestions = []

    if not au_call:
        suggestions.append(
            {
                "market": "AU",
                "severity": "high",
                "asset_type": "CALL",
                "finding": "No ENABLED campaign Call asset on VC_AU_S_CORE / VC_AU_S_ROLES.",
                "suggestion": f"Add campaign Call with {AU_PHONE} on both Stage 1 campaigns (match site).",
            }
        )
    else:
        phones = sorted({r.get("phone") for r in au_call})
        suggestions.append(
            {
                "market": "AU",
                "severity": "info",
                "asset_type": "CALL",
                "finding": f"ENABLED Call phones: {phones}",
                "suggestion": f"Confirm digits match {AU_PHONE}.",
            }
        )

    if not au_snip:
        suggestions.append(
            {
                "market": "AU",
                "severity": "medium",
                "asset_type": "STRUCTURED_SNIPPET",
                "finding": "No ENABLED structured snippet on AU VC_* campaigns.",
                "suggestion": "Mirror US Types snippet (Virtual Assistants, Bookkeepers, Accountants, Social Media Managers, Customer Support, Recruiters).",
            }
        )

    # AU sitelink quality
    au_sl_texts = [(r["campaign"], r.get("text"), (r.get("final_urls") or [None])[0]) for r in au_sl]
    wrong_how = [x for x in au_sl_texts if x[1] == "How Hiring Works" and x[2] and "how-it-works" not in x[2]]
    if wrong_how:
        suggestions.append(
            {
                "market": "AU",
                "severity": "medium",
                "asset_type": "SITELINK",
                "finding": f"How Hiring Works sitelink points at hub, not /how-it-works ({len(wrong_how)} link(s)).",
                "suggestion": "Pause wrong URL; keep how-it-works?market=au version (US already cleaned this).",
            }
        )
    home_clutter = [x for x in au_sl_texts if x[1] in ("AU Employer Home",) or (x[1] == "Tell Us Who You Need" and x[2] and x[2].rstrip("/").endswith("/au"))]
    if any(x[1] == "AU Employer Home" for x in au_sl_texts):
        suggestions.append(
            {
                "market": "AU",
                "severity": "medium",
                "asset_type": "SITELINK",
                "finding": "AU Employer Home sitelink still ENABLED on CORE (homepage clutter).",
                "suggestion": "Pause AU Employer Home; keep Tell Us Who You Need → /au#gate (or role #gate).",
            }
        )
    # Duplicate same-text ENABLED sitelinks
    from collections import Counter

    for camp in ("VC_AU_S_CORE", "VC_AU_S_ROLES"):
        texts = [t for c, t, _ in au_sl_texts if c == camp]
        dupes = [t for t, n in Counter(texts).items() if n > 1]
        if dupes:
            suggestions.append(
                {
                    "market": "AU",
                    "severity": "medium",
                    "asset_type": "SITELINK",
                    "finding": f"{camp}: duplicate ENABLED sitelink text: {dupes}",
                    "suggestion": "Pause older/wrong-URL duplicates so Google is not choosing between twins.",
                }
            )

    role_sl_missing = []
    for role_text, path in (
        ("Accounting Hire", "/au/accounting"),
        ("Sales Hire", "/au/sales"),
        ("Customer Service Hire", "/au/customer-service"),
        ("HR Hire", "/au/hr"),
        ("Recruitment Hire", "/au/recruitment"),
    ):
        if not any(t == role_text for _, t, _ in au_sl_texts):
            role_sl_missing.append(f"{role_text} → {path}")
    if role_sl_missing:
        suggestions.append(
            {
                "market": "AU",
                "severity": "low",
                "asset_type": "SITELINK",
                "finding": "ROLES sitelinks thin beyond marketing/social/books.",
                "suggestion": "Optional adds: " + "; ".join(role_sl_missing[:3]) + ("…" if len(role_sl_missing) > 3 else ""),
            }
        )

    if len(au_co) < 8:
        suggestions.append(
            {
                "market": "AU",
                "severity": "low",
                "asset_type": "CALLOUT",
                "finding": f"AU has {len({(r['campaign'], r.get('text')) for r in au_co})} ENABLED campaign×callout pairs (6 texts × 2 camps).",
                "suggestion": "Callouts look solid. Optional AU-only: Australian Hours · Obligation-Free Chat.",
            }
        )

    # US
    us_phones = sorted({r.get("phone") for r in us_call})
    if us_call:
        suggestions.append(
            {
                "market": "US",
                "severity": "info",
                "asset_type": "CALL",
                "finding": f"ENABLED Call on CORE+ROLES: {us_phones}",
                "suggestion": f"Matches expected public number {US_PHONE}." if any("964" in (p or "") for p in us_phones) else f"Verify against {US_PHONE}.",
            }
        )
    else:
        suggestions.append(
            {
                "market": "US",
                "severity": "high",
                "asset_type": "CALL",
                "finding": "No ENABLED campaign Call on VC_US_* Stage 1.",
                "suggestion": f"Re-attach Call {US_PHONE} to CORE + ROLES.",
            }
        )

    if us_snip:
        suggestions.append(
            {
                "market": "US",
                "severity": "info",
                "asset_type": "STRUCTURED_SNIPPET",
                "finding": "Types snippet ENABLED on CORE + ROLES.",
                "suggestion": "Keep. No action.",
            }
        )

    suggestions.append(
        {
            "market": "US",
            "severity": "low",
            "asset_type": "SITELINK",
            "finding": f"US has {len(us_sl)} ENABLED sitelinks across CORE+ROLES; several older duplicates already PAUSED.",
            "suggestion": "Looks cleaned vs prior 310 sweep. Optional: add Accounting / Sales role sitelinks if you want parity with more LPs.",
        }
    )
    suggestions.append(
        {
            "market": "BOTH",
            "severity": "info",
            "asset_type": "IMAGE",
            "finding": "Image extensions not queried this pass (campaign_asset IMAGE enum invalid).",
            "suggestion": "If Ads UI shows thin images on VC_*, consider role portraits from ads-launch/assets/role-portraits — suggestions only.",
        }
    )

    return {
        "phones_expected": {"AU": AU_PHONE, "US": US_PHONE},
        "counts": {
            "AU_CALL_enabled": len(au_call),
            "AU_SITELINK_enabled": len(au_sl),
            "AU_CALLOUT_enabled": len(au_co),
            "AU_SNIPPET_enabled": len(au_snip),
            "US_CALL_enabled": len(us_call),
            "US_SITELINK_enabled": len(us_sl),
            "US_CALLOUT_enabled": len(us_co),
            "US_SNIPPET_enabled": len(us_snip),
        },
        "suggestions": suggestions,
    }


def build_payload(probe: dict) -> dict:
    validate_all()
    by_name = {s["ad_group"]: s for s in probe["ad_groups"]}
    must = []
    for ag_name, draft in DRAFTS.items():
        inv = by_name.get(ag_name)
        if not inv:
            raise SystemExit(f"Draft for unknown AG {ag_name}")
        final_url = (inv.get("final_urls") or [None])[0] or "https://www.virtualcoworker.app/au"
        paused_ids = [p["ad_id"] for p in inv.get("paused_ads") or []]
        must.append(
            {
                "ad_group": ag_name,
                "ad_group_id": inv.get("ad_group_id"),
                "campaign": inv.get("campaign"),
                "campaign_status": inv.get("campaign_status"),
                "ad_group_status": inv.get("ad_group_status"),
                "final_url": final_url,
                "path1": draft["path1"],
                "path2": draft["path2"],
                "enabled_rsas": inv.get("enabled_rsas"),
                "paused_rsas": inv.get("paused_rsas"),
                "rsa_count": inv.get("rsa_count"),
                "open_enabled_slot": inv.get("open_enabled_slot"),
                "room_to_create": inv.get("room_to_create"),
                "api_action": inv.get("create_vs_update"),
                "preferred_paused_ad_id": paused_ids[0] if paused_ids and inv.get("create_vs_update") == "update_paused" else None,
                "metrics_30d": {
                    "impr": inv.get("impr"),
                    "clicks": inv.get("clicks"),
                    "ctr": inv.get("ctr"),
                    "cost": inv.get("cost"),
                },
                "why": draft["why"],
                "headlines": draft["headlines"],
                "descriptions": draft["descriptions"],
                "priority": "must_fill",
                "status": "DRAFT_NOT_POSTED",
            }
        )

    also = []
    for ag_name, draft in ALSO_CONSIDER.items():
        inv = by_name.get(ag_name, {})
        final_url = (inv.get("final_urls") or [None])[0] or "https://www.virtualcoworker.app/au"
        also.append(
            {
                "ad_group": ag_name,
                "ad_group_id": inv.get("ad_group_id"),
                "campaign": inv.get("campaign"),
                "final_url": final_url,
                "path1": draft["path1"],
                "path2": draft["path2"],
                "enabled_rsas": inv.get("enabled_rsas"),
                "paused_rsas": inv.get("paused_rsas"),
                "blocker": draft["blocker"],
                "why": draft["why"],
                "headlines": draft["headlines"],
                "descriptions": draft["descriptions"],
                "priority": "also_consider",
                "status": "DRAFT_OPTIONAL_NOT_POSTED",
            }
        )

    blockers = [
        {
            "ad_group": s["ad_group"],
            "campaign": s["campaign"],
            "enabled_rsas": s["enabled_rsas"],
            "paused_rsas": s["paused_rsas"],
            "note": "Already 3 RSAs enabled — no open slot without pausing one first.",
        }
        for s in probe["ad_groups"]
        if not s.get("needs_draft")
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "banner": "DRAFT — not posted. Approve before API create.",
        "mutations": 0,
        "account": {"id": "5735391940", "label": "AU"},
        "campaigns": ["VC_AU_S_CORE", "VC_AU_S_ROLES"],
        "phones": {"AU": AU_PHONE, "US": US_PHONE},
        "probe_api_calls": probe.get("api_calls"),
        "probe_generated_at": probe.get("generated_at"),
        "must_fill_count": len(must),
        "also_consider_count": len(also),
        "must_fill": must,
        "also_consider": also,
        "blockers_full_ags": blockers,
        "assets_gap": asset_gap_report(probe),
        "notes": [
            "Zero Ads API mutations in this deliverable.",
            "Most open slots are update_paused (3 RSAs already exist; rewrite paused + enable) — only Offshore_VA_PH and Admin_City_Test have create room.",
            "AU RSA copy: no USD pricing, no DKI, spell out role words, employment admin language.",
            "Brand campaigns deferred — not audited for RSA drafts.",
        ],
    }


def render_html(payload: dict) -> str:
    def esc(s: object) -> str:
        return html.escape(str(s if s is not None else ""))

    def rsa_card(item: dict, optional: bool = False) -> str:
        cls = "card optional" if optional else "card"
        badge = "ALSO CONSIDER" if optional else "MUST FILL"
        metrics = item.get("metrics_30d") or {}
        ctr = metrics.get("ctr")
        ctr_s = f"{ctr * 100:.1f}%" if isinstance(ctr, (int, float)) else "—"
        action = item.get("api_action") or item.get("blocker") or "—"
        paused = item.get("preferred_paused_ad_id")
        h_lis = "".join(f"<li><code>{esc(h)}</code> <span class='len'>{len(h)}</span></li>" for h in item["headlines"])
        d_lis = "".join(f"<li><code>{esc(d)}</code> <span class='len'>{len(d)}</span></li>" for d in item["descriptions"])
        return f"""
<article class="{cls}" id="{esc(item['ad_group'])}">
  <header>
    <p class="badge">{esc(badge)}</p>
    <h3>{esc(item['ad_group'])}</h3>
    <p class="meta">{esc(item.get('campaign'))} · enabled {esc(item.get('enabled_rsas'))} · paused {esc(item.get('paused_rsas'))} · action <strong>{esc(action)}</strong></p>
  </header>
  <p><strong>Final URL:</strong> <a href="{esc(item['final_url'])}" target="_blank" rel="noopener">{esc(item['final_url'])}</a>
     · paths <code>{esc(item.get('path1'))}/{esc(item.get('path2'))}</code></p>
  <p class="why"><strong>Why:</strong> {esc(item.get('why'))}</p>
  <p class="metrics">30d: {esc(metrics.get('impr', '—'))} impr · {esc(metrics.get('clicks', '—'))} clicks · {esc(ctr_s)} CTR
    {" · update paused ad " + esc(paused) if paused else ""}</p>
  <div class="cols">
    <div><h4>15 headlines</h4><ol class="copy">{h_lis}</ol></div>
    <div><h4>4 descriptions</h4><ol class="copy">{d_lis}</ol></div>
  </div>
</article>"""

    must_html = "\n".join(rsa_card(i) for i in payload["must_fill"])
    also_html = "\n".join(rsa_card(i, optional=True) for i in payload["also_consider"])
    blockers = "".join(
        f"<li><strong>{esc(b['ad_group'])}</strong> ({esc(b['campaign'])}) — {esc(b['note'])}</li>"
        for b in payload["blockers_full_ags"]
    )
    gaps = "".join(
        f"""<li class="sev-{esc(s['severity'])}"><span class="tag">{esc(s['market'])} · {esc(s['asset_type'])} · {esc(s['severity'])}</span>
        <strong>{esc(s['finding'])}</strong><br />→ {esc(s['suggestion'])}</li>"""
        for s in payload["assets_gap"]["suggestions"]
    )
    counts = payload["assets_gap"]["counts"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>AU RSA Draft Review · Virtual Coworker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    .draft-banner {{
      background: #1a1a1a; color: #fff; padding: 1rem 1.25rem; border-radius: 8px;
      border-left: 6px solid #e8a317; margin: 0 0 1.5rem;
    }}
    .draft-banner strong {{ color: #ffd56a; }}
    .stats {{ display: flex; flex-wrap: wrap; gap: .75rem; margin: 1rem 0 1.5rem; }}
    .stat {{ background: #f4f4f2; padding: .75rem 1rem; border-radius: 8px; min-width: 8rem; }}
    .stat b {{ display: block; font-size: 1.4rem; }}
    .card {{ border: 1px solid #ddd; border-radius: 10px; padding: 1rem 1.25rem; margin: 0 0 1.25rem; background: #fff; }}
    .card.optional {{ border-style: dashed; opacity: .92; background: #fafaf8; }}
    .badge {{ display: inline-block; font-size: .7rem; letter-spacing: .04em; font-weight: 700;
      background: #0b6e4f; color: #fff; padding: .2rem .5rem; border-radius: 4px; margin: 0 0 .35rem; }}
    .optional .badge {{ background: #6b5b00; }}
    .meta, .metrics, .why {{ color: #333; margin: .35rem 0; }}
    .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    @media (max-width: 900px) {{ .cols {{ grid-template-columns: 1fr; }} }}
    ol.copy {{ margin: 0; padding-left: 1.2rem; font-family: "IBM Plex Mono", monospace; font-size: .82rem; }}
    ol.copy .len {{ color: #888; font-size: .7rem; }}
    .sev-high .tag {{ background: #8b1e1e; color: #fff; }}
    .sev-medium .tag {{ background: #8a5a00; color: #fff; }}
    .sev-low .tag, .sev-info .tag {{ background: #345; color: #fff; }}
    .tag {{ display: inline-block; font-size: .65rem; padding: .15rem .4rem; border-radius: 3px; margin-right: .35rem; }}
    #assets li {{ margin: 0 0 .85rem; line-height: 1.4; }}
    .toc a {{ margin-right: .75rem; }}
  </style>
</head>
<body data-page="au-rsa-review.html" data-foot="Draft RSA review<br />Not posted">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="page-head">
        <p class="kicker">Ads · AU Stage 1 · draft only</p>
        <h1>AU RSA draft review</h1>
        <p>Human responsive search ads for <code>VC_AU_S_CORE</code> + <code>VC_AU_S_ROLES</code>. Generated {esc(payload['generated_at'])}.</p>
      </header>

      <div class="draft-banner" role="status">
        <strong>DRAFT — not posted. Approve before API create.</strong><br />
        Zero Ads mutations in this pack. Machine JSON: <code>ads-launch/_au_rsa_draft.json</code>.
        Phones for reference: AU <strong>{esc(AU_PHONE)}</strong> · US <strong>{esc(US_PHONE)}</strong> (not stuffed into every RSA).
      </div>

      <div class="stats">
        <div class="stat"><b>{esc(payload['must_fill_count'])}</b> must-fill drafts</div>
        <div class="stat"><b>{esc(payload['also_consider_count'])}</b> also-consider</div>
        <div class="stat"><b>{esc(len(payload['blockers_full_ags']))}</b> full AGs (no slot)</div>
        <div class="stat"><b>{esc(payload.get('probe_api_calls'))}</b> read-only API calls</div>
        <div class="stat"><b>0</b> mutations</div>
      </div>

      <section class="panel">
        <div class="panel-hd"><p class="kicker">Jump</p><h2>Contents</h2></div>
        <div class="panel-bd toc">
          <a href="#must">Must-fill RSAs</a>
          <a href="#also">Also consider</a>
          <a href="#blockers">No open slot</a>
          <a href="#assets">Assets gap — US &amp; AU</a>
        </div>
      </section>

      <section class="panel" id="must">
        <div class="panel-hd">
          <p class="kicker">Open slots</p>
          <h2>Must-fill — one new RSA per ad group</h2>
        </div>
        <div class="panel-bd">
          <p>Where enabled &lt; 3 after pauses. Most need <strong>update paused RSA + enable</strong> (already 3 ads). Create room only on Offshore + Admin City.</p>
          {must_html}
        </div>
      </section>

      <section class="panel" id="also">
        <div class="panel-hd">
          <p class="kicker">Optional</p>
          <h2>Also consider — not mixed with must-fill</h2>
        </div>
        <div class="panel-bd">
          <p>These ad groups already have <strong>3 enabled RSAs</strong>. Drafts only useful if George pauses one first.</p>
          {also_html}
        </div>
      </section>

      <section class="panel" id="blockers">
        <div class="panel-hd"><p class="kicker">Blockers</p><h2>No open slot</h2></div>
        <div class="panel-bd"><ul>{blockers}</ul></div>
      </section>

      <section class="panel" id="assets">
        <div class="panel-hd">
          <p class="kicker">Show only — do not create</p>
          <h2>Assets gap — US &amp; AU</h2>
        </div>
        <div class="panel-bd">
          <p>Campaign-level VC_* CORE/ROLES only. Recommendations only — <strong>not executed</strong>.</p>
          <p>Counts (ENABLED): AU Call {esc(counts['AU_CALL_enabled'])} · Sitelink {esc(counts['AU_SITELINK_enabled'])} ·
            Callout {esc(counts['AU_CALLOUT_enabled'])} · Snippet {esc(counts['AU_SNIPPET_enabled'])} ·
            US Call {esc(counts['US_CALL_enabled'])} · Sitelink {esc(counts['US_SITELINK_enabled'])} ·
            Callout {esc(counts['US_CALLOUT_enabled'])} · Snippet {esc(counts['US_SNIPPET_enabled'])}</p>
          <ul>{gaps}</ul>
        </div>
      </section>
    </main>
  </div>
  <script src="nav.js"></script>
</body>
</html>
"""


def main() -> int:
    if not PROBE.exists():
        raise SystemExit(f"Missing probe {PROBE} — run probe_au_rsa_assets_readonly.py first")
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    payload = build_payload(probe)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUT_HTML.write_text(render_html(payload), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_HTML}")
    print(f"must_fill={payload['must_fill_count']} also_consider={payload['also_consider_count']} mutations=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
