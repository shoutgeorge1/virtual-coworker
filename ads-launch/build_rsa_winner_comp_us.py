#!/usr/bin/env python3
"""Human RSA add + pause weak ads — US (winner/comp voice, not LLM).

George feedback 2026-08-12: pause low CTR, no abbreviations, sound human,
steal competitor messaging (MyOutDesk / Wing). Editor CSV only — no Ads API.

- New RSAs: Paused
- Pause rows: match existing weak ads by Final URL + headlines (Editor finds them)
- Campaign Status blank. Brand deferred. No DKI. Spell out every word.

Usage:
  python3 ads-launch/build_rsa_winner_comp_us.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_rsa_admin_rewrite_us import HEADERS, HOST, US  # noqa: E402

OUT_ADD = HERE / "google-ads-editor-rsa-add-winner-comp-us.csv"
OUT_PAUSE = HERE / "google-ads-editor-rsa-pause-weak-winner-comp-us.csv"
OUT_MD = HERE / "RSA-WINNER-COMP-ADD-US-2026-08-12.md"

ABBREV_RE = re.compile(
    r"\b(EA|VA|PH|RSA|DKI|SMM|WFH|CRM|TA|CS|HR|PPC|SEO|FB)\b", re.IGNORECASE
)
DKI_RE = re.compile(r"\{(KeyWord|KEYWORD|Location|LOCATION)", re.IGNORECASE)

# LLM / agency sludge — fail the build if these sneak back in
SLUDGE = re.compile(
    r"clear employer process|request hiring shortlist|partner-managed|"
    r"employer hiring path|scale .+ bandwidth|employer-only intake|"
    r"dedicated seat continuity|staffing partner model|interview-ready|"
    r"ongoing capacity|ops capacity|hire path",
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
        raise SystemExit(f"{where}: sludge phrasing: {SLUDGE.search(blob)!r}")
    if blob.count("?") > 1 or blob.count("!") > 1:
        raise SystemExit(f"{where}: too many ? or !")
    if "?" in blob and "!" in blob:
        raise SystemExit(f"{where}: ? and ! together")
    for ch in ("\u2014", "\u2013", "\u2026", "...", "\u2018", "\u2019", "\u201c", "\u201d"):
        if ch in blob:
            raise SystemExit(f"{where}: fancy punctuation")


# Plain English. Steal MyOutDesk/Wing energy. Sound like a person.
RSAS: list[dict] = [
    {
        "label": "hire_assistant_human",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Hire_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "hire",
        "path2": "help",
        "headlines": [
            "Need an Extra Pair of Hands?",
            "Hire a Filipino Teammate",
            "Get Your Time Back",
            "Book a Free Strategy Call",
            "You Meet Them First",
            "We Handle the Payroll",
            "Not Freelancers",
            "On Your US Hours",
            "Someone Who Sticks Around",
            "Reduce Admin Overload",
            "Ready in Days",
            "Tell Us Who You Need",
            "Dedicated Help for Your Team",
            "Skip the Job Board Chaos",
            "Real People. Real Work.",
        ],
        "descs": [
            "Need help that actually sticks around. Hire a dedicated Filipino teammate.",
            "Book a free strategy call. We find people. You meet them. We handle payroll.",
            "Not freelancers who disappear. One person on your hours, on your work.",
            "Get your time back. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "agency_human",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "team",
        "path2": "hire",
        "headlines": [
            "Build a Team That Works",
            "Hire Filipino Staff",
            "Book a Free Strategy Call",
            "You Interview. You Decide.",
            "We Handle Payroll",
            "Not a Freelance Bench",
            "Reduce Admin Overload",
            "Ready in Days",
            "On Your US Hours",
            "Get Your Time Back",
            "Tell Us What You Need",
            "Someone You Can Rely On",
            "Skip Marketplace Guesswork",
            "Real Help for Busy Teams",
            "Start With One Person",
        ],
        "descs": [
            "Build a team that drives growth without the local hiring headache.",
            "Free strategy call. We shortlist. You interview. We handle payroll.",
            "Dedicated Filipino staff for US teams - not a rotating freelance bench.",
            "Start with one person. Scale when it works. You stay in control.",
        ],
    },
    {
        "label": "offshore_human",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Offshore_VA_PH",
        "final_url": f"{HOST}/us",
        "path1": "offshore",
        "path2": "help",
        "headlines": [
            "Hire Offshore Help That Stays",
            "Filipino Teammate for US Work",
            "Book a Free Strategy Call",
            "You Meet Them First",
            "Not Freelance Chaos",
            "On Your Hours",
            "Get Admin Off Your Plate",
            "Ready in Days",
            "We Handle Payroll",
            "Someone Who Owns the Work",
            "Tell Us the Role",
            "Skip DIY Overseas Hiring",
            "Real Remote Staff",
            "You Keep the Final Say",
            "Help That Shows Up Daily",
        ],
        "descs": [
            "Offshore help that stays with you - a dedicated Filipino teammate.",
            "Book a free strategy call. You meet them before anyone starts.",
            "We handle recruiting and payroll. You keep the final say.",
            "Get admin off your plate without freelance chaos.",
        ],
    },
    {
        "label": "staffing_human",
        "campaign": "VC_US_S_CORE",
        "ad_group": "Staffing_Agency_PH",
        "final_url": f"{HOST}/us",
        "path1": "staff",
        "path2": "hire",
        "headlines": [
            "Need Staff Without the Mess?",
            "Hire Filipino Team Members",
            "Book a Free Strategy Call",
            "You Interview Every Hire",
            "We Do the Recruiting",
            "Not Upwork Staffing",
            "Reduce Admin Overload",
            "Ready in Days",
            "On Your US Hours",
            "Get Your Time Back",
            "Tell Us the Roles",
            "People Who Stick Around",
            "Skip DIY Philippines Hiring",
            "Real Help. Real Continuity.",
            "Start With One Seat",
        ],
        "descs": [
            "Need staff without building your own Philippines recruiting desk.",
            "Book a free strategy call. Tell us the roles. Meet the people first.",
            "Dedicated teammates - not Upwork staffing or freelance churn.",
            "We recruit. You decide. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "admin_human",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Administration_EA_PH",
        "final_url": f"{HOST}/us/administrative-support",
        "path1": "admin",
        "path2": "help",
        "headlines": [
            "Inbox Eating Your Week?",
            "Hire an Executive Assistant",
            "Get Your Calendar Back",
            "Book a Free Strategy Call",
            "Filipino Admin Who Stays",
            "You Meet Them First",
            "We Handle Payroll",
            "On Your US Hours",
            "Not a Freelance Assistant",
            "Follow-Ups Actually Done",
            "Ready in Days",
            "Tell Us What You Need",
            "Someone Who Learns Your Rhythm",
            "Reduce Admin Overload",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Inbox and calendar eating your week. Hire a dedicated Filipino admin.",
            "Book a free strategy call. You meet them. We handle payroll.",
            "Not a freelance assistant. Someone who learns your rhythm and stays.",
            "Follow-ups actually get done. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "support_human",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Customer_Service_Hire_PH",
        "final_url": f"{HOST}/us/customer-service",
        "path1": "support",
        "path2": "hire",
        "headlines": [
            "Customers Waiting Too Long?",
            "Hire Customer Support Help",
            "Book a Free Strategy Call",
            "Filipino Support Who Stays",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Rotating Agents",
            "Chat and Email Covered",
            "Ready in Days",
            "Get Queues Under Control",
            "Someone Customers Trust",
            "Tell Us Your Support Needs",
            "Real People on Your Brand",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Customers waiting too long. Hire dedicated Filipino support on your hours.",
            "Book a free strategy call. You meet them. We handle payroll.",
            "Chat and email covered by someone who stays - not rotating agents.",
            "Your brand keeps a steady voice. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "social_hire_human",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Hire_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "social",
        "path2": "hire",
        "headlines": [
            "Social Falling Behind?",
            "Hire Social Media Help",
            "Book a Free Strategy Call",
            "Filipino Social Teammate",
            "You Meet Them First",
            "On Your US Hours",
            "We Handle Payroll",
            "Not Freelance Posters",
            "Keep Your Brand Voice",
            "Ready in Days",
            "Get Posting Done Daily",
            "Someone Who Owns the Feed",
            "Tell Us What You Need",
            "Real Help for Busy Brands",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Social falling behind. Hire a dedicated Filipino teammate for your feed.",
            "Book a free strategy call. You meet them. We handle payroll.",
            "Keep your brand voice. Not freelancers who post and vanish.",
            "Daily posting help that sticks. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "social_outsource_human",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Outsource_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "social",
        "path2": "help",
        "headlines": [
            "Outsource Social Without Chaos",
            "Dedicated Social Help",
            "Book a Free Strategy Call",
            "Filipino Teammate for Social",
            "You Meet Them First",
            "Keep Brand Voice Control",
            "Not a Freelance Bench",
            "On Your Hours",
            "Ready in Days",
            "We Handle Payroll",
            "Get the Calendar Moving",
            "Someone Who Stays",
            "Tell Us Your Channels",
            "Real Continuity on Social",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Outsource social without freelance chaos - one dedicated Filipino teammate.",
            "Book a free strategy call. You meet them before anyone starts.",
            "You keep brand voice control. We handle recruiting and payroll.",
            "Get the content calendar moving with someone who stays.",
        ],
    },
    {
        "label": "books_hire_human",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Hire_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "books",
        "path2": "hire",
        "headlines": [
            "Books Piling Up Again?",
            "Hire a Bookkeeper",
            "Book a Free Strategy Call",
            "Filipino Books Teammate",
            "You Meet Them First",
            "Same Person Every Week",
            "We Handle Payroll",
            "Not Freelance Book Tasks",
            "On Your Close Calendar",
            "Ready in Days",
            "Get Reconciliation Done",
            "Someone Who Owns the Books",
            "Tell Us Your Tools",
            "Real Continuity on Books",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Books piling up again. Hire a dedicated Filipino bookkeeper who stays.",
            "Book a free strategy call. You meet them. We handle payroll.",
            "Same person every week - not freelance bookkeeping task bundles.",
            "You keep approval control. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "books_outsource_human",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Outsource_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "books",
        "path2": "help",
        "headlines": [
            "Outsource Books Without Churn",
            "Dedicated Bookkeeping Help",
            "Book a Free Strategy Call",
            "Filipino Books Teammate",
            "You Meet Them First",
            "Same Seat Every Week",
            "Not Freelance Book Tasks",
            "We Handle Payroll",
            "On Your Close Calendar",
            "Ready in Days",
            "Get the Books Current",
            "Someone Who Stays",
            "Tell Us Your Stack",
            "Real Ownership on Books",
            "Nobody Starts Till You Say",
        ],
        "descs": [
            "Outsource bookkeeping without freelancer churn - one dedicated teammate.",
            "Book a free strategy call. You meet them before anyone starts.",
            "Same seat every week. You keep approval. We handle payroll.",
            "Get the books current with help that actually sticks around.",
        ],
    },
]


# Weak enabled RSAs from probe (CTR soft, old abbrev/DKI). Pause to make room.
PAUSE: list[dict] = [
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Outsource_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "offshore",
        "path2": "ph",
        "ad_id": "820036923814",
        "ctr_note": "5.6% CTR · old PH/SMM copy",
        "headlines": [
            "PH Social Media Team",
            "Outsource Content Posting",
            "Outsource Community Ops",
            "Brand Social Staffing",
            "Philippines SMM Bench",
            "Scale Social Without Hire",
            "Dedicated Content Seats",
            "Fit for US Brands",
            "Remote Engagement Support",
            "Vetted Channel Managers",
            "Outsource Social Calendar",
            "Offshore Brand Voice Ops",
            "Partner-Led SMM Ops",
            "Interview Then Place",
            "Outsource This Role PH",
        ],
        "descs": [
            "Add Philippines social capacity for posting, engagement, and content ops.",
            "Dedicated seats keep calendars moving without freelancer churn.",
            "Ask about an outsourcing path for your organization's channels.",
            "For US businesses that need dependable remote social ops.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Social_Media_Hire_PH",
        "final_url": f"{HOST}/us/social-media",
        "path1": "social",
        "path2": "hire",
        "ad_id": "820036923805",
        "ctr_note": "7.3% CTR · DKI + VA copy",
        "headlines": [
            "{KeyWord:Hire Social VA}",
            "Instagram & FB VA Hire",
            "LinkedIn Content Support",
            "Filipino Community Manager",
            "Hire Social Media VA",
            "Filipino SMM for Hire",
            "Social Manager Philippines",
            "US Social Staffing",
            "Vetted SMM Shortlist",
            "Interview Before You Hire",
            "Dedicated Social Seat",
            "Community Manager Hire",
            "Content Scheduler VA",
            "Employer Hiring Path",
            "Remote SMM Specialist",
        ],
        "descs": [
            "Hire a dedicated Filipino social media manager through a staffing partner.",
            "Shortlist is interview-ready; we handle recruiting, vetting, and support.",
            "For US employers who need reliable day-to-day social capacity.",
            "Ongoing SMM hires — not one-off freelance posting gigs.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Hire_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "books",
        "path2": "hire",
        "ad_id": "820036923973",
        "ctr_note": "7.1% CTR · DKI + VA copy",
        "headlines": [
            "{KeyWord:Hire Bookkeeper}",
            "Philippines Books VA",
            "Remote Reconciliation Hire",
            "Filipino Books Specialist",
            "Hire Bookkeeper Philippines",
            "Filipino Bookkeeper Hire",
            "Virtual Bookkeeper PH",
            "US Books Staffing",
            "Vetted Books Shortlist",
            "Interview Before Hire",
            "Dedicated Books Seat",
            "QuickBooks VA Hire",
            "Xero Bookkeeper Hire",
            "Employer Hiring Path",
            "Remote Books Specialist",
        ],
        "descs": [
            "Hire a dedicated Filipino bookkeeper through a staffing partner.",
            "Interview shortlisted talent; we recruit, vet, and support the hire.",
            "For US employers who need reliable weekly books capacity.",
            "Ongoing bookkeeping hires — not marketplace task bundles.",
        ],
    },
    {
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Bookkeeping_Outsource_PH",
        "final_url": f"{HOST}/us/bookkeeping",
        "path1": "outsource",
        "path2": "books",
        "ad_id": "820036923985",
        "ctr_note": "7.9% CTR · PH abbrev copy",
        "headlines": [
            "Dedicated PH Bookkeeper",
            "Same Books Seat Weekly",
            "Accountable Books Support",
            "Philippines Books Continuity",
            "Not Freelance Book Tasks",
            "Offshore Books Ownership",
            "Books Seat You Can Keep",
            "Interview Bookkeeper First",
            "Vetted Helpdesk Seat PH",
            "Remote Care Ownership",
            "Staffing Not Gig Support",
            "Proof in Dedicated CS",
            "Ticket Seat From PH",
            "Chat Email Seat Dedicated",
            "Request Dedicated Support",
        ],
        "descs": [
            "Outsource bookkeeping with a dedicated Philippines seat — not task bundles.",
            "Proof is continuity: one vetted bookkeeper you interview before placement.",
            "Built for US employers who need accountable offshore books help.",
            "Partner-led model. Response-time and CSAT goals set after we talk.",
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
                "Human winner/comp RSA 2026-08-12; Paused; no abbrev; "
                f"angle={rsa['label']}"
            ),
        }
    )
    for i, h in enumerate(rsa["headlines"], 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(rsa["descs"], 1):
        r[f"Description {i}"] = d
    rows.append(r)


def append_pause(rows: list[dict[str, str]], ad: dict) -> None:
    # Pause rows intentionally keep old copy (incl. abbrev) so Editor matches live ads.
    r = blank_row()
    r.update(
        {
            "Account": US,
            "Row Type": "Ad",
            "Campaign": ad["campaign"],
            "Campaign Type": "Search",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ad["ad_group"],
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": ad["final_url"],
            "Path 1": ad["path1"],
            "Path 2": ad["path2"],
            "Comment": (
                f"Pause weak RSA 2026-08-12; {ad['ctr_note']}; "
                f"ad_id={ad['ad_id']}; Campaign Status blank"
            ),
        }
    )
    for i, h in enumerate(ad["headlines"], 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(ad["descs"], 1):
        r[f"Description {i}"] = d
    rows.append(r)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def write_md() -> None:
    lines = [
        "# Human RSA replace — US · 2026-08-12",
        "",
        "Response to George: low-CTR RSAs paused; new copy is plain English "
        "(MyOutDesk/Wing energy). **No Ads API mutate** — Editor import.",
        "",
        "## Import order",
        "",
        "1. `google-ads-editor-rsa-pause-weak-winner-comp-us.csv` (pause 4 weak)",
        "2. `google-ads-editor-rsa-add-winner-comp-us.csv` (10 new Paused)",
        "3. Post both. Enable new ones after a day of CTR.",
        "",
        "## New ads (Paused)",
        "",
        "| Ad group | Sample |",
        "|----------|--------|",
    ]
    for rsa in RSAS:
        lines.append(
            f"| `{rsa['ad_group']}` | {rsa['headlines'][0]} · {rsa['headlines'][3]} |"
        )
    lines += [
        "",
        "## Pausing",
        "",
        "| Ad group | Why |",
        "|----------|-----|",
    ]
    for ad in PAUSE:
        lines.append(f"| `{ad['ad_group']}` | {ad['ctr_note']} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    adds: list[dict[str, str]] = []
    pauses: list[dict[str, str]] = []
    for rsa in RSAS:
        append_add(adds, rsa)
    for ad in PAUSE:
        append_pause(pauses, ad)
    write_csv(OUT_ADD, adds)
    write_csv(OUT_PAUSE, pauses)
    write_md()
    print(f"ADD   {OUT_ADD.name} ({len(adds)} Paused RSAs)")
    print(f"PAUSE {OUT_PAUSE.name} ({len(pauses)} weak RSAs)")
    print(f"NOTE  {OUT_MD.name}")


if __name__ == "__main__":
    main()
