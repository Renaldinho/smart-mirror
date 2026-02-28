from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator


class TopicConfig(BaseModel):
    raw: str
    action: str
    status: str


class GestureContract(BaseModel):
    version: int
    gestures: list[str]
    actions: list[str]
    topics: TopicConfig


class DetectionConfig(BaseModel):
    min_detection_confidence: float = Field(ge=0.0, le=1.0)
    min_tracking_confidence: float = Field(ge=0.0, le=1.0)
    stability_frames: int = Field(ge=1, le=20)
    cooldown_ms: int = Field(ge=0, le=60_000)
    publish_fps: int = Field(ge=1, le=60)
    no_hand_reset_ms: int = Field(ge=0, le=60_000)


class DiagnosticsConfig(BaseModel):
    overlay_enabled: bool = True


class GestureConfig(BaseModel):
    version: int
    device_id: str = Field(min_length=1)
    detection: DetectionConfig
    mapping: dict[str, str]
    diagnostics: DiagnosticsConfig

    @field_validator("mapping")
    @classmethod
    def _mapping_non_empty(cls, value: dict[str, str]) -> dict[str, str]:
        if not value:
            raise ValueError("mapping must not be empty")
        return value


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML config at {path} must be an object")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON contract at {path} must be an object")
    return data


def load_contract(path: Path) -> GestureContract:
    contract = GestureContract.model_validate(_load_json(path))
    if contract.version != 1:
        raise ValueError(f"Unsupported contract version: {contract.version}")
    return contract


def load_gesture_config(path: Path, contract: GestureContract) -> GestureConfig:
    config = GestureConfig.model_validate(_load_yaml(path))
    if config.version != contract.version:
        raise ValueError(
            f"Gesture config version {config.version} does not match contract version {contract.version}"
        )

    for gesture in contract.gestures:
        if gesture not in config.mapping:
            raise ValueError(f"Missing gesture mapping for {gesture}")

    allowed_actions = set(contract.actions)
    for gesture, action in config.mapping.items():
        if gesture not in contract.gestures:
            raise ValueError(f"Gesture {gesture} is not part of contract")
        if action not in allowed_actions:
            raise ValueError(f"Action {action} mapped from {gesture} is not part of contract")

    return config

