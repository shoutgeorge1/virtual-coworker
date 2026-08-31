#!/usr/bin/env python3
"""Post approved RSA challengers via Google Ads API.

George authorized this mutate 2026-08-14. Brand deferred.
Ready groups + US Administration_EA_PH (needs_claim; $8 already on live LP).
Action: update_paused only. Keep PAUSED until Google reports Excellent.

On RESOURCE_EXHAUSTED: STOP. Do not retry.

Usage (from virtual-coworker):
  /Users/george/Developer/shoutgeorge-ads/.venv/bin/python \\
    ads-launch/post_rsa_challengers.py
"""

from __future__ import annotations

import json
import sys
import time
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
US_CAMPS = ("VC_US_S_CORE", "VC_US_S_ROLES")
AU_CAMPS = ("VC_AU_S_CORE", "VC_AU_S_ROLES")
SKIP_AGS = {("US", "Hire_VA_PH"), ("AU", "Recruitment_Hire_PH")}
SKIP_BRAND = {"Brand_VC"}

REPO = Path(__file__).resolve().parents[1]
REVIEW = REPO / "xray" / "data" / "rsa-challenger-review.json"
OUT = REPO / "ads-launch" / "_rsa_challenger_post.json"

CUSTOMERS = {"US": US, "AU": AU}
CAMPS = {"US": US_CAMPS, "AU": AU_CAMPS}


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

        for detail in details:
            failure = GoogleAdsFailure.deserialize(detail.value) if hasattr(detail, "value") else None
            if failure is None:
                continue
            for err in failure.errors:
                idx = None
                if err.location:
                    for el in err.location.field_path_elements:
                        if el.field_name == "operations" and el.index is not None:
                            idx = int(el.index)
                if idx is not None:
                    pf_by_index[idx] = err.message
    except Exception:  # noqa: BLE001
        pass
    return pf_by_index


def _text_assets(client, texts: list[str]):
    out = []
    for t in texts:
        asset = client.get_type("AdTextAsset")
        asset.text = t
        out.append(asset)
    return out


def load_jobs() -> list[dict]:
    blob = json.loads(REVIEW.read_text(encoding="utf-8"))
    jobs: list[dict] = []
    for g in blob["groups"]:
        market = g["market"]
        ag = g["ad_group"]
        status = g["status"]
        include = status == "ready" or (
            status == "needs_claim" and market == "US" and ag == "Administration_EA_PH"
        )
        if not include:
            continue
        if ag in SKIP_BRAND or (market, ag) in SKIP_AGS:
            continue
        if g.get("enabled_rsas", 0) >= 3:
            continue
        ch = g.get("challenger") or {}
        if ch.get("api_action") != "update_paused":
            raise SystemExit(f"{market} {ag}: expected update_paused, got {ch.get('api_action')}")
        if not ch.get("paused_ad_id"):
            raise SystemExit(f"{market} {ag}: missing paused_ad_id")
        hs = [h["text"] if isinstance(h, dict) else h for h in ch["headlines"]]
        ds = [d["text"] if isinstance(d, dict) else d for d in ch["descriptions"]]
        jobs.append(
            {
                "market": market,
                "customer": CUSTOMERS[market],
                "campaign": g["campaign"],
                "ad_group": ag,
                "ag_id": str(g["ad_group_id"]),
                "review_status": status,
                "ad_id": str(ch["paused_ad_id"]),
                "paused_headline": ch.get("paused_headline"),
                "final_url": ch["final_url"] or g.get("final_url") or "",
                "path1": ch["path1"],
                "path2": ch["path2"],
                "headlines": hs,
                "descs": ds,
            }
        )
    return jobs


