#!/usr/bin/env python3
"""Build xray Ads package overview from Stage 1 Editor CSVs.

Reads:
  ads-launch/google-ads-editor-import-us.csv
  ads-launch/google-ads-editor-import-au.csv
  ads-launch/google-ads-editor-campaign-negatives-us.csv / -au.csv (MMC negs)
  ads-launch/phase1-enable-manifest-us.csv / -au.csv (tier counts)
  NEGATIVE_REVIEW_HOLDOUT from build_stage1_editor_package.py

Writes:
  xray/data/ads-package.json
  xray/ads-package.html

Display names (dashboard only):
  Editor campaign / ad group IDs stay unchanged in import CSVs.
  This builder adds human `display_name` fields for the overview UI.
  See DISPLAY_NAME_MAP / campaign_display() / ad_group_display().

Run standalone, or via build_stage1_editor_package.main() after CSV regen.
"""

from __future__ import annotations

import csv
import html
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADS = ROOT / "ads-launch"
XRAY = ROOT / "xray"
OUT_JSON = XRAY / "data" / "ads-package.json"
OUT_HTML = XRAY / "ads-package.html"

US_CSV = ADS / "google-ads-editor-import-us.csv"
AU_CSV = ADS / "google-ads-editor-import-au.csv"
US_NEG_CSV = ADS / "google-ads-editor-campaign-negatives-us.csv"
AU_NEG_CSV = ADS / "google-ads-editor-campaign-negatives-au.csv"
MANIFEST_US = ADS / "phase1-enable-manifest-us.csv"
MANIFEST_AU = ADS / "phase1-enable-manifest-au.csv"

# USA account Editor local DB (Get recent changes → then read). No Ads API.
EDITOR_US_DB = (
    Path.home()
    / "Library/Application Support/Google/Google-AdWords-Editor/749/ape_4967151855.db"
)
# Editor enums (do not swap): Exact=2, Phrase=1, Broad=0; Enabled=0, Paused=1
_MATCH = {0: "Broad", 1: "Phrase", 2: "Exact"}
_STATUS = {0: "Enabled", 1: "Paused"}

ACCOUNT_LABELS = {
    "496-715-1855": "US",
    "573-539-1940": "AU",
}

# Dashboard-only labels. Editor CSV entity names stay technical for import stability.
CAMPAIGN_DISPLAY = {
    "VC_US_S_CORE": "US · Core Search",
    "VC_US_S_ROLES": "US · Role Search",
    "VC_AU_S_CORE": "AU · Core Search",
    "VC_AU_S_ROLES": "AU · Role Search",
}

# Full AG overrides when underscore-split looks awkward.
AD_GROUP_DISPLAY = {
    "Hire_VA_PH": "Virtual Assistant · Hire",
    "Offshore_VA_PH": "Offshore VA · Core",
    "Administration_EA_PH": "Administration · EA",
    "Admin_City_Test": "Admin · City Test",
    "Digital_Marketing_Hire_PH": "Digital Marketing · Hire",
    "Digital_Marketing_Outsource_PH": "Digital Marketing · Outsource",
    "Customer_Service_Hire_PH": "Customer Service · Hire",
    "Customer_Service_Outsource_PH": "Customer Service · Outsource",
    "Human_Resources_Hire_PH": "Human Resources · Hire",
    "Human_Resources_Outsource_PH": "Human Resources · Outsource",
    "Social_Media_Hire_PH": "Social Media · Hire",
    "Social_Media_Outsource_PH": "Social Media · Outsource",
    "Accounting_Hire_PH": "Accounting · Hire",
    "Accounting_Outsource_PH": "Accounting · Outsource",
    "Bookkeeping_Hire_PH": "Bookkeeping · Hire",
    "Bookkeeping_Outsource_PH": "Bookkeeping · Outsource",
    "Recruitment_Hire_PH": "Recruitment · Hire",
    "Recruitment_Outsource_PH": "Recruitment · Outsource",
    "Sales_Hire_PH": "Sales · Hire",
    "Sales_Outsource_PH": "Sales · Outsource",
}


def campaign_display(name: str) -> str:
    """Human label for operators; falls back to technical name."""
    return CAMPAIGN_DISPLAY.get(name, name.replace("_", " · "))


def ad_group_display(name: str) -> str:
    """Readable AG label, e.g. Digital Marketing · Hire (not Digital_Marketing_Hire_PH)."""
    if name in AD_GROUP_DISPLAY:
        return AD_GROUP_DISPLAY[name]
    raw = name[:-3] if name.endswith("_PH") else name
    for suffix, label in (("_Hire", "Hire"), ("_Outsource", "Outsource")):
        if raw.endswith(suffix):
            role = raw[: -len(suffix)].replace("_", " ")
            return f"{role} · {label}"
    return raw.replace("_", " ")


def _load_holdouts() -> list[str]:
    sys.path.insert(0, str(ADS))
    from build_stage1_editor_package import NEGATIVE_REVIEW_HOLDOUT  # type: ignore

    return list(NEGATIVE_REVIEW_HOLDOUT)


