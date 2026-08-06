#!/usr/bin/env python3
"""Build Stage 1 Google Ads Editor import — 2 campaigns × 2 markets (v6).

v6 (2026-08-05): George-approved architecture — Brand deferred.
  VC_{US|AU}_S_CORE   (~60%) high-intent VA / hire / PH-offshore
  VC_{US|AU}_S_ROLES  (~40%) Digital · Social · Admin · Controlled roles

OPERATING RULE (locked): Old account = historical archive.
  New VC_* = isolated clean system. This builder emits ONLY:
  - new Paused VC_* campaigns (never PM_*)
  - campaign-level negatives from the curated NEGATIVES list below
  It does NOT pull, attach, or reference account shared / PM_* mega
  negative lists (some 3000+ terms). Do not add shared-list rows here.

RSA: 3 unique full RSAs (15H/4D) per main AG — hire-intent / role-outcome or
PH-offshore / proof-speed-of-staffing angles from ST evidence. City-test AGs
stay 1 RSA. Exact+Phrase only. No Ads API. All Paused.

Activation (docs only — CSV still all Paused; do not invent v8 for vibes):
  See ads-launch/PHASED-ACTIVATION.md — enable PH/Filipino/offshore long-tail
  Exact first across Core+Roles (books/accounting OK when PH-shaped);
  generic Core heads later. PRIMARY/CONTROLLED labels are structure, not enable order.

Outputs:
  - ads-launch/google-ads-editor-import.csv (= multi-account; Account on every row)
  - ads-launch/google-ads-editor-import-us.csv (US only — preferred import path)
  - ads-launch/google-ads-editor-import-au.csv (AU only — preferred import path)
  - ads-launch/google-ads-editor-import-multi-account.csv (same as combined)
  - ads-launch/phase1-enable-manifest-us.csv / -au.csv (review tiers; all Paused)
  - ads-launch/PHASE1-REVIEW.md
  - ads-launch/EDITOR-PREFLIGHT-REPORT.md
  - mirrors into xray/docs/ads-launch/
"""

from __future__ import annotations

import csv
import json
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
LP_VERSION = "stage1-v7"

# George-decidable Stage 1 defaults (see ads-launch/DECISIONS.md).
# 2-campaign model: Core ~60% / Roles ~40% of Stage 1 daily spend.
# Placeholders within a $10–20k/account monthly budget story (not enable approval).
# US $75+$50 = $125/day ≈ $3.8k/mo; AU A$75+A$50 ≈ A$3.8k/mo — room to scale.
BUDGET_DAILY = {
    "US": {"core": "75", "roles": "50"},  # USD
    "AU": {"core": "75", "roles": "50"},  # AUD
}
MAX_CPC = {"US": "8", "AU": "6"}  # USD / AUD

# Editor multi-account import — Customer IDs in XXX-XXX-XXXX format.
# Column name must be "Account" (Google Ads Editor). Required so USA+AU
# rows do not land in the wrong client account when importing one CSV.
ACCOUNT_IDS = {
    "US": "496-715-1855",
    "AU": "573-539-1940",
}

# Roles campaign AG structure labels (all under VC_*_S_ROLES).
# NOTE: PRIMARY vs CONTROLLED is package structure only — NOT enable order.
# Enable order = intent quality per ads-launch/PHASED-ACTIVATION.md
# (PH/Filipino/offshore long-tail first; books/accounting can be Phase 1).
PRIMARY_ROLE_KEYS = ("digital_marketing", "social_media")
# Admin = EA/admin support (generic VA cluster lives in CORE, not here).
ADMIN_ROLE_KEY = "administration"
CONTROLLED_ROLE_KEYS = (
    "accounting",
    "bookkeeping",
    "customer_service",
    "hr",
    "recruitment",
    "sales",
)

# Final URL suffix only — do NOT also put UTMs on Tracking template (double-UTM bug).
# Use supported ValueTrack IDs — NOT undefined {_campaign}/{_adgroup} custom params.
SUFFIX = (
    "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"
    f"&utm_content={{adgroupid}}&utm_term={{keyword}}&utm_matchtype={{matchtype}}"
    f"&utm_device={{device}}&lp_version={LP_VERSION}"
)
TRACK = "{lpurl}"

# Commercial / research negatives held out of import — judge from live ST + lead quality.
# Still reported in EDITOR-PREFLIGHT-REPORT.md. Competitor-named review terms stay active.
# Broad negs block any query containing all tokens — pay/hourly rate + generic VA
# reviews suppress employer research, so they stay out of import until ST proves waste.
NEGATIVE_REVIEW_HOLDOUT = (
    "review",
    "reviews",
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
    "cheap",
    "cheapest",
    "filipina va",
    # Employer-research Broad risks (moved from active NEGATIVES)
    "pay rate",
    "hourly rate",
    "virtual assistant reviews",
)

# Employer-research queries that must remain reachable under campaign Broad negatives.
# qa() fails if any active Broad negative would block these (token containment).
EMPLOYER_RESEARCH_CANARIES = (
    "virtual assistant pay rate for us employers",
    "filipino virtual assistant hourly rate",
    "virtual assistant reviews for small business",
    "best virtual assistant reviews comparison",
    "virtual assistant pricing philippines",
    "how much does a virtual assistant cost",
    "cost of a virtual assistant for small business",
    "virtual assistant philippines cost",
    "cheap virtual assistant philippines for hire",
    "top 10 virtual assistant companies for agencies",
    "filipina va for bookkeeping hire",
)

