#!/usr/bin/env python3
"""Zoho CRM V8 modules + fields inventory (READ-only).

Writes sanitized ads-launch/zoho/CRM-SCHEMA-INVENTORY.md
Raw responses only under .local/zoho/. Never writes CRM records.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (
    BOOTSTRAP_SCOPES,
    DOCS_DIR,
    ensure_local_dir,
    crm_url,
    http_get_json,
    load_credentials,
    mask_secret,
    refresh_access_token,
    write_json,
)

INVENTORY_MD = DOCS_DIR / "CRM-SCHEMA-INVENTORY.md"
TRACKING_HINTS = (
    "gclid",
    "gbraid",
    "wbraid",
    "utm_",
    "submission",
    "vc_",
    "google_ads",
    "click_id",
    "landing",
    "referrer",
    "lp_version",
    "market",
)


def is_blocked(status: int, body: Any) -> tuple[bool, str]:
    if status in (401, 403):
        return True, f"HTTP {status} — auth or permission denied"
    if isinstance(body, dict):
        code = str(body.get("code") or "")
        msg = str(body.get("message") or "")
        if code in {"OAUTH_SCOPE_MISMATCH", "NO_PERMISSION", "AUTHORIZATION_FAILED", "INVALID_TOKEN"}:
            return True, f"{code}: {msg}"
        if "permission" in msg.lower() or "admin" in msg.lower():
            return True, msg
    return False, ""


def admin_request_paragraph() -> str:
    return (
        "**Request for Zoho admin (copy/paste):** George needs CRM API read access for Virtual Coworker "
        "lead inventory — not full Zoho One admin for every app. Please confirm: (1) **Zoho One seat** "
        "is assigned (login exists); (2) the **CRM application** is enabled on that seat; (3) the CRM "
        "**profile/role** allows Modules + Fields metadata API (Settings → Modules/Fields read) — a One "
        "seat alone does not grant CRM Admin; (4) a **Self Client** in the API Console for the correct "
        "data-center may be created by a developer with CRM access (Client ID/secret + grant code with "
        "READ-only scopes listed below) — Self Client ≠ CRM Admin; (5) separately, only a **CRM Admin** "
        "(or equivalent) can authorize the **native Zoho ↔ Google Ads** connector and change auto-tagging "
        "— do not treat Self Client OAuth as Ads connector approval. Scopes needed (READ only): "
        + ", ".join(BOOTSTRAP_SCOPES)
        + "."
    )


def least_privilege_runbook() -> str:
    return """## Production least-privilege runbook (after inventory)

