from __future__ import annotations

from dataclasses import dataclass

from gesture_service.classifier import classify_frame, classify_hand, is_pinching


@dataclass(slots=True)
class Landmark:
    x: float
    y: float


def _blank_hand() -> list[Landmark]:
    return [Landmark(x=0.5, y=0.5) for _ in range(21)]


def _set_finger(landmarks: list[Landmark], *, tip: int, pip: int, extended: bool) -> None:
    landmarks[pip].y = 0.60
    landmarks[tip].y = 0.40 if extended else 0.80


def _build_hand(kind: str) -> list[Landmark]:
    hand = _blank_hand()

    if kind == "OPEN_PALM":
        _set_finger(hand, tip=8, pip=6, extended=True)
        _set_finger(hand, tip=12, pip=10, extended=True)
        _set_finger(hand, tip=16, pip=14, extended=True)
        _set_finger(hand, tip=20, pip=18, extended=True)
    elif kind == "FIST":
        _set_finger(hand, tip=8, pip=6, extended=False)
        _set_finger(hand, tip=12, pip=10, extended=False)
        _set_finger(hand, tip=16, pip=14, extended=False)
        _set_finger(hand, tip=20, pip=18, extended=False)
    elif kind == "POINTING":
        _set_finger(hand, tip=8, pip=6, extended=True)
        _set_finger(hand, tip=12, pip=10, extended=False)
        _set_finger(hand, tip=16, pip=14, extended=False)
        _set_finger(hand, tip=20, pip=18, extended=False)
    else:
        raise ValueError(kind)

    hand[4].x = 0.2
    hand[4].y = 0.5
    hand[8].x = 0.8
    hand[8].y = 0.3 if kind != "FIST" else 0.7
    return hand


def test_classify_open_palm() -> None:
    gesture, confidence = classify_hand(_build_hand("OPEN_PALM"))
    assert gesture == "OPEN_PALM"
    assert confidence > 0.8


def test_classify_fist() -> None:
    gesture, confidence = classify_hand(_build_hand("FIST"))
    assert gesture == "FIST"
    assert confidence > 0.8


def test_classify_pointing() -> None:
    gesture, confidence = classify_hand(_build_hand("POINTING"))
    assert gesture == "POINTING"
    assert confidence > 0.8


def test_detect_both_pinch() -> None:
    hand1 = _build_hand("POINTING")
    hand2 = _build_hand("POINTING")
    hand1[4].x, hand1[4].y = 0.5, 0.5
    hand1[8].x, hand1[8].y = 0.52, 0.5
    hand2[4].x, hand2[4].y = 0.4, 0.5
    hand2[8].x, hand2[8].y = 0.42, 0.5

    assert is_pinching(hand1)
    assert is_pinching(hand2)

    gesture, confidence, hands_detected = classify_frame([hand1, hand2])
    assert gesture == "BOTH_PINCH"
    assert confidence > 0.9
    assert hands_detected == 2

