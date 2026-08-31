#!/usr/bin/env python3
"""Resume remaining forensic Ads reads. Keeps US conversion_actions already pulled.

Does not re-run US conversion_actions. Stops on quota/token errors.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SG_ROOT = Path("/Users/george/Developer/shoutgeorge-ads")
sys.path.insert(0, str(SG_ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

REPO = Path("/Users/george/Developer/virtual-coworker")
sys.path.insert(0, str(REPO / "ads-launch"))

from pull_forensic_recovery import (  # noqa: E402
    AU_ID,
    CAMPAIGNS_Q,
    CONV_ACTIONS_Q,
    CONV_METRICS_Q,
    LANDING_Q,
    OUT,
    US_ID,
    VC_ENV,
    parse_campaigns,
    parse_conversion_actions,
    parse_conv_metrics,
    parse_landings,
    run_call,
)
from sg_google_ads.client import build_client  # noqa: E402
from sg_google_ads.config import load_settings  # noqa: E402
from sg_google_ads.exceptions import SgGoogleAdsError  # noqa: E402


def main() -> int:
    load_dotenv(SG_ROOT / ".env", override=False)
    if VC_ENV.is_file():
        load_dotenv(VC_ENV, override=True)

    prior = json.loads(OUT.read_text(encoding="utf-8"))
    us = dict(prior.get("us") or {})
    au = dict(prior.get("au") or {}) if prior.get("au") else {"market": "AU", "customer_id": AU_ID}
    api_calls = list(prior.get("api_calls") or [])
    n = max((c.get("n") or 0) for c in api_calls) + 1 if api_calls else 1
    started = datetime.now(timezone.utc).isoformat()

    try:
        settings = load_settings(env_file=SG_ROOT / ".env")
        client = build_client(settings, include_login_customer_id=True)
    except SgGoogleAdsError as exc:
        print(f"client fail: {exc}", file=sys.stderr)
        return 1

    plan = [
        (US_ID, "us_campaigns", CAMPAIGNS_Q, "campaigns", parse_campaigns, us),
        (US_ID, "us_conversion_metrics", CONV_METRICS_Q, "conversion_metrics", parse_conv_metrics, us),
        (US_ID, "us_landing_pages", LANDING_Q, "landing_pages", parse_landings, us),
        (AU_ID, "au_conversion_actions", CONV_ACTIONS_Q, "conversion_actions", parse_conversion_actions, au),
        (AU_ID, "au_campaigns", CAMPAIGNS_Q, "campaigns", parse_campaigns, au),
        (AU_ID, "au_conversion_metrics", CONV_METRICS_Q, "conversion_metrics", parse_conv_metrics, au),
        (AU_ID, "au_landing_pages", LANDING_Q, "landing_pages", parse_landings, au),
    ]

    hard_stop = None
    for customer_id, name, query, key, parser, block in plan:
        rows = run_call(
            client, n=n, name=name, customer_id=customer_id, query=query, api_calls=api_calls
        )
        last = api_calls[-1]
        if last.get("stop"):
            hard_stop = last.get("error")
            break
        if rows is not None:
            block[key] = parser(rows)
        else:
            block[f"{key}_error"] = last.get("error")
        n += 1

    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "pull_started_utc": started,
        "prior_pull_started_utc": prior.get("pull_started_utc"),
        "read_only": True,
        "window": prior.get("window"),
        "customer_ids": {"us": US_ID, "au": AU_ID},
        "api_calls_used": len(api_calls),
        "api_calls": api_calls,
        "hard_stop": hard_stop,
        "us": us,
        "au": au,
        "honesty": prior.get("honesty"),
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(api_calls)} total recorded calls)")
    return 0 if hard_stop is None else 2


if __name__ == "__main__":
    raise SystemExit(main())
