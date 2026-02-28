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

After first successful build, use this faster command for normal restarts:

```bash
docker compose up -d
```

Build only when Dockerfiles or dependency manifests changed:

```bash
docker compose build magicmirror gesture-service
docker compose up -d
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
    - `ls -l /dev/video*`
  - Confirm camera permissions for Docker user/group.
  - If camera is not `/dev/video0`, set `GESTURE_CAMERA_DEVICE` in `.env` (example: `/dev/video1`).
- High latency:
  - Lower `stability_frames` or `cooldown_ms` in `config/gestures.yaml`.
  - Ensure Pi CPU governor is not power-saving.

## 7) Build-time optimization tips

- First build on Raspberry Pi can take 5-15 minutes; this is normal.
- Keep Docker BuildKit enabled (default in modern Docker).
- Avoid `--no-cache` unless debugging build issues.
- Use targeted rebuilds:
  - `docker compose build magicmirror`
  - `docker compose build gesture-service`
