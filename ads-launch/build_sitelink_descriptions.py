#!/usr/bin/env python3
"""Build description-only Google Ads Editor CSVs for existing sitelinks.

Live-safe:
- Link Text + Final URL copied from sitelink-add CSVs (unchanged).
- Only Description Line 1 / Line 2 change (customer-facing copy).
- Campaign Status / Budget blank. VC_* CORE + ROLES only. Not Brand.
- Does not revive paused US Employer Home / AU Employer Home.
- No Ads API.

Usage:
  python3 ads-launch/build_sitelink_descriptions.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
LINK_MAX = 25
DESC_MAX = 35

US_ADD = OUT_DIR / "google-ads-editor-sitelink-add-us.csv"
AU_ADD = OUT_DIR / "google-ads-editor-sitelink-add-au.csv"
OUT_US = OUT_DIR / "google-ads-editor-sitelink-descriptions-us.csv"
OUT_AU = OUT_DIR / "google-ads-editor-sitelink-descriptions-au.csv"

COMMENT = (
    "Sitelink descriptions only 2026-08-17; Link Text + Final URL unchanged; "
    "Campaign Status blank (live-safe); not account-level / not Brand; "
    "do not revive Employer Home"
)

# Customer-facing lines searchers see under sitelink titles. Keys = exact Link Text.
COPY: dict[str, tuple[str, str]] = {
    "Tell Us Who You Need": (
        "Tell us the role you need",
        "A specialist will follow up",
    ),
    "How Hiring Works": (
        "We recruit. You interview.",
        "You choose who starts.",
    ),
    "Take the VA Quiz": (
        "Find the right staff role",
        "A short quiz for employers",
    ),
    "Hire by Role": (
        "Admin, books, or marketing",
        "Dedicated staff, your hours",
    ),
    "Admin Support Hire": (
        "EA and admin on your hours",
        "Calendar, inbox, follow-up",
    ),
    "Bookkeeping Hire": (
        "Books done without local hire",
        "Invoices, reports, your hours",
    ),
    "Digital Marketing Hire": (
        "Marketing help on your hours",
        "Content, ads, and campaigns",
    ),
    "Social Media Hire": (
        "Social managed on your hours",
        "Posts, replies, your hours",
    ),
}

FORBIDDEN_LINK_TEXT = {"US Employer Home", "AU Employer Home"}


def _check_copy() -> None:
    for text, (d1, d2) in COPY.items():
        if len(text) > LINK_MAX:
            raise SystemExit(f"link text {len(text)} > {LINK_MAX}: {text!r}")
        if not d1 or len(d1) > DESC_MAX:
            raise SystemExit(f"{text}: desc1 {len(d1)} chars: {d1!r}")
        if not d2 or len(d2) > DESC_MAX:
            raise SystemExit(f"{text}: desc2 {len(d2)} chars: {d2!r}")


def rewrite(src: Path, dest: Path, *, account: str, mkt: str) -> list[dict[str, str]]:
    with src.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise SystemExit(f"{src.name}: missing header")
        rows = list(reader)

    expected_camps = {f"VC_{mkt}_S_CORE", f"VC_{mkt}_S_ROLES"}
    out: list[dict[str, str]] = []
    for i, r in enumerate(rows, 2):
        if (r.get("Account") or "").strip() != account:
            raise SystemExit(f"{src.name}:{i} Account must be {account}")
        if (r.get("Row Type") or "").strip() != "Sitelink":
            raise SystemExit(f"{src.name}:{i} Row Type must be Sitelink")
        camp = (r.get("Campaign") or "").strip()
        if camp not in expected_camps:
            raise SystemExit(f"{src.name}:{i} unexpected campaign {camp}")
        text = (r.get("Link Text") or "").strip()
        if text in FORBIDDEN_LINK_TEXT:
            raise SystemExit(f"{src.name}:{i} must not include paused {text}")
        if text not in COPY:
            raise SystemExit(f"{src.name}:{i} no copy for {text!r}")
        url = (r.get("Final URL") or "").strip()
        if not url:
            raise SystemExit(f"{src.name}:{i} empty Final URL — refusing to blank destinations")
        d1, d2 = COPY[text]
        row = {h: r.get(h) or "" for h in fieldnames}
        row["Campaign Status"] = ""
        row["Budget"] = ""
        row["Description Line 1"] = d1
        row["Description Line 2"] = d2
        row["Comment"] = COMMENT
        if row["Link Text"] != text:
            raise SystemExit(f"{src.name}:{i} Link Text mutated")
        if row["Final URL"] != url:
            raise SystemExit(f"{src.name}:{i} Final URL mutated")
        out.append(row)

    with dest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out)

    desc_changed = 0
    for src_row, out_row in zip(rows, out, strict=True):
        if src_row["Link Text"] != out_row["Link Text"]:
            raise SystemExit(f"{dest.name}: Link Text drift")
        if src_row["Final URL"] != out_row["Final URL"]:
            raise SystemExit(f"{dest.name}: Final URL drift")
        if (src_row.get("Campaign Status") or out_row.get("Campaign Status")):
            if out_row.get("Campaign Status"):
                raise SystemExit(f"{dest.name}: Campaign Status must be blank")
        if out_row["Description Line 1"] != src_row["Description Line 1"] or out_row[
            "Description Line 2"
        ] != src_row["Description Line 2"]:
            desc_changed += 1
    if desc_changed != len(out):
        raise SystemExit(f"{dest.name}: expected every row to change descriptions, got {desc_changed}/{len(out)}")
    if len(out) != 12:
        raise SystemExit(f"{dest.name}: expected 12 rows, got {len(out)}")
    return out


def main() -> None:
    _check_copy()
    us = rewrite(US_ADD, OUT_US, account="496-715-1855", mkt="US")
    au = rewrite(AU_ADD, OUT_AU, account="573-539-1940", mkt="AU")
    print(f"US: {OUT_US.name} ({len(us)} sitelinks) · descriptions only")
    print(f"AU: {OUT_AU.name} ({len(au)} sitelinks) · same copy; import after USA if preview is description-only")
    print("Link Text + Final URL unchanged vs sitelink-add CSVs. Brand deferred. 0 Ads API calls.")


if __name__ == "__main__":
    main()
