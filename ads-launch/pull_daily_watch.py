#!/usr/bin/env python3
"""Daily Google Ads second-pair-of-eyes — cheap read-only GAQL.

Hard rules:
- No mutate / upload / enable / pause
- On RESOURCE_EXHAUSTED: STOP, do not retry
- Cap: 4 GAQL searches by default (US+AU search terms + campaign pacing)
- Optional --ads-policy adds 1 more call (US only) → max 5
- Brand deferred — VC_* CORE/ROLES only (LIKE 'VC_US_%' / 'VC_AU_%')
- Writes xray/data/daily-watch.json for the Daily watch tab

Ops tone (2026-08-10):
- Do NOT flag “0 conversions” — phone/tracking not trusted yet
- Job-seeker terms = “add negative” operator notes, not a hall of shame
- Already-excluded terms: quiet unless still spending today
- Brand deferred one-liner only — Stage 1 VC_* first

Usage (from shoutgeorge-ads venv):
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    /Users/george/Developer/virtual-coworker/ads-launch/pull_daily_watch.py

  # Prove plumbing with 1–2 calls only:
  .../pull_daily_watch.py --limit-calls 2
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SG_ROOT = Path(
    __import__("os").environ.get(
        "SHOUTGEORGE_ADS_ROOT", "/Users/george/Developer/shoutgeorge-ads"
    )
)
if (SG_ROOT / "src").is_dir():
    sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from sg_google_ads.client import build_client, run_gaql  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import (  # noqa: E402
    ApiAccessError,
    QuotaExhaustedError,
    SgGoogleAdsError,
)

# Local Mac: shoutgeorge-ads .env + VC overlay. Cloud: GOOGLE_ADS_* already in env.
if (SG_ROOT / ".env").is_file():
    load_dotenv(SG_ROOT / ".env")
_vc_env = SG_ROOT / "clients" / "virtual-coworker.env"
if _vc_env.is_file():
    load_dotenv(_vc_env, override=True)

US_ID = "4967151855"
AU_ID = "5735391940"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "xray" / "data" / "daily-watch.json"

# Job-seeker / waste patterns (Stage 1 negatives intent — flag for add-negative, don't mutate)
BAD_TERM_RE = re.compile(
    r"\b("
    r"jobs?|careers?|salary|salaries|wages?|resume|cvs?|"
    r"employment|internship|interns?|vacanc(?:y|ies)|"
    r"indeed|glassdoor|jobstreet|unemployment|"
    r"hiring\s+me|apply\s+(?:now|as|to\s+be)|"
    r"work\s+from\s+home|from\s+home|at\s+home|"
    r"job\s*seekers?|jobseekers?"
    r")\b",
    re.I,
)

# Minimum spend to bother listing a job-seeker term (USD)
MIN_NEG_COST = 1.0
# Spend vs daily budget ratio that counts as a blow-up
BLOWUP_RATIO = 1.5
TOP_TERMS = 12
EXCLUDED_STATUSES = frozenset({"EXCLUDED", "ADDED_EXCLUDED"})


def _money(micros: Any) -> float:
    try:
        return round(int(micros or 0) / 1_000_000, 2)
    except (TypeError, ValueError):
        return 0.0


def _enum_name(val: Any) -> str:
    if val is None:
        return ""
    name = getattr(val, "name", None)
    if name:
        return str(name)
    return str(val)


def fetch_rows(client: Any, customer_id: str, query: str) -> list[Any]:
    return list(run_gaql(client, customer_id, query))


def search_terms_query(prefix: str) -> str:
    # Date segment so we can tell “already excluded” vs “still spending today”.
    return f"""
        SELECT
          campaign.name,
          campaign.status,
          ad_group.name,
          search_term_view.search_term,
          search_term_view.status,
          segments.date,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions
        FROM search_term_view
        WHERE campaign.name LIKE '{prefix}%'
          AND campaign.status != 'REMOVED'
          AND segments.date DURING LAST_7_DAYS
          AND metrics.cost_micros > 0
        ORDER BY metrics.cost_micros DESC
    """


def campaign_pacing_query(prefix: str) -> str:
    return f"""
        SELECT
          campaign.name,
          campaign.status,
          campaign_budget.amount_micros,
          campaign_budget.explicitly_shared,
          segments.date,
          metrics.impressions,
          metrics.clicks,
          metrics.cost_micros,
          metrics.conversions
        FROM campaign
        WHERE campaign.name LIKE '{prefix}%'
          AND campaign.status != 'REMOVED'
          AND segments.date DURING LAST_7_DAYS
        ORDER BY campaign.name, segments.date
    """


def ads_policy_query(prefix: str) -> str:
    return f"""
        SELECT
          campaign.name,
          ad_group.name,
          ad_group_ad.ad.id,
          ad_group_ad.status,
          ad_group_ad.policy_summary.approval_status,
          ad_group_ad.policy_summary.review_status
        FROM ad_group_ad
        WHERE campaign.name LIKE '{prefix}%'
          AND campaign.status != 'REMOVED'
          AND ad_group.status != 'REMOVED'
          AND ad_group_ad.status != 'REMOVED'
          AND ad_group_ad.policy_summary.approval_status != 'APPROVED'
        LIMIT 50
    """


def score_search_terms(rows: list[Any], market: str) -> dict[str, Any]:
    # Roll up same term+campaign across days / ad groups.
    rolled: dict[tuple[str, str], dict[str, Any]] = {}
    all_dates: set[str] = set()
    for row in rows:
        term = (row.search_term_view.search_term or "").strip()
        camp = row.campaign.name
        day = str(row.segments.date)
        all_dates.add(day)
        key = (term.lower(), camp)
        cost = _money(row.metrics.cost_micros)
        clicks = int(row.metrics.clicks or 0)
        conv = float(row.metrics.conversions or 0)
        cur = rolled.get(key)
        if cur is None:
            rolled[key] = {
                "market": market,
                "search_term": term,
                "campaign": camp,
                "campaign_status": _enum_name(row.campaign.status),
                "ad_group": row.ad_group.name,
                "cost_usd": cost,
                "cost_today": 0.0,
                "clicks": clicks,
                "conversions": conv,
                "status": _enum_name(row.search_term_view.status),
                "job_seeker_like": bool(BAD_TERM_RE.search(term)),
                "days": {day: cost},
            }
        else:
            cur["cost_usd"] = round(cur["cost_usd"] + cost, 2)
            cur["clicks"] += clicks
            cur["conversions"] += conv
            cur["status"] = _enum_name(row.search_term_view.status) or cur["status"]
            cur["campaign_status"] = (
                _enum_name(row.campaign.status) or cur["campaign_status"]
            )
            cur["days"][day] = round(cur["days"].get(day, 0.0) + cost, 2)

    focus_day = sorted(all_dates)[-1] if all_dates else None
    scored: list[dict[str, Any]] = []
    for cur in rolled.values():
        cost_today = cur["days"].get(focus_day, 0.0) if focus_day else 0.0
        cur["cost_today"] = round(cost_today, 2)
        cur["focus_day"] = focus_day
        cur.pop("days", None)
        scored.append(cur)

    scored.sort(key=lambda x: x["cost_usd"], reverse=True)
    total_cost = round(sum(x["cost_usd"] for x in scored), 2)

    # Operator notes only — not “0 conversions” (tracking untrusted).
    # Job-seeker: “add negative” unless already excluded with no spend on focus day.
    # Do NOT blanket-flag every EXCLUDED term — that’s historical noise.
    notes: list[dict[str, Any]] = []
    for x in scored:
        if not x["job_seeker_like"] or x["cost_usd"] < MIN_NEG_COST:
            continue
        st = x.get("status") or ""
        excluded = st in EXCLUDED_STATUSES
        still_on_focus = (x.get("cost_today") or 0) > 0
        if excluded and not still_on_focus:
            continue  # already handled; 7d history only
        note = dict(x)
        note["note_kind"] = (
            "still_spending_confirm" if excluded and still_on_focus else "add_negative"
        )
        notes.append(note)

    return {
        "market": market,
        "row_count": len(rows),
        "unique_term_campaigns": len(scored),
        "total_cost_usd": total_cost,
        "focus_day": focus_day,
        "top_by_spend": scored[:TOP_TERMS],
        "operator_notes": notes[:TOP_TERMS],
        # Back-compat alias for older HTML (prefer operator_notes)
        "flagged": notes[:TOP_TERMS],
    }


def score_pacing(rows: list[Any], market: str) -> dict[str, Any]:
    by_camp: dict[str, dict[str, Any]] = {}
    for row in rows:
        name = row.campaign.name
        day = str(row.segments.date)
        budget = _money(row.campaign_budget.amount_micros)
        cost = _money(row.metrics.cost_micros)
        blob = by_camp.setdefault(
            name,
            {
                "name": name,
                "status": _enum_name(row.campaign.status),
                "daily_budget_usd": budget,
                "cost_last_7_days": 0.0,
                "cost_today": 0.0,
                "clicks_last_7_days": 0,
                "conversions_last_7_days": 0.0,
                "days": {},
            },
        )
        blob["daily_budget_usd"] = budget or blob["daily_budget_usd"]
        blob["status"] = _enum_name(row.campaign.status) or blob["status"]
        blob["cost_last_7_days"] = round(blob["cost_last_7_days"] + cost, 2)
        blob["clicks_last_7_days"] += int(row.metrics.clicks or 0)
        blob["conversions_last_7_days"] += float(row.metrics.conversions or 0)
        blob["days"][day] = round(cost, 2)

    all_dates = sorted({d for c in by_camp.values() for d in c["days"]})
    today = all_dates[-1] if all_dates else None
    blowups: list[dict[str, Any]] = []
    camps_out: list[dict[str, Any]] = []
    for c in by_camp.values():
        cost_today = c["days"].get(today, 0.0) if today else 0.0
        c["cost_today"] = cost_today
        c.pop("days", None)
        budget = float(c["daily_budget_usd"] or 0)
        ratio = (cost_today / budget) if budget > 0 else 0.0
        c["spend_vs_budget_today"] = round(ratio, 2)
        # Only blow-up ENABLED campaigns — paused/removed aren't fires
        if (
            c.get("status") == "ENABLED"
            and budget > 0
            and ratio >= BLOWUP_RATIO
        ):
            blowups.append(
                {
                    "market": market,
                    "campaign": c["name"],
                    "status": c.get("status"),
                    "cost_today": cost_today,
                    "daily_budget_usd": budget,
                    "ratio": round(ratio, 2),
                }
            )
        camps_out.append(c)

    camps_out.sort(key=lambda x: x["cost_last_7_days"], reverse=True)
    return {
        "market": market,
        "focus_day": today,
        "campaigns": camps_out,
        "blowups": blowups,
        "total_cost_last_7_days": round(sum(c["cost_last_7_days"] for c in camps_out), 2),
        "total_cost_today": round(sum(c["cost_today"] for c in camps_out), 2),
    }


def score_ads_policy(rows: list[Any], market: str) -> dict[str, Any]:
    items = []
    for row in rows:
        items.append(
            {
                "market": market,
                "campaign": row.campaign.name,
                "ad_group": row.ad_group.name,
                "ad_id": str(row.ad_group_ad.ad.id),
                "ad_status": _enum_name(row.ad_group_ad.status),
                "approval_status": _enum_name(
                    row.ad_group_ad.policy_summary.approval_status
                ),
                "review_status": _enum_name(
                    row.ad_group_ad.policy_summary.review_status
                ),
            }
        )
    return {"market": market, "row_count": len(items), "ads": items}


def _camp_short(name: str) -> str:
    return re.sub(r"^VC_(US|AU)_S_", "", name or "").replace("_", " ")


def build_digest(
    *,
    us_terms: dict[str, Any] | None,
    au_terms: dict[str, Any] | None,
    us_pace: dict[str, Any] | None,
    au_pace: dict[str, Any] | None,
    us_policy: dict[str, Any] | None,
) -> dict[str, Any]:
    problems: list[str] = []

    # Blowups first — real money, not search-term chatter
    for block in (us_pace, au_pace):
        if not block:
            continue
        focus = block.get("focus_day") or "latest day"
        for b in block.get("blowups") or []:
            problems.append(
                f"{b['market']}: {b['campaign']} spent ${b['cost_today']:.2f} "
                f"vs ${b['daily_budget_usd']:.0f}/day budget "
                f"({b['ratio']:.1f}×) on {focus}"
            )

    for block in (us_terms, au_terms):
        if not block:
            continue
        focus = block.get("focus_day") or "latest day"
        for t in block.get("operator_notes") or block.get("flagged") or []:
            kind = t.get("note_kind") or "add_negative"
            term = t.get("search_term") or ""
            market = t.get("market") or ""
            camp = _camp_short(t.get("campaign") or "")
            cost = float(t.get("cost_usd") or 0)
            cost_focus = float(t.get("cost_today") or 0)
            st = t.get("status") or ""

            if kind == "still_spending_confirm":
                problems.append(
                    f"{market}: “{term}” still spending on {focus} "
                    f"(${cost_focus:.2f}) — confirm pause/negative "
                    f"({st or 'status?'} · {camp} · ${cost:.2f} 7d)"
                )
            else:
                if st in EXCLUDED_STATUSES:
                    continue
                problems.append(
                    f"{market}: add negative “{term}” "
                    f"(${cost:.2f} 7d · {camp})"
                )

    if us_policy:
        for ad in (us_policy.get("ads") or [])[:3]:
            problems.append(
                f"US: ad {ad['ad_id']} on {ad['campaign']} / {ad['ad_group']} "
                f"approval={ad['approval_status']}"
            )

    seen: set[str] = set()
    bullets: list[str] = []
    for p in problems:
        if p in seen:
            continue
        seen.add(p)
        bullets.append(p)
        if len(bullets) >= 5:
            break

    if not bullets:
        status = "nothing_on_fire"
        summary = "Quiet pull — no spend blowups or open negatives on this check."
    else:
        status = "attention"
        n = len(bullets)
        summary = f"{n} operator note{'s' if n != 1 else ''}."

    return {
        "status": status,
        "summary": summary,
        "bullets": bullets,
        "problem_count": len(bullets),
    }


def run_call(
    client: Any,
    *,
    n: int,
    name: str,
    customer_id: str,
    query: str,
    api_calls: list[dict[str, Any]],
) -> list[Any] | None:
    try:
        print(f"API call {n}: {name} …", flush=True)
        rows = fetch_rows(client, customer_id, query)
        api_calls.append(
            {"n": n, "name": name, "ok": True, "row_count": len(rows)}
        )
        return rows
    except QuotaExhaustedError as exc:
        print(f"STOP quota on call {n}: {exc}", file=sys.stderr)
        api_calls.append({"n": n, "name": name, "ok": False, "error": str(exc)})
        return None
    except ApiAccessError as exc:
        print(f"STOP API on call {n}: {exc}", file=sys.stderr)
        api_calls.append({"n": n, "name": name, "ok": False, "error": str(exc)})
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Cheap daily Ads watch pull")
    parser.add_argument(
        "--limit-calls",
        type=int,
        default=4,
        help="Hard cap on GAQL searches (default 4, max 5 with --ads-policy)",
    )
    parser.add_argument(
        "--ads-policy",
        action="store_true",
        help="Add 1 US ad-policy call (disapproved/limited) if under call budget",
    )
    args = parser.parse_args()
    limit = max(1, min(int(args.limit_calls), 5))

    started = datetime.now(timezone.utc).isoformat()
    api_calls: list[dict[str, Any]] = []
    hard_stop: str | None = None

    try:
        env_file = SG_ROOT / ".env" if (SG_ROOT / ".env").is_file() else None
        settings = load_settings(env_file=env_file)
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        print(f"ERROR building client: {exc}", file=sys.stderr)
        return 1

    us_terms = au_terms = us_pace = au_pace = us_policy = None
    n = 0

    plan: list[tuple[str, str, str, str]] = [
        ("us_search_terms_7d", US_ID, search_terms_query("VC_US_"), "us_terms"),
        ("au_search_terms_7d", AU_ID, search_terms_query("VC_AU_"), "au_terms"),
        ("us_campaign_pacing_7d", US_ID, campaign_pacing_query("VC_US_"), "us_pace"),
        ("au_campaign_pacing_7d", AU_ID, campaign_pacing_query("VC_AU_"), "au_pace"),
    ]
    if args.ads_policy:
        plan.append(
            ("us_ads_not_approved", US_ID, ads_policy_query("VC_US_"), "us_policy")
        )

    buckets: dict[str, Any] = {}
    for name, cid, query, key in plan:
        if n >= limit:
            break
        n += 1
        rows = run_call(
            client, n=n, name=name, customer_id=cid, query=query, api_calls=api_calls
        )
        if rows is None:
            hard_stop = (api_calls[-1] or {}).get("error")
            break
        buckets[key] = rows

    if "us_terms" in buckets:
        us_terms = score_search_terms(buckets["us_terms"], "US")
    if "au_terms" in buckets:
        au_terms = score_search_terms(buckets["au_terms"], "AU")
    if "us_pace" in buckets:
        us_pace = score_pacing(buckets["us_pace"], "US")
    if "au_pace" in buckets:
        au_pace = score_pacing(buckets["au_pace"], "AU")
    if "us_policy" in buckets:
        us_policy = score_ads_policy(buckets["us_policy"], "US")

    digest = build_digest(
        us_terms=us_terms,
        au_terms=au_terms,
        us_pace=us_pace,
        au_pace=au_pace,
        us_policy=us_policy,
    )

    # Explicit fact-check for the term George asked about
    va_ph_check: dict[str, Any] | None = None
    for block in (us_terms, au_terms):
        if not block:
            continue
        for t in block.get("top_by_spend") or []:
            if (t.get("search_term") or "").lower() == "va workers ph":
                va_ph_check = {
                    "search_term": t["search_term"],
                    "market": t["market"],
                    "campaign": t["campaign"],
                    "campaign_status": t.get("campaign_status"),
                    "status": t.get("status"),
                    "cost_usd_7d": t.get("cost_usd"),
                    "cost_today": t.get("cost_today"),
                    "focus_day": t.get("focus_day"),
                    "verdict": (
                        "still_spending_confirm"
                        if (t.get("cost_today") or 0) > 0
                        else (
                            "already_excluded_historical"
                            if (t.get("status") or "") in EXCLUDED_STATUSES
                            else "present_not_excluded"
                        )
                    ),
                }
                break
        if va_ph_check:
            break

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "started_at_utc": started,
        "window": "LAST_7_DAYS",
        "scope": "VC_US_* + VC_AU_* (Brand deferred — Stage 1 first)",
        "api_calls": api_calls,
        "api_calls_used": len(api_calls),
        "api_call_cap": limit,
        "hard_stop": hard_stop,
        "digest": digest,
        "checks": {"va_workers_ph": va_ph_check},
        "markets": {
            "US": {"search_terms": us_terms, "pacing": us_pace, "ads_policy": us_policy},
            "AU": {"search_terms": au_terms, "pacing": au_pace},
        },
        "notes": [
            "Read-only. No Ads mutations.",
            "Do not flag 0 conversions — tracking not trusted yet.",
            "Brand ads deferred (Stage 1 VC_* first).",
            "Basic Access: keep this job ≤5 GAQL searches/day.",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Digest: {digest['status']} — {digest['summary']}")
    for b in digest.get("bullets") or []:
        print(f"  • {b}")
    if va_ph_check:
        print(
            f"va workers ph: {va_ph_check['verdict']} · "
            f"status={va_ph_check['status']} · "
            f"7d=${va_ph_check['cost_usd_7d']} · "
            f"today=${va_ph_check['cost_today']}"
        )
    print(f"API calls used: {len(api_calls)} (cap {limit})")
    return 1 if hard_stop else 0


if __name__ == "__main__":
    raise SystemExit(main())