def read_live_ops_from_editor(db_path: Path = EDITOR_US_DB) -> dict:
    """Snapshot VC_US_* keyword reality from local Google Ads Editor DB."""
    if not db_path.exists():
        return {
            "available": False,
            "note": f"Editor DB not found: {db_path}",
        }
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    camps = con.execute(
        """
        SELECT name, status, budgetAmount/1000000.0 AS budget,
               maxCpcBidCeiling/1000000.0 AS max_cpc
        FROM Campaign WHERE name LIKE 'VC_%'
        ORDER BY name
        """
    ).fetchall()
    kw_rows = con.execute(
        """
        SELECT c.name AS campaign, k.criterionType, k.status, COUNT(*) AS n
        FROM Keyword k
        JOIN AdGroup a ON a.localId = (k.parentId & 0xFFFFFFFF)
        JOIN Campaign c ON c.localId = (a.parentId & 0xFFFFFFFF)
        WHERE c.name LIKE 'VC_%'
        GROUP BY c.name, k.criterionType, k.status
        ORDER BY c.name, k.criterionType, k.status
        """
    ).fetchall()
    paused_exact = con.execute(
        """
        SELECT COUNT(*) FROM Keyword k
        JOIN AdGroup a ON a.localId = (k.parentId & 0xFFFFFFFF)
        JOIN Campaign c ON c.localId = (a.parentId & 0xFFFFFFFF)
        WHERE c.name LIKE 'VC_%' AND k.criterionType = 2 AND k.status = 1
        """
    ).fetchone()[0]
    enabled_exact = con.execute(
        """
        SELECT COUNT(*) FROM Keyword k
        JOIN AdGroup a ON a.localId = (k.parentId & 0xFFFFFFFF)
        JOIN Campaign c ON c.localId = (a.parentId & 0xFFFFFFFF)
        WHERE c.name LIKE 'VC_%' AND k.criterionType = 2 AND k.status = 0
        """
    ).fetchone()[0]
    phrase_paused = con.execute(
        """
        SELECT COUNT(*) FROM Keyword k
        JOIN AdGroup a ON a.localId = (k.parentId & 0xFFFFFFFF)
        JOIN Campaign c ON c.localId = (a.parentId & 0xFFFFFFFF)
        WHERE c.name LIKE 'VC_%' AND k.criterionType = 1 AND k.status = 1
        """
    ).fetchone()[0]
    phrase_enabled = con.execute(
        """
        SELECT COUNT(*) FROM Keyword k
        JOIN AdGroup a ON a.localId = (k.parentId & 0xFFFFFFFF)
        JOIN Campaign c ON c.localId = (a.parentId & 0xFFFFFFFF)
        WHERE c.name LIKE 'VC_%' AND k.criterionType = 1 AND k.status = 0
        """
    ).fetchone()[0]
    mtime = datetime.fromtimestamp(db_path.stat().st_mtime, tz=timezone.utc)
    campaigns = []
    for name, status, budget, max_cpc in camps:
        campaigns.append(
            {
                "name": name,
                "display_name": campaign_display(name),
                "status": _STATUS.get(status, str(status)),
                "budget": budget,
                "max_cpc": max_cpc,
            }
        )
    breakdown = []
    for camp, ctype, status, n in kw_rows:
        breakdown.append(
            {
                "campaign": camp,
                "match": _MATCH.get(ctype, str(ctype)),
                "status": _STATUS.get(status, str(status)),
                "count": n,
            }
        )
    return {
        "available": True,
        "source": str(db_path),
        "db_mtime_utc": mtime.strftime("%Y-%m-%d %H:%M UTC"),
        "account": "496-715-1855",
        "market": "US",
        "campaigns": campaigns,
        "keyword_breakdown": breakdown,
        "counts": {
            "exact_enabled": enabled_exact,
            "exact_paused": paused_exact,
            "phrase_enabled": phrase_enabled,
            "phrase_paused": phrase_paused,
        },
        "policy": {
            "match": "Exact-only bidding live (all Phrase paused)",
            "au_mirror": (
                "AU package mirrors USA pause curation (LIVE_PAUSED + PHRASE_HOLD); "
                "AU campaigns not live yet"
            ),
            "measurement": (
                "Phone = guiding light until Zoho offline qualify; "
                "Max Clicks meantime; prefer phone over form spam"
            ),
            "brand": (
                "Brand paused by George 2026-08-07 (~$1k/lead; SEO owns brand) "
                "— deferred; don’t re-enable"
            ),
        },
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _nonempty(row: dict[str, str], *keys: str) -> list[str]:
    out = []
    for k in keys:
        v = (row.get(k) or "").strip()
        if v:
            out.append(v)
    return out


def _headlines(row: dict[str, str]) -> list[str]:
    return _nonempty(row, *[f"Headline {i}" for i in range(1, 16)])


def _descriptions(row: dict[str, str]) -> list[str]:
    return _nonempty(row, *[f"Description {i}" for i in range(1, 5)])


def _url_pattern(urls: list[str]) -> str:
    if not urls:
        return "—"
    hosts = sorted({u.split("?")[0].rstrip("/") for u in urls if u})
    if len(hosts) == 1:
        return hosts[0]
    # Collapse shared prefix
    markets = sorted({u.split("/")[3] if len(u.split("/")) > 3 else u for u in hosts})
    bases = sorted({"/".join(u.split("/")[:4]) for u in hosts})
    if len(bases) == 1:
        return bases[0] + "/*"
    if len(set(m for m in markets if m in ("us", "au"))) == 1:
        m = markets[0]
        return f"https://vision-three-alpha.vercel.app/{m}/…"
    return f"{len(hosts)} Final URLs"


def _tier_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    rows = _read_csv(path)
    # Column name may vary slightly
    key = None
    if rows:
        for c in rows[0]:
            if c.lower().replace(" ", "") in ("enabletier", "tier"):
                key = c
                break
        if key is None:
            for c in rows[0]:
                if "tier" in c.lower():
                    key = c
                    break
    if not key:
        return {}
    c = Counter((r.get(key) or "").strip() for r in rows)
    return dict(sorted(c.items(), key=lambda kv: kv[0]))


def _is_campaign_neg(r: dict[str, str]) -> bool:
    if (r.get("Criterion Type") or "").strip().lower() == "campaign negative":
        return True
    # MMC negatives CSV (Keywords, Negative → Make multiple changes)
    return bool((r.get("Match type") or "").strip()) and bool(
        (r.get("Keyword") or "").strip()
    ) and bool((r.get("Campaign") or "").strip()) and not (
        r.get("Row Type") or ""
    ).strip()


def _is_positive_kw(r: dict[str, str]) -> bool:
    if (r.get("Row Type") or "") != "Keyword":
        return False
    if _is_campaign_neg(r):
        return False
    if (r.get("Negative") or "").strip().lower() == "true":
        return False
    return (r.get("Criterion Type") or "").strip().lower() in {"exact", "phrase", "broad"}


def parse_market(
    rows: list[dict[str, str]], market: str, neg_rows: list[dict[str, str]] | None = None
) -> dict:
    neg_rows = neg_rows or []
    by_type: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in rows:
        by_type[r.get("Row Type") or ""].append(r)

    campaign_negs = [
        r
        for r in (*rows, *neg_rows)
        if _is_campaign_neg(r)
        or (r.get("Row Type") or "") == "Campaign negative keyword"
    ]

    campaigns = []
    for r in by_type["Campaign"]:
        cname = r["Campaign"]
        ads = [a for a in by_type["Ad"] if a["Campaign"] == cname]
        urls = [a["Final URL"] for a in ads if a.get("Final URL")]
        ags = [a for a in by_type["Ad group"] if a["Campaign"] == cname]
        kws = [k for k in by_type["Keyword"] if k["Campaign"] == cname and _is_positive_kw(k)]
        negs = [n for n in campaign_negs if n["Campaign"] == cname]
        campaigns.append(
            {
                "name": cname,
                "display_name": campaign_display(cname),
                "account": market,
                "account_id": r.get("Account") or "",
                "budget": r.get("Budget") or "",
                "budget_type": r.get("Budget type") or "Daily",
                "bid_strategy": r.get("Bid Strategy Type") or "",
                "max_cpc": r.get("Maximum CPC bid limit") or "",
                "status": r.get("Campaign Status") or "",
                "networks": r.get("Networks") or "",
                "location": r.get("Location") or "",
                "tracking_template": r.get("Tracking template") or "",
                "final_url_suffix": r.get("Final URL suffix") or "",
                "final_url_pattern": _url_pattern(urls),
                "ad_group_count": len(ags),
                "keyword_count": len(kws),
                "rsa_count": len(ads),
                "negative_count": len(negs),
                "comment": (r.get("Comment") or "").strip(),
            }
        )

    ad_groups = []
    for r in by_type["Ad group"]:
        cname, ag = r["Campaign"], r["Ad Group"]
        kws = [
            k
            for k in by_type["Keyword"]
            if k["Campaign"] == cname and k["Ad Group"] == ag and _is_positive_kw(k)
        ]
        ads = [
            a for a in by_type["Ad"] if a["Campaign"] == cname and a["Ad Group"] == ag
        ]
        urls = [a["Final URL"] for a in ads if a.get("Final URL")]
        match = Counter((k.get("Criterion Type") or "") for k in kws)
        ad_groups.append(
            {
                "campaign": cname,
                "campaign_display": campaign_display(cname),
                "name": ag,
                "display_name": ad_group_display(ag),
                "status": r.get("Ad Group Status") or "",
                "keyword_count": len(kws),
                "exact": match.get("Exact", 0),
                "phrase": match.get("Phrase", 0),
                "rsa_count": len(ads),
                "final_url": urls[0] if urls else "",
                "final_urls": sorted(set(urls)),
            }
        )

    keywords = []
    for r in by_type["Keyword"]:
        if not _is_positive_kw(r):
            continue
        cname, ag = r["Campaign"], r["Ad Group"]
        keywords.append(
            {
                "campaign": cname,
                "campaign_display": campaign_display(cname),
                "ad_group": ag,
                "ad_group_display": ad_group_display(ag),
                "keyword": r.get("Keyword") or "",
                "match": r.get("Criterion Type") or "",
                "status": r.get("Keyword Status") or "",
            }
        )

    rsas = []
    for r in by_type["Ad"]:
        hs, ds = _headlines(r), _descriptions(r)
        cname, ag = r["Campaign"], r["Ad Group"]
        rsas.append(
            {
                "campaign": cname,
                "campaign_display": campaign_display(cname),
                "ad_group": ag,
                "ad_group_display": ad_group_display(ag),
                "status": r.get("Ad Status") or "",
                "ad_type": r.get("Ad type") or "",
                "final_url": r.get("Final URL") or "",
                "path1": r.get("Path 1") or "",
                "path2": r.get("Path 2") or "",
                "headlines": hs,
                "descriptions": ds,
                "headline_count": len(hs),
                "description_count": len(ds),
            }
        )

    negatives = sorted(
        {
            (r.get("Keyword") or "").strip()
            for r in campaign_negs
            if (r.get("Keyword") or "").strip()
        }
    )
    neg_match = Counter(
        (r.get("Criterion Type") or r.get("Match type") or "") for r in campaign_negs
    )

    sitelinks = []
    for r in by_type["Sitelink"]:
        sitelinks.append(
            {
                "campaign": r["Campaign"],
                "link_text": r.get("Link Text") or "",
                "final_url": r.get("Final URL") or "",
                "desc1": r.get("Description Line 1") or "",
                "desc2": r.get("Description Line 2") or "",
            }
        )

    callouts = []
    for r in by_type["Callout"]:
        callouts.append(
            {
                "campaign": r["Campaign"],
                "text": r.get("Callout text") or "",
            }
        )

    snippets = []
    for r in by_type["Structured snippet"]:
        snippets.append(
            {
                "campaign": r["Campaign"],
                "header": r.get("Header") or "",
                "values": r.get("Snippet Values") or "",
            }
        )

    # Deduplicate assets (same asset repeated per campaign)
    uniq_sitelinks = []
    seen_sl = set()
    for s in sitelinks:
        key = (s["link_text"], s["final_url"])
        if key in seen_sl:
            continue
        seen_sl.add(key)
        uniq_sitelinks.append(s)

    uniq_callouts = []
    seen_co = set()
    for c in callouts:
        if c["text"] in seen_co:
            continue
        seen_co.add(c["text"])
        uniq_callouts.append(c)

    uniq_snippets = []
    seen_sn = set()
    for s in snippets:
        key = (s["header"], s["values"])
        if key in seen_sn:
            continue
        seen_sn.add(key)
        uniq_snippets.append(s)

    camp0 = by_type["Campaign"][0] if by_type["Campaign"] else {}
    return {
        "market": market,
        "account_id": camp0.get("Account") or "",
        "campaigns": campaigns,
        "ad_groups": ad_groups,
        "keywords": keywords,
        "rsas": rsas,
        "negatives": negatives,
        "negative_row_count": len(campaign_negs),
        "negative_match_types": dict(neg_match),
        "sitelinks": uniq_sitelinks,
        "sitelink_row_count": len(sitelinks),
        "callouts": uniq_callouts,
        "callout_row_count": len(callouts),
        "structured_snippets": uniq_snippets,
        "snippet_row_count": len(snippets),
        "tracking_template": camp0.get("Tracking template") or "",
        "final_url_suffix": camp0.get("Final URL suffix") or "",
        "counts": {
            "campaigns": len(campaigns),
            "ad_groups": len(ad_groups),
            "keywords": len(keywords),
            "rsas": len(rsas),
            "unique_negatives": len(negatives),
            "negative_rows": len(campaign_negs),
        },
    }


def _csv_pause_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    """Counts from package CSV comments / match types (import still all Paused)."""
    live_paused = 0
    phrase = 0
    exact = 0
    for r in rows:
        if not _is_positive_kw(r):
            continue
        mt = (r.get("Criterion Type") or "").strip()
        if mt == "Phrase":
            phrase += 1
        elif mt == "Exact":
            exact += 1
        if "VC_Keywords_Paused_Live" in (r.get("Comment") or ""):
            live_paused += 1
    return {
        "exact_rows": exact,
        "phrase_rows": phrase,
        "live_paused_tagged": live_paused,
    }


def build_package() -> dict:
    holdouts = _load_holdouts()
    us_rows = _read_csv(US_CSV)
    au_rows = _read_csv(AU_CSV)
    us_negs = _read_csv(US_NEG_CSV) if US_NEG_CSV.exists() else []
    au_negs = _read_csv(AU_NEG_CSV) if AU_NEG_CSV.exists() else []
    us = parse_market(us_rows, "US", us_negs)
    au = parse_market(au_rows, "AU", au_negs)
    tiers_us = _tier_counts(MANIFEST_US)
    tiers_au = _tier_counts(MANIFEST_AU)
    live = read_live_ops_from_editor()
    us_pause = _csv_pause_counts(us_rows)
    au_pause = _csv_pause_counts(au_rows)

    name_map = {
        "note": (
            "Display names are dashboard-only. Google Ads Editor CSV campaign and "
            "ad group names stay technical for import accuracy — do not rename "
            "entities in the CSV based on this table."
        ),
        "campaigns": [
            {"editor": k, "display": v} for k, v in sorted(CAMPAIGN_DISPLAY.items())
        ],
        "ad_groups": [
            {"editor": k, "display": v} for k, v in sorted(AD_GROUP_DISPLAY.items())
        ],
    }

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source_files": [
            str(US_CSV.relative_to(ROOT)),
            str(AU_CSV.relative_to(ROOT)),
        ],
        "display_name_map": name_map,
        "live_ops": live,
        "package_curation": {
            "us": us_pause,
            "au": au_pause,
            "note": (
                "Editor import CSVs still ship every row Paused (Import ≠ Enable). "
                "LIVE_PAUSED tags + PHRASE_HOLD tiers mirror USA Editor curation "
                "so AU does not re-enable junk later."
            ),
        },
        "safety": {
            "status": "Paused",
            "banner": "CSV package · all Paused · SAFE TO IMPORT FOR REVIEW",
            "note": (
                "Import ≠ Post ≠ Enable. Live USA VC_* is already spending "
                "(see Live ops). Do not bulk-Enable CSV rows that are LIVE_PAUSED "
                "or PHRASE_HOLD."
            ),
        },
        "holdouts": {
            "label": "Commercial / employer-research holdouts (NOT in import CSVs)",
            "terms": holdouts,
            "count": len(holdouts),
            "why": "Held out so cost/review/comparison/rate employer research is not blocked pre-launch. Competitor-named review terms stay in active negatives.",
        },
        "phase1_tiers": {
            "us": tiers_us,
            "au": tiers_au,
            "docs": [
                {"label": "PHASE1-REVIEW.md", "href": "docs/ads-launch/PHASE1-REVIEW.md"},
                {
                    "label": "PHASED-ACTIVATION.md",
                    "href": "docs/ads-launch/PHASED-ACTIVATION.md",
                },
                {
                    "label": "phase1-enable-manifest-us.csv",
                    "href": "docs/ads-launch/phase1-enable-manifest-us.csv",
                },
                {
                    "label": "phase1-enable-manifest-au.csv",
                    "href": "docs/ads-launch/phase1-enable-manifest-au.csv",
                },
            ],
        },
        "markets": {"US": us, "AU": au},
        "totals": {
            "campaigns": us["counts"]["campaigns"] + au["counts"]["campaigns"],
            "ad_groups": us["counts"]["ad_groups"] + au["counts"]["ad_groups"],
            "keywords": us["counts"]["keywords"] + au["counts"]["keywords"],
            "rsas": us["counts"]["rsas"] + au["counts"]["rsas"],
            "unique_negatives_per_market": us["counts"]["unique_negatives"],
            "negative_rows_total": us["counts"]["negative_rows"]
            + au["counts"]["negative_rows"],
            "holdouts": len(holdouts),
        },
    }


