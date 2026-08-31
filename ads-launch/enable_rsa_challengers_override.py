#!/usr/bin/env python3
"""Enable the 29 posted RSA challengers. George overrode the Ad Strength gate.

Quote 2026-08-14: "As long as you're not turning anything off, I'm good."
PENDING is fine. Enable these 29 IDs only. Do not pause, disable, or edit
any other ads. Do not touch Brand, leave-alone groups, US Hire_VA_PH,
AU Recruitment_Hire_PH, or currently ENABLED winners.

On RESOURCE_EXHAUSTED: STOP. Do not retry.

Usage (from virtual-coworker):
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    ads-launch/enable_rsa_challengers_override.py
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
FORBIDDEN = {("US", "Hire_VA_PH"), ("AU", "Recruitment_Hire_PH")}
FORBIDDEN_AG_PREFIX = "Brand"

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


def snapshot_query(ad_ids: list[str]) -> str:
    ids = ", ".join(ad_ids)
    return f"""
      SELECT
        campaign.name,
        ad_group.id,
        ad_group.name,
        ad_group_ad.ad.id,
        ad_group_ad.status,
        ad_group_ad.ad_strength,
        ad_group_ad.ad.final_urls,
        ad_group_ad.ad.responsive_search_ad.path1,
        ad_group_ad.ad.responsive_search_ad.path2,
        ad_group_ad.ad.responsive_search_ad.headlines
      FROM ad_group_ad
      WHERE ad_group_ad.ad.id IN ({ids})
        AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
        AND ad_group_ad.status != REMOVED
    """


def pull_snapshot(ga, customer: str, ad_ids: list[str]) -> dict[str, dict]:
    by_ad: dict[str, dict] = {}
    for row in ga.search(customer_id=customer, query=snapshot_query(ad_ids)):
        rsa = row.ad_group_ad.ad.responsive_search_ad
        ad_id = str(row.ad_group_ad.ad.id)
        by_ad[ad_id] = {
            "ad_id": ad_id,
            "ag_id": str(row.ad_group.id),
            "ad_group": row.ad_group.name,
            "campaign": row.campaign.name,
            "status": row.ad_group_ad.status.name,
            "ad_strength": row.ad_group_ad.ad_strength.name,
            "final_urls": list(row.ad_group_ad.ad.final_urls),
            "path1": rsa.path1,
            "path2": rsa.path2,
            "headlines": [h.text for h in rsa.headlines],
        }
    return by_ad


def copy_matches(job: dict, live: dict) -> tuple[bool, str]:
    expected = list(job.get("live_headlines") or [])
    got = list(live.get("headlines") or [])
    if expected and set(expected) != set(got):
        return False, "headline set does not match posted challenger copy"
    if job.get("live_path1") and live.get("path1") != job["live_path1"]:
        return False, f"path1 {live.get('path1')!r} != {job['live_path1']!r}"
    if job.get("live_path2") and live.get("path2") != job["live_path2"]:
        return False, f"path2 {live.get('path2')!r} != {job['live_path2']!r}"
    expected_url = (job.get("live_final_urls") or [job.get("final_url")])[0]
    live_urls = live.get("final_urls") or []
    if expected_url and expected_url not in live_urls:
        return False, f"final URL {live_urls} missing {expected_url}"
    return True, "copy ok"


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


def mutate_enables(client, customer: str, jobs: list[dict], *, validate_only: bool):
    if not jobs:
        return {}, None
    ops = enable_ops(client, customer, jobs)
    req = client.get_type("MutateAdGroupAdsRequest")
    req.customer_id = customer
    req.operations.extend(ops)
    req.partial_failure = True
    req.validate_only = validate_only
    try:
        resp = client.get_service("AdGroupAdService").mutate_ad_group_ads(request=req)
    except GoogleAdsException as exc:
        if _quota(exc):
            raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
        raise RuntimeError(
            f"AdGroupAd enable {'validate' if validate_only else 'mutate'} failed ({customer}): {_api_error_text(exc)}"
        ) from exc
    pf = getattr(resp, "partial_failure_error", None)
    err_idx = _parse_partial_failures(pf)
    by_ag: dict[str, str | None] = {}
    for i, job in enumerate(jobs):
        by_ag[job["ad_group"]] = err_idx.get(i)
    return by_ag, (pf.message if pf and getattr(pf, "code", 0) else None)


def refuse_forbidden(jobs: list[dict]) -> None:
    for job in jobs:
        key = (job["market"], job["ad_group"])
        if key in FORBIDDEN or str(job["ad_group"]).startswith(FORBIDDEN_AG_PREFIX):
            raise SystemExit(f"Refusing forbidden group {job['market']} {job['ad_group']}")
        if "Brand" in str(job.get("campaign") or ""):
            raise SystemExit(f"Refusing Brand campaign {job['campaign']}")


def main() -> int:
    payload = json.loads(AUDIT.read_text(encoding="utf-8"))
    jobs = payload.get("jobs") or []
    if len(jobs) != 29:
        raise SystemExit(f"Expected 29 posted challengers, found {len(jobs)}")
    refuse_forbidden(jobs)
    allowed = {(j["market"], j["ad_id"]) for j in jobs}
    us_ids = [j["ad_id"] for j in jobs if j["market"] == "US"]
    au_ids = [j["ad_id"] for j in jobs if j["market"] == "AU"]
    print(f"Jobs: {len(jobs)} · US {len(us_ids)} · AU {len(au_ids)}")
    print("Override: enable these 29 even if PENDING. Do not pause anything else.")

    settings = load_settings()
    print(f"Access level: {settings.access_level} · MCC login set")
    client = build_client(settings)
    ga = client.get_service("GoogleAdsService")
    api_calls = 0
    mutate_items = 0
    errors: list[str] = []
    live: dict[str, dict[str, dict]] = {}

    for market, customer, ids in (("US", US, us_ids), ("AU", AU, au_ids)):
        print(f"API {api_calls + 1} · snapshot {market} ({len(ids)} ad IDs)")
        api_calls += 1
        try:
            live[market] = pull_snapshot(ga, customer, ids)
        except GoogleAdsException as exc:
            if _quota(exc):
                raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
            raise
        print(f"  rows {len(live[market])}")

    to_enable: list[dict] = []
    for job in jobs:
        where = f"{job['market']} {job['ad_group']} {job['ad_id']}"
        if (job["market"], job["ad_id"]) not in allowed:
            raise SystemExit(f"Refusing unexpected ad {where}")
        row = live.get(job["market"], {}).get(job["ad_id"])
        if not row:
            job["enabled"] = False
            job["left_paused"] = True
            job["error"] = "missing from snapshot"
            job["note"] = "Ad ID not returned in snapshot — skipped. Nothing else paused."
            errors.append(f"missing: {where}")
            print(f"  SKIP missing {where}")
            continue
        if row["ad_group"] != job["ad_group"] or row["ag_id"] != str(job["ag_id"]):
            job["enabled"] = False
            job["left_paused"] = True
            job["error"] = "ad group mismatch"
            job["note"] = f"Snapshot ad group {row['ad_group']}/{row['ag_id']} != {job['ad_group']}/{job['ag_id']} — skipped."
            errors.append(f"mismatch: {where}")
            print(f"  SKIP mismatch {where}")
            continue
        ok, reason = copy_matches(job, row)
        job["ad_strength"] = row["ad_strength"]
        job["live_status"] = row["status"]
        job["live_final_urls"] = row["final_urls"]
        job["live_path1"] = row["path1"]
        job["live_path2"] = row["path2"]
        job["live_headlines"] = row["headlines"]
        job["copy_ok"] = ok
        print(f"  {row['status']:8} {row['ad_strength']:10} {job['market']} {job['ad_group']:32} {reason}")
        if not ok:
            job["enabled"] = False
            job["left_paused"] = row["status"] != "ENABLED"
            job["error"] = f"copy check failed: {reason}"
            job["note"] = f"Copy no longer matches posted challenger — skipped. Status left {row['status']}."
            errors.append(f"copy: {where} {reason}")
            continue
        if row["status"] == "ENABLED":
            job["enabled"] = True
            job["left_paused"] = False
            job["error"] = None
            job["note"] = "Already ENABLED. George override — left on. Nothing else touched."
            continue
        if row["status"] != "PAUSED":
            job["enabled"] = False
            job["left_paused"] = False
            job["error"] = f"unexpected status {row['status']}"
            job["note"] = f"Status is {row['status']}, not PAUSED — skipped. Did not change it."
            errors.append(f"status: {where} is {row['status']}")
            continue
        to_enable.append(job)

    print(f"To enable: {len(to_enable)}")

    validated: list[dict] = []
    for market, customer in (("US", US), ("AU", AU)):
        batch = [j for j in to_enable if j["market"] == market]
        if not batch:
            continue
        print(f"API {api_calls + 1} · validate_only enable {market} ({len(batch)})")
        api_calls += 1
        by_ag, pf_msg = mutate_enables(client, customer, batch, validate_only=True)
        if pf_msg:
            print(f"  PARTIAL validate {market}: {pf_msg}")
        for job in batch:
            err = by_ag.get(job["ad_group"])
            if err:
                job["error"] = f"validate_only failed: {err}"
                job["note"] = f"validate_only failed. Still PAUSED. Nothing else changed. {err}"
                job["enabled"] = False
                job["left_paused"] = True
                errors.append(f"validate {job['market']} {job['ad_group']}: {err}")
                print(f"  FAIL validate {job['ad_group']:32} {err}")
            else:
                validated.append(job)
                print(f"  OK   validate {job['ad_group']:32} ad={job['ad_id']}")

    for market, customer in (("US", US), ("AU", AU)):
        batch = [j for j in validated if j["market"] == market]
        if not batch:
            continue
        print(f"API {api_calls + 1} · ENABLE {market} ({len(batch)})")
        api_calls += 1
        mutate_items += len(batch)
        by_ag, pf_msg = mutate_enables(client, customer, batch, validate_only=False)
        if pf_msg:
            errors.append(f"enable {market}: {pf_msg}")
            print(f"  PARTIAL enable {market}: {pf_msg}")
        for job in batch:
            err = by_ag.get(job["ad_group"])
            if err:
                job["error"] = f"enable failed: {err}"
                job["note"] = f"Enable failed. Still PAUSED. Nothing else paused. {err}"
                job["enabled"] = False
                job["left_paused"] = True
                print(f"  FAIL enable {job['ad_group']:32} {err}")
            else:
                job["enabled"] = True
                job["left_paused"] = False
                job["live_status"] = "ENABLED"
                job["action"] = "enable_override_pending"
                job["error"] = None
                job["note"] = (
                    "Enabled — George overrode the Ad Strength gate. "
                    f"Google still reports {job.get('ad_strength') or 'PENDING'}. "
                    "Nothing else was paused."
                )
                print(f"  OK   enable {job['ad_group']:32} ad={job['ad_id']}")

    enabled_jobs = [j for j in jobs if j.get("enabled")]
    if enabled_jobs:
        confirm: dict[str, dict[str, dict]] = {}
        for market, customer, ids in (("US", US, us_ids), ("AU", AU, au_ids)):
            if not any(j["market"] == market for j in enabled_jobs):
                continue
            print(f"API {api_calls + 1} · confirm {market}")
            api_calls += 1
            try:
                confirm[market] = pull_snapshot(ga, customer, ids)
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
            job["live_final_urls"] = row["final_urls"]
            job["live_path1"] = row["path1"]
            job["live_path2"] = row["path2"]
            job["live_headlines"] = row["headlines"]
            if job.get("enabled") and row["status"] != "ENABLED":
                job["error"] = (job.get("error") or "") + f" confirm status {row['status']}"
                job["left_paused"] = row["status"] == "PAUSED"
                job["enabled"] = False
                job["note"] = f"Enable mutate ran but confirm status is {row['status']}. Did not pause anything else."

    enabled_n = sum(1 for j in jobs if j.get("enabled"))
    paused_n = sum(1 for j in jobs if j.get("left_paused") and not j.get("enabled"))
    fail_n = sum(1 for j in jobs if j.get("error"))
    now = datetime.now(timezone.utc).isoformat()
    payload["generated_at"] = now
    payload["banner"] = (
        "ENABLED via API — George overrode the Ad Strength gate. "
        f"{enabled_n} of 29 challengers ON. PENDING is fine. Nothing else paused."
    )
    payload["authorized_by"] = (
        "George 2026-08-14 · override PENDING · enable the 29 posted challengers · "
        "do not turn anything off"
    )
    payload["enable_pass"] = {
        "generated_at": now,
        "bar": "GEORGE OVERRIDE — ENABLE REGARDLESS OF PENDING",
        "api_calls": api_calls,
        "mutate_items": mutate_items,
        "all_pending": False,
        "override_pending": True,
        "enabled": enabled_n,
        "left_paused": paused_n,
        "failed": fail_n,
        "errors": errors,
    }
    payload["api_calls_this_pass"] = api_calls
    payload["counts"]["enabled_excellent"] = sum(
        1 for j in jobs if j.get("enabled") and j.get("ad_strength") == "EXCELLENT"
    )
    payload["counts"]["enabled_good"] = sum(
        1 for j in jobs if j.get("enabled") and j.get("ad_strength") == "GOOD"
    )
    payload["counts"]["enabled_above_average"] = enabled_n
    payload["counts"]["enabled_override"] = enabled_n
    payload["counts"]["left_paused"] = paused_n
    payload["counts"]["failed"] = fail_n
    payload["errors"] = errors
    payload["brand_untouched"] = True
    payload["winners_untouched"] = True
    payload["landing_pages_untouched"] = True
    payload["strength_note"] = (
        "George overrode PENDING. Enabled the 29 posted challenger IDs only. "
        f"enabled={enabled_n} failed={fail_n} api_calls={api_calls}."
    )
    AUDIT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {AUDIT}")
    print(
        f"\nDone. enabled={enabled_n} left_paused={paused_n} failed={fail_n} "
        f"api_calls={api_calls} mutate_items={mutate_items}"
    )
    if errors:
        print("Failures / skips:")
        for e in errors:
            print(f"  - {e}")
    return 1 if fail_n else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QuotaExhaustedError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
