# Raspberry Pi Runbook

## 1) Prerequisites

- Raspberry Pi OS (Bookworm recommended).
- Docker + Docker Compose plugin.
- Pi camera enabled (`raspi-config`).
- Chromium installed for kiosk mode.

## 2) Prepare repository

```bash
git clone <your-repo-url> smart-mirror
cd smart-mirror
git submodule update --init --recursive
cp .env.example .env
```

Set secure MQTT credentials in `.env`.

## 3) Start runtime

```bash
docker compose up --build -d
```

Check:

```bash
docker compose ps
docker compose logs -f gesture-service
docker compose logs -f magicmirror
```

## 4) Launch kiosk browser

```bash
./scripts/run-kiosk.sh
```

This opens `http://localhost:8080` in fullscreen kiosk mode.

## 5) Tune gesture behavior

Edit `config/gestures.yaml`, then restart containers:

```bash
docker compose restart gesture-service magicmirror
```

## 6) Troubleshooting

- Broker auth errors:
  - Remove broker data volume and restart:
    - `docker volume rm smart-mirror_mosquitto-data`
- No camera frames:
  - Verify devices exist:
    - `ls -l /dev/video0 /dev/vchiq`
  - Confirm camera permissions for Docker user/group.
- High latency:
  - Lower `stability_frames` or `cooldown_ms` in `config/gestures.yaml`.
  - Ensure Pi CPU governor is not power-saving.
