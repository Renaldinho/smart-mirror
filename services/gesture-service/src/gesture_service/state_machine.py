from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Decision:
    should_emit: bool
    gesture: str
    action: str | None
    stability_frames: int
    reason: str


class GestureDebouncer:
    def __init__(
        self,
        *,
        mapping: dict[str, str],
        stability_frames: int,
        cooldown_ms: int,
        no_hand_reset_ms: int,
    ) -> None:
        self._mapping = mapping
        self._stability_frames = stability_frames
        self._cooldown_ms = cooldown_ms
        self._no_hand_reset_ms = no_hand_reset_ms

        self._current_gesture: str | None = None
        self._stable_count = 0
        self._last_seen_hand_ms: int | None = None
        self._last_emitted_by_action: dict[str, int] = {}

    def observe(self, gesture: str, now_ms: int) -> Decision:
        self._last_seen_hand_ms = now_ms

        if gesture != self._current_gesture:
            self._current_gesture = gesture
            self._stable_count = 1
        else:
            self._stable_count += 1

        action = self._mapping.get(gesture, "IGNORE")

        if self._stable_count < self._stability_frames:
            return Decision(
                should_emit=False,
                gesture=gesture,
                action=action,
                stability_frames=self._stable_count,
                reason="unstable",
            )

        if action == "IGNORE":
            return Decision(
                should_emit=False,
                gesture=gesture,
                action=action,
                stability_frames=self._stable_count,
                reason="ignored",
            )

        last_emitted = self._last_emitted_by_action.get(action)
        if last_emitted is not None and now_ms - last_emitted < self._cooldown_ms:
            return Decision(
                should_emit=False,
                gesture=gesture,
                action=action,
                stability_frames=self._stable_count,
                reason="cooldown",
            )

        self._last_emitted_by_action[action] = now_ms
        # Reset to force re-stabilization before the next emit.
        self._current_gesture = None
        self._stable_count = 0

        return Decision(
            should_emit=True,
            gesture=gesture,
            action=action,
            stability_frames=self._stability_frames,
            reason="emit",
        )

    def on_no_hand(self, now_ms: int) -> bool:
        if self._last_seen_hand_ms is None:
            return False
        if now_ms - self._last_seen_hand_ms < self._no_hand_reset_ms:
            return False
        self._current_gesture = None
        self._stable_count = 0
        self._last_seen_hand_ms = None
        return True

