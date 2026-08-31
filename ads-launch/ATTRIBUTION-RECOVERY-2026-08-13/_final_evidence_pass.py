#!/usr/bin/env python3
"""Final evidence pass — 13 Aug 2026. READ-ONLY.

Hard:
- No Ads mutate / upload / enable
- No Zoho writes
- STOP on Ads RESOURCE_EXHAUSTED
- ≤12 Google Ads queries, ≤20 Zoho CRM requests
- No retry loops after schema failures
- Never print tokens, emails, phones, full GCLIDs, or full CRM ids
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
sys.path.insert(0, str(SG_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "zoho"))

from dotenv import load_dotenv  # noqa: E402

from sg_google_ads.client import build_client, run_gaql  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import (  # noqa: E402
    ApiAccessError,
    QuotaExhaustedError,
    SgGoogleAdsError,
)
from _common import (  # noqa: E402
    crm_url,
    ensure_local_dir,
    http_get_json,
    load_credentials,
    refresh_access_token,
    write_json,
)

US_ID = "4967151855"
AU_ID = "5735391940"
WINDOW_START = "2024-08-01"
WINDOW_END = "2026-08-12"
ADS_MAX = 12
ZOHO_MAX = 20
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / ".local" / "attribution-final-evidence-2026-08-13.json"
VC_ENV = SG_ROOT / "clients" / "virtual-coworker.env"
ENV_PATH = REPO / ".env"

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)


def _enum(val: Any) -> str:
    if val is None:
        return ""
    if hasattr(val, "name"):
        return str(val.name)
    return str(val).strip()


def _num(val: Any) -> float:
    try:
        return float(val or 0)
    except (TypeError, ValueError):
        return 0.0


def _money(micros: Any) -> float:
    try:
        return round(float(micros) / 1_000_000.0, 2)
    except (TypeError, ValueError):
        return 0.0


def gclid_hash(val: Any) -> str | None:
    s = str(val or "").strip()
    if not s or s.lower() in {"none", "null"}:
        return None
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def lookup_id(obj: Any) -> str | None:
    if isinstance(obj, dict):
        i = str(obj.get("id") or "").strip()
        return i or None
    return None


def lookup_name(obj: Any) -> str:
    if isinstance(obj, dict):
        return str(obj.get("name") or "")
    return str(obj or "")


def redact_email(s: Any) -> Any:
    if isinstance(s, str):
        return EMAIL_RE.sub("[email]", s)
    if isinstance(s, dict):
        return {k: redact_email(v) for k, v in s.items()}
    if isinstance(s, list):
        return [redact_email(x) for x in s]
    return s


class AdsBudget:
    def __init__(self) -> None:
        self.n = 0
        self.log: list[dict[str, Any]] = []
        self.hard_stop: str | None = None

    def run(self, client: Any, customer_id: str, name: str, query: str) -> list[Any]:
        if self.hard_stop:
            self.log.append({"n": self.n + 1, "name": name, "ok": False, "skipped": self.hard_stop})
            return []
        if self.n >= ADS_MAX:
            self.log.append({"n": self.n + 1, "name": name, "ok": False, "skipped": "ads_cap"})
            return []
        self.n += 1
        entry: dict[str, Any] = {"n": self.n, "name": name, "ok": False}
        try:
            rows = list(run_gaql(client, customer_id, query))
            entry["ok"] = True
            entry["row_count"] = len(rows)
            self.log.append(entry)
            return rows
        except QuotaExhaustedError as exc:
            entry["error"] = "RESOURCE_EXHAUSTED"
            self.log.append(entry)
            self.hard_stop = str(exc)
            return []
        except ApiAccessError as exc:
            entry["error"] = str(exc)[:400]
            self.log.append(entry)
            return []
        except Exception as exc:  # noqa: BLE001
            text = str(exc)
            if "RESOURCE_EXHAUSTED" in text.upper():
                entry["error"] = "RESOURCE_EXHAUSTED"
                self.hard_stop = text[:400]
            else:
                entry["error"] = text[:400]
            self.log.append(entry)
            return []


class ZohoBudget:
    def __init__(self) -> None:
        self.n = 0
        self.log: list[dict[str, Any]] = []
        self.stopped: str | None = None

    def _count(self, name: str) -> bool:
        if self.stopped:
            self.log.append({"n": self.n + 1, "name": name, "ok": False, "skipped": self.stopped})
            return False
        if self.n >= ZOHO_MAX:
            self.log.append({"n": self.n + 1, "name": name, "ok": False, "skipped": "zoho_cap"})
            return False
        self.n += 1
        return True

    def get(self, name: str, url: str, token: str) -> tuple[int, Any]:
        if not self._count(name):
            return 0, {"error": "skipped"}
        st, body = http_get_json(url, access_token=token)
        ok = st == 200
        err = None
        if not ok:
            err = f"HTTP {st}"
            if st in (429, 403):
                self.stopped = f"rate {st}"
        self.log.append({"n": self.n, "name": name, "ok": ok, "http": st, "error": err})
        return st, body

    def coql(self, name: str, url: str, token: str, sql: str) -> tuple[int, Any]:
        if not self._count(name):
            return 0, {"error": "skipped"}
        payload = json.dumps({"select_query": sql}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Zoho-oauthtoken {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                raw = res.read().decode("utf-8", errors="replace")
                st = res.getcode() or 200
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="replace")
            st = e.code
            if st in (429, 403):
                self.stopped = f"rate {st}"
        except urllib.error.URLError as e:
            self.log.append({"n": self.n, "name": name, "ok": False, "error": str(e.reason)[:300]})
            return 0, {"error": str(e.reason)}
        try:
            body: Any = json.loads(raw)
        except json.JSONDecodeError:
            body = {"raw": raw[:200]}
        ok = st == 200
        self.log.append({"n": self.n, "name": name, "ok": ok, "http": st, "error": None if ok else f"HTTP {st}"})
        return st, body


def parse_conversion_actions(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
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
                "primary_for_goal": bool(getattr(ca, "primary_for_goal", False)),
                "include_in_conversions_metric": bool(
                    getattr(ca, "include_in_conversions_metric", False)
                ),
                "counting_type": _enum(ca.counting_type),
                "default_value": _num(getattr(vs, "default_value", 0) if vs else 0),
            }
        )
    out.sort(key=lambda r: r["name"].lower())
    return out


def parse_goal_config(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        c = row.campaign
        cfg = row.conversion_goal_campaign_config
        out.append(
            {
                "campaign_id": str(c.id),
                "campaign_name": c.name,
                "status": _enum(c.status),
                "bidding": _enum(c.bidding_strategy_type),
                "goal_config_level": _enum(getattr(cfg, "goal_config_level", None)),
                "custom_conversion_goal": str(
                    getattr(cfg, "custom_conversion_goal", "") or ""
                ),
            }
        )
    return out


def parse_campaign_conv_goals(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        c = row.campaign
        g = row.campaign_conversion_goal
        out.append(
            {
                "campaign_id": str(c.id),
                "campaign_name": c.name,
                "category": _enum(g.category),
                "origin": _enum(g.origin),
                "biddable": bool(getattr(g, "biddable", False)),
            }
        )
    return out


def parse_custom_goals(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        g = row.custom_conversion_goal
        actions = []
        raw_actions = getattr(g, "conversion_actions", None) or []
        for a in raw_actions:
            actions.append(str(a))
        out.append(
            {
                "id": str(getattr(g, "id", "") or ""),
                "name": g.name,
                "status": _enum(g.status),
                "conversion_action_count": len(actions),
                "conversion_actions": actions,
            }
        )
    return out


def parse_monthly_actions(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "month": str(row.segments.month),
                "action": str(row.segments.conversion_action_name),
                "conversions": round(_num(row.metrics.conversions), 2),
                "all_conversions": round(_num(row.metrics.all_conversions), 2),
            }
        )
    out.sort(key=lambda r: (r["month"], -r["all_conversions"]))
    return out


def parse_change_event(rows: list[Any]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        ev = row.change_event
        fields: list[str] = []
        raw_fields = getattr(ev, "changed_fields", None)
        paths = getattr(raw_fields, "paths", None) if raw_fields is not None else None
        if paths:
            fields = [str(p) for p in list(paths)[:20]]
        elif raw_fields is not None:
            fields = [str(raw_fields)[:200]]
        out.append(
            {
                "when": str(getattr(ev, "change_date_time", "") or ""),
                "resource_type": _enum(getattr(ev, "change_resource_type", None)),
                "operation": _enum(getattr(ev, "resource_change_operation", None)),
                "client_type": _enum(getattr(ev, "client_type", None)),
                "changed_fields": fields[:20],
                "resource_name": str(getattr(ev, "change_resource_name", "") or "")[:80],
            }
        )
    return out


def ads_account(client: Any, budget: AdsBudget, market: str, customer_id: str) -> dict[str, Any]:
    block: dict[str, Any] = {"market": market, "customer_id": customer_id}

    rows = budget.run(
        client,
        customer_id,
        f"{market.lower()}_goal_config_vc",
        f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.bidding_strategy_type,
          conversion_goal_campaign_config.goal_config_level,
          conversion_goal_campaign_config.custom_conversion_goal
        FROM conversion_goal_campaign_config
        WHERE campaign.name LIKE 'VC_%'
        """,
    )
    block["goal_config"] = parse_goal_config(rows) if rows else []
    if not rows and budget.log and not budget.log[-1].get("ok"):
        block["goal_config_status"] = "UNKNOWN_schema_or_empty"

    if budget.hard_stop:
        return block

    rows = budget.run(
        client,
        customer_id,
        f"{market.lower()}_campaign_conversion_goal_vc",
        f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign_conversion_goal.category,
          campaign_conversion_goal.origin,
          campaign_conversion_goal.biddable
        FROM campaign_conversion_goal
        WHERE campaign.name LIKE 'VC_%'
        """,
    )
    block["campaign_conversion_goals"] = parse_campaign_conv_goals(rows) if rows else []

    if budget.hard_stop:
        return block

    rows = budget.run(
        client,
        customer_id,
        f"{market.lower()}_conversion_actions",
        """
        SELECT
          conversion_action.id,
          conversion_action.name,
          conversion_action.status,
          conversion_action.type,
          conversion_action.category,
          conversion_action.primary_for_goal,
          conversion_action.counting_type,
          conversion_action.include_in_conversions_metric,
          conversion_action.value_settings.default_value
        FROM conversion_action
        WHERE conversion_action.status != 'REMOVED'
        """,
    )
    block["conversion_actions"] = parse_conversion_actions(rows) if rows else []

    if budget.hard_stop:
        return block

    rows = budget.run(
        client,
        customer_id,
        f"{market.lower()}_monthly_conversion_actions",
        f"""
        SELECT
          segments.month,
          segments.conversion_action_name,
          metrics.conversions,
          metrics.all_conversions
        FROM customer
        WHERE segments.date BETWEEN '{WINDOW_START}' AND '{WINDOW_END}'
        """,
    )
    block["monthly_conversion_actions"] = parse_monthly_actions(rows) if rows else []

    return block


def maybe_change_history(client: Any, budget: AdsBudget, market: str, customer_id: str) -> list[dict[str, Any]]:
    if budget.hard_stop or budget.n >= ADS_MAX:
        return []
    rows = budget.run(
        client,
        customer_id,
        f"{market.lower()}_change_event_14d",
        """
        SELECT
          change_event.change_date_time,
          change_event.change_resource_type,
          change_event.change_resource_name,
          change_event.client_type,
          change_event.resource_change_operation,
          change_event.changed_fields
        FROM change_event
        WHERE change_event.change_date_time DURING LAST_14_DAYS
        LIMIT 100
        """,
    )
    return parse_change_event(rows) if rows else []


def maybe_custom_goals(client: Any, budget: AdsBudget, market: str, customer_id: str) -> list[dict[str, Any]]:
    if budget.hard_stop or budget.n >= ADS_MAX:
        return []
    rows = budget.run(
        client,
        customer_id,
        f"{market.lower()}_custom_conversion_goal",
        """
        SELECT
          custom_conversion_goal.id,
          custom_conversion_goal.name,
          custom_conversion_goal.status,
          custom_conversion_goal.conversion_actions
        FROM custom_conversion_goal
        """,
    )
    return parse_custom_goals(rows) if rows else []


def zoho_rows(body: Any) -> list[dict[str, Any]]:
    if isinstance(body, dict) and isinstance(body.get("data"), list):
        return [r for r in body["data"] if isinstance(r, dict)]
    return []


def run_zoho(zb: ZohoBudget) -> dict[str, Any]:
    load_dotenv(ENV_PATH, override=False)
    creds = load_credentials()
    token_data = refresh_access_token(creds)
    token = str(token_data["access_token"])
    api = creds.get("api_domain") or "https://www.zohoapis.com"
    coql_url = crm_url(api, "/coql")

    out: dict[str, Any] = {"note": "hashes only; no emails/phones/full gclids/full record ids in summaries"}

    st, body = zb.coql(
        "jo_gclid_all",
        coql_url,
        token,
        "select id, Created_Time, Region, Stage, Client_Name, UTM_Gclid, UTM_Source, UTM_Campaign from Job_Orders where UTM_Gclid is not null order by Created_Time desc limit 50",
    )
    jo_gclid_rows = zoho_rows(body) if st == 200 else []
    enquiry_ids: list[str] = []
    jo_summaries = []
    for rec in jo_gclid_rows:
        eid = lookup_id(rec.get("Client_Name"))
        if eid:
            enquiry_ids.append(eid)
        created = str(rec.get("Created_Time") or "")[:7]
        jo_summaries.append(
            {
                "month": created,
                "region": rec.get("Region") or "",
                "stage": rec.get("Stage") or "",
                "utm_source": rec.get("UTM_Source") or "",
                "has_enquiry_lookup": bool(eid),
                "jo_gclid_hash": gclid_hash(rec.get("UTM_Gclid")),
                "enquiry_id_hash": hashlib.sha256(eid.encode()).hexdigest()[:12] if eid else None,
            }
        )
    out["jo_with_direct_gclid"] = {
        "n": len(jo_summaries),
        "http": st,
        "rows": jo_summaries,
    }

    lead_by_id: dict[str, dict[str, Any]] = {}
    if enquiry_ids:
        # COQL IN typically accepts up to 100 ids. We have ≤18.
        id_list = ",".join(f"'{i}'" for i in enquiry_ids[:50])
        st, body = zb.coql(
            "leads_for_gclid_jos",
            coql_url,
            token,
            f"select id, utm_gclid, Region, Lead_Status, Created_Time, utm_source from Leads where id in ({id_list})",
        )
        for rec in zoho_rows(body) if st == 200 else []:
            i = str(rec.get("id") or "")
            if i:
                lead_by_id[i] = rec

    same = inherited_copy = jo_only = lead_only_on_linked = different = 0
    unique_jo = set()
    unique_lead = set()
    unique_effective = set()
    for rec in jo_gclid_rows:
        eid = lookup_id(rec.get("Client_Name"))
        jh = gclid_hash(rec.get("UTM_Gclid"))
        lh = gclid_hash(lead_by_id.get(eid or "", {}).get("utm_gclid")) if eid else None
        if jh:
            unique_jo.add(jh)
            unique_effective.add(jh)
        if lh:
            unique_lead.add(lh)
            unique_effective.add(lh)
        if jh and lh and jh == lh:
            same += 1
            inherited_copy += 1  # stored on both; cannot prove copy vs dual-write
        elif jh and not lh:
            jo_only += 1
        elif (not jh) and lh:
            lead_only_on_linked += 1
        elif jh and lh and jh != lh:
            different += 1
    out["direct_vs_inherited_on_gclid_jos"] = {
        "joined_enquiries_found": len(lead_by_id),
        "same_hash_on_jo_and_enquiry": same,
        "jo_gclid_enquiry_empty": jo_only,
        "enquiry_gclid_jo_empty": lead_only_on_linked,
        "different_hashes": different,
        "unique_jo_gclid_hashes": len(unique_jo),
        "unique_enquiry_gclid_hashes": len(unique_lead),
        "unique_effective_hashes": len(unique_effective),
        "verdict": (
            "same hash on both objects is consistent with copy/inheritance but does not prove "
            "a live formula; different hashes mean independent stamps"
        ),
    }

    # 90d JOs: detect inherited GCLID (enquiry has it, JO does not)
    st, body = zb.coql(
        "jo_90d_lookup_gclid",
        coql_url,
        token,
        "select id, Created_Time, Region, Stage, Client_Name, UTM_Gclid from Job_Orders where Created_Time >= '2026-05-15T00:00:00+00:00' order by Created_Time desc limit 200",
    )
    jo90 = zoho_rows(body) if st == 200 else []
    eids90: list[str] = []
    jo90_meta = []
    for rec in jo90:
        eid = lookup_id(rec.get("Client_Name"))
        if eid:
            eids90.append(eid)
        jo90_meta.append(
            {
                "eid": eid,
                "month": str(rec.get("Created_Time") or "")[:7],
                "region": rec.get("Region") or "",
                "stage": rec.get("Stage") or "",
                "jo_hash": gclid_hash(rec.get("UTM_Gclid")),
            }
        )
    out["jo_90d_sample"] = {
        "n": len(jo90),
        "http": st,
        "with_enquiry_lookup": sum(1 for r in jo90_meta if r["eid"]),
        "with_direct_gclid": sum(1 for r in jo90_meta if r["jo_hash"]),
    }

    lead90: dict[str, str | None] = {}
    unique_eids = list(dict.fromkeys([e for e in eids90 if e]))
    for i in range(0, len(unique_eids), 50):
        chunk = unique_eids[i : i + 50]
        id_list = ",".join(f"'{x}'" for x in chunk)
        st, body = zb.coql(
            f"leads_utm_gclid_chunk_{i // 50 + 1}",
            coql_url,
            token,
            f"select id, utm_gclid from Leads where id in ({id_list})",
        )
        for rec in zoho_rows(body) if st == 200 else []:
            lead90[str(rec.get("id") or "")] = gclid_hash(rec.get("utm_gclid"))

    inherited = 0
    direct = 0
    both = 0
    neither = 0
    effective_hashes = set()
    region_eff: Counter[str] = Counter()
    stage_eff: Counter[str] = Counter()
    month_eff: Counter[str] = Counter()
    cancelled_eff = 0
    placement_eff = 0
    for rec in jo90_meta:
        jh = rec["jo_hash"]
        lh = lead90.get(rec["eid"] or "") if rec["eid"] else None
        eff = jh or lh
        if jh and lh:
            both += 1
        elif jh:
            direct += 1
        elif lh:
            inherited += 1
        else:
            neither += 1
        if eff:
            effective_hashes.add(eff)
            region_eff[str(rec["region"] or "(blank)")] += 1
            stage_eff[str(rec["stage"] or "(blank)")] += 1
            month_eff[str(rec["month"] or "(blank)")] += 1
            stg = str(rec["stage"] or "").lower()
            if "cancel" in stg:
                cancelled_eff += 1
            if stg == "placement":
                placement_eff += 1

    out["click_linked_90d_jos"] = {
        "denominator_note": "click-linked = JO.UTM_Gclid OR linked enquiry utm_gclid; NOT all 782 JOs",
        "jo_rows_in_query": len(jo90_meta),
        "enquiries_resolved": len(lead90),
        "direct_jo_only": direct,
        "inherited_enquiry_only": inherited,
        "both_objects": both,
        "neither": neither,
        "click_linked_n": direct + inherited + both,
        "unique_effective_gclid_hashes": len(effective_hashes),
        "region": dict(region_eff),
        "stage": dict(stage_eff),
        "month": dict(month_eff),
        "cancelled_among_click_linked": cancelled_eff,
        "placement_stage_among_click_linked": placement_eff,
    }

    st, body = zb.get(
        "related_lists_job_orders",
        crm_url(api, "/settings/related_lists?module=Job_Orders"),
        token,
    )
    rel_jo = []
    if st == 200 and isinstance(body, dict):
        for r in body.get("related_lists") or []:
            if not isinstance(r, dict):
                continue
            rel_jo.append(
                {
                    "api_name": r.get("api_name"),
                    "display_label": r.get("display_label"),
                    "module": (r.get("module") or {}).get("api_name")
                    if isinstance(r.get("module"), dict)
                    else r.get("module"),
                    "href": r.get("href"),
                }
            )
    out["related_lists_job_orders"] = rel_jo
    placement_rel = [
        r
        for r in rel_jo
        if "deal" in str(r).lower() or "placement" in str(r).lower()
    ]
    out["placements_relationship"] = {
        "deals_module_job_order_lookup": False,
        "related_list_to_deals_or_placements": placement_rel,
        "verdict": "UNKNOWN"
        if not placement_rel
        else "related_list_present_not_proven_populated",
    }

    if placement_rel and jo_gclid_rows:
        # One related-records GET on a Placement-stage JO if any; else first JO.
        target = None
        for rec in jo_gclid_rows:
            if str(rec.get("Stage") or "") == "Placement":
                target = rec
                break
        target = target or jo_gclid_rows[0]
        tid = str(target.get("id") or "")
        api_name = placement_rel[0].get("api_name") or "Deals"
        if tid and api_name:
            st, body = zb.get(
                "related_records_one_jo",
                crm_url(api, f"/Job_Orders/{tid}/{api_name}?fields=Stage,Region"),
                token,
            )
            n_rel = len(zoho_rows(body)) if st == 200 else None
            out["placements_relationship"]["one_jo_related_http"] = st
            out["placements_relationship"]["one_jo_related_n"] = n_rel
            if st == 200:
                out["placements_relationship"]["verdict"] = (
                    "explicit_related_list" if n_rel else "related_list_empty_on_sample"
                )
            else:
                out["placements_relationship"]["verdict"] = "UNKNOWN"

    return out


def main() -> int:
    load_dotenv(SG_ROOT / ".env", override=False)
    if VC_ENV.is_file():
        load_dotenv(VC_ENV, override=True)

    started = datetime.now(timezone.utc).isoformat()
    ads_budget = AdsBudget()
    payload: dict[str, Any] = {
        "generated_at_utc": started,
        "read_only": True,
        "window": f"{WINDOW_START} to {WINDOW_END}",
        "ads_max": ADS_MAX,
        "zoho_max": ZOHO_MAX,
    }

    try:
        settings = load_settings(env_file=SG_ROOT / ".env")
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        payload["ads_client_error"] = str(exc)
        client = None

    # Pass 1 already spent 9 Ads queries (US+AU goals/actions/monthly + US change_event)
    # then crashed while parsing change_event. Do NOT replay those queries.
    # Remaining budget: 3. Use them for campaign goal config + VC conversion-goal rows.
    prior_spent = int(os.environ.get("ADS_PRIOR_SPENT", "9"))
    ads_budget.n = prior_spent
    ads_budget.log.append(
        {
            "n": 0,
            "name": "prior_pass1_unwritten",
            "ok": False,
            "error": (
                "Pass 1 used 9 queries (US/AU goal_config, campaign_conversion_goal, "
                "conversion_actions, monthly + US change_event) then crashed on FieldMask parse. "
                "Results were not written. Those 9 count against the ceiling. This process "
                "does not replay them."
            ),
        }
    )
    if client is not None:
        us: dict[str, Any] = {"market": "US", "customer_id": US_ID, "replay": False}
        au: dict[str, Any] = {"market": "AU", "customer_id": AU_ID, "replay": False}
        rows = ads_budget.run(
            client,
            US_ID,
            "us_goal_config_vc_pass2",
            """
            SELECT
              campaign.id,
              campaign.name,
              campaign.status,
              campaign.bidding_strategy_type,
              conversion_goal_campaign_config.goal_config_level,
              conversion_goal_campaign_config.custom_conversion_goal
            FROM conversion_goal_campaign_config
            WHERE campaign.name LIKE 'VC_%'
            """,
        )
        us["goal_config"] = parse_goal_config(rows) if rows else []
        rows = ads_budget.run(
            client,
            AU_ID,
            "au_goal_config_vc_pass2",
            """
            SELECT
              campaign.id,
              campaign.name,
              campaign.status,
              campaign.bidding_strategy_type,
              conversion_goal_campaign_config.goal_config_level,
              conversion_goal_campaign_config.custom_conversion_goal
            FROM conversion_goal_campaign_config
            WHERE campaign.name LIKE 'VC_%'
            """,
        )
        au["goal_config"] = parse_goal_config(rows) if rows else []
        rows = ads_budget.run(
            client,
            US_ID,
            "us_campaign_conversion_goal_vc_pass2",
            """
            SELECT
              campaign.id,
              campaign.name,
              campaign_conversion_goal.category,
              campaign_conversion_goal.origin,
              campaign_conversion_goal.biddable
            FROM campaign_conversion_goal
            WHERE campaign.name LIKE 'VC_%'
            """,
        )
        us["campaign_conversion_goals"] = parse_campaign_conv_goals(rows) if rows else []
        us["change_event_14d"] = []
        us["change_event_14d_status"] = (
            "UNKNOWN — pass1 fetched LAST_14_DAYS then parse crashed; not retried"
        )
        au["change_event_14d"] = []
        au["campaign_conversion_goals"] = []
        au["campaign_conversion_goals_status"] = "UNKNOWN — ads budget exhausted after pass2"
        payload["us"] = us
        payload["au"] = au
        payload["ads_monthly_status"] = (
            "UNKNOWN this pass (fetched in pass1, unwritten, not replayed). "
            "Use morning 2-year action totals on disk, not a monthly mix."
        )
        payload["ads_conversion_action_refresh_status"] = (
            "Not replayed. Morning inventory in xray/data/recovery-ads-raw.json "
            "(generated 2026-08-13T16:03Z) is the conversion-action snapshot."
        )

    payload["ads_calls_used"] = ads_budget.n
    payload["ads_call_log"] = ads_budget.log
    payload["ads_hard_stop"] = ads_budget.hard_stop

    zb = ZohoBudget()
    try:
        payload["zoho"] = run_zoho(zb)
    except SystemExit as exc:
        payload["zoho_error"] = str(exc)
        payload["zoho"] = {}
    payload["zoho_calls_used"] = zb.n
    payload["zoho_call_log"] = zb.log
    payload["zoho_stopped"] = zb.stopped
    payload["generated_finished_utc"] = datetime.now(timezone.utc).isoformat()

    ensure_local_dir()
    write_json(OUT, payload)
    print(
        json.dumps(
            {
                "wrote": str(OUT),
                "ads_calls": ads_budget.n,
                "ads_hard_stop": ads_budget.hard_stop,
                "ads_log": [
                    {k: v for k, v in e.items() if k != "error" or not e.get("ok")}
                    for e in ads_budget.log
                ],
                "zoho_calls": zb.n,
                "zoho_stopped": zb.stopped,
            },
            indent=2,
        )
    )
    return 0 if ads_budget.hard_stop is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
