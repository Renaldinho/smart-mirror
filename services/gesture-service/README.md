# gesture-service

Python service that:

1. Captures camera frames.
2. Detects hand landmarks with MediaPipe.
3. Classifies hand gestures.
4. Applies stability/cooldown rules.
5. Publishes MQTT events for MagicMirror consumers.

## Environment variables

- `GESTURE_CONFIG_PATH` (default: `/app/config/gestures.yaml`)
- `GESTURE_CONTRACT_PATH` (default: `/app/shared/gesture-config/contract.json`)
- `MQTT_HOST` (default: `mosquitto`)
- `MQTT_PORT` (default: `1883`)
- `MQTT_USERNAME`
- `MQTT_PASSWORD`
- `MQTT_CLIENT_ID_PREFIX` (default: `gesture-service`)
- `GESTURE_DEBUG_WINDOW` (`1` to open OpenCV debug window)
- `CAMERA_INDEX` (default: `0`, used for OpenCV fallback)
- `CAMERA_DEVICE` (example: `/dev/video1`, preferred OpenCV device path)

## Local test

```bash
pip install -e ".[dev]"
pytest
```
