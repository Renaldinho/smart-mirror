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
chmod +x scripts/run-kiosk.sh scripts/run-gesture-host.sh scripts/verify.sh
```

Set secure MQTT credentials in `.env`.
Set camera source if needed (default is `CAMERA_INDEX=0`):

```bash
ls -l /dev/video*
# If needed:
# echo "GESTURE_CAMERA_DEVICE=/dev/video1" >> .env
# or:
# echo "CAMERA_INDEX=1" >> .env
```

`gesture-service` does not auto-scan by default (`CAMERA_AUTO_SCAN=0`) to avoid long startup delays.

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
  - Try index mode first:
    - set `CAMERA_INDEX=0` or `CAMERA_INDEX=1` in `.env`.
  - If needed, set explicit device path:
    - `GESTURE_CAMERA_DEVICE=/dev/videoX`
  - Enable fallback probing only if needed:
    - `CAMERA_AUTO_SCAN=1`
    - `CAMERA_SCAN_MAX_INDEX=4`
  - Restart gesture container:
    - `docker compose up -d gesture-service`
- High latency:
  - Lower `stability_frames` or `cooldown_ms` in `config/gestures.yaml`.
  - Ensure Pi CPU governor is not power-saving.

Host fallback mode (if Docker camera stack remains unstable):

```bash
docker compose up -d mosquitto magicmirror
./scripts/run-gesture-host.sh
```

## 7) Build-time optimization tips

- First build on Raspberry Pi can take 5-15 minutes; this is normal.
- Keep Docker BuildKit enabled (default in modern Docker).
- Avoid `--no-cache` unless debugging build issues.
- Use targeted rebuilds:
  - `docker compose build magicmirror`
  - `docker compose build gesture-service`
