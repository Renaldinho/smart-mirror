from gesture_service.state_machine import GestureDebouncer


def test_stability_gate_emits_only_after_required_frames() -> None:
    debouncer = GestureDebouncer(
        mapping={"OPEN_PALM": "TOGGLE_WIDGETS"},
        stability_frames=3,
        cooldown_ms=1200,
        no_hand_reset_ms=1000,
    )

    first = debouncer.observe("OPEN_PALM", now_ms=100)
    second = debouncer.observe("OPEN_PALM", now_ms=120)
    third = debouncer.observe("OPEN_PALM", now_ms=140)

    assert not first.should_emit
    assert not second.should_emit
    assert third.should_emit
    assert third.action == "TOGGLE_WIDGETS"


def test_cooldown_blocks_fast_retrigger() -> None:
    debouncer = GestureDebouncer(
        mapping={"OPEN_PALM": "TOGGLE_WIDGETS"},
        stability_frames=2,
        cooldown_ms=1000,
        no_hand_reset_ms=1000,
    )

    debouncer.observe("OPEN_PALM", now_ms=0)
    first_emit = debouncer.observe("OPEN_PALM", now_ms=50)
    assert first_emit.should_emit

    debouncer.observe("OPEN_PALM", now_ms=100)
    blocked = debouncer.observe("OPEN_PALM", now_ms=150)
    assert not blocked.should_emit
    assert blocked.reason == "cooldown"

    second_emit = debouncer.observe("OPEN_PALM", now_ms=1200)
    assert second_emit.should_emit


def test_no_hand_reset_clears_state() -> None:
    debouncer = GestureDebouncer(
        mapping={"FIST": "NEXT_LAYOUT"},
        stability_frames=2,
        cooldown_ms=1000,
        no_hand_reset_ms=300,
    )

    debouncer.observe("FIST", now_ms=100)
    assert debouncer.on_no_hand(now_ms=200) is False
    assert debouncer.on_no_hand(now_ms=450) is True

    # State should require fresh stabilization after reset.
    first = debouncer.observe("FIST", now_ms=500)
    second = debouncer.observe("FIST", now_ms=550)
    assert not first.should_emit
    assert second.should_emit