FIELDS = [
    "Account",  # Customer ID — required for USA+AU multi-account Editor import
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
    "Maximum CPC bid limit",  # Maximize Clicks campaign-level cap only
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

# Campaign-level Broad negatives — curated Stage 1 set only (tight).
# Applied per VC_* campaign as "Campaign negative keyword" rows.
# NEVER inherit account shared / PM_* mega lists into this package.
# Never bare hire/hiring. Do NOT blanket-neg "how to" (blocks converting
# "how to hire a virtual assistant"); use specific DIY how-tos instead.
# Soft cap: keep this curated, not a 3k dump. QA fails if unique > MAX.
MAX_UNIQUE_NEGATIVES = 220
NEGATIVES = [
    # Job seeker (ST: VA jobs $723, salary $270+, AU jobs $426, PH salary $231)
    "job",
    "jobs",
    "salary",
    "salaries",
    "wage",
    "wages",
    # pay rate / hourly rate → NEGATIVE_REVIEW_HOLDOUT (employer research)
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
# Review / pricing research — generic commercial holdouts moved to
    # NEGATIVE_REVIEW_HOLDOUT (not imported). Keep competitor-named review terms.
    "bruntwork reviews",
    "brunt work reviews",
    "remote coworker reviews",
    "onlinejobs ph reviews",
    "onlinejobs ph pricing",
    "myoutdesk reviews",
    "athena assistant pricing",
    "athena ea reviews",
    "virtualstaff ph reviews",
    # virtual assistant reviews → NEGATIVE_REVIEW_HOLDOUT (employer research)
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
    # cheap / cheapest → NEGATIVE_REVIEW_HOLDOUT
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
    # filipina va → NEGATIVE_REVIEW_HOLDOUT (can be employer intent)
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

_HOLDOUT_SET = {t.lower() for t in NEGATIVE_REVIEW_HOLDOUT}
NEGATIVES = [n for n in NEGATIVES if n.lower() not in _HOLDOUT_SET]
assert not any(n.lower() in _HOLDOUT_SET for n in NEGATIVES)

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

# Canonical category LP slugs (vision microsite /{market}/{slug})
ROLE_CATEGORY_SLUG = {
    "digital_marketing": "digital-marketing",
    "social_media": "social-media",
    "accounting": "accounting",
    "bookkeeping": "bookkeeping",
    "administration": "administrative-support",
    "customer_service": "customer-service",
    "hr": "hr",
    "recruitment": "recruitment",
    "sales": "sales",
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
        # v6: generic VA / hire / PH-offshore cluster lives in VC_*_S_CORE.
        # ROLES Admin AG = EA / admin support only (category Final URL still admin).
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
        # v6: Hire_PH Phrase seeds moved to CORE_PHRASE_BY_AG
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

# ---------------------------------------------------------------------------
# CORE campaign keywords — high-intent VA / hire / PH-offshore (ST-heavy).
# Split Hire vs Offshore to avoid intra-campaign Exact overlap.
# ---------------------------------------------------------------------------

CORE_EXACT_BY_AG: dict[str, list[str]] = {
    "Hire_VA_PH": [
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
        "hire filipino virtual assistant",
        "hire a filipino virtual assistant",
        "hire filipino virtual assistants",
        "hire filipino va",
        "hire a filipino va",
        "hire virtual assistant from philippines",
        "hire philippines virtual assistant",
        "hire a virtual assistant philippines",
        "hire virtual assistant philippines",
        "hire va philippines",
        "hire offshore virtual assistant",
        "hire overseas virtual assistant",
        "hire remote virtual assistant",
        "hire a va in the philippines",
        "hire a virtual assistant in the philippines",
        "hiring virtual assistant philippines",
        "hire virtual assistant ph",
        "virtual assistant hiring philippines",
        "virtual assistant hiring",
        "hiring virtual assistant",
        "filipino virtual assistant for hire",
        "where to hire virtual assistant philippines",
        "virtual assistant services",
        "va services",
        "virtual assistant agency",
        "va agency",
        "virtual assistant company",
        "virtual assistant companies",
        "dedicated virtual assistant",
        "virtual assistant for business",
        "remote virtual assistant for business",
        "virtual assistance",
        "virtual assistance services",
        "virtual assistant providers",
        "find a virtual assistant",
        "virtual staffing company",
    ],
    "Offshore_VA_PH": [
        "filipino virtual assistant",
        "filipino virtual assistants",
        "filipino va",
        "filipino vas",
        "virtual assistant philippines",
        "philippines virtual assistant",
        "virtual assistants philippines",
        "philippine virtual assistant",
        "virtual assistant in philippines",
        "virtual assistants in philippines",
        "virtual assistants in the philippines",
        "virtual assistant from the philippines",
        "va philippines",
        "philippines va",
        "va in philippines",
        "va from philippines",
        "va agency philippines",
        "virtual assistant agency philippines",
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
        "philippines va company",
        "philippines assistant",
        "virtual staff philippines",
        "virtual staff ph",
        "remote staff philippines",
        "philippines virtual staffing",
        "filipino virtual assistant company",
        "dedicated virtual assistant philippines",
    ],
}

CORE_PHRASE_BY_AG: dict[str, list[str]] = {
    "Hire_VA_PH": [
        "hire virtual assistant",
        "hire a virtual assistant",
        "hire filipino virtual assistant",
        "hire filipino va",
        "hire va philippines",
        "hire virtual assistant philippines",
        "how to hire a virtual assistant",
        "looking for a virtual assistant",
        "virtual assistant for business",
        "virtual assistant services",
        "va agency",
        "hire remote filipino assistant",
        "dedicated virtual assistant",
    ],
    "Offshore_VA_PH": [
        "offshore virtual assistant",
        "offshore va",
        "philippines virtual assistant",
        "filipino virtual assistant",
        "virtual assistant philippines",
        "va philippines",
        "virtual assistant services philippines",
        "va agency philippines",
        "philippines virtual staffing",
        "filipino virtual assistant company",
        "dedicated virtual assistant philippines",
        "outsource virtual assistant philippines",
    ],
}


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


def _third_rsa_angles() -> dict:
    """Third unique RSA per main AG — proof/speed or dedicated-seat angles from ST evidence.
    Not a noun-swap clone of A/B. City-test AGs stay 1 RSA.
    """

    def H(*hs: str) -> list[str]:
        return list(hs)

    def D(*ds: str) -> list[str]:
        return list(ds)

    out: dict = {}
    out['digital_marketing'] = {
        'Digital_Marketing_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Marketing Talent",
                    "Vetted Marketers Ready",
                    "Recruit Then You Interview",
                    "Marketing Hire Shortlist",
                    "PH Marketer Screening",
                    "Skip Marketplace Search",
                    "Role Brief to Shortlist",
                    "Get Marketing Finalists",
                    "Digital Hire Pathway",
                    "Screened SEO Candidates",
                    "Content Hire Pipeline",
                    "Employer Shortlist First",
                    "Marketing Seat Ready",
                    "Staffing Pipeline Speed",
                    "Ask for Marketing Shortlist",
                ),
                lambda m: D(
                    "Need a marketing hire? We recruit and screen Philippines talent into a shortlist.",
                    "You interview finalists — we handle sourcing and vetting for digital roles.",
                    "Speed comes from a staffing pipeline — placement timing set in follow-up.",
                    "Tell us the marketing seat. We return interview-ready candidates.",
                ),
            'shortlist',
            'mkt',
        ),
        'Digital_Marketing_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH Marketer",
                    "Same Marketer Daily",
                    "Accountable Marketing Seat",
                    "Philippines Marketing Hire",
                    "Not Rotating Freelancers",
                    "Offshore With Ownership",
                    "Marketing Ops Continuity",
                    "PH Specialist You Keep",
                    "Interview Then Commit",
                    "Vetted Then Dedicated",
                    "Remote Marketing Owner",
                    "Staffing Not Gig Apps",
                    "Marketing Seat Proof",
                    "Campaign Owner From PH",
                    "Request Dedicated Seat",
                ),
                lambda m: D(
                    "Outsource marketing with a dedicated Philippines seat — not freelancer rotation.",
                    "Continuity is the proof: one vetted marketer you interview before placement.",
                    f"Built for {m['employers']} who want accountable offshore marketing capacity.",
                    "Partner-led seat. You keep hire authority — savings are not promised in ads.",
                ),
            'dedicated',
            'mkt',
        ),
    }

    out['social_media'] = {
        'Social_Media_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Social Managers",
                    "Vetted SMM Finalists",
                    "SMM Hire Shortlist Fast",
                    "Recruit Social Then Interview",
                    "PH Community Manager Screen",
                    "Skip Gig SMM Search",
                    "Social Role to Shortlist",
                    "Get SMM Candidates Ready",
                    "Employer Social Hire Path",
                    "Screened Content Schedulers",
                    "Brand Voice Hire Pipeline",
                    "Social Seat Shortlist",
                    "Staffing Pipeline for SMM",
                    "Interview-Ready SMM List",
                    "Ask for SMM Shortlist",
                ),
                lambda m: D(
                    "Need a social media hire? We recruit and screen Philippines SMM talent first.",
                    "Shortlist-first path: you interview; we source and vet community managers.",
                    "Speed means a ready staffing pipeline — not a response-time promise.",
                    "Tell us the social seat. Review vetted finalists before you hire.",
                ),
            'shortlist',
            'smm',
        ),
        'Social_Media_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH Social Seat",
                    "Same SMM Every Day",
                    "Accountable Social Manager",
                    "Philippines SMM Continuity",
                    "Not Freelance Posters",
                    "Offshore Brand Voice Seat",
                    "Social Ops You Can Keep",
                    "Interview SMM Then Place",
                    "Vetted Channel Owner PH",
                    "Remote Social Ownership",
                    "Staffing Not Gig Boards",
                    "Proof in Dedicated SMM",
                    "Community Seat From PH",
                    "Calendar Owner Dedicated",
                    "Request Dedicated SMM",
                ),
                lambda m: D(
                    "Outsource social with a dedicated Philippines seat — not rotating freelancers.",
                    "Proof is continuity: one vetted SMM you interview before placement support.",
                    f"Built for {m['employers']} needing accountable offshore social capacity.",
                    "Partner-led seat model. Engagement and follower goals set after we talk.",
                ),
            'dedicated',
            'smm',
        ),
    }

    out['accounting'] = {
        'Accounting_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Accountants PH",
                    "Vetted Finance Finalists",
                    "Accounting Hire Shortlist",
                    "Recruit AP Then Interview",
                    "PH Accountant Screening",
                    "Skip Freelance Finance",
                    "Finance Role to Shortlist",
                    "Get Accounting Finalists",
                    "Employer Finance Hire Path",
                    "Screened Ledger Candidates",
                    "AP Hire Pipeline Ready",
                    "Accounting Seat Shortlist",
                    "Staffing Pipeline Finance",
                    "Interview-Ready Accountants",
                    "Ask for Finance Shortlist",
                ),
                lambda m: D(
                    "Need an accounting hire? We recruit and screen Philippines finance talent first.",
                    "Shortlist-first: you interview AP/AR and accounting finalists we vet.",
                    "Credentials and close timing are confirmed in follow-up, not ad promises.",
                    "Tell us the finance seat. Review vetted candidates before you hire.",
                ),
            'shortlist',
            'acct',
        ),
        'Accounting_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH Accountant",
                    "Same Finance Seat Daily",
                    "Accountable Ledger Support",
                    "Philippines Accounting Seat",
                    "Not Gig Bookkeeping Apps",
                    "Offshore Finance Continuity",
                    "AP Owner You Can Keep",
                    "Interview Then Place PH",
                    "Vetted Accounting Seat",
                    "Remote Finance Ownership",
                    "Staffing Not Task Markets",
                    "Proof in Dedicated Finance",
                    "Ledger Seat From PH",
                    "Close Support Dedicated",
                    "Request Dedicated Finance",
                ),
                lambda m: D(
                    "Outsource accounting with a dedicated Philippines seat — not task gigs.",
                    "Proof is continuity: one vetted finance seat you interview first.",
                    f"Built for {m['employers']} who need accountable offshore accounting capacity.",
                    "Partner-led model. Rates and terms discussed after we understand the seat.",
                ),
            'dedicated',
            'acct',
        ),
    }

    out['bookkeeping'] = {
        'Bookkeeping_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Bookkeepers PH",
                    "Vetted Books Finalists",
                    "Bookkeeper Hire Shortlist",
                    "Recruit Books Then Interview",
                    "PH Bookkeeper Screening",
                    "Skip Marketplace Books",
                    "Books Role to Shortlist",
                    "Get Bookkeeping Finalists",
                    "Employer Books Hire Path",
                    "Screened Reconciliation Help",
                    "Weekly Books Hire Pipeline",
                    "Books Seat Shortlist",
                    "Staffing Pipeline Books",
                    "Interview-Ready Bookkeepers",
                    "Ask for Books Shortlist",
                ),
                lambda m: D(
                    "Need a bookkeeper? We recruit and screen Philippines books talent first.",
                    "Shortlist-first hiring: you interview; we source and vet bookkeepers.",
                    "Speed means a ready staffing pipeline — not a turnaround promise.",
                    "Tell us the books seat. Review vetted finalists before you hire.",
                ),
            'shortlist',
            'books',
        ),
        'Bookkeeping_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH Bookkeeper",
                    "Same Books Seat Weekly",
                    "Accountable Books Support",
                    "Philippines Books Continuity",
                    "Not Freelance Book Tasks",
                    "Offshore Books Ownership",
                    "Books Seat You Can Keep",
                    "Interview Bookkeeper First",
                    "Vetted Weekly Books Seat",
                    "Remote Books Ownership",
                    "Staffing Not Gig Bundles",
                    "Proof in Dedicated Books",
                    "Reconciliation Seat PH",
                    "Xero QB Seat Dedicated",
                    "Request Dedicated Books",
                ),
                lambda m: D(
                    "Outsource bookkeeping with a dedicated Philippines seat — not task bundles.",
                    "Proof is continuity: one vetted bookkeeper you interview before placement.",
                    f"Built for {m['employers']} who need accountable offshore books capacity.",
                    "Partner-led seat. Tool fit is confirmed in follow-up, not in the ad.",
                ),
            'dedicated',
            'books',
        ),
    }

    out['administration'] = {
        'Administration_EA_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Executive Assistants",
                    "Vetted EA Finalists",
                    "EA Hire Shortlist Fast",
                    "Recruit EA Then Interview",
                    "PH EA Screening Path",
                    "Skip Freelance EA Hunt",
                    "EA Role Brief to List",
                    "Get EA Candidates Ready",
                    "Employer EA Hire Path",
                    "Screened Calendar Support",
                    "Executive Ops Pipeline",
                    "EA Seat Shortlist",
                    "Staffing Pipeline for EA",
                    "Interview-Ready EA List",
                    "Ask for EA Shortlist",
                ),
                lambda m: D(
                    "Need an executive assistant? We recruit and screen Philippines EA talent first.",
                    "Shortlist-first: you interview; we source and vet remote EA finalists.",
                    "Speed means a staffing pipeline — availability confirmed in follow-up.",
                    "Tell us the EA seat. Review vetted candidates before you hire.",
                ),
            'shortlist',
            'ea',
        ),
    }

    out['customer_service'] = {
        'Customer_Service_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Support Agents",
                    "Vetted CS Finalists",
                    "Support Hire Shortlist",
                    "Recruit CS Then Interview",
                    "PH Support Screening",
                    "Skip Freelance Agents",
                    "Support Role to Shortlist",
                    "Get CS Candidates Ready",
                    "Employer Support Hire Path",
                    "Screened Chat Email Help",
                    "Helpdesk Hire Pipeline",
                    "CS Seat Shortlist",
                    "Staffing Pipeline Support",
                    "Interview-Ready Agents",
                    "Ask for Support Shortlist",
                ),
                lambda m: D(
                    "Need customer service staff? We recruit and screen Philippines support talent.",
                    "Shortlist-first hiring: you interview; we source and vet CS finalists.",
                    "Speed means a ready staffing pipeline — not an SLA promise.",
                    "Tell us the support seat. Review vetted agents before you hire.",
                ),
            'shortlist',
            'cs',
        ),
        'Customer_Service_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH Support Seat",
                    "Same Agent Coverage Daily",
                    "Accountable Care Capacity",
                    "Philippines Support Continuity",
                    "Not Rotating Gig Agents",
                    "Offshore Support Ownership",
                    "Support Seat You Keep",
                    "Interview Agents Then Place",
                    "Vetted Helpdesk Seat PH",
                    "Remote Care Ownership",
                    "Staffing Not Gig Support",
                    "Proof in Dedicated CS",
                    "Ticket Seat From PH",
                    "Chat Email Seat Dedicated",
                    "Request Dedicated Support",
                ),
                lambda m: D(
                    "Outsource support with a dedicated Philippines seat — not rotating agents.",
                    "Proof is continuity: one vetted support seat you interview first.",
                    f"Built for {m['employers']} who need accountable offshore customer care.",
                    "Partner-led model. Response-time and CSAT goals set after we talk.",
                ),
            'dedicated',
            'cs',
        ),
    }

    out['hr'] = {
        'Human_Resources_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist HR Assistants",
                    "Vetted People Ops Finalists",
                    "HR Hire Shortlist Path",
                    "Recruit HR Then Interview",
                    "PH HR Screening Path",
                    "Skip Freelance HR Gigs",
                    "HR Role Brief to List",
                    "Get HR Candidates Ready",
                    "Employer HR Hire Path",
                    "Screened Onboarding Help",
                    "People Ops Hire Pipeline",
                    "HR Seat Shortlist",
                    "Staffing Pipeline for HR",
                    "Interview-Ready HR Staff",
                    "Ask for HR Shortlist",
                ),
                lambda m: D(
                    "Need HR support? We recruit and screen Philippines people-ops talent first.",
                    "Shortlist-first: you interview; we source and vet HR admin finalists.",
                    "A clear employer hire path for HR support — you interview the shortlist.",
                    "Tell us the HR seat. Review vetted candidates before you hire.",
                ),
            'shortlist',
            'hr',
        ),
        'Human_Resources_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH HR Seat",
                    "Same HR Admin Daily",
                    "Accountable People Ops",
                    "Philippines HR Continuity",
                    "Not Freelance HR Tasks",
                    "Offshore HR Ownership",
                    "HR Seat You Can Keep",
                    "Interview HR Then Place",
                    "Vetted People Ops Seat",
                    "Remote HR Ownership",
                    "Staffing Not Gig HR Apps",
                    "Proof in Dedicated HR",
                    "Onboarding Seat From PH",
                    "Payroll Admin Dedicated",
                    "Request Dedicated HR",
                ),
                lambda m: D(
                    "Outsource HR admin with a dedicated Philippines seat — not task gigs.",
                    "Proof is continuity: one vetted HR seat you interview before placement.",
                    f"Built for {m['employers']} needing accountable offshore people-ops capacity.",
                    "Partner-led model. Policy control stays with you — terms set in follow-up.",
                ),
            'dedicated',
            'hr',
        ),
    }

    out['recruitment'] = {
        'Recruitment_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Recruiting Ops",
                    "Vetted TA Finalists",
                    "Recruiting Hire Shortlist",
                    "Recruit TA Then Interview",
                    "PH Sourcer Screening",
                    "Skip Freelance Recruiters",
                    "TA Role Brief to List",
                    "Get Recruiting Finalists",
                    "Employer TA Hire Path",
                    "Screened Screening Support",
                    "Sourcing Hire Pipeline",
                    "TA Seat Shortlist",
                    "Staffing Pipeline for TA",
                    "Interview-Ready TA Staff",
                    "Ask for TA Shortlist",
                ),
                lambda m: D(
                    "Need recruiting support? We recruit and screen Philippines TA talent first.",
                    "Shortlist-first: you interview; we source and vet recruiting ops finalists.",
                    "Employer-only path for recruiting ops — you interview vetted finalists.",
                    "Tell us the TA seat. Review vetted candidates before you hire.",
                ),
            'shortlist',
            'ta',
        ),
        'Recruitment_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH TA Seat",
                    "Same Sourcer Daily",
                    "Accountable Recruiting Ops",
                    "Philippines TA Continuity",
                    "Not Gig Recruiting Apps",
                    "Offshore TA Ownership",
                    "TA Seat You Can Keep",
                    "Interview TA Then Place",
                    "Vetted Recruiting Seat",
                    "Remote TA Ownership",
                    "Staffing Not Job Boards",
                    "Proof in Dedicated TA",
                    "Sourcing Seat From PH",
                    "Screening Ops Dedicated",
                    "Request Dedicated TA",
                ),
                lambda m: D(
                    "Outsource recruiting ops with a dedicated Philippines seat — not gig apps.",
                    "Proof is continuity: one vetted TA seat you interview before placement.",
                    f"Built for {m['employers']} needing accountable offshore recruiting capacity.",
                    "Partner-led model. You keep hiring decisions — fill targets set in follow-up.",
                ),
            'dedicated',
            'ta',
        ),
    }

    out['sales'] = {
        'Sales_Hire_PH': (
            'C_speed',
                lambda m: H(
                    "Shortlist Lead Gen Talent",
                    "Vetted Sales Finalists",
                    "Lead Gen Hire Shortlist",
                    "Recruit Sales Then Interview",
                    "PH Setter Screening",
                    "Skip Freelance Lead Lists",
                    "Sales Role to Shortlist",
                    "Get Pipeline Finalists",
                    "Employer Sales Hire Path",
                    "Screened Appointment Setters",
                    "Outbound Hire Pipeline",
                    "Sales Seat Shortlist",
                    "Staffing Pipeline Sales",
                    "Interview-Ready Setters",
                    "Ask for Sales Shortlist",
                ),
                lambda m: D(
                    "Need sales support? We recruit and screen Philippines lead-gen talent first.",
                    "Shortlist-first: you interview; we source and vet setters and sales VAs.",
                    "Pipeline and meeting volume are confirmed in follow-up, not ad promises.",
                    "Tell us the sales seat. Review vetted finalists before you hire.",
                ),
            'shortlist',
            'sales',
        ),
        'Sales_Outsource_PH': (
            'C_proof',
                lambda m: H(
                    "Dedicated PH Sales Seat",
                    "Same Setter Every Day",
                    "Accountable Lead Gen Seat",
                    "Philippines Sales Continuity",
                    "Not Gig Outbound Apps",
                    "Offshore Pipeline Ownership",
                    "Sales Seat You Can Keep",
                    "Interview Setter Then Place",
                    "Vetted Lead Gen Seat PH",
                    "Remote Outbound Ownership",
                    "Staffing Not List Markets",
                    "Proof in Dedicated Sales",
                    "Prospecting Seat From PH",
                    "Appointment Seat Dedicated",
                    "Request Dedicated Sales",
                ),
                lambda m: D(
                    "Outsource lead gen with a dedicated Philippines seat — not gig list work.",
                    "Proof is continuity: one vetted sales seat you interview before placement.",
                    f"Built for {m['employers']} who need accountable offshore outbound capacity.",
                    "Partner-led model. Appointment and revenue goals set after we talk.",
                ),
            'dedicated',
            'sales',
        ),
    }

    return out


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
                    "Employer Hiring Path",
                    "Marketing Ops Assistant",
                    "Staffing Partner Model",
                    f"Built for {m['sme']}",
                    "Ongoing Marketing Capacity",
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill digital marketing roles with vetted Philippines specialists.",
                    f"Support campaigns, content ops, and reporting for your {m['business']}.",
                    "Staffing partner workflow: shortlist, interview, then dedicated hire support.",
                    f"We {m['specialize']} in remote marketing hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill social media roles with vetted Philippines specialists.",
                    "Coverage for scheduling, community replies, and content workflows.",
                    f"Staffing support for {m['business']} social channels that need consistency.",
                    f"We {m['specialize']} in remote social media hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill accounting roles with vetted Philippines specialists.",
                    "Day-to-day AP/AR workflows and accounting ops with dedicated seats.",
                    f"Staffing support shaped for your {m['business']} finance stack.",
                    f"We {m['specialize']} in remote accounting hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill bookkeeping roles with vetted Philippines specialists.",
                    "Support for categorisation, reconciliations, and weekly books rhythm."
                    if m["tag"] == "AU"
                    else "Support for categorization, reconciliations, and weekly books rhythm.",
                    f"Staffing support shaped for your {m['business']} books stack.",
                    f"We {m['specialize']} in remote bookkeeping hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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

    # ---- administration (EA / admin only — generic VA RSAs live on CORE) ----
    cat["administration"] = {
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill executive assistant roles with vetted Philippines specialists.",
                    "Support for calendar control, coordination, and executive follow-through.",
                    f"Staffing support shaped for leaders in your {m['business']}.",
                    f"We {m['specialize']} in remote EA hires for employers.",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill customer service roles with vetted Philippines specialists.",
                    "Coverage for inbox, chat, and customer care workflows.",
                    f"Staffing support shaped for your {m['business']} support queue.",
                    f"We {m['specialize']} in remote support hires for employers.",
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
                    "Start Hiring Request",
                ),
                lambda m: D(
                    "Outsource customer service to dedicated Philippines specialists.",
                    "Keep quality standards while we recruit, vet, and support the seat.",
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
                    "Outsource This Role PH",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill HR assistant roles with vetted Philippines specialists.",
                    "Support for coordination, documentation, onboarding, and payroll admin.",
                    f"Staffing support shaped for your {m['business']} people ops.",
                    f"We {m['specialize']} in remote HR hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill recruitment assistant roles with vetted Philippines specialists.",
                    "Support for sourcing coordination, screening support, and TA ops.",
                    f"Staffing support shaped for your {m['business']} hiring pipeline.",
                    f"We {m['specialize']} in remote recruiting hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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
                    "Tell Us Who You Need",
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
                    "Request Hiring Shortlist",
                ),
                lambda m: D(
                    "Fill sales support roles with vetted Philippines specialists.",
                    "Coverage for prospecting support, list work, and appointment setting.",
                    f"Staffing support shaped for your {m['business']} pipeline.",
                    f"We {m['specialize']} in remote sales hires for employers.",
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
                    "Start Hiring Request",
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
                    "Outsource This Role PH",
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

    # Append third unique RSA (proof/speed or dedicated-seat) per main AG
    for role, ag_map in _third_rsa_angles().items():
        for ag, entry in ag_map.items():
            if ag not in cat[role]:
                raise ValueError(f"third RSA AG missing from catalog: {role}/{ag}")
            if len(cat[role][ag]) != 2:
                raise ValueError(
                    f"expected 2 RSAs before third append: {role}/{ag} has {len(cat[role][ag])}"
                )
            cat[role][ag].append(entry)

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
            "Hire PH Role Staff",
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
            "Hire PH Role Staff",
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


def iter_role_ags(role: str) -> list[str]:
    return list(EXACT_BY_AG[role].keys())


def roles_tier(role: str) -> str:
    if role in PRIMARY_ROLE_KEYS:
        return "primary"
    if role == ADMIN_ROLE_KEY:
        return "admin"
    if role in CONTROLLED_ROLE_KEYS:
        return "controlled"
    raise ValueError(f"unknown role tier: {role}")


def append_campaign_shell(
    rows: list[dict[str, str]],
    *,
    cname: str,
    loc: str,
    budget_ph: str,
    comment: str,
) -> None:
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
            "Maximum CPC bid limit": "[APPROVAL_MAX_CPC]",
            "Comment": comment,
        }
    )
    rows.append(r)


