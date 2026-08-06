#!/usr/bin/env python3
"""Build Stage 1 Google Ads Editor import — role Search only (brand deferred).

No Ads API. Regenerates:
  - ads-launch/google-ads-editor-import.csv
  - mirrors into xray/docs/ads-launch/
"""

from __future__ import annotations

import csv
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ads-launch" / "google-ads-editor-import.csv"
MIRROR = ROOT / "xray" / "docs" / "ads-launch" / "google-ads-editor-import.csv"

HL_MAX = 30
DESC_MAX = 90
PATH_MAX = 15

SUFFIX = (
    "utm_source=google&utm_medium=cpc&utm_campaign={_campaign}"
    "&utm_content={_adgroup}&utm_term={keyword}&lp_version=stage1-v2"
)
TRACK = "{lpurl}?" + SUFFIX

FIELDS = [
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
    "Max CPC",
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

# Campaign-level negatives (Broad) — curated; do NOT include hire/hiring.
# Phrase-style multi-word kept as Broad negatives (Editor Broad neg covers close variants).
NEGATIVES = [
    # Job seeker
    "job",
    "jobs",
    "salary",
    "salaries",
    "wage",
    "wages",
    "pay rate",
    "career",
    "careers",
    "hiring me",
    "i need a job",
    "resume",
    "cv",
    "apply",
    "application",
    "employment",
    "intern",
    "internship",
    "job description",
    "job listings",
    "work from home job",
    "wfh job",
    "remote job",
    "online job",
    "online jobs",
    "part time job",
    "full time job",
    "no experience",
    "entry level",
    "indeed",
    "glassdoor",
    "jobstreet",
    "linkedin jobs",
    "onlinejobs",
    "onlinejobs.ph",
    "virtual assistant jobs",
    "virtual assistant job",
    "virtual assistant careers",
    "virtual assistant salary",
    "apply as virtual assistant",
    # Info / DIY
    "what is",
    "how to become",
    "tutorial",
    "course",
    "courses",
    "training",
    "certification",
    "certificate",
    "template",
    "examples",
    "definition",
    "diy",
    # Junk / tire-kick
    "free",
    "cheap",
    "cheapest",
    "torrent",
    "reddit",
    "youtube",
    "pdf",
    # Platforms (protect Core intent; not conquest)
    "upwork",
    "fiverr",
    "freelancer.com",
    # Excluded verticals / language
    "medical",
    "nurse",
    "nursing",
    "doctor",
    "physician",
    "healthcare staffing",
    "medical staffing",
    "software developer",
    "web developer",
    "web developers",
    "programmer",
    "programming",
    "coding",
    "software engineer",
    "it staffing",
    "tech staffing",
    "technology staffing",
    "spanish",
    "español",
    "bilingual spanish",
    # Misc dual-intent
    "consumer",
    "personal assistant job",
]

ROLES = [
    "digital_marketing",
    "social_media",
    "accounting",
    "bookkeeping",
    "administration",
    "customer_service",
    "hr",
    "recruitment",
    "sales",
]

ROLE_LABEL = {
    "digital_marketing": "Digital Marketing",
    "social_media": "Social Media",
    "accounting": "Accounting",
    "bookkeeping": "Bookkeeping",
    "administration": "Administration",
    "customer_service": "Customer Service",
    "hr": "Human Resources",
    "recruitment": "Recruitment",
    "sales": "Sales",
}

# Exact keywords per role (employer / PH / Filipino / hire / outsource language).
# Harvested + curated from Editor archaeology; job/medical/tech/spanish stripped.
EXACT: dict[str, list[str]] = {
    "digital_marketing": [
        "hire digital marketer philippines",
        "hire filipino digital marketing manager",
        "hire a filipino digital marketing va",
        "outsource digital marketing philippines",
        "digital marketing outsourcing philippines",
        "digital marketer outsourcing philippines",
        "filipino digital marketing manager",
        "digital marketing manager philippines",
        "philippines digital marketing manager",
        "digital marketing managers philippines",
        "digital marketing virtual assistant",
        "virtual assistant digital marketing",
        "digital marketing va",
        "hire remote digital marketer",
        "remote digital marketing manager philippines",
        "virtual digital marketing manager philippines",
        "outsource digital marketing to philippines",
        "hire digital marketing va philippines",
        "filipino digital marketing va",
        "digital marketing staff philippines",
    ],
    "social_media": [
        "social media virtual assistant",
        "hire social media virtual assistant",
        "social media va philippines",
        "social media virtual assistant philippines",
        "social media manager philippines",
        "filipino social media manager",
        "hire social media manager philippines",
        "outsource social media philippines",
        "social media management virtual assistant",
        "hire filipino social media manager",
        "filipino social media specialist",
        "social media specialist philippines",
        "social media marketing virtual assistant",
        "virtual assistant social media manager",
        "hire social media va",
        "offshore social media manager",
        "philippines social media manager",
        "social media staff philippines",
        "hire remote social media manager",
        "filipino social media va",
    ],
    "accounting": [
        "hire accountant philippines",
        "hire filipino accountant",
        "hire a filipino accountant",
        "outsource accounting philippines",
        "outsource accountant philippines",
        "outsourced accounting philippines",
        "virtual accountant philippines",
        "filipino accountant",
        "accountant philippines",
        "philippines accountant",
        "accounting virtual assistant",
        "virtual assistant accountant",
        "hire virtual accountant philippines",
        "filipino accounting virtual assistant",
        "offshore accountant philippines",
        "remote accountant philippines",
        "hire remote accountant philippines",
        "accounting staff philippines",
        "accounts payable philippines",
        "hire accounts payable philippines",
    ],
    "bookkeeping": [
        "virtual bookkeeper philippines",
        "hire virtual bookkeeper philippines",
        "hire bookkeeper philippines",
        "hire a filipino bookkeeper",
        "hire filipino bookkeeper",
        "filipino bookkeeper",
        "filipino bookkeepers",
        "bookkeeper philippines",
        "philippines bookkeepers",
        "outsource bookkeeping philippines",
        "bookkeeping services philippines",
        "virtual bookkeeping philippines",
        "bookkeeping virtual assistant",
        "virtual assistant bookkeeping",
        "offshore bookkeeper",
        "offshore bookkeeper philippines",
        "remote bookkeeping philippines",
        "hire remote bookkeeper philippines",
        "philippines bookkeeping outsourcing",
        "virtual bookkeeping services philippines",
    ],
    "administration": [
        # General employer VA / admin (replaces old CORE — brand deferred, roles-first)
        "hire virtual assistant philippines",
        "hire a virtual assistant in the philippines",
        "hire filipino virtual assistant",
        "hire filipino va",
        "hiring virtual assistant philippines",
        "filipino virtual assistant",
        "filipino virtual assistants",
        "virtual assistant philippines",
        "philippines virtual assistant",
        "virtual assistant company philippines",
        "virtual assistant companies philippines",
        "virtual assistant services philippines",
        "outsource virtual assistant philippines",
        "hire va philippines",
        "filipino va",
        "hire offshore virtual assistant",
        "offshore virtual assistant philippines",
        "hire virtual assistant",
        "hire a virtual assistant",
        "virtual assistant for business",
        "virtual assistant company",
        "virtual assistant agency",
        "offshore virtual assistant",
        "dedicated virtual assistant",
        "virtual staffing company",
        "hire remote virtual assistant",
        "hire filipino administrative assistant",
        "administrative assistant philippines",
        "hire virtual administrative assistant",
        "filipino executive assistant",
        "hire executive assistant philippines",
        "virtual executive assistant philippines",
        "hire virtual executive assistant",
        "offshore executive assistant",
        "office administrator philippines",
        "hire admin assistant philippines",
    ],
    "customer_service": [
        "hire customer service virtual assistant",
        "customer service virtual assistant",
        "filipino customer service va",
        "hire filipino customer service",
        "hire filipino customer service representative",
        "customer service philippines",
        "customer service representative philippines",
        "outsource customer service philippines",
        "customer support outsourcing philippines",
        "virtual customer service philippines",
        "virtual customer support philippines",
        "hire philippines customer service",
        "filipino customer service",
        "customer care assistant philippines",
        "customer service assistant philippines",
        "hire remote customer service philippines",
        "offshore customer service philippines",
        "virtual customer service agent",
        "hire customer support philippines",
        "customer support staff philippines",
    ],
    "hr": [
        "hire virtual hr assistant",
        "filipino virtual hr assistant",
        "hire remote hr staff",
        "hire hr assistant philippines",
        "virtual hr assistant philippines",
        "filipino hr assistant",
        "outsource hr philippines",
        "hr virtual assistant philippines",
        "hire filipino hr assistant",
        "human resources assistant philippines",
        "hire human resources assistant philippines",
        "offshore hr assistant",
        "virtual human resources assistant",
        "hr staffing philippines",
        "hire hr coordinator philippines",
        "filipino human resources assistant",
        "remote hr assistant philippines",
        "outsource human resources philippines",
        "hire payroll assistant philippines",
        "virtual payroll assistant philippines",
    ],
    "recruitment": [
        "hire virtual recruitment assistant",
        "virtual recruitment assistant philippines",
        "recruitment assistant philippines",
        "filipino recruitment assistant",
        "hire filipino recruitment assistant",
        "hire recruitment assistant philippines",
        "offshore recruitment philippines",
        "remote recruitment assistant philippines",
        "recruitment virtual assistant",
        "hire a recruitment assistant",
        "recruitment assistant services",
        "filipino recruitment staff",
        "philippines recruitment assistant",
        "virtual recruiting assistant philippines",
        "hire recruiting assistant philippines",
        "outsource recruitment support philippines",
        "talent sourcing assistant philippines",
        "hire talent acquisition assistant philippines",
        "offshore recruitment assistant",
        "recruitment coordinator philippines",
    ],
    "sales": [
        "hire filipino lead generation specialist",
        "lead generation specialist philippines",
        "outsource lead generation philippines",
        "lead generation services philippines",
        "lead generation agency philippines",
        "filipino lead generation va",
        "filipino lead generation virtual assistant",
        "lead generation virtual assistant",
        "virtual assistant lead generation",
        "philippines lead generation specialist",
        "remote lead generation philippines",
        "virtual lead generation philippines",
        "hire sales assistant philippines",
        "filipino sales assistant",
        "virtual sales assistant philippines",
        "hire virtual sales assistant",
        "offshore sales assistant philippines",
        "appointment setter philippines",
        "hire appointment setter philippines",
        "filipino appointment setter",
    ],
}

# Extra Phrase (subset) — discovery without Broad.
PHRASE: dict[str, list[str]] = {
    "digital_marketing": [
        "hire digital marketer philippines",
        "outsource digital marketing philippines",
        "filipino digital marketing manager",
        "digital marketing virtual assistant",
        "hire digital marketing va",
    ],
    "social_media": [
        "hire social media virtual assistant",
        "social media manager philippines",
        "filipino social media manager",
        "outsource social media philippines",
        "social media va philippines",
    ],
    "accounting": [
        "hire accountant philippines",
        "outsource accounting philippines",
        "filipino accountant",
        "virtual accountant philippines",
        "hire filipino accountant",
    ],
    "bookkeeping": [
        "hire virtual bookkeeper philippines",
        "outsource bookkeeping philippines",
        "filipino bookkeeper",
        "virtual bookkeeper philippines",
        "hire bookkeeper philippines",
    ],
    "administration": [
        "hire virtual assistant philippines",
        "hire filipino virtual assistant",
        "virtual assistant for business",
        "hire filipino va",
        "offshore virtual assistant",
        "hire executive assistant philippines",
        "filipino executive assistant",
    ],
    "customer_service": [
        "hire customer service virtual assistant",
        "outsource customer service philippines",
        "filipino customer service",
        "customer support outsourcing philippines",
        "hire filipino customer service",
    ],
    "hr": [
        "hire virtual hr assistant",
        "filipino virtual hr assistant",
        "outsource hr philippines",
        "hire hr assistant philippines",
        "virtual hr assistant philippines",
    ],
    "recruitment": [
        "hire virtual recruitment assistant",
        "recruitment assistant philippines",
        "filipino recruitment assistant",
        "offshore recruitment philippines",
        "hire recruitment assistant philippines",
    ],
    "sales": [
        "outsource lead generation philippines",
        "lead generation specialist philippines",
        "hire filipino lead generation specialist",
        "virtual sales assistant philippines",
        "hire appointment setter philippines",
    ],
}

# Light city Phrase tests — Administration only (documented in report).
CITY_PHRASE_US = [
    "hire virtual assistant new york",
    "hire virtual assistant los angeles",
    "hire virtual assistant chicago",
    "hire filipino va texas",
    "hire virtual assistant florida",
]
CITY_PHRASE_AU = [
    "hire virtual assistant sydney",
    "hire virtual assistant melbourne",
    "hire virtual assistant brisbane",
    "hire filipino va australia",
    "hire virtual assistant perth",
]


def _len_ok(s: str, max_len: int) -> bool:
    # DKI / location insertion: pin may wrap the whole headline; validate default ≤ max.
    m = re.fullmatch(r"\{(?:KeyWord|KEYWORD|LOCATION\([^)]+\)):(.+)\}", s)
    if m:
        return len(m.group(1)) <= max_len
    return len(s) <= max_len


def validate_rsa(headlines: list[str], descs: list[str], where: str) -> None:
    assert len(headlines) == 15, f"{where}: need 15 headlines, got {len(headlines)}"
    assert len(descs) == 4, f"{where}: need 4 descriptions, got {len(descs)}"
    assert len(set(headlines)) == 15, f"{where}: duplicate headlines"
    assert len(set(descs)) == 4, f"{where}: duplicate descriptions"
    for i, h in enumerate(headlines, 1):
        if not _len_ok(h, HL_MAX):
            raise ValueError(f"{where} H{i} too long ({len(h)}): {h!r}")
    for i, d in enumerate(descs, 1):
        if len(d) > DESC_MAX:
            raise ValueError(f"{where} D{i} too long ({len(d)}): {d!r}")


def market_line(mkt: str) -> str:
    return "US" if mkt == "US" else "AU"


def rsa_pair(role: str, mkt: str) -> list[tuple[str, list[str], list[str], str, str]]:
    """Return list of (ad_name_suffix, headlines, descriptions, path1, path2)."""
    m = market_line(mkt)
    m_full = "US" if mkt == "US" else "Australian"
    label = ROLE_LABEL[role]

    # Shared safe claims — no pricing, no top 1%, no % savings guarantees.
    pairs: list[tuple[str, list[str], list[str], str, str]] = []

    def add(suffix: str, hs: list[str], ds: list[str], p1: str, p2: str) -> None:
        validate_rsa(hs, ds, f"{mkt}/{role}/{suffix}")
        for p in (p1, p2):
            if len(p) > PATH_MAX:
                raise ValueError(f"path too long: {p}")
        pairs.append((suffix, hs, ds, p1, p2))

    if role == "digital_marketing":
        add(
            "A_staffing",
            [
                "Hire Digital Marketing Staff",
                f"{m} Employer Staffing",
                "Filipino Marketing Talent",
                "Digital Marketing VA Hire",
                "Philippines Marketing Hire",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated Marketing Hire",
                "Offshore Marketing Staff",
                "Interview Your Shortlist",
                "Remote Marketing Manager",
                "Employers Hiring Only",
                "Marketing Staff Partner",
                "Clear Hiring Path",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Filipino digital marketing staff through a staffing partner.",
                "You interview shortlisted talent. We recruit, vet, and support the hire.",
                f"Employers only. Request a consult for your {m_full} business.",
                "Role-focused remote marketing hires — not freelance task gigs.",
            ],
            "marketing",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource Digital Marketing",
                "PH Digital Marketing Hire",
                "Hire Marketing VA Now",
                "Filipino SEO & Content VA",
                "Remote Campaign Support",
                "Marketing Ops Assistant",
                "Scale Marketing Capacity",
                "Dedicated Not Freelance",
                f"Staffing for {m} Teams",
                "Vetted Philippines Talent",
                "Marketing Role Shortlist",
                "Hire Ongoing Marketing Help",
                "Business Marketing Staff",
                "Partner-Led VA Hiring",
                "Book an Employer Consult",
            ],
            [
                "Outsource digital marketing support to vetted Philippines specialists.",
                "Ongoing dedicated hire for campaigns, content support, and reporting ops.",
                "Staffing partner model: shortlist, interview, then dedicated placement support.",
                f"Built for {m_full} employers hiring remote marketing capacity.",
            ],
            "digital",
            "ph",
        )
    elif role == "social_media":
        add(
            "A_staffing",
            [
                "Hire Social Media Staff",
                "Social Media VA Philippines",
                "Filipino Social Media Hire",
                f"{m} Teams Hiring SMM",
                "Recruit Vet & Manage",
                "Not a Freelance Market",
                "Dedicated Social Hire",
                "Offshore Social Manager",
                "Interview Before You Hire",
                "Employers Hiring Only",
                "Social Media Staffing",
                "Remote SMM for Business",
                "Clear Employer Path",
                "Philippines SMM Talent",
                "Request a Hiring Consult",
            ],
            [
                "Hire a dedicated Filipino social media manager through a staffing partner.",
                "You interview the shortlist. We handle recruiting, vetting, and hire support.",
                f"Employers only — request a consult for your {m_full} business.",
                "Ongoing social media capacity — not one-off freelance gigs.",
            ],
            "social",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource Social Media",
                "Hire Social Media VA",
                "PH Social Media Manager",
                "Content & Community VA",
                "Social Scheduling Support",
                "Brand Social Ops Hire",
                "Scale Social Capacity",
                "Dedicated SMM Assistant",
                f"Staffing for {m} Brands",
                "Vetted Social Media Talent",
                "Remote Social Specialist",
                "Hire Ongoing Social Help",
                "Business Social Staffing",
                "Partner-Led SMM Hiring",
                "Book an Employer Consult",
            ],
            [
                "Outsource social media management to vetted Philippines specialists.",
                "Dedicated help for posting, community ops, and content workflows.",
                "Staffing partner process: recruit, shortlist, you interview, we support.",
                f"For {m_full} employers who need reliable remote social capacity.",
            ],
            "social",
            "ph",
        )
    elif role == "accounting":
        add(
            "A_staffing",
            [
                "Hire Accountant Philippines",
                "Filipino Accountant Hire",
                "Outsource Accounting PH",
                f"{m} Employer Accounting",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated Accounting Hire",
                "Offshore Accounting Staff",
                "Interview Your Shortlist",
                "Employers Hiring Only",
                "Virtual Accountant PH",
                "Accounting Staff Partner",
                "Clear Hiring Path",
                "Remote Accounting Talent",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Filipino accounting staff through a staffing partner.",
                "You interview shortlisted talent. We recruit, vet, and support the hire.",
                f"Employers only. Request a consult for your {m_full} business.",
                "Accounting support hires — dedicated remote staff, not task gigs.",
            ],
            "accounting",
            "hire",
        )
        add(
            "B_role",
            [
                "PH Accounting Outsourcing",
                "Hire Virtual Accountant",
                "Accounts Payable Support",
                "Book a Finance Staff Hire",
                "Filipino Accounting VA",
                "Remote Ledger Support",
                "Scale Finance Ops",
                "Dedicated Not Freelance",
                f"Staffing for {m} Finance",
                "Vetted Accounting Talent",
                "Accounting Role Shortlist",
                "Hire Ongoing AP Help",
                "Business Accounting Staff",
                "Partner-Led Finance Hire",
                "Book an Employer Consult",
            ],
            [
                "Outsource accounting support to vetted Philippines specialists.",
                "Dedicated help for AP/AR workflows and day-to-day accounting ops.",
                "Staffing partner model with interview-before-hire shortlists.",
                f"Built for {m_full} employers hiring remote accounting capacity.",
            ],
            "accounting",
            "ph",
        )
    elif role == "bookkeeping":
        add(
            "A_staffing",
            [
                "Hire Bookkeeper Philippines",
                "Virtual Bookkeeper PH",
                "Filipino Bookkeeper Hire",
                f"{m} Teams Hiring Books",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated Bookkeeping Hire",
                "Offshore Bookkeeper",
                "Interview Before You Hire",
                "Employers Hiring Only",
                "Bookkeeping Staff Partner",
                "Remote Books Talent",
                "Clear Employer Path",
                "PH Bookkeeping Staff",
                "Request a Hiring Consult",
            ],
            [
                "Hire a dedicated Filipino bookkeeper through a staffing partner.",
                "You interview the shortlist. We recruit, vet, and support placement.",
                f"Employers only — consult for your {m_full} bookkeeping hire.",
                "Ongoing bookkeeping capacity — not marketplace task gigs.",
            ],
            "bookkeeping",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource Bookkeeping PH",
                "Hire Virtual Bookkeeper",
                "Philippines Bookkeeping",
                "Remote Books Assistant",
                "Weekly Books Support",
                "Scale Bookkeeping Ops",
                "Dedicated Books VA",
                "Filipino Books Specialist",
                f"Staffing for {m} SMBs",
                "Vetted Bookkeeping Talent",
                "Bookkeeping Shortlist",
                "Hire Ongoing Books Help",
                "Business Books Staffing",
                "Partner-Led Books Hire",
                "Book an Employer Consult",
            ],
            [
                "Outsource bookkeeping to vetted Philippines specialists.",
                "Dedicated remote bookkeeping support for growing businesses.",
                "Staffing partner process: shortlist, interview, dedicated hire support.",
                f"For {m_full} employers who need reliable books capacity.",
            ],
            "books",
            "ph",
        )
    elif role == "administration":
        add(
            "A_staffing",
            [
                "Hire Virtual Assistant PH",
                "Filipino VA for Business",
                "Hire Filipino VA Staff",
                f"{m} Employer VA Hiring",
                "Recruit Vet & Manage",
                "Not a Freelance Market",
                "Dedicated Remote Hire",
                "Offshore VA Partner",
                "Interview Before You Hire",
                "Employers Hiring Only",
                "Virtual Staffing Company",
                "Admin Staff Philippines",
                "Clear Hiring Path",
                "Executive Assistant PH",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Philippines admin staff through a staffing partner.",
                "You interview shortlisted talent. We recruit, vet, and support the hire.",
                f"Employers only. Request a consult for your {m_full} business.",
                "Dedicated virtual assistants — not a gig marketplace.",
            ],
            "admin",
            "hire",
        )
        add(
            "B_role",
            [
                # Light DKI — default must stay ≤30
                "{KeyWord:Hire Filipino VA}",
                "Philippines Admin Staff",
                "Hire Virtual EA Today",
                "Business VA Outsourcing",
                "Remote Admin Capacity",
                "Office Admin Philippines",
                "Scale Admin Operations",
                "Dedicated VA Not Gig",
                f"Staffing for {m} Teams",
                "Vetted Philippines Talent",
                "Admin Role Shortlist",
                "Hire Ongoing Admin Help",
                "Partner-Led VA Hiring",
                "Virtual Admin Support",
                "Book an Employer Consult",
            ],
            [
                "Outsource administration support to vetted Filipino virtual assistants.",
                "Dedicated help for inbox, scheduling, documentation, and ops follow-through.",
                "Staffing partner model with interview-before-hire shortlists.",
                f"Built for {m_full} employers hiring remote admin capacity.",
            ],
            "va",
            "ph",
        )
    elif role == "customer_service":
        add(
            "A_staffing",
            [
                "Hire Customer Service PH",
                "Filipino Support Staff",
                "CS Virtual Assistant Hire",
                f"{m} Employer Support Hire",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated Support Hire",
                "Offshore Customer Care",
                "Interview Your Shortlist",
                "Employers Hiring Only",
                "Customer Support Partner",
                "Remote Support Talent",
                "Clear Hiring Path",
                "PH Customer Service Hire",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Filipino customer service staff through a staffing partner.",
                "You interview shortlisted talent. We recruit, vet, and support the hire.",
                f"Employers only. Request a consult for your {m_full} support hire.",
                "Ongoing customer support capacity — not freelance task gigs.",
            ],
            "support",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource Customer Service",
                "Hire CS Representative PH",
                "Virtual Customer Support",
                "Chat & Email Support VA",
                "Customer Care Philippines",
                "Scale Support Capacity",
                "Dedicated Support Agent",
                "Filipino Support VA",
                f"Staffing for {m} Support",
                "Vetted Support Talent",
                "Support Role Shortlist",
                "Hire Ongoing CS Help",
                "Business Support Staffing",
                "Partner-Led Support Hire",
                "Book an Employer Consult",
            ],
            [
                "Outsource customer service to vetted Philippines specialists.",
                "Dedicated remote support for inbox, chat, and customer care workflows.",
                "Staffing partner process: shortlist, interview, dedicated hire support.",
                f"For {m_full} employers who need reliable remote support capacity.",
            ],
            "support",
            "ph",
        )
    elif role == "hr":
        add(
            "A_staffing",
            [
                "Hire Virtual HR Assistant",
                "Filipino HR Staff Hire",
                "HR Assistant Philippines",
                f"{m} Employer HR Hiring",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated HR Hire",
                "Offshore HR Support",
                "Interview Before You Hire",
                "Employers Hiring Only",
                "HR Staffing Partner",
                "Remote HR Talent",
                "Clear Hiring Path",
                "PH Human Resources Hire",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Filipino HR support staff through a staffing partner.",
                "You interview the shortlist. We recruit, vet, and support placement.",
                f"Employers only — consult for your {m_full} HR hire.",
                "Ongoing HR admin capacity — not marketplace task gigs.",
            ],
            "hr",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource HR Support PH",
                "Hire HR Coordinator PH",
                "Virtual HR Operations",
                "Payroll Admin Assistant",
                "People Ops Support Hire",
                "Scale HR Administration",
                "Dedicated HR VA",
                "Filipino HR Specialist",
                f"Staffing for {m} HR Teams",
                "Vetted HR Talent",
                "HR Role Shortlist",
                "Hire Ongoing HR Help",
                "Business HR Staffing",
                "Partner-Led HR Hiring",
                "Book an Employer Consult",
            ],
            [
                "Outsource HR administration to vetted Philippines specialists.",
                "Dedicated help for HR coordination, documentation, and people-ops support.",
                "Staffing partner model with interview-before-hire shortlists.",
                f"Built for {m_full} employers hiring remote HR capacity.",
            ],
            "hr",
            "ph",
        )
    elif role == "recruitment":
        add(
            "A_staffing",
            [
                "Hire Recruitment Assistant",
                "Filipino Recruiting Staff",
                "Recruitment VA Philippines",
                f"{m} Talent Ops Hiring",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated Recruiting Hire",
                "Offshore Recruiting Help",
                "Interview Your Shortlist",
                "Employers Hiring Only",
                "Recruiting Staff Partner",
                "Remote Recruiting Talent",
                "Clear Hiring Path",
                "PH Recruitment Support",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Filipino recruitment support through a staffing partner.",
                "You interview shortlisted talent. We recruit, vet, and support the hire.",
                f"Employers only. Request a consult for your {m_full} recruiting hire.",
                "Recruiting coordination capacity — dedicated staff, not task gigs.",
            ],
            "recruit",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource Recruiting Support",
                "Hire Recruiting Assistant",
                "Talent Sourcing Assistant",
                "Virtual Recruiting Ops",
                "Screening Support PH",
                "Scale Recruiting Capacity",
                "Dedicated Recruiting VA",
                "Filipino Recruiting Hire",
                f"Staffing for {m} TA Teams",
                "Vetted Recruiting Talent",
                "Recruiting Role Shortlist",
                "Hire Ongoing TA Help",
                "Business Recruiting Staff",
                "Partner-Led TA Hiring",
                "Book an Employer Consult",
            ],
            [
                "Outsource recruitment support to vetted Philippines specialists.",
                "Dedicated help for sourcing coordination, screening support, and TA ops.",
                "Staffing partner process: shortlist, interview, dedicated hire support.",
                f"For {m_full} employers who need reliable recruiting capacity.",
            ],
            "recruit",
            "ph",
        )
    elif role == "sales":
        add(
            "A_staffing",
            [
                "Hire Sales Support PH",
                "Lead Gen Specialist PH",
                "Filipino Sales Assistant",
                f"{m} Employer Sales Hire",
                "Recruit Vet & Manage",
                "Not a Gig Marketplace",
                "Dedicated Sales Hire",
                "Offshore Lead Gen Staff",
                "Interview Before You Hire",
                "Employers Hiring Only",
                "Sales Staffing Partner",
                "Remote Sales Talent",
                "Clear Hiring Path",
                "PH Appointment Setters",
                "Request a Hiring Consult",
            ],
            [
                "Hire dedicated Filipino sales support staff through a staffing partner.",
                "You interview the shortlist. We recruit, vet, and support placement.",
                f"Employers only — consult for your {m_full} sales hire.",
                "Lead gen and sales support capacity — dedicated, not freelance gigs.",
            ],
            "sales",
            "hire",
        )
        add(
            "B_role",
            [
                "Outsource Lead Generation",
                "Hire Appointment Setter PH",
                "Virtual Sales Assistant",
                "Pipeline Support Staff",
                "Lead Research VA Hire",
                "Scale Outbound Capacity",
                "Dedicated Lead Gen VA",
                "Filipino Lead Gen Hire",
                f"Staffing for {m} Sales",
                "Vetted Sales Support",
                "Sales Role Shortlist",
                "Hire Ongoing Lead Help",
                "Business Sales Staffing",
                "Partner-Led Sales Hire",
                "Book an Employer Consult",
            ],
            [
                "Outsource lead generation support to vetted Philippines specialists.",
                "Dedicated help for prospecting support, lists, and appointment setting.",
                "Staffing partner model with interview-before-hire shortlists.",
                f"Built for {m_full} employers hiring remote sales capacity.",
            ],
            "sales",
            "ph",
        )
    else:
        raise KeyError(role)

    return pairs


