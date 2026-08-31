#!/usr/bin/env python3
"""Build Paused Google Ads Editor CSVs for the quiz LP funnel.

VC_US_S_QUIZ / VC_AU_S_QUIZ — exploratory employer hiring quiz.
Final URLs: /us/quiz and /au/quiz only. Exact match. Brand deferred.
No Ads API. Import → review → Post (still Paused) → Enable only when George says.

Not a statistically controlled A/B test — exploratory funnel only.
Do not change live CORE/ROLES.

Usage:
  python3 ads-launch/build_quiz_editor_package.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from build_sitelink_add import sitelinks_quiz, validate_sitelink

OUT_DIR = Path(__file__).resolve().parent
US = "496-715-1855"
AU = "573-539-1940"
HOST = "https://www.virtualcoworker.app"
# Site tracking.ts already stamps stage1-v8. ChatGPT mega prompt said v7 —
# keep v8 so quiz ads match what the LP actually sends. Distinguish via lp_variant.
LP_VERSION = "stage1-v8"
LP_VARIANT = "quiz"

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

NEG_MMC_FIELDS = ["Account", "Campaign", "Keyword", "Match type", "Comment"]

UTM_SUFFIX = (
    "utm_source=google&utm_medium=cpc&utm_campaign={campaignid}"
    "&utm_content={adgroupid}&utm_term={keyword}&utm_matchtype={matchtype}"
    f"&utm_device={{device}}&lp_version={LP_VERSION}&lp_variant={LP_VARIANT}"
)

# Quiz keywords after CORE/ROLES Exact overlap audit.
# Unique quiz / exploratory only in the import CSV. Exact clones dropped.
AD_GROUPS = [
    {
        "name": "What_Kind_Of_VA",
        "cloned_from": "quiz-unique exploratory (not in CORE/ROLES Exact)",
        "keywords": [
            "what kind of virtual assistant do i need",
            "what type of virtual assistant do i need",
            "what virtual assistant do i need",
            "what va do i need",
            "which virtual assistant do i need",
            "types of virtual assistants",
            "kinds of virtual assistants",
            "virtual assistant quiz",
            "hiring quiz virtual assistant",
            "what kind of va should i hire",
        ],
        "path1": "quiz",
        "path2": "what-va",
    },
    {
        "name": "Hire_VA_Explore",
        "cloned_from": "exploratory how-to unique vs CORE Hire_VA_PH Exact",
        "keywords": [
            "hiring a virtual assistant",
            "where to hire a virtual assistant",
            "how to hire filipino va",
            "should i hire a virtual assistant",
            "do i need a virtual assistant",
            "how to choose a virtual assistant",
            "help me hire a virtual assistant",
        ],
        "path1": "quiz",
        "path2": "hire",
    },
    {
        "name": "VA_Small_Business",
        "cloned_from": "SMB/startup Exact themes unique vs ROLES",
        "keywords": [
            "virtual assistant for small business",
            "virtual assistant small business",
            "hire virtual assistant small business",
            "virtual assistant for small businesses",
            "va for small business",
            "virtual assistant for startup",
            "virtual assistant for startups",
            "small business virtual assistant",
        ],
        "path1": "quiz",
        "path2": "smb",
    },
    {
        "name": "Admin_VA_Quiz",
        "cloned_from": "admin exploratory unique vs ROLES Administration_EA_PH Exact",
        "keywords": [
            "hire administrative assistant",
            "hire admin assistant",
            "virtual assistant for admin",
            "administrative virtual assistant",
            "virtual executive assistant",
            "admin virtual assistant",
        ],
        "path1": "quiz",
        "path2": "admin",
    },
    {
        "name": "Bookkeeping_VA_Quiz",
        "cloned_from": "books exploratory unique vs ROLES Bookkeeping_Hire_PH Exact",
        "keywords": [
            "hire virtual bookkeeper",
            "virtual bookkeeper",
            "hire bookkeeper",
            "outsource bookkeeping",
        ],
        "path1": "quiz",
        "path2": "books",
    },
]

# Exact CORE/ROLES clones — not in quiz import. Documented for George.
DROPPED_UNNECESSARY = [
    ("hire virtual assistant", "Hire_VA_Explore", "Exact in CORE Hire_VA_PH"),
    ("hire a virtual assistant", "Hire_VA_Explore", "Exact in CORE Hire_VA_PH"),
    ("hire virtual assistant philippines", "Hire_VA_Explore", "Exact in CORE Hire_VA_PH"),
    ("hire filipino virtual assistant", "Hire_VA_Explore", "Exact in CORE Hire_VA_PH"),
    ("hire a filipino virtual assistant", "Hire_VA_Explore", "Exact in CORE Hire_VA_PH"),
    ("hire virtual administrative assistant", "Admin_VA_Quiz", "Exact in ROLES Administration_EA_PH"),
    ("virtual assistant bookkeeping", "Bookkeeping_VA_Quiz", "Exact in ROLES Bookkeeping_Hire_PH"),
    ("hire virtual bookkeeping assistant", "Bookkeeping_VA_Quiz", "Exact in ROLES Bookkeeping_Hire_PH"),
]

# Quiz-shaped but high-volume CORE Exact — hold out unless George approves.
OPTIONAL_HOLDOUT = [
    (
        "how to hire a virtual assistant",
        "Hire_VA_Explore",
        "Exploratory/how-to, but Exact in CORE Hire_VA_PH — auction split risk",
    ),
]

US_HEADLINES = [
    "Find the right VA",
    "Take the employer quiz",
    "Employer hiring quiz",
    "What kind of VA do you need?",
    "Who should you hire first?",
    "A few taps. Clear answer.",
    "Quiz: admin, sales, books",
    "Find your first hire",
    "For US businesses",
    "Dedicated Filipino VA",
    "Virtual assistant quiz",
    "See which seat to hire",
    "Filipino VA for SMBs",
    "Shortlist after the quiz",
    "Talk after the quiz",
]

AU_HEADLINES = [
    "Find the right assistant",
    "Take the hiring quiz",
    "Hiring quiz for business",
    "Who should you hire first?",
    "What kind of VA do you need?",
    "A few taps. Clear answer.",
    "Quiz: admin, sales, books",
    "A starting point not a pitch",
    "For Australian businesses",
    "Dedicated Filipino staff",
    "Virtual assistant quiz",
    "See which role to hire",
    "Have a chat after the quiz",
    "Filipino VA for SMBs",
    "Employer quiz for business",
]

US_DESCS = [
    "Take the employer quiz. We’ll name the seat that buys back your week.",
    "Hiring quiz for US businesses. Dedicated Filipino teammates — not a job board.",
    "Admin, sales, books, support, or marketing? A few taps. A clear first hire.",
    "You interview the shortlist. Nobody starts until you say yes. Free chat after the quiz.",
]

AU_DESCS = [
    "Take the employer quiz. We’ll name the role that takes the load — then chat.",
    "Hiring quiz for Australian businesses. Dedicated Filipino staff — not a job board.",
    "Admin, sales, books, support or marketing? A few taps. A clear first hire.",
    "You interview the shortlist. Nobody starts until you say yes. No obligation.",
]


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
    for d in descs:
        if len(d) > 90:
            raise SystemExit(f"{where}: description too long ({len(d)}): {d}")


def campaign_row(*, account: str, camp: str, location: str, budget: str, cpc: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Campaign",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Budget": budget,
            "Budget type": "Daily",
            "Bid Strategy Type": "Maximize Clicks",
            "Networks": "Google Search",
            "Languages": "en",
            "Location": location,
            "Location options": "Presence",
            "Tracking template": "{lpurl}",
            "Final URL suffix": UTM_SUFFIX,
            "Maximum CPC bid limit": cpc,
            "Comment": (
                f"Quiz LP exploratory {LP_VERSION} lp_variant={LP_VARIANT} · Paused · "
                "Brand deferred · Final URL=/us/quiz or /au/quiz · Enable only when George says · "
                "Not a controlled A/B test"
            ),
        }
    )
    return r


def ag_row(*, account: str, camp: str, ag: str, cloned: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Ad group",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Group Status": "Paused",
            "Comment": f"Quiz AG · {cloned} · Exact · Paused",
        }
    )
    return r


def kw_row(*, account: str, camp: str, ag: str, keyword: str) -> dict[str, str]:
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Keyword",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Keyword": keyword,
            "Criterion Type": "Exact",
            "Keyword Status": "Paused",
            "Comment": "Quiz Exact · unique/exploratory vs CORE/ROLES · Paused until Enable",
        }
    )
    return r


def rsa_row(
    *,
    account: str,
    camp: str,
    ag: str,
    final_url: str,
    path1: str,
    path2: str,
    headlines: list[str],
    descs: list[str],
) -> dict[str, str]:
    validate_rsa(headlines, descs, f"{camp}/{ag}")
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Ad",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Ad Group": ag,
            "Ad Status": "Paused",
            "Ad type": "Responsive search ad",
            "Final URL": final_url,
            "Path 1": path1,
            "Path 2": path2,
            "Comment": "Quiz RSA · exploratory employer quiz · Paused · not hire-specialist hard sell",
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    return r


def sitelink_quiz_row(
    *,
    account: str,
    camp: str,
    text: str,
    d1: str,
    d2: str,
    url: str,
) -> dict[str, str]:
    validate_sitelink(text, d1, d2, url, f"{camp}/{text}")
    r = blank_row()
    r.update(
        {
            "Account": account,
            "Row Type": "Sitelink",
            "Campaign": camp,
            "Campaign Type": "Search",
            "Campaign Status": "Paused",
            "Networks": "Google Search",
            "Location options": "Presence",
            "Final URL": url,
            "Link Text": text,
            "Description Line 1": d1,
            "Description Line 2": d2,
            "Comment": "Quiz sitelink · microsite only — no WP · Paused with campaign",
        }
    )
    return r


def build_market(
    *,
    account: str,
    camp: str,
    location: str,
    budget: str,
    cpc: str,
    final_url: str,
    headlines: list[str],
    descs: list[str],
) -> list[dict[str, str]]:
    rows = [campaign_row(account=account, camp=camp, location=location, budget=budget, cpc=cpc)]
    for ag in AD_GROUPS:
        rows.append(ag_row(account=account, camp=camp, ag=ag["name"], cloned=ag["cloned_from"]))
        for kw in ag["keywords"]:
            rows.append(kw_row(account=account, camp=camp, ag=ag["name"], keyword=kw))
        rows.append(
            rsa_row(
                account=account,
                camp=camp,
                ag=ag["name"],
                final_url=final_url,
                path1=ag["path1"],
                path2=ag["path2"],
                headlines=headlines,
                descs=descs,
            )
        )
    if camp == "VC_US_S_QUIZ":
        mkt = "US"
    elif camp == "VC_AU_S_QUIZ":
        mkt = "AU"
    else:
        raise SystemExit(f"Unknown quiz campaign for sitelinks: {camp}")
    for text, d1, d2, url in sitelinks_quiz(mkt):
        rows.append(
            sitelink_quiz_row(
                account=account,
                camp=camp,
                text=text,
                d1=d1,
                d2=d2,
                url=url,
            )
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def load_core_negatives(path: Path, campaign_filter: str) -> list[tuple[str, str]]:
    """(keyword, match_type) from existing MMC campaign-negatives file."""
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("Campaign") or "").strip() != campaign_filter:
                continue
            kw = (row.get("Keyword") or "").strip()
            mt = (row.get("Match type") or "Broad").strip() or "Broad"
            if not kw:
                continue
            key = (kw.lower(), mt.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append((kw, mt))
    return out


def build_negatives(
    *,
    account: str,
    camp: str,
    source_negs: list[tuple[str, str]],
    comment: str,
) -> list[dict[str, str]]:
    rows = []
    for kw, mt in source_negs:
        rows.append(
            {
                "Account": account,
                "Campaign": camp,
                "Keyword": kw,
                "Match type": mt,
                "Comment": comment,
            }
        )
    return rows


def load_exact_inventory(path: Path, camps: set[str]) -> dict[str, list[tuple[str, str]]]:
    """kw lower -> [(campaign, ad_group), ...] for Exact positives only."""
    out: dict[str, list[tuple[str, str]]] = defaultdict(list)
    if not path.exists():
        return out
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if (row.get("Row Type") or "").strip() != "Keyword":
                continue
            camp = (row.get("Campaign") or "").strip()
            if camp not in camps:
                continue
            if (row.get("Criterion Type") or "").strip().lower() != "exact":
                continue
            if (row.get("Negative") or "").strip().lower() in {"yes", "true", "1"}:
                continue
            kw = (row.get("Keyword") or "").strip().lower()
            ag = (row.get("Ad Group") or "").strip()
            if kw:
                out[kw].append((camp, ag))
    return out


def classify_keyword(kw: str, exact_us: dict, exact_au: dict) -> tuple[str, str]:
    hits = exact_us.get(kw.lower(), []) + exact_au.get(kw.lower(), [])
    if not hits:
        return "unique_quiz", ""
    loc = "; ".join(f"{c}/{a}" for c, a in hits[:4])
    hold = {h[0] for h in OPTIONAL_HOLDOUT}
    if kw.lower() in hold:
        return "optional_holdout", loc
    return "unnecessary_duplicate", loc


def write_overlap_report(
    path: Path,
    *,
    exact_us: dict,
    exact_au: dict,
) -> None:
    included: list[tuple[str, str, str, str]] = []
    for ag in AD_GROUPS:
        for kw in ag["keywords"]:
            klass, loc = classify_keyword(kw, exact_us, exact_au)
            included.append((ag["name"], kw, klass, loc))

    leaked = [(ag, kw, loc) for ag, kw, klass, loc in included if klass != "unique_quiz"]

    lines = [
        "# Quiz keyword overlap vs CORE/ROLES — 2026-08-09",
        "",
        "Source inventories (repo Editor CSVs — **not** a live Ads API dump):",
        "- `ads-launch/google-ads-editor-import-us.csv` · `VC_US_S_CORE` / `VC_US_S_ROLES`",
        "- `ads-launch/google-ads-editor-import-au.csv` · `VC_AU_S_CORE` / `VC_AU_S_ROLES`",
        "",
        "Match compared: **Exact** positives only. Live campaigns were **not** changed.",
        "",
        "Classes:",
        "- **unique_quiz** — not Exact in CORE/ROLES → in quiz import",
        "- **unnecessary_duplicate** — Exact already in CORE/ROLES money groups → **dropped** from quiz import",
        "- **optional_holdout** — quiz-shaped but Exact in CORE → **held out** until George approves",
        "- **intentional_limited_overlap** — none kept in this pass (Exact auction split not worth it)",
        "",
        "This is an **exploratory funnel**, not a statistically controlled A/B test.",
        "",
        "## Included in quiz import (unique_quiz)",
        "",
        "| Ad group | Keyword | Class |",
        "|----------|---------|-------|",
    ]
    for ag, kw, klass, _loc in included:
        lines.append(f"| `{ag}` | `{kw}` | {klass} |")

    lines += [
        "",
        "## Dropped — unnecessary Exact duplicates",
        "",
        "| Would-be AG | Keyword | Already Exact in |",
        "|-------------|---------|------------------|",
    ]
    for kw, ag, why in DROPPED_UNNECESSARY:
        lines.append(f"| `{ag}` | `{kw}` | {why} |")

    lines += [
        "",
        "## Optional holdout (George can add later)",
        "",
        "| Would-be AG | Keyword | Why hold |",
        "|-------------|---------|----------|",
    ]
    for kw, ag, why in OPTIONAL_HOLDOUT:
        lines.append(f"| `{ag}` | `{kw}` | {why} |")

    if leaked:
        lines += [
            "",
            "## Builder leak check",
            "",
            "The following included keywords still match CORE/ROLES Exact — **builder should fail**:",
            "",
        ]
        for ag, kw, loc in leaked:
            lines.append(f"- `{ag}` · `{kw}` · {loc}")

    lines += [
        "",
        "## What this does not do",
        "",
        "- Does not pause, add, or rewrite live CORE/ROLES keywords",
        "- Does not invent a Google Ads Experiment",
        "- Does not clone historical mega negative lists into quiz MMC",
        "  (quiz MMC = Stage 1 CORE employer/job-seeker protections only;",
        "  attach Sniper / Competitors / Job seekers shared lists in Editor — George)",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    if leaked:
        raise SystemExit(
            "Quiz import still contains Exact CORE/ROLES overlap. "
            "Fix AD_GROUPS before shipping CSVs:\n"
            + "\n".join(f"  {ag} · {kw} · {loc}" for ag, kw, loc in leaked)
        )


def validate_import_csv(path: Path, rows: list[dict[str, str]], *, camp: str, final_url: str) -> None:
    errors: list[str] = []
    if path.name.startswith("google-ads-editor-quiz-campaign-negatives"):
        errors.append(f"{path.name}: campaign-negatives file must not use Account Import writer")
    status_by_type = {
        "Campaign": "Campaign Status",
        "Ad group": "Ad Group Status",
        "Keyword": "Keyword Status",
        "Ad": "Ad Status",
    }
    allowed_final = {f"{HOST}/us/quiz", f"{HOST}/au/quiz"}
    for i, r in enumerate(rows, 2):
        rt = (r.get("Row Type") or "").strip()
        if (r.get("Campaign") or "").strip() != camp:
            errors.append(f"{path.name}:{i} campaign must be {camp}")
        field = status_by_type.get(rt)
        if field and (r.get(field) or "").strip() != "Paused":
            errors.append(f"{path.name}:{i} {rt} {field}={r.get(field)!r} (must be Paused)")
        if rt == "Campaign":
            if (r.get("Campaign Type") or "").strip() != "Search":
                errors.append(f"{path.name}:{i} Campaign Type must be Search")
            if (r.get("Bid Strategy Type") or "").strip() != "Maximize Clicks":
                errors.append(f"{path.name}:{i} Bid Strategy must be Maximize Clicks")
            if "lp_variant=quiz" not in (r.get("Final URL suffix") or ""):
                errors.append(f"{path.name}:{i} Final URL suffix missing lp_variant=quiz")
        if rt == "Keyword":
            mt = (r.get("Criterion Type") or "").strip()
            if mt.lower() != "exact":
                errors.append(f"{path.name}:{i} Keyword match must be Exact, got {mt}")
            if (r.get("Negative") or "").strip():
                errors.append(f"{path.name}:{i} do not put campaign negatives in Account Import")
        if rt == "Ad":
            url = (r.get("Final URL") or "").strip()
            if url not in allowed_final:
                errors.append(f"{path.name}:{i} Final URL must be quiz LP, got {url}")
            if url != final_url:
                errors.append(f"{path.name}:{i} Final URL mismatch {url} vs {final_url}")
            if "calendly" in url.lower():
                errors.append(f"{path.name}:{i} Calendly must not be Final URL")
        if rt == "Sitelink":
            if (r.get("Campaign Status") or "").strip() != "Paused":
                errors.append(f"{path.name}:{i} Sitelink Campaign Status must be Paused")
            try:
                validate_sitelink(
                    r.get("Link Text") or "",
                    r.get("Description Line 1") or "",
                    r.get("Description Line 2") or "",
                    r.get("Final URL") or "",
                    f"{path.name}:{i}",
                )
            except SystemExit as exc:
                errors.append(str(exc))
            quiz_lp = f"{HOST}/us/quiz" if camp.endswith("US_S_QUIZ") else f"{HOST}/au/quiz"
            if (r.get("Final URL") or "").strip() == quiz_lp:
                errors.append(f"{path.name}:{i} do not sitelink quiz campaign back to quiz LP")
    if errors:
        raise SystemExit("Quiz import validation failed:\n- " + "\n- ".join(errors))


def validate_mmc_csv(path: Path, rows: list[dict[str, str]], *, camp: str) -> None:
    errors: list[str] = []
    with path.open(encoding="utf-8") as f:
        header = f.readline().strip()
    expected = ",".join(NEG_MMC_FIELDS)
    if header != expected:
        errors.append(f"{path.name}: MMC header must be {expected!r} (not Account Import)")
    if "Row Type" in header:
        errors.append(f"{path.name}: looks like Account Import — use Keywords, Negative → Make multiple changes")
    if not rows:
        errors.append(f"{path.name}: empty negatives")
    for i, r in enumerate(rows, 2):
        if (r.get("Campaign") or "").strip() != camp:
            errors.append(f"{path.name}:{i} campaign must be {camp}")
        if not (r.get("Keyword") or "").strip():
            errors.append(f"{path.name}:{i} missing Keyword")
    if errors:
        raise SystemExit("Quiz MMC negatives validation failed:\n- " + "\n- ".join(errors))


def main() -> None:
    exact_us = load_exact_inventory(
        OUT_DIR / "google-ads-editor-import-us.csv",
        {"VC_US_S_CORE", "VC_US_S_ROLES"},
    )
    exact_au = load_exact_inventory(
        OUT_DIR / "google-ads-editor-import-au.csv",
        {"VC_AU_S_CORE", "VC_AU_S_ROLES"},
    )
    overlap_path = OUT_DIR / "QUIZ-KEYWORD-OVERLAP-2026-08-09.md"
    write_overlap_report(overlap_path, exact_us=exact_us, exact_au=exact_au)

    us_rows = build_market(
        account=US,
        camp="VC_US_S_QUIZ",
        location="United States",
        budget="40",
        cpc="10",
        final_url=f"{HOST}/us/quiz",
        headlines=US_HEADLINES,
        descs=US_DESCS,
    )
    au_rows = build_market(
        account=AU,
        camp="VC_AU_S_QUIZ",
        location="Australia",
        budget="40",
        cpc="6",
        final_url=f"{HOST}/au/quiz",
        headlines=AU_HEADLINES,
        descs=AU_DESCS,
    )

    out_us = OUT_DIR / "google-ads-editor-quiz-import-us.csv"
    out_au = OUT_DIR / "google-ads-editor-quiz-import-au.csv"
    write_csv(out_us, us_rows, HEADERS)
    write_csv(out_au, au_rows, HEADERS)
    validate_import_csv(out_us, us_rows, camp="VC_US_S_QUIZ", final_url=f"{HOST}/us/quiz")
    validate_import_csv(out_au, au_rows, camp="VC_AU_S_QUIZ", final_url=f"{HOST}/au/quiz")

    us_negs_src = load_core_negatives(OUT_DIR / "google-ads-editor-campaign-negatives-us.csv", "VC_US_S_CORE")
    au_negs_src = load_core_negatives(OUT_DIR / "google-ads-editor-campaign-negatives-au.csv", "VC_AU_S_CORE")
    if not us_negs_src:
        raise SystemExit("Missing US CORE campaign negatives to clone (Stage 1 employer/job-seeker list)")
    if not au_negs_src:
        raise SystemExit("Missing AU CORE campaign negatives to clone (Stage 1 employer/job-seeker list)")

    out_neg_us = OUT_DIR / "google-ads-editor-quiz-campaign-negatives-us.csv"
    out_neg_au = OUT_DIR / "google-ads-editor-quiz-campaign-negatives-au.csv"
    us_neg_rows = build_negatives(
        account=US,
        camp="VC_US_S_QUIZ",
        source_negs=us_negs_src,
        comment="Quiz campaign neg · Stage 1 CORE employer/job-seeker protections · MMC only · not mega-list",
    )
    au_neg_rows = build_negatives(
        account=AU,
        camp="VC_AU_S_QUIZ",
        source_negs=au_negs_src,
        comment="Quiz campaign neg · Stage 1 CORE employer/job-seeker protections · MMC only · not mega-list",
    )
    write_csv(out_neg_us, us_neg_rows, NEG_MMC_FIELDS)
    write_csv(out_neg_au, au_neg_rows, NEG_MMC_FIELDS)
    validate_mmc_csv(out_neg_us, us_neg_rows, camp="VC_US_S_QUIZ")
    validate_mmc_csv(out_neg_au, au_neg_rows, camp="VC_AU_S_QUIZ")

    xray_docs = OUT_DIR.parent / "xray" / "docs" / "ads-launch"
    if xray_docs.is_dir():
        (xray_docs / overlap_path.name).write_text(overlap_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"US import: {out_us.name} ({len(us_rows)} rows)")
    print(f"AU import: {out_au.name} ({len(au_rows)} rows)")
    print(f"US negs MMC: {out_neg_us.name} ({len(us_negs_src)} rows)")
    print(f"AU negs MMC: {out_neg_au.name} ({len(au_negs_src)} rows)")
    print(f"Overlap report: {overlap_path.name}")
    print("Campaigns: VC_US_S_QUIZ · VC_AU_S_QUIZ — all Paused. No API mutate.")
    print("Validation: all statuses Paused · RSA final URLs quiz-only · sitelinks microsite · MMC ≠ Account Import.")


if __name__ == "__main__":
    main()
