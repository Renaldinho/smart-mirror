from __future__ import annotations

from typing import Protocol, Sequence


class LandmarkLike(Protocol):
    x: float
    y: float


def _finger_extended(landmarks: Sequence[LandmarkLike], tip_index: int, pip_index: int) -> bool:
    return landmarks[tip_index].y < landmarks[pip_index].y


def is_pinching(landmarks: Sequence[LandmarkLike], threshold: float = 0.05) -> bool:
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
    return distance < threshold


def classify_hand(landmarks: Sequence[LandmarkLike]) -> tuple[str, float]:
    fingers = [
        _finger_extended(landmarks, 8, 6),
        _finger_extended(landmarks, 12, 10),
        _finger_extended(landmarks, 16, 14),
        _finger_extended(landmarks, 20, 18),
    ]

    if all(fingers):
        return "OPEN_PALM", 0.9
    if not any(fingers):
        return "FIST", 0.9
    if fingers[0] and not any(fingers[1:]):
        return "POINTING", 0.85
    return "UNKNOWN", 0.4


def classify_frame(hands: Sequence[Sequence[LandmarkLike]]) -> tuple[str, float, int]:
    hands_detected = len(hands)
    if hands_detected == 0:
        return "UNKNOWN", 0.0, 0

    if hands_detected >= 2 and is_pinching(hands[0]) and is_pinching(hands[1]):
        return "BOTH_PINCH", 0.92, hands_detected

    gesture, confidence = classify_hand(hands[0])
    return gesture, confidence, hands_detected