def city_rsa(mkt: str) -> tuple[list[str], list[str], str, str]:
    m = market_line(mkt)
    m_full = "US" if mkt == "US" else "Australian"
    headlines = [
        # Entire headline must be the insertion pin; default ≤30 chars
        "{LOCATION(City):Hire Filipino VA}",
        "Hire Virtual Assistant",
        "Filipino VA for Business",
        f"{m} Employer Staffing",
        "Recruit Vet & Manage",
        "Not a Freelance Market",
        "Dedicated Remote Hire",
        "Philippines Admin Staff",
        "Interview Before You Hire",
        "Employers Hiring Only",
        "Offshore VA Partner",
        "Clear Hiring Path",
        "Remote Admin Capacity",
        "Partner-Led VA Hiring",
        "Request a Hiring Consult",
    ]
    descs = [
        "Hire dedicated Philippines virtual assistants for your business operations.",
        "City-aware headline test with staffing-partner hiring — you interview the shortlist.",
        f"Employers only. Request a consult for your {m_full} business.",
        "Light geo creative test — same employer LP and gate as core admin ads.",
    ]
    validate_rsa(headlines, descs, f"{mkt}/administration/city")
    return headlines, descs, "hire", "local"


def blank_row() -> dict[str, str]:
    return {k: "" for k in FIELDS}


