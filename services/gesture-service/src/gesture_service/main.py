from __future__ import annotations

import os
import signal
import time
from pathlib import Path

from gesture_service.classifier import classify_frame
from gesture_service.config import load_contract, load_gesture_config
from gesture_service.contracts import RawGestureEvent, GestureStatusEvent
from gesture_service.detector import HandDetector
from gesture_service.logging_utils import configure_logging, log_json
from gesture_service.mqtt_client import GestureMqttClient
from gesture_service.state_machine import GestureDebouncer


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _should_show_debug_window() -> bool:
    return os.getenv("GESTURE_DEBUG_WINDOW", "0") == "1"


def main() -> None:
    logger = configure_logging()
    stopped = False

    def _stop_handler(_sig: int, _frame: object) -> None:
        nonlocal stopped
        stopped = True

    signal.signal(signal.SIGTERM, _stop_handler)
    signal.signal(signal.SIGINT, _stop_handler)

    config_path = Path(_env("GESTURE_CONFIG_PATH", "/app/config/gestures.yaml"))
    contract_path = Path(_env("GESTURE_CONTRACT_PATH", "/app/shared/gesture-config/contract.json"))
    camera_index = int(_env("CAMERA_INDEX", "0"))
    mqtt_host = _env("MQTT_HOST", "mosquitto")
    mqtt_port = int(_env("MQTT_PORT", "1883"))
    mqtt_username = _env("MQTT_USERNAME", "mirror")
    mqtt_password = _env("MQTT_PASSWORD", "mirror-secret")
    mqtt_client_id_prefix = _env("MQTT_CLIENT_ID_PREFIX", "gesture-service")

    contract = load_contract(contract_path)
    config = load_gesture_config(config_path, contract)

    mqtt_client = GestureMqttClient(
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_username,
        password=mqtt_password,
        client_id_prefix=mqtt_client_id_prefix,
    )
    mqtt_client.connect()

    debouncer = GestureDebouncer(
        mapping=config.mapping,
        stability_frames=config.detection.stability_frames,
        cooldown_ms=config.detection.cooldown_ms,
        no_hand_reset_ms=config.detection.no_hand_reset_ms,
    )

    detector = HandDetector(
        min_detection_confidence=config.detection.min_detection_confidence,
        min_tracking_confidence=config.detection.min_tracking_confidence,
        camera_index=camera_index,
        debug_window=_should_show_debug_window(),
    )
    detector.start()

    log_json(logger, "gesture-service-started", configPath=str(config_path), deviceId=config.device_id)

    status_interval_sec = 5.0
    next_status_at = time.monotonic() + status_interval_sec
    min_loop_interval_sec = 1.0 / float(config.detection.publish_fps)

    try:
        while not stopped:
            loop_start = time.monotonic()
            now_ms = int(time.time() * 1000)

            try:
                result = detector.poll()
            except RuntimeError as exc:
                detector.recover()
                log_json(
                    logger,
                    "gesture-camera-read-failed",
                    error=str(exc),
                    backend=detector.camera_backend,
                    cameraState=detector.camera_state,
                )
                time.sleep(0.5)
                continue
            gesture, confidence, hands_detected = classify_frame(result.landmarks)

            emitted = False
            if hands_detected == 0:
                debouncer.on_no_hand(now_ms)
            else:
                decision = debouncer.observe(gesture, now_ms)
                if decision.should_emit:
                    raw_event = RawGestureEvent(
                        deviceId=config.device_id,
                        gesture=decision.gesture,  # type: ignore[arg-type]
                        confidence=confidence,
                        handsDetected=hands_detected,
                        stabilityFrames=decision.stability_frames,
                        fps=round(1.0 / max(0.001, time.monotonic() - loop_start), 2),
                    )
                    raw_payload = raw_event.model_dump(mode="json", by_alias=True)
                    emitted = mqtt_client.publish(
                        contract.topics.raw, raw_payload, qos=1
                    )
                    log_json(
                        logger,
                        "gesture-raw-emitted",
                        event=raw_payload,
                        published=emitted,
                    )

            if time.monotonic() >= next_status_at:
                status_event = GestureStatusEvent(
                    deviceId=config.device_id,
                    camera=detector.camera_state,  # type: ignore[arg-type]
                    broker="connected" if mqtt_client.is_connected else "disconnected",
                    fps=round(1.0 / max(0.001, time.monotonic() - loop_start), 2),
                )
                status_payload = status_event.model_dump(mode="json", by_alias=True)
                mqtt_client.publish(contract.topics.status, status_payload, qos=0)
                log_json(logger, "gesture-status-emitted", event=status_payload)
                next_status_at = time.monotonic() + status_interval_sec

            elapsed = time.monotonic() - loop_start
            if elapsed < min_loop_interval_sec:
                time.sleep(min_loop_interval_sec - elapsed)
    finally:
        detector.stop()
        mqtt_client.close()
        log_json(logger, "gesture-service-stopped")


if __name__ == "__main__":
    main()