def validate_jobs(jobs: list[dict]) -> None:
    seen: list[tuple[str, str]] = []
    for job in jobs:
        where = f"{job['market']} {job['ad_group']}"
        hs, ds = job["headlines"], job["descs"]
        seen.append((job["market"], job["ad_group"]))
        if job["campaign"] not in CAMPS[job["market"]]:
            raise SystemExit(f"{where}: campaign {job['campaign']} not allowed")
        if len(hs) != 15:
            raise SystemExit(f"{where}: need 15 headlines, got {len(hs)}")
        if len(ds) != 4:
            raise SystemExit(f"{where}: need 4 descriptions, got {len(ds)}")
        if len(set(hs)) != 15:
            raise SystemExit(f"{where}: duplicate headlines")
        if len(set(ds)) != 4:
            raise SystemExit(f"{where}: duplicate descriptions")
        for h in hs:
            if len(h) > 30:
                raise SystemExit(f"{where}: headline too long ({len(h)}): {h}")
            if "wordpress" in h.lower() or "virtualcoworker.com/" in h.lower():
                raise SystemExit(f"{where}: WP/url in headline: {h}")
        for d in ds:
            if len(d) > 90:
                raise SystemExit(f"{where}: description too long ({len(d)}): {d}")
            if "wordpress" in d.lower() or "virtualcoworker.com/" in d.lower():
                raise SystemExit(f"{where}: WP/url in desc: {d}")
        p1, p2 = job["path1"], job["path2"]
        if not p1 or not p2 or len(p1) > 15 or len(p2) > 15:
            raise SystemExit(f"{where}: bad paths {p1!r}/{p2!r}")
        url = job["final_url"]
        prefix = "https://www.virtualcoworker.app/" + job["market"].lower()
        if not url.startswith(prefix):
            raise SystemExit(f"{where}: bad final_url {url}")
        if not job["ad_id"]:
            raise SystemExit(f"{where}: missing ad_id")
    if len(seen) != len(set(seen)):
        raise SystemExit("duplicate ad groups in jobs")
    print(f"Local validate OK · {len(jobs)} update_paused jobs")


