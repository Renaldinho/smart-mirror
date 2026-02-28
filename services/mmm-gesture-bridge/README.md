# MMM-GestureBridge

MagicMirror module that bridges `gesture.raw.v1` MQTT messages to mirror UI actions.

## Responsibilities

- Subscribe to raw gesture topic.
- Map gestures using shared `config/gestures.yaml`.
- Execute presentation actions on the mirror DOM.
- Publish `gesture.action.v1` events.
- Render diagnostics overlay.

## Test

```bash
npm install
npm test
```
