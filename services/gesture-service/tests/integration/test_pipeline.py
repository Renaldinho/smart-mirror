import pytest

from gesture_service.state_machine import GestureDebouncer


@pytest.mark.integration
def test_pipeline_no_hand_does_not_emit_phantom_actions() -> None:
    debouncer = GestureDebouncer(
        mapping={
            "OPEN_PALM": "TOGGLE_WIDGETS",
            "FIST": "NEXT_LAYOUT",
            "POINTING": "NEXT_WIDGET",
            "BOTH_PINCH": "TOGGLE_FOCUS_MODE",
            "UNKNOWN": "IGNORE",
        },
        stability_frames=3,
        cooldown_ms=1200,
        no_hand_reset_ms=1000,
    )

    # Stabilize and emit once.
    debouncer.observe("OPEN_PALM", now_ms=0)
    debouncer.observe("OPEN_PALM", now_ms=50)
    emitted = debouncer.observe("OPEN_PALM", now_ms=100)
    assert emitted.should_emit

    # No hand long enough resets state.
    assert debouncer.on_no_hand(now_ms=1300)

    # Fresh stabilization required, no phantom emit.
    first = debouncer.observe("OPEN_PALM", now_ms=1400)
    second = debouncer.observe("OPEN_PALM", now_ms=1450)
    third = debouncer.observe("OPEN_PALM", now_ms=1500)
    assert not first.should_emit
    assert not second.should_emit
    assert third.should_emit

