from __future__ import annotations

import json
from pathlib import Path

from gesture_service.config import load_contract, load_gesture_config


def test_load_config_matches_contract(tmp_path: Path) -> None:
    contract_path = tmp_path / "contract.json"
    config_path = tmp_path / "gestures.yaml"

    contract_path.write_text(
        json.dumps(
            {
                "version": 1,
                "gestures": ["OPEN_PALM", "FIST", "POINTING", "BOTH_PINCH", "UNKNOWN"],
                "actions": [
                    "TOGGLE_WIDGETS",
                    "NEXT_LAYOUT",
                    "NEXT_WIDGET",
                    "TOGGLE_FOCUS_MODE",
                    "IGNORE",
                ],
                "topics": {"raw": "a", "action": "b", "status": "c"},
            }
        ),
        encoding="utf-8",
    )

    config_path.write_text(
        "\n".join(
            [
                "version: 1",
                "device_id: mirror-rpi-01",
                "detection:",
                "  min_detection_confidence: 0.7",
                "  min_tracking_confidence: 0.7",
                "  stability_frames: 4",
                "  cooldown_ms: 1200",
                "  publish_fps: 15",
                "  no_hand_reset_ms: 1000",
                "mapping:",
                "  OPEN_PALM: TOGGLE_WIDGETS",
                "  FIST: NEXT_LAYOUT",
                "  POINTING: NEXT_WIDGET",
                "  BOTH_PINCH: TOGGLE_FOCUS_MODE",
                "  UNKNOWN: IGNORE",
                "diagnostics:",
                "  overlay_enabled: true",
            ]
        ),
        encoding="utf-8",
    )

    contract = load_contract(contract_path)
    config = load_gesture_config(config_path, contract)
    assert config.device_id == "mirror-rpi-01"
    assert config.mapping["POINTING"] == "NEXT_WIDGET"

