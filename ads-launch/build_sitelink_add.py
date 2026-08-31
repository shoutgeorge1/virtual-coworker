#!/usr/bin/env python3
"""Build ADD-only Google Ads Editor CSVs: campaign sitelinks for US + AU.

Live-safe:
- Campaign Status / Budget blank (do not rewrite live CORE/ROLES)
- Campaign-level only on VC_* Search (not account-level, not Brand, not PM_*)
- Microsite Final URLs only (www.virtualcoworker.app — no WordPress)
- No Ads API

Usage:
  python3 ads-launch/build_sitelink_add.py
"""

from __future__ import annotations

import csv
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
HOST = "https://www.virtualcoworker.app"
US = "496-715-1855"
AU = "573-539-1940"

LINK_MAX = 25
DESC_MAX = 35

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

COMMENT = (
    "Sitelink add 2026-08-12; Campaign Status blank (live-safe); "
    "microsite only — no WP; not account-level / not Brand; no #gate in Final URL"
)


def blank_row() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def validate_sitelink(text: str, d1: str, d2: str, url: str, where: str) -> None:
    if not text or len(text) > LINK_MAX:
        raise SystemExit(f"{where}: link text {len(text)} chars (max {LINK_MAX}): {text!r}")
    if not d1 or len(d1) > DESC_MAX:
        raise SystemExit(f"{where}: desc1 {len(d1)} chars (max {DESC_MAX}): {d1!r}")
    if not d2 or len(d2) > DESC_MAX:
        raise SystemExit(f"{where}: desc2 {len(d2)} chars (max {DESC_MAX}): {d2!r}")
    if not url.startswith(f"{HOST}/"):
        raise SystemExit(f"{where}: Final URL must be {HOST}/… got {url}")
    low = url.lower()
    if "wordpress" in low or "try.virtualcoworker" in low or "calendly" in low:
        raise SystemExit(f"{where}: forbidden host/path in sitelink URL: {url}")


def sitelinks_core(mkt: str) -> list[tuple[str, str, str, str]]:
    m = mkt.lower()
    base = f"{HOST}/{m}"
    return [
        (
            "Tell Us Who You Need",
            "Employer hiring path",
            "Form for businesses",
            # Ads Final URLs reject #fragments — hub URL; form is on the page.
            base,
        ),
        (
            "How Hiring Works",
            "Recruit, vet, shortlist",
            "You interview talent",
            f"{HOST}/how-it-works?market={m}",
        ),
        (
            "Take the VA Quiz",
            "Find the right role",
            "A few taps. Employers.",
            f"{base}/quiz",
        ),
        (
            "Hire by Role",
            "Admin, books, marketing",
            "Philippines staff seats",
            f"{HOST}/services?market={m}",
        ),
        (
            "Admin Support Hire",
            "EA / admin category LP",
            "Role-specific landing",
            f"{base}/administrative-support",
        ),
        (
            "Bookkeeping Hire",
            "Philippines books staff",
            "Category landing page",
            f"{base}/bookkeeping",
        ),
    ]


def sitelinks_roles(mkt: str) -> list[tuple[str, str, str, str]]:
    m = mkt.lower()
    base = f"{HOST}/{m}"
    return [
        (
            "Tell Us Who You Need",
            "Employer hiring path",
            "Form for businesses",
            base,
        ),
        (
            "How Hiring Works",
            "Recruit, vet, shortlist",
            "You interview talent",
            f"{HOST}/how-it-works?market={m}",
        ),
        (
            "Take the VA Quiz",
            "Find the right role",
            "A few taps. Employers.",
            f"{base}/quiz",
        ),
        (
            "Digital Marketing Hire",
            "Philippines marketing staff",
            "Category landing page",
            f"{base}/digital-marketing",
        ),
        (
            "Social Media Hire",
            "Philippines SMM staff",
            "Category landing page",
            f"{base}/social-media",
        ),
        (
            "Bookkeeping Hire",
            "Philippines books staff",
            "Category landing page",
            f"{base}/bookkeeping",
        ),
    ]


