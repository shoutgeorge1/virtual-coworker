"""Shared helpers for Zoho CRM bootstrap / inventory CLIs.

Official Zoho CRM API V8 only. Never print full secrets. Raw payloads stay under .local/zoho/.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_ZOHO = REPO_ROOT / ".local" / "zoho"
CREDS_PATH = LOCAL_ZOHO / "credentials.json"
DOCS_DIR = Path(__file__).resolve().parent

# Bootstrap / inventory: READ-only scopes (no ALL / CREATE / UPDATE / DELETE).
# Verified against https://www.zoho.com/crm/developer/docs/api/v8/scopes.html
BOOTSTRAP_SCOPES = [
    "ZohoCRM.org.READ",
    "ZohoCRM.users.READ",
    "ZohoCRM.settings.modules.READ",
    "ZohoCRM.settings.fields.READ",
    "ZohoCRM.modules.READ",
    "ZohoCRM.bulk.READ",
    "ZohoCRM.coql.READ",
]

DEFAULT_ACCOUNTS_URL = "https://accounts.zoho.com"
DEFAULT_API_DOMAIN = "https://www.zohoapis.com"
CRM_API_VERSION = "v8"

_SECRET_RE = re.compile(
    r"(access_token|refresh_token|client_secret|code|authorization|api_key|password)=([^&\s]+)",
    re.I,
)


def mask_secret(value: str | None, keep: int = 4) -> str:
    if not value:
        return "(empty)"
    v = str(value)
    if len(v) <= keep * 2:
        return "***"
    return f"{v[:keep]}…{v[-keep:]}"


def redact_text(text: str) -> str:
    def _sub(m: re.Match[str]) -> str:
        return f"{m.group(1)}={mask_secret(m.group(2))}"

    return _SECRET_RE.sub(_sub, text)


def ensure_local_dir() -> Path:
    LOCAL_ZOHO.mkdir(parents=True, exist_ok=True)
    return LOCAL_ZOHO


def prompt(label: str, *, secret: bool = False, default: str | None = None) -> str:
    hint = f" [{default}]" if default else ""
    try:
        raw = input(f"{label}{hint}: ").strip()
    except EOFError:
        print("\nAborted: stdin closed.", file=sys.stderr)
        sys.exit(2)
    if not raw and default is not None:
        return default
    if secret and raw:
        print(f"  → received {mask_secret(raw)}")
    return raw


def write_json(path: Path, data: Any, *, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.chmod(tmp, mode)
    tmp.replace(path)
    os.chmod(path, mode)


def load_credentials() -> dict[str, Any]:
    """Load credentials from env (preferred in prod) or .local/zoho/credentials.json."""
    env_refresh = (os.environ.get("ZOHO_CRM_REFRESH_TOKEN") or "").strip()
    env_client = (os.environ.get("ZOHO_CRM_CLIENT_ID") or "").strip()
    env_secret = (os.environ.get("ZOHO_CRM_CLIENT_SECRET") or "").strip()
    accounts = (os.environ.get("ZOHO_CRM_ACCOUNTS_URL") or "").strip() or DEFAULT_ACCOUNTS_URL
    api_domain = (os.environ.get("ZOHO_CRM_API_DOMAIN") or "").strip() or DEFAULT_API_DOMAIN

    if env_refresh and env_client and env_secret:
        return {
            "client_id": env_client,
            "client_secret": env_secret,
            "refresh_token": env_refresh,
            "accounts_url": accounts.rstrip("/"),
            "api_domain": api_domain.rstrip("/"),
            "source": "env",
        }

    if CREDS_PATH.is_file():
        data = json.loads(CREDS_PATH.read_text(encoding="utf-8"))
        return {
            "client_id": data.get("client_id") or "",
            "client_secret": data.get("client_secret") or "",
            "refresh_token": data.get("refresh_token") or "",
            "accounts_url": (data.get("accounts_url") or DEFAULT_ACCOUNTS_URL).rstrip("/"),
            "api_domain": (data.get("api_domain") or DEFAULT_API_DOMAIN).rstrip("/"),
            "api_domain_from_token": data.get("api_domain_from_token"),
            "scopes": data.get("scopes") or BOOTSTRAP_SCOPES,
            "source": str(CREDS_PATH),
        }

    raise SystemExit(
        "No Zoho credentials found.\n"
        "Run: npm run zoho:bootstrap\n"
        "Or set ZOHO_CRM_CLIENT_ID / ZOHO_CRM_CLIENT_SECRET / ZOHO_CRM_REFRESH_TOKEN."
    )


def http_form(
    url: str,
    fields: dict[str, str],
    *,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any] | str]:
    body = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.getcode() or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error calling Zoho: {e.reason}") from e

    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, redact_text(raw)


def http_get_json(
    url: str,
    *,
    access_token: str,
    timeout: float = 30.0,
) -> tuple[int, dict[str, Any] | str]:
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            raw = res.read().decode("utf-8", errors="replace")
            status = res.getcode() or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    except urllib.error.URLError as e:
        raise SystemExit(f"Network error calling Zoho: {e.reason}") from e

    try:
        return status, json.loads(raw)
    except json.JSONDecodeError:
        return status, redact_text(raw)


def exchange_grant_code(
    *,
    accounts_url: str,
    client_id: str,
    client_secret: str,
    code: str,
) -> dict[str, Any]:
    status, data = http_form(
        f"{accounts_url.rstrip('/')}/oauth/v2/token",
        {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
        },
    )
    if status != 200 or not isinstance(data, dict) or not data.get("refresh_token"):
        err = data if isinstance(data, str) else json.dumps(
            {k: (mask_secret(str(v)) if "token" in k.lower() or "secret" in k.lower() else v) for k, v in data.items()}
        )
        raise SystemExit(f"Token exchange failed (HTTP {status}): {err}")
    return data


def refresh_access_token(creds: dict[str, Any]) -> dict[str, Any]:
    status, data = http_form(
        f"{creds['accounts_url']}/oauth/v2/token",
        {
            "grant_type": "refresh_token",
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
        },
    )
    if status != 200 or not isinstance(data, dict) or not data.get("access_token"):
        err = data if isinstance(data, str) else {
            k: (mask_secret(str(v)) if "token" in k.lower() else v) for k, v in data.items()
        }
        raise SystemExit(f"Refresh failed (HTTP {status}): {err}")
    # Preserve / update api domain from token response when present
    if data.get("api_domain"):
        creds["api_domain"] = str(data["api_domain"]).rstrip("/")
    return data


def crm_url(api_domain: str, path: str) -> str:
    base = api_domain.rstrip("/")
    p = path if path.startswith("/") else f"/{path}"
    return f"{base}/crm/{CRM_API_VERSION}{p}"
