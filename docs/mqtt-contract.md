# MQTT Contract

## Topics

| Topic | Producer | Consumer | QoS | Retain |
|---|---|---|---|---|
| `mirror/gesture/raw/v1` | gesture-service | MMM-GestureBridge | 1 | false |
| `mirror/gesture/action/v1` | MMM-GestureBridge | diagnostics tools | 1 | false |
| `mirror/gesture/status/v1` | gesture-service | MMM-GestureBridge | 0 | false |

## `gesture.raw.v1`

```json
{
  "schema": "gesture.raw.v1",
  "eventId": "uuid-v4",
  "ts": "ISO-8601 UTC",
  "deviceId": "mirror-rpi-01",
  "gesture": "OPEN_PALM|FIST|POINTING|BOTH_PINCH|UNKNOWN",
  "confidence": 0.82,
  "handsDetected": 1,
  "stabilityFrames": 4,
  "fps": 14.7
}
```

## `gesture.action.v1`

```json
{
  "schema": "gesture.action.v1",
  "eventId": "uuid-v4",
  "sourceEventId": "uuid-v4",
  "ts": "ISO-8601 UTC",
  "action": "TOGGLE_WIDGETS|NEXT_LAYOUT|NEXT_WIDGET|TOGGLE_FOCUS_MODE",
  "gesture": "OPEN_PALM|FIST|POINTING|BOTH_PINCH",
  "deviceId": "mirror-rpi-01"
}
```

## `gesture.status.v1`

```json
{
  "schema": "gesture.status.v1",
  "eventId": "uuid-v4",
  "ts": "ISO-8601 UTC",
  "deviceId": "mirror-rpi-01",
  "camera": "ok",
  "broker": "connected",
  "fps": 14.9
}
```

## Delivery expectations

- Consumers must ignore unknown fields.
- Producers keep event IDs unique.
- Clock should be synced (NTP) for timestamp ordering.
