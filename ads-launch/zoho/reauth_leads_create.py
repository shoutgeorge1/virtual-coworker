#!/usr/bin/env python3
"""Exchange a Self Client grant, verify Leads.CREATE, then replace refresh token.

Reads the one-time grant from stdin. Never prints tokens, grant, or secrets.
Does not set ZOHO_CRM_ENABLED or ZOHO_SUBMISSION_ENABLED.
Does not overwrite .env until scope + metadata GET succeed.
"""

from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (  # noqa: E402
    DEFAULT_ACCOUNTS_URL,
    DEFAULT_API_DOMAIN,
    LOCAL_ZOHO,
    crm_url,
    ensure_local_dir,
    exchange_grant_code,
    http_form,
    http_get_json,
    refresh_access_token,
    write_json,
)

REPO = Path(__file__).resolve().parents[2]
ENV_PATH = REPO / ".env"
REQUIRED_CREATE = "zohocrm.modules.leads.create"
EXPECTED_READ = {
    "zohocrm.org.read",
    "zohocrm.users.read",
    "zohocrm.settings.modules.read",
    "zohocrm.settings.fields.read",
    "zohocrm.modules.read",
    "zohocrm.bulk.read",
    "zohocrm.coql.read",
}
FORBIDDEN = re.compile(
    r"zohocrm\.(modules\.(all|leads\.(update|delete))|settings\.all|modules\.\w+\.(update|delete|all))",
    re.I,
)


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


def parse_scopes(raw: str) -> list[str]:
    return [p.strip() for p in raw.replace(",", " ").split() if p.strip()]


def norm(scope: str) -> str:
    return scope.strip().lower()


def token_info(accounts_url: str, access_token: str) -> tuple[int, dict]:
    status, data = http_form(
        f"{accounts_url.rstrip('/')}/oauth/v2/token/info",
        {"access_token": access_token},
    )
    if not isinstance(data, dict):
        return status, {}
    return status, data


def replace_env_refresh(path: Path, new_refresh: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    found = False
    out: list[str] = []
    for line in lines:
        if line.startswith("ZOHO_CRM_REFRESH_TOKEN="):
            out.append(f"ZOHO_CRM_REFRESH_TOKEN={new_refresh}\n")
            found = True
        else:
            out.append(line)
    if not found:
        if out and not out[-1].endswith("\n"):
            out[-1] = out[-1] + "\n"
        out.append(f"ZOHO_CRM_REFRESH_TOKEN={new_refresh}\n")
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text("".join(out), encoding="utf-8")
    os.chmod(tmp, 0o600)
    tmp.replace(path)
    os.chmod(path, 0o600)


def main() -> int:
    load_dotenv(ENV_PATH)
    if (os.environ.get("ZOHO_CRM_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_CRM_ENABLED is true")
        return 2
    if (os.environ.get("ZOHO_SUBMISSION_ENABLED") or "").strip().lower() == "true":
        print("Refusing: ZOHO_SUBMISSION_ENABLED is true")
        return 2

    grant = sys.stdin.read().strip()
    if not grant:
        print("No grant on stdin")
        return 2

    client_id = (os.environ.get("ZOHO_CRM_CLIENT_ID") or "").strip()
    client_secret = (os.environ.get("ZOHO_CRM_CLIENT_SECRET") or "").strip()
    accounts = (os.environ.get("ZOHO_CRM_ACCOUNTS_URL") or "").strip() or DEFAULT_ACCOUNTS_URL
    api_domain = (os.environ.get("ZOHO_CRM_API_DOMAIN") or "").strip() or DEFAULT_API_DOMAIN
    if not client_id or not client_secret:
        print("Missing ZOHO_CRM_CLIENT_ID or ZOHO_CRM_CLIENT_SECRET")
        return 2

    print("Exchanging grant…")
    try:
        token = exchange_grant_code(
            accounts_url=accounts,
            client_id=client_id,
            client_secret=client_secret,
            code=grant,
        )
    except SystemExit as e:
        print(str(e))
        return 1

    if not token.get("refresh_token") or not token.get("access_token"):
        print("Exchange failed: missing token fields")
        return 1

    api_domain = str(token.get("api_domain") or api_domain).rstrip("/")
    raw_scope = str(token.get("scope") or "")
    print("Exchange HTTP 200. Checking token info…")

    info_status, info = token_info(accounts, str(token["access_token"]))
    info_scope = str(info.get("scope") or info.get("scopes") or "")
    combined = raw_scope or info_scope
    scopes = parse_scopes(combined)
    if not scopes and info_scope:
        scopes = parse_scopes(info_scope)
    lowered = {norm(s) for s in scopes}

    print(f"token_info HTTP {info_status}")
    print("scopes_returned=" + (",".join(scopes) if scopes else "(none in token body)"))

    forbidden_hits = [s for s in scopes if FORBIDDEN.search(s)]
    missing_create = REQUIRED_CREATE not in lowered
    missing_reads = sorted(EXPECTED_READ - lowered)

    ensure_local_dir()
    write_json(
        LOCAL_ZOHO / "reauth-verify.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "exchange_ok": True,
            "token_info_http": info_status,
            "scopes": scopes,
            "has_leads_create": not missing_create,
            "missing_reads": missing_reads,
            "forbidden_hits": forbidden_hits,
            "api_domain": api_domain,
            "env_updated": False,
        },
    )

    if missing_create:
        print("VERIFY FAIL: Leads.CREATE not on token. Old refresh token left unchanged.")
        return 1
    if forbidden_hits:
        print("VERIFY FAIL: token has extra write/all scopes. Old refresh token left unchanged.")
        print("forbidden=" + ",".join(forbidden_hits))
        return 1
    if missing_reads:
        print("VERIFY WARN: missing expected read scopes: " + ",".join(missing_reads))

    print("Scope OK (Leads.CREATE present, no UPDATE/DELETE/ALL). Metadata GET…")
    access = refresh_access_token(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": token["refresh_token"],
            "accounts_url": accounts,
            "api_domain": api_domain,
        }
    )
    st, body = http_get_json(
        crm_url(api_domain, "/settings/modules?module=Leads"),
        access_token=str(access["access_token"]),
    )
    print(f"metadata GET HTTP {st}")
    if st != 200:
        print("VERIFY FAIL: metadata GET failed. Old refresh token left unchanged.")
        return 1

    print("Verified. Updating ZOHO_CRM_REFRESH_TOKEN in gitignored .env only…")
    replace_env_refresh(ENV_PATH, str(token["refresh_token"]))
    write_json(
        LOCAL_ZOHO / "reauth-verify.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "exchange_ok": True,
            "token_info_http": info_status,
            "scopes": scopes,
            "has_leads_create": True,
            "missing_reads": missing_reads,
            "forbidden_hits": [],
            "api_domain": api_domain,
            "metadata_http": st,
            "env_updated": True,
            "env_key": "ZOHO_CRM_REFRESH_TOKEN",
        },
    )
    print("Refresh token replaced. Production flags unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
