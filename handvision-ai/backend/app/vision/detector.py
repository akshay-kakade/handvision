import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np

from ..config import settings
from ..schemas.detection import BoundingBox, Landmark
from ..utils.image_processing import resize_frame, bgr_to_rgb

logger = logging.getLogger(__name__)

def ensure_model_file(model_path: Path, model_url: str) -> bool:
    """
    Checks if the MediaPipe hand_landmarker.task asset exists locally.
    If missing, downloads it once from the official Google URL.
    Does NOT download if the file is already present.
    """
    if model_path.exists() and model_path.stat().st_size > 10000:
        logger.info("MediaPipe model already exists at %s", model_path)
        return True

    logger.info("Downloading official MediaPipe Hand Landmarker model from %s...", model_url)
    try:
        model_path.parent.mkdir(parents=True, exist_ok=True)
        import requests
        resp = requests.get(model_url, timeout=30, stream=True)
        resp.raise_for_status()
        with open(model_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info("Downloaded Hand Landmarker model successfully (%d bytes)", model_path.stat().st_size)
        return True
    except Exception as e:
        logger.warning("Could not download model asset: %s. Will fallback to mp.solutions.hands if available.", e)
        return False

class HandDetector:
    """
    Thread-safe Hand Landmarker wrapper.
    Supports official MediaPipe Tasks HandLandmarker API with graceful fallback
    to MediaPipe Solutions Hands API.
    """
    def __init__(
        self,
        max_hands: int = 4,
        min_detection_confidence: float = 0.5,
        min_presence_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_path: Optional[Path] = None,
        model_url: Optional[str] = None
    ):
        self.max_hands = max_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_presence_confidence = min_presence_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_path = model_path or settings.MODEL_PATH
        self.model_url = model_url or settings.MODEL_URL

        self.tasks_landmarker = None
        self.solutions_hands = None
        self.api_mode: Optional[str] = None
        self.is_initialized: bool = False

        self._initialize()

    def _initialize(self) -> None:
        """Initializes the MediaPipe detector."""
        # 1. Attempt official Tasks API with model asset
        try:
            model_ready = ensure_model_file(self.model_path, self.model_url)
            if model_ready and self.model_path.exists():
                import mediapipe as mp
                from mediapipe.tasks import python as mp_python
                from mediapipe.tasks.python import vision

                base_options = mp_python.BaseOptions(model_asset_path=str(self.model_path))
                options = vision.HandLandmarkerOptions(
                    base_options=base_options,
                    running_mode=vision.RunningMode.IMAGE,
                    num_hands=self.max_hands,
                    min_hand_detection_confidence=self.min_detection_confidence,
                    min_hand_presence_confidence=self.min_presence_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
                self.tasks_landmarker = vision.HandLandmarker.create_from_options(options)
                self.api_mode = "tasks"
                self.is_initialized = True
                logger.info("Initialized MediaPipe Tasks HandLandmarker successfully")
                return
        except Exception as e:
            logger.warning("Failed to initialize MediaPipe Tasks HandLandmarker: %s. Trying solutions fallback...", e)

        # 2. Fallback to classic solutions.hands API
        try:
            import mediapipe as mp
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
                self.solutions_hands = mp.solutions.hands.Hands(
                    static_image_mode=False,
                    max_num_hands=self.max_hands,
                    min_detection_confidence=self.min_detection_confidence,
                    min_tracking_confidence=self.min_tracking_confidence
                )
                self.api_mode = "solutions"
                self.is_initialized = True
                logger.info("Initialized MediaPipe Solutions Hands fallback successfully")
                return
        except Exception as e:
            logger.error("Failed to initialize MediaPipe Solutions Hands: %s", e)

        logger.error("Neither MediaPipe Tasks nor Solutions API could be initialized.")
        self.is_initialized = False

    def detect(self, bgr_frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs hand detection and landmark extraction on an input BGR frame.
        
        Args:
            bgr_frame: np.ndarray (OpenCV BGR image)
            
        Returns:
            List of detected hands with keys:
            - 'landmarks': List[Landmark] (all 21 points)
            - 'bbox': BoundingBox
            - 'handedness': str or None ('Left'/'Right')
            - 'handedness_confidence': float or None
        """
        if not self.is_initialized or bgr_frame is None or bgr_frame.size == 0:
            return []

        # Resize if dimensions exceed threshold
        resized_bgr, _ = resize_frame(
            bgr_frame,
            max_width=settings.MAX_FRAME_WIDTH,
            max_height=settings.MAX_FRAME_HEIGHT
        )
        rgb_frame = bgr_to_rgb(resized_bgr)

        if self.api_mode == "tasks" and self.tasks_landmarker is not None:
            return self._detect_tasks(rgb_frame)
        elif self.api_mode == "solutions" and self.solutions_hands is not None:
            return self._detect_solutions(rgb_frame)
        return []

    def _detect_tasks(self, rgb_frame: np.ndarray) -> List[Dict[str, Any]]:
        import mediapipe as mp
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.tasks_landmarker.detect(mp_image)

        detected_hands = []
        if not result or not result.hand_landmarks:
            return detected_hands

        for idx, hand_lms in enumerate(result.hand_landmarks):
            landmarks = [
                Landmark(
                    x=float(np.clip(lm.x, 0.0, 1.0)),
                    y=float(np.clip(lm.y, 0.0, 1.0)),
                    z=float(lm.z)
                )
                for lm in hand_lms
            ]

            handedness_label = None
            handedness_score = None
            if result.handedness and idx < len(result.handedness) and len(result.handedness[idx]) > 0:
                cat = result.handedness[idx][0]
                handedness_label = cat.category_name
                handedness_score = round(float(cat.score), 2)

            bbox = self._calculate_bounding_box(landmarks)

            detected_hands.append({
                "landmarks": landmarks,
                "bbox": bbox,
                "handedness": handedness_label,
                "handedness_confidence": handedness_score
            })

        return detected_hands

    def _detect_solutions(self, rgb_frame: np.ndarray) -> List[Dict[str, Any]]:
        result = self.solutions_hands.process(rgb_frame)
        detected_hands = []
        if not result or not result.multi_hand_landmarks:
            return detected_hands

        for idx, hand_landmarks in enumerate(result.multi_hand_landmarks):
            landmarks = [
                Landmark(
                    x=float(np.clip(lm.x, 0.0, 1.0)),
                    y=float(np.clip(lm.y, 0.0, 1.0)),
                    z=float(lm.z)
                )
                for lm in hand_landmarks.landmark
            ]

            handedness_label = None
            handedness_score = None
            if result.multi_handedness and idx < len(result.multi_handedness):
                cls = result.multi_handedness[idx].classification[0]
                handedness_label = cls.label
                handedness_score = round(float(cls.score), 2)

            bbox = self._calculate_bounding_box(landmarks)

            detected_hands.append({
                "landmarks": landmarks,
                "bbox": bbox,
                "handedness": handedness_label,
                "handedness_confidence": handedness_score
            })

        return detected_hands

    def _calculate_bounding_box(self, landmarks: List[Landmark], margin: float = 0.03) -> BoundingBox:
        """Computes normalized bounding box enclosing landmarks with safe margin."""
        xs = [lm.x for lm in landmarks]
        ys = [lm.y for lm in landmarks]

        min_x = max(0.0, min(xs) - margin)
        min_y = max(0.0, min(ys) - margin)
        max_x = min(1.0, max(xs) + margin)
        max_y = min(1.0, max(ys) + margin)

        width = min(1.0 - min_x, max(0.01, max_x - min_x))
        height = min(1.0 - min_y, max(0.01, max_y - min_y))

        return BoundingBox(
            x=round(min_x, 4),
            y=round(min_y, 4),
            width=round(width, 4),
            height=round(height, 4)
        )

    def close(self) -> None:
        """Releases detector resources."""
        if self.tasks_landmarker:
            try:
                self.tasks_landmarker.close()
            except Exception:
                pass
            self.tasks_landmarker = None

        if self.solutions_hands:
            try:
                self.solutions_hands.close()
            except Exception:
                pass
            self.solutions_hands = None

        self.is_initialized = False
