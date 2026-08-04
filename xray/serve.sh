#!/bin/zsh
# Durable static server for VC X-Ray dashboard on port 8766.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PORT=8766

# Free the port if something else (or a stale server) holds it.
if command -v lsof >/dev/null 2>&1; then
  pids="$(lsof -ti tcp:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "Killing old listener(s) on ${PORT}: ${pids}"
    # shellcheck disable=SC2086
    kill ${pids} 2>/dev/null || true
    sleep 0.3
    pids="$(lsof -ti tcp:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
    if [[ -n "${pids}" ]]; then
      # shellcheck disable=SC2086
      kill -9 ${pids} 2>/dev/null || true
    fi
  fi
fi

cd "$ROOT"
exec /usr/bin/python3 -m http.server "$PORT" --bind 127.0.0.1
