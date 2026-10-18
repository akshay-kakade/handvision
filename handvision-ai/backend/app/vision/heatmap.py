from typing import List, Tuple, Dict, Any, Optional
import cv2
import numpy as np
from ..schemas.detection import Landmark

# Key landmark indices with higher intensity weight (fingertips and palm center)
FINGERTIP_INDICES = {4, 8, 12, 16, 20}
PALM_CENTER_INDICES = {0, 9}

def generate_spatial_heatmap(
    all_hand_landmarks: List[List[Landmark]],
    width: int = 320,
    height: int = 240,
    sigma: float = 12.0
) -> np.ndarray:
    """
    Generates a normalized spatial landmark intensity heatmap.
    
    Places 2D Gaussian kernels at normalized landmark locations across all detected hands.
    Assigns higher intensity weights to fingertips and palm centers.
    
    Returns:
      A 2D float32 numpy array with values normalized in range [0.0, 1.0].
      If no landmarks are provided, returns an array of zeros.
    """
    heatmap = np.zeros((height, width), dtype=np.float32)

    if not all_hand_landmarks:
        return heatmap

    # Pre-create coordinate grid for kernel evaluation
    y_coords, x_coords = np.ogrid[:height, :width]
    two_sigma_sq = 2.0 * (sigma ** 2)

    for landmarks in all_hand_landmarks:
        for idx, lm in enumerate(landmarks):
            # Convert normalized coordinates to pixel space
            px = int(np.clip(lm.x * width, 0, width - 1))
            py = int(np.clip(lm.y * height, 0, height - 1))

            # Weight fingertips and palm center higher
            weight = 1.5 if idx in FINGERTIP_INDICES else (1.2 if idx in PALM_CENTER_INDICES else 1.0)

            # Local bounding box to restrict Gaussian evaluation
            radius = int(sigma * 3)
            x_min = max(0, px - radius)
            x_max = min(width, px + radius + 1)
            y_min = max(0, py - radius)
            y_max = min(height, py + radius + 1)

            if x_min >= x_max or y_min >= y_max:
                continue

            # Gaussian computation within the bounding box
            dist_sq = (x_coords[:, x_min:x_max] - px) ** 2 + (y_coords[y_min:y_max, :] - py) ** 2
            kernel = weight * np.exp(-dist_sq / two_sigma_sq)
            heatmap[y_min:y_max, x_min:x_max] += kernel

    # Normalize intensity to [0.0, 1.0]
    max_val = np.max(heatmap)
    if max_val > 1e-5:
        heatmap /= max_val

    return heatmap

def apply_colormap_to_heatmap(
    heatmap: np.ndarray,
    colormap: int = cv2.COLORMAP_JET
) -> np.ndarray:
    """
    Converts a normalized [0, 1] float32 heatmap into an 8-bit BGR color image.
    """
    scaled = (np.clip(heatmap, 0.0, 1.0) * 255.0).astype(np.uint8)
    color_map = cv2.applyColorMap(scaled, colormap)
    return color_map

def extract_heatmap_points(
    all_hand_landmarks: List[List[Landmark]]
) -> List[Dict[str, float]]:
    """
    Extracts normalized coordinates and weights for frontend Canvas rendering.
    Enables low-bandwidth, GPU-accelerated client-side radial gradient rendering.
    """
    points = []
    for landmarks in all_hand_landmarks:
        for idx, lm in enumerate(landmarks):
            weight = 1.5 if idx in FINGERTIP_INDICES else (1.2 if idx in PALM_CENTER_INDICES else 1.0)
            points.append({
                "x": lm.x,
                "y": lm.y,
                "weight": weight
            })
    return points