def append_negatives_assets(
    rows: list[dict[str, str]],
    *,
    cname: str,
    sitelinks: list[tuple[str, str, str, str]],
) -> None:
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
                "Keyword": neg,
                "Criterion Type": "Broad",
                "Negative": "True",
                "Comment": (
                    "VC-only curated Stage1 neg; NOT account shared / PM_* mega list; "
                    "repeated per campaign (Editor requirement)"
                ),
            }
        )
        rows.append(r)

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


def append_kw_rows(
    rows: list[dict[str, str]],
    *,
    cname: str,
    ag: str,
    exact: list[str],
    phrase: list[str],
) -> None:
    seen_exact: set[str] = set()
    for kw in exact:
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
                "Keyword": kw,
                "Criterion Type": "Exact",
                "Keyword Status": "Paused",
                "Comment": "v6 Exact — ST evidence + employer long-tail",
            }
        )
        rows.append(r)

    seen_phrase: set[str] = set()
    for kw in phrase:
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
                "Keyword": kw,
                "Criterion Type": "Phrase",
                "Keyword Status": "Paused",
                "Comment": "v6 Phrase — discovery from converting ST clusters",
            }
        )
        rows.append(r)


def append_ad_group(
    rows: list[dict[str, str]],
    *,
    cname: str,
    ag: str,
    comment: str,
) -> None:
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
            "Comment": comment,
        }
    )
    rows.append(r)


