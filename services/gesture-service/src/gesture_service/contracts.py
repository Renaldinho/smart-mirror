from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

GestureName = Literal["OPEN_PALM", "FIST", "POINTING", "BOTH_PINCH", "UNKNOWN"]
ActionName = Literal["TOGGLE_WIDGETS", "NEXT_LAYOUT", "NEXT_WIDGET", "TOGGLE_FOCUS_MODE"]


def utc_iso_now() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class RawGestureEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: Literal["gesture.raw.v1"] = Field(
        default="gesture.raw.v1", alias="schema", serialization_alias="schema"
    )
    eventId: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_iso_now)
    deviceId: str
    gesture: GestureName
    confidence: float
    handsDetected: int
    stabilityFrames: int
    fps: float

    @field_validator("confidence")
    @classmethod
    def _confidence_range(cls, value: float) -> float:
        if value < 0 or value > 1:
            raise ValueError("confidence must be in [0, 1]")
        return value


class GestureActionEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: Literal["gesture.action.v1"] = Field(
        default="gesture.action.v1", alias="schema", serialization_alias="schema"
    )
    eventId: str = Field(default_factory=lambda: str(uuid4()))
    sourceEventId: str
    ts: str = Field(default_factory=utc_iso_now)
    action: ActionName
    gesture: Literal["OPEN_PALM", "FIST", "POINTING", "BOTH_PINCH"]
    deviceId: str


class GestureStatusEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_name: Literal["gesture.status.v1"] = Field(
        default="gesture.status.v1", alias="schema", serialization_alias="schema"
    )
    eventId: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_iso_now)
    deviceId: str
    camera: Literal["ok", "degraded", "error"]
    broker: Literal["connected", "disconnected"]
    fps: float
