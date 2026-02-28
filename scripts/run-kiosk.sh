#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://localhost:8080}"

if command -v chromium-browser >/dev/null 2>&1; then
  BROWSER_BIN="chromium-browser"
elif command -v chromium >/dev/null 2>&1; then
  BROWSER_BIN="chromium"
else
  echo "Chromium binary not found (tried chromium-browser and chromium)." >&2
  exit 1
fi

"$BROWSER_BIN" \
  --kiosk \
  --incognito \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --noerrdialogs \
  --disable-session-crashed-bubble \
  "$URL"