def snapshot_query(market: str) -> str:
    camps = ", ".join(f"'{c}'" for c in CAMPS[market])
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
        ad_group_ad.ad.responsive_search_ad.headlines,
        ad_group_ad.ad.responsive_search_ad.descriptions
      FROM ad_group_ad
      WHERE campaign.name IN ({camps})
        AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
        AND ad_group_ad.status != REMOVED
    """


def pull_snapshot(ga, market: str, customer: str) -> dict[str, dict]:
    by_ag: dict[str, dict] = {}
    for row in ga.search(customer_id=customer, query=snapshot_query(market)):
        name = row.ad_group.name
        ag = by_ag.setdefault(
            name,
            {
                "ag_id": str(row.ad_group.id),
                "campaign": row.campaign.name,
                "ads": {},
                "enabled": 0,
                "paused": 0,
            },
        )
        ad_id = str(row.ad_group_ad.ad.id)
        st = row.ad_group_ad.status.name
        rsa = row.ad_group_ad.ad.responsive_search_ad
        strength = row.ad_group_ad.ad_strength.name
        rec = {
            "ad_id": ad_id,
            "status": st,
            "ad_strength": strength,
            "final_urls": list(row.ad_group_ad.ad.final_urls),
            "path1": rsa.path1,
            "path2": rsa.path2,
            "headlines": [h.text for h in rsa.headlines],
            "descriptions": [d.text for d in rsa.descriptions],
        }
        ag["ads"][ad_id] = rec
        if st == "ENABLED":
            ag["enabled"] += 1
        elif st == "PAUSED":
            ag["paused"] += 1
    return by_ag


def gate_jobs(jobs: list[dict], snaps: dict[str, dict[str, dict]]) -> tuple[list[dict], list[dict]]:
    ok: list[dict] = []
    skipped: list[dict] = []
    for job in jobs:
        where = f"{job['market']} {job['ad_group']}"
        snap = snaps[job["market"]].get(job["ad_group"])
        if not snap:
            skipped.append({**job, "skip": f"{where}: ad group missing from snapshot"})
            continue
        if snap["campaign"] not in CAMPS[job["market"]]:
            skipped.append({**job, "skip": f"{where}: campaign {snap['campaign']} not allowed"})
            continue
        if snap["enabled"] >= 3:
            skipped.append({**job, "skip": f"{where}: {snap['enabled']} enabled RSAs — leave alone"})
            continue
        live = snap["ads"].get(job["ad_id"])
        if not live:
            skipped.append({**job, "skip": f"{where}: paused_ad_id {job['ad_id']} not found"})
            continue
        if live["status"] != "PAUSED":
            skipped.append(
                {
                    **job,
                    "skip": f"{where}: ad {job['ad_id']} is {live['status']}, not PAUSED — will not edit",
                }
            )
            continue
        job["prior"] = {
            "status": live["status"],
            "ad_strength": live["ad_strength"],
            "final_urls": live["final_urls"],
            "path1": live["path1"],
            "path2": live["path2"],
            "headlines": live["headlines"][:3],
        }
        ok.append(job)
    return ok, skipped


def build_ad_update_ops(client, customer: str, jobs: list[dict]) -> list:
    ad_service = client.get_service("AdService")
    ops = []
    for job in jobs:
        op = client.get_type("AdOperation")
        ad = op.update
        ad.resource_name = ad_service.ad_path(customer, job["ad_id"])
        ad.final_urls.append(job["final_url"])
        ad.responsive_search_ad.headlines.extend(_text_assets(client, job["headlines"]))
        ad.responsive_search_ad.descriptions.extend(_text_assets(client, job["descs"]))
        ad.responsive_search_ad.path1 = job["path1"]
        ad.responsive_search_ad.path2 = job["path2"]
        op.update_mask.CopyFrom(
            field_mask_pb2.FieldMask(
                paths=[
                    "final_urls",
                    "responsive_search_ad.headlines",
                    "responsive_search_ad.descriptions",
                    "responsive_search_ad.path1",
                    "responsive_search_ad.path2",
                ]
            )
        )
        ops.append(op)
    return ops


def mutate_ads(client, customer: str, jobs: list[dict], *, validate_only: bool):
    if not jobs:
        return {}, None
    ops = build_ad_update_ops(client, customer, jobs)
    req = client.get_type("MutateAdsRequest")
    req.customer_id = customer
    req.operations.extend(ops)
    req.partial_failure = True
    req.validate_only = validate_only
    try:
        resp = client.get_service("AdService").mutate_ads(request=req)
    except GoogleAdsException as exc:
        if _quota(exc):
            raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
        raise RuntimeError(f"Ad mutate failed ({customer}): {_api_error_text(exc)}") from exc
    pf = getattr(resp, "partial_failure_error", None)
    err_idx = _parse_partial_failures(pf)
    by_ag: dict[str, str | None] = {}
    for i, job in enumerate(jobs):
        by_ag[job["ad_group"]] = err_idx.get(i)
    return by_ag, (pf.message if pf and getattr(pf, "code", 0) else None)


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


def write_audit(payload: dict) -> None:
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


def main() -> int:
    jobs = load_jobs()
    validate_jobs(jobs)
    us_n = sum(1 for j in jobs if j["market"] == "US")
    au_n = sum(1 for j in jobs if j["market"] == "AU")
    print(f"Jobs: {len(jobs)} · US {us_n} · AU {au_n}")

    settings = load_settings()
    print(f"Access level: {settings.access_level} · MCC login set")
    if settings.access_level != "basic":
        print(f"NOTE: expected basic, got {settings.access_level}")

    client = build_client(settings)
    ga = client.get_service("GoogleAdsService")
    api_calls = 0
    mutate_items = 0
    errors: list[str] = []

    # 1. Snapshot
    snaps: dict[str, dict[str, dict]] = {}
    for market, customer in (("US", US), ("AU", AU)):
        print(f"API {api_calls + 1} · snapshot {market} {customer}")
        api_calls += 1
        try:
            snaps[market] = pull_snapshot(ga, market, customer)
        except GoogleAdsException as exc:
            if _quota(exc):
                raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
            raise
        print(f"  {len(snaps[market])} ad groups")

    gated, skipped = gate_jobs(jobs, snaps)
    for s in skipped:
        print(f"  SKIP {s['skip']}")
    print(f"Gated: {len(gated)} will update · {len(skipped)} skipped")
    if not gated:
        write_audit(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "banner": "NO JOBS PASSED SNAPSHOT GATE",
                "api_calls": api_calls,
                "mutate_items": 0,
                "jobs": [],
                "skipped": [{"market": s["market"], "ad_group": s["ad_group"], "skip": s["skip"]} for s in skipped],
                "errors": errors,
            }
        )
        return 1

    results: dict[tuple[str, str], dict] = {}
    for job in gated:
        results[(job["market"], job["ad_group"])] = {
            "market": job["market"],
            "campaign": job["campaign"],
            "ad_group": job["ad_group"],
            "ag_id": job["ag_id"],
            "ad_id": job["ad_id"],
            "review_status": job["review_status"],
            "final_url": job["final_url"],
            "path1": job["path1"],
            "path2": job["path2"],
            "action": "update_paused",
            "copy_ok": False,
            "enabled": False,
            "left_paused": True,
            "ad_strength": None,
            "live_status": "PAUSED",
            "error": None,
            "note": None,
            "prior": job.get("prior"),
        }

    # 2. validate_only per account
    validated: list[dict] = []
    for market, customer in (("US", US), ("AU", AU)):
        batch = [j for j in gated if j["market"] == market]
        if not batch:
            continue
        print(f"API {api_calls + 1} · validate_only {market} ({len(batch)} ads)")
        api_calls += 1
        mutate_items += len(batch)
        by_ag, pf_msg = mutate_ads(client, customer, batch, validate_only=True)
        if pf_msg:
            errors.append(f"validate {market}: {pf_msg}")
            print(f"  PARTIAL validate {market}: {pf_msg}")
        for job in batch:
            err = by_ag.get(job["ad_group"])
            rec = results[(job["market"], job["ad_group"])]
            if err:
                rec["error"] = f"validate_only: {err}"
                rec["note"] = "Copy failed Google validate. Needs revise. Not posted."
                print(f"  FAIL validate {job['ad_group']:32} {err}")
            else:
                rec["copy_ok"] = True
                validated.append(job)
                print(f"  OK   validate {job['ad_group']:32} ad={job['ad_id']}")

    # 3. Real mutate (keep paused)
    posted: list[dict] = []
    for market, customer in (("US", US), ("AU", AU)):
        batch = [j for j in validated if j["market"] == market]
        if not batch:
            continue
        print(f"API {api_calls + 1} · mutate_ads {market} ({len(batch)} RSA copy updates, stay PAUSED)")
        api_calls += 1
        mutate_items += len(batch)
        by_ag, pf_msg = mutate_ads(client, customer, batch, validate_only=False)
        if pf_msg:
            errors.append(f"mutate {market}: {pf_msg}")
            print(f"  PARTIAL mutate {market}: {pf_msg}")
        for job in batch:
            err = by_ag.get(job["ad_group"])
            rec = results[(job["market"], job["ad_group"])]
            if err:
                rec["copy_ok"] = False
                rec["error"] = f"mutate: {err}"
                rec["note"] = "Validate passed; live mutate failed. Still old paused copy."
                print(f"  FAIL mutate {job['ad_group']:32} {err}")
            else:
                posted.append(job)
                rec["note"] = "Copy updated. Still PAUSED pending Ad Strength."
                print(f"  OK   mutate {job['ad_group']:32} ad={job['ad_id']}")

    # 4. Ad Strength
    print("Waiting 6s for Ad Strength…")
    time.sleep(6)
    after: dict[str, dict[str, dict]] = {}
    for market, customer in (("US", US), ("AU", AU)):
        print(f"API {api_calls + 1} · ad strength {market}")
        api_calls += 1
        try:
            after[market] = pull_snapshot(ga, market, customer)
        except GoogleAdsException as exc:
            if _quota(exc):
                raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
            raise

    pending = [
        j
        for j in posted
        if (after[j["market"]].get(j["ad_group"], {}).get("ads", {}).get(j["ad_id"], {}) or {}).get(
            "ad_strength"
        )
        in {None, "UNSPECIFIED", "UNKNOWN", "PENDING"}
    ]
    if pending:
        print(f"Waiting 10s for {len(pending)} PENDING Ad Strength…")
        time.sleep(10)
        for market in {j["market"] for j in pending}:
            print(f"API {api_calls + 1} · ad strength retry {market}")
            api_calls += 1
            try:
                after[market] = pull_snapshot(ga, market, customer=CUSTOMERS[market])
            except GoogleAdsException as exc:
                if _quota(exc):
                    raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
                raise

    to_enable: list[dict] = []
    for job in posted:
        live = after[job["market"]].get(job["ad_group"], {}).get("ads", {}).get(job["ad_id"], {})
        rec = results[(job["market"], job["ad_group"])]
        strength = live.get("ad_strength") or "UNKNOWN"
        rec["ad_strength"] = strength
        rec["live_status"] = live.get("status") or "PAUSED"
        rec["live_final_urls"] = live.get("final_urls")
        rec["live_path1"] = live.get("path1")
        rec["live_path2"] = live.get("path2")
        rec["live_headlines"] = live.get("headlines")
        if strength == "EXCELLENT":
            to_enable.append(job)
            rec["note"] = "Google Ad Strength Excellent — enabling."
            print(f"  EXCELLENT {job['market']} {job['ad_group']:32} → enable")
        else:
            rec["left_paused"] = True
            rec["note"] = f"Google Ad Strength {strength} — left PAUSED. Do not enable Average/Poor/Pending."
            print(f"  {strength:10} {job['market']} {job['ad_group']:32} left PAUSED")

    # 5. Enable Excellent only
    for market, customer in (("US", US), ("AU", AU)):
        batch = [j for j in to_enable if j["market"] == market]
        if not batch:
            continue
        print(f"API {api_calls + 1} · enable Excellent {market} ({len(batch)})")
        api_calls += 1
        mutate_items += len(batch)
        by_ag, pf_msg = mutate_enables(client, customer, batch)
        if pf_msg:
            errors.append(f"enable {market}: {pf_msg}")
            print(f"  PARTIAL enable {market}: {pf_msg}")
        for job in batch:
            err = by_ag.get(job["ad_group"])
            rec = results[(job["market"], job["ad_group"])]
            if err:
                rec["error"] = f"enable failed: {err}"
                rec["note"] = "Copy updated + Excellent, but enable failed. Still PAUSED."
                rec["left_paused"] = True
                print(f"  FAIL enable {job['ad_group']:32} {err}")
            else:
                rec["enabled"] = True
                rec["left_paused"] = False
                rec["live_status"] = "ENABLED"
                rec["note"] = "Posted and enabled (Google Ad Strength Excellent)."
                print(f"  OK   enable {job['ad_group']:32} ad={job['ad_id']}")

    # 6. Confirm
    confirm: dict[str, dict[str, dict]] = {}
    for market, customer in (("US", US), ("AU", AU)):
        print(f"API {api_calls + 1} · confirm {market}")
        api_calls += 1
        try:
            confirm[market] = pull_snapshot(ga, market, customer)
        except GoogleAdsException as exc:
            if _quota(exc):
                raise QuotaExhaustedError("Google Ads API quota exhausted. STOP — do not retry.") from exc
            raise

    for key, rec in results.items():
        market, ag = key
        live = confirm.get(market, {}).get(ag, {}).get("ads", {}).get(rec["ad_id"], {})
        if live:
            rec["live_status"] = live.get("status")
            rec["ad_strength"] = live.get("ad_strength") or rec.get("ad_strength")
            rec["live_final_urls"] = live.get("final_urls")
            rec["live_path1"] = live.get("path1")
            rec["live_path2"] = live.get("path2")
            rec["live_headlines"] = live.get("headlines")
            rec["resource_name"] = f"customers/{CUSTOMERS[market]}/adGroupAds/{rec['ag_id']}~{rec['ad_id']}"

    job_rows = list(results.values())
    skip_rows = [{"market": s["market"], "ad_group": s["ad_group"], "ad_id": s["ad_id"], "skip": s["skip"]} for s in skipped]
    posted_n = sum(1 for r in job_rows if r["copy_ok"] and not str(r.get("error") or "").startswith("mutate"))
    enabled_n = sum(1 for r in job_rows if r["enabled"])
    paused_n = sum(1 for r in job_rows if r["copy_ok"] and r["left_paused"] and not r["enabled"])
    fail_n = sum(1 for r in job_rows if r.get("error"))
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "banner": "POSTED via API — update_paused, enable only if Excellent",
        "authorized_by": "George 2026-08-14",
        "api_calls": api_calls,
        "mutate_items": mutate_items,
        "counts": {
            "jobs": len(job_rows),
            "skipped_gate": len(skip_rows),
            "copy_updated": posted_n,
            "enabled_excellent": enabled_n,
            "left_paused": paused_n,
            "failed": fail_n,
        },
        "jobs": job_rows,
        "skipped": skip_rows,
        "errors": errors,
        "brand_untouched": True,
        "winners_untouched": True,
        "landing_pages_untouched": True,
    }
    write_audit(payload)
    print(
        f"\nDone. posted={posted_n} enabled={enabled_n} left_paused={paused_n} "
        f"failed={fail_n} skipped={len(skip_rows)} api_calls={api_calls} mutate_items={mutate_items}"
    )
    return 1 if fail_n else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QuotaExhaustedError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
