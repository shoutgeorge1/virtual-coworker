#!/usr/bin/env bash
# Morning executive snapshot refresh runner
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"
echo "Running Virtual Coworker Executive Refresh Orchestrator..."
python3 ads-launch/refresh_executive_dashboard.py "$@"
