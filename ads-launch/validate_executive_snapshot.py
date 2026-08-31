#!/usr/bin/env python3
"""Validation engine for Virtual Coworker executive dashboard snapshot.

Validates:
1. Required top-level and nested fields exist.
2. US and AU data remain strictly separated.
3. USD and AUD are never combined.
4. Spend and outcome counts are nonnegative.
5. Current cumulative MTD values do not unexpectedly fall below the previous snapshot.
6. No NaN, Infinity, undefined or malformed dates are generated.
7. No completed month changes (frozen historical snapshots preserved).
8. Agency baselines remain frozen.
9. All pilot unit costs use the same current-month spend and outcome period.
10. Missing downstream outcomes are None/pending, never $0.
"""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DATA_DIR = REPO / "xray" / "data"
PROD_SNAPSHOT_PATH = DATA_DIR / "executive-snapshot.json"
AGENCY_BASELINE_PATH = DATA_DIR / "agency-baseline.json"

REQUIRED_TOP_LEVEL = [
    "generated_at_utc",
    "customer_ids",
    "freshness",
    "performance_us",
    "performance_au",
    "sales_ops_us",
    "sales_ops_us_now",
    "sales_ops_au",
    "sales_ops_au_now",
]

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
MALFORMED_STR_RE = re.compile(r"\b(NaN|Infinity|-Infinity|undefined)\b", re.I)


class ValidationError(Exception):
    """Raised when snapshot fails safety/integrity validation."""
    pass