def append_rsa(
    rows: list[dict[str, str]],
    *,
    cname: str,
    ag: str,
    final: str,
    headlines: list[str],
    descs: list[str],
    p1: str,
    p2: str,
    comment: str,
) -> None:
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
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": final,
            "Path 1": p1,
            "Path 2": p2,
            "Comment": comment,
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    rows.append(r)


def core_rsa(mkt: str, angle: str) -> tuple[list[str], list[str], str, str]:
    """angle: hire | hire_b | hire_c | offshore | offshore_b | offshore_c — full 15/4."""
    m = market_bits(mkt)
    if angle == "hire":
        headlines = [
            "Hire Virtual Assistant PH",
            "Hire Filipino VA",
            f"{m['tag']} Employer VA Hire",
            "Philippines VA Staffing",
            "Dedicated Remote VA",
            "Vetted VA Shortlist",
            "Interview Before Hire",
            "Not Gig Platform VA",
            "How to Hire a VA",
            "Core VA Employer Path",
            "Hire PH Role Staff",
            "Remote Admin Capacity",
            "Clear Employer Path",
            "Staffing Partner Hire",
            "{KeyWord:Hire Virtual Assistant}",
        ]
        descs = [
            f"Hire dedicated Philippines VAs for your {m['business']}.",
            "Tell us who you need. We recruit and screen — you interview the shortlist.",
            "Employer path only. Form inquiry is not a job order or placement.",
            "Staffing partner for established businesses — not DIY training or job ads.",
        ]
        return headlines, descs, "hire", "va"
    if angle == "hire_b":
        headlines = [
            "Looking for a VA?",
            "VA for Hire Philippines",
            "Virtual Assistant Agency",
            f"{m['tag']} VA Hiring Path",
            "Filipino VA for Business",
            "You Interview Finalists",
            "Dedicated Not Freelance",
            "VA Services for SMBs",
            "Hire Remote VA Seat",
            "Employer Hiring Only",
            "Virtual Staffing Partner",
            "Not a Job Board VA",
            "Scale Admin Bandwidth",
            "Request Hiring Shortlist",
            "{KeyWord:Hire Filipino VA}",
        ]
        descs = [
            f"Match hire-VA searches to vetted Philippines talent for {m['employers']}.",
            "We shortlist. You interview. Dedicated seat — not marketplace task work.",
            "Employer hire path for dedicated VA seats — not marketplace task work.",
            "Tell us the role. We recruit and vet. You decide who joins.",
        ]
        return headlines, descs, "va", "hire"
    if angle == "hire_c":
        headlines = [
            "How to Hire a VA Fast",
            "VA Shortlist for Employers",
            "Screened Filipino Finalists",
            f"{m['tag']} Hire Path Speed",
            "Recruit Vet Then Interview",
            "Skip Job Board Searching",
            "Get VA Candidates Ready",
            "Staffing Pipeline Hire",
            "Role Brief to Shortlist",
            "Employer Shortlist First",
            "Vetted Remote VA Seats",
            "Not DIY VA Hiring",
            "Dedicated Hire Support",
            "Clear Next Hire Step",
            "{KeyWord:How to Hire a VA}",
        ]
        descs = [
            f"Need a VA for your {m['business']}? We recruit and screen — you interview.",
            "Shortlist-first hiring: tell us the role, review vetted Philippines finalists.",
                    "Speed comes from a staffing pipeline — timelines confirmed in follow-up.",
            "Employer path only. Inquiry accepted is not a job order or placement.",
        ]
        return headlines, descs, "shortlist", "va"

    if angle == "offshore":
        headlines = [
            "Offshore VA Philippines",
            "Philippines Remote Staff",
            "Outsource VA to PH",
            f"{m['tag']} Offshore Staffing",
            "Dedicated Offshore Seat",
            "Not Freelance Offshore",
            "Vetted PH Remote Team",
            "Hire Offshore Capacity",
            "Philippines Staff Partner",
            "Core Offshore Hire Path",
            "Remote Ops From PH",
            "Employer Offshore Path",
            "Interview PH Shortlist",
            "Staff Not Marketplace",
            "{KeyWord:Offshore Virtual Assistant}",
        ]
        descs = [
            f"Philippines offshore staffing for {m['employers']} needing dedicated seats.",
            "Outsource the role to a vetted Philippines teammate — you keep hire authority.",
            "Employer hire path for dedicated offshore seats — not freelance gigs.",
            "Tell us the role. We shortlist. You decide who joins your business.",
        ]
        return headlines, descs, "offshore", "ph"
    if angle == "offshore_b":
        headlines = [
            "Filipino Virtual Assistant",
            "VA Philippines Staffing",
            "Philippines VA Company",
            f"{m['tag']} PH Remote Hire",
            "Offshore VA Partner",
            "Virtual Staff Philippines",
            "Dedicated PH VA Seat",
            "Outsource Admin to PH",
            "Not Gig Offshore VA",
            "Vetted Filipino Talent",
            "Remote Staff From PH",
            "Employer PH Hire Path",
            "Interview Before Place",
            "Staffing Not Freelance",
            "{KeyWord:Philippines Virtual Assistant}",
        ]
        descs = [
            f"Philippines VA and remote staff for {m['business']} ops capacity.",
            "Filipino talent shortlist — you interview; we recruit, vet, and support.",
            "Offshore staffing partner model. Not Upwork. Not a job board.",
            "Employer inquiries only. Inquiry accepted ≠ job order or placement.",
        ]
        return headlines, descs, "ph", "va"
    if angle == "offshore_c":
        headlines = [
            "Dedicated PH VA Seat",
            "Same VA Every Workday",
            "Philippines Seat Not Gig",
            f"{m['tag']} Offshore Proof Path",
            "Accountable Remote Staff",
            "Interview Then Place PH",
            "Vetted Offshore Teammate",
            "Not Rotating Freelancers",
            "Offshore With Continuity",
            "PH Staff You Can Keep",
            "Remote Ops Ownership",
            "Staffing Seat Evidence",
            "Outsource Role Dedicated",
            "Employer Controls Hire",
            "{KeyWord:Dedicated Virtual Assistant}",
        ]
        descs = [
            f"Philippines offshore seats for {m['employers']} who want one dedicated teammate.",
            "Proof is continuity: a vetted seat you interview — not marketplace rotation.",
            "We recruit and support. You keep hire authority before placement.",
            "Employer hire path for one dedicated teammate — not marketplace rotation.",
        ]
        return headlines, descs, "dedicated", "ph"

    raise ValueError(f"unknown core RSA angle: {angle}")