def _esc(s: object) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def _live_ops_html(live: dict, curation: dict) -> str:
    if not live.get("available"):
        return (
            "<div class='notice' style='margin-top:1rem'>"
            f"<p><strong>Live ops:</strong> {_esc(live.get('note') or 'Editor DB unavailable')}</p>"
            "</div>"
        )
    counts = live.get("counts") or {}
    policy = live.get("policy") or {}
    camp_lis = "".join(
        "<li><strong>{dn}</strong> · {st} · ${b:.0f}/day · max CPC ${c:.0f}</li>".format(
            dn=_esc(c.get("display_name") or c["name"]),
            st=_esc(c.get("status")),
            b=float(c.get("budget") or 0),
            c=float(c.get("max_cpc") or 0),
        )
        for c in live.get("campaigns") or []
    )
    us_c = curation.get("us") or {}
    au_c = curation.get("au") or {}
    return f"""
      <section class="panel" id="live-ops" style="margin-top:1rem;border-color:var(--tint-teal-edge)">
        <div class="panel-hd" style="background:var(--tint-teal-hd)">
          <p class="kicker">USA Editor DB · {_esc(live.get('db_mtime_utc'))}</p>
          <h2>Live ops (what’s actually spending)</h2>
          <span class="badge badge-ok">US live</span>
        </div>
        <div class="panel-bd">
          <ul class="short-bullets">
            <li><strong>Campaigns:</strong></li>
          </ul>
          <ul class="short-bullets" style="margin-top:0">{camp_lis}</ul>
          <ul class="short-bullets" style="margin-top:0.65rem">
            <li><strong>Exact Enabled:</strong> {counts.get('exact_enabled', '—')} ·
              <strong>Exact Paused:</strong> {counts.get('exact_paused', '—')}</li>
            <li><strong>Phrase:</strong> {counts.get('phrase_paused', '—')} paused ·
              {counts.get('phrase_enabled', 0)} enabled
              <span class="dim">({_esc(policy.get('match', 'Exact-only'))})</span></li>
            <li><strong>AU package:</strong> {_esc(policy.get('au_mirror', ''))}</li>
            <li><strong>Measurement:</strong> {_esc(policy.get('measurement', ''))}</li>
            <li class="dim">{_esc(policy.get('brand', ''))}</li>
          </ul>
          <p class="muted" style="margin:0.75rem 0 0;font-size:0.86rem">
            Package CSV tags (still all Paused for import):
            US LIVE_PAUSED rows <strong>{us_c.get('live_paused_tagged', '—')}</strong> ·
            AU <strong>{au_c.get('live_paused_tagged', '—')}</strong>
            (mirrored). Phrase → PHRASE_HOLD in enable manifests.
          </p>
        </div>
      </section>
    """