def camp_name(mkt: str, role: str) -> str:
    return f"VC_{mkt}_S_ROLE_{role}"


def build() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for mkt, loc, budget_ph in (
        ("US", "United States", "[APPROVAL_DAILY_BUDGET_USD]"),
        ("AU", "Australia", "[APPROVAL_DAILY_BUDGET_AUD]"),
    ):
        base_url = f"https://vision-three-alpha.vercel.app/{mkt.lower()}"
        for role in ROLES:
            cname = camp_name(mkt, role)
            comment = (
                f"Stage1 Max Clicks; Search partners OFF; Display OFF; "
                f"brand deferred; role={ROLE_LABEL[role]}; confirm networks in Editor"
            )

            # Campaign
            r = blank_row()
            r.update(
                {
                    "Row Type": "Campaign",
                    "Campaign": cname,
                    "Campaign Type": "Search",
                    "Campaign Status": "Paused",
                    "Budget": budget_ph,
                    "Budget type": "Daily",
                    "Bid Strategy Type": "Maximize Clicks",
                    "Networks": "Google Search",
                    "Languages": "en",
                    "Location": loc,
                    "Location options": "Presence",
                    "Tracking template": TRACK,
                    "Final URL suffix": SUFFIX,
                    "Max CPC": "[APPROVAL_MAX_CPC]",
                    "Comment": comment,
                }
            )
            rows.append(r)

            primary_ag = f"{ROLE_LABEL[role].replace(' ', '_')}_PH"
            # Ad group
            r = blank_row()
            r.update(
                {
                    "Row Type": "Ad group",
                    "Campaign": cname,
                    "Campaign Type": "Search",
                    "Campaign Status": "Paused",
                    "Budget type": "Daily",
                    "Bid Strategy Type": "Maximize Clicks",
                    "Networks": "Google Search",
                    "Languages": "en",
                    "Location options": "Presence",
                    "Tracking template": TRACK,
                    "Final URL suffix": SUFFIX,
                    "Ad Group": primary_ag,
                    "Ad Group Status": "Paused",
                    "Max CPC": "[APPROVAL_MAX_CPC]",
                    "Comment": f"Primary Exact+Phrase AG — {ROLE_LABEL[role]}",
                }
            )
            rows.append(r)

            final = f"{base_url}?role={role}"

            # Keywords Exact
            for kw in EXACT[role]:
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Keyword",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Tracking template": TRACK,
                        "Final URL suffix": SUFFIX,
                        "Ad Group": primary_ag,
                        "Ad Group Status": "Paused",
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Keyword": kw,
                        "Criterion Type": "Exact",
                        "Keyword Status": "Paused",
                    }
                )
                rows.append(r)

            # Keywords Phrase
            for kw in PHRASE[role]:
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Keyword",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Tracking template": TRACK,
                        "Final URL suffix": SUFFIX,
                        "Ad Group": primary_ag,
                        "Ad Group Status": "Paused",
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Keyword": kw,
                        "Criterion Type": "Phrase",
                        "Keyword Status": "Paused",
                    }
                )
                rows.append(r)

            # RSAs (2 angles)
            for suffix, hs, ds, p1, p2 in rsa_pair(role, mkt):
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Ad",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Tracking template": TRACK,
                        "Final URL suffix": SUFFIX,
                        "Ad Group": primary_ag,
                        "Ad Group Status": "Paused",
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Ad Status": "Paused",
                        "Ad type": "Responsive search ad",
                        "Final URL": final,
                        "Path 1": p1,
                        "Path 2": p2,
                        "Comment": f"RSA angle {suffix}; full 15/4 fill; no invented pricing",
                    }
                )
                for i, h in enumerate(hs, 1):
                    r[f"Headline {i}"] = h
                for i, d in enumerate(ds, 1):
                    r[f"Description {i}"] = d
                rows.append(r)

            # Light city AG — administration only
            if role == "administration":
                city_ag = "Admin_City_Test"
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Ad group",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Tracking template": TRACK,
                        "Final URL suffix": SUFFIX,
                        "Ad Group": city_ag,
                        "Ad Group Status": "Paused",
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Comment": "LIGHT city Phrase + location-insertion RSA — document-only test",
                    }
                )
                rows.append(r)
                city_kws = CITY_PHRASE_US if mkt == "US" else CITY_PHRASE_AU
                for kw in city_kws:
                    r = blank_row()
                    r.update(
                        {
                            "Row Type": "Keyword",
                            "Campaign": cname,
                            "Campaign Type": "Search",
                            "Campaign Status": "Paused",
                            "Budget type": "Daily",
                            "Bid Strategy Type": "Maximize Clicks",
                            "Networks": "Google Search",
                            "Languages": "en",
                            "Location options": "Presence",
                            "Tracking template": TRACK,
                            "Final URL suffix": SUFFIX,
                            "Ad Group": city_ag,
                            "Ad Group Status": "Paused",
                            "Max CPC": "[APPROVAL_MAX_CPC]",
                            "Keyword": kw,
                            "Criterion Type": "Phrase",
                            "Keyword Status": "Paused",
                        }
                    )
                    rows.append(r)
                hs, ds, p1, p2 = city_rsa(mkt)
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Ad",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Tracking template": TRACK,
                        "Final URL suffix": SUFFIX,
                        "Ad Group": city_ag,
                        "Ad Group Status": "Paused",
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Ad Status": "Paused",
                        "Ad type": "Responsive search ad",
                        "Final URL": final,
                        "Path 1": p1,
                        "Path 2": p2,
                        "Comment": "Location insertion test RSA; full 15/4",
                    }
                )
                for i, h in enumerate(hs, 1):
                    r[f"Headline {i}"] = h
                for i, d in enumerate(ds, 1):
                    r[f"Description {i}"] = d
                rows.append(r)

            # Campaign negatives
            for neg in NEGATIVES:
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Campaign negative keyword",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Tracking template": TRACK,
                        "Final URL suffix": SUFFIX,
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Keyword": neg,
                        "Criterion Type": "Broad",
                        "Negative": "True",
                        "Comment": "Curated Stage1 negatives — not wholesale historical import",
                    }
                )
                rows.append(r)

            # Callouts (campaign level)
            for callout in [
                "Vetted Filipino Talent",
                "Employer Hiring Only",
                "Recruit Vet & Manage",
                "Dedicated Remote Staff",
                "Interview Your Shortlist",
                "Not a Gig Marketplace",
            ]:
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Callout",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Callout text": callout,
                        "Comment": "Employer-focused callout",
                    }
                )
                rows.append(r)

            # Structured snippet
            r = blank_row()
            r.update(
                {
                    "Row Type": "Structured snippet",
                    "Campaign": cname,
                    "Campaign Type": "Search",
                    "Campaign Status": "Paused",
                    "Budget type": "Daily",
                    "Bid Strategy Type": "Maximize Clicks",
                    "Networks": "Google Search",
                    "Languages": "en",
                    "Location options": "Presence",
                    "Header": "Types",
                    "Snippet Values": (
                        "Virtual Assistants;Bookkeepers;Accountants;"
                        "Social Media Managers;Customer Support;Recruiters"
                    ),
                    "Comment": "Employer role types — no WP sprawl",
                }
            )
            rows.append(r)

            # Sitelinks → microsite only (no WP)
            sitelinks = [
                (
                    "Request a Consult",
                    "Employer hiring path",
                    "Talk with our team",
                    f"{base_url}#gate",
                ),
                (
                    "How Hiring Works",
                    "Recruit, vet, shortlist",
                    "You interview talent",
                    base_url,
                ),
                (
                    f"Hire {ROLE_LABEL[role]}",
                    "Philippines remote staff",
                    "Role-focused staffing",
                    final,
                ),
                (
                    f"{mkt} Employer Page",
                    "Dedicated landing page",
                    "Not WordPress homepage",
                    base_url,
                ),
            ]
            for link_text, d1, d2, url in sitelinks:
                r = blank_row()
                r.update(
                    {
                        "Row Type": "Sitelink",
                        "Campaign": cname,
                        "Campaign Type": "Search",
                        "Campaign Status": "Paused",
                        "Budget type": "Daily",
                        "Bid Strategy Type": "Maximize Clicks",
                        "Networks": "Google Search",
                        "Languages": "en",
                        "Location options": "Presence",
                        "Final URL": url,
                        "Link Text": link_text,
                        "Description Line 1": d1,
                        "Description Line 2": d2,
                        "Comment": "Microsite sitelink only — no WP",
                    }
                )
                rows.append(r)

    return rows


