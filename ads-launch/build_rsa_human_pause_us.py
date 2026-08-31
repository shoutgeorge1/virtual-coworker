#!/usr/bin/env python3
"""Build Editor CSV: pause old weak RSAs in VC_US_S_ROLES groups getting new human ads.

No Ads API. CTR from on-disk `_us_rsa_probe.json` (LAST_14_DAYS, before 2026-08-10
human in-place updates). Pause old EA/VA/PH/DKI copy; keep CTR winners and the
Aug 10 rewritten ads that are already serving.

Google's 3-ad cap counts paused ads. After this import, remove the paused rows
in Editor, then import `google-ads-editor-rsa-add-human-us.csv`.

Usage:
  python3 ads-launch/build_rsa_human_pause_us.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "_us_rsa_probe.json"
OUT_CSV = HERE / "google-ads-editor-rsa-pause-weak-us.csv"
OUT_MD = HERE / "RSA-HUMAN-PAUSE-ADD-US-2026-08-12.md"
ADD_CSV = HERE / "google-ads-editor-rsa-add-human-us.csv"
US = "496-715-1855"

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

# One pause per new ad (2 in Administration_EA_PH). Prefer CTR < 5% old
# abbrev/DKI copy. Do not pause Aug 10 rewritten ads or real CTR winners.
# CTR source: ads-launch/_us_rsa_probe.json LAST_14_DAYS.
PAUSE_PLAN: list[dict] = [
    {
        "ad_id": "820036923820",
        "ad_group": "Administration_EA_PH",
        "why": "CTR below 5% · old EA/VA copy",
    },
    {
        "ad_id": "820036923823",
        "ad_group": "Administration_EA_PH",
        "why": "CTR below 5% · old DKI + EA copy",
    },
    {
        "ad_id": "820036923832",
        "ad_group": "Accounting_Hire_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036923961",
        "ad_group": "Accounting_Outsource_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036923970",
        "ad_group": "Bookkeeping_Hire_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036923979",
        "ad_group": "Bookkeeping_Outsource_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036923994",
        "ad_group": "Customer_Service_Hire_PH",
        "why": "CTR below 5% · old CS/abbrev copy",
    },
    {
        "ad_id": "820036924003",
        "ad_group": "Customer_Service_Outsource_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036923787",
        "ad_group": "Digital_Marketing_Hire_PH",
        "why": "old copy / make room for human RSAs (above 5%; DKI/VA; 20% winner kept)",
    },
    {
        "ad_id": "820036923793",
        "ad_group": "Digital_Marketing_Outsource_PH",
        "why": "old copy / make room for human RSAs (3 impr noise; old PH; 50% seat kept)",
    },
    {
        "ad_id": "820036923802",
        "ad_group": "Social_Media_Hire_PH",
        "why": "CTR below 5% · old VA/SMM copy",
    },
    {
        "ad_id": "820036923814",
        "ad_group": "Social_Media_Outsource_PH",
        "why": "old copy / make room for human RSAs (just over 5%; old PH/SMM; 20% winner kept)",
    },
    {
        "ad_id": "820036924006",
        "ad_group": "Human_Resources_Hire_PH",
        "why": "CTR below 5% · old HR/VA copy",
    },
    {
        "ad_id": "820036924015",
        "ad_group": "Human_Resources_Outsource_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036924024",
        "ad_group": "Recruitment_Hire_PH",
        "why": "CTR below 5% · old VA/PH copy (18.6% DKI winner kept)",
    },
    {
        "ad_id": "820036924036",
        "ad_group": "Recruitment_Outsource_PH",
        "why": "CTR below 5% · old PH abbrev copy",
    },
    {
        "ad_id": "820036924042",
        "ad_group": "Sales_Hire_PH",
        "why": "CTR below 5% · old PH abbrev copy (12.5% DKI winner kept)",
    },
    {
        "ad_id": "820036924051",
        "ad_group": "Sales_Outsource_PH",
        "why": "old copy / make room for human RSAs",
    },
    {
        "ad_id": "820314203428",
        "ad_group": "Appointment_Setter_Hire_PH",
        "why": "CTR below 5% · old PH/DKI copy",
    },
]


def texts(items: list) -> list[str]:
    out = []
    for item in items:
        if isinstance(item, dict):
            out.append(item.get("text") or "")
        else:
            out.append(str(item))
    return out


def load_probe_by_id() -> dict[str, dict]:
    data = json.loads(PROBE.read_text())
    by_id = {}
    for rsa in data["rsas"]:
        by_id[str(rsa["ad_id"])] = rsa
    return by_id


def blank_row() -> dict[str, str]:
    return {h: "" for h in HEADERS}


def rsa_to_row(rsa: dict, why: str) -> dict[str, str]:
    headlines = texts(rsa["headlines"])
    descs = texts(rsa["descriptions"])
    urls = rsa.get("final_urls") or []
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
            "Final URL": urls[0] if urls else "",
            "Path 1": rsa.get("path1") or "",
            "Path 2": rsa.get("path2") or "",
            "Comment": (
                f"Pause old RSA 2026-08-12; {why}; "
                "Campaign/Ad Group Status blank (live-US-safe); "
                f"ad_id={rsa['ad_id']}"
            ),
        }
    )
    for i, h in enumerate(headlines, 1):
        r[f"Headline {i}"] = h
    for i, d in enumerate(descs, 1):
        r[f"Description {i}"] = d
    return r


def write_markdown(rows_meta: list[dict]) -> None:
    add_n = sum(1 for _ in ADD_CSV.open(encoding="utf-8")) - 1
    lines = [
        "# Pause weak RSAs + add human RSAs — US ROLES · 2026-08-12",
        "",
        "**Account:** `496-715-1855`  ",
        "**Campaign:** `VC_US_S_ROLES` only (Brand untouched. CORE skipped.)  ",
        "**Pause CSV:** `ads-launch/google-ads-editor-rsa-pause-weak-us.csv`  ",
        "**Add CSV:** `ads-launch/google-ads-editor-rsa-add-human-us.csv`  ",
        "**Regenerator:** `python3 ads-launch/build_rsa_human_pause_us.py`",
        "",
        "No Ads API. New ads stay **Paused**. Do not Enable from these files.",
        "",
        "## CTR source",
        "",
        "Per-ad CTR from `ads-launch/_us_rsa_probe.json` (`LAST_14_DAYS`, pulled before the 2026-08-10 in-place human updates). Executive creative snapshot (last 7 days, 2026-08-10) matches the same ad ids where it has rows. No live API dump this pass.",
        "",
        "Aug 10 rewrites kept the same ad ids, so their probe CTR is the **old** copy. Those rewritten ads are **not** in this pause file. Winners at or above 5% CTR are kept.",
        "",
        "## 3-ad cap",
        "",
        "Google allows **3 ads per ad group**, and **paused ads still count**. Importing pause then add will not fit until the paused old ads are **removed** in Editor. Pause first so you can see which rows to delete; then add.",
        "",
        f"Pause rows: **{len(rows_meta)}**. Add rows: **{add_n}** (all Paused).",
        "",
        "## Ads paused",
        "",
        "| Ad group | Headline 1 | Probe CTR | Why |",
        "|----------|------------|-----------|-----|",
    ]
    for m in rows_meta:
        h1 = m["h1"].replace("|", "/")
        lines.append(
            f"| `{m['ad_group']}` | {h1} | {m['ctr_label']} | {m['why']} |"
        )
    lines.extend(
        [
            "",
            "## Kept (not paused)",
            "",
            "- CTR winners in these groups (Recruiting DKI 18.6%, Sales DKI 12.5%, CS hire 13.3%, CS outsource 16%, social outsource 20%, marketing hire 20%, books outsource 7.9%, books hire DKI 7.1%, accounting hire DKI 25%, marketing outsource 50% on tiny sample, HR hire shortlist 50% on 2 impr).",
            "- Aug 10 rewritten ads already serving (human-ish copy on the old ad ids).",
            "- CORE and Brand. `Admin_City_Test`.",
            "",
            "## Import (do not Enable)",
            "",
            "1. Editor → USA account (`496-715-1855`) → **Get recent changes**.",
            "2. **Account → Import → From file…** → `google-ads-editor-rsa-pause-weak-us.csv`",
            f"3. Preview should show **{len(rows_meta)} Ad changes** to **Paused** (not campaign/ad group status). Post.",
            "4. In each ad group in the table, **remove** those paused old ads (3-ad cap). Admin needs **2** removed; every other group in the table needs **1**.",
            "5. **Account → Import → From file…** → `google-ads-editor-rsa-add-human-us.csv`",
            f"6. Preview should show **{add_n} Ad adds**, all **Paused**. Post. Enable only after you like them.",
            "",
            "Do not import `google-ads-editor-rsa-add-admin-us.csv` on top — those two admin ads are already in the human add file.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    by_id = load_probe_by_id()
    rows: list[dict[str, str]] = []
    meta: list[dict] = []
    seen: set[str] = set()

    for plan in PAUSE_PLAN:
        ad_id = plan["ad_id"]
        if ad_id in seen:
            raise SystemExit(f"duplicate pause ad_id {ad_id}")
        seen.add(ad_id)
        rsa = by_id.get(ad_id)
        if not rsa:
            raise SystemExit(f"ad_id {ad_id} not in probe")
        if rsa["campaign"] != "VC_US_S_ROLES":
            raise SystemExit(f"{ad_id} is not VC_US_S_ROLES")
        if rsa["ad_group"] != plan["ad_group"]:
            raise SystemExit(
                f"{ad_id} group {rsa['ad_group']} != {plan['ad_group']}"
            )
        rows.append(rsa_to_row(rsa, plan["why"]))
        headlines = texts(rsa["headlines"])
        ctr = rsa.get("ctr")
        impr = rsa.get("impr") or 0
        clicks = rsa.get("clicks") or 0
        if impr:
            ctr_label = f"{ctr * 100:.1f}% ({impr} impr / {clicks} clicks)"
        else:
            ctr_label = "0% (0 impr)"
        meta.append(
            {
                "ad_group": rsa["ad_group"],
                "h1": headlines[0] if headlines else "",
                "ctr_label": ctr_label,
                "why": plan["why"],
            }
        )

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)

    write_markdown(meta)
    print(f"Wrote {OUT_CSV}")
    print(f"  pause rows={len(rows)} · all Ad Status=Paused")
    print(f"Wrote {OUT_MD}")
    for m in meta:
        print(f"  {m['ad_group']}: {m['h1'][:40]} · {m['ctr_label']}")


if __name__ == "__main__":
    main()
