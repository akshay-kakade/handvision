import pytest
from pydantic import ValidationError
from app.schemas.detection import (
    BoundingBox,
    Landmark,
    HandDetection,
    DetectionResult,
    HealthResponse,
)

def test_valid_detection_result():
    lms = [Landmark(x=0.5, y=0.5, z=0.0) for _ in range(21)]
    bbox = BoundingBox(x=0.2, y=0.2, width=0.4, height=0.4)

    hand = HandDetection(
        track_id=1,
        handedness="Right",
        handedness_confidence=0.98,
        gesture="Peace Sign",
        gesture_confidence=0.89,
        bounding_box=bbox,
        landmarks=lms
    )

    result = DetectionResult(
        type="detection_result",
        timestamp=1700000000000,
        processing_ms=18.4,
        frame_width=640,
        frame_height=480,
        hands_detected=1,
        hands=[hand]
    )

    assert result.hands_detected == 1
    assert result.hands[0].track_id == 1
    assert len(result.hands[0].landmarks) == 21
    assert result.hands[0].gesture == "Peace Sign"

def test_empty_hands_detection_result():
    result = DetectionResult(
        type="detection_result",
        timestamp=1700000000000,
        processing_ms=5.2,
        frame_width=640,
        frame_height=480,
        hands_detected=0,
        hands=[]
    )

    assert result.hands_detected == 0
    assert len(result.hands) == 0

def test_reject_malformed_bounding_box():
    # Out of range coordinates (> 1.0)
    with pytest.raises(ValidationError):
        BoundingBox(x=1.5, y=0.2, width=0.3, height=0.3)

    # Negative coordinates
    with pytest.raises(ValidationError):
        BoundingBox(x=-0.1, y=0.2, width=0.3, height=0.3)

def test_reject_malformed_detection_result():
    # Missing required timestamp
    with pytest.raises(ValidationError):
        DetectionResult(
            frame_width=640,
            frame_height=480,
            hands_detected=0
        )

    # Invalid frame dimensions (<= 0)
    with pytest.raises(ValidationError):
        DetectionResult(
            type="detection_result",
            timestamp=1700000000,
            processing_ms=10.0,
            frame_width=0,
            frame_height=480,
            hands_detected=0
        )

def test_health_response_schema():
    health = HealthResponse(
        status="healthy",
        detector_initialized=True,
        model_loaded=True,
        version="1.0.0",
        max_hands=4
    )
    assert health.status == "healthy"
    assert health.detector_initialized is True
