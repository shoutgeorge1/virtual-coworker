#!/usr/bin/env python3
"""Optional refresh orchestrator for attribution dashboard inputs.

READ-ONLY. Respects Google Ads API caps. Does NOT mutate campaigns.

Default: compile only from on-disk snapshots (0 Ads API calls).

  python3 ads-launch/refresh_attribution_dashboard.py

With live pulls (requires credentials; uses existing capped pullers):

  python3 ads-launch/refresh_attribution_dashboard.py --pull

--pull runs, in order (each script has its own hard cap):
  1. pull_executive_snapshot.py   (≤2 Ads)
  2. pull_impression_share.py     (≤3 Ads)
  3. pull_daily_watch.py          (≤4 Ads)
  4. pull_ga4_executive.py        (GA4 only — not Ads quota)
  5. compile_attribution_dashboard.py

Zoho is NOT auto-pulled (quota + PII). Re-run probe scripts separately when needed,
then recompile.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ADS = REPO / "ads-launch"


def run(script: str) -> None:
    path = ADS / script
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, str(path)], check=True, cwd=str(REPO))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--pull",
        action="store_true",
        help="Run capped Ads/GA4 pullers before compile (read-only)",
    )
    args = ap.parse_args()
    if args.pull:
        run("pull_executive_snapshot.py")
        run("pull_impression_share.py")
        run("pull_daily_watch.py")
        run("pull_ga4_executive.py")
    run("compile_attribution_dashboard.py")
    print("\nDone. Deploy xray if you want it live: cd xray && npm run deploy")


if __name__ == "__main__":
    main()