def sitelinks_quiz(mkt: str) -> list[tuple[str, str, str, str]]:
    """Quiz campaign: do not sitelink back to the quiz LP (ad already goes there)."""
    m = mkt.lower()
    base = f"{HOST}/{m}"
    return [
        (
            "Tell Us Who You Need",
            "Employer hiring path",
            "Form for businesses",
            base,
        ),
        (
            "How Hiring Works",
            "Recruit, vet, shortlist",
            "You interview talent",
            f"{HOST}/how-it-works?market={m}",
        ),
        (
            "Hire by Role",
            "Admin, books, marketing",
            "Philippines staff seats",
            f"{HOST}/services?market={m}",
        ),
        (
            "Admin Support Hire",
            "EA / admin category LP",
            "Role-specific landing",
            f"{base}/administrative-support",
        ),
    ]


def sitelink_row(
    *,
    account: str,
    campaign: str,
    text: str,
    d1: str,
    d2: str,
    url: str,
    campaign_status: str = "",
    comment: str = COMMENT,
) -> dict[str, str]:
    where = f"{account}/{campaign}/{text}"
    validate_sitelink(text, d1, d2, url, where)
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Sitelink",
            "Campaign": campaign,
            "Campaign Type": "Search",
            "Campaign Status": campaign_status,
            "Networks": "Google Search",
            "Location options": "Presence",
            "Final URL": url,
            "Link Text": text,
            "Description Line 1": d1,
            "Description Line 2": d2,
            "Comment": comment,
        }
    )
    return r


def build_market(account: str, mkt: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for text, d1, d2, url in sitelinks_core(mkt):
        rows.append(
            sitelink_row(
                account=account,
                campaign=f"VC_{mkt}_S_CORE",
                text=text,
                d1=d1,
                d2=d2,
                url=url,
            )
        )
    for text, d1, d2, url in sitelinks_roles(mkt):
        rows.append(
            sitelink_row(
                account=account,
                campaign=f"VC_{mkt}_S_ROLES",
                text=text,
                d1=d1,
                d2=d2,
                url=url,
            )
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def validate_csv(path: Path, rows: list[dict[str, str]], *, account: str, mkt: str) -> None:
    errors: list[str] = []
    if not rows:
        errors.append(f"{path.name}: empty")
    expected_camps = {f"VC_{mkt}_S_CORE", f"VC_{mkt}_S_ROLES"}
    seen: set[tuple[str, str]] = set()
    for i, r in enumerate(rows, 2):
        if (r.get("Account") or "").strip() != account:
            errors.append(f"{path.name}:{i} Account must be {account}")
        if (r.get("Row Type") or "").strip() != "Sitelink":
            errors.append(f"{path.name}:{i} Row Type must be Sitelink")
        camp = (r.get("Campaign") or "").strip()
        if camp not in expected_camps:
            errors.append(f"{path.name}:{i} unexpected campaign {camp}")
        if (r.get("Campaign Status") or "").strip():
            errors.append(f"{path.name}:{i} Campaign Status must be blank (live-safe)")
        if (r.get("Budget") or "").strip():
            errors.append(f"{path.name}:{i} Budget must be blank")
        if (r.get("Ad Group") or "").strip():
            errors.append(f"{path.name}:{i} Ad Group must be blank (campaign-level only)")
        key = (camp, (r.get("Link Text") or "").strip())
        if key in seen:
            errors.append(f"{path.name}:{i} duplicate sitelink {key}")
        seen.add(key)
        validate_sitelink(
            r["Link Text"],
            r["Description Line 1"],
            r["Description Line 2"],
            r["Final URL"],
            f"{path.name}:{i}",
        )
    if len(rows) != 12:
        errors.append(f"{path.name}: expected 12 sitelink rows (6 CORE + 6 ROLES), got {len(rows)}")
    if errors:
        raise SystemExit("Sitelink add validation failed:\n- " + "\n- ".join(errors))


def main() -> None:
    us_rows = build_market(US, "US")
    au_rows = build_market(AU, "AU")
    out_us = OUT_DIR / "google-ads-editor-sitelink-add-us.csv"
    out_au = OUT_DIR / "google-ads-editor-sitelink-add-au.csv"
    write_csv(out_us, us_rows)
    write_csv(out_au, au_rows)
    validate_csv(out_us, us_rows, account=US, mkt="US")
    validate_csv(out_au, au_rows, account=AU, mkt="AU")
    print(f"US: {out_us.name} ({len(us_rows)} sitelinks) · {US}")
    print(f"AU: {out_au.name} ({len(au_rows)} sitelinks) · {AU}")
    print("Campaigns: VC_*_S_CORE + VC_*_S_ROLES only. Brand deferred. No API mutate.")


if __name__ == "__main__":
    main()