def build_core(
    rows: list[dict[str, str]],
    *,
    mkt: str,
    loc: str,
    budget_ph: str,
    base_url: str,
) -> None:
    """VC_*_S_CORE — high-intent VA / hire / PH-offshore (~60% budget).

    Final URL = market employer home (/us or /au) — NOT administrative-support.
    Category admin traffic lives under ROLES Administration_EA_PH.
    """
    core_final = base_url.rstrip("/")  # …/us or …/au
    cname = f"VC_{mkt}_S_CORE"
    append_campaign_shell(
        rows,
        cname=cname,
        loc=loc,
        budget_ph=budget_ph,
        comment=(
            "Stage1 v7 CORE (~60%); Max Clicks; Search only; Exact+Phrase; "
            "Paused; Brand deferred; Final URL=market home"
        ),
    )

    for ag, angles in (
        ("Hire_VA_PH", ("hire", "hire_b", "hire_c")),
        ("Offshore_VA_PH", ("offshore", "offshore_b", "offshore_c")),
    ):
        append_ad_group(
            rows,
            cname=cname,
            ag=ag,
            comment=f"CORE AG — {ag}; Final URL=market home",
        )
        append_kw_rows(
            rows,
            cname=cname,
            ag=ag,
            exact=CORE_EXACT_BY_AG[ag],
            phrase=CORE_PHRASE_BY_AG[ag],
        )
        for angle in angles:
            hs, ds, p1, p2 = core_rsa(mkt, angle)
            validate_rsa(hs, ds, f"{mkt}/core/{ag}/{angle}")
            append_rsa(
                rows,
                cname=cname,
                ag=ag,
                final=core_final,
                headlines=hs,
                descs=ds,
                p1=p1,
                p2=p2,
                comment=f"Core RSA {angle}; Final URL=market home",
            )

    append_negatives_assets(
        rows,
        cname=cname,
        sitelinks=[
            (
                "Tell Us Who You Need",
                "Employer hiring path",
                "Form for businesses",
                f"{core_final}#gate",
            ),
            (
                "How Hiring Works",
                "Recruit, vet, shortlist",
                "You interview talent",
                core_final,
            ),
            (
                "Admin Support Hire",
                "EA / admin category LP",
                "Role-specific landing",
                f"{core_final}/administrative-support",
            ),
            (
                f"{mkt} Employer Home",
                "Generic Core landing",
                "Not WordPress homepage",
                core_final,
            ),
        ],
    )


def build_roles(
    rows: list[dict[str, str]],
    *,
    mkt: str,
    loc: str,
    budget_ph: str,
    base_url: str,
) -> None:
    """VC_*_S_ROLES — Digital · Social · Admin · Controlled (~40% budget)."""
    cname = f"VC_{mkt}_S_ROLES"
    mbits = market_bits(mkt)
    append_campaign_shell(
        rows,
        cname=cname,
        loc=loc,
        budget_ph=budget_ph,
        comment=(
            "Stage1 v6 ROLES (~40%); AGs Digital·Social·Admin·Controlled; "
            "category Final URLs; Max Clicks; Paused; Brand deferred"
        ),
    )

    role_order = (
        list(PRIMARY_ROLE_KEYS)
        + [ADMIN_ROLE_KEY]
        + list(CONTROLLED_ROLE_KEYS)
    )

    for role in role_order:
        tier = roles_tier(role)
        slug = ROLE_CATEGORY_SLUG[role]
        final = f"{base_url}/{slug}"
        for ag in iter_role_ags(role):
            append_ad_group(
                rows,
                cname=cname,
                ag=ag,
                comment=f"ROLES {tier} — {ag}; category={slug}",
            )
            append_kw_rows(
                rows,
                cname=cname,
                ag=ag,
                exact=EXACT_BY_AG[role][ag],
                phrase=PHRASE_BY_AG[role][ag],
            )
            for suffix, hl_fn, desc_fn, p1, p2 in RSA_CATALOG[role][ag]:
                hs = hl_fn(mbits)
                ds = desc_fn(mbits)
                validate_rsa(hs, ds, f"{mkt}/{role}/{ag}/{suffix}")
                append_rsa(
                    rows,
                    cname=cname,
                    ag=ag,
                    final=final,
                    headlines=hs,
                    descs=ds,
                    p1=p1,
                    p2=p2,
                    comment=(
                        f"RSA angle {suffix}; full 15/4; tier={tier}; "
                        f"role={ROLE_LABEL[role]}; no invented pricing"
                    ),
                )

        if role == ADMIN_ROLE_KEY:
            city_ag = "Admin_City_Test"
            append_ad_group(
                rows,
                cname=cname,
                ag=city_ag,
                comment="LIGHT city Phrase + location-insertion RSA (Admin tier)",
            )
            city_kws = CITY_PHRASE_US if mkt == "US" else CITY_PHRASE_AU
            append_kw_rows(
                rows,
                cname=cname,
                ag=city_ag,
                exact=[],
                phrase=city_kws,
            )
            hs, ds, p1, p2 = city_rsa(mkt)
            append_rsa(
                rows,
                cname=cname,
                ag=city_ag,
                final=final,
                headlines=hs,
                descs=ds,
                p1=p1,
                p2=p2,
                comment="Location insertion test RSA; full 15/4",
            )

    # Campaign-level sitelinks span primary role LPs
    append_negatives_assets(
        rows,
        cname=cname,
        sitelinks=[
            (
                "Tell Us Who You Need",
                "Employer hiring path",
                "Form for businesses",
                f"{base_url}/administrative-support#gate",
            ),
            (
                "Digital Marketing Hire",
                "Philippines marketing staff",
                "Category landing page",
                f"{base_url}/digital-marketing",
            ),
            (
                "Social Media Hire",
                "Philippines SMM staff",
                "Category landing page",
                f"{base_url}/social-media",
            ),
            (
                "Bookkeeping Hire",
                "Philippines books staff",
                "Category landing page",
                f"{base_url}/bookkeeping",
            ),
        ],
    )


def build() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for mkt, loc, budget_ph in (
        ("US", "United States", "[APPROVAL_DAILY_BUDGET_USD]"),
        ("AU", "Australia", "[APPROVAL_DAILY_BUDGET_AUD]"),
    ):
        base_url = f"https://vision-three-alpha.vercel.app/{mkt.lower()}"
        build_core(
            rows, mkt=mkt, loc=loc, budget_ph=budget_ph, base_url=base_url
        )
        build_roles(
            rows, mkt=mkt, loc=loc, budget_ph=budget_ph, base_url=base_url
        )

    apply_budget_cpc_defaults(rows)
    stamp_account_ids(rows)
    return rows


def market_from_campaign(cname: str) -> str | None:
    if "_US_" in cname:
        return "US"
    if "_AU_" in cname:
        return "AU"
    return None


def stamp_account_ids(rows: list[dict[str, str]]) -> None:
    """Stamp Editor Account (Customer ID) on every row from campaign market."""
    for r in rows:
        mkt = market_from_campaign(r.get("Campaign") or "")
        if not mkt:
            raise SystemExit(
                f"Cannot stamp Account — unknown market for row: "
                f"{r.get('Row Type')} / {r.get('Campaign')!r}"
            )
        r["Account"] = ACCOUNT_IDS[mkt]


def apply_budget_cpc_defaults(rows: list[dict[str, str]]) -> None:
    """Fill Budget + campaign-only Maximum CPC bid limit (Maximize Clicks)."""
    for r in rows:
        cname = r.get("Campaign") or ""
        mkt = market_from_campaign(cname)
        if not mkt:
            continue
        if r.get("Row Type") != "Campaign":
            # Maximize Clicks bid limit + URL options live on campaign only.
            r["Maximum CPC bid limit"] = ""
            r["Tracking template"] = ""
            r["Final URL suffix"] = ""
            continue
        r["Maximum CPC bid limit"] = MAX_CPC[mkt]
        budgets = BUDGET_DAILY[mkt]
        if cname.endswith("_S_CORE"):
            r["Budget"] = budgets["core"]
        elif cname.endswith("_S_ROLES"):
            r["Budget"] = budgets["roles"]
        elif r.get("Budget", "").startswith("[APPROVAL_"):
            r["Budget"] = budgets["roles"]


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def broad_negative_blocks(query: str, negative: str) -> bool:
    """Google Broad negative: query blocked if it contains every negative token."""
    q = set(_tokens(query))
    n = _tokens(negative)
    return bool(n) and all(t in q for t in n)


def assert_employer_research_canaries(active_broad_negs: set[str]) -> None:
    """Fail if campaign Broad negatives would suppress employer research queries."""
    for query in EMPLOYER_RESEARCH_CANARIES:
        blockers = sorted(
            neg for neg in active_broad_negs if broad_negative_blocks(query, neg)
        )
        if blockers:
            raise SystemExit(
                f"Employer-research canary blocked by active Broad negative(s) "
                f"{blockers}: {query!r}"
            )


# Enable-order tiers (review manifests only — CSV Status stays Paused).
# 1A = Exact + PH geo + hire/VA/outsource strength (not bare "philippines" heads)
# 1B = PH-shaped Phrase, or PH Exact without hire/VA/outsource strength
# 2  = Roles category Exact/Phrase without PH geo
# 3  = generic Core heads (no PH geo)
_PH_GEO_RE = re.compile(
    r"\b(philippines|philippine|filipino|filipina|offshore|overseas)\b|\bph\b",
    re.I,
)
_STRONG_PH_INTENT_RE = re.compile(
    r"\b("
    r"hire|hiring|"
    r"outsource|outsourcing|"
    r"virtual assistants?|virtual staff(?:ing)?|"
    r"vas?|"
    r"staffing"
    r")\b",
    re.I,
)


