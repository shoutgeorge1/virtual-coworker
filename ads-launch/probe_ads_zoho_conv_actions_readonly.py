#!/usr/bin/env python3
"""Read-only Google Ads conversion-action settings for US + AU.

George authorized this inventory in the 2026-08-19 JO/Placement pipeline audit.

Hard rules:
- Exactly 2 GAQL calls (one per child account)
- conversion_action settings only — no metrics, campaigns, keywords, ads
- No mutate / upload / enable / pause
- Stop immediately on RESOURCE_EXHAUSTED
- Do not print tokens
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from sg_google_ads.client import build_client, run_gaql  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import (  # noqa: E402
    ApiAccessError,
    QuotaExhaustedError,
    SgGoogleAdsError,
)

if (SG_ROOT / ".env").is_file():
    load_dotenv(SG_ROOT / ".env")
_vc_env = SG_ROOT / "clients" / "virtual-coworker.env"
if _vc_env.is_file():
    load_dotenv(_vc_env, override=True)

US_ID = "4967151855"
AU_ID = "5735391940"
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / ".local" / "ads" / "conv-actions-2026-08-19.json"

GAQL = """
    SELECT
      conversion_action.id,
      conversion_action.name,
      conversion_action.status,
      conversion_action.type,
      conversion_action.category,
      conversion_action.origin,
      conversion_action.primary_for_goal,
      conversion_action.counting_type,
      conversion_action.include_in_conversions_metric,
      conversion_action.click_through_lookback_window_days,
      conversion_action.view_through_lookback_window_days,
      conversion_action.value_settings.default_value,
      conversion_action.value_settings.always_use_default_value
    FROM conversion_action
    WHERE conversion_action.status != 'REMOVED'
"""


def _enum(val: Any) -> str | None:
    if val is None:
        return None
    if hasattr(val, "name"):
        return str(val.name)
    text = str(val).strip()
    return text or None


def _num(val: Any) -> float:
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def parse_rows(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        ca = row.conversion_action
        vs = getattr(ca, "value_settings", None)
        out.append(
            {
                "id": str(getattr(ca, "id", "") or ""),
                "name": ca.name,
                "status": _enum(ca.status),
                "type": _enum(ca.type_),
                "category": _enum(ca.category),
                "origin": _enum(getattr(ca, "origin", None)),
                "primary_for_goal": bool(getattr(ca, "primary_for_goal", False)),
                "counting_type": _enum(ca.counting_type),
                "include_in_conversions_metric": bool(
                    getattr(ca, "include_in_conversions_metric", False)
                ),
                "click_window_days": int(
                    getattr(ca, "click_through_lookback_window_days", 0) or 0
                ),
                "view_window_days": int(
                    getattr(ca, "view_through_lookback_window_days", 0) or 0
                ),
                "default_value": _num(getattr(vs, "default_value", 0) if vs else 0),
                "always_use_default_value": bool(
                    getattr(vs, "always_use_default_value", False) if vs else False
                ),
            }
        )
    return out


def interesting(row: dict[str, Any]) -> bool:
    blob = f"{row.get('name') or ''} {row.get('type') or ''}".lower()
    needles = (
        "zoho",
        "job order",
        "placement",
        "discovery",
        "upload",
        "oci",
        "zapier",
        "recruit",
        "converted",
    )
    return any(n in blob for n in needles) or row.get("type") == "UPLOAD_CLICKS"


def pull_one(client: Any, customer_id: str, label: str) -> dict[str, Any]:
    print(f"GAQL 1/{label} conversion_action settings {customer_id}", flush=True)
    try:
        rows = run_gaql(client, customer_id, GAQL)
    except QuotaExhaustedError as exc:
        return {"ok": False, "error": "RESOURCE_EXHAUSTED", "detail": str(exc)[:240]}
    except (ApiAccessError, SgGoogleAdsError) as exc:
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:240]}
    parsed = parse_rows(rows or [])
    return {
        "ok": True,
        "customer_id": customer_id,
        "row_count": len(parsed),
        "upload_or_crm_shaped": [r for r in parsed if interesting(r)],
        "placement_named": [r for r in parsed if "placement" in (r.get("name") or "").lower()],
        "all_names": [r["name"] for r in parsed],
    }


def main() -> int:
    settings = load_settings()
    client = build_client(settings)
    payload: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "api_calls_planned": 2,
        "hard_stop": None,
        "US": None,
        "AU": None,
    }
    payload["US"] = pull_one(client, US_ID, "US")
    if payload["US"].get("error") == "RESOURCE_EXHAUSTED":
        payload["hard_stop"] = "US RESOURCE_EXHAUSTED — did not call AU"
        print("STOP: US quota", flush=True)
    else:
        payload["AU"] = pull_one(client, AU_ID, "AU")
        if payload["AU"].get("error") == "RESOURCE_EXHAUSTED":
            payload["hard_stop"] = "AU RESOURCE_EXHAUSTED after US succeeded"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}", flush=True)
    us = payload.get("US") or {}
    au = payload.get("AU") or {}
    print(
        f"US ok={us.get('ok')} n={us.get('row_count')} "
        f"placement={len(us.get('placement_named') or [])} "
        f"crm={len(us.get('upload_or_crm_shaped') or [])}",
        flush=True,
    )
    print(
        f"AU ok={au.get('ok')} n={au.get('row_count')} "
        f"placement={len(au.get('placement_named') or [])} "
        f"crm={len(au.get('upload_or_crm_shaped') or [])}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
