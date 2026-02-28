# Raspberry Pi Runbook

Run all commands from repo root (`~/smart-mirror`) unless a section says otherwise.

## 1) Prerequisites

- Raspberry Pi OS (Bookworm recommended).
- Docker + Docker Compose plugin.
- Pi camera enabled (`raspi-config`).
- Chromium installed for kiosk mode.
- Python 3 + venv available.
- `python3-picamera2` installed on host OS.

## 2) Prepare repository

```bash
git clone <your-repo-url> smart-mirror
cd smart-mirror
git submodule update --init --recursive
cp .env.example .env
chmod +x scripts/*.sh
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
docker compose up --build -d mosquitto magicmirror
```

After first successful build, use this faster command for normal restarts:

```bash
docker compose up -d
```

Build only when Dockerfiles or dependency manifests changed:
```bash
docker compose build magicmirror
docker compose up -d mosquitto magicmirror
```

Check:

```bash
docker compose ps
docker compose logs -f magicmirror
```

## 4) Install host gesture service (recommended)

```bash
./scripts/install-gesture-service.sh
```

View service logs:

```bash
journalctl --user -u smart-mirror-gesture.service -f
```

Enable auto-start at boot (without user login):

```bash
sudo loginctl enable-linger "$USER"
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
systemctl --user restart smart-mirror-gesture.service
```

## 7) Troubleshooting

- Broker auth errors:
  - Remove broker data volume and restart:
    - `docker volume rm smart-mirror_mosquitto-data`
- No camera frames:
  - Verify devices exist:
    - `ls -l /dev/video*`
  - Check host service logs:
    - `journalctl --user -u smart-mirror-gesture.service -n 200 --no-pager`
  - Try index mode first:
    - set `CAMERA_INDEX=0` or `CAMERA_INDEX=1` in `.env`
  - If needed, set explicit device path:
    - `GESTURE_CAMERA_DEVICE=/dev/videoX`
  - Restart host service:
    - `systemctl --user restart smart-mirror-gesture.service`
- High latency:
  - Lower `stability_frames` or `cooldown_ms` in `config/gestures.yaml`.
  - Ensure Pi CPU governor is not power-saving.

Optional all-docker gesture mode (not recommended for Pi camera stack):

```bash
docker compose --profile docker-gesture up --build -d
```

## 8) Build-time optimization tips

- First build on Raspberry Pi can take 5-15 minutes; this is normal.
- Keep Docker BuildKit enabled (default in modern Docker).
- Avoid `--no-cache` unless debugging build issues.
- Use targeted rebuilds:
  - `docker compose build magicmirror`
