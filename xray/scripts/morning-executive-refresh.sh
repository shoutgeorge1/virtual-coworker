#!/bin/zsh
# Morning Executive refresh: Master orchestrator (Ads pull ≤2 calls, Zoho read-only census, sales validation, atomic snapshot update, bake, deploy, smoke).
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

"$PY" "$REPO/ads-launch/refresh_executive_dashboard.py" --deploy

echo "=== done $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
