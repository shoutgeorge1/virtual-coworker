#!/usr/bin/env python3
"""Compile forensic recovery-audit JSON + CSVs from on-disk + Ads reads.

Read-only. No Ads API. Run after pull_forensic_recovery*.py and crawl_legacy_lps.py.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

REPO = Path(__file__).resolve().parents[1]
OUT_JSON = REPO / "xray" / "data" / "recovery-audit.json"
OUT_DIR = REPO / "xray" / "data" / "recovery"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def money(n: Any) -> float:
    try:
        return round(float(n or 0), 2)
    except (TypeError, ValueError):
        return 0.0


def canon_url(url: str) -> str:
    if not url:
        return ""
    raw = url.strip()
    raw = re.sub(r"\{ignore\}.*$", "", raw, flags=re.I)
    raw = raw.split("?")[0].split("#")[0]
    p = urlparse(raw)
    host = (p.netloc or "").lower().removeprefix("www.")
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    scheme = "https"
    return urlunparse((scheme, host, path, "", "", ""))


def host_class(url: str) -> str:
    u = (url or "").lower()
    if "virtualcoworker.app" in u:
        return "app_paid"
    if "try.virtualcoworker.com" in u:
        return "try"
    if "/lp-" in u or "/lp/" in u:
        return "wp_lp_dead_or_fb"
    if "virtualcoworker.com.ph" in u:
        return "ph_jobs"
    if "virtualcoworker.com.au" in u:
        if "/contact" in u:
            return "wp_contact"
        if u.rstrip("/").endswith("virtualcoworker.com.au"):
            return "wp_home"
        return "wp_services_or_content"
    if "virtualcoworker.com" in u:
        if "/contact" in u:
            return "wp_contact"
        if u.rstrip("/").endswith("virtualcoworker.com"):
            return "wp_home"
        return "wp_services_or_content"
    return "other"


def classify_conversion(row: dict[str, Any], metrics: dict[str, Any] | None) -> dict[str, str]:
    name = (row.get("name") or "")
    n = name.lower()
    t = (row.get("type") or "")
    cat = (row.get("category") or "")
    primary = bool(row.get("primary_for_goal"))
    include = bool(row.get("include_in_conversions_metric"))

    quality = "unverifiable"
    confidence = "uncertain"
    note = ""

    if "searching for a job" in n or "job seeker" in n:
        quality = "job-seeker activity"
        confidence = "confirmed job seeker"
        note = "Job-seeker click was counted as a conversion."
    elif "ebook" in n or "page_view" in n:
        quality = "page view or engagement signal"
        confidence = "duplicate-non-lead"
        note = "Not an employer lead."
    elif "chat opened" in n or "chat started" in n:
        quality = "page view or engagement signal"
        confidence = "duplicate-non-lead"
        note = "Chat widget engagement, not a lead."
    elif "gtm_submit_button_click" in n or n.endswith(" (web) click"):
        quality = "page view or engagement signal"
        confidence = "duplicate-non-lead"
        note = "Button/page click import."
    elif t == "CLICK_TO_CALL" or "phone_click" in n or "phone_call_clicks" in n:
        quality = "phone click or other micro-conversion"
        confidence = "duplicate-non-lead"
        note = "Tap ≠ 60s consult. Not a qualified lead."
    elif t in ("AD_CALL", "WEBSITE_CALL") or "calls from ads" in n or "website # phone" in n or "phone calls" in n:
        quality = "qualified-duration phone call"
        confidence = "uncertain"
        note = "Call duration may be 60s on new VC_* actions; legacy * names are unverified. Caller could still be a job seeker."
    elif "zoho jo" in n or "job order" in n or "converted job orders" in n:
        quality = "likely qualified employer lead"
        confidence = "uncertain"
        note = "Closest CRM-shaped signal. Zoho inventory is incomplete — cannot confirm these are real employer job orders. Zapier and Standard OCI duplicates exist."
    elif "discovery scheduled" in n or "calendly" in n or "call booked" in n or "meeting scheduled" in n:
        quality = "form submission of uncertain quality"
        confidence = "probable employer"
        note = "Appointment/schedule signal. Not proof the booker was an employer or that the call happened."
    elif "thank_you" in n or "thank you" in n or "free consultation form" in n or "contact us form" in n or "form_submit" in n or "form submission" in n or t in ("WEBPAGE", "LEAD_FORM_SUBMIT") and "SUBMIT" in cat:
        if "vc_us_thank_you" in n or "vc_au_thank_you" in n:
            quality = "form submission of uncertain quality"
            confidence = "uncertain"
            note = "Current .app thank-you. GA4 thank-you hits in this window are internal testing — not employer leads."
        else:
            quality = "form submission of uncertain quality"
            confidence = "uncertain"
            note = "WP consult/contact form. Dual-door Job radio + .ph nav. No CRM proof."
    elif "purchase" in n or "close_convert" in n or "qualify_lead" in n:
        quality = "unverifiable"
        confidence = "duplicate-non-lead"
        note = "GA4 auto-import. Meaning changed or empty."
    elif "offline" in n or "zapier" in n or "oci" in n:
        quality = "duplicate or overlapping tracking"
        confidence = "uncertain"
        note = "Offline/Zapier/OCI. Often overlaps a twin action."
    elif "universal_analytics" in t.lower() or t.startswith("UNIVERSAL"):
        quality = "obsolete legacy conversion"
        confidence = "duplicate-non-lead"
        note = "Old UA goal. Do not use for bidding."
    else:
        quality = "unverifiable"
        confidence = "uncertain"
        note = "Name/type not enough to trust."

    if include and primary and quality in (
        "page view or engagement signal",
        "phone click or other micro-conversion",
        "job-seeker activity",
    ):
        note += " Historically Primary / included in Conversions — inflated Smart Bidding."

    m = metrics or {}
    return {
        "quality": quality,
        "confidence": confidence,
        "note": note.strip(),
        "conversions": m.get("conversions", 0) or 0,
        "all_conversions": m.get("all_conversions", 0) or 0,
    }


def campaign_cohort(name: str) -> str:
    n = name or ""
    if n.startswith("VC_US_") or n.startswith("VC_AU_"):
        return "stage1"
    if "Brand" in n:
        return "brand_deferred"
    if "PERFORMANCE" in n or "Performance Max" in n or "PMax" in n:
        return "pmax"
    if "DSA" in n:
        return "dsa"
    if "Competitor" in n:
        return "competitor"
    if n.startswith("PM_"):
        return "pm_rsa"
    if n.startswith("LK -"):
        return "lk_agency"
    if n.startswith("[Original]") or n.startswith("NA -") or n.startswith("APAC"):
        return "original"
    return "legacy_other"


def trustworthy_note(camp: dict[str, Any], market: str) -> tuple[str, str]:
    cohort = campaign_cohort(camp["name"])
    if cohort == "stage1":
        if market == "US":
            return (
                "0 Ads conversions in the 2y window (campaign is new). Sales ops 8–10 Aug: 4 enquiries, 2 booked calls, 1 job seeker, 1 not-a-fit. Not a historical nugget.",
                "probable employer",
            )
        return (
            "New Stage 1. No ops enquiry counts yet. Ads conversions 0. Do not read empty Conversions as failure of the market.",
            "uncertain",
        )
    if cohort == "brand_deferred":
        return (
            "Brand classified only. High all-conv vs conv. Not a Stage 1 recovery path.",
            "uncertain",
        )
    if cohort in ("pmax", "dsa"):
        return (
            "All conversions ≫ conversions. Catch-all / PMax. Not trustworthy employer leads.",
            "duplicate-non-lead",
        )
    if cohort == "competitor":
        return (
            "Competitor conquest. Do not revive.",
            "uncertain",
        )
    return (
        "Reported conversions are mostly WP consult forms, phone, Calendly, or Zoho uploads — not proven job orders. See conversion table.",
        "uncertain",
    )


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def main() -> int:
    ads = load(REPO / "xray" / "data" / "recovery-ads-raw.json")
    crawl = load(REPO / "xray" / "data" / "recovery-lp-crawl.json")
    hist = load(REPO / "ads-launch" / "historical-performance-summary.json")
    ga4 = load(REPO / "xray" / "data" / "ga4-snapshot.json")
    ishare = load(REPO / "xray" / "data" / "impression-share.json")

    crawl_by_canon = {canon_url(p["requested"]): p for p in crawl.get("pages") or []}

    conv_rows: list[dict[str, Any]] = []
    for market, block in (("US", ads.get("us") or {}), ("AU", ads.get("au") or {})):
        metrics_map = {
            (m.get("name") or ""): m for m in (block.get("conversion_metrics") or [])
        }
        seen_metric_names = set()
        for ca in block.get("conversion_actions") or []:
            m = metrics_map.get(ca["name"])
            if m:
                seen_metric_names.add(ca["name"])
            cls = classify_conversion(ca, m)
            conv_rows.append(
                {
                    "account": market,
                    "customer_id": block.get("customer_id"),
                    "name": ca["name"],
                    "id": ca.get("id"),
                    "status": ca.get("status"),
                    "type": ca.get("type"),
                    "category": ca.get("category"),
                    "origin": ca.get("origin"),
                    "primary_for_goal": ca.get("primary_for_goal"),
                    "include_in_conversions_metric": ca.get(
                        "include_in_conversions_metric"
                    ),
                    "counting_type": ca.get("counting_type"),
                    "click_window_days": ca.get("click_window_days"),
                    "phone_call_duration_seconds": ca.get(
                        "phone_call_duration_seconds"
                    ),
                    "default_value": ca.get("default_value"),
                    "quality": cls["quality"],
                    "confidence": cls["confidence"],
                    "note": cls["note"],
                    "conversions": cls["conversions"],
                    "all_conversions": cls["all_conversions"],
                    "date_range": ads.get("window"),
                }
            )
        for name, m in metrics_map.items():
            if name in seen_metric_names:
                continue
            fake = {"name": name, "type": "", "category": m.get("category")}
            cls = classify_conversion(fake, m)
            conv_rows.append(
                {
                    "account": market,
                    "customer_id": block.get("customer_id"),
                    "name": name,
                    "id": "",
                    "status": "NOT_IN_CURRENT_INVENTORY",
                    "type": "",
                    "category": m.get("category"),
                    "origin": "",
                    "primary_for_goal": "",
                    "include_in_conversions_metric": "",
                    "counting_type": "",
                    "click_window_days": "",
                    "phone_call_duration_seconds": "",
                    "default_value": "",
                    "quality": cls["quality"],
                    "confidence": cls["confidence"],
                    "note": cls["note"]
                    + " Action missing from current inventory (removed or renamed).",
                    "conversions": cls["conversions"],
                    "all_conversions": cls["all_conversions"],
                    "date_range": ads.get("window"),
                }
            )

    camp_rows: list[dict[str, Any]] = []
    for market, block in (("US", ads.get("us") or {}), ("AU", ads.get("au") or {})):
        for c in block.get("campaigns") or []:
            if money(c.get("cost")) <= 0 and c.get("status") != "ENABLED":
                continue
            trust, conf = trustworthy_note(c, market)
            camp_rows.append(
                {
                    "account": market,
                    "customer_id": block.get("customer_id"),
                    "campaign": c["name"],
                    "status": c.get("status"),
                    "channel": c.get("channel"),
                    "bidding": c.get("bidding"),
                    "cohort": campaign_cohort(c["name"]),
                    "daily_budget": c.get("daily_budget"),
                    "impressions": c.get("impressions"),
                    "clicks": c.get("clicks"),
                    "cost": c.get("cost"),
                    "avg_cpc": c.get("avg_cpc"),
                    "ctr_pct": c.get("ctr_pct"),
                    "reported_conversions": c.get("conversions"),
                    "all_conversions": c.get("all_conversions"),
                    "reported_cpa": c.get("cpa"),
                    "all_cpa": c.get("all_cpa"),
                    "trustworthy_employer_leads": "unverified",
                    "confidence": conf,
                    "note": trust,
                    "date_range": ads.get("window"),
                    "landing_page": "see landing-page table",
                    "ad_group": "campaign-level rollup",
                    "query": "",
                }
            )

    lp_agg: dict[str, dict[str, Any]] = {}
    for market, block in (("US", ads.get("us") or {}), ("AU", ads.get("au") or {})):
        for row in block.get("landing_pages") or []:
            key = canon_url(row.get("url") or "")
            slot = lp_agg.setdefault(
                f"{market}|{key}",
                {
                    "account": market,
                    "canonical_url": key,
                    "class": host_class(key),
                    "clicks": 0,
                    "cost": 0.0,
                    "impressions": 0,
                    "conversions": 0.0,
                    "all_conversions": 0.0,
                    "sample_raw_urls": [],
                },
            )
            slot["clicks"] += int(row.get("clicks") or 0)
            slot["cost"] = round(slot["cost"] + money(row.get("cost")), 2)
            slot["impressions"] += int(row.get("impressions") or 0)
            slot["conversions"] = round(
                slot["conversions"] + float(row.get("conversions") or 0), 2
            )
            slot["all_conversions"] = round(
                slot["all_conversions"] + float(row.get("all_conversions") or 0), 2
            )
            if len(slot["sample_raw_urls"]) < 3:
                slot["sample_raw_urls"].append(row.get("url"))

    lp_rows: list[dict[str, Any]] = []
    for slot in sorted(lp_agg.values(), key=lambda r: -r["cost"]):
        live = crawl_by_canon.get(slot["canonical_url"]) or {}
        has_form = bool(live.get("employer_form_present"))
        job_nav = bool(live.get("job_seeker_nav"))
        if slot["class"] == "wp_home":
            trust = "Homepage has no lead form. Job-seeker nav to .ph. Historical conversions cannot be employer forms on this URL."
            conf = "duplicate-non-lead"
        elif slot["class"] == "wp_services_or_content":
            trust = "Service/content page: no on-page employer form (crawl). Ads conversions attributed here are not form-on-URL."
            conf = "uncertain"
        elif slot["class"] == "wp_contact":
            trust = "Gravity Form exists (name, email, phone, company, country, message required; Job radio on US). Dual-door. Uncertain quality."
            conf = "uncertain"
        elif slot["class"] == "try":
            trust = "Employer-lean Formspree + Calendly. Thank-you 404. Tiny Ads URL share historically. Not safer than current .app."
            conf = "uncertain"
        elif slot["class"] == "app_paid":
            trust = "Current Stage 1 destination. Ungated employer form (name, email, phone required; website optional). Thank-you in GA4 is testing."
            conf = "uncertain"
        else:
            trust = "See crawl."
            conf = "uncertain"
        lp_rows.append(
            {
                **slot,
                "live_status": live.get("status"),
                "live_title": live.get("title"),
                "employer_form": has_form,
                "job_seeker_nav": job_nav,
                "required_fields": "; ".join(live.get("required_fields") or []),
                "gtm": ", ".join(live.get("gtm") or []),
                "elapsed_ms": live.get("elapsed_ms"),
                "trust_note": trust,
                "confidence": conf,
                "date_range": ads.get("window"),
            }
        )

    term_rows: list[dict[str, Any]] = []
    for market, blob in (("US", hist.get("usa") or {}), ("AU", hist.get("au") or {})):
        for t in (blob.get("top_employer_terms") or [])[:15]:
            conv = float(t.get("conversions") or 0)
            cost = money(t.get("cost"))
            term_rows.append(
                {
                    "account": market,
                    "search_term": t.get("search_term"),
                    "class": t.get("class"),
                    "category_hint": t.get("category_hint"),
                    "impressions": t.get("impressions"),
                    "clicks": t.get("clicks"),
                    "cost": cost,
                    "conversions": conv,
                    "all_conversions": t.get("all_conversions"),
                    "cpa": round(cost / conv, 2) if conv else None,
                    "confidence": "uncertain",
                    "note": "Editor ST ~2024-08-01 to 2026-08-04. Ads conversions ≠ employer leads. Cluster already targeted in VC_* Exact.",
                    "date_range": "2024-08-01 to 2026-08-04",
                    "campaign": "mixed historical (see Editor ST export)",
                    "ad_group": "",
                    "landing_page": "mostly WP homepage / services (see LP table)",
                }
            )

    us_jo = next(
        (
            r
            for r in conv_rows
            if r["account"] == "US" and r["name"] == "Zoho JO Submitted US [Original] via Zapier"
        ),
        {},
    )
    au_jo = next(
        (
            r
            for r in conv_rows
            if r["account"] == "AU" and r["name"] == "Zoho JO Submitted AU [Original] via Zapier"
        ),
        {},
    )
    us_jobseek = next(
        (r for r in conv_rows if "searching for a job" in (r["name"] or "").lower()),
        {},
    )
    us_home = next(
        (r for r in lp_rows if r["account"] == "US" and r["class"] == "wp_home"),
        {},
    )
    au_home = next(
        (r for r in lp_rows if r["account"] == "AU" and r["class"] == "wp_home"),
        {},
    )

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "as_of": "2026-08-13",
        "read_only": True,
        "window_ads": ads.get("window"),
        "api_calls": ads.get("api_calls"),
        "verdict_one_line": (
            "No. After stripping job-seeker clicks, phone taps, chat opens, GA4 duplicates, "
            "Brand, PMax/DSA, and unverified WP consult forms, there is no proven golden "
            "campaign, page, or conversion to safely revive. Keep VC_* on Max Clicks to the ungated .app form."
        ),
        "executive": {
            "successful_period": {
                "answer": "No period is proven successful as employer leads.",
                "detail": (
                    f"USA {ads.get('us', {}).get('customer_id')} spent ${sum(c['cost'] for c in (ads.get('us') or {}).get('campaigns') or []):,.0f} "
                    "from 2024-08-01 to 2026-08-12 with 2,597 reported conversions vs 4,633 all-conversions. "
                    "AU spent similarly inflated. The only CRM-shaped counts are Zoho JO uploads "
                    f"(US {us_jo.get('conversions', 0)} / AU {au_jo.get('conversions', 0)} in Conversions) — Zoho is incomplete, so those are uncertain, not confirmed. "
                    "LK Generic VA and PMax look 'good' only if you treat Ads conversions as leads. They are not."
                ),
            },
            "wordpress_leads": {
                "answer": "WP received almost all paid clicks. That is not the same as generating verified employer leads.",
                "detail": (
                    f"US homepage https://virtualcoworker.com/ : ${us_home.get('cost', 0):,.0f} / {us_home.get('clicks', 0):,} clicks / "
                    f"{us_home.get('conversions', 0)} reported conv. Live crawl 13 Aug 2026: no form, job-seeker nav, GTM-TTKNKT, no AW- in HTML. "
                    "Forms live only on /contact-us/ (Gravity Forms: first+last, email, phone, company, country, message required; US includes a Job radio). "
                    "Service pages have no on-page form. 82% of historical Final URL refs were homepage or /services/* (Editor inventory 5 Aug 2026)."
                ),
            },
            "test_wp_now": {
                "answer": "No. Do not send current VC_* traffic to WordPress.",
                "detail": (
                    "WP homepage/services cannot convert on-page. Contact form has more required fields than .app, a Job option, .ph dual-door, recaptcha, and untrusted conversion twins. "
                    "try.* is employer-lean but thank-you is still 404. Moving traffic would reset Stage 1 learning for a worse funnel."
                ),
            },
            "recoverable_pattern": {
                "answer": "Query cluster only — already live. Not a forgotten page.",
                "detail": (
                    "Employer-intent terms (hire / Philippines / Filipino + VA) converted in Ads historically at high CPA "
                    "(e.g. US 'virtual assistant philippines' $17,669 / 34.5 conv / Editor 2024-08-01–2026-08-04). "
                    "Those Exact themes are already in VC_US_S_CORE / ROLES. Calendly-booked (US 373 reported) is a tracking recovery already on the conversion-plan as Secondary — not a WP revival."
                ),
            },
            "old_conversions": {
                "answer": "Inflated, duplicated, and often not leads. Some were expensive auctions on top of that.",
                "detail": (
                    "US Free Consultation Form 1,036 conv vs 1,843 all-conv, plus GA4 thank-you 788 — overlapping form tracking. "
                    f"Job-seeker click conversion recorded {us_jobseek.get('all_conversions', 0)} all-conversions. "
                    "AU counted Chat Opened/Started (184+164 all-conv). Zoho Zapier and Standard OCI double-count discovery and JO. "
                    "eBook / UA goals / GA4 page_view & click were Primary historically. Phone clicks ≠ 60s consults."
                ),
            },
            "current_problem": {
                "answer": "Not a forgotten WP page. Current constraint is early Stage 1 + auction (IS) + untrusted Ads conversions.",
                "detail": (
                    f"Last 7d Search IS (13 Aug pull): US Core 31% (lost 44% budget / 25% rank); US Roles 20% (lost 65% rank / 15% budget). "
                    f"GA4 US ~{((ga4.get('market_from_landing_path') or {}).get('US'))} paid-ish sessions / 7d; thank-you sessions are testing. "
                    "Ungated .app form just went live. Max Conv was tried ~12 Aug and died — stay Max Clicks."
                ),
            },
            "safest_next": {
                "answer": "Leave VC_* Exact + Max Clicks on the ungated .app form. Wait 7–14 days for sales-ops confirmed employer inquiries. Do not change Final URLs.",
                "detail": "Proposal only. No account or website changes in this audit.",
            },
        },
        "timeline": [
            {"date": "2011+", "what": "Company operating; WP properties become the public sites.", "source": "WP schema / org copy"},
            {"date": "~2023-10-20", "what": "AU chat + website-call conversion actions dated in names (Chat Opened/Started, Website Phone Calls).", "source": "AU conversion inventory"},
            {"date": "2024-08-01 → 2026-08-04", "what": "Editor performance window: US $724k / 87k clicks / 2,597 conv / 4,629 all-conv; AU $457k / 49k clicks / 1,413 / 3,505.", "source": "audit-data/performance Editor CSVs"},
            {"date": "2025-07", "what": "WP /lp-fb/ and /thank-you-landing/ published (Yoast dates). try.* Next experiment exists by Aug 2026.", "source": "raw HTML / funnel autopsy"},
            {"date": "2026-08-05", "what": "Funnel autopsy: 82% Final URL refs = WP home + /services/*. try.* + lp-* = 2.2%. lp-* mostly 404/redirect. Stage 1 Editor package built, all Paused. Brand deferred.", "source": "landing-page-funnel-audit.md + ads-launch/"},
            {"date": "2026-08-06", "what": "Production host www.virtualcoworker.app. Isolation lock: new VC_* parallel to museum PM_*.", "source": "CHATGPT-DEBRIEF.md"},
            {"date": "2026-08-07", "what": "George paused live US Exact junk/general terms (LIVE_PAUSED cohort).", "source": "VC-KEYWORDS-PAUSED-LIVE.md"},
            {"date": "2026-08-08", "what": "US Stage 1 traffic live (VC_US_S_CORE / ROLES). Sales ops 8–10 Aug: 4 US enquiries / 2 booked / 1 job seeker / 1 not-a-fit. Spend $336.88 → $84/enquiry (tiny sample).", "source": "executive-snapshot.json"},
            {"date": "2026-08-09", "what": "AU Stage 1 wakes. Semantic AGs / RSA human work. Phrase remains paused.", "source": "ads-launch notes + exec snapshot"},
            {"date": "2026-08-10", "what": "US call assets / 310 sweep. Website 60s call action live. Cheyenne US-only enquiry email.", "source": "CONVERSION-PLAN.md"},
            {"date": "2026-08-11", "what": "Ungated employer form work on .app. Brand US prelaunch doc exists — Brand still deferred.", "source": "vision/lib/ungated-us-home.ts"},
            {"date": "2026-08-12", "what": "Max Conv tried and died. Back to Max Clicks. RSA winner/comp add (Editor CSV, not this audit).", "source": "George current context + RSA playbooks"},
            {"date": "2026-08-13", "what": "This forensic read: conversion inventory + 2y campaign/LP metrics. WP crawl. Brand campaigns are Paused. Leftover NA A/B tests still Enabled on Max Conv (museum — not a recommendation).", "source": "recovery-ads-raw.json"},
        ],
        "golden_nuggets": [
            {
                "rank": 1,
                "type": "keyword/query cluster",
                "supported": True,
                "headline": "Hire + Philippines/Filipino + VA Exact cluster",
                "why": "Recurring non-brand employer-intent queries in Editor ST. Already the Phase 1 design of VC_* CORE/ROLES. Not forgotten.",
                "account": "US + AU",
                "campaign": "VC_*_S_CORE / ROLES (now); historically LK Generic VA / Original Core / SKAG",
                "ad_group": "Hire_VA_PH / Offshore_VA_PH and role twins",
                "query": "virtual assistant philippines; how to hire a virtual assistant; filipino virtual assistant",
                "landing_page": "Should stay https://www.virtualcoworker.app/us (or /au) — not WP home",
                "date_range": "2024-08-01 to 2026-08-04 (ST) and live from 2026-08-08",
                "spend": "US 'virtual assistant philippines' $17,669 / 446 clicks / 34.5 conv (uncertain)",
                "confidence": "uncertain on historical conv; high on intent match",
                "do": "Keep Exact. Do not Broad. Do not move to WP.",
            },
            {
                "rank": 2,
                "type": "ad message / tracking",
                "supported": True,
                "headline": "Calendly booked is the least-dirty historical appointment signal",
                "why": "US 'LK - Scheduled Calendly Call' 373 conversions / 457 all-conv in 2024-08-01–2026-08-12. Still not confirmed employers.",
                "account": "US 496-715-1855",
                "campaign": "mixed LK / Original",
                "ad_group": "unknown (action-level rollup)",
                "query": "",
                "landing_page": "try.* used Calendly; thank-you 404. Current .app thank-you already has Calendly popup — Ads map not live.",
                "date_range": "2024-08-01 to 2026-08-12",
                "spend": "not isolatable to this action",
                "confidence": "probable employer",
                "do": "Optional later: map VC_US_Calendly_Booked Secondary (already in conversion plan F). Not a traffic move.",
            },
            {
                "rank": 3,
                "type": "form configuration",
                "supported": True,
                "headline": "Current .app form is already lower friction than WP",
                "why": "WP /contact-us/ requires first, last, email, phone, company, country, message + recaptcha + Job radio. .app ungated: name, email, phone required; website optional. No Job radio.",
                "account": "n/a",
                "campaign": "VC_*",
                "ad_group": "",
                "query": "",
                "landing_page": "https://www.virtualcoworker.app/us",
                "date_range": "crawl 2026-08-13",
                "spend": "n/a",
                "confidence": "n/a — UX evidence, not lead proof",
                "do": "Do not copy the WP form. Protect the ungated .app form. Do not publish changes in this audit.",
            },
            {
                "rank": 4,
                "type": "landing page",
                "supported": False,
                "headline": "No golden WordPress page",
                "why": "The URL with the conversions is the homepage, which has no form. Contact-us has a form but was not the primary paid destination. lp-* are 404/redirect. try.* thank-you 404.",
                "account": "US + AU",
                "campaign": "mostly LK / PMax / DSA / PM_RSA",
                "ad_group": "",
                "query": "",
                "landing_page": "https://virtualcoworker.com/ and https://virtualcoworker.com.au/",
                "date_range": "2024-08-01 to 2026-08-12",
                "spend": f"US home ${us_home.get('cost', 0):,.0f}; AU home ${au_home.get('cost', 0):,.0f}",
                "confidence": "duplicate-non-lead for homepage-attributed conv",
                "do": "Do not revive.",
            },
            {
                "rank": 5,
                "type": "campaign period",
                "supported": False,
                "headline": "No clean golden period after stripping junk",
                "why": "Best reported CPA pockets are Brand, tiny A/B tests, or PMax/DSA with all-conv inflation. LK Generic VA spent ~$150k US / $140k AU on Max Conv into WP. Zoho JO (67 US / 36 AU) over ~$1.18M combined spend is ~$11k per reported JO if those JOs are real — and they are unverified.",
                "account": "both",
                "campaign": "LK - Generic VA; [Original] PMax",
                "ad_group": "",
                "query": "",
                "landing_page": "WP home / services",
                "date_range": "2024-08-01 to 2026-08-12",
                "spend": "US LK Generic VA $150,186; US PMax $145,863; AU PMax $144,537; AU LK Generic VA $140,359",
                "confidence": "uncertain",
                "do": "Do not revive PMax, DSA, Max Conv, or Generic VA catch-alls.",
            },
        ],
        "recovery_tests": {
            "primary": {
                "name": "Hold the line — ungated .app, Max Clicks, Exact",
                "account": "US 496-715-1855 first (AU watch)",
                "campaign": "VC_US_S_CORE (primary), VC_US_S_ROLES (observe)",
                "ad_group": "Hire_VA_PH / Offshore_VA_PH — do not split out a new campaign",
                "query": "Existing live Exact PH/hire VA terms only",
                "destination": "https://www.virtualcoworker.app/us (unchanged)",
                "rationale": "Smallest credible test is to let the new form collect sales-verified inquiries on traffic you already bought. Historical WP cannot beat that on evidence.",
                "exclusions": "No Broad. No Max Conv. No WP Final URL. No Brand. No Phrase enable. No PMax/DSA.",
                "budget_exposure": "Current $75 Core + $50 Roles / day. Do not raise for this test.",
                "duration": "14 days from 13 Aug 2026 (through 27 Aug 2026)",
                "min_clicks": "≥250 US clicks or 14 calendar days, whichever second",
                "min_qualified": "≥3 sales-ops confirmed employer inquiries (Cheyenne/Holly classify; job seekers never count)",
                "primary_metric": "Sales-ops confirmed employer inquiries — not Ads Conversions",
                "guardrails": "Daily search-term skim. Pause obvious job-seeker Exact if it appears. Keep Max Clicks.",
                "stop": "If job-seeker share of enquiries >50% of form submits, stop and tighten negatives (Editor CSV) — still no WP move.",
                "protect_learning": "No campaign duplication. No Final URL experiment. No bidding strategy flip.",
            },
            "secondary": [
                {
                    "name": "Map Calendly booked as Secondary (tracking only)",
                    "account": "US then AU",
                    "campaign": "VC_US_S_* campaign-specific goals",
                    "destination": "unchanged .app thank-you",
                    "rationale": "Historical Calendly volume is the least-dirty appointment signal. Conversion plan F already describes this. Do not make it Primary while thank-you exists.",
                    "note": "George creates in Ads UI + GTM. This audit does not implement.",
                },
                {
                    "name": "If 14-day form is empty: optional phone-optional copy test on .app only",
                    "account": "US",
                    "campaign": "VC_US_S_CORE",
                    "destination": "same /us",
                    "rationale": "WP required phone AND message AND company. If .app still gets zero employer forms after traffic, the next lever is field friction on .app — not routing to WP. Still proposal-only.",
                    "note": "Do not implement unless George asks after the 14-day hold.",
                },
            ],
        },
        "do_not_revive": [
            "WordPress homepage as Final URL (no form, .ph dual-door, $348k US / $209k AU attributed spend)",
            "WP /services/* as paid LPs (no on-page form)",
            "Dead lp-* paths (404 or 301 to home)",
            "try.virtualcoworker.com until thank-you is 200 and Ads events exist (thank-you still 404 on 13 Aug 2026)",
            "PMax and DSA catch-alls",
            "Max Conversions / tCPA on untrusted actions (tried ~12 Aug, died)",
            "Broad match positives",
            "Competitor conquest campaigns",
            "Chat Opened / Chat Started / eBook / GA4 page_view / gtm_submit_button_click as Primary",
            "Clicks “I am searching for a job” as any conversion",
            "Attaching Zoho Zapier + Standard OCI twins as Primary (duplicates)",
            "Brand-first spend (deferred — classify only)",
            "Phrase enable-all with Exact live",
            "Leftover Enabled NA A/B Max Conv tests — museum, not a recovery vehicle",
        ],
        "limitations": [
            "Zoho CRM/Recruit inventory is deferred — cannot confirm Job Orders or Placements against Ads clicks.",
            "Search-term Editor export (~2024-08-01 to 2026-08-04) has ST cost < campaign cost (PMax/DSA / missing rows).",
            "landing_page_view URLs include {ignore} ValueTrack junk; canonicalization is ours.",
            "Conversion actions that fired historically but were REMOVED do not appear in inventory; some still appear in metrics (status NOT_IN_CURRENT_INVENTORY).",
            "No auction-insights (field error on 13 Aug pull). IS from campaign metrics only.",
            "campaign.start_date is not queryable in this API version — timeline uses docs + current status, not create dates.",
            "GA4 thank-you / form events on .app are internal testing — not employer leads.",
            "Call transcripts / dispositions not available.",
            "WP organic ~500–700/mo is mostly PH (George + CEO session) — not a US/AU employer engine.",
            "Ads API mutations forbidden; this file is evidence only.",
        ],
        "human_leads_current": {
            "us": {
                "window": "2026-08-08 to 2026-08-10",
                "enquiries": 4,
                "booked": 2,
                "job_seeker": 1,
                "not_a_fit": 1,
                "spend_usd": 336.88,
                "source": "Cheyenne sales-ops email; executive-snapshot.json",
                "confidence": "probable employer for the 2 booked; confirmed job seeker for 1",
            },
            "au": {"enquiries": None, "note": "No ops AU enquiry report as of 10 Aug email."},
        },
        "impression_share_last_7d": ishare.get("performance_us"),
        "impression_share_au_last_7d": ishare.get("performance_au"),
        "conversions": conv_rows,
        "campaigns": camp_rows,
        "landing_pages": lp_rows,
        "search_terms": term_rows,
        "crawl": crawl.get("pages"),
        "csv": {
            "conversions": "data/recovery/conversions.csv",
            "campaigns": "data/recovery/campaigns.csv",
            "landing_pages": "data/recovery/landing-pages.csv",
            "search_terms": "data/recovery/search-terms.csv",
        },
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    write_csv(
        OUT_DIR / "conversions.csv",
        conv_rows,
        [
            "account",
            "customer_id",
            "name",
            "status",
            "type",
            "category",
            "primary_for_goal",
            "include_in_conversions_metric",
            "counting_type",
            "quality",
            "confidence",
            "conversions",
            "all_conversions",
            "date_range",
            "note",
        ],
    )
    write_csv(
        OUT_DIR / "campaigns.csv",
        camp_rows,
        [
            "account",
            "campaign",
            "status",
            "channel",
            "bidding",
            "cohort",
            "cost",
            "clicks",
            "impressions",
            "reported_conversions",
            "all_conversions",
            "reported_cpa",
            "confidence",
            "trustworthy_employer_leads",
            "date_range",
            "note",
        ],
    )
    write_csv(
        OUT_DIR / "landing-pages.csv",
        lp_rows,
        [
            "account",
            "canonical_url",
            "class",
            "cost",
            "clicks",
            "conversions",
            "all_conversions",
            "live_status",
            "employer_form",
            "job_seeker_nav",
            "confidence",
            "trust_note",
            "date_range",
        ],
    )
    write_csv(
        OUT_DIR / "search-terms.csv",
        term_rows,
        [
            "account",
            "search_term",
            "class",
            "cost",
            "clicks",
            "conversions",
            "all_conversions",
            "cpa",
            "confidence",
            "date_range",
            "note",
        ],
    )
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote CSVs in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