def classify_enable_tier(keyword: str, match_type: str, campaign: str) -> str:
    kw = keyword.strip()
    mt = (match_type or "").strip()
    ph = bool(_PH_GEO_RE.search(kw))
    strong = bool(_STRONG_PH_INTENT_RE.search(kw))
    is_core = campaign.endswith("_S_CORE")
    if ph and mt == "Exact" and strong:
        return "1A"
    if ph:
        return "1B"
    if is_core:
        return "3"
    return "2"


MANIFEST_FIELDS = [
    "Account",
    "Campaign",
    "Ad Group",
    "Keyword",
    "Match Type",
    "Tier",
    "Final URL",
    "Status",
]

OUT_MANIFEST_US = ROOT / "ads-launch" / "phase1-enable-manifest-us.csv"
OUT_MANIFEST_AU = ROOT / "ads-launch" / "phase1-enable-manifest-au.csv"
PHASE1_REVIEW = ROOT / "ads-launch" / "PHASE1-REVIEW.md"


def qa(rows: list[dict[str, str]]) -> None:
    kinds = Counter(r["Row Type"] for r in rows)
    print("Row types:", dict(kinds))
    camps = sorted({r["Campaign"] for r in rows if r["Campaign"]})
    print("Campaigns:", len(camps))
    for c in camps:
        print(" ", c)

    leftover = [
        (r.get("Row Type"), r.get("Campaign"), r.get("Budget"), r.get("Maximum CPC bid limit"))
        for r in rows
        if "[APPROVAL_" in (r.get("Budget") or "")
        or "[APPROVAL_" in (r.get("Maximum CPC bid limit") or "")
    ]
    if leftover:
        raise SystemExit(f"APPROVAL placeholders remain: {leftover[:5]}")
    camp_budgets = {
        r["Campaign"]: r["Budget"]
        for r in rows
        if r["Row Type"] == "Campaign"
    }
    print("Daily budgets:", camp_budgets)
    print("Maximum CPC bid limit US/AU:", MAX_CPC)

    for r in rows:
        cap = (r.get("Maximum CPC bid limit") or "").strip()
        if r["Row Type"] == "Campaign":
            mkt = market_from_campaign(r["Campaign"])
            if not mkt or cap != MAX_CPC[mkt]:
                raise SystemExit(
                    f"Campaign {r['Campaign']} bad Maximum CPC bid limit={cap!r}"
                )
        elif cap:
            raise SystemExit(
                f"Non-campaign {r['Row Type']} has Maximum CPC bid limit={cap!r}"
            )

    if "{_campaign}" in SUFFIX or "{_adgroup}" in SUFFIX:
        raise SystemExit("Undefined custom tracking params in SUFFIX")
    if "{campaignid}" not in SUFFIX or "{adgroupid}" not in SUFFIX:
        raise SystemExit("SUFFIX missing ValueTrack campaignid/adgroupid")
    for term in NEGATIVE_REVIEW_HOLDOUT:
        if any(
            r.get("Keyword", "").lower() == term.lower()
            and r.get("Row Type") == "Campaign negative keyword"
            for r in rows
        ):
            raise SystemExit(f"Holdout negative still in import: {term}")
    print("Negative holdouts (not imported):", len(NEGATIVE_REVIEW_HOLDOUT))

    active_broad_negs = {
        r["Keyword"].lower()
        for r in rows
        if r["Row Type"] == "Campaign negative keyword"
        and (r.get("Criterion Type") or "") == "Broad"
    }
    # Holdout terms must never appear in import CSVs (any row Keyword).
    import_keywords = {
        (r.get("Keyword") or "").lower()
        for r in rows
        if (r.get("Keyword") or "").strip()
    }
    for term in NEGATIVE_REVIEW_HOLDOUT:
        if term.lower() in import_keywords:
            raise SystemExit(f"Holdout term leaked into import Keyword column: {term}")
    assert_employer_research_canaries(active_broad_negs)
    print(
        "Employer-research canaries OK:",
        len(EMPLOYER_RESEARCH_CANARIES),
        "queries vs",
        len(active_broad_negs),
        "unique Broad negs",
    )

    ads = [r for r in rows if r["Row Type"] == "Ad"]
    for r in ads:
        hs = [r[f"Headline {i}"] for i in range(1, 16)]
        ds = [r[f"Description {i}"] for i in range(1, 5)]
        if any(not h for h in hs) or any(not d for d in ds):
            raise SystemExit(f"BLANK RSA SLOT: {r['Campaign']} / {r['Ad Group']}")
        validate_rsa(hs, ds, f"{r['Campaign']}/{r['Ad Group']}")

    # Main AGs: exactly 3 unique full RSAs; city-test may stay 1–2
    from collections import defaultdict as _dd
    ag_rsa = _dd(int)
    for r in ads:
        ag_rsa[(r["Campaign"], r["Ad Group"])] += 1
    for (camp, ag), n in sorted(ag_rsa.items()):
        if "City" in ag:
            if n < 1 or n > 2:
                raise SystemExit(f"City AG RSA count {n} not in 1–2: {camp}/{ag}")
        elif n != 3:
            raise SystemExit(f"Main AG needs exactly 3 RSAs, got {n}: {camp}/{ag}")

    us_ads = [
        r
        for r in ads
        if r["Campaign"].startswith("VC_US_") and "City" not in r["Ad Group"]
    ]
    freq = Counter()
    for r in us_ads:
        hs = {
            h
            for h in (r[f"Headline {i}"] for i in range(1, 16))
            if not h.startswith("{")
        }
        for h in hs:
            freq[h] += 1
    # Fewer campaigns → shared CTAs recur more; flag only extreme clones.
    spam = [(h, c) for h, c in freq.items() if c > 18]
    if spam:
        raise SystemExit(f"Boilerplate headline spam across RSAs: {spam[:8]}")

    expected = {
        "VC_US_S_CORE",
        "VC_US_S_ROLES",
        "VC_AU_S_CORE",
        "VC_AU_S_ROLES",
    }
    if set(camps) != expected:
        raise SystemExit(f"Expected {sorted(expected)}, got {camps}")

    for c in camps:
        kws = [
            r
            for r in rows
            if r["Campaign"] == c
            and r["Row Type"] == "Keyword"
            and r["Negative"] != "True"
        ]
        ads_c = [r for r in rows if r["Campaign"] == c and r["Row Type"] == "Ad"]
        if not kws or not ads_c:
            raise SystemExit(f"EMPTY SHELL: {c} kws={len(kws)} ads={len(ads_c)}")
        ags = {r["Ad Group"] for r in kws}
        if c.endswith("_S_CORE") and len(ags) < 2:
            raise SystemExit(f"CORE needs ≥2 AGs: {c} ags={ags}")
        if c.endswith("_S_ROLES") and len(ags) < 4:
            raise SystemExit(f"ROLES needs Digital·Social·Admin·Controlled AGs: {c}={ags}")

    # Budget share check (~60/40)
    for mkt, cur in (("US", "$"), ("AU", "A$")):
        core_b = int(camp_budgets[f"VC_{mkt}_S_CORE"])
        roles_b = int(camp_budgets[f"VC_{mkt}_S_ROLES"])
        total = core_b + roles_b
        core_pct = core_b / total
        if not (0.55 <= core_pct <= 0.65):
            raise SystemExit(
                f"{mkt} Core share {core_pct:.0%} not ~60% ({cur}{core_b}+{cur}{roles_b})"
            )

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
    if re.search(r"\bconsult\b|book a demo|schedule a demo", blob, re.I):
        raise SystemExit("Consult/demo language leaked into RSA")

    # Public-copy lint: RSA Headline/Description fields only (not Editor comments).
    # Banned list shared with vision/lib/public-copy-lint.test.ts
    banned_path = Path(__file__).resolve().parent.parent / "vision" / "lib" / "public-copy-banned.json"
    if banned_path.is_file():
        banned_phrases = json.loads(banned_path.read_text(encoding="utf-8")).get("phrases") or []
        blob_l = blob.lower()
        for phrase in banned_phrases:
            if phrase and phrase.lower() in blob_l:
                raise SystemExit(
                    f"Banned public-copy phrase in RSA Headline/Description: {phrase!r}"
                )
    else:
        raise SystemExit(f"Missing public-copy banned list: {banned_path}")

    mt = Counter(
        r["Criterion Type"]
        for r in rows
        if r["Row Type"] == "Keyword" and r["Negative"] != "True"
    )
    print("Positive match types:", dict(mt))
    if mt.get("Broad"):
        raise SystemExit("Positive Broad keywords not allowed")

    for r in ads:
        fu = r.get("Final URL") or ""
        camp = r.get("Campaign") or ""
        if "?role=" in fu:
            raise SystemExit(f"Legacy inert ?role= Final URL: {fu}")
        if "virtualcoworker.com" in fu.lower():
            raise SystemExit(f"WP Final URL leak: {fu}")
        if "/us" not in fu and "/au" not in fu:
            raise SystemExit(f"Final URL missing market path: {fu}")
        # CORE → market employer home; ROLES → category slug paths.
        is_core = camp.endswith("_S_CORE")
        path_only = fu.split("?", 1)[0].split("#", 1)[0].rstrip("/")
        ends_market_home = path_only.endswith("/us") or path_only.endswith("/au")
        if is_core and not ends_market_home:
            raise SystemExit(f"CORE Final URL must be market home (/us|/au): {fu}")
        if not is_core and ends_market_home:
            raise SystemExit(f"ROLES Final URL must be category path, not home: {fu}")
        if not is_core:
            known_slugs = (
                "digital-marketing",
                "social-media",
                "accounting",
                "bookkeeping",
                "administrative-support",
                "customer-service",
                "hr",
                "recruitment",
                "sales",
            )
            if not any(f"/{slug}" in path_only for slug in known_slugs):
                raise SystemExit(f"ROLES Final URL missing category slug: {fu}")
        if r["Tracking template"] not in ("", TRACK):
            raise SystemExit(
                f"Unexpected tracking template (want {{lpurl}} only): "
                f"{r['Tracking template']!r}"
            )
        if (
            r["Tracking template"] not in ("", TRACK)
            and "utm_source" in r["Tracking template"]
            and r.get("Final URL suffix")
            and "utm_source" in r["Final URL suffix"]
        ):
            raise SystemExit(f"Double UTM on {r['Campaign']}/{r['Ad Group']}")

    for r in rows:
        for col in ("Campaign Status", "Ad Group Status", "Keyword Status", "Ad Status"):
            st = r.get(col) or ""
            if st and st != "Paused":
                raise SystemExit(
                    f"Non-paused {col}={st} on {r['Row Type']} {r.get('Campaign')}"
                )

    # Account (Customer ID) required for USA+AU multi-account Editor import
    acct_counts: Counter[str] = Counter()
    for r in rows:
        acct = (r.get("Account") or "").strip()
        mkt = market_from_campaign(r.get("Campaign") or "")
        if not mkt:
            raise SystemExit(f"Row missing marketable Campaign: {r.get('Row Type')}")
        expected = ACCOUNT_IDS[mkt]
        if acct != expected:
            raise SystemExit(
                f"Bad Account={acct!r} for {r.get('Campaign')} "
                f"(expected {expected})"
            )
        acct_counts[acct] += 1
    if set(acct_counts) != set(ACCOUNT_IDS.values()):
        raise SystemExit(f"Account IDs incomplete: {dict(acct_counts)}")
    print("Account stamps:", dict(acct_counts))

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

    # Brand terms must not appear as Stage 1 positives (Brand deferred)
    for brand_kw in ("virtual coworker", "virtualcoworker"):
        if brand_kw in pos_blob:
            raise SystemExit(f"Brand keyword in Stage 1 package (deferred): {brand_kw}")

    negs = {
        r["Keyword"].lower()
        for r in rows
        if r["Row Type"] == "Campaign negative keyword"
    }
    if "hire" in negs or "hiring" in negs:
        raise SystemExit("hire/hiring must not be campaign negatives")

    # Isolation lock: no PM_* entities, no shared-list attach rows, tight negs only.
    forbidden_row_types = {
        "Campaign negative keyword list",
        "Negative keyword list",
        "Shared set",
        "Campaign shared set",
        "Audience",
        "Campaign audience",
        "Ad group audience",
    }
    for r in rows:
        if r["Row Type"] in forbidden_row_types:
            raise SystemExit(
                f"Isolation lock: forbidden Row Type in package: {r['Row Type']}"
            )
        camp = r.get("Campaign") or ""
        if camp.startswith("PM_"):
            raise SystemExit(f"Isolation lock: PM_* campaign leaked into package: {camp}")
        if not camp.startswith("VC_") and r["Row Type"] not in ("",):
            # Every entity row must belong to a VC_* campaign
            if r["Row Type"] and camp:
                raise SystemExit(
                    f"Isolation lock: non-VC campaign in package: {camp} ({r['Row Type']})"
                )
    if len(negs) > MAX_UNIQUE_NEGATIVES:
        raise SystemExit(
            f"Isolation lock: unique negatives {len(negs)} > cap {MAX_UNIQUE_NEGATIVES} "
            "(do not dump account mega lists into Stage 1)"
        )
    if len(NEGATIVES) > MAX_UNIQUE_NEGATIVES:
        raise SystemExit(
            f"NEGATIVES source list too large: {len(NEGATIVES)} > {MAX_UNIQUE_NEGATIVES}"
        )

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
    if len(dki_ads) < 8:
        raise SystemExit(f"DKI underused: only {len(dki_ads)} ads have KeyWord insertion")

    # lp_version stamp
    if f"lp_version={LP_VERSION}" not in SUFFIX:
        raise SystemExit(f"SUFFIX missing {LP_VERSION}")

    print(
        "QA OK — RSA ads:",
        len(ads),
        "positive KWs:",
        sum(mt.values()),
        "unique negs:",
        len(negs),
        "lp_version:",
        LP_VERSION,
    )