def qa(rows: list[dict[str, str]]) -> None:
    kinds = Counter(r["Row Type"] for r in rows)
    print("Row types:", dict(kinds))
    camps = sorted({r["Campaign"] for r in rows if r["Campaign"]})
    print("Campaigns:", len(camps))
    for c in camps:
        print(" ", c)

    # RSA completeness
    ads = [r for r in rows if r["Row Type"] == "Ad"]
    for r in ads:
        hs = [r[f"Headline {i}"] for i in range(1, 16)]
        ds = [r[f"Description {i}"] for i in range(1, 5)]
        if any(not h for h in hs) or any(not d for d in ds):
            raise SystemExit(f"BLANK RSA SLOT: {r['Campaign']} / {r['Ad Group']}")
        validate_rsa(hs, ds, f"{r['Campaign']}/{r['Ad Group']}")

    # No empty role shells: every ROLE campaign must have keywords + ads
    for c in camps:
        kws = [
            r
            for r in rows
            if r["Campaign"] == c and r["Row Type"] == "Keyword" and r["Negative"] != "True"
        ]
        ads_c = [r for r in rows if r["Campaign"] == c and r["Row Type"] == "Ad"]
        if not kws or not ads_c:
            raise SystemExit(f"EMPTY SHELL: {c} kws={len(kws)} ads={len(ads_c)}")

    # Forbidden claim patterns
    blob = "\n".join(
        " ".join(r[f"Headline {i}"] for i in range(1, 16))
        + " "
        + " ".join(r[f"Description {i}"] for i in range(1, 5))
        for r in ads
    )
    bad = re.compile(
        r"top\s*1%|\$\d+\s*/?\s*hr|80%\s*|save\s*\d+%|guaranteed|cheapest|\$7|\$8|\$10",
        re.I,
    )
    if bad.search(blob):
        raise SystemExit(f"Forbidden claim in RSA: {bad.search(blob).group(0)}")

    # Brand must not be present
    if any("BRAND" in c for c in camps):
        raise SystemExit("Brand campaign found — should be deferred/absent")

    # Match types
    mt = Counter(
        r["Criterion Type"]
        for r in rows
        if r["Row Type"] == "Keyword" and r["Negative"] != "True"
    )
    print("Positive match types:", dict(mt))
    if mt.get("Broad"):
        raise SystemExit("Positive Broad keywords not allowed")

    # Negatives must not include hire/hiring alone
    negs = {
        r["Keyword"].lower()
        for r in rows
        if r["Row Type"] == "Campaign negative keyword"
    }
    if "hire" in negs or "hiring" in negs:
        raise SystemExit("hire/hiring must not be campaign negatives")

    print("QA OK — RSA ads:", len(ads), "positive KWs:", sum(mt.values()))


def main() -> None:
    rows = build()
    qa(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    MIRROR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, MIRROR)
    print(f"Wrote {OUT} ({len(rows)} rows)")
    print(f"Mirrored {MIRROR}")


if __name__ == "__main__":
    main()
