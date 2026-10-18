from typing import Optional, List
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    """
    Normalized bounding box in image coordinates [0.0, 1.0].
    x: top-left corner x coordinate
    y: top-left corner y coordinate
    width: normalized width of bounding box
    height: normalized height of bounding box
    """
    x: float = Field(..., ge=0.0, le=1.0, description="Normalized x of top-left corner")
    y: float = Field(..., ge=0.0, le=1.0, description="Normalized y of top-left corner")
    width: float = Field(..., ge=0.0, le=1.0, description="Normalized width")
    height: float = Field(..., ge=0.0, le=1.0, description="Normalized height")

class Landmark(BaseModel):
    """
    Normalized 3D hand landmark.
    x, y: normalized coordinates relative to frame width and height [0.0, 1.0].
    z: landmark depth relative to wrist landmark, roughly on the same scale as x.
    """
    x: float = Field(..., description="Normalized x coordinate [0, 1]")
    y: float = Field(..., description="Normalized y coordinate [0, 1]")
    z: float = Field(..., description="Estimated depth coordinate relative to wrist")

class HandDetection(BaseModel):
    """
    Structured detection output for a single detected hand.
    """
    track_id: int = Field(..., description="Persistent track ID assigned to this hand")
    handedness: Optional[str] = Field(None, description="Handedness label ('Left' or 'Right')")
    handedness_confidence: Optional[float] = Field(None, description="Confidence score for handedness")
    gesture: str = Field(..., description="Recognized gesture name or 'Unknown'")
    gesture_confidence: Optional[float] = Field(None, description="Confidence for recognized gesture or None")
    bounding_box: BoundingBox = Field(..., description="Normalized bounding box")
    landmarks: List[Landmark] = Field(..., description="All 21 normalized landmarks")

class DetectionResult(BaseModel):
    """
    Full detection result payload returned via WebSocket for a processed frame.
    """
    type: str = Field("detection_result", description="Message type identifier")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    processing_ms: float = Field(..., description="Backend inference and tracking latency in ms")
    frame_width: int = Field(..., ge=1, description="Width of the processed frame")
    frame_height: int = Field(..., ge=1, description="Height of the processed frame")
    hands_detected: int = Field(..., ge=0, description="Count of detected hands")
    hands: List[HandDetection] = Field(default_factory=list, description="List of detected hands")

class HealthResponse(BaseModel):
    """
    Response model for GET /health.
    """
    model_config = {"protected_namespaces": ()}

    status: str = Field("healthy", description="Application status: healthy or degraded")
    detector_initialized: bool = Field(..., description="Whether hand detector loaded")
    model_loaded: bool = Field(..., description="Whether model weights/task asset is ready")
    version: str = Field("1.0.0", description="Backend version")
    max_hands: int = Field(4, description="Maximum configured hands")
