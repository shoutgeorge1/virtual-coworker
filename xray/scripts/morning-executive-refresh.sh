#!/bin/zsh
# Morning Executive refresh: Ads (≤2) + Zoho read-only + sales labels + GA4 + bake + deploy.
# HARD: never deploy without September/month tabs (renderMonthTabs).
set -euo pipefail

REPO="/Users/george/Developer/virtual-coworker"
XRAY="$REPO/xray"
PY="/Users/george/Developer/shoutgeorge-ads/.venv/bin/python"
if [ ! -f "$PY" ]; then
  PY="python3"
fi
LOG_DIR="$XRAY/.serve-logs"
mkdir -p "$LOG_DIR"

exec >>"$LOG_DIR/morning-executive-refresh.log" 2>&1
echo "=== $(date -u '+%Y-%m-%dT%H:%M:%SZ') morning executive refresh ==="

guard_month_tabs() {
  local js="$XRAY/executive.js"
  local html="$XRAY/executive.html"
  if ! grep -q 'renderMonthTabs' "$js"; then
    echo "REFUSE DEPLOY: $js missing renderMonthTabs (would wipe September tab)"
    return 1
  fi
  if ! grep -q 'ex-month-tabs' "$html"; then
    echo "REFUSE DEPLOY: $html missing ex-month-tabs"
    return 1
  fi
  echo "month-tabs guard OK"
}

# Refresh open-month GA4 through previous complete day (independent of Ads OAuth).
if ! "$PY" "$REPO/ads-launch/pull_ga4_executive.py" --skip-experiments; then
  echo "WARNING: GA4 pull failed — continuing with last good GA4 snapshot"
fi

guard_month_tabs

"$PY" "$REPO/ads-launch/refresh_executive_dashboard.py" --deploy

guard_month_tabs
# Post-deploy: live must still have tabs (catches stale uploads).
if command -v curl >/dev/null 2>&1; then
  live_js="$(curl -fsS 'https://vc-xray.vercel.app/executive.js' || true)"
  if [[ -n "$live_js" ]] && ! print -r -- "$live_js" | grep -q 'renderMonthTabs'; then
    echo "ALERT: live executive.js missing renderMonthTabs after deploy"
    exit 1
  fi
fi

echo "=== done $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
