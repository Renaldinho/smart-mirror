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

## 3) Start runtime

Recommended on Raspberry Pi (Picamera2 on host OS):

```bash
docker compose up -d mosquitto magicmirror
```

Optional all-docker mode (uses OpenCV camera in container):

```bash
docker compose --profile docker-gesture up --build -d
```

After first successful build, use this faster command for normal restarts:

```bash
docker compose up -d
```

Build only when Dockerfiles or dependency manifests changed:

For all-docker mode rebuilds:
```bash
docker compose build magicmirror gesture-service
docker compose --profile docker-gesture up -d
```

Check:

```bash
docker compose ps
docker compose logs -f magicmirror
```

## 4) Start gesture service on host (Picamera2 mode)

Install host dependencies once:

```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-opencv python3-yaml python3-paho-mqtt python3-venv
```

Start service:

```bash
chmod +x scripts/run-gesture-host.sh
./scripts/run-gesture-host.sh
```

The script reads MQTT credentials from repo `.env`.

If you want a virtual environment:

```bash
cd services/gesture-service
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
cd ../..
./scripts/run-gesture-host.sh
```

## 5) Launch kiosk browser

```bash
./scripts/run-kiosk.sh
```

This opens `http://localhost:8080` in fullscreen kiosk mode.

## 6) Tune gesture behavior

Edit `config/gestures.yaml`, then restart:

```bash
docker compose restart magicmirror
# and restart host gesture process if running in host mode
```

## 7) Troubleshooting

- Broker auth errors:
  - Remove broker data volume and restart:
    - `docker volume rm smart-mirror_mosquitto-data`
- No camera frames:
  - Verify devices exist:
    - `ls -l /dev/video*`
  - Host Picamera2 sanity check:
    - `python3 -c "from picamera2 import Picamera2; c=Picamera2(); c.start(); print(c.capture_array().shape); c.stop()"`
  - All-docker mode only: if camera is not `/dev/video0`, set `GESTURE_CAMERA_DEVICE` in `.env` (example: `/dev/video1`).
- High latency:
  - Lower `stability_frames` or `cooldown_ms` in `config/gestures.yaml`.
  - Ensure Pi CPU governor is not power-saving.

## 8) Build-time optimization tips

- First build on Raspberry Pi can take 5-15 minutes; this is normal.
- Keep Docker BuildKit enabled (default in modern Docker).
- Avoid `--no-cache` unless debugging build issues.
- Use targeted rebuilds:
  - `docker compose build magicmirror`
  - `docker compose build gesture-service`