def render_html(pkg: dict) -> str:
    data_json = json.dumps(pkg, ensure_ascii=False, separators=(",", ":"))
    t = pkg["totals"]
    us, au = pkg["markets"]["US"], pkg["markets"]["AU"]
    holdouts = pkg["holdouts"]["terms"]
    tiers_us = pkg["phase1_tiers"]["us"]
    tiers_au = pkg["phase1_tiers"]["au"]
    live = pkg.get("live_ops") or {}
    curation = pkg.get("package_curation") or {}
    live_html = _live_ops_html(live, curation)

    # Campaign rows — package CSV status + live note for US
    live_by_name = {
        c["name"]: c for c in (live.get("campaigns") or []) if live.get("available")
    }
    camp_rows = []
    for mkt in ("US", "AU"):
        for c in pkg["markets"][mkt]["campaigns"]:
            dname = c.get("display_name") or campaign_display(c["name"])
            live_c = live_by_name.get(c["name"])
            if live_c:
                st_badge = (
                    f"<span class='badge badge-ok'>{_esc(live_c['status'])} live</span>"
                    f"<br /><span class='dim'>CSV import: Paused</span>"
                )
                max_cpc = live_c.get("max_cpc") or c["max_cpc"]
            else:
                st_badge = "<span class='badge badge-high'>Paused</span>"
                if mkt == "AU":
                    st_badge += "<br /><span class='dim'>not live · mirrors US pauses</span>"
                max_cpc = c["max_cpc"]
            camp_rows.append(
                "<tr>"
                f"<td><span class='name-display'>{_esc(dname)}</span>"
                f"<code class='name-tech'>{_esc(c['name'])}</code></td>"
                f"<td>{_esc(c['account'])}<br /><span class='dim'>{_esc(c['account_id'])}</span></td>"
                f"<td>${_esc(c['budget'])} {_esc(c['budget_type']).lower()}</td>"
                f"<td>{_esc(c['bid_strategy'])}</td>"
                f"<td>${_esc(max_cpc)}</td>"
                f"<td>{st_badge}</td>"
                f"<td><code class='url'>{_esc(c['final_url_pattern'])}</code></td>"
                f"<td class='num'>{c['ad_group_count']}</td>"
                f"<td class='num'>{c['keyword_count']}</td>"
                f"<td class='num'>{c['rsa_count']}</td>"
                "</tr>"
            )

    map_camp_rows = "".join(
        f"<tr><td><span class='name-display'>{_esc(r['display'])}</span></td>"
        f"<td><code class='name-tech'>{_esc(r['editor'])}</code></td></tr>"
        for r in pkg.get("display_name_map", {}).get("campaigns", [])
    )
    map_ag_rows = "".join(
        f"<tr><td><span class='name-display'>{_esc(r['display'])}</span></td>"
        f"<td><code class='name-tech'>{_esc(r['editor'])}</code></td></tr>"
        for r in pkg.get("display_name_map", {}).get("ad_groups", [])
    )
    map_note = _esc(
        pkg.get("display_name_map", {}).get(
            "note",
            "Display names are dashboard-only; Editor CSV names stay technical.",
        )
    )

    holdout_lis = "".join(f"<li><code>{_esc(t)}</code></li>" for t in holdouts)
    neg_lis = "".join(f"<li><code>{_esc(t)}</code></li>" for t in us["negatives"])

    # Assets from US (same creative shape; URLs differ by market — show both)
    sl_rows = []
    for mkt in ("US", "AU"):
        for s in pkg["markets"][mkt]["sitelinks"]:
            sl_rows.append(
                f"<tr><td>{_esc(mkt)}</td><td>{_esc(s['link_text'])}</td>"
                f"<td><code class='url'>{_esc(s['final_url'])}</code></td>"
                f"<td>{_esc(s['desc1'])} · {_esc(s['desc2'])}</td></tr>"
            )
    # Deduplicate display by link_text+url
    # Actually show unique across markets
    seen = set()
    sl_html = []
    for row_html, key in zip(
        sl_rows,
        [
            (m, s["link_text"], s["final_url"])
            for m in ("US", "AU")
            for s in pkg["markets"][m]["sitelinks"]
        ],
    ):
        if key in seen:
            continue
        seen.add(key)
        sl_html.append(row_html)

    callout_items = []
    seen_c = set()
    for mkt in ("US", "AU"):
        for c in pkg["markets"][mkt]["callouts"]:
            if c["text"] in seen_c:
                continue
            seen_c.add(c["text"])
            callout_items.append(f"<li>{_esc(c['text'])}</li>")

    snippet_items = []
    seen_s = set()
    for mkt in ("US", "AU"):
        for s in pkg["markets"][mkt]["structured_snippets"]:
            key = (s["header"], s["values"])
            if key in seen_s:
                continue
            seen_s.add(key)
            snippet_items.append(
                f"<li><strong>{_esc(s['header'])}</strong> — {_esc(s['values'])}</li>"
            )

    tier_rows = []
    all_tiers = sorted(set(tiers_us) | set(tiers_au))
    for tier in all_tiers:
        tier_rows.append(
            f"<tr><td><strong>{_esc(tier)}</strong></td>"
            f"<td class='num'>{tiers_us.get(tier, 0)}</td>"
            f"<td class='num'>{tiers_au.get(tier, 0)}</td></tr>"
        )

    tracking = us.get("tracking_template") or "{lpurl}"
    suffix = us.get("final_url_suffix") or ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>Ads package · Virtual Coworker Search Pilot</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    .safety-banner {{
      margin-top: 0.85rem;
      padding: 0.85rem 1.05rem;
      border-radius: 8px;
      border: 1px solid var(--tint-amber-edge);
      background: var(--tint-amber);
      color: var(--ink);
    }}
    .safety-banner strong {{
      display: block;
      font-size: 0.95rem;
      letter-spacing: 0.01em;
      margin-bottom: 0.25rem;
    }}
    .safety-banner p {{ margin: 0; font-size: 0.88rem; color: var(--body); }}
    .pkg-toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 0.65rem;
      align-items: center;
      margin: 0 0 0.75rem;
    }}
    .pkg-toolbar label {{
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .pkg-toolbar select,
    .pkg-toolbar input[type="search"] {{
      font: inherit;
      font-size: 0.88rem;
      padding: 0.35rem 0.5rem;
      border: 1px solid var(--edge);
      border-radius: 6px;
      background: var(--panel);
      color: var(--ink);
      min-width: 10rem;
    }}
    .pkg-toolbar input[type="search"] {{ min-width: 14rem; flex: 1; }}
    .tab-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin: 0 0 0.75rem;
    }}
    .tab-row button {{
      font: inherit;
      font-size: 0.82rem;
      font-weight: 600;
      padding: 0.35rem 0.65rem;
      border-radius: 6px;
      border: 1px solid var(--edge);
      background: var(--panel);
      color: var(--body);
      cursor: pointer;
    }}
    .tab-row button[aria-pressed="true"] {{
      background: var(--tint-teal-hd);
      border-color: var(--tint-teal-edge);
      color: var(--ink);
    }}
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.86rem;
    }}
    .data-table th,
    .data-table td {{
      text-align: left;
      padding: 0.45rem 0.5rem;
      border-bottom: 1px solid var(--edge-soft);
      vertical-align: top;
    }}
    .data-table th {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--dim);
      font-weight: 700;
      background: var(--panel-inset);
      position: sticky;
      top: 0;
    }}
    .data-table td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    .data-table code.url {{
      font-size: 0.72rem;
      word-break: break-all;
    }}
    .dim {{ color: var(--dim); font-size: 0.75rem; }}
    .scroll-box {{
      max-height: 22rem;
      overflow: auto;
      border: 1px solid var(--edge-soft);
      border-radius: 6px;
      background: var(--panel);
    }}
    .scroll-box.tall {{ max-height: 28rem; }}
    .neg-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.85rem;
    }}
    @media (max-width: 860px) {{
      .neg-grid {{ grid-template-columns: 1fr; }}
    }}
    .chip-list {{
      list-style: none;
      margin: 0;
      padding: 0;
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }}
    .chip-list li {{
      margin: 0;
      padding: 0.2rem 0.45rem;
      border: 1px solid var(--edge-soft);
      border-radius: 4px;
      background: var(--panel);
      font-size: 0.8rem;
    }}
    .chip-list.holdout li {{
      border-color: var(--tint-amber-edge);
      background: var(--tint-amber);
    }}
    .ag-block {{
      border: 1px solid var(--edge-soft);
      border-radius: 6px;
      background: var(--panel);
      margin: 0 0 0.5rem;
    }}
    .ag-block summary {{
      cursor: pointer;
      padding: 0.55rem 0.75rem;
      font-size: 0.88rem;
      font-weight: 600;
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem 0.75rem;
      align-items: baseline;
    }}
    .ag-block summary::-webkit-details-marker {{ display: none; }}
    .ag-block summary .meta {{
      font-weight: 500;
      color: var(--muted);
      font-size: 0.8rem;
    }}
    .ag-block .ag-bd {{
      padding: 0 0.75rem 0.75rem;
      border-top: 1px solid var(--edge-soft);
    }}
    .rsa-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.65rem;
      margin-top: 0.55rem;
    }}
    @media (max-width: 760px) {{
      .rsa-grid {{ grid-template-columns: 1fr; }}
    }}
    .rsa-card {{
      border: 1px solid var(--edge-soft);
      border-radius: 6px;
      padding: 0.55rem 0.65rem;
      background: var(--panel-inset);
      font-size: 0.82rem;
    }}
    .rsa-card h4 {{
      margin: 0 0 0.35rem;
      font-size: 0.8rem;
      color: var(--ink);
    }}
    .rsa-card ol {{
      margin: 0;
      padding-left: 1.1rem;
    }}
    .rsa-card li {{ margin: 0.1rem 0; }}
    .count-note {{
      font-size: 0.84rem;
      color: var(--muted);
      margin: 0 0 0.55rem;
    }}
    .empty-msg {{
      padding: 0.75rem;
      color: var(--muted);
      font-size: 0.88rem;
    }}
    .name-display {{
      display: block;
      font-weight: 600;
      font-size: 0.95rem;
      letter-spacing: -0.01em;
      color: var(--ink);
    }}
    .name-tech {{
      display: inline-block;
      margin-top: 0.2rem;
      font-size: 0.72rem;
      font-weight: 500;
      letter-spacing: 0.01em;
      color: var(--muted);
      background: transparent;
      padding: 0;
    }}
    .ag-block summary .name-display {{
      flex: 1 1 auto;
      min-width: 10rem;
    }}
    .short-bullets {{
      list-style: none;
      margin: 0;
      padding: 0;
    }}
    .short-bullets li {{
      padding: 0.28rem 0;
      border-bottom: 1px solid var(--edge-soft);
      font-size: 0.9rem;
      line-height: 1.4;
    }}
    .short-bullets li:last-child {{ border-bottom: none; }}
    .badge-ok {{
      background: var(--tint-green-hd);
      border: 1px solid var(--tint-green-edge);
      color: var(--ink);
    }}
  </style>
