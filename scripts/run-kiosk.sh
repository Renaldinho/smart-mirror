#!/usr/bin/env bash
set -euo pipefail

URL="${1:-http://localhost:8080}"

chromium-browser \
  --kiosk \
  --incognito \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --noerrdialogs \
  --disable-session-crashed-bubble \
  "$URL"
