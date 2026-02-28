#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/gesture-service"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but not found." >&2
  exit 1
fi

if [ -d "$SERVICE_DIR/.venv" ]; then
  # shellcheck source=/dev/null
  source "$SERVICE_DIR/.venv/bin/activate"
fi

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  # shellcheck source=/dev/null
  source "$ROOT_DIR/.env"
  set +a
fi

export MQTT_HOST="${MQTT_HOST:-127.0.0.1}"
export MQTT_PORT="${MQTT_PORT:-1883}"
export MQTT_USERNAME="${MQTT_USERNAME:-mirror}"
export MQTT_PASSWORD="${MQTT_PASSWORD:-mirror-secret}"
export MQTT_CLIENT_ID_PREFIX="${MQTT_CLIENT_ID_PREFIX:-gesture-service-host}"
export GESTURE_CONFIG_PATH="${GESTURE_CONFIG_PATH:-$ROOT_DIR/config/gestures.yaml}"
export GESTURE_CONTRACT_PATH="${GESTURE_CONTRACT_PATH:-$ROOT_DIR/shared/gesture-config/contract.json}"
export PREFER_PICAMERA2="${PREFER_PICAMERA2:-1}"
export CAMERA_INDEX="${CAMERA_INDEX:-0}"

# Backward-compat for older .env values used only inside Docker containers.
if [[ "$GESTURE_CONFIG_PATH" == /app/* ]]; then
  export GESTURE_CONFIG_PATH="$ROOT_DIR/config/gestures.yaml"
fi
if [[ "$GESTURE_CONTRACT_PATH" == /app/* ]]; then
  export GESTURE_CONTRACT_PATH="$ROOT_DIR/shared/gesture-config/contract.json"
fi
if [[ "$MQTT_HOST" == "mosquitto" ]]; then
  export MQTT_HOST="127.0.0.1"
fi

cd "$SERVICE_DIR"
exec env PYTHONPATH=src python3 -m gesture_service.main
