# smart-mirror

MagicMirror2-based mirror runtime with local gesture control.

## What this repo contains

- `vendor/MagicMirror2`: pinned git submodule for MagicMirror2.
- `services/gesture-service`: Python detector that emits normalized gestures over MQTT.
- `services/mmm-gesture-bridge`: custom MagicMirror module that consumes gestures and triggers UI actions.
- `config/`: shared runtime config (`gestures.yaml`, Mosquitto, MagicMirror config).
- `shared/gesture-config/contract.json`: shared contract used by Python and Node loaders.

## Quick start

1. Copy env vars:
   - `cp .env.example .env`
2. Start full stack (all Docker images):
   - `docker compose up --build -d`
3. Subsequent starts (no rebuild):
   - `docker compose up -d`
4. Open mirror runtime:
   - `http://localhost:8080`

## Actions mapped in MVP

- `OPEN_PALM` -> `TOGGLE_WIDGETS`
- `FIST` -> `NEXT_LAYOUT`
- `POINTING` -> `NEXT_WIDGET`
- `BOTH_PINCH` -> `TOGGLE_FOCUS_MODE`

## Local development

Gesture service tests:

- `cd services/gesture-service`
- `python -m venv .venv`
- `. .venv/bin/activate` (Linux/macOS) or `.venv\\Scripts\\activate` (Windows PowerShell)
- `pip install -e ".[dev]"`
- `pytest`

MMM-GestureBridge tests:

- `cd services/mmm-gesture-bridge`
- `npm install`
- `npm test`

## Raspberry Pi notes

- Target OS: Raspberry Pi OS.
- Default camera device mapping is `GESTURE_CAMERA_DEVICE=/dev/video0`.
- `gesture-service` also auto-scans `/dev/video*` when `CAMERA_AUTO_SCAN=1`.
- If your camera appears on a different node, set `GESTURE_CAMERA_DEVICE` in `.env` (for example `/dev/video1`).
- Run Chromium in kiosk mode against `http://localhost:8080`.

Optional fallback mode:

- Run gesture service on host OS using `scripts/run-gesture-host.sh` if your camera stack is unstable in Docker.

Detailed setup docs:

- `docs/architecture.md`
- `docs/mqtt-contract.md`
- `docs/runbook-raspberry-pi.md`
