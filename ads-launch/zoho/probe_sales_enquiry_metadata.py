#!/usr/bin/env python3
"""Read-only Zoho CRM v8 metadata for Sales Enquiries (Leads).

GET only: modules + Leads fields. Cap 3 CRM calls after token refresh.
Does not set ZOHO_CRM_ENABLED or ZOHO_SUBMISSION_ENABLED.
Never prints tokens or field values from records.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    http_get_json,
    load_credentials,
    refresh_access_token,
    write_json,
)

REPO = Path(__file__).resolve().parents[2]
ENV_PATH = REPO / ".env"
MAX_CRM_GETS = 3
CALLS = 0


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


def get(url: str, token: str) -> tuple[int, dict[str, Any] | str]:
    global CALLS
    if CALLS >= MAX_CRM_GETS:
        raise SystemExit(f"Cap reached ({MAX_CRM_GETS} CRM GETs). Stop.")
    CALLS += 1
    status, body = http_get_json(url, access_token=token)
    if status == 429 or (isinstance(body, dict) and str(body.get("code") or "") in {"RATE_LIMIT", "TOO_MANY_REQUESTS"}):
        raise SystemExit(f"RATE LIMIT on GET {url} HTTP {status}. Stop.")
    return status, body


def pick_vals(field: dict[str, Any]) -> list[str]:
    raw = field.get("pick_list_values") or []
    out: list[str] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                display = str(item.get("display_value") or item.get("actual_value") or "").strip()
                if display:
                    out.append(display)
    return out


def main() -> int:
    load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    if (os.environ.get("ZOHO_SUBMISSION_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_SUBMISSION_ENABLED is true (leave production posting off)")
        return 2

    ensure_local_dir()
    creds = load_credentials()
    token_body = refresh_access_token(creds)
    token = str(token_body["access_token"])
    api_domain = creds["api_domain"]
    print(f"Token refresh ok. api_domain={api_domain} version=v8")
    print(f"accounts_url={creds['accounts_url']}")
    print(f"source={creds.get('source')}")

    cached_modules = LOCAL_ZOHO / "raw-modules-sales-enquiry.json"
    reuse = "--reuse-modules" in sys.argv and cached_modules.is_file()
    if reuse:
        cached = json.loads(cached_modules.read_text(encoding="utf-8"))
        st, modules_body = int(cached.get("http_status") or 0), cached.get("body")
        print("Reusing cached modules metadata (no GET)")
    else:
        st, modules_body = get(crm_url(api_domain, "/settings/modules"), token)
        write_json(LOCAL_ZOHO / "raw-modules-sales-enquiry.json", {"http_status": st, "body": modules_body})
    if st != 200 or not isinstance(modules_body, dict):
        print(f"Modules GET failed HTTP {st}")
        return 1

    modules = modules_body.get("modules") or []
    candidates: list[dict[str, Any]] = []
    print("\nMODULES (api_supported)")
    for m in modules:
        if not isinstance(m, dict):
            continue
        if m.get("api_supported") is False:
            continue
        api = m.get("api_name")
        plural = m.get("plural_label") or ""
        singular = m.get("singular_label") or ""
        print(f"  {api} | plural={plural} | singular={singular}")
        blob = f"{api} {plural} {singular}".lower()
        if api == "Leads" or plural == "Sales Enquiries" or singular == "Sales Enquiry":
            candidates.append(m)
        elif "sales enquir" in blob and "history" not in blob and "_X_" not in str(api):
            candidates.append(m)

    target = None
    for m in candidates:
        if m.get("api_name") == "Leads":
            target = m
            break
    if not target and candidates:
        target = candidates[0]

    if not target:
        print("No Sales Enquiries / Leads module found")
        return 1
    print(f"\nCANDIDATES: {[c.get('api_name') for c in candidates]}")

    module_api = str(target.get("api_name"))
    print(f"\nTARGET module api_name={module_api} display={target.get('plural_label')} singular={target.get('singular_label')}")

    st, fields_body = get(
        crm_url(api_domain, f"/settings/fields?module={module_api}"),
        token,
    )
    write_json(LOCAL_ZOHO / f"raw-fields-{module_api}.json", {"http_status": st, "body": fields_body})
    if st != 200 or not isinstance(fields_body, dict):
        print(f"Fields GET failed HTTP {st}")
        return 1

    fields = [f for f in (fields_body.get("fields") or []) if isinstance(f, dict)]
    print(f"\nFIELDS count={len(fields)}")
    print("label | api_name | type | system_mandatory | read_only | custom")
    wanted = {
        "first_name",
        "last_name",
        "email",
        "phone",
        "company",
        "description",
        "lead_source",
        "lead_status",
        "region",
        "website",
        "referrer",
        "referring_url",
        "utm_gclid",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "gbraid",
        "wbraid",
        "campaign_name",
        "submission_timestamp",
        "form_source",
        "gravity_form_entry_id",
        "vc_submission_id",
        "adgroup",
        "ad_group",
        "keyword",
        "match",
        "device",
        "landing",
    }
    mapped_rows = []
    mandatory = []
    for f in fields:
        api = str(f.get("api_name") or "")
        label = str(f.get("field_label") or f.get("display_label") or "")
        dtype = str(f.get("data_type") or "")
        sys_mand = bool(f.get("system_mandatory"))
        required = bool(f.get("required"))
        read_only = bool(f.get("read_only") or f.get("field_read_only"))
        custom = bool(f.get("custom_field"))
        writable = not read_only
        row = {
            "label": label,
            "api_name": api,
            "type": dtype,
            "system_mandatory": sys_mand,
            "required": required,
            "writable": writable,
            "custom": custom,
            "length": f.get("length"),
        }
        if sys_mand or required:
            mandatory.append(row)
        key = api.lower()
        if key in wanted or any(w in key for w in wanted) or any(w in label.lower() for w in wanted):
            mapped_rows.append(row)
            extra = ""
            if api in {"Lead_Source", "Region", "Lead_Status", "Form_Source"}:
                vals = pick_vals(f)
                extra = f" picklist={vals[:40]}"
                row["picklist"] = vals
            print(
                f"  {label} | {api} | {dtype} | mand={sys_mand}/{required} | "
                f"writable={writable} | custom={custom}{extra}"
            )

    print("\nMANDATORY")
    for row in mandatory:
        print(f"  {row['label']} | {row['api_name']} | {row['type']}")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "api_domain": api_domain,
        "accounts_url": creds["accounts_url"],
        "api_version": "v8",
        "module_api_name": module_api,
        "module_plural": target.get("plural_label"),
        "module_singular": target.get("singular_label"),
        "field_count": len(fields),
        "mandatory": mandatory,
        "relevant": mapped_rows,
        "crm_gets": CALLS,
        "zoho_crm_enabled": (os.environ.get("ZOHO_CRM_ENABLED") or "").strip() or "unset",
        "zoho_submission_enabled": (os.environ.get("ZOHO_SUBMISSION_ENABLED") or "").strip() or "unset",
    }
    write_json(LOCAL_ZOHO / "sales-enquiry-metadata-summary.json", summary)
    print(f"\nCRM GETs used: {CALLS}/{MAX_CRM_GETS}")
    print("No records created or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
