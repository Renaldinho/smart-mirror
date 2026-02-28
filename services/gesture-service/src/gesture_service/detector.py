from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import cv2
import mediapipe as mp

try:
    from picamera2 import Picamera2  # type: ignore
except Exception:  # pragma: no cover - import availability is platform-specific.
    Picamera2 = None  # type: ignore


@dataclass(slots=True)
class DetectionResult:
    landmarks: list[list[Any]]
    frame_bgr: Any | None


class HandDetector:
    def __init__(
        self,
        *,
        min_detection_confidence: float,
        min_tracking_confidence: float,
        camera_index: int = 0,
        debug_window: bool = False,
    ) -> None:
        self._camera_index = camera_index
        self._debug_window = debug_window
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._mp_draw = mp.solutions.drawing_utils
        self._capture: cv2.VideoCapture | None = None
        self._picam2: Any | None = None
        self.camera_state: str = "error"
        self.camera_backend: str = "unknown"

    def start(self) -> None:
        prefer_picamera = os.getenv("PREFER_PICAMERA2", "1") == "1"
        if prefer_picamera and Picamera2 is not None:
            self._picam2 = Picamera2()
            self._picam2.start()
            self.camera_backend = "picamera2"
            self.camera_state = "ok"
            return

        self._capture = cv2.VideoCapture(self._camera_index)
        if not self._capture.isOpened():
            raise RuntimeError("Unable to open camera device")
        self.camera_backend = "opencv"
        self.camera_state = "ok"

    def recover(self) -> None:
        if self._picam2 is not None:
            try:
                self._picam2.stop()
                self._picam2.start()
                self.camera_state = "degraded"
            except Exception:
                self.camera_state = "error"
            return

        if self._capture is not None:
            self._capture.release()
        self._capture = cv2.VideoCapture(self._camera_index)
        if self._capture.isOpened():
            self.camera_state = "degraded"
        else:
            self.camera_state = "error"

    def stop(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        if self._picam2 is not None:
            self._picam2.stop()
            self._picam2 = None
        if self._debug_window:
            cv2.destroyAllWindows()

    def _capture_frame(self) -> Any:
        if self._picam2 is not None:
            try:
                frame = self._picam2.capture_array()
            except Exception as exc:
                self.camera_state = "degraded"
                raise RuntimeError("Failed to read frame from picamera2") from exc
            if frame.shape[-1] == 4:
                self.camera_state = "ok"
                return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            self.camera_state = "ok"
            return frame

        if self._capture is None:
            raise RuntimeError("Camera not initialized")
        ok, frame = self._capture.read()
        if not ok:
            self.camera_state = "degraded"
            raise RuntimeError("Failed to read frame from camera")
        self.camera_state = "ok"
        return frame

    def poll(self) -> DetectionResult:
        frame_bgr = self._capture_frame()
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        result = self._hands.process(rgb)

        landmarks: list[list[Any]] = []
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                landmarks.append(list(hand_landmarks.landmark))
                if self._debug_window:
                    self._mp_draw.draw_landmarks(
                        frame_bgr, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                    )

        if self._debug_window:
            cv2.imshow("Gesture Service Debug", frame_bgr)
            cv2.waitKey(1)

        return DetectionResult(landmarks=landmarks, frame_bgr=frame_bgr)
