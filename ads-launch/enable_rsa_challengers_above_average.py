#!/usr/bin/env python3
"""Enable posted RSA challengers if Google Ad Strength is GOOD or EXCELLENT.

George changed the bar 2026-08-14: above Average = GOOD + EXCELLENT.
AVERAGE / POOR / PENDING stay paused. Only the 29 ads in
ads-launch/_rsa_challenger_post.json. No other inventory.

Strength pull: 2 GAQL searches max (US + AU), those ad IDs only.
If ALL 29 are still PENDING: do not enable. Do not poll.

On RESOURCE_EXHAUSTED: STOP. Do not retry.

Usage (from virtual-coworker):
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    ads-launch/enable_rsa_challengers_above_average.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
if (SG_ROOT / "src").is_dir():
    sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402
from google.ads.googleads.errors import GoogleAdsException  # noqa: E402
from google.protobuf import field_mask_pb2  # noqa: E402

from sg_google_ads.client import build_client  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import QuotaExhaustedError  # noqa: E402

if (SG_ROOT / ".env").is_file():
    load_dotenv(SG_ROOT / ".env")
_vc_env = SG_ROOT / "clients" / "virtual-coworker.env"
if _vc_env.is_file():
    load_dotenv(_vc_env, override=True)

US = "4967151855"
AU = "5735391940"
CUSTOMERS = {"US": US, "AU": AU}
ENABLE_OK = {"GOOD", "EXCELLENT"}
LEAVE_PAUSED = {"AVERAGE", "POOR", "PENDING", "UNSPECIFIED", "UNKNOWN", None, ""}

REPO = Path(__file__).resolve().parents[1]
AUDIT = REPO / "ads-launch" / "_rsa_challenger_post.json"


def _quota(exc: BaseException) -> bool:
    t = str(exc).upper()
    return "RESOURCE_EXHAUSTED" in t or ("QUOTA" in t and "EXHAUST" in t)


def _api_error_text(exc: GoogleAdsException) -> str:
    parts = []
    failure = getattr(exc, "failure", None)
    if failure is not None:
        for err in failure.errors:
            loc = ""
            if err.location:
                fields = [f.field_name for f in err.location.field_path_elements]
                loc = " @ " + ".".join(fields) if fields else ""
            parts.append(f"{err.message}{loc}")
    return "; ".join(parts) if parts else str(exc)


def _parse_partial_failures(pf) -> dict[int, str]:
    pf_by_index: dict[int, str] = {}
    if not pf or not getattr(pf, "code", 0):
        return pf_by_index
    details = list(getattr(pf, "details", []) or [])
    try:
        from google.ads.googleads.v25.errors.types.errors import GoogleAdsFailure
    except ImportError:
        from google.ads.googleads.v21.errors.types.errors import GoogleAdsFailure  # type: ignore
    for detail in details:
        failure = GoogleAdsFailure()
        if detail.Is(failure.DESCRIPTOR):
            detail.Unpack(failure)
            for err in failure.errors:
                idx = None
                if err.location:
                    for el in err.location.field_path_elements:
                        if el.field_name == "operations":
                            idx = el.index
                            break
                if idx is not None:
                    pf_by_index[idx] = err.message
    return pf_by_index


def strength_query(ad_ids: list[str]) -> str:
    ids = ", ".join(ad_ids)
    return f"""
      SELECT
        campaign.name,
        ad_group.id,
        ad_group.name,
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.ad_strength
      FROM ad_group_ad
      WHERE ad_group_ad.ad.id IN ({ids})
        AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
        AND ad_group_ad.status != REMOVED
    """


def pull_strength(ga, customer: str, ad_ids: list[str]) -> dict[str, dict]:
    by_ad: dict[str, dict] = {}
    for row in ga.search(customer_id=customer, query=strength_query(ad_ids)):
        ad_id = str(row.ad_group_ad.ad.id)
        by_ad[ad_id] = {
            "ad_id": ad_id,
            "ag_id": str(row.ad_group.id),
            "ad_group": row.ad_group.name,
            "campaign": row.campaign.name,
            "status": row.ad_group_ad.status.name,
            "ad_strength": row.ad_group_ad.ad_strength.name,
        }
    return by_ad


def enable_ops(client, customer: str, jobs: list[dict]) -> list:
    aga_service = client.get_service("AdGroupAdService")
    ops = []
    for job in jobs:
        op = client.get_type("AdGroupAdOperation")
        aga = op.update
        aga.resource_name = aga_service.ad_group_ad_path(customer, job["ag_id"], job["ad_id"])
        aga.status = client.enums.AdGroupAdStatusEnum.ENABLED
        op.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
        ops.append(op)
    return ops


def mutate_enables(client, customer: str, jobs: list[dict]):
    if not jobs:
        return {}, None
    ops = enable_ops(client, customer, jobs)
    req = client.get_type("MutateAdGroupAdsRequest")
    req.customer_id = customer
    req.operations.extend(ops)
    req.partial_failure = True
    try:
        resp = client.get_service("AdGroupAdService").mutate_ad_group_ads(request=req)
    except GoogleAdsException as exc:
        if _quota(exc):
            raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
        raise RuntimeError(f"AdGroupAd enable failed ({customer}): {_api_error_text(exc)}") from exc
    pf = getattr(resp, "partial_failure_error", None)
    err_idx = _parse_partial_failures(pf)
    by_ag: dict[str, str | None] = {}
    for i, job in enumerate(jobs):
        by_ag[job["ad_group"]] = err_idx.get(i)
    return by_ag, (pf.message if pf and getattr(pf, "code", 0) else None)


def main() -> int:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    jobs = payload.get("jobs") or []
    if len(jobs) != 29:
        raise SystemExit(f"Expected 29 posted challengers, found {len(jobs)}")
    allowed = {(j["market"], j["ad_id"]) for j in jobs}
    us_ids = [j["ad_id"] for j in jobs if j["market"] == "US"]
    au_ids = [j["ad_id"] for j in jobs if j["market"] == "AU"]
    print(f"Jobs: {len(jobs)} · US {len(us_ids)} · AU {len(au_ids)}")
    print("Bar: enable GOOD + EXCELLENT. Leave AVERAGE / POOR / PENDING paused.")

    settings = load_settings()
    print(f"Access level: {settings.access_level} · MCC login set")
    client = build_client(settings)
    ga = client.get_service("GoogleAdsService")
    api_calls = 0
    mutate_items = 0
    errors: list[str] = []
    live: dict[str, dict[str, dict]] = {}

    for market, customer, ids in (("US", US, us_ids), ("AU", AU, au_ids)):
        print(f"API {api_calls + 1} · Ad Strength {market} ({len(ids)} ad IDs)")
        api_calls += 1
        try:
            live[market] = pull_strength(ga, customer, ids)
        except GoogleAdsException as exc:
            if _quota(exc):
                raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
            raise
        print(f"  rows {len(live[market])}")

    strengths: dict[str, int] = {}
    missing: list[str] = []
    to_enable: list[dict] = []
    for job in jobs:
        row = live.get(job["market"], {}).get(job["ad_id"])
        if not row:
            missing.append(f"{job['market']} {job['ad_group']} {job['ad_id']}")
            job["ad_strength"] = "MISSING"
            job["live_status"] = job.get("live_status") or "PAUSED"
            job["enabled"] = False
            job["left_paused"] = True
            job["note"] = "Ad ID not returned in strength pull — left PAUSED."
            continue
        if (job["market"], job["ad_id"]) not in allowed:
            raise SystemExit(f"Refusing unexpected ad {job['market']} {job['ad_id']}")
        strength = row["ad_strength"] or "UNKNOWN"
        strengths[strength] = strengths.get(strength, 0) + 1
        job["ad_strength"] = strength
        job["live_status"] = row["status"]
        print(f"  {strength:10} {row['status']:8} {job['market']} {job['ad_group']:32} {job['ad_id']}")
        if strength in ENABLE_OK:
            if row["status"] == "ENABLED":
                job["enabled"] = True
                job["left_paused"] = False
                job["note"] = f"Already ENABLED · Google Ad Strength {strength}."
            else:
                to_enable.append(job)
                job["note"] = f"Google Ad Strength {strength} (above Average) — enabling."
        else:
            job["enabled"] = False
            job["left_paused"] = True
            job["note"] = (
                f"Google Ad Strength {strength} — left PAUSED. "
                "Enable only Good/Excellent (above Average)."
            )

    if missing:
        errors.append("missing from strength pull: " + "; ".join(missing))
        print(f"MISSING {len(missing)}: {missing}")

    all_pending = all((j.get("ad_strength") in {None, "UNSPECIFIED", "UNKNOWN", "PENDING"}) for j in jobs)
    print(f"Strength mix: {strengths}")
    if all_pending:
        print("ALL 29 still PENDING. No enables. No further polls.")
        payload["generated_at"] = datetime.now(timezone.utc).isoformat()
        payload["banner"] = (
            "POSTED via API — enable if Good or Excellent (above Average). "
            "All 29 still PENDING after one strength pull. None enabled."
        )
        payload["authorized_by"] = "George 2026-08-14 · enable bar Good+ (above Average)"
        payload["enable_pass"] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "bar": "GOOD + EXCELLENT",
            "api_calls": api_calls,
            "mutate_items": 0,
            "all_pending": True,
            "strengths": strengths,
            "enabled": 0,
            "left_paused": 29,
        }
        payload["api_calls_this_pass"] = api_calls
        payload["counts"]["enabled_excellent"] = 0
        payload["counts"]["enabled_good"] = 0
        payload["counts"]["enabled_above_average"] = 0
        payload["counts"]["left_paused"] = 29
        payload["strength_note"] = (
            "One strength pull (US + AU, 29 ad IDs). All PENDING. None enabled. No loop."
        )
        AUDIT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {AUDIT}")
        return 0

    for market, customer in (("US", US), ("AU", AU)):
        batch = [j for j in to_enable if j["market"] == market]
        if not batch:
            continue
        print(f"API {api_calls + 1} · enable Good+ {market} ({len(batch)})")
        api_calls += 1
        mutate_items += len(batch)
        by_ag, pf_msg = mutate_enables(client, customer, batch)
        if pf_msg:
            errors.append(f"enable {market}: {pf_msg}")
            print(f"  PARTIAL enable {market}: {pf_msg}")
        for job in batch:
            err = by_ag.get(job["ad_group"])
            if err:
                job["error"] = f"enable failed: {err}"
                job["note"] = f"Strength {job['ad_strength']} but enable failed. Still PAUSED."
                job["enabled"] = False
                job["left_paused"] = True
                print(f"  FAIL enable {job['ad_group']:32} {err}")
            else:
                job["enabled"] = True
                job["left_paused"] = False
                job["live_status"] = "ENABLED"
                job["action"] = "enable_above_average"
                job["error"] = None
                job["note"] = (
                    f"Enabled — Google Ad Strength {job['ad_strength']} (above Average). "
                    "George can pause again if it underperforms."
                )
                print(f"  OK   enable {job['ad_group']:32} ad={job['ad_id']} {job['ad_strength']}")

    enabled_jobs = [j for j in jobs if j.get("enabled")]
    if enabled_jobs:
        confirm: dict[str, dict[str, dict]] = {}
        for market, customer, ids in (("US", US, us_ids), ("AU", AU, au_ids)):
            if not any(j["market"] == market for j in enabled_jobs):
                continue
            print(f"API {api_calls + 1} · confirm {market}")
            api_calls += 1
            try:
                confirm[market] = pull_strength(ga, customer, ids)
            except GoogleAdsException as exc:
                if _quota(exc):
                    raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
                raise
        for job in jobs:
            row = confirm.get(job["market"], {}).get(job["ad_id"])
            if not row:
                continue
            job["live_status"] = row["status"]
            job["ad_strength"] = row["ad_strength"] or job.get("ad_strength")
            if job.get("enabled") and row["status"] != "ENABLED":
                job["error"] = (job.get("error") or "") + f" confirm status {row['status']}"
                job["left_paused"] = True
                job["enabled"] = False
                job["note"] = f"Enable mutate ran but confirm status is {row['status']}."

    enabled_n = sum(1 for j in jobs if j.get("enabled"))
    good_n = sum(1 for j in jobs if j.get("enabled") and j.get("ad_strength") == "GOOD")
    excellent_n = sum(1 for j in jobs if j.get("enabled") and j.get("ad_strength") == "EXCELLENT")
    paused_n = sum(1 for j in jobs if j.get("left_paused") and not j.get("enabled"))
    fail_n = sum(1 for j in jobs if j.get("error"))
    payload["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload["banner"] = (
        "POSTED via API — enable if Good or Excellent (above Average). "
        "Average / Poor / Pending stay paused."
    )
    payload["authorized_by"] = "George 2026-08-14 · enable bar Good+ (above Average)"
    payload["enable_pass"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bar": "GOOD + EXCELLENT",
        "api_calls": api_calls,
        "mutate_items": mutate_items,
        "all_pending": False,
        "strengths": strengths,
        "enabled": enabled_n,
        "enabled_good": good_n,
        "enabled_excellent": excellent_n,
        "left_paused": paused_n,
        "failed": fail_n,
        "errors": errors,
    }
    payload["api_calls_this_pass"] = api_calls
    payload["counts"]["enabled_excellent"] = excellent_n
    payload["counts"]["enabled_good"] = good_n
    payload["counts"]["enabled_above_average"] = enabled_n
    payload["counts"]["left_paused"] = paused_n
    payload["counts"]["failed"] = fail_n
    payload["errors"] = list(payload.get("errors") or []) + errors
    payload["strength_note"] = (
        f"One strength pull (US + AU). Enabled Good+ only. "
        f"enabled={enabled_n} paused={paused_n} api_calls={api_calls}."
    )
    AUDIT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {AUDIT}")
    print(
        f"\nDone. enabled={enabled_n} (good={good_n} excellent={excellent_n}) "
        f"left_paused={paused_n} failed={fail_n} api_calls={api_calls} mutate_items={mutate_items}"
    )
    return 1 if fail_n else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QuotaExhaustedError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