1. **Keep bootstrap scopes READ-only** for inventory machines. Do not reuse ALL scopes in production.
2. **Production write path** (only after George approves schema + live test): narrow to the verified module, e.g. `ZohoCRM.modules.leads.CREATE` + `ZohoCRM.modules.leads.UPDATE` (or upsert equivalent) — never `modules.ALL` / `settings.ALL` unless proven required.
3. Store `ZOHO_CRM_CLIENT_ID`, `ZOHO_CRM_CLIENT_SECRET`, `ZOHO_CRM_REFRESH_TOKEN`, `ZOHO_CRM_ACCOUNTS_URL`, `ZOHO_CRM_API_DOMAIN` as **server-only** secrets (Vercel/env). Never `NEXT_PUBLIC_*`.
4. Feature-gate with `ZOHO_CRM_ENABLED=true` only when verified field API names are in the mapping worksheet.
5. Prefer external id `VC_Submission_ID` (or verified equivalent) for upsert idempotency.
6. **`--apply-schema` / field creation** requires explicit George approval — do not auto-create fields from these scripts.
7. Webhook (`ZOHO_WEBHOOK_URL`) remains a separate channel; webhook 200 ≠ `zoho_synced`.
8. Native Google Ads connector changes stay on the audit checklist — do not authorize from this CLI.
"""


def sanitize_field(f: dict[str, Any]) -> dict[str, Any]:
    return {
        "api_name": f.get("api_name"),
        "field_label": f.get("field_label") or f.get("display_label"),
        "data_type": f.get("data_type"),
        "custom_field": f.get("custom_field"),
        "system_mandatory": f.get("system_mandatory"),
        "external": f.get("external"),
        "unique": f.get("unique"),
        "read_only": f.get("read_only") or f.get("field_read_only"),
        "length": f.get("length"),
    }


def field_looks_tracking(api_name: str | None, label: str | None) -> bool:
    blob = f"{api_name or ''} {label or ''}".lower()
    return any(h in blob for h in TRACKING_HINTS)


def write_inventory_md(
    *,
    modules: list[dict[str, Any]],
    fields_by_module: dict[str, list[dict[str, Any]]],
    blocked: bool,
    block_reason: str,
    creds_meta: dict[str, str],
) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [
        "# Zoho CRM schema inventory (sanitized)",
        "",
        f"Generated: {now}",
        f"API: Zoho CRM **{creds_meta.get('version', 'v8')}**",
        f"Accounts URL: `{creds_meta.get('accounts_url')}`",
        f"API domain: `{creds_meta.get('api_domain')}`",
        f"Credentials source: `{creds_meta.get('source')}` (secrets masked)",
        "",
        "> Raw JSON lives only under `.local/zoho/` (gitignored). No PII / tokens in this file.",
        "",
        "## Bootstrap scopes used (READ-only)",
        "",
        "```",
        ",".join(BOOTSTRAP_SCOPES),
        "```",
        "",
    ]

    if blocked:
        lines += [
            "## Access blocked",
            "",
            f"Reason: {block_reason}",
            "",
            admin_request_paragraph(),
            "",
            least_privilege_runbook(),
            "",
            "## Modules",
            "",
            "_Inventory incomplete — fix access, then re-run `npm run zoho:inventory`._",
            "",
        ]
        INVENTORY_MD.write_text("\n".join(lines), encoding="utf-8")
        return

    lines += [
        "## Modules",
        "",
        "| API name | Plural | Singular | Access type |",
        "|----------|--------|----------|-------------|",
    ]
    for m in modules:
        lines.append(
            f"| `{m.get('api_name')}` | {m.get('plural_label') or ''} | "
            f"{m.get('singular_label') or ''} | {m.get('access_type') or ''} |"
        )

    lines += ["", "## Fields (by module)", ""]
    for mod_api, fields in fields_by_module.items():
        lines.append(f"### `{mod_api}` ({len(fields)} fields)")
        lines.append("")
        lines.append("| API name | Label | Type | Custom | Mandatory | External | Unique | Tracking-ish |")
        lines.append("|----------|-------|------|--------|-----------|----------|--------|--------------|")
        for f in fields:
            track = "yes" if field_looks_tracking(f.get("api_name"), f.get("field_label")) else ""
            lines.append(
                f"| `{f.get('api_name')}` | {f.get('field_label') or ''} | {f.get('data_type') or ''} | "
                f"{f.get('custom_field')} | {f.get('system_mandatory')} | {f.get('external')} | "
                f"{f.get('unique')} | {track} |"
            )
        lines.append("")

    # Suggested VC mapping targets (proposal only — not invented as live)
    lines += [
        "## Suggested VC tracking fields (proposal — not auto-created)",
        "",
        "If missing after inventory, propose creation (George approval + `--apply-schema` only — not implemented as auto-create):",
        "",
        "| Proposed API name | Purpose | Notes |",
        "|-------------------|---------|-------|",
        "| `VC_Submission_ID` | Idempotent external id | Prefer unique/external |",
        "| `GCLID` or use `$gclid` | Google click id | Prefer Zoho `$gclid` when supported |",
        "| `GBRAID` | iOS click id | Custom if absent |",
        "| `WBRAID` | Web click id | Custom if absent |",
        "| `UTM_Source` / `UTM_Medium` / `UTM_Campaign` / `UTM_Term` / `UTM_Content` | Campaign attribution | Map only if fields exist |",
        "| `VC_Market` | us / au | |",
        "| `VC_Category` | Role category | |",
        "| `VC_Variant` | LP variant | |",
        "| `VC_LP_Version` | Package version | |",
        "| `VC_Landing_Page_URL` | Landing URL | |",
        "",
        least_privilege_runbook(),
        "",
        "## Related docs",
        "",
        "- `GEORGE-5-MINUTE-SETUP.md`",
        "- `ZOHO-FIELD-MAPPING-WORKSHEET.md`",
        "- `NATIVE-GOOGLE-ADS-AUDIT.md`",
        "- `PRODUCTION-LEAST-PRIVILEGE.md`",
        "",
    ]
    INVENTORY_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ensure_local_dir()
    creds = load_credentials()
    print(
        f"Using credentials from {creds.get('source')} "
        f"(client_id={mask_secret(creds.get('client_id'))})"
    )
    token = refresh_access_token(creds)
    access = str(token["access_token"])
    api_domain = creds["api_domain"]

    status, modules_body = http_get_json(
        crm_url(api_domain, "/settings/modules"),
        access_token=access,
    )
    write_json(
        ensure_local_dir() / "raw-modules.json",
        {"http_status": status, "body": modules_body},
        mode=0o600,
    )

    blocked, reason = is_blocked(status, modules_body)
    modules: list[dict[str, Any]] = []
    fields_by_module: dict[str, list[dict[str, Any]]] = {}

    if not blocked and isinstance(modules_body, dict):
        raw_modules = modules_body.get("modules") or []
        if isinstance(raw_modules, list):
            for m in raw_modules:
                if not isinstance(m, dict):
                    continue
                if m.get("api_supported") is False:
                    continue
                modules.append(
                    {
                        "api_name": m.get("api_name"),
                        "plural_label": m.get("plural_label"),
                        "singular_label": m.get("singular_label"),
                        "access_type": m.get("access_type"),
                    }
                )

        # Field meta for common + custom modules (cap to keep runtime sane)
        priority = {"Leads", "Contacts", "Accounts", "Deals", "Campaigns"}
        ordered = sorted(
            modules,
            key=lambda m: (0 if m.get("api_name") in priority else 1, str(m.get("api_name"))),
        )
        for m in ordered[:40]:
            api_name = m.get("api_name")
            if not api_name:
                continue
            f_status, f_body = http_get_json(
                crm_url(api_domain, f"/settings/fields?module={api_name}"),
                access_token=access,
            )
            write_json(
                ensure_local_dir() / f"raw-fields-{api_name}.json",
                {"http_status": f_status, "body": f_body},
                mode=0o600,
            )
            f_blocked, f_reason = is_blocked(f_status, f_body)
            if f_blocked and api_name in priority:
                blocked, reason = True, f_reason
                break
            if isinstance(f_body, dict) and isinstance(f_body.get("fields"), list):
                fields_by_module[str(api_name)] = [
                    sanitize_field(f) for f in f_body["fields"] if isinstance(f, dict)
                ]
    else:
        blocked = True
        if not reason:
            reason = f"Modules API HTTP {status}"

    creds_meta = {
        "version": "v8",
        "accounts_url": creds["accounts_url"],
        "api_domain": api_domain,
        "source": str(creds.get("source")),
    }
    write_inventory_md(
        modules=modules,
        fields_by_module=fields_by_module,
        blocked=blocked,
        block_reason=reason,
        creds_meta=creds_meta,
    )
    write_json(
        DOCS_DIR / "zoho-schema-summary.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "blocked": blocked,
            "block_reason": reason or None,
            "module_count": len(modules),
            "modules": [m.get("api_name") for m in modules],
            "field_counts": {k: len(v) for k, v in fields_by_module.items()},
            "trackingish_fields": {
                mod: [
                    f.get("api_name")
                    for f in fields
                    if field_looks_tracking(f.get("api_name"), f.get("field_label"))
                ]
                for mod, fields in fields_by_module.items()
            },
        },
    )

    # Refresh worksheet stub checkmarks if we have Leads fields
    print(f"Wrote {INVENTORY_MD}")
    if blocked:
        print("ACCESS BLOCKED:", reason)
        print(admin_request_paragraph())
        return 1

    print(f"Modules: {len(modules)}; field modules inventoried: {len(fields_by_module)}")
    print("No CRM records were written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
