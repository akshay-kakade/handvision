"""Pydantic schemas package."""
from .detection import (
    BoundingBox,
    Landmark,
    HandDetection,
    DetectionResult,
    HealthResponse,
)

__all__ = [
    "BoundingBox",
    "Landmark",
    "HandDetection",
    "DetectionResult",
    "HealthResponse",
]