</head>
<body data-page="ads-package.html" data-foot="US live Exact-only<br />AU mirrors pauses · CSV Paused">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="page-head">
        <p class="kicker">Live USA Editor + Stage 1 CSV · {_esc(pkg['generated_at'])}</p>
        <h1>Ads package</h1>
        <p>
          Top = what’s live in USA Ads (from local Editor DB). Below = Paused
          import CSVs for review / AU mirror. Exact-only bidding; junk Exact + all
          Phrase stay Paused so AU import doesn’t re-enable them.
        </p>
      </header>

      <div class="safety-banner" role="status">
        <strong>{_esc(pkg['safety']['banner'])}</strong>
        <p>{_esc(pkg['safety']['note'])}</p>
      </div>

      {live_html}

      <div class="stats stats-4" style="margin-top:1rem;border:1px solid var(--tint-teal-edge);border-radius:8px;overflow:hidden">
        <div class="stat">
          <p class="lbl">Campaigns</p>
          <p class="val">{t['campaigns']}</p>
          <p class="sub">US live · AU paused</p>
        </div>
        <div class="stat">
          <p class="lbl">Keywords</p>
          <p class="val">{t['keywords']}</p>
          <p class="sub">{us['counts']['keywords']} per market CSV</p>
        </div>
        <div class="stat">
          <p class="lbl">Exact live</p>
          <p class="val">{(live.get('counts') or {}).get('exact_enabled', '—')}</p>
          <p class="sub">{(live.get('counts') or {}).get('exact_paused', '—')} Exact paused</p>
        </div>
        <div class="stat">
          <p class="lbl">Phrase</p>
          <p class="val">{(live.get('counts') or {}).get('phrase_paused', '—')}</p>
          <p class="sub">all paused · Exact-only</p>
        </div>
      </div>

      <section class="panel" id="campaigns">
        <div class="panel-hd">
          <p class="kicker">Structure</p>
          <h2>Campaigns</h2>
          <span class="badge badge-high">Paused</span>
        </div>
        <div class="panel-bd">
          <div class="scroll-box">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Campaign</th>
                  <th>Account</th>
                  <th>Budget</th>
                  <th>Bid</th>
                  <th>Max CPC</th>
                  <th>Status</th>
                  <th>Final URL pattern</th>
                  <th>AGs</th>
                  <th>KWs</th>
                  <th>RSAs</th>
                </tr>
              </thead>
              <tbody>
                {''.join(camp_rows)}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section class="panel" id="name-map">
        <div class="panel-hd">
          <p class="kicker">Dashboard display layer</p>
          <h2>Name map</h2>
          <span class="badge badge-info">Import IDs unchanged</span>
        </div>
        <div class="panel-bd">
          <p class="muted" style="margin:0 0 0.85rem;font-size:0.88rem">{map_note}</p>
          <div class="neg-grid">
            <div>
              <h3 style="margin:0 0 0.45rem;font-size:0.92rem">Campaigns</h3>
              <div class="scroll-box" style="max-height:14rem">
                <table class="data-table">
                  <thead><tr><th>Display</th><th>Editor</th></tr></thead>
                  <tbody>{map_camp_rows}</tbody>
                </table>
              </div>
            </div>
            <div>
              <h3 style="margin:0 0 0.45rem;font-size:0.92rem">Ad groups</h3>
              <div class="scroll-box tall">
                <table class="data-table">
                  <thead><tr><th>Display</th><th>Editor</th></tr></thead>
                  <tbody>{map_ag_rows}</tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="panel" id="ad-groups">
        <div class="panel-hd">
          <p class="kicker">Under each campaign</p>
          <h2>Ad groups</h2>
          <span class="badge badge-info">{t['ad_groups']} total</span>
        </div>
        <div class="panel-bd">
          <div class="pkg-toolbar">
            <label for="ag-market">Market</label>
            <select id="ag-market">
              <option value="US">US</option>
              <option value="AU">AU</option>
            </select>
            <label for="ag-campaign">Campaign</label>
            <select id="ag-campaign"></select>
          </div>
          <div id="ag-list"></div>
        </div>
      </section>

      <section class="panel" id="keywords">
        <div class="panel-hd">
          <p class="kicker">Browsable · not a wall</p>
          <h2>Keywords</h2>
          <span class="badge badge-info" id="kw-count-badge">—</span>
        </div>
        <div class="panel-bd">
          <div class="tab-row" id="kw-market-tabs" role="tablist">
            <button type="button" data-market="US" aria-pressed="true">US ({us['counts']['keywords']})</button>
            <button type="button" data-market="AU" aria-pressed="false">AU ({au['counts']['keywords']})</button>
          </div>
          <div class="pkg-toolbar">
            <label for="kw-campaign">Campaign</label>
            <select id="kw-campaign"></select>
            <label for="kw-ag">Ad group</label>
            <select id="kw-ag"></select>
            <label for="kw-match">Match</label>
            <select id="kw-match">
              <option value="">All</option>
              <option value="Exact">Exact</option>
              <option value="Phrase">Phrase</option>
            </select>
            <input type="search" id="kw-search" placeholder="Filter keywords…" autocomplete="off" />
          </div>
          <p class="count-note" id="kw-filter-note"></p>
          <div class="scroll-box tall">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Keyword</th>
                  <th>Match</th>
                  <th>Ad group</th>
                  <th>Campaign</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody id="kw-tbody"></tbody>
            </table>
            <p class="empty-msg" id="kw-empty" hidden>No keywords match this filter.</p>
          </div>
        </div>
      </section>

      <section class="panel" id="rsas">
        <div class="panel-hd">
          <p class="kicker">Responsive search ads</p>
          <h2>RSAs</h2>
          <span class="badge badge-info">15 headlines · 4 descriptions</span>
        </div>
        <div class="panel-bd">
          <p class="muted" style="margin:0 0 0.75rem;font-size:0.88rem">
            Each ad group has RSAs built to the 15H / 4D Editor target. Expand an ad group to read copy.
          </p>
          <div class="pkg-toolbar">
            <label for="rsa-market">Market</label>
            <select id="rsa-market">
              <option value="US">US</option>
              <option value="AU">AU</option>
            </select>
            <label for="rsa-campaign">Campaign</label>
            <select id="rsa-campaign"></select>
            <input type="search" id="rsa-search" placeholder="Filter ad group…" autocomplete="off" />
          </div>
          <div id="rsa-list"></div>
        </div>
      </section>

      <section class="panel" id="negatives">
        <div class="panel-hd">
          <p class="kicker">VC-only curated · not shared mega lists</p>
          <h2>Negatives</h2>
          <span class="badge badge-high">{us['counts']['unique_negatives']} unique · campaign-level Broad</span>
        </div>
        <div class="panel-bd">
          <p class="muted" style="margin:0 0 0.75rem;font-size:0.88rem">
            Same {us['counts']['unique_negatives']} terms attached to every <code>VC_*</code> campaign
            ({us['counts']['negative_rows']} rows per market × 2 campaigns).
            Not account shared / PM_* mega lists.
          </p>
          <div class="neg-grid">
            <div>
              <h3 style="margin:0 0 0.45rem;font-size:0.92rem">In import (active)</h3>
              <div class="scroll-box tall">
                <ul class="chip-list" style="padding:0.55rem">{neg_lis}</ul>
              </div>
            </div>
            <div>
              <h3 style="margin:0 0 0.45rem;font-size:0.92rem">Holdouts (not imported)</h3>
              <p class="muted" style="margin:0 0 0.45rem;font-size:0.82rem">{_esc(pkg['holdouts']['why'])}</p>
              <ul class="chip-list holdout">{holdout_lis}</ul>
            </div>
          </div>
        </div>
      </section>

      <section class="panel" id="assets">
        <div class="panel-hd">
          <p class="kicker">Extensions</p>
          <h2>Assets</h2>
        </div>
        <div class="panel-bd">
          <h3 style="margin:0 0 0.4rem;font-size:0.92rem">Sitelinks</h3>
          <div class="scroll-box" style="margin-bottom:1rem">
            <table class="data-table">
              <thead>
                <tr><th>Mkt</th><th>Link text</th><th>Final URL</th><th>Descriptions</th></tr>
              </thead>
              <tbody>{''.join(sl_html)}</tbody>
            </table>
          </div>
          <div class="neg-grid">
            <div>
              <h3 style="margin:0 0 0.4rem;font-size:0.92rem">Callouts</h3>
              <ul class="chip-list">{''.join(callout_items)}</ul>
            </div>
            <div>
              <h3 style="margin:0 0 0.4rem;font-size:0.92rem">Structured snippets</h3>
              <ul style="margin:0;padding-left:1.1rem;font-size:0.88rem">{''.join(snippet_items)}</ul>
            </div>
          </div>
        </div>
      </section>

      <section class="panel" id="tracking">
        <div class="panel-hd">
          <p class="kicker">UTM · Final URL suffix</p>
          <h2>Tracking template</h2>
        </div>
        <div class="panel-bd">
          <p style="margin:0 0 0.5rem"><strong>Template:</strong> <code>{_esc(tracking)}</code></p>
          <p style="margin:0 0 0.5rem"><strong>Final URL suffix:</strong></p>
          <p style="margin:0"><code style="font-size:0.78rem;word-break:break-all">{_esc(suffix)}</code></p>
          <p class="muted" style="margin:0.65rem 0 0;font-size:0.86rem">
            Same suffix on all four campaigns. <code>lp_version=stage1-v7</code> stamps package generation.
            No third-party click trackers in the Editor CSV.
          </p>
        </div>
      </section>

      <section class="panel" id="phase1">
        <div class="panel-hd">
          <p class="kicker">Review ladder · still Paused</p>
          <h2>Phase 1 manifests / tiers</h2>
        </div>
        <div class="panel-bd">
          <p class="muted" style="margin:0 0 0.65rem;font-size:0.88rem">
            Enable order for later — these are <strong>not</strong> Enabled import files.
            Review 1A → 1B; Enable only after TRAFFIC READY + explicit approval.
          </p>
          <div class="scroll-box" style="margin-bottom:0.75rem;max-height:14rem">
            <table class="data-table">
              <thead><tr><th>Tier</th><th>US</th><th>AU</th></tr></thead>
              <tbody>{''.join(tier_rows)}</tbody>
            </table>
          </div>
          <p style="margin:0;font-size:0.88rem">
            <a href="docs/ads-launch/PHASE1-REVIEW.md">PHASE1-REVIEW.md</a> ·
            <a href="docs/ads-launch/PHASED-ACTIVATION.md">PHASED-ACTIVATION.md</a> ·
            <a href="docs/ads-launch/phase1-enable-manifest-us.csv">manifest US</a> ·
            <a href="docs/ads-launch/phase1-enable-manifest-au.csv">manifest AU</a> ·
            <a href="docs/ads-launch/EDITOR-PREFLIGHT-REPORT.md">Editor preflight</a>
          </p>
        </div>
      </section>

      <div class="notice notice-quiet" style="margin-top:1.15rem">
        <p>
          <strong>Regenerate:</strong>
          <code>python3 ads-launch/build_xray_ads_overview.py</code>
          (also runs at the end of
          <code>python3 ads-launch/build_stage1_editor_package.py</code>).
        </p>
      </div>
    </main>
  </div>

  <script type="application/json" id="ads-package-data">{data_json}</script>
  <script src="nav.js"></script>
  <script>
  (function () {{
    var pkg = JSON.parse(document.getElementById("ads-package-data").textContent);
    var markets = pkg.markets;

    function el(id) {{ return document.getElementById(id); }}
    function clear(node) {{ while (node.firstChild) node.removeChild(node.firstChild); }}

    function fillSelect(select, items, allLabel) {{
      clear(select);
      if (allLabel) {{
        var o = document.createElement("option");
        o.value = "";
        o.textContent = allLabel;
        select.appendChild(o);
      }}
      items.forEach(function (item) {{
        var o = document.createElement("option");
        if (typeof item === "string") {{
          o.value = item;
          o.textContent = item;
        }} else {{
          o.value = item.value;
          o.textContent = item.label;
        }}
        select.appendChild(o);
      }});
    }}

    function campLabel(c) {{
      return c.display_name || c.name;
    }}

    function agLabel(a) {{
      return a.display_name || a.name;
    }}

    function campaignOptions(mkt) {{
      return markets[mkt].campaigns.map(function (c) {{
        return {{ value: c.name, label: campLabel(c) }};
      }});
    }}

    function agOptions(mkt, campaign) {{
      return markets[mkt].ad_groups
        .filter(function (a) {{ return !campaign || a.campaign === campaign; }})
        .map(function (a) {{
          return {{ value: a.name, label: agLabel(a) }};
        }});
    }}

    /* —— Ad groups —— */
    var agMarket = el("ag-market");
    var agCampaign = el("ag-campaign");
    var agList = el("ag-list");

    function renderAGs() {{
      var mkt = agMarket.value;
      var camp = agCampaign.value;
      var rows = markets[mkt].ad_groups.filter(function (a) {{
        return !camp || a.campaign === camp;
      }});
      clear(agList);
      rows.forEach(function (a) {{
        var d = document.createElement("details");
        d.className = "ag-block";
        var s = document.createElement("summary");
        s.innerHTML =
          "<span class='name-display'>" + agLabel(a) + "</span>" +
          "<code class='name-tech'>" + a.name + "</code>" +
          "<span class='meta'>" + (a.campaign_display || a.campaign) + "</span>" +
          "<span class='meta'>" + a.keyword_count + " KW · " +
          a.exact + " Exact · " + a.phrase + " Phrase · " +
          a.rsa_count + " RSA</span>" +
          "<span class='meta'>" + (a.final_url || "—") + "</span>";
        d.appendChild(s);
        var bd = document.createElement("div");
        bd.className = "ag-bd";
        bd.innerHTML =
          "<p class='muted' style='margin:0.55rem 0 0;font-size:0.84rem'>Status: <strong>" +
          a.status + "</strong>" +
          (a.final_urls && a.final_urls.length > 1
            ? " · Final URLs: " + a.final_urls.map(function (u) {{ return "<code>" + u + "</code>"; }}).join(" · ")
            : "") +
          "</p>";
        d.appendChild(bd);
        agList.appendChild(d);
      }});
    }}

    function syncAgCampaign() {{
      fillSelect(agCampaign, campaignOptions(agMarket.value), "All campaigns");
      renderAGs();
    }}
    agMarket.addEventListener("change", syncAgCampaign);
    agCampaign.addEventListener("change", renderAGs);
    syncAgCampaign();

    /* —— Keywords —— */
    var kwMarket = "US";
    var kwCampaign = el("kw-campaign");
    var kwAg = el("kw-ag");
    var kwMatch = el("kw-match");
    var kwSearch = el("kw-search");
    var kwTbody = el("kw-tbody");
    var kwEmpty = el("kw-empty");
    var kwNote = el("kw-filter-note");
    var kwBadge = el("kw-count-badge");

    function syncKwFilters() {{
      fillSelect(kwCampaign, campaignOptions(kwMarket), "All campaigns");
      fillSelect(kwAg, agOptions(kwMarket, kwCampaign.value), "All ad groups");
      renderKeywords();
    }}

    function renderKeywords() {{
      var camp = kwCampaign.value;
      var ag = kwAg.value;
      var match = kwMatch.value;
      var q = (kwSearch.value || "").trim().toLowerCase();
      var rows = markets[kwMarket].keywords.filter(function (k) {{
        if (camp && k.campaign !== camp) return false;
        if (ag && k.ad_group !== ag) return false;
        if (match && k.match !== match) return false;
        if (q && k.keyword.toLowerCase().indexOf(q) === -1) return false;
        return true;
      }});
      clear(kwTbody);
      var MAX = 400;
      var show = rows.slice(0, MAX);
      show.forEach(function (k) {{
        var tr = document.createElement("tr");
        tr.innerHTML =
          "<td><code>" + k.keyword + "</code></td>" +
          "<td>" + k.match + "</td>" +
          "<td><span class='name-display'>" + (k.ad_group_display || k.ad_group) + "</span>" +
          "<code class='name-tech'>" + k.ad_group + "</code></td>" +
          "<td><span class='name-display'>" + (k.campaign_display || k.campaign) + "</span>" +
          "<code class='name-tech'>" + k.campaign + "</code></td>" +
          "<td><span class='badge badge-high'>" + k.status + "</span></td>";
        kwTbody.appendChild(tr);
      }});
      kwEmpty.hidden = rows.length > 0;
      kwBadge.textContent = rows.length + " shown";
      kwNote.textContent =
        rows.length + " keyword" + (rows.length === 1 ? "" : "s") +
        " · " + kwMarket +
        (rows.length > MAX ? " (showing first " + MAX + " — narrow filter)" : "");
    }}

    document.getElementById("kw-market-tabs").addEventListener("click", function (e) {{
      var btn = e.target.closest("button[data-market]");
      if (!btn) return;
      kwMarket = btn.getAttribute("data-market");
      Array.prototype.forEach.call(
        document.querySelectorAll("#kw-market-tabs button"),
        function (b) {{ b.setAttribute("aria-pressed", b === btn ? "true" : "false"); }}
      );
      syncKwFilters();
    }});
    kwCampaign.addEventListener("change", function () {{
      fillSelect(kwAg, agOptions(kwMarket, kwCampaign.value), "All ad groups");
      renderKeywords();
    }});
    kwAg.addEventListener("change", renderKeywords);
    kwMatch.addEventListener("change", renderKeywords);
    kwSearch.addEventListener("input", renderKeywords);
    syncKwFilters();

    /* —— RSAs —— */
    var rsaMarket = el("rsa-market");
    var rsaCampaign = el("rsa-campaign");
    var rsaSearch = el("rsa-search");
    var rsaList = el("rsa-list");

    function renderRSAs() {{
      var mkt = rsaMarket.value;
      var camp = rsaCampaign.value;
      var q = (rsaSearch.value || "").trim().toLowerCase();
      var byAg = {{}};
      markets[mkt].rsas.forEach(function (ad) {{
        if (camp && ad.campaign !== camp) return;
        var hay = ((ad.ad_group_display || "") + " " + ad.ad_group).toLowerCase();
        if (q && hay.indexOf(q) === -1) return;
        var key = ad.campaign + "||" + ad.ad_group;
        if (!byAg[key]) byAg[key] = [];
        byAg[key].push(ad);
      }});
      clear(rsaList);
      Object.keys(byAg).sort().forEach(function (key) {{
        var parts = key.split("||");
        var ads = byAg[key];
        var d = document.createElement("details");
        d.className = "ag-block";
        var first = ads[0];
        var s = document.createElement("summary");
        s.innerHTML =
          "<span class='name-display'>" + (first.ad_group_display || parts[1]) + "</span>" +
          "<code class='name-tech'>" + parts[1] + "</code>" +
          "<span class='meta'>" + (first.campaign_display || parts[0]) + "</span>" +
          "<span class='meta'>" + ads.length + " RSA · " +
          first.headline_count + "H / " + first.description_count + "D</span>" +
          "<span class='meta'>" + (first.final_url || "") + "</span>";
        d.appendChild(s);
        var bd = document.createElement("div");
        bd.className = "ag-bd";
        var grid = document.createElement("div");
        grid.className = "rsa-grid";
        ads.forEach(function (ad, idx) {{
          var card = document.createElement("div");
          card.className = "rsa-card";
          var hHtml = ad.headlines.map(function (h) {{ return "<li>" + h + "</li>"; }}).join("");
          var dHtml = ad.descriptions.map(function (x) {{ return "<li>" + x + "</li>"; }}).join("");
          card.innerHTML =
            "<h4>RSA " + (idx + 1) + " · " + ad.headline_count + "H / " + ad.description_count + "D · " + ad.status + "</h4>" +
            "<p class='dim' style='margin:0 0 0.35rem'>Paths: " +
            (ad.path1 || "—") + " / " + (ad.path2 || "—") + "</p>" +
            "<strong>Headlines</strong><ol>" + hHtml + "</ol>" +
            "<strong style='display:block;margin-top:0.4rem'>Descriptions</strong><ol>" + dHtml + "</ol>";
          grid.appendChild(card);
        }});
        bd.appendChild(grid);
        d.appendChild(bd);
        rsaList.appendChild(d);
      }});
      if (!rsaList.firstChild) {{
        rsaList.innerHTML = "<p class='empty-msg'>No RSAs match.</p>";
      }}
    }}

    function syncRsaCampaign() {{
      fillSelect(rsaCampaign, campaignOptions(rsaMarket.value), "All campaigns");
      renderRSAs();
    }}
    rsaMarket.addEventListener("change", syncRsaCampaign);
    rsaCampaign.addEventListener("change", renderRSAs);
    rsaSearch.addEventListener("input", renderRSAs);
    syncRsaCampaign();
  }})();
  </script>
</body>
</html>
"""


def main() -> None:
    if not US_CSV.exists() or not AU_CSV.exists():
        raise SystemExit(f"Missing Editor CSVs under {ADS}")
    pkg = build_package()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(
        json.dumps(pkg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    OUT_HTML.write_text(render_html(pkg), encoding="utf-8")
    t = pkg["totals"]
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUT_HTML.relative_to(ROOT)}")
    print(
        f"Totals: {t['campaigns']} campaigns · {t['ad_groups']} AGs · "
        f"{t['keywords']} keywords · {t['rsas']} RSAs · "
        f"{t['unique_negatives_per_market']} unique negs · "
        f"{t['holdouts']} holdouts"
    )


if __name__ == "__main__":
    main()
