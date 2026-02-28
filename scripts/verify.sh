#!/usr/bin/env bash
set -euo pipefail

echo "Running gesture-service tests..."
pushd services/gesture-service >/dev/null
python -m pytest
popd >/dev/null

echo "Running MMM-GestureBridge tests..."
pushd services/mmm-gesture-bridge >/dev/null
npm test
popd >/dev/null

echo "Verification complete."
