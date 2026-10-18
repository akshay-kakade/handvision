import base64
import logging
from typing import Tuple, Optional, Union
import cv2
import numpy as np

logger = logging.getLogger(__name__)

def decode_image(payload: Union[bytes, str]) -> Optional[np.ndarray]:
    """
    Decodes an image payload into an OpenCV BGR numpy array.
    Supports:
      - Raw binary image bytes (JPEG, PNG, WebP)
      - Base64 string (with or without 'data:image/...;base64,' prefix)
    Returns:
      np.ndarray (BGR) or None if decoding fails or payload is malformed.
    """
    try:
        if isinstance(payload, str):
            if "," in payload:
                # Remove header e.g. "data:image/jpeg;base64,"
                payload = payload.split(",", 1)[1]
            raw_bytes = base64.b64decode(payload)
        elif isinstance(payload, (bytes, bytearray)):
            raw_bytes = bytes(payload)
        else:
            logger.warning("Unsupported image payload type: %s", type(payload))
            return None

        if len(raw_bytes) == 0:
            return None

        nparr = np.frombuffer(raw_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None or img.size == 0 or len(img.shape) != 3:
            logger.warning("cv2.imdecode produced empty or invalid image")
            return None

        return img
    except Exception as e:
        logger.error("Error decoding image: %s", e)
        return None

def resize_frame(
    frame: np.ndarray,
    max_width: int = 640,
    max_height: int = 480
) -> Tuple[np.ndarray, float]:
    """
    Downsamples a frame if it exceeds max_width or max_height while preserving aspect ratio.
    Returns:
      Tuple[resized_frame, scale_factor]
    """
    height, width = frame.shape[:2]
    if width <= max_width and height <= max_height:
        return frame, 1.0

    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h)

    new_w = max(1, int(width * scale))
    new_h = max(1, int(height * scale))

    resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return resized, scale

def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    """
    Converts standard OpenCV BGR image to RGB format required by MediaPipe.
    """
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
