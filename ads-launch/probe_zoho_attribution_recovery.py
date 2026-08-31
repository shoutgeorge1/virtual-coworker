#!/usr/bin/env python3
"""Pass 3 — cheap read-only Zoho reads for attribution recovery (2026-08-13).

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
GCLID_RE = re.compile(r"[A-Za-z0-9_-]{10,}")
CALLS = 0
MAX_CALLS = 16
STOPPED = None


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
        with urllib.request.urlopen(req, timeout=30) as res:
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


def get(url: str, token: str) -> tuple[int, Any]:
    global CALLS, STOPPED
    CALLS += 1
    if CALLS > MAX_CALLS:
        STOPPED = "cap"
        return 0, {"error": "cap"}
    st, body = http_get_json(url, access_token=token)
    if st in (429, 403):
        STOPPED = f"rate {st}"
    return st, body


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


def rows_of(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    data = body.get("data")
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


def sanitize_candidate(rec: dict[str, Any], kind: str) -> dict[str, Any]:
    company = rec.get("Company") or rec.get("Company_Name") or rec.get("Name") or rec.get("Deal_Name") or ""
    if isinstance(company, dict):
        company = company.get("name")
    client = rec.get("Client_Name")
    client_name = name_of(client) if isinstance(client, dict) else str(client or "")
    status = rec.get("Lead_Status") or rec.get("Stage") or ""
    if isinstance(status, dict):
        status = status.get("name")
    source = rec.get("Lead_Source") or rec.get("UTM_Source") or rec.get("utm_source") or ""
    if isinstance(source, dict):
        source = source.get("name")
    created_by = name_of(rec.get("Created_By"))
    owner = name_of(rec.get("Owner"))
    gclid = rec.get("utm_gclid") or rec.get("UTM_Gclid") or ""
    testish = any(
        x in f"{company} {client_name} {status}".lower()
        for x in ("test", "zoflow", "n/a", "na", "junk", "asdf")
    )
    junkish = str(status).lower() in {
        "junk lead",
        "decided against / not a fit",
        "not a fit",
    }
    return {
        "kind": kind,
        "id": str(rec.get("id") or "")[:24],
        "created": str(rec.get("Created_Time") or "")[:19],
        "region": str(rec.get("Region") or "")[:16],
        "status": str(status or "")[:48],
        "company": str(company or "")[:60],
        "source": str(source or "")[:32],
        "form_source": str(rec.get("Form_Source") or "")[:40],
        "utm_source": str(rec.get("utm_source") or rec.get("UTM_Source") or "")[:32],
        "utm_campaign": str(rec.get("utm_campaign") or rec.get("UTM_Campaign") or rec.get("Campaign_Name") or "")[:48],
        "created_by": created_by[:32],
        "owner": owner[:32],
        "has_gclid": click_present(gclid),
        "gclid_len": len(str(gclid)) if click_present(gclid) else 0,
        "has_enquiry_lookup": bool(client_name),
        "enquiry_lookup_name": client_name[:40],
        "job_order_via_form": rec.get("Job_Order_submitted_via_form"),
        "client_status": str(rec.get("Client_Status") or "")[:32],
        "looks_test": testish,
        "looks_junk_status": junkish,
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
    now = datetime.now(timezone.utc)
    since_90 = (now - timedelta(days=90)).strftime("%Y-%m-%dT00:00:00+00:00")
    since_180 = (now - timedelta(days=180)).strftime("%Y-%m-%dT00:00:00+00:00")
    out: dict[str, Any] = {
        "generated_at": now.isoformat(),
        "queries": {},
        "candidates": {},
        "lois": {},
        "calls": 0,
        "stopped_reason": None,
    }

    def q(label: str, sql: str) -> Any:
        global STOPPED
        if STOPPED:
            out["queries"][label] = {"skipped": STOPPED, "sql": sql}
            print(f"{label}: skipped ({STOPPED})")
            return out["queries"][label]
        st, body = post_json(coql, token, {"select_query": sql})
        rec: dict[str, Any] = {"http": st, "sql": sql}
        if st != 200:
            rec["error"] = redact(body.get("message") if isinstance(body, dict) else str(body)[:180])
        elif "limit" in sql.lower() and "count(" not in sql.lower():
            rec["n"] = len(rows_of(body))
            rec["rows"] = [sanitize_candidate(r, label) for r in rows_of(body)]
        else:
            rec["count"] = count_val(body)
        out["queries"][label] = rec
        print(f"{label}: http={st} count={rec.get('count')} n={rec.get('n')} err={str(rec.get('error', ''))[:80]}")
        return rec

    q("Leads.gclid_90d", f"select COUNT(id) from Leads where utm_gclid is not null and Created_Time >= '{since_90}'")
    q("Leads.gclid_180d", f"select COUNT(id) from Leads where utm_gclid is not null and Created_Time >= '{since_180}'")
    q("Job_Orders.gclid_90d", f"select COUNT(id) from Job_Orders where UTM_Gclid is not null and Created_Time >= '{since_90}'")
    q("Job_Orders.gclid_180d", f"select COUNT(id) from Job_Orders where UTM_Gclid is not null and Created_Time >= '{since_180}'")
    q("Job_Orders.linked_enquiry_90d", f"select COUNT(id) from Job_Orders where Client_Name is not null and Created_Time >= '{since_90}'")
    q("Leads.converted_90d", f"select COUNT(id) from Leads where Converted__s = true and Created_Time >= '{since_90}'")
    q("Leads.jo_via_form_90d", f"select COUNT(id) from Leads where Job_Order_submitted_via_form = true and Created_Time >= '{since_90}'")
    q("Calls.90d", f"select COUNT(id) from Calls where Created_Time >= '{since_90}'")

    q(
        "Leads.gclid_recent20",
        "select id, Created_Time, Region, Lead_Status, Company, Lead_Source, Form_Source, utm_source, utm_campaign, Campaign_Name, Job_Order_submitted_via_form, Created_By, utm_gclid from Leads where utm_gclid is not null order by Created_Time desc limit 20",
    )
    q(
        "Job_Orders.gclid_recent20",
        "select id, Created_Time, Region, Stage, Client_Status, UTM_Source, UTM_Campaign, Created_By, Owner, Name, Company_Name, Client_Name, UTM_Gclid from Job_Orders where UTM_Gclid is not null order by Created_Time desc limit 20",
    )

    # Lois metadata — users list already known; fetch AllUsers and keep Lois only, redacted.
    if not STOPPED:
        st, body = get(crm_url(api, "/users?type=AllUsers&page=1&per_page=200"), token)
        lois = None
        if st == 200 and isinstance(body, dict):
            for u in body.get("users") or []:
                if not isinstance(u, dict):
                    continue
                if "lois" in str(u.get("full_name") or "").lower() or "social marketing" in str(u.get("full_name") or "").lower():
                    lois = u
                    break
        if lois:
            email = str(lois.get("email") or "")
            domain = email.split("@")[-1] if "@" in email else ""
            out["lois"] = {
                "http": st,
                "full_name": lois.get("full_name"),
                "status": lois.get("status"),
                "confirmed": lois.get("confirm"),
                "profile": (lois.get("profile") or {}).get("name") if isinstance(lois.get("profile"), dict) else lois.get("profile"),
                "role": (lois.get("role") or {}).get("name") if isinstance(lois.get("role"), dict) else lois.get("role"),
                "email_domain": domain,
                "created_time": lois.get("created_time") or lois.get("Created_Time"),
                "modified_time": lois.get("Modified_Time") or lois.get("modified_time"),
                "last_activity": lois.get("last_activity") or lois.get("Last_Activity_Time"),
                "id_present": bool(lois.get("id")),
            }
            print(f"Lois: {out['lois']}")
        else:
            out["lois"] = {"http": st, "found": False, "error": redact(body.get("message") if isinstance(body, dict) else st)}
            print(f"Lois: not found http={st}")

    out["calls"] = CALLS
    out["stopped_reason"] = STOPPED
    write_json(LOCAL_ZOHO / "probe-attribution-recovery-2026-08-13.json", out)
    print(f"\nWrote {LOCAL_ZOHO / 'probe-attribution-recovery-2026-08-13.json'} calls={CALLS} stopped={STOPPED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