OUT_US = ROOT / "ads-launch" / "google-ads-editor-import-us.csv"
OUT_AU = ROOT / "ads-launch" / "google-ads-editor-import-au.csv"
OUT_MULTI = ROOT / "ads-launch" / "google-ads-editor-import-multi-account.csv"
PREFLIGHT = ROOT / "ads-launch" / "EDITOR-PREFLIGHT-REPORT.md"


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _final_url_by_ag(rows: list[dict[str, str]]) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for r in rows:
        if r["Row Type"] != "Ad":
            continue
        key = (r["Campaign"], r["Ad Group"])
        fu = (r.get("Final URL") or "").strip()
        if fu and key not in out:
            out[key] = fu
    return out


def build_enable_manifest_rows(rows: list[dict[str, str]], market: str) -> list[dict[str, str]]:
    """Review-only enable ladder rows (all Status=Paused)."""
    acct = ACCOUNT_IDS[market]
    finals = _final_url_by_ag(rows)
    manifest: list[dict[str, str]] = []
    for r in rows:
        if r["Row Type"] != "Keyword" or r.get("Negative") == "True":
            continue
        if r.get("Account") != acct:
            continue
        camp = r["Campaign"]
        ag = r["Ad Group"]
        kw = r["Keyword"]
        mt = r.get("Criterion Type") or ""
        tier = classify_enable_tier(kw, mt, camp)
        # Guard: bare philippines service heads must not land in 1A
        if tier == "1A" and not _STRONG_PH_INTENT_RE.search(kw):
            raise SystemExit(f"Tier 1A without strong intent: {kw!r}")
        manifest.append(
            {
                "Account": acct,
                "Campaign": camp,
                "Ad Group": ag,
                "Keyword": kw,
                "Match Type": mt,
                "Tier": tier,
                "Final URL": finals.get((camp, ag), ""),
                "Status": "Paused",
            }
        )
    # Stable review order: tier → campaign → AG → match → keyword
    tier_rank = {"1A": 0, "1B": 1, "2": 2, "3": 3}
    manifest.sort(
        key=lambda m: (
            tier_rank.get(m["Tier"], 9),
            m["Campaign"],
            m["Ad Group"],
            0 if m["Match Type"] == "Exact" else 1,
            m["Keyword"].lower(),
        )
    )
    return manifest


def write_manifest_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_phase1_review(
    us_rows: list[dict[str, str]],
    au_rows: list[dict[str, str]],
) -> None:
    from datetime import datetime, timezone

    def tier_counts(rows: list[dict[str, str]]) -> Counter[str]:
        return Counter(r["Tier"] for r in rows)

    us_c = tier_counts(us_rows)
    au_c = tier_counts(au_rows)
    lines = [
        "# Phase 1 enable review manifests",
        "",
        f"- Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "- Purpose: **review-only** enable ladder — not an Enabled import file",
        "- Every keyword Status = **Paused** (do not enable from these CSVs)",
        "- Source of enable order: `PHASED-ACTIVATION.md`",
        "",
        "## Tier definitions",
        "",
        "| Tier | Meaning |",
        "|------|---------|",
        "| **1A** | Strongest PH/Filipino/offshore long-tail **Exact** "
        "(hire / VA / outsource + PH geo). "
        "Not bare `philippines` service heads. |",
        "| **1B** | PH-shaped **Phrase**, or slightly broader PH **Exact** "
        "(geo + role/service without hire/VA/outsource strength). |",
        "| **2** | Broader category Exact/Phrase **without** PH geo (Roles). |",
        "| **3** | Generic Core heads later (no PH geo). |",
        "",
        "## Files",
        "",
        f"- `phase1-enable-manifest-us.csv` — {len(us_rows)} keywords "
        f"(Account `{ACCOUNT_IDS['US']}`)",
        f"- `phase1-enable-manifest-au.csv` — {len(au_rows)} keywords "
        f"(Account `{ACCOUNT_IDS['AU']}`)",
        "",
        "## Counts",
        "",
        "| Tier | US | AU |",
        "|------|----|----|",
    ]
    for tier in ("1A", "1B", "2", "3"):
        lines.append(f"| {tier} | {us_c.get(tier, 0)} | {au_c.get(tier, 0)} |")
    lines += [
        f"| **Total** | **{len(us_rows)}** | **{len(au_rows)}** |",
        "",
        "## Operator notes",
        "",
        "1. Review 1A first (US before AU), then 1B — still leave Status=Paused "
        "until TRAFFIC READY + explicit George Enable approval "
        "(Zoho/CRM is parallel, not a traffic gate).",
        "2. Bare Core heads are Tier **3** — later, not first.",
        "3. Generic `philippines` + service heads without hire/VA/outsource are "
        "**1B**, not 1A.",
        "4. Import/Post of the Editor package is separate; these manifests do not "
        "replace Editor import CSVs.",
        "",
    ]
    PHASE1_REVIEW.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_phase1_manifests(rows: list[dict[str, str]]) -> tuple[int, int]:
    us_m = build_enable_manifest_rows(rows, "US")
    au_m = build_enable_manifest_rows(rows, "AU")
    if any(r["Status"] != "Paused" for r in us_m + au_m):
        raise SystemExit("Phase1 manifest must keep Status=Paused")
    # Sanity: no Tier 1A that is only bare philippines + service (no strong intent)
    for r in us_m + au_m:
        if r["Tier"] == "1A" and r["Match Type"] != "Exact":
            raise SystemExit(f"Tier 1A must be Exact: {r}")
        if r["Final URL"] == "":
            raise SystemExit(
                f"Manifest missing Final URL for {r['Campaign']}/{r['Ad Group']}"
            )
    write_manifest_csv(OUT_MANIFEST_US, us_m)
    write_manifest_csv(OUT_MANIFEST_AU, au_m)
    write_phase1_review(us_m, au_m)
    print(
        "Phase1 manifests:",
        f"US {len(us_m)} (1A={sum(1 for r in us_m if r['Tier']=='1A')})",
        f"AU {len(au_m)} (1A={sum(1 for r in au_m if r['Tier']=='1A')})",
    )
    return len(us_m), len(au_m)


