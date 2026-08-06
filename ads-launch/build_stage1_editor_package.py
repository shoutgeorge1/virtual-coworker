#!/usr/bin/env python3
"""Build Stage 1 Google Ads Editor import — role Search only (brand deferred).

v4 (2026-08-05 evening): fold real ~2y Editor search-term + campaign metrics from
audit-data/performance/* into keywords + negatives. Keep high-intent employer
queries; kill job-seeker / Spanish-LATAM / WFH fluff / review-pricing / DSA
catch-alls. Do not clone DSA or thin PM_*_RSA farms. No Ads API. All Paused.

Outputs:
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
LP_VERSION = "stage1-v4"

SUFFIX = (
    "utm_source=google&utm_medium=cpc&utm_campaign={_campaign}"
    f"&utm_content={{_adgroup}}&utm_term={{keyword}}&lp_version={LP_VERSION}"
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

# Campaign-level Broad negatives — curated from strategy + real ~2y ST waste.
# Never bare hire/hiring. Do NOT blanket-neg "how to" (blocks converting
# "how to hire a virtual assistant"); use specific DIY how-tos instead.
NEGATIVES = [
    # Job seeker (ST: VA jobs $723, salary $270+, AU jobs $426, PH salary $231)
    "job",
    "jobs",
    "salary",
    "salaries",
    "wage",
    "wages",
    "pay rate",
    "hourly rate",
    "career",
    "careers",
    "hiring me",
    "i need a job",
    "looking for a job",
    "resume",
    "cv",
    "apply",
    "application",
    "employment",
    "intern",
    "internship",
    "job description",
    "job listings",
    "job opening",
    "job openings",
    "vacancies",
    "vacancy",
    "work from home job",
    "wfh job",
    "remote job",
    "remote jobs",
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
    "onlinejobs ph",
    "onlinejobsph",
    "online jobs ph",
    "online jobs philippines",
    "ph jobs online",
    "virtual assistant jobs",
    "virtual assistant job",
    "virtual assistant careers",
    "virtual assistant salary",
    "virtual assistant philippines salary",
    "va philippines salary",
    "filipino virtual assistant salary",
    "apply as virtual assistant",
    "va jobs",
    "va job",
    "va salary",
    "va philippines jobs",
    "how much do virtual assistants make",
    "bookkeeper philippines salary",
    # WFH fluff (ST: work from home $448; receptionist/WFH variants)
    "work from home",
    "wfh",
    "work from home receptionist",
    "work from home start today",
    "online work from home",
    "remote work from home",
    "workathome",
    # Info / DIY — keep "how to hire" open; kill become/make-money/get-job
    "what is",
    "what is a virtual assistant",
    "how to become",
    "how to become a virtual assistant",
    "how to make money",
    "how to get a job",
    "how to start",
    "tutorial",
    "course",
    "courses",
    "training",
    "certification",
    "certificate",
    "template",
    "examples",
    "example",
    "definition",
    "meaning",
    "diy",
    "for beginners",
    "skills required",
    # Review / pricing research (ST: reviews + cost clusters)
    "reviews",
    "review",
    "pricing",
    "virtual assistant cost",
    "virtual assistant philippines cost",
    "cost of a virtual assistant",
    "cost of virtual assistant philippines",
    "how much does a virtual assistant cost",
    "how much is a virtual assistant",
    "how much does a va cost",
    "how much do virtual assistants cost",
    "top 10 virtual assistant companies",
    "top 10",
    "bruntwork reviews",
    "brunt work reviews",
    "remote coworker reviews",
    "onlinejobs ph reviews",
    "onlinejobs ph pricing",
    "myoutdesk reviews",
    "athena assistant pricing",
    "athena ea reviews",
    "virtualstaff ph reviews",
    "virtual assistant reviews",
    # DSA / marketplace catch-alls (ST: online ph $1.9k, onlinejobs*, wing, hellorache)
    "online ph",
    "onlineph",
    "wing assistant",
    "hello rache",
    "hellorache",
    "hello rache virtual assistant",
    "virtual world assistants",
    "virtual staff finder",
    "doer virtual assistant",
    "evirtualassistants",
    "virtuestaff",
    "the va hub",
    "pineapple virtual assistant hub",
    # Junk / tire-kick
    "free",
    "free virtual assistant",
    "cheap",
    "cheapest",
    "torrent",
    "reddit",
    "youtube",
    "pdf",
    "near me",
    # Platforms / marketplace bleed (protect intent; not conquest)
    "upwork",
    "upwork virtual assistant",
    "fiverr",
    "freelancer.com",
    "freelancer",
    "wishup",
    "athena",
    "boldly",
    "myoutdesk",
    "zirtual",
    "bruntwork",
    # Spanish / LATAM waste (USA ST ~$1.3k+ mostly 0-conv)
    "spanish",
    "español",
    "espanol",
    "bilingual spanish",
    "asistente virtual",
    "asistentes virtuales",
    "asistente virtual bilingue",
    "asistente virtual bilingüe",
    "trabajo asistente virtual",
    "trabajos de asistente virtual",
    "trabajo de asistente virtual",
    "asistente virtual en español",
    "asistente virtual trabajo",
    "filipina va",
    "virtual assistant colombia",
    "virtual assistant in colombia",
    "argentina virtual assistant",
    "latam virtual assistant",
    "mexico virtual assistant",
    "virtual assistant mexico",
    # Excluded verticals
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
    "graphic designer",
    "web design",
    # Misc dual-intent
    "consumer",
    "personal assistant job",
    "for students",
    "school",
    "homework",
    "us based virtual assistant",
    "diploma in digital marketing",
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

# ---------------------------------------------------------------------------
# Keywords — theme-split. Exact = employer long-tail. Phrase = discovery seeds.
# v4: promoted from real ST keepers (conv / hire-intent cost) + archaeology.
# Stripped: jobs/salary/medical/tech/spanish/cheap/DSA catch-alls/brand.
# DO NOT add bare "social media manager" / agency-only / competitor brands.
# ---------------------------------------------------------------------------

EXACT_BY_AG: dict[str, dict[str, list[str]]] = {
    "digital_marketing": {
        "Digital_Marketing_Hire_PH": [
            # ST keepers: virtual marketing assistant 6c/$2152; marketing VA 2c;
            # digital marketing VA 1c; marketing virtual assistant 4.5c
            "virtual marketing assistant",
            "marketing virtual assistant",
            "marketing virtual assistants",
            "marketing va",
            "digital marketing virtual assistant",
            "virtual assistant digital marketing",
            "hire digital marketing manager",
            "hire digital marketer philippines",
            "hire filipino digital marketing manager",
            "hire a filipino digital marketing va",
            "hire filipino digital marketing va",
            "hire digital marketing va philippines",
            "hire remote digital marketer",
            "hire remote digital marketing manager",
            "hire a filipino digital marketer",
            "filipino digital marketing manager",
            "filipino digital marketing va",
            "filipino digital marketing specialist",
            "filipino digital marketing virtual assistant",
            "digital marketing va philippines",
            "remote digital marketing manager philippines",
            "virtual digital marketing manager philippines",
            "philippines digital marketing manager",
            "digital marketing manager philippines",
            "digital marketing staff philippines",
            "hire seo virtual assistant philippines",
            "seo virtual assistant philippines",
            "hire content marketing va philippines",
            "filipino ppc virtual assistant",
            "hire email marketing va philippines",
            "dedicated digital marketing va philippines",
            "hire philippines digital marketing specialist",
            "filipino marketing virtual assistant",
            "hire offshore digital marketing va",
            "remote marketing assistant",
            "google ads specialist philippines",
            "hire seo expert philippines",
            "social media marketing va",
        ],
        "Digital_Marketing_Outsource_PH": [
            # ST: outsource/outsourcing digital marketing PH + SEO PH spend
            "outsource digital marketing philippines",
            "digital marketing outsourcing philippines",
            "digital marketing philippines",
            "digital marketer outsourcing philippines",
            "outsource digital marketing to philippines",
            "offshore digital marketing philippines",
            "offshore digital marketing manager",
            "offshore marketing staff philippines",
            "philippines digital marketing outsourcing",
            "outsource seo to philippines",
            "outsource seo philippines",
            "seo philippines",
            "philippines seo specialist",
            "outsource content marketing philippines",
            "digital marketing agency alternative philippines",
            "dedicated marketing staff philippines",
            "remote marketing team philippines",
            "outsource ppc management philippines",
            "philippines remote marketing hire",
            "outsource marketing operations philippines",
            "filipino marketing team for hire",
            "offshore digital marketing specialist",
            "outsource campaign management philippines",
            "marketing ops outsourcing philippines",
            "philippines digital marketing support staff",
            "hire outsourced digital marketer",
            "philippines digital marketing agency",
            "seo company philippines",
        ],
    },
    "social_media": {
        "Social_Media_Hire_PH": [
            # ST keepers: SMM PH 6c/$2451; filipino SMM 3c; social VA cluster
            "social media manager philippines",
            "filipino social media manager",
            "hire philippines social media manager",
            "hire social media manager philippines",
            "hire a social media manager",
            "social media manager for hire",
            "hire social media manager for small business",
            "social media virtual assistant",
            "virtual social media assistant",
            "virtual assistant social media",
            "virtual assistant social media manager",
            "social media va",
            "va for social media",
            "social media assistant",
            "social media manager virtual assistant",
            "virtual social media manager",
            "hire social media virtual assistant",
            "hire filipino social media manager",
            "hire social media va",
            "hire filipino social media va",
            "hire remote social media manager",
            "social media va philippines",
            "social media virtual assistant philippines",
            "filipino social media specialist",
            "filipino social media va",
            "philippines social media manager",
            "social media management virtual assistant",
            "social media marketing virtual assistant",
            "social media staff philippines",
            "hire instagram virtual assistant philippines",
            "hire facebook ads va philippines",
            "filipino community manager hire",
            "hire content scheduler philippines",
            "dedicated social media va philippines",
            "hire philippines social media specialist",
            "social media assistant philippines",
            "remote social media assistant philippines",
            "instagram manager philippines",
        ],
        "Social_Media_Outsource_PH": [
            # ST: social media management/outsourcing PH converting cluster
            "outsource social media philippines",
            "outsource social media management",
            "social media outsourcing",
            "outsource social media marketing philippines",
            "offshore social media manager",
            "offshore social media philippines",
            "social media management philippines",
            "social media outsourcing philippines",
            "philippines social media outsourcing",
            "philippines social media marketing",
            "social media services philippines",
            "dedicated social media staff philippines",
            "remote social media team philippines",
            "outsource community management philippines",
            "outsource content posting philippines",
            "filipino social media team for hire",
            "offshore smm specialist",
            "social media ops outsourcing philippines",
            "philippines remote smm hire",
            "outsource brand social media philippines",
            "hire outsourced social media manager",
            "social media support staff philippines",
            "offshore content and social va",
            "philippines social media management staff",
            "outsource linkedin management philippines",
        ],
    },
    "accounting": {
        "Accounting_Hire_PH": [
            # ST: philippines accountant / filipino accountant / accounting VA
            "philippines accountant",
            "filipino accountant",
            "accountant for hire philippines",
            "remote accountant philippines",
            "accounting virtual assistant",
            "virtual assistant accounting",
            "virtual assistant for accounting",
            "accounting va",
            "hire accountant philippines",
            "hire filipino accountant",
            "hire a filipino accountant",
            "hire philippines accountant",
            "hire virtual accountant philippines",
            "hire remote accountant philippines",
            "hire accounts payable philippines",
            "filipino accounting virtual assistant",
            "virtual accountant philippines",
            "accountant philippines",
            "virtual assistant accountant",
            "accounting staff philippines",
            "accounts payable philippines",
            "hire accounts receivable philippines",
            "filipino ap specialist hire",
            "hire philippines accounting assistant",
            "remote accounting assistant philippines",
            "hire filipino accounting va",
            "dedicated accountant philippines",
            "hire payroll accountant philippines",
            "filipino staff accountant hire",
            "online filipino accountant hire",
            "find filipino accountant for business",
            "online accountant philippines",
            "accountant filipino",
        ],
        "Accounting_Outsource_PH": [
            # ST: PH accounting outsourcing 1c/$466; outsource accounting PH
            "philippines accounting outsourcing",
            "philippine accounting outsourcing",
            "outsourced accounting services philippines",
            "outsource accounting philippines",
            "outsource accountant philippines",
            "outsourced accounting philippines",
            "accounting outsourcing philippines",
            "offshore accountant philippines",
            "offshore accounting philippines",
            "bpo accounting philippines",
            "accounting services philippines",
            "philippines accounting services",
            "outsource accounts payable philippines",
            "outsource bookkeeping accounting philippines",
            "remote accounting team philippines",
            "dedicated accounting staff philippines",
            "filipino accounting team for hire",
            "outsource finance ops philippines",
            "philippines remote accounting support",
            "hire outsourced accountant",
            "accounting support outsourcing philippines",
            "offshore ap ar staff philippines",
            "outsource general ledger philippines",
            "philippines accounting services for smbs",
            "outsource accounting to philippines",
            "philippines outsourcing accounting",
            "filipino finance ops outsourcing",
        ],
    },
    "bookkeeping": {
        "Bookkeeping_Hire_PH": [
            # ST keepers: philippines bookkeeper 3c/$1366; bookkeeper PH 1c/$997
            "philippines bookkeeper",
            "bookkeeper philippines",
            "bookkeeper in philippines",
            "virtual bookkeeper philippines",
            "va bookkeeper",
            "virtual assistant bookkeeper",
            "virtual assistant bookkeeping",
            "bookkeeping virtual assistant",
            "filipino virtual bookkeeper",
            "quickbooks virtual assistant",
            "virtual assistant quickbooks",
            "virtual assistant for quickbooks",
            "hire a bookkeeper",
            "hire virtual bookkeeper philippines",
            "hire bookkeeper philippines",
            "hire a filipino bookkeeper",
            "hire filipino bookkeeper",
            "hire remote bookkeeper philippines",
            "filipino bookkeeper",
            "filipino bookkeepers",
            "philippines bookkeepers",
            "remote bookkeeping philippines",
            "virtual bookkeeping philippines",
            "hire quickbooks bookkeeper philippines",
            "hire xero bookkeeper philippines",
            "filipino quickbooks virtual assistant",
            "dedicated bookkeeper philippines",
            "hire philippines bookkeeping va",
            "online filipino bookkeeper hire",
            "hire weekly bookkeeper philippines",
            "remote books assistant philippines",
            "filipino bookkeeping specialist hire",
            "hire virtual bookkeeping assistant",
            "philippines virtual bookkeeper for smbs",
            "hire offshore bookkeeping va",
            "online bookkeeper philippines",
            "bookkeeper ph",
            "quickbooks proadvisor philippines",
        ],
        "Bookkeeping_Outsource_PH": [
            # ST: bookkeeping philippines 2c; outsourcing PH clusters
            "bookkeeping philippines",
            "outsource bookkeeping philippines",
            "bookkeeping services philippines",
            "philippines bookkeeping outsourcing",
            "virtual bookkeeping services philippines",
            "offshore bookkeeper",
            "offshore bookkeeper philippines",
            "bookkeeping outsourcing philippines",
            "bookkeeper outsourcing philippines",
            "bookkeeper outsourcing",
            "outsourced bookkeeping philippines",
            "remote bookkeeping team philippines",
            "dedicated books staff philippines",
            "outsource accounts bookkeeping philippines",
            "philippines remote bookkeeping support",
            "hire outsourced bookkeeper",
            "offshore books management philippines",
            "outsource reconciliation support philippines",
            "filipino bookkeeping team for hire",
            "smb bookkeeping outsourcing philippines",
            "outsource xero bookkeeping philippines",
            "outsource quickbooks bookkeeping philippines",
            "philippines bookkeeping ops staff",
            "remote month end books philippines",
            "freelance bookkeeper philippines",
        ],
    },
    "administration": {
        # Absorbs former CORE hire_va depth (brand deferred). ST-heavy keepers.
        "Administration_Hire_PH": [
            # Core converting ST (employer) — brand/competitors excluded
            "virtual assistant",
            "virtual assistants",
            "hire virtual assistant",
            "hire a virtual assistant",
            "virtual assistant hire",
            "hire a va",
            "hire va",
            "virtual assistants for hire",
            "virtual assistant for hire",
            "va for hire",
            "looking for a virtual assistant",
            "looking for virtual assistant",
            "how to hire a virtual assistant",
            "how to hire a virtual assistant philippines",
            "filipino virtual assistant",
            "filipino virtual assistants",
            "filipino va",
            "filipino vas",
            "hire filipino virtual assistant",
            "hire a filipino virtual assistant",
            "hire filipino virtual assistants",
            "hire filipino va",
            "hire a filipino va",
            "virtual assistant philippines",
            "philippines virtual assistant",
            "virtual assistants philippines",
            "philippine virtual assistant",
            "virtual assistant in philippines",
            "virtual assistants in philippines",
            "virtual assistants in the philippines",
            "virtual assistant from the philippines",
            "hire virtual assistant from philippines",
            "hire philippines virtual assistant",
            "hire a virtual assistant philippines",
            "hire virtual assistant philippines",
            "hire va philippines",
            "va philippines",
            "philippines va",
            "va in philippines",
            "va from philippines",
            "virtual assistant services",
            "va services",
            "virtual assistant agency",
            "va agency",
            "va agency philippines",
            "virtual assistant agency philippines",
            "virtual assistant companies",
            "virtual assistant company philippines",
            "virtual assistant companies philippines",
            "virtual assistant services philippines",
            "outsource virtual assistant philippines",
            "outsourcing virtual assistant",
            "offshore virtual assistant",
            "offshore virtual assistant philippines",
            "offshore virtual assistants",
            "offshore va",
            "overseas virtual assistant",
            "virtual assistant overseas",
            "hire offshore virtual assistant",
            "hire overseas virtual assistant",
            "hire remote virtual assistant",
            "virtual assistant for business",
            "virtual assistant company",
            "dedicated virtual assistant",
            "virtual staffing company",
            "filipino virtual assistant for hire",
            "hire a va in the philippines",
            "hire a virtual assistant in the philippines",
            "hiring virtual assistant philippines",
            "hire virtual assistant ph",
            "philippines va company",
            "remote virtual assistant for business",
            "virtual assistant hiring philippines",
            "virtual assistant hiring",
            "hiring virtual assistant",
            "virtual admin assistant",
            "virtual assistance",
            "virtual assistance services",
            "virtual assistant providers",
            "find a virtual assistant",
            "philippines assistant",
            "virtual staff philippines",
            "virtual staff ph",
            "remote staff philippines",
            "where to hire virtual assistant philippines",
        ],
        "Administration_EA_PH": [
            # ST: PH EA / admin assistant / virtual office / personal assistant PH
            "philippines executive assistant",
            "executive assistant philippines",
            "virtual executive assistant philippines",
            "admin assistant philippines",
            "personal assistant philippines",
            "virtual office assistant",
            "virtual admin assistant",
            "remote general administrative assistant philippines",
            "hire filipino administrative assistant",
            "administrative assistant philippines",
            "hire virtual administrative assistant",
            "filipino executive assistant",
            "hire executive assistant philippines",
            "hire virtual executive assistant",
            "offshore executive assistant",
            "office administrator philippines",
            "hire admin assistant philippines",
            "filipino admin assistant",
            "virtual admin assistant philippines",
            "hire remote executive assistant",
            "executive virtual assistant philippines",
            "filipino virtual executive assistant",
            "hire an offshore executive assistant",
            "remote executive assistant philippines",
            "hire philippines admin support",
            "dedicated executive assistant philippines",
            "outsource executive assistant philippines",
            "virtual administrative support philippines",
            "hire filipino ea",
            "philippines remote admin hire",
            "filipino assistant",
        ],
    },
    "customer_service": {
        "Customer_Service_Hire_PH": [
            # ST: CS VA; philippines customer service; filipino CS
            "customer service virtual assistant",
            "virtual assistant customer service",
            "philippines customer service",
            "customer service philippines",
            "customer support philippines",
            "filipino customer service",
            "virtual customer service representative",
            "philippine customer service",
            "hire customer service virtual assistant",
            "hire filipino customer service",
            "hire filipino customer service representative",
            "hire philippines customer service",
            "hire customer support philippines",
            "hire remote customer service philippines",
            "filipino customer service va",
            "customer service representative philippines",
            "virtual customer service philippines",
            "virtual customer support philippines",
            "customer care assistant philippines",
            "customer service assistant philippines",
            "virtual customer service agent",
            "customer support staff philippines",
            "filipino customer support hire",
            "hire chat support philippines",
            "hire email support va philippines",
            "dedicated cs representative philippines",
            "hire philippines support specialist",
            "remote customer support agent philippines",
            "filipino call support staff hire",
            "hire bilingual english support philippines",
            "customer service staff philippines hire",
            "customer service hire",
            "live chat support agent philippines",
        ],
        "Customer_Service_Outsource_PH": [
            # ST: outsource customer service (+ PH outsourcing)
            "outsource customer service",
            "outsource customer service philippines",
            "customer support outsourcing philippines",
            "offshore customer service philippines",
            "customer service outsourcing philippines",
            "outsource customer support philippines",
            "philippines customer service outsourcing",
            "customer service agency philippines",
            "remote support team philippines",
            "dedicated support staff philippines",
            "outsource chat support philippines",
            "outsource helpdesk philippines",
            "filipino support team for hire",
            "offshore customer care philippines",
            "hire outsourced customer service",
            "smb customer support outsourcing ph",
            "outsource inbox support philippines",
            "customer care outsourcing philippines",
            "offshore support agent philippines",
            "outsource ticket support philippines",
            "philippines english support outsourcing",
            "remote customer care team philippines",
            "support ops staffing philippines",
            "outsource ecommerce customer service",
            "outsource customer service for small business",
        ],
    },
    "hr": {
        "Human_Resources_Hire_PH": [
            # ST thin but real: human resources VA / hr virtual assistants
            "human resources virtual assistant",
            "hr virtual assistants",
            "virtual assistant hr",
            "hr virtual assistant",
            "hire virtual hr assistant",
            "hire hr assistant philippines",
            "hire filipino hr assistant",
            "hire human resources assistant philippines",
            "hire hr coordinator philippines",
            "hire remote hr staff",
            "hire payroll assistant philippines",
            "filipino virtual hr assistant",
            "virtual hr assistant philippines",
            "filipino hr assistant",
            "hr virtual assistant philippines",
            "human resources assistant philippines",
            "virtual human resources assistant",
            "filipino human resources assistant",
            "remote hr assistant philippines",
            "virtual payroll assistant philippines",
            "hire people ops assistant philippines",
            "dedicated hr va philippines",
            "hire philippines hr admin",
            "filipino hr coordinator hire",
            "hire benefits admin philippines",
            "remote people ops va philippines",
            "hire onboarding assistant philippines",
            "philippines hr support hire",
            "hire virtual people ops assistant",
            "filipino payroll support hire",
        ],
        "Human_Resources_Outsource_PH": [
            "outsource hr philippines",
            "outsource human resources philippines",
            "offshore hr assistant",
            "hr staffing philippines",
            "philippines hr outsourcing",
            "outsource hr administration philippines",
            "remote hr team philippines",
            "dedicated hr staff philippines",
            "outsource payroll admin philippines",
            "offshore people ops philippines",
            "filipino hr team for hire",
            "hire outsourced hr assistant",
            "hr ops outsourcing philippines",
            "philippines remote hr support",
            "outsource employee onboarding philippines",
            "outsource hr documentation philippines",
            "offshore hr coordination philippines",
            "smb hr admin outsourcing philippines",
            "people ops staffing philippines",
            "remote hr coordinator philippines",
            "outsource leave admin philippines",
            "philippines human resources support staff",
        ],
    },
    "recruitment": {
        # ST nearly empty for employer recruitment VA — keep curated long-tail,
        # do not invent DSA/generic winners.
        "Recruitment_Hire_PH": [
            "hire virtual recruitment assistant",
            "hire filipino recruitment assistant",
            "hire recruitment assistant philippines",
            "hire a recruitment assistant",
            "hire recruiting assistant philippines",
            "hire talent acquisition assistant philippines",
            "virtual recruitment assistant philippines",
            "recruitment assistant philippines",
            "filipino recruitment assistant",
            "remote recruitment assistant philippines",
            "recruitment virtual assistant",
            "virtual assistant recruitment",
            "philippines recruitment assistant",
            "virtual recruiting assistant philippines",
            "filipino recruitment staff",
            "recruitment coordinator philippines",
            "talent sourcing assistant philippines",
            "dedicated recruiting va philippines",
            "hire philippines sourcing assistant",
            "filipino talent acquisition va",
            "hire screening assistant philippines",
            "remote recruiting coordinator philippines",
            "hire recruiter assistant philippines",
            "philippines ta assistant hire",
            "hire virtual recruiting ops assistant",
            "filipino recruiting coordinator hire",
            "hire candidate coordination philippines",
        ],
        "Recruitment_Outsource_PH": [
            "offshore recruitment philippines",
            "outsource recruitment support philippines",
            "offshore recruitment assistant",
            "recruitment assistant services",
            "philippines recruiting outsourcing",
            "outsource talent sourcing philippines",
            "remote recruiting team philippines",
            "dedicated recruiting staff philippines",
            "outsource candidate screening philippines",
            "offshore ta support philippines",
            "filipino recruiting team for hire",
            "hire outsourced recruitment assistant",
            "recruiting ops outsourcing philippines",
            "philippines remote recruiting support",
            "outsource interview scheduling philippines",
            "offshore sourcer philippines",
            "smb recruiting support outsourcing ph",
            "talent ops staffing philippines",
            "outsource recruiter coordination philippines",
            "philippines recruitment process support",
            "remote sourcing team philippines",
            "outsource ats admin philippines",
        ],
    },
    "sales": {
        "Sales_Hire_PH": [
            # ST keepers: sales VA 2c; VA for sales 3c; lead gen VA 5.3c; appt setter
            "sales virtual assistant",
            "sales virtual assistants",
            "sales va",
            "virtual assistant for sales",
            "virtual assistant sales",
            "virtual sales assistant",
            "hire virtual sales assistant",
            "lead generation virtual assistant",
            "virtual assistant lead generation",
            "virtual assistant for lead generation",
            "lead gen va",
            "virtual assistant appointment setter",
            "appointment setter philippines",
            "va appointment setter",
            "virtual appointment setter",
            "virtual assistant cold calling",
            "hire filipino lead generation specialist",
            "hire sales assistant philippines",
            "hire appointment setter philippines",
            "hire filipino appointment setter",
            "hire lead generation va philippines",
            "filipino lead generation specialist",
            "lead generation specialist philippines",
            "filipino lead generation va",
            "filipino lead generation virtual assistant",
            "philippines lead generation specialist",
            "filipino sales assistant",
            "virtual sales assistant philippines",
            "filipino appointment setter",
            "remote lead generation philippines",
            "virtual lead generation philippines",
            "hire outbound sales va philippines",
            "dedicated sales va philippines",
            "hire philippines sdr assistant",
            "filipino pipeline support hire",
            "hire lead research va philippines",
            "remote appointment setter philippines",
            "hire b2b lead gen va philippines",
            "lead generation philippines",
        ],
        "Sales_Outsource_PH": [
            "outsource lead generation philippines",
            "lead generation services philippines",
            "lead generation agency philippines",
            "offshore sales assistant philippines",
            "philippines lead generation outsourcing",
            "outsource appointment setting philippines",
            "remote sales support philippines",
            "dedicated lead gen staff philippines",
            "offshore lead generation philippines",
            "filipino sales team for hire",
            "hire outsourced appointment setter",
            "outsource prospecting philippines",
            "sales ops outsourcing philippines",
            "philippines remote sdr support",
            "outsource list building philippines",
            "offshore bdr support philippines",
            "smb lead gen outsourcing philippines",
            "pipeline support staffing philippines",
            "outsource cold outreach support ph",
            "philippines sales development staffing",
            "remote outbound team philippines",
            "outsource crm sales admin philippines",
            "sales representative hiring philippines",
        ],
    },
}

PHRASE_BY_AG: dict[str, dict[str, list[str]]] = {
    "digital_marketing": {
        "Digital_Marketing_Hire_PH": [
            "hire filipino digital marketing",
            "hire digital marketing va",
            "virtual marketing assistant",
            "marketing virtual assistant",
            "digital marketing virtual assistant",
            "hire remote digital marketer philippines",
            "filipino seo virtual assistant",
            "hire philippines marketing va",
            "dedicated digital marketing hire",
            "seo virtual assistant philippines",
            "hire digital marketing manager philippines",
        ],
        "Digital_Marketing_Outsource_PH": [
            "outsource digital marketing philippines",
            "digital marketing outsourcing philippines",
            "offshore digital marketing",
            "outsource marketing to philippines",
            "philippines marketing staff",
            "offshore marketing team",
            "outsource campaign management",
            "outsource seo philippines",
            "philippines digital marketing staff",
        ],
    },
    "social_media": {
        "Social_Media_Hire_PH": [
            "hire social media virtual assistant",
            "hire filipino social media",
            "social media manager philippines",
            "filipino social media manager",
            "social media va philippines",
            "hire remote social media manager",
            "social media virtual assistant",
            "hire social media specialist philippines",
            "va for social media",
            "hire philippines social media manager",
            "virtual social media assistant",
        ],
        "Social_Media_Outsource_PH": [
            "outsource social media philippines",
            "outsource social media management",
            "offshore social media manager",
            "social media outsourcing philippines",
            "philippines social media staff",
            "offshore smm team",
            "outsource community management",
            "social media management philippines",
            "philippines social media marketing",
        ],
    },
    "accounting": {
        "Accounting_Hire_PH": [
            "hire accountant philippines",
            "hire filipino accountant",
            "virtual accountant philippines",
            "filipino accounting virtual assistant",
            "hire accounts payable philippines",
            "philippines accounting assistant",
            "hire remote accountant",
            "filipino staff accountant",
            "accounting virtual assistant",
            "philippines accountant for business",
        ],
        "Accounting_Outsource_PH": [
            "outsource accounting philippines",
            "accounting outsourcing philippines",
            "philippines accounting outsourcing",
            "offshore accountant philippines",
            "outsource accounts payable",
            "philippines accounting staff",
            "offshore finance ops",
            "outsourced accounting team",
            "bpo accounting philippines",
        ],
    },
    "bookkeeping": {
        "Bookkeeping_Hire_PH": [
            "hire virtual bookkeeper philippines",
            "hire filipino bookkeeper",
            "philippines bookkeeper",
            "bookkeeper philippines",
            "virtual bookkeeper philippines",
            "hire quickbooks bookkeeper philippines",
            "filipino bookkeeping virtual assistant",
            "hire xero bookkeeper",
            "philippines bookkeeper for hire",
            "remote bookkeeper philippines",
            "virtual assistant bookkeeping",
            "va bookkeeper",
        ],
        "Bookkeeping_Outsource_PH": [
            "outsource bookkeeping philippines",
            "bookkeeping outsourcing philippines",
            "bookkeeping philippines",
            "offshore bookkeeper philippines",
            "outsource quickbooks bookkeeping",
            "philippines bookkeeping staff",
            "offshore books team",
            "outsourced bookkeeping services",
        ],
    },
    "administration": {
        "Administration_Hire_PH": [
            "hire virtual assistant philippines",
            "hire filipino virtual assistant",
            "hire filipino va",
            "hire a virtual assistant",
            "offshore virtual assistant",
            "offshore va",
            "virtual assistant for business",
            "hire va philippines",
            "filipino virtual assistant company",
            "dedicated virtual assistant philippines",
            "philippines virtual staffing",
            "hire remote filipino assistant",
            "how to hire a virtual assistant",
            "virtual assistant services philippines",
            "va agency philippines",
            "looking for a virtual assistant",
        ],
        "Administration_EA_PH": [
            "hire executive assistant philippines",
            "filipino executive assistant",
            "hire virtual executive assistant",
            "offshore executive assistant",
            "virtual administrative assistant philippines",
            "hire filipino admin assistant",
            "philippines executive assistant hire",
            "remote executive assistant philippines",
            "admin assistant philippines",
            "virtual admin assistant",
        ],
    },
    "customer_service": {
        "Customer_Service_Hire_PH": [
            "hire customer service virtual assistant",
            "hire filipino customer service",
            "customer service philippines hire",
            "customer service virtual assistant",
            "filipino customer support",
            "hire chat support philippines",
            "virtual customer service philippines",
            "hire remote customer support",
            "philippines customer service staff",
            "philippines customer service",
        ],
        "Customer_Service_Outsource_PH": [
            "outsource customer service philippines",
            "outsource customer service",
            "customer support outsourcing philippines",
            "offshore customer service",
            "outsource chat support",
            "philippines support team",
            "offshore customer care",
            "outsourced helpdesk philippines",
            "philippines customer service outsourcing",
        ],
    },
    "hr": {
        "Human_Resources_Hire_PH": [
            "hire virtual hr assistant",
            "hire filipino hr assistant",
            "human resources virtual assistant",
            "virtual hr assistant philippines",
            "hire hr coordinator philippines",
            "filipino human resources assistant",
            "hire payroll assistant philippines",
            "remote hr assistant philippines",
            "philippines people ops hire",
            "hr virtual assistant",
        ],
        "Human_Resources_Outsource_PH": [
            "outsource hr philippines",
            "outsource human resources philippines",
            "offshore hr assistant",
            "hr outsourcing philippines",
            "philippines hr staff",
            "offshore people ops",
            "outsource payroll admin",
        ],
    },
    "recruitment": {
        "Recruitment_Hire_PH": [
            "hire virtual recruitment assistant",
            "hire filipino recruitment assistant",
            "recruitment assistant philippines",
            "hire recruiting assistant philippines",
            "filipino talent acquisition assistant",
            "hire screening assistant philippines",
            "virtual recruiting assistant",
            "philippines recruitment coordinator",
            "recruitment virtual assistant",
        ],
        "Recruitment_Outsource_PH": [
            "offshore recruitment philippines",
            "outsource recruitment support",
            "outsource talent sourcing philippines",
            "philippines recruiting staff",
            "offshore recruiting assistant",
            "outsource candidate screening",
            "recruiting ops outsourcing",
        ],
    },
    "sales": {
        "Sales_Hire_PH": [
            "hire filipino lead generation specialist",
            "hire appointment setter philippines",
            "sales virtual assistant",
            "virtual assistant for sales",
            "lead generation virtual assistant",
            "virtual sales assistant philippines",
            "hire lead generation va",
            "filipino appointment setter",
            "hire sales assistant philippines",
            "philippines lead generation specialist",
            "remote appointment setter philippines",
            "virtual assistant appointment setter",
        ],
        "Sales_Outsource_PH": [
            "outsource lead generation philippines",
            "lead generation outsourcing philippines",
            "offshore sales assistant",
            "outsource appointment setting",
            "philippines lead gen staff",
            "offshore sdr support",
            "outsource prospecting philippines",
            "lead generation philippines",
        ],
    },
}

CITY_PHRASE_US = [
    "hire virtual assistant new york",
    "hire virtual assistant los angeles",
    "hire virtual assistant chicago",
    "hire filipino va texas",
    "hire virtual assistant florida",
    "hire virtual assistant california",
    "hire filipino va miami",
]
CITY_PHRASE_AU = [
    "hire virtual assistant sydney",
    "hire virtual assistant melbourne",
    "hire virtual assistant brisbane",
    "hire filipino va australia",
    "hire virtual assistant perth",
    "hire virtual assistant adelaide",
    "hire filipino va canberra",
]


def _len_ok(s: str, max_len: int) -> bool:
    m = re.fullmatch(r"\{(?:KeyWord|KEYWORD|LOCATION\([^)]+\)):(.+)\}", s)
    if m:
        return len(m.group(1)) <= max_len
    return len(s) <= max_len


def validate_rsa(headlines: list[str], descs: list[str], where: str) -> None:
    assert len(headlines) == 15, f"{where}: need 15 headlines, got {len(headlines)}"
    assert len(descs) == 4, f"{where}: need 4 descriptions, got {len(descs)}"
    assert all(h.strip() for h in headlines), f"{where}: blank headline"
    assert all(d.strip() for d in descs), f"{where}: blank description"
    assert len(set(headlines)) == 15, f"{where}: duplicate headlines: {headlines}"
    assert len(set(descs)) == 4, f"{where}: duplicate descriptions"
    for i, h in enumerate(headlines, 1):
        if not _len_ok(h, HL_MAX):
            raw = re.fullmatch(r"\{(?:KeyWord|KEYWORD|LOCATION\([^)]+\)):(.+)\}", h)
            n = len(raw.group(1)) if raw else len(h)
            raise ValueError(f"{where} H{i} too long ({n}): {h!r}")
    for i, d in enumerate(descs, 1):
        if len(d) > DESC_MAX:
            raise ValueError(f"{where} D{i} too long ({len(d)}): {d!r}")


def market_bits(mkt: str) -> dict[str, str]:
    if mkt == "US":
        return {
            "tag": "US",
            "adj": "US",
            "full": "US",
            "business": "US business",
            "employers": "US employers",
            "teams": "US teams",
            "sme": "US SMBs",
            "org": "organization",
            "specialize": "specialize",
            "labor": "labor",
        }
    return {
        "tag": "AU",
        "adj": "Australian",
        "full": "Australian",
        "business": "Australian business",
        "employers": "Australian employers",
        "teams": "Australian teams",
        "sme": "Australian SMEs",
        "org": "organisation",
        "specialize": "specialise",
        "labor": "labour",
    }


# RSA catalog: role -> ag -> angle -> (headlines_fn, descs_fn, path1, path2)
# Built as callables so US/AU language differs beyond a country token swap.


def _rsa_catalog() -> dict:
    """Return role -> ag_name -> list of (suffix, hl_fn, desc_fn, p1, p2)."""

    def H(*hs: str) -> list[str]:
        return list(hs)

    def D(*ds: str) -> list[str]:
        return list(ds)

    cat: dict = {}

    # ---- digital marketing ----
    cat["digital_marketing"] = {
        "Digital_Marketing_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Digital Marketing VA",
                    "Filipino Marketing Manager",
                    "Philippines Marketing Hire",
                    f"{m['tag']} Marketing Staffing",
                    "Vetted Marketing Shortlist",
                    "You Interview Finalists",
                    "Dedicated Not Freelance",
                    "SEO & Content VA Hire",
                    "Remote Campaign Manager",
                    "Employer Consult Path",
                    "Marketing Ops Assistant",
                    "Staffing Partner Model",
                    f"Built for {m['sme']}",
                    "Ongoing Marketing Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire a dedicated Filipino digital marketing VA through a staffing partner.",
                    "We recruit and vet; you interview the shortlist before placement support.",
                    f"For {m['employers']} who need ongoing remote marketing capacity.",
                    "Role-focused marketing hires — not gig-marketplace task work.",
                ),
                "marketing",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Marketing VA}",
                    "PPC & SEO Support Hire",
                    "Content Ops From PH",
                    "Email Marketing VA PH",
                    "Filipino Growth Marketer",
                    "Campaign Reporting VA",
                    "Scale Marketing Bandwidth",
                    f"{m['adj']} Teams Hiring Now",
                    "Philippines Marketing Talent",
                    "Dedicated Channel Support",
                    "Interview-Ready Shortlist",
                    "Remote Marketing Specialist",
                    "Partner-Managed Placement",
                    "No Marketplace Guesswork",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill digital marketing roles with vetted Philippines specialists.",
                    f"Support campaigns, content ops, and reporting for your {m['business']}.",
                    "Staffing partner workflow: shortlist, interview, then dedicated hire support.",
                    f"We {m['specialize']} in employer-intent remote marketing hires.",
                ),
                "digital",
                "va",
            ),
        ],
        "Digital_Marketing_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Marketing to PH",
                    "Offshore Marketing Staff",
                    "Philippines Marketing Team",
                    f"{m['tag']} Outsourcing Partner",
                    "Dedicated Marketing Seat",
                    "Not a Freelance Bench",
                    "Vetted Offshore Marketers",
                    "Campaign Ops Outsourcing",
                    "Remote Marketing Capacity",
                    "Employer-Only Path",
                    "Marketing Staff Placement",
                    "Clear Outsourcing Process",
                    f"For {m['sme']}",
                    "Ongoing Not Project-Only",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource digital marketing support to dedicated Philippines staff.",
                    "A staffing partner places ongoing capacity — you keep interview control.",
                    f"Designed for {m['employers']} scaling marketing without local payroll drag.",
                    "Offshore marketing ops with recruit, vet, and manage support.",
                ),
                "outsource",
                "mkt",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Digital Marketing Ops",
                    "Outsource SEO Support",
                    "Outsource PPC Ops PH",
                    "Content Engine Staffing",
                    "Marketing Team Philippines",
                    "Scale Without Headcount",
                    "Dedicated Channel Owners",
                    f"Fit for {m['adj']} Brands",
                    "Remote Marketing Bench",
                    "Vetted Specialist Seats",
                    "Outsource Reporting Ops",
                    "Philippines Growth Support",
                    "Partner-Led Outsourcing",
                    "Interview Before Placement",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines marketing capacity for SEO, content, and paid support.",
                    "Dedicated seats beat rotating freelancers for campaign continuity.",
                    f"Ask about an outsourcing path tailored to your {m['org']}.",
                    f"Built for {m['full']} businesses that want accountable remote marketers.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- social media ----
    cat["social_media"] = {
        "Social_Media_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Social Media VA",
                    "Filipino SMM for Hire",
                    "Social Manager Philippines",
                    f"{m['tag']} Social Staffing",
                    "Vetted SMM Shortlist",
                    "Interview Before You Hire",
                    "Dedicated Social Seat",
                    "Community Manager Hire",
                    "Content Scheduler VA",
                    "Employer Hiring Path",
                    "Remote SMM Specialist",
                    "Not Gig Marketplace",
                    f"Made for {m['sme']}",
                    "Ongoing Social Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire a dedicated Filipino social media manager through a staffing partner.",
                    "Shortlist is interview-ready; we handle recruiting, vetting, and support.",
                    f"For {m['employers']} who need reliable day-to-day social capacity.",
                    "Ongoing SMM hires — not one-off freelance posting gigs.",
                ),
                "social",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Social VA}",
                    "Instagram & FB VA Hire",
                    "LinkedIn Content Support",
                    "Filipino Community Manager",
                    "Brand Social Ops Hire",
                    "Posting & Engagement VA",
                    "Scale Social Bandwidth",
                    f"{m['adj']} Brands Hiring",
                    "Philippines SMM Talent",
                    "Dedicated Channel VA",
                    "Social Calendar Owner",
                    "Partner-Managed Hire",
                    "Remote Social Specialist",
                    "Clear Employer Process",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill social media roles with vetted Philippines specialists.",
                    "Coverage for scheduling, community replies, and content workflows.",
                    f"Staffing support for {m['business']} social channels that need consistency.",
                    f"We {m['specialize']} in employer-intent remote SMM hires.",
                ),
                "social",
                "va",
            ),
        ],
        "Social_Media_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Social Media",
                    "Offshore SMM Philippines",
                    "Social Ops Outsourcing",
                    f"{m['tag']} Social Partner",
                    "Dedicated SMM Seat",
                    "Not Freelance Rotation",
                    "Vetted Social Staff",
                    "Community Ops Offshore",
                    "Remote Social Capacity",
                    "Employer-Only Intake",
                    "SMM Staff Placement",
                    "Predictable Social Coverage",
                    f"For {m['sme']}",
                    "Ongoing Channel Support",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource social media management to dedicated Philippines staff.",
                    "Keep brand voice control while we recruit, vet, and support the seat.",
                    f"Built for {m['employers']} who want accountable offshore SMM coverage.",
                    "Partner-led outsourcing — interview finalists before placement.",
                ),
                "outsource",
                "smm",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Social Media Team",
                    "Outsource Content Posting",
                    "Outsource Community Ops",
                    "Brand Social Staffing",
                    "Philippines SMM Bench",
                    "Scale Social Without Hire",
                    "Dedicated Content Seats",
                    f"Fit for {m['adj']} Brands",
                    "Remote Engagement Support",
                    "Vetted Channel Managers",
                    "Outsource Social Calendar",
                    "Offshore Brand Voice Ops",
                    "Partner-Led SMM Ops",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines social capacity for posting, engagement, and content ops.",
                    "Dedicated seats keep calendars moving without freelancer churn.",
                    f"Ask about an outsourcing path for your {m['org']}'s channels.",
                    f"For {m['full']} businesses that need dependable remote social ops.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- accounting ----
    cat["accounting"] = {
        "Accounting_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Accountant Philippines",
                    "Filipino Accountant Hire",
                    "Virtual Accountant PH",
                    f"{m['tag']} Finance Staffing",
                    "Vetted Accounting Shortlist",
                    "Interview Your Finalists",
                    "Dedicated Accounting Seat",
                    "AP Specialist for Hire",
                    "Remote Staff Accountant",
                    "Employer Hiring Path",
                    "Accounting VA Philippines",
                    "Not Task Marketplace",
                    f"Built for {m['sme']}",
                    "Ongoing Finance Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire dedicated Filipino accounting staff through a staffing partner.",
                    "You interview shortlisted talent; we recruit, vet, and support placement.",
                    f"For {m['employers']} adding remote AP/AR and accounting capacity.",
                    "Dedicated accounting hires — not freelance bookkeeping gigs.",
                ),
                "accounting",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Accountant}",
                    "Accounts Payable Hire PH",
                    "AR Support Philippines",
                    "Filipino Accounting VA",
                    "Ledger Ops Assistant",
                    "Payroll Admin Support",
                    "Scale Finance Bandwidth",
                    f"{m['adj']} Finance Teams",
                    "Philippines Accounting Talent",
                    "Dedicated AP Capacity",
                    "Remote Accounting Hire",
                    "Partner-Managed Placement",
                    "Interview-Ready Accountants",
                    "Clear Employer Process",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill accounting roles with vetted Philippines specialists.",
                    "Day-to-day AP/AR workflows and accounting ops with dedicated seats.",
                    f"Staffing support shaped for your {m['business']} finance stack.",
                    f"We {m['specialize']} in employer-intent remote accounting hires.",
                ),
                "finance",
                "va",
            ),
        ],
        "Accounting_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Accounting PH",
                    "Offshore Accounting Staff",
                    "Philippines Finance Ops",
                    f"{m['tag']} Accounting Partner",
                    "Dedicated Finance Seat",
                    "Not Gig Bookkeeping",
                    "Vetted Accounting Staff",
                    "AP/AR Outsourcing PH",
                    "Remote Finance Capacity",
                    "Employer-Only Path",
                    "Accounting Staff Placement",
                    "Predictable Close Support",
                    f"For {m['sme']}",
                    "Ongoing Ledger Capacity",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource accounting support to dedicated Philippines specialists.",
                    "Staffing partner model with interview control before placement.",
                    f"Designed for {m['employers']} who need offshore finance ops capacity.",
                    "Recruit, vet, and manage support around your accounting workflows.",
                ),
                "outsource",
                "acct",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Accounting Outsourcing",
                    "Outsource AP Workflows",
                    "Outsource AR Support",
                    "Finance Ops Philippines",
                    "Remote Accounting Bench",
                    "Scale Without Local Hire",
                    "Dedicated Ledger Seats",
                    f"Fit for {m['adj']} Finance",
                    "Month-End Support Staff",
                    "Vetted Accounting Seats",
                    "Outsource GL Support",
                    "Offshore Finance Ops",
                    "Partner-Led Accounting",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines accounting capacity for AP, AR, and ledger support.",
                    "Dedicated seats beat rotating contractors for close continuity.",
                    f"Ask about outsourcing finance ops for your {m['org']}.",
                    f"For {m['full']} businesses that want accountable remote accountants.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- bookkeeping ----
    cat["bookkeeping"] = {
        "Bookkeeping_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Bookkeeper Philippines",
                    "Filipino Bookkeeper Hire",
                    "Virtual Bookkeeper PH",
                    f"{m['tag']} Books Staffing",
                    "Vetted Books Shortlist",
                    "Interview Before Hire",
                    "Dedicated Books Seat",
                    "QuickBooks VA Hire",
                    "Xero Bookkeeper Hire",
                    "Employer Hiring Path",
                    "Remote Books Specialist",
                    "Not Marketplace Gigs",
                    f"Built for {m['sme']}",
                    "Weekly Books Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire a dedicated Filipino bookkeeper through a staffing partner.",
                    "Interview shortlisted talent; we recruit, vet, and support the hire.",
                    f"For {m['employers']} who need reliable weekly books capacity.",
                    "Ongoing bookkeeping hires — not marketplace task bundles.",
                ),
                "books",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Bookkeeper}",
                    "Philippines Books VA",
                    "Remote Reconciliation Hire",
                    "Filipino Books Specialist",
                    "Weekly Close Support",
                    "Transaction Coding VA",
                    "Scale Bookkeeping Ops",
                    f"{m['adj']} SMBs Hiring",
                    "Dedicated Books Talent",
                    "Virtual Books Assistant",
                    "Partner-Managed Hire",
                    "Interview-Ready Bookkeepers",
                    "Clear Employer Process",
                    "Tools You Already Use",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill bookkeeping roles with vetted Philippines specialists.",
                    "Support for categorisation, reconciliations, and weekly books rhythm."
                    if m["tag"] == "AU"
                    else "Support for categorization, reconciliations, and weekly books rhythm.",
                    f"Staffing support shaped for your {m['business']} books stack.",
                    f"We {m['specialize']} in employer-intent remote bookkeeping hires.",
                ),
                "books",
                "va",
            ),
        ],
        "Bookkeeping_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Bookkeeping PH",
                    "Offshore Bookkeeper Hire",
                    "Philippines Books Team",
                    f"{m['tag']} Books Partner",
                    "Dedicated Books Seat",
                    "Not Freelance Books",
                    "Vetted Bookkeeping Staff",
                    "Books Ops Outsourcing",
                    "Remote Books Capacity",
                    "Employer-Only Intake",
                    "Bookkeeper Placement",
                    "Predictable Books Coverage",
                    f"For {m['sme']}",
                    "Ongoing Reconciliation",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource bookkeeping to dedicated Philippines specialists.",
                    "Keep approval control; we recruit, vet, and support the seat.",
                    f"Built for {m['employers']} who want accountable offshore books help.",
                    "Partner-led outsourcing with interview-before-placement discipline.",
                ),
                "outsource",
                "books",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Bookkeeping Outsourcing",
                    "Outsource QuickBooks Books",
                    "Outsource Xero Books",
                    "Remote Books Bench",
                    "Philippines Books Ops",
                    "Scale Books Without Hire",
                    "Dedicated Ledger Seats",
                    f"Fit for {m['adj']} SMBs",
                    "Month-End Books Staff",
                    "Vetted Bookkeeping Seats",
                    "Outsource Bank Recs",
                    "Offshore Books Management",
                    "Partner-Led Books Ops",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines bookkeeping capacity for weekly and month-end work.",
                    "Dedicated seats keep the books current without freelancer churn.",
                    f"Ask about an outsourcing path for your {m['org']}'s books.",
                    f"For {m['full']} businesses that need dependable remote bookkeepers.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- administration (Hire VA + EA) ----
    cat["administration"] = {
        "Administration_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire a Virtual Assistant",
                    "Filipino VA for Business",
                    "Philippines VA Services",
                    f"{m['tag']} VA Staffing",
                    "How to Hire a VA",
                    "Vetted VA Shortlist",
                    "You Interview Finalists",
                    "Offshore VA Partner",
                    "VA Agency Alternative",
                    "Employers Hiring Only",
                    "Virtual Staffing Company",
                    "Not a Gig Marketplace",
                    f"Built for {m['sme']}",
                    "Dedicated Remote VA Seat",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire Filipino virtual assistants with a clear employer staffing path.",
                    "We recruit and vet; you interview before we support the placement.",
                    f"For {m['employers']} searching hire VA / Philippines VA intent.",
                    "Dedicated VAs for business ops — not freelance task boards.",
                ),
                "va",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Filipino VA}",
                    "Virtual Assistants PH",
                    "Hire VA Philippines",
                    "Offshore VA Hire",
                    "VA Services for SMBs",
                    "Looking for a VA?",
                    "Scale Admin Bandwidth",
                    f"{m['adj']} Teams Hiring",
                    "Dedicated VA Capacity",
                    "Partner-Managed VA Hire",
                    "Interview-Ready Talent",
                    "Overseas VA Staffing",
                    "Remote Admin Specialist",
                    "Philippines Staffing Hire",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Match converting hire-VA searches to vetted Philippines talent.",
                    "Coverage for inbox, scheduling, documentation, and ops follow-through.",
                    f"Staffing support shaped for your {m['business']} day-to-day ops.",
                    f"We {m['specialize']} in employer-intent remote VA hires.",
                ),
                "admin",
                "ph",
            ),
        ],
        "Administration_EA_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Executive Assistant",
                    "Filipino EA for Business",
                    "Virtual EA Philippines",
                    f"{m['tag']} EA Staffing",
                    "Vetted EA Shortlist",
                    "Interview Your EA",
                    "Dedicated EA Seat",
                    "Offshore EA Partner",
                    "Admin Assistant Hire",
                    "Employer Hiring Path",
                    "Remote EA Specialist",
                    "Not Freelance EA Gigs",
                    f"Made for {m['sme']}",
                    "Executive Ops Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire a dedicated Filipino executive assistant through a staffing partner.",
                    "Shortlist is interview-ready; we handle recruiting, vetting, and support.",
                    f"For {m['employers']} who need a reliable remote EA seat.",
                    "Ongoing executive support — not marketplace personal-assistant gigs.",
                ),
                "ea",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Virtual EA}",
                    "Philippines EA Hire",
                    "Remote Executive Support",
                    "Filipino Admin Assistant",
                    "Calendar & Travel Ops",
                    "Stakeholder Coord VA",
                    "Scale Executive Bandwidth",
                    f"{m['adj']} Leaders Hiring",
                    "Dedicated EA Capacity",
                    "Partner-Managed EA Hire",
                    "Interview-Ready EAs",
                    "Clear Employer Process",
                    "Office Admin Philippines",
                    "Virtual Admin Specialist",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill executive assistant roles with vetted Philippines specialists.",
                    "Support for calendar control, coordination, and executive follow-through.",
                    f"Staffing support shaped for leaders in your {m['business']}.",
                    f"We {m['specialize']} in employer-intent remote EA hires.",
                ),
                "ea",
                "ph",
            ),
        ],
    }

    # ---- customer service ----
    cat["customer_service"] = {
        "Customer_Service_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Customer Service PH",
                    "Filipino Support Hire",
                    "CS Virtual Assistant",
                    f"{m['tag']} Support Staffing",
                    "Vetted CS Shortlist",
                    "Interview Support Finalists",
                    "Dedicated Support Seat",
                    "Chat & Email VA Hire",
                    "Remote CS Specialist",
                    "Employer Hiring Path",
                    "Customer Care Philippines",
                    "Not Freelance Support",
                    f"Built for {m['sme']}",
                    "Ongoing Support Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire dedicated Filipino customer service staff through a staffing partner.",
                    "You interview the shortlist; we recruit, vet, and support placement.",
                    f"For {m['employers']} who need reliable remote support coverage.",
                    "Ongoing CS capacity — not rotating freelance agents.",
                ),
                "support",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire CS Support}",
                    "Hire Chat Support PH",
                    "Email Support VA Hire",
                    "Filipino Support Agent",
                    "Helpdesk Assistant PH",
                    "Ticket Triage VA",
                    "Scale Support Bandwidth",
                    f"{m['adj']} Support Teams",
                    "Philippines CS Talent",
                    "Dedicated Care Capacity",
                    "Partner-Managed Hire",
                    "Interview-Ready Agents",
                    "Clear Employer Process",
                    "Remote Customer Care",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill customer service roles with vetted Philippines specialists.",
                    "Coverage for inbox, chat, and customer care workflows.",
                    f"Staffing support shaped for your {m['business']} support queue.",
                    f"We {m['specialize']} in employer-intent remote support hires.",
                ),
                "support",
                "va",
            ),
        ],
        "Customer_Service_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Customer Service",
                    "Offshore Support Philippines",
                    "CS Ops Outsourcing",
                    f"{m['tag']} Support Partner",
                    "Dedicated Support Seat",
                    "Not Gig Support Bench",
                    "Vetted Support Staff",
                    "Helpdesk Outsourcing PH",
                    "Remote Care Capacity",
                    "Employer-Only Intake",
                    "Support Staff Placement",
                    "Predictable Coverage",
                    f"For {m['sme']}",
                    "Ongoing Ticket Capacity",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource customer service to dedicated Philippines specialists.",
                    "Keep QA control while we recruit, vet, and support the seat.",
                    f"Built for {m['employers']} scaling support without local headcount drag.",
                    "Partner-led outsourcing with interview-before-placement discipline.",
                ),
                "outsource",
                "cs",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Support Outsourcing",
                    "Outsource Chat Support",
                    "Outsource Email Support",
                    "Customer Care Philippines",
                    "Remote Support Bench",
                    "Scale Support Without Hire",
                    "Dedicated Agent Seats",
                    f"Fit for {m['adj']} Brands",
                    "Ticket Ops Staffing",
                    "Vetted Support Seats",
                    "Outsource Helpdesk Ops",
                    "Offshore Customer Care",
                    "Partner-Led Support Ops",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines support capacity for chat, email, and ticket workflows.",
                    "Dedicated seats keep response times steady without freelancer churn.",
                    f"Ask about an outsourcing path for your {m['org']}'s support.",
                    f"For {m['full']} businesses that need dependable remote customer care.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- hr ----
    cat["hr"] = {
        "Human_Resources_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Virtual HR Assistant",
                    "Filipino HR Staff Hire",
                    "HR Assistant Philippines",
                    f"{m['tag']} HR Staffing",
                    "Vetted HR Shortlist",
                    "Interview HR Finalists",
                    "Dedicated HR Seat",
                    "People Ops VA Hire",
                    "Payroll Admin Hire",
                    "Employer Hiring Path",
                    "Remote HR Specialist",
                    "Not Marketplace HR Gigs",
                    f"Built for {m['sme']}",
                    "Ongoing HR Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire dedicated Filipino HR support through a staffing partner.",
                    "You interview the shortlist; we recruit, vet, and support placement.",
                    f"For {m['employers']} who need reliable remote HR admin capacity.",
                    "Ongoing people-ops hires — not freelance HR task gigs.",
                ),
                "hr",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire HR Assistant}",
                    "Hire HR Coordinator PH",
                    "Onboarding Assistant Hire",
                    "Filipino People Ops VA",
                    "Benefits Admin Support",
                    "HR Docs & Compliance VA",
                    "Scale HR Bandwidth",
                    f"{m['adj']} HR Teams",
                    "Philippines HR Talent",
                    "Dedicated People Ops",
                    "Partner-Managed Hire",
                    "Interview-Ready HR Staff",
                    "Clear Employer Process",
                    "Remote Payroll Support",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill HR assistant roles with vetted Philippines specialists.",
                    "Support for coordination, documentation, onboarding, and payroll admin.",
                    f"Staffing support shaped for your {m['business']} people ops.",
                    f"We {m['specialize']} in employer-intent remote HR hires.",
                ),
                "hr",
                "va",
            ),
        ],
        "Human_Resources_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource HR Support PH",
                    "Offshore HR Philippines",
                    "People Ops Outsourcing",
                    f"{m['tag']} HR Partner",
                    "Dedicated HR Seat",
                    "Not Freelance HR Bench",
                    "Vetted HR Staff",
                    "Payroll Admin Offshore",
                    "Remote HR Capacity",
                    "Employer-Only Intake",
                    "HR Staff Placement",
                    "Predictable HR Coverage",
                    f"For {m['sme']}",
                    "Ongoing People Ops",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource HR administration to dedicated Philippines specialists.",
                    "Keep policy control; we recruit, vet, and support the seat.",
                    f"Built for {m['employers']} who need accountable offshore HR admin.",
                    "Partner-led outsourcing with interview-before-placement discipline.",
                ),
                "outsource",
                "hr",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH HR Outsourcing",
                    "Outsource Onboarding Ops",
                    "Outsource Payroll Admin",
                    "HR Ops Philippines",
                    "Remote People Ops Bench",
                    "Scale HR Without Hire",
                    "Dedicated HR Seats",
                    f"Fit for {m['adj']} HR",
                    "Employee Docs Staffing",
                    "Vetted HR Admin Seats",
                    "Outsource Leave Admin",
                    "Offshore People Ops",
                    "Partner-Led HR Ops",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines HR capacity for admin, onboarding, and payroll support.",
                    "Dedicated seats keep people ops moving without contractor churn.",
                    f"Ask about an outsourcing path for your {m['org']}'s HR admin.",
                    f"For {m['full']} businesses that need dependable remote HR support.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- recruitment ----
    cat["recruitment"] = {
        "Recruitment_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Recruitment Assistant",
                    "Filipino Recruiting Hire",
                    "Recruiting VA Philippines",
                    f"{m['tag']} TA Staffing",
                    "Vetted Recruiting Shortlist",
                    "Interview TA Finalists",
                    "Dedicated Recruiting Seat",
                    "Sourcing Assistant Hire",
                    "Screening Support Hire",
                    "Employer Hiring Path",
                    "Remote Recruiting Ops",
                    "Not Freelance Recruiters",
                    f"Built for {m['sme']}",
                    "Ongoing TA Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire dedicated Filipino recruitment support through a staffing partner.",
                    "You interview the shortlist; we recruit, vet, and support placement.",
                    f"For {m['employers']} who need reliable recruiting coordination capacity.",
                    "Ongoing TA support hires — not freelance sourcing gigs.",
                ),
                "recruit",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Recruiting VA}",
                    "Hire Sourcer Philippines",
                    "TA Coordinator Hire",
                    "Filipino Screening VA",
                    "Interview Scheduling VA",
                    "ATS Admin Assistant",
                    "Scale Recruiting Bandwidth",
                    f"{m['adj']} TA Teams",
                    "Philippines Recruiting Talent",
                    "Dedicated Sourcing Capacity",
                    "Partner-Managed Hire",
                    "Interview-Ready Recruiters",
                    "Clear Employer Process",
                    "Remote Recruiting Support",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill recruitment assistant roles with vetted Philippines specialists.",
                    "Support for sourcing coordination, screening support, and TA ops.",
                    f"Staffing support shaped for your {m['business']} hiring pipeline.",
                    f"We {m['specialize']} in employer-intent remote recruiting hires.",
                ),
                "recruit",
                "va",
            ),
        ],
        "Recruitment_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Recruiting Support",
                    "Offshore TA Philippines",
                    "Recruiting Ops Outsourcing",
                    f"{m['tag']} Recruiting Partner",
                    "Dedicated TA Seat",
                    "Not Gig Recruiting",
                    "Vetted Recruiting Staff",
                    "Sourcing Ops Offshore",
                    "Remote TA Capacity",
                    "Employer-Only Intake",
                    "Recruiting Staff Placement",
                    "Predictable Pipeline Help",
                    f"For {m['sme']}",
                    "Ongoing Screening Capacity",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource recruitment support to dedicated Philippines specialists.",
                    "Keep hiring decisions; we recruit, vet, and support the TA seat.",
                    f"Built for {m['employers']} who need accountable offshore recruiting ops.",
                    "Partner-led outsourcing with interview-before-placement discipline.",
                ),
                "outsource",
                "ta",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Recruiting Outsourcing",
                    "Outsource Talent Sourcing",
                    "Outsource Screening Ops",
                    "Recruiting Bench PH",
                    "Remote TA Ops Staff",
                    "Scale TA Without Hire",
                    "Dedicated Sourcer Seats",
                    f"Fit for {m['adj']} TA",
                    "Candidate Coord Staffing",
                    "Vetted Recruiting Seats",
                    "Outsource ATS Admin",
                    "Offshore Recruiting Ops",
                    "Partner-Led TA Ops",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines recruiting capacity for sourcing and screening support.",
                    "Dedicated seats keep pipelines moving without contractor churn.",
                    f"Ask about an outsourcing path for your {m['org']}'s TA ops.",
                    f"For {m['full']} businesses that need dependable remote recruiting support.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    # ---- sales ----
    cat["sales"] = {
        "Sales_Hire_PH": [
            (
                "A_staffing",
                lambda m: H(
                    "Hire Lead Gen Specialist",
                    "Filipino Sales Assistant",
                    "Appointment Setter PH",
                    f"{m['tag']} Sales Staffing",
                    "Vetted Sales Shortlist",
                    "Interview Sales Finalists",
                    "Dedicated Sales Seat",
                    "Pipeline Support Hire",
                    "Outbound VA Philippines",
                    "Employer Hiring Path",
                    "Remote SDR Support",
                    "Not Freelance Lead Gigs",
                    f"Built for {m['sme']}",
                    "Ongoing Lead Capacity",
                    "Book a Hiring Consult",
                ),
                lambda m: D(
                    "Hire dedicated Filipino sales support through a staffing partner.",
                    "You interview the shortlist; we recruit, vet, and support placement.",
                    f"For {m['employers']} who need reliable lead-gen and appointment capacity.",
                    "Ongoing sales support hires — not freelance list-pull gigs.",
                ),
                "sales",
                "hire",
            ),
            (
                "B_role",
                lambda m: H(
                    "{KeyWord:Hire Lead Gen VA}",
                    "Hire Appointment Setter",
                    "B2B Prospecting VA",
                    "Filipino Pipeline VA",
                    "Lead Research Specialist",
                    "CRM Sales Admin Hire",
                    "Scale Outbound Bandwidth",
                    f"{m['adj']} Sales Teams",
                    "Philippines Sales Talent",
                    "Dedicated Outbound Seat",
                    "Partner-Managed Hire",
                    "Interview-Ready Setters",
                    "Clear Employer Process",
                    "Remote Sales Support",
                    "Request Employer Consult",
                ),
                lambda m: D(
                    "Fill sales support roles with vetted Philippines specialists.",
                    "Coverage for prospecting support, list work, and appointment setting.",
                    f"Staffing support shaped for your {m['business']} pipeline.",
                    f"We {m['specialize']} in employer-intent remote sales hires.",
                ),
                "sales",
                "va",
            ),
        ],
        "Sales_Outsource_PH": [
            (
                "A_partner",
                lambda m: H(
                    "Outsource Lead Generation",
                    "Offshore Sales Philippines",
                    "Sales Ops Outsourcing",
                    f"{m['tag']} Sales Partner",
                    "Dedicated Lead Gen Seat",
                    "Not Gig Outbound",
                    "Vetted Sales Staff",
                    "Appointment Setting PH",
                    "Remote Pipeline Capacity",
                    "Employer-Only Intake",
                    "Sales Staff Placement",
                    "Predictable Outbound Help",
                    f"For {m['sme']}",
                    "Ongoing Prospecting Ops",
                    "Start With a Consult",
                ),
                lambda m: D(
                    "Outsource lead generation support to dedicated Philippines specialists.",
                    "Keep offer control; we recruit, vet, and support the sales seat.",
                    f"Built for {m['employers']} who need accountable offshore outbound help.",
                    "Partner-led outsourcing with interview-before-placement discipline.",
                ),
                "outsource",
                "sales",
            ),
            (
                "B_capacity",
                lambda m: H(
                    "PH Lead Gen Outsourcing",
                    "Outsource Appointment Set",
                    "Outsource Prospecting",
                    "Sales Development PH",
                    "Remote Outbound Bench",
                    "Scale Pipeline Without Hire",
                    "Dedicated Setter Seats",
                    f"Fit for {m['adj']} Sales",
                    "List Building Staffing",
                    "Vetted Lead Gen Seats",
                    "Outsource CRM Admin",
                    "Offshore SDR Support",
                    "Partner-Led Sales Ops",
                    "Interview Then Place",
                    "Book Outsourcing Consult",
                ),
                lambda m: D(
                    "Add Philippines sales capacity for prospecting and appointment setting.",
                    "Dedicated seats keep outbound moving without freelancer churn.",
                    f"Ask about an outsourcing path for your {m['org']}'s pipeline.",
                    f"For {m['full']} businesses that need dependable remote sales support.",
                ),
                "offshore",
                "ph",
            ),
        ],
    }

    return cat


RSA_CATALOG = _rsa_catalog()


def city_rsa(mkt: str) -> tuple[list[str], list[str], str, str]:
    m = market_bits(mkt)
    if mkt == "US":
        headlines = [
            "{LOCATION(City):Hire Filipino VA}",
            "Hire Virtual Assistant",
            "Filipino VA for US Teams",
            "US City Employer Hire",
            "Vetted VA Shortlist",
            "Interview Before You Hire",
            "Dedicated Remote VA",
            "Philippines Admin Staff",
            "Employers Hiring Only",
            "Offshore VA Partner",
            "Inbox & Calendar Support",
            "Clear Employer Path",
            "Remote Admin Capacity",
            "Partner-Led VA Hiring",
            "Request a Hiring Consult",
        ]
        descs = [
            "Hire dedicated Philippines virtual assistants for your US business operations.",
            "City-aware headline test — same staffing-partner path and employer landing page.",
            "You interview the shortlist. We recruit, vet, and support the hire.",
            "Light geo creative test for US metros — not a city-farm keyword blast.",
        ]
    else:
        headlines = [
            "{LOCATION(City):Hire Filipino VA}",
            "Hire Virtual Assistant",
            "Filipino VA for AU Teams",
            "AU City Employer Hire",
            "Vetted VA Shortlist",
            "Interview Before You Hire",
            "Dedicated Remote VA",
            "Philippines Admin Staff",
            "Employers Hiring Only",
            "Offshore VA Partner",
            "Inbox & Calendar Support",
            "Clear Employer Path",
            "Remote Admin Capacity",
            "Partner-Led VA Hiring",
            "Request a Hiring Consult",
        ]
        descs = [
            "Hire dedicated Philippines virtual assistants for your Australian business.",
            "City-aware headline test — same staffing-partner path and employer landing page.",
            "You interview the shortlist. We recruit, vet, and support the hire.",
            "Light geo creative test for Australian cities — not a city-farm keyword blast.",
        ]
    validate_rsa(headlines, descs, f"{mkt}/administration/city")
    return headlines, descs, "hire", "local"


def blank_row() -> dict[str, str]:
    return {k: "" for k in FIELDS}


def camp_name(mkt: str, role: str) -> str:
    return f"VC_{mkt}_S_ROLE_{role}"


def iter_role_ags(role: str) -> list[str]:
    return list(EXACT_BY_AG[role].keys())


def build() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for mkt, loc, budget_ph in (
        ("US", "United States", "[APPROVAL_DAILY_BUDGET_USD]"),
        ("AU", "Australia", "[APPROVAL_DAILY_BUDGET_AUD]"),
    ):
        base_url = f"https://vision-three-alpha.vercel.app/{mkt.lower()}"
        mbits = market_bits(mkt)
        for role in ROLES:
            cname = camp_name(mkt, role)
            comment = (
                f"Stage1 v3 Max Clicks; Search partners OFF; Display OFF; "
                f"brand deferred; role={ROLE_LABEL[role]}; theme-split AGs; "
                f"confirm networks in Editor"
            )

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

            final = f"{base_url}?role={role}"

            for ag in iter_role_ags(role):
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
                        "Ad Group": ag,
                        "Ad Group Status": "Paused",
                        "Max CPC": "[APPROVAL_MAX_CPC]",
                        "Comment": f"Theme AG — {ag}",
                    }
                )
                rows.append(r)

                seen_exact: set[str] = set()
                for kw in EXACT_BY_AG[role][ag]:
                    key = kw.strip().lower()
                    if key in seen_exact:
                        continue
                    seen_exact.add(key)
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
                            "Ad Group": ag,
                            "Ad Group Status": "Paused",
                            "Max CPC": "[APPROVAL_MAX_CPC]",
                            "Keyword": kw,
                            "Criterion Type": "Exact",
                            "Keyword Status": "Paused",
                            "Comment": "v4 Exact — ST evidence + employer long-tail",
                        }
                    )
                    rows.append(r)

                seen_phrase: set[str] = set()
                for kw in PHRASE_BY_AG[role][ag]:
                    key = kw.strip().lower()
                    if key in seen_phrase:
                        continue
                    seen_phrase.add(key)
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
                            "Ad Group": ag,
                            "Ad Group Status": "Paused",
                            "Max CPC": "[APPROVAL_MAX_CPC]",
                            "Keyword": kw,
                            "Criterion Type": "Phrase",
                            "Keyword Status": "Paused",
                            "Comment": "v4 Phrase — discovery from converting ST clusters",
                        }
                    )
                    rows.append(r)

                for suffix, hl_fn, desc_fn, p1, p2 in RSA_CATALOG[role][ag]:
                    hs = hl_fn(mbits)
                    ds = desc_fn(mbits)
                    validate_rsa(hs, ds, f"{mkt}/{role}/{ag}/{suffix}")
                    for p in (p1, p2):
                        if len(p) > PATH_MAX:
                            raise ValueError(f"path too long: {p}")
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
                            "Ad Group": ag,
                            "Ad Group Status": "Paused",
                            "Max CPC": "[APPROVAL_MAX_CPC]",
                            "Ad Status": "Paused",
                            "Ad type": "Responsive search ad",
                            "Final URL": final,
                            "Path 1": p1,
                            "Path 2": p2,
                            "Comment": (
                                f"RSA angle {suffix}; full 15/4; "
                                f"role-unique; market={mkt}; no invented pricing"
                            ),
                        }
                    )
                    for i, h in enumerate(hs, 1):
                        r[f"Headline {i}"] = h
                    for i, d in enumerate(ds, 1):
                        r[f"Description {i}"] = d
                    rows.append(r)

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
                        "Comment": "LIGHT city Phrase + location-insertion RSA",
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
                        "Comment": "v4 curated + real ST waste (jobs/salary/LATAM/DSA/reviews)",
                    }
                )
                rows.append(r)

            # Callouts (campaign level) — filled, employer-focused
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

    ads = [r for r in rows if r["Row Type"] == "Ad"]
    for r in ads:
        hs = [r[f"Headline {i}"] for i in range(1, 16)]
        ds = [r[f"Description {i}"] for i in range(1, 5)]
        if any(not h for h in hs) or any(not d for d in ds):
            raise SystemExit(f"BLANK RSA SLOT: {r['Campaign']} / {r['Ad Group']}")
        validate_rsa(hs, ds, f"{r['Campaign']}/{r['Ad Group']}")

    us_ads = [
        r
        for r in ads
        if r["Campaign"].startswith("VC_US_") and "City" not in r["Ad Group"]
    ]
    hl_sets = []
    for r in us_ads:
        hs = {
            h
            for h in (r[f"Headline {i}"] for i in range(1, 16))
            if not h.startswith("{")
        }
        hl_sets.append(hs)
    freq = Counter()
    for s in hl_sets:
        for h in s:
            freq[h] += 1
    spam = [(h, c) for h, c in freq.items() if c > 12]
    if spam:
        raise SystemExit(f"Boilerplate headline spam across RSAs: {spam[:8]}")

    for c in camps:
        kws = [
            r
            for r in rows
            if r["Campaign"] == c and r["Row Type"] == "Keyword" and r["Negative"] != "True"
        ]
        ads_c = [r for r in rows if r["Campaign"] == c and r["Row Type"] == "Ad"]
        if not kws or not ads_c:
            raise SystemExit(f"EMPTY SHELL: {c} kws={len(kws)} ads={len(ads_c)}")
        ags = {r["Ad Group"] for r in kws}
        if len(ags) < 2:
            raise SystemExit(f"FAT SINGLE AG: {c} ags={ags}")

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

    if any("BRAND" in c for c in camps):
        raise SystemExit("Brand campaign found — should be deferred/absent")

    mt = Counter(
        r["Criterion Type"]
        for r in rows
        if r["Row Type"] == "Keyword" and r["Negative"] != "True"
    )
    print("Positive match types:", dict(mt))
    if mt.get("Broad"):
        raise SystemExit("Positive Broad keywords not allowed")

    pos_blob = " ".join(
        r["Keyword"].lower()
        for r in rows
        if r["Row Type"] == "Keyword" and r["Negative"] != "True"
    )
    for term in (
        "medical",
        "nurse",
        "spanish",
        "programmer",
        "coding",
        "web developer",
        "salary",
        " career",
    ):
        if term in pos_blob:
            raise SystemExit(f"LEAK in positives: {term}")

    negs = {
        r["Keyword"].lower()
        for r in rows
        if r["Row Type"] == "Campaign negative keyword"
    }
    if "hire" in negs or "hiring" in negs:
        raise SystemExit("hire/hiring must not be campaign negatives")

    for r in rows:
        if r["Row Type"] == "Callout" and not r["Callout text"]:
            raise SystemExit("Empty callout")
        if r["Row Type"] == "Sitelink" and (
            not r["Link Text"] or not r["Description Line 1"] or not r["Final URL"]
        ):
            raise SystemExit("Empty sitelink fields")
        if r["Row Type"] == "Structured snippet" and not r["Snippet Values"]:
            raise SystemExit("Empty structured snippet")

    dki_ads = [
        r
        for r in ads
        if "{KeyWord:" in " ".join(r[f"Headline {i}"] for i in range(1, 16))
    ]
    if len(dki_ads) < 18:
        raise SystemExit(f"DKI underused: only {len(dki_ads)} ads have KeyWord insertion")

    print(
        "QA OK — RSA ads:",
        len(ads),
        "positive KWs:",
        sum(mt.values()),
        "unique negs:",
        len(negs),
    )


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
