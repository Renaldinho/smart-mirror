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
2. Start stack (Pi recommended, host Picamera2 mode):
   - `docker compose up -d mosquitto magicmirror`
3. Start gesture service on host:
   - `./scripts/run-gesture-host.sh`
4. Subsequent starts (no rebuild):
   - `docker compose up -d`
5. Open mirror runtime:
   - `http://localhost:8080`

All-docker mode (optional):

- `docker compose --profile docker-gesture up --build -d`

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
- Recommended: run gesture service on host OS with Picamera2 (`scripts/run-gesture-host.sh`).
- Optional all-docker mode uses camera video device mapping (default `/dev/video0`).
- Run Chromium in kiosk mode against `http://localhost:8080`.

Detailed setup docs:

- `docs/architecture.md`
- `docs/mqtt-contract.md`
- `docs/runbook-raspberry-pi.md`
