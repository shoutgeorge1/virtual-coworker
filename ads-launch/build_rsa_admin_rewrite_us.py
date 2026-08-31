#!/usr/bin/env python3
"""Build ADD-only Google Ads Editor CSV: new human RSAs for Administration_EA_PH.

Live-US-safe:
- Campaign Status / Budget / Ad Group Status blank (do not rewrite live campaigns)
- New RSAs ship Paused (George enables after review)
- Final URL: live /us/administrative-support
- No Brand. No keywords. No Ads API. No DKI. No EA/VA/PH in ad copy.

VC_US_S_ROLES is the campaign, not an ad group. This file only rewrites
Administration_EA_PH (the admin / executive-assistant AG inside that campaign).

Usage:
  python3 ads-launch/build_rsa_admin_rewrite_us.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
OUT_CSV = OUT_DIR / "google-ads-editor-rsa-add-admin-us.csv"
US = "496-715-1855"
HOST = "https://www.virtualcoworker.app"
ADMIN_LP = f"{HOST}/us/administrative-support"

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

ABBREV_RE = re.compile(r"\b(EA|VA|PH|RSA|DKI)\b", re.IGNORECASE)
DKI_RE = re.compile(r"\{(KeyWord|KEYWORD|Location|LOCATION)", re.IGNORECASE)


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


# Voice: live /us/administrative-support — Book a Free Strategy Call,
# dedicated Filipino teammate, you interview / you pick, payroll handled,
# US hours, not a marketplace. $8 only because this LP states typical admin rate.
# No tilde on $8 (Google PROHIBITED ~$8 on 2026-08-10).
RSAS: list[dict] = [
    {
        "label": "executive_assistant",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Administration_EA_PH",
        "final_url": ADMIN_LP,
        "path1": "admin",
        "path2": "hire",
        "headlines": [
            "Inbox Eating Your Week?",
            "Hire Executive Assistant",
            "Dedicated Filipino Admin",
            "On Your US Hours",
            "You Interview. You Pick.",
            "We Handle Payroll",
            "Book a Free Strategy Call",
            "Admin Around $8 an Hour",
            "Calendar Stops Owning You",
            "Not a Freelance Marketplace",
            "They Learn How You Work",
            "Follow-Ups Actually Done",
            "Your Managers Get Time Back",
            "Philippines Admin Support",
            "Skip the Marketplace Hunt",
        ],
        "descs": [
            "Inbox eating your week. Hire a dedicated Filipino executive assistant.",
            "Book a free strategy call. We recruit. You interview. We handle payroll.",
            "Typical admin around $8 an hour. A dedicated teammate, not a freelance marketplace.",
            "You pick who joins. Nobody starts until you say yes.",
        ],
    },
    {
        "label": "virtual_assistant",
        "campaign": "VC_US_S_ROLES",
        "ad_group": "Administration_EA_PH",
        "final_url": ADMIN_LP,
        "path1": "assistant",
        "path2": "philippines",
        "headlines": [
            "Hire a Virtual Assistant",
            "Dedicated Filipino Teammate",
            "Administrative Support Hire",
            "On Your Business Hours",
            "You Interview Each Person",
            "Payroll Handled for You",
            "Book a Free Strategy Call",
            "Admin About $8 an Hour",
            "Not a Gig Marketplace",
            "Still Doing Admin Yourself?",
            "We Recruit. You Decide.",
            "Filipino Admin for US Work",
            "One Person You Can Keep",
            "Clear Admin Off Your Desk",
            "Talk Through the Role",
        ],
        "descs": [
            "Still doing the admin yourself. A dedicated Filipino virtual assistant on your hours.",
            "Free strategy call. We recruit and screen. You interview. We handle payroll.",
            "Typical admin around $8 an hour. One person you keep - not rotating freelancers.",
            "You meet them on video. Nobody starts until you say yes. Employers only.",
        ],
    },
]


def append_rsa(rows: list[dict[str, str]], rsa: dict) -> None:
    where = f"{rsa['campaign']}/{rsa['ad_group']}/{rsa['label']}"
    validate_rsa(rsa["headlines"], rsa["descs"], where)
    blob = " ".join(rsa["headlines"] + rsa["descs"])
    if "$8" not in blob:
        raise SystemExit(f"{where}: expected $8 on admin LP")
    for p in (rsa["path1"], rsa["path2"]):
        if len(p) > 15:
            raise SystemExit(f"{where}: path too long ({len(p)}): {p}")
        if ABBREV_RE.search(p):
            raise SystemExit(f"{where}: abbreviation in path: {p}")
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
                "Human RSA rewrite 2026-08-12; Paused; Campaign Status blank "
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
    rows: list[dict[str, str]] = []
    for rsa in RSAS:
        append_rsa(rows, rsa)
        print(f"OK {rsa['label']}")
        for i, h in enumerate(rsa["headlines"], 1):
            print(f"  H{i:02d} ({len(h):2d}) {h}")
        for i, d in enumerate(rsa["descs"], 1):
            print(f"  D{i} ({len(d):2d}) {d}")
    write_csv(OUT_CSV, rows)
    print(f"Wrote {OUT_CSV}")
    print(f"  RSAs={len(rows)} · AG=Administration_EA_PH · campaign=VC_US_S_ROLES")
    print(f"  Final URL={ADMIN_LP}")
    print("  All Paused · Brand excluded · no negatives")


if __name__ == "__main__":
    main()
