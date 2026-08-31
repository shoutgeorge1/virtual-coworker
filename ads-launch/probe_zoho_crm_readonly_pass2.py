#!/usr/bin/env python3
"""Pass 2: counts with WHERE + Job Order / Placement samples. READ ONLY."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "zoho"))
from _common import (  # noqa: E402
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    http_get_json,
    load_credentials,
    refresh_access_token,
    write_json,
)

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
PHONE_RE = re.compile(r"(?:\+?\d[\d\s().\-]{7,}\d)")
HOST_RE = re.compile(r"https?://([^/\s]+)", re.I)
CALLS = 0
MAX_CALLS = 32


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
        return PHONE_RE.sub("[phone]", EMAIL_RE.sub("[email]", s))
    if isinstance(s, dict):
        return {k: redact(v) for k, v in s.items()}
    if isinstance(s, list):
        return [redact(x) for x in s]
    return s


def name_of(obj: Any) -> str:
    if isinstance(obj, dict):
        return str(obj.get("name") or "")
    return str(obj or "")


def host_of(url: Any) -> str:
    if not isinstance(url, str) or not url:
        return ""
    m = HOST_RE.search(url)
    if m:
        return m.group(1).lower()[:60]
    low = url.lower()
    if "virtualcoworker.app" in low:
        return "virtualcoworker.app"
    if "virtualcoworker.com" in low:
        return "virtualcoworker.com"
    return "(non-url)"


def post_json(url: str, token: str, payload: dict[str, Any]) -> tuple[int, Any]:
    global CALLS
    CALLS += 1
    if CALLS > MAX_CALLS:
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
        with urllib.request.urlopen(req, timeout=30) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.getcode() or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}
    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, {"raw": raw[:200]}


def get(url: str, token: str) -> tuple[int, Any]:
    global CALLS
    CALLS += 1
    if CALLS > MAX_CALLS:
        return 0, {"error": "cap"}
    return http_get_json(url, access_token=token)


def count_val(body: Any) -> int | None:
    if not isinstance(body, dict):
        return None
    data = body.get("data")
    if isinstance(data, list) and data and isinstance(data[0], dict):
        row = data[0]
        for k, v in row.items():
            try:
                return int(v)
            except (TypeError, ValueError):
                continue
    return None


def grouped(body: Any, key: str) -> list[dict[str, Any]]:
    out = []
    if not isinstance(body, dict):
        return out
    for row in body.get("data") or []:
        if not isinstance(row, dict):
            continue
        k = row.get(key)
        cnt = None
        for kk, v in row.items():
            if kk == key:
                continue
            try:
                cnt = int(v)
            except (TypeError, ValueError):
                continue
        out.append({"key": redact(name_of(k) if isinstance(k, dict) else k) or "(blank)", "count": cnt})
    return out


def sample_rows(records: list[dict[str, Any]], kind: str) -> dict[str, Any]:
    sources: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    regions: Counter[str] = Counter()
    countries: Counter[str] = Counter()
    creators: Counter[str] = Counter()
    form_src: Counter[str] = Counter()
    utm_src: Counter[str] = Counter()
    hosts: Counter[str] = Counter()
    gclid = 0
    gravity = 0
    recruit_id = 0
    preview = []
    for rec in records:
        st = rec.get("Lead_Status") or rec.get("Stage") or rec.get("Status") or ""
        if isinstance(st, dict):
            st = st.get("name")
        statuses[str(st or "(blank)")] += 1
        src = rec.get("Lead_Source") or rec.get("Last_Sync_Source") or ""
        if isinstance(src, dict):
            src = src.get("name")
        sources[str(src or "(blank)")] += 1
        regions[str(rec.get("Region") or "(blank)")] += 1
        countries[str(rec.get("Country") or rec.get("Mailing_Country") or rec.get("Billing_Country") or "(blank)")] += 1
        creators[name_of(rec.get("Created_By"))] += 1
        form_src[str(rec.get("Form_Source") or "(blank)")[:50]] += 1
        utm_src[str(rec.get("utm_source") or rec.get("UTM_Source") or "(blank)")[:40]] += 1
        for url_key in ("Referring_URL", "Website", "Company_Website", "Referrer"):
            h = host_of(rec.get(url_key))
            if h:
                hosts[h] += 1
        if rec.get("utm_gclid") or rec.get("UTM_Gclid"):
            gclid += 1
        if rec.get("Gravity_Form_Entry_ID"):
            gravity += 1
        if rec.get("Recruit_Job_Opening_ID"):
            recruit_id += 1
        company = rec.get("Company") or rec.get("Company_Name") or rec.get("Account_Name") or rec.get("Name") or ""
        if isinstance(company, dict):
            company = company.get("name")
        preview.append(
            {
                "first_name": str(rec.get("First_Name") or "")[:20],
                "company": str(company)[:40],
                "source": str(src or "")[:30],
                "status": str(st or "")[:36],
                "region": str(rec.get("Region") or "")[:16],
                "country": str(rec.get("Country") or rec.get("Mailing_Country") or "")[:20],
                "created": str(rec.get("Created_Time") or "")[:19],
                "created_by": name_of(rec.get("Created_By"))[:28],
                "form_source": str(rec.get("Form_Source") or "")[:40],
                "utm_source": str(rec.get("utm_source") or rec.get("UTM_Source") or "")[:24],
                "has_gclid": bool(rec.get("utm_gclid") or rec.get("UTM_Gclid")),
                "has_gravity": bool(rec.get("Gravity_Form_Entry_ID")),
                "referrer_host": host_of(rec.get("Referring_URL") or rec.get("Referrer") or ""),
            }
        )
    return {
        "kind": kind,
        "n": len(records),
        "statuses": dict(statuses.most_common(20)),
        "sources": dict(sources.most_common(15)),
        "regions": dict(regions.most_common(12)),
        "countries": dict(countries.most_common(12)),
        "created_by": dict(creators.most_common(12)),
        "form_source": dict(form_src.most_common(12)),
        "utm_source": dict(utm_src.most_common(12)),
        "referrer_hosts": dict(hosts.most_common(15)),
        "has_gclid": gclid,
        "has_gravity_id": gravity,
        "has_recruit_id": recruit_id,
        "preview": preview[:15],
    }


def main() -> int:
    load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    ensure_local_dir()
    creds = load_credentials()
    token = str(refresh_access_token(creds)["access_token"])
    api = creds["api_domain"]
    coql = crm_url(api, "/coql")
    since_90 = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00+00:00")
    since_2y = "2024-08-01T00:00:00+00:00"
    out: dict[str, Any] = {"generated_at": datetime.now(timezone.utc).isoformat(), "queries": {}}

    def q(label: str, sql: str) -> Any:
        st, body = post_json(coql, token, {"select_query": sql})
        rec = {"http": st, "sql": sql}
        if st != 200:
            rec["error"] = redact(body.get("message") if isinstance(body, dict) else str(body)[:180])
        elif "group by" in sql.lower():
            key = sql.split("select ", 1)[1].split(",", 1)[0].strip()
            rec["rows"] = grouped(body, key)
        else:
            rec["count"] = count_val(body)
        out["queries"][label] = rec
        print(f"{label}: http={st} count={rec.get('count')} rows={len(rec.get('rows') or [])} err={rec.get('error', '')[:60]}")
        return rec

    for mod in ("Leads", "Job_Orders", "Contacts", "Deals"):
        q(f"{mod}.all", f"select COUNT(id) from {mod} where Created_Time is not null")
        q(f"{mod}.90d", f"select COUNT(id) from {mod} where Created_Time >= '{since_90}'")
        q(f"{mod}.since_2024_08", f"select COUNT(id) from {mod} where Created_Time >= '{since_2y}'")

    q("Leads.gclid", "select COUNT(id) from Leads where utm_gclid is not null")
    q("Leads.gravity", "select COUNT(id) from Leads where Gravity_Form_Entry_ID is not null")
    q("Job_Orders.gclid", "select COUNT(id) from Job_Orders where UTM_Gclid is not null")
    q("Job_Orders.recruit_id", "select COUNT(id) from Job_Orders where Recruit_Job_Opening_ID is not null")

    q(
        "Leads.status_90d",
        f"select Lead_Status, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Lead_Status",
    )
    q(
        "Leads.source_90d",
        f"select Lead_Source, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Lead_Source",
    )
    q(
        "Leads.region_90d",
        f"select Region, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Region",
    )
    q(
        "Leads.form_90d",
        f"select Form_Source, COUNT(id) from Leads where Created_Time >= '{since_90}' group by Form_Source",
    )
    q(
        "Job_Orders.stage_90d",
        f"select Stage, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Stage",
    )
    q(
        "Job_Orders.region_90d",
        f"select Region, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Region",
    )
    q(
        "Job_Orders.sync_90d",
        f"select Last_Sync_Source, COUNT(id) from Job_Orders where Created_Time >= '{since_90}' group by Last_Sync_Source",
    )
    q(
        "Deals.stage_90d",
        f"select Stage, COUNT(id) from Deals where Created_Time >= '{since_90}' group by Stage",
    )
    q(
        "Deals.region_90d",
        f"select Region, COUNT(id) from Deals where Created_Time >= '{since_90}' group by Region",
    )

    samples = {}
    gets = [
        (
            "Leads",
            "First_Name,Company,Lead_Source,Lead_Status,Created_Time,Created_By,Country,Region,Form_Source,utm_source,utm_medium,utm_campaign,utm_gclid,Gravity_Form_Entry_ID,Referring_URL,Source_Type,Website",
        ),
        (
            "Job_Orders",
            "Name,First_Name,Company_Name,Stage,Created_Time,Created_By,Country,Region,UTM_Source,UTM_Medium,UTM_Campaign,UTM_Gclid,Last_Sync_Source,Client_Status,Company_Website,Recruit_Job_Opening_ID,Job_Title",
        ),
        (
            "Contacts",
            "First_Name,Account_Name,Lead_Source,Created_Time,Created_By,Mailing_Country,Region",
        ),
        (
            "Deals",
            "Deal_Name,Stage,Lead_Source,Created_Time,Created_By,Country,Region,Account_Name",
        ),
    ]
    for mod, fields in gets:
        if CALLS >= MAX_CALLS:
            break
        st, body = get(
            crm_url(api, f"/{mod}?per_page=30&sort_by=Created_Time&sort_order=desc&fields={fields}"),
            token,
        )
        recs = body.get("data") if isinstance(body, dict) else None
        if st != 200 or not isinstance(recs, list):
            samples[mod] = {"http": st, "error": redact((body or {}).get("message") if isinstance(body, dict) else st)}
            print(f"sample {mod}: http={st} err={samples[mod].get('error')}")
            continue
        samples[mod] = sample_rows([r for r in recs if isinstance(r, dict)], mod)
        samples[mod]["http"] = st
        print(f"sample {mod}: n={samples[mod]['n']} gclid={samples[mod]['has_gclid']} gravity={samples[mod]['has_gravity_id']}")

    out["samples"] = samples
    out["calls"] = CALLS
    write_json(LOCAL_ZOHO / "probe-pass2-2026-08-13.json", out)
    print(f"calls={CALLS} wrote probe-pass2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