def write_preflight(rows: list[dict[str, str]]) -> None:
    from datetime import datetime, timezone

    kinds = Counter(r["Row Type"] for r in rows)
    camps = [r for r in rows if r["Row Type"] == "Campaign"]
    pos = [
        r
        for r in rows
        if r["Row Type"] == "Keyword" and r.get("Negative") != "True"
    ]
    negs = [r for r in rows if r["Row Type"] == "Campaign negative keyword"]
    us_rows = [r for r in rows if r["Account"] == ACCOUNT_IDS["US"]]
    au_rows = [r for r in rows if r["Account"] == ACCOUNT_IDS["AU"]]
    unique_negs = len({r["Keyword"].lower() for r in negs})
    lines = [
        "# Editor preflight report",
        "",
        f"- Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- LP version (suffix): `{LP_VERSION}` (unchanged)",
        f"- Package hygiene: Editor ValueTrack + campaign CPC cap + US/AU split",
        "",
        "## Operating rule (locked)",
        "",
        "**Old account = historical archive. New `VC_*` = isolated clean system.**",
        "",
        "- Leave old `PM_*` campaigns, shared mega negative lists, old Zoho/Zapier "
        "conversion actions, and historical reporting alone.",
        "- This package attaches **only** curated campaign-level negatives "
        f"(~{unique_negs} unique, cap {MAX_UNIQUE_NEGATIVES}) — **not** account shared / "
        "`PM_*` 3000+ dumps.",
        "- Do **not** attach account shared negative lists to `VC_*` after Import/Post.",
        "- Do **not** use audiences to restrict targeting for initial Search launch "
        "(Observation later; ignore customer-lifecycle warnings until Zoho/first-party data).",
        "- Import ≠ live. Every campaign stays **Paused**. No Enable from this package.",
        "",
        "## Verdict",
        "",
        "- **SAFE TO IMPORT FOR REVIEW** (local QA passed)",
        "- **IMPORT/POST/ENABLE NOT PERFORMED**",
        "- Import = draft on your computer. Post = upload to Google (still Paused).",
        "- Enable is a separate explicit decision after TRAFFIC READY + George approval "
        "(CRM READY / OPTIMIZATION READY are parallel — not traffic gates).",
        "",
        "## Files",
        "",
        "| File | Use |",
        "|------|-----|",
        f"| `google-ads-editor-import-us.csv` ({len(us_rows)} rows) | **Preferred** — import into USA `{ACCOUNT_IDS['US']}` only |",
        f"| `google-ads-editor-import-au.csv` ({len(au_rows)} rows) | **Preferred** — import into AU `{ACCOUNT_IDS['AU']}` only |",
        f"| `google-ads-editor-import.csv` / `-multi-account.csv` ({len(rows)} rows) | Manager multi-account only — every row has Account |",
        f"| `phase1-enable-manifest-us.csv` / `-au.csv` | **Review-only** enable ladder (tiers 1A/1B/2/3; all Paused) |",
        f"| `PHASE1-REVIEW.md` | Tier definitions + per-market counts |",
        "",
        "## Counts",
        "",
        f"- Campaigns: {kinds.get('Campaign', 0)} (all Paused)",
        f"- Ad groups: {kinds.get('Ad group', 0)}",
        f"- Positive keywords: {len(pos)}",
        f"- RSAs: {kinds.get('Ad', 0)}",
        f"- Active campaign negatives: {len(negs)} rows "
        f"({unique_negs} unique × 4 campaigns) — VC-only curated, not shared mega lists",
        f"- Commercial holdouts (not imported): {len(NEGATIVE_REVIEW_HOLDOUT)} "
        f"(includes pay rate / hourly rate / virtual assistant reviews + cost/pricing/"
        f"review research terms)",
        f"- Employer-research Broad canaries: {len(EMPLOYER_RESEARCH_CANARIES)} "
        f"(QA fails if active Broad negs would block them)",
        f"- Shared-list / audience / PM_* rows: **none** (isolation QA)",
        "",
        "## Budgets + bid caps (campaign only)",
        "",
    ]
    for c in camps:
        lines.append(
            f"- `{c['Campaign']}` · Account `{c['Account']}` · "
            f"Budget {c['Budget']}/day · Maximum CPC bid limit {c['Maximum CPC bid limit']} · "
            f"Maximize Clicks · Paused"
        )
    lines += [
        "",
        "## Tracking (UTMs)",
        "",
        f"- Tracking template (campaign): `{TRACK}`",
        f"- Final URL suffix (campaign): `{SUFFIX}`",
        "- No `{_campaign}` / `{_adgroup}` custom params",
        "",
        "## Conversion actions + campaign goals (after Post — Ads UI)",
        "",
        "Editor CSV does **not** fully express conversion goals. After Post, George sets "
        "these in Google Ads UI. Do **not** replace or delete old Zoho/Zapier conversion "
        "actions — leave them for historical reporting.",
        "",
        "### New conversion actions (via **new** per-market GTM — plan, not live yet)",
        "",
        "| Action (create new) | Fires when | Primary for Stage 1? |",
        "|---------------------|------------|----------------------|",
        "| Employer inquiry delivered | `employer_inquiry_submitted` after durable delivery "
        "(not log-only) | **Yes** |",
        "| Qualified phone call (~60s) | Call tracking / CallRail when wired "
        "(phone click alone ≠ qualified) | **Yes** (when ready) |",
        "",
        "Wire tags in the **new** US/AU GTM containers → new Ads conversion actions. "
        "Keep `NEXT_PUBLIC_ENABLE_ADS_CONVERSIONS=false` until mapping is tested. "
        "Details: `10-tracking-event-spec.md` · `DECISIONS.md`.",
        "",
        "### Campaign-specific goals (required for each `VC_*`)",
        "",
        "1. Open each `VC_US_*` / `VC_AU_*` campaign → **Settings → Goals** "
        "(or Goals on the campaign).",
        "2. Choose **campaign-specific** goals — do **not** use the account-default "
        "goal basket that includes old Zoho/Zapier micros.",
        "3. Include **only** the new actions above (inquiry delivered + phone ~60s when ready).",
        "4. Leave Maximize Clicks for now — do **not** switch to Max Conversions until "
        "those new actions are verified.",
        "",
        "Launch Control checklist encodes the same steps in plain English.",
        "",
        "## Audiences",
        "",
        "- **Launch:** no audience targeting restrictions on `VC_*`.",
        "- **Later:** Observation-only audiences OK once first-party/Zoho data exists.",
        "- Ignore customer-lifecycle / audience warnings until then — not launch-critical.",
        "",
        "## Negative holdouts (not in CSV)",
        "",
        f"Held out so cost/review/comparison/rate employer research is not blocked "
        f"pre-launch (**{len(NEGATIVE_REVIEW_HOLDOUT)}** terms; not in import CSVs):",
        "",
    ]
    for t in NEGATIVE_REVIEW_HOLDOUT:
        lines.append(f"- `{t}`")
    lines += [
        "",
        "Competitor-named review/pricing terms (e.g. `bruntwork reviews`) stay active.",
        "Job-seeker / medical / Spanish / platform negatives stay active.",
        "",
        "## Phase 1 review manifests",
        "",
        "- `phase1-enable-manifest-us.csv` / `phase1-enable-manifest-au.csv` — "
        "keyword enable ladder with tiers **1A / 1B / 2 / 3** (all **Paused**).",
        "- `PHASE1-REVIEW.md` — tier definitions + counts.",
        "- These are **not** Enabled import files. Enable order follows "
        "`PHASED-ACTIVATION.md` after TRAFFIC READY + explicit George approval.",
        "",
        "## Operator path",
        "",
        "1. Leave old account machinery alone (no dig/delete/rewrite/pause binge tonight).",
        "2. Download fresh USA + AU accounts into Editor (read-only sync).",
        "3. Import **US split** into USA → Check changes → leave **Paused**.",
        "4. Import **AU split** into AU → Check changes → leave **Paused**.",
        "5. Confirm `VC_*` negatives are campaign-level curated only — "
        "**do not** attach shared mega lists.",
        "6. Review Phase 1 manifests (1A → 1B) — still Paused until enable approval.",
        "7. Post only after review (still Paused). Then set campaign-specific goals in Ads UI.",
        "8. Enable is a separate explicit decision — never from Import/Post alone.",
        "",
    ]
    PREFLIGHT.write_text("\n".join(lines) + "\n", encoding="utf-8")


DOC_MIRRORS = (
    "EDITOR-PREFLIGHT-REPORT.md",
    "PHASE1-REVIEW.md",
    "DECISIONS.md",
    "PHASED-ACTIVATION.md",
    "10-tracking-event-spec.md",
    "07-phased-activation-recommendation.md",
    "TONIGHT-HANDOFF.md",
)


def mirror_docs() -> None:
    dest_root = ROOT / "xray" / "docs" / "ads-launch"
    dest_root.mkdir(parents=True, exist_ok=True)
    for name in DOC_MIRRORS:
        src = ROOT / "ads-launch" / name
        if src.exists():
            shutil.copy2(src, dest_root / name)


def main() -> None:
    rows = build()
    qa(rows)
    write_csv(OUT, rows)
    write_csv(OUT_MULTI, rows)
    write_csv(OUT_US, [r for r in rows if r["Account"] == ACCOUNT_IDS["US"]])
    write_csv(OUT_AU, [r for r in rows if r["Account"] == ACCOUNT_IDS["AU"]])
    us_n, au_n = write_phase1_manifests(rows)
    write_preflight(rows)
    MIRROR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT, MIRROR)
    shutil.copy2(OUT_US, MIRROR.parent / OUT_US.name)
    shutil.copy2(OUT_AU, MIRROR.parent / OUT_AU.name)
    shutil.copy2(OUT_MANIFEST_US, MIRROR.parent / OUT_MANIFEST_US.name)
    shutil.copy2(OUT_MANIFEST_AU, MIRROR.parent / OUT_MANIFEST_AU.name)
    mirror_docs()
    # Keep Launch Control Ads package page honest after CSV regen
    from build_xray_ads_overview import main as build_xray_ads_overview

    build_xray_ads_overview()
    print(f"Wrote {OUT} ({len(rows)} rows)")
    print(f"Wrote {OUT_US} / {OUT_AU} / {OUT_MULTI}")
    print(f"Wrote {OUT_MANIFEST_US} ({us_n}) / {OUT_MANIFEST_AU} ({au_n})")
    print(f"Wrote {PHASE1_REVIEW}")
    print(f"Wrote {PREFLIGHT}")
    print(f"Mirrored CSV + docs → {MIRROR.parent}")


if __name__ == "__main__":
    main()
