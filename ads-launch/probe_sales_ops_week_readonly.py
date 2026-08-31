#!/usr/bin/env python3
"""Read-only Zoho ping for a Cheyenne sales-ops week (attribution watch).

Hard rules:
- GET + COQL SELECT only. Never create/update/delete.
- Never print tokens, emails, phones, or raw click IDs.
- Cap API volume. Stop on rate limit.
- Does not set ZOHO_CRM_ENABLED. Does not call Google Ads.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "zoho"))
from _common import (  # noqa: E402
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    load_credentials,
    refresh_access_token,
    write_json,
)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().\-]{7,}\d)")
CALLS = 0
MAX_CALLS = 4
STOPPED = None

# This week: Mon Aug 10 – Sun Aug 16 2026 (inclusive), America/Los_Angeles.
# UTC midnight Aug 17 cuts Sunday 17:00–23:59 PT — use PT midnight instead.
WINDOW_START = "2026-08-17T00:00:00-07:00"
WINDOW_END = "2026-08-24T00:00:00-07:00"


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def redact(s: Any) -> Any:
    if isinstance(s, str):
        s = EMAIL_RE.sub("[email]", s)
        s = PHONE_RE.sub("[phone]", s)
        return s
    if isinstance(s, dict):
        return {k: redact(v) for k, v in s.items()}
    if isinstance(s, list):
        return [redact(x) for x in s]
    return s


def name_of(obj: Any) -> str:
    if isinstance(obj, dict):
        return str(obj.get("name") or "")
    return str(obj or "")


def click_present(val: Any) -> bool:
    return bool(val) and str(val).strip() not in ("", "null", "None")


def post_json(url: str, token: str, payload: dict[str, Any]) -> tuple[int, Any]:
    global CALLS, STOPPED
    CALLS += 1
    if CALLS > MAX_CALLS:
        STOPPED = "cap"
        return 0, {"error": "cap"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Zoho-oauthtoken {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.getcode() or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
        if status in (429, 403) or "RATE" in raw.upper() or "LIMIT" in raw.upper():
            STOPPED = f"rate {status}"
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, {"raw": raw[:200]}


def rows_of(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, dict) and isinstance(body.get("data"), list):
        return [r for r in body["data"] if isinstance(r, dict)]
    return []


def host_of(s: str) -> str:
    s = str(s or "").strip()
    if "://" in s:
        s = s.split("://", 1)[1]
    return s.split("/")[0][:64]


def sanitize_lead(rec: dict[str, Any]) -> dict[str, Any]:
    gclid = rec.get("utm_gclid") or ""
    website = str(rec.get("Website") or "")
    referrer = str(rec.get("Referrer") or rec.get("Referring_URL") or "")
    camp = str(rec.get("Campaign_Name") or rec.get("utm_campaign") or "")
    return {
        "created": str(rec.get("Created_Time") or "")[:19],
        "region": str(rec.get("Region") or "")[:16],
        "status": str(rec.get("Lead_Status") or "")[:48],
        "source": str(rec.get("Lead_Source") or "")[:32],
        "form_source": str(rec.get("Form_Source") or "")[:40],
        "utm_source": str(rec.get("utm_source") or "")[:32],
        "utm_medium": str(rec.get("utm_medium") or "")[:32],
        "utm_campaign": str(rec.get("utm_campaign") or "")[:48],
        "campaign_name": camp[:48],
        "created_by": name_of(rec.get("Created_By"))[:32],
        "has_gclid": click_present(gclid),
        "website_host": host_of(website),
        "referrer_host": host_of(referrer),
        "looks_app_host": "virtualcoworker.app" in f"{website} {referrer}".lower(),
        "looks_vc_campaign": "VC_" in camp.upper(),
    }


def is_googleish(r: dict[str, Any]) -> bool:
    src = str(r.get("source") or "").lower()
    utm = str(r.get("utm_source") or "").lower()
    return src in {"google", "googleads", "google ads", "google organic"} or utm in {
        "google",
        "googleads",
        "google ads",
    }


def is_organic_medium(r: dict[str, Any]) -> bool:
    med = str(r.get("utm_medium") or "").lower()
    camp = str(r.get("utm_campaign") or r.get("campaign_name") or "").lower()
    return med == "organic" or "organic:" in camp or camp == "organic"


def count_map(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    c: Counter[str] = Counter((r.get(key) or "(blank)") for r in rows)
    return dict(c.most_common())


def main() -> int:
    if not os.environ.get("GITHUB_ACTIONS"):
        load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    ensure_local_dir()
    creds = load_credentials()
    token = str(refresh_access_token(creds)["access_token"])
    api = creds["api_domain"]
    coql = crm_url(api, "/coql")

    fields = (
        "id, Created_Time, Region, Lead_Status, Lead_Source, Form_Source, "
        "utm_source, utm_medium, utm_campaign, Campaign_Name, Website, Referrer, "
        "Referring_URL, Created_By, utm_gclid"
    )
    sql = (
        f"select {fields} from Leads where Created_Time >= '{WINDOW_START}' "
        f"and Created_Time < '{WINDOW_END}' order by Created_Time desc limit 200"
    )
    st, body = post_json(coql, token, {"select_query": sql})
    if st != 200:
        print(f"COQL failed http={st} err={str(redact(body))[:240]}")
        return 1

    leads = [sanitize_lead(r) for r in rows_of(body)]
    usa = [r for r in leads if str(r.get("region") or "").upper() in {"USA", "US", "UNITED STATES"}]
    au = [r for r in leads if str(r.get("region") or "").upper() in {"AU", "AUS", "AUSTRALIA"}]

    def region_block(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "n": len(rows),
            "with_utm_gclid": sum(1 for r in rows if r.get("has_gclid")),
            "googleish_no_gclid": sum(1 for r in rows if is_googleish(r) and not r.get("has_gclid")),
            "utm_medium_or_campaign_organic": sum(1 for r in rows if is_organic_medium(r)),
            "looks_vc_campaign": sum(1 for r in rows if r.get("looks_vc_campaign")),
            "discovery_scheduled": sum(
                1 for r in rows if "discovery scheduled" in str(r.get("status") or "").lower()
            ),
            "by_source": count_map(rows, "source"),
            "by_utm_source": count_map(rows, "utm_source"),
            "by_utm_medium": count_map(rows, "utm_medium"),
            "by_status": count_map(rows, "status"),
            "by_utm_campaign": count_map(rows, "utm_campaign"),
        }

    usa_block = region_block(usa)
    au_block = region_block(au)
    watch_rows = [
        r
        for r in usa + au
        if is_googleish(r)
        or is_organic_medium(r)
        or str(r.get("utm_source") or "").lower() in {"bing", "facebook", "fb", "meta"}
        or str(r.get("source") or "").lower() in {"bing", "facebook", "fb", "meta"}
    ]

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "window_start": WINDOW_START,
        "window_end_exclusive": WINDOW_END,
        "api_calls": CALLS,
        "stopped": STOPPED,
        "leads_in_window": len(leads),
        "usa": usa_block,
        "au": au_block,
        "watch": {
            "n": len(watch_rows),
            "note": (
                "Google/Bing/Facebook CRM labels without utm_gclid are not paid proof. "
                "utm_medium=organic or campaign 'organic: google' is a common paid-leak stamp."
            ),
        },
        "all_regions": count_map(leads, "region"),
    }

    raw_path = LOCAL_ZOHO / "probe-sales-ops-week-2026-08-10-16.json"
    write_json(raw_path, {"summary": summary, "usa_rows": redact(usa), "au_rows": redact(au)})
    pub = Path(__file__).resolve().parents[1] / "xray" / "data" / "sales-ops-week-zoho.json"
    pub_summary = {k: v for k, v in summary.items() if k != "watch"}
    pub.write_text(json.dumps(pub_summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(pub_summary, indent=2))
    print(f"wrote {raw_path}")
    print(f"wrote {pub}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