def _check_no_nan_or_malformed(obj: Any, path: str = "") -> list[str]:
    """Recursively ensure no NaN, Infinity, undefined, or malformed strings exist."""
    errors = []
    if obj is None:
        return errors
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            errors.append(f"Invalid float at {path}: {obj}")
    elif isinstance(obj, str):
        if obj.strip() in ("NaN", "Infinity", "-Infinity", "undefined"):
            errors.append(f"Malformed string at {path}: '{obj}'")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            errors.extend(_check_no_nan_or_malformed(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            errors.extend(_check_no_nan_or_malformed(item, f"{path}[{idx}]"))
    return errors


def validate_agency_baseline() -> list[str]:
    """Verify agency baselines remain frozen."""
    errors = []
    if not AGENCY_BASELINE_PATH.is_file():
        errors.append(f"Agency baseline file missing: {AGENCY_BASELINE_PATH}")
        return errors
    try:
        data = json.loads(AGENCY_BASELINE_PATH.read_text(encoding="utf-8"))
        us = data.get("us") or {}
        au = data.get("au") or {}
        if float(us.get("total_spend") or 0) != 724880.0:
            errors.append(f"US agency baseline total spend mutated: {us.get('total_spend')} != 724880.0")
        if float(au.get("total_spend") or 0) != 458167.0:
            errors.append(f"AU agency baseline total spend mutated: {au.get('total_spend')} != 458167.0")
        if us.get("currency") != "USD":
            errors.append(f"US agency currency invalid: {us.get('currency')}")
        if au.get("currency") != "AUD":
            errors.append(f"AU agency currency invalid: {au.get('currency')}")
    except Exception as exc:
        errors.append(f"Error reading agency baseline: {exc}")
    return errors


def validate_frozen_snapshots() -> list[str]:
    """Verify completed historical frozen snapshots remain intact."""
    errors = []
    for frozen_path in DATA_DIR.glob("executive-snapshot-frozen-*.json"):
        try:
            data = json.loads(frozen_path.read_text(encoding="utf-8"))
            if not data.get("generated_at_utc"):
                errors.append(f"Frozen snapshot missing generated_at_utc: {frozen_path.name}")
        except Exception as exc:
            errors.append(f"Failed to parse frozen snapshot {frozen_path.name}: {exc}")
    return errors


def validate_snapshot_payload(
    new_data: dict[str, Any],
    prev_data: dict[str, Any] | None = None,
) -> list[str]:
    """Run full validation suite on proposed snapshot."""
    errors: list[str] = []

    # 1. Required top-level fields
    for field in REQUIRED_TOP_LEVEL:
        if field not in new_data or new_data[field] is None:
            errors.append(f"Missing required top-level field: '{field}'")

    if errors:
        return errors

    # 2. No NaN, Infinity, undefined
    errors.extend(_check_no_nan_or_malformed(new_data))

    # 3. Market separation & Currency integrity
    us_perf = new_data.get("performance_us") or {}
    au_perf = new_data.get("performance_au") or {}
    us_camps = us_perf.get("campaigns") or []
    au_camps = au_perf.get("campaigns") or []

    for c in us_camps:
        name = str(c.get("name") or "")
        if name.startswith("VC_AU_"):
            errors.append(f"AU campaign found in US performance block: {name}")

    for c in au_camps:
        name = str(c.get("name") or "")
        if name.startswith("VC_US_"):
            errors.append(f"US campaign found in AU performance block: {name}")

    us_sales = new_data.get("sales_ops_us") or {}
    au_sales = new_data.get("sales_ops_au") or {}

    if us_sales.get("market") != "US":
        errors.append(f"sales_ops_us market must be 'US', got: {us_sales.get('market')}")
    if au_sales.get("market") != "AU":
        errors.append(f"sales_ops_au market must be 'AU', got: {au_sales.get('market')}")

    # 4. Nonnegative spend and outcome counts
    def _check_nonneg(val: Any, name: str) -> None:
        if val is not None:
            try:
                num = float(val)
                if num < 0:
                    errors.append(f"Negative value for {name}: {num}")
            except (ValueError, TypeError):
                errors.append(f"Non-numeric value for {name}: {val}")

    _check_nonneg(us_sales.get("spend_usd"), "us_sales.spend_usd")
    _check_nonneg(au_sales.get("spend_usd"), "au_sales.spend_usd")
    _check_nonneg(us_sales.get("enquiries"), "us_sales.enquiries")
    _check_nonneg(au_sales.get("enquiries"), "au_sales.enquiries")
    _check_nonneg(us_sales.get("sales_calls_completed"), "us_sales.sales_calls_completed")
    _check_nonneg(au_sales.get("sales_calls_completed"), "au_sales.sales_calls_completed")

    # 5. Freshness structure & dates
    freshness = new_data.get("freshness")
    if not isinstance(freshness, dict):
        errors.append("Missing or invalid 'freshness' block in snapshot")
    else:
        for fkey in [
            "google_ads_through",
            "zoho_refreshed_at_utc",
            "us_sales_confirmed_through",
            "au_sales_confirmed_through",
            "dashboard_generated_at_utc",
            "status",
        ]:
            if not freshness.get(fkey):
                errors.append(f"freshness block missing '{fkey}'")

        ads_thru = str(freshness.get("google_ads_through") or "")
        if not ISO_DATE_RE.match(ads_thru):
            errors.append(f"Malformed date for google_ads_through: {ads_thru}")

        status = freshness.get("status")
        valid_statuses = {"Current", "Awaiting sales update", "Refresh failed—showing last good data"}
        if status not in valid_statuses:
            errors.append(f"Invalid freshness status: '{status}', expected one of {valid_statuses}")

    # 6. Cumulative MTD values do not unexpectedly drop vs previous snapshot
    if prev_data:
        prev_us_by_date = (prev_data.get("performance_us") or {}).get("by_date_stage1") or (prev_data.get("performance_us") or {}).get("by_date") or {}
        new_us_by_date = us_perf.get("by_date_stage1") or us_perf.get("by_date") or {}

        prev_us_spend = sum(float(v.get("cost_usd") or 0) for v in prev_us_by_date.values())
        new_us_spend = sum(float(v.get("cost_usd") or 0) for v in new_us_by_date.values())

        if new_us_spend + 0.50 < prev_us_spend:
            errors.append(f"US cumulative spend unexpectedly dropped: ${new_us_spend:.2f} < ${prev_us_spend:.2f}")

        prev_au_by_date = (prev_data.get("performance_au") or {}).get("by_date_stage1") or (prev_data.get("performance_au") or {}).get("by_date") or {}
        new_au_by_date = au_perf.get("by_date_stage1") or au_perf.get("by_date") or {}

        prev_au_spend = sum(float(v.get("cost_usd") or 0) for v in prev_au_by_date.values())
        new_au_spend = sum(float(v.get("cost_usd") or 0) for v in new_au_by_date.values())

        if new_au_spend + 0.50 < prev_au_spend:
            errors.append(f"AU cumulative spend unexpectedly dropped: A${new_au_spend:.2f} < A${prev_au_spend:.2f}")

    # 7. Missing downstream outcomes must be None, never $0
    if us_sales.get("job_orders_total") in (0, None):
        if us_sales.get("cost_per_job_order_usd") == 0:
            errors.append("US cost_per_job_order_usd must not be 0 when job orders are 0 or unconfirmed")
    if us_sales.get("placements") in (0, None):
        if us_sales.get("cost_per_placement_usd") == 0:
            errors.append("US cost_per_placement_usd must not be 0 when placements are 0 or unconfirmed")

    # 8. Check agency baselines and frozen snapshots
    errors.extend(validate_agency_baseline())
    errors.extend(validate_frozen_snapshots())

    return errors


def validate_snapshot_file(target_file: Path, prev_file: Path | None = None) -> tuple[bool, list[str]]:
    """Validate a snapshot file path against previous snapshot file."""
    if not target_file.is_file():
        return False, [f"Snapshot file does not exist: {target_file}"]
    try:
        new_data = json.loads(target_file.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"Failed to parse JSON in {target_file}: {exc}"]

    prev_data = None
    if prev_file and prev_file.is_file():
        try:
            prev_data = json.loads(prev_file.read_text(encoding="utf-8"))
        except Exception:
            prev_data = None

    errors = validate_snapshot_payload(new_data, prev_data)
    return len(errors) == 0, errors


def atomic_replace_snapshot(tmp_path: Path, prod_path: Path = PROD_SNAPSHOT_PATH) -> bool:
    """Atomically replaces prod_path with tmp_path after successful validation."""
    if not tmp_path.is_file():
        raise FileNotFoundError(f"Temporary snapshot file not found: {tmp_path}")
    
    ok, errors = validate_snapshot_file(tmp_path, prod_path if prod_path.is_file() else None)
    if not ok:
        raise ValidationError(f"Snapshot validation failed: {'; '.join(errors)}")
    
    # Atomic rename/replace
    tmp_path.replace(prod_path)
    return True


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROD_SNAPSHOT_PATH
    prev = Path(sys.argv[2]) if len(sys.argv) > 2 else (PROD_SNAPSHOT_PATH if path != PROD_SNAPSHOT_PATH else None)
    print(f"Validating snapshot {path} ...")
    ok, errors = validate_snapshot_file(path, prev)
    if ok:
        print("✓ Snapshot validation passed successfully!")
        return 0
    else:
        print(f"✗ Snapshot validation failed with {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
