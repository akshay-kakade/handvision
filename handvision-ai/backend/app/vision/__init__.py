"""Vision module for hand detection, gesture recognition, tracking, and heatmap."""
from .gestures import classify_gesture
from .tracker import HandTracker

try:
    from .detector import HandDetector
except ImportError:
    HandDetector = None

try:
    from .heatmap import generate_spatial_heatmap, apply_colormap_to_heatmap, extract_heatmap_points
except ImportError:
    generate_spatial_heatmap = None
    apply_colormap_to_heatmap = None
    extract_heatmap_points = None

__all__ = [
    "HandDetector",
    "classify_gesture",
    "HandTracker",
    "generate_spatial_heatmap",
    "apply_colormap_to_heatmap",
    "extract_heatmap_points",
]
