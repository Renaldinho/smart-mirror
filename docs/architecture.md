# Architecture

## Components

1. `gesture-service` (Python)
   - Captures camera frames.
   - Detects hand landmarks via MediaPipe Hands.
   - Classifies gestures.
   - Applies stability/cooldown guards.
   - Publishes normalized MQTT events.

2. `mosquitto` (MQTT broker)
   - Local broker on mirror device.
   - Username/password auth from `.env`.

3. `MMM-GestureBridge` (MagicMirror module)
   - Subscribes to raw gesture events.
   - Maps gestures to UI actions from `config/gestures.yaml`.
   - Applies layout/focus/widget changes in the mirror UI.
   - Publishes mapped action events.

4. `MagicMirror2`
   - Renders the mirror UI in browser/kiosk.

## Data flow

1. Camera frame -> landmarks -> gesture label.
2. Guarded stable gesture -> `mirror/gesture/raw/v1`.
3. MMM-GestureBridge receives event and maps to action.
4. Module updates DOM state (layout/widget/focus).
5. Module publishes action result to `mirror/gesture/action/v1`.
6. Service heartbeat goes to `mirror/gesture/status/v1`.

## Guard rails

- Stability: same gesture required for N frames.
- Cooldown: per-action minimum interval.
- Unknown gestures ignored for action output.

## Runtime topology

- All control paths are local to Raspberry Pi.
- No cloud/backend dependency for gesture interactions.
