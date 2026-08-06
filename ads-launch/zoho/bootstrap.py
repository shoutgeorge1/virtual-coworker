#!/usr/bin/env python3
"""Turnkey Zoho CRM OAuth bootstrap (Self Client → refresh token).

READ-only scopes only. Saves credentials to .local/zoho/credentials.json (mode 0o600).
Never prints full secrets. Does not write CRM records.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _common import (
    BOOTSTRAP_SCOPES,
    CREDS_PATH,
    DEFAULT_ACCOUNTS_URL,
    DEFAULT_API_DOMAIN,
    crm_url,
    ensure_local_dir,
    exchange_grant_code,
    http_get_json,
    mask_secret,
    prompt,
    refresh_access_token,
    write_json,
)


def print_scope_instructions(accounts_url: str) -> None:
    scopes = ",".join(BOOTSTRAP_SCOPES)
    print(
        """
=== Zoho Self Client — READ-only bootstrap ===

1. Zoho API Console → Self Client for your CRM org data center.
2. Generate a grant code with these scopes (comma-separated, READ only):

"""
        + scopes
        + f"""

3. Accounts URL for your DC (examples):
   - US: https://accounts.zoho.com
   - AU: https://accounts.zoho.com.au
   - EU: https://accounts.zoho.eu
   Current default: {accounts_url}

4. Paste Client ID, Client Secret, and the one-time grant code below.
   Grant codes expire quickly — generate, then paste immediately.

Docs: https://www.zoho.com/crm/developer/docs/api/v8/scopes.html
"""
    )


def main() -> int:
    ensure_local_dir()
    accounts_url = prompt("Accounts URL", default=DEFAULT_ACCOUNTS_URL).rstrip("/")
    print_scope_instructions(accounts_url)

    client_id = prompt("Self Client ID", secret=True)
    client_secret = prompt("Self Client Secret", secret=True)
    code = prompt("Grant code", secret=True)
    api_domain_hint = prompt("API domain (blank = default / token)", default="")

    if not client_id or not client_secret or not code:
        print("Client ID, secret, and grant code are required.", file=sys.stderr)
        return 2

    print("Exchanging grant code…")
    token = exchange_grant_code(
        accounts_url=accounts_url,
        client_id=client_id,
        client_secret=client_secret,
        code=code,
    )

    api_domain = (
        api_domain_hint.rstrip("/")
        or str(token.get("api_domain") or DEFAULT_API_DOMAIN).rstrip("/")
    )

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": token["refresh_token"],
        "accounts_url": accounts_url,
        "api_domain": api_domain,
        "api_domain_from_token": token.get("api_domain"),
        "scopes": BOOTSTRAP_SCOPES,
        "token_type": token.get("token_type"),
        "expires_in_hint": token.get("expires_in"),
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "note": "Server-only. Never commit. Never NEXT_PUBLIC_*. Mode 0o600.",
    }
    write_json(CREDS_PATH, payload, mode=0o600)
    print(f"Saved credentials → {CREDS_PATH} (mode 600)")
    print(f"  client_id:     {mask_secret(client_id)}")
    print(f"  refresh_token: {mask_secret(str(token['refresh_token']))}")
    print(f"  accounts_url:  {accounts_url}")
    print(f"  api_domain:    {api_domain}")

    # Harmless org READ smoke test (no writes).
    print("Running org READ smoke test…")
    access = refresh_access_token(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": token["refresh_token"],
            "accounts_url": accounts_url,
            "api_domain": api_domain,
        }
    )
    status, org = http_get_json(
        crm_url(api_domain, "/org"),
        access_token=str(access["access_token"]),
    )
    if status == 200 and isinstance(org, dict):
        orgs = org.get("org") or []
        name = "(unknown)"
        if isinstance(orgs, list) and orgs:
            name = str(orgs[0].get("company_name") or orgs[0].get("domain_name") or name)
        print(f"Org READ OK — company/domain: {name}")
        write_json(
            ensure_local_dir() / "org-smoke.json",
            {"status": status, "sanitized": {"company_or_domain": name}},
            mode=0o600,
        )
    else:
        print(
            f"Org READ returned HTTP {status}. Credentials saved; check CRM Admin / scopes / DC.",
            file=sys.stderr,
        )
        write_json(
            ensure_local_dir() / "org-smoke.json",
            {"status": status, "error_redacted": True},
            mode=0o600,
        )
        return 1

    print(
        "\nNext: npm run zoho:inventory\n"
        "Then copy ZOHO_CRM_* vars into vision/.env.local (server-only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
