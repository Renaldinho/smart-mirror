from pydantic import ValidationError

from gesture_service.contracts import GestureActionEvent, GestureStatusEvent, RawGestureEvent


def test_raw_event_validation() -> None:
    event = RawGestureEvent(
        deviceId="mirror-rpi-01",
        gesture="OPEN_PALM",
        confidence=0.8,
        handsDetected=1,
        stabilityFrames=4,
        fps=15.0,
    )
    dumped = event.model_dump(mode="json", by_alias=True)
    assert dumped["schema"] == "gesture.raw.v1"
    assert dumped["gesture"] == "OPEN_PALM"


def test_action_event_validation() -> None:
    event = GestureActionEvent(
        sourceEventId="d662a5f8-4e00-4b11-8aa2-731cbf95e3ef",
        action="NEXT_LAYOUT",
        gesture="FIST",
        deviceId="mirror-rpi-01",
    )
    dumped = event.model_dump(mode="json", by_alias=True)
    assert dumped["schema"] == "gesture.action.v1"
    assert dumped["action"] == "NEXT_LAYOUT"


def test_status_event_validation() -> None:
    event = GestureStatusEvent(
        deviceId="mirror-rpi-01",
        camera="ok",
        broker="connected",
        fps=14.2,
    )
    assert event.model_dump(mode="json", by_alias=True)["schema"] == "gesture.status.v1"


def test_invalid_confidence_rejected() -> None:
    try:
        RawGestureEvent(
            deviceId="mirror-rpi-01",
            gesture="OPEN_PALM",
            confidence=1.4,
            handsDetected=1,
            stabilityFrames=4,
            fps=10.0,
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("Expected invalid confidence to raise ValidationError")
