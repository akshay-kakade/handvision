import time
import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse

from ..config import settings
from ..schemas.detection import (
    DetectionResult,
    HandDetection,
    HealthResponse,
)
from ..utils.image_processing import decode_image
from ..vision.detector import HandDetector
from ..vision.gestures import classify_gesture
from ..vision.tracker import HandTracker

logger = logging.getLogger(__name__)

router = APIRouter()

# Global detector instance and lock for non-thread-safe inference
_detector: Optional[HandDetector] = None
_detector_lock = asyncio.Lock()
_start_time = time.time()

def get_detector() -> HandDetector:
    global _detector
    if _detector is None:
        _detector = HandDetector(
            max_hands=settings.MAX_HANDS,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_presence_confidence=settings.MIN_PRESENCE_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE,
            model_path=settings.MODEL_PATH,
            model_url=settings.MODEL_URL
        )
    return _detector

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint reporting detector status, model readiness, and uptime.
    """
    detector = get_detector()
    is_ready = detector.is_initialized
    model_ready = settings.MODEL_PATH.exists() or (detector.solutions_hands is not None)

    return HealthResponse(
        status="healthy" if is_ready else "degraded",
        detector_initialized=is_ready,
        model_loaded=model_ready,
        version="1.0.0",
        max_hands=settings.MAX_HANDS
    )

@router.websocket("/ws/detect")
async def websocket_detect_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket detection endpoint.
    - Accepts webcam frames (binary JPEG/PNG or base64 text)
    - Performs hand landmark detection, persistent tracking, and gesture recognition
    - Returns structured JSON detection results
    - Maintains independent tracking state per connected client
    - Drops stale frames to prevent queuing latency
    """
    await websocket.accept()
    logger.info("WebSocket client connected: %s", websocket.client)

    # Per-client persistent tracker
    client_tracker = HandTracker(
        max_disappeared=settings.TRACK_MAX_DISAPPEARED,
        max_distance=settings.TRACK_DISTANCE_THRESHOLD,
        min_iou=settings.TRACK_IOU_THRESHOLD
    )

    detector = get_detector()
    is_processing = False

    try:
        while True:
            # Receive frame data (text or binary bytes)
            message = await websocket.receive()
            if "bytes" in message and message["bytes"]:
                raw_payload = message["bytes"]
            elif "text" in message and message["text"]:
                raw_payload = message["text"]
            else:
                continue

            # Drop frame if previous inference is still in-flight
            if is_processing:
                # Dropping to keep real-time latency strictly minimal
                continue

            is_processing = True
            t_start = time.perf_counter()

            try:
                # Decode image
                frame = decode_image(raw_payload)
                if frame is None:
                    # Send empty result or error acknowledgment
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid or corrupt image frame"
                    })
                    continue

                h, w = frame.shape[:2]

                # Run detection in thread pool with lock to prevent concurrent MediaPipe access
                async with _detector_lock:
                    detected_raw = await asyncio.to_thread(detector.detect, frame)

                # Update per-client persistent tracker
                track_ids = client_tracker.update(detected_raw)

                # Perform rule-based gesture recognition for each hand
                hands_output = []
                for idx, det in enumerate(detected_raw):
                    t_id = track_ids[idx] if idx < len(track_ids) else (idx + 1)
                    gesture_name, gesture_conf = classify_gesture(
                        det["landmarks"],
                        det.get("handedness")
                    )

                    hands_output.append(
                        HandDetection(
                            track_id=t_id,
                            handedness=det.get("handedness"),
                            handedness_confidence=det.get("handedness_confidence"),
                            gesture=gesture_name,
                            gesture_confidence=gesture_conf,
                            bounding_box=det["bbox"],
                            landmarks=det["landmarks"]
                        )
                    )

                t_end = time.perf_counter()
                processing_ms = round((t_end - t_start) * 1000.0, 2)

                result = DetectionResult(
                    type="detection_result",
                    timestamp=int(time.time() * 1000),
                    processing_ms=processing_ms,
                    frame_width=w,
                    frame_height=h,
                    hands_detected=len(hands_output),
                    hands=hands_output
                )

                await websocket.send_text(result.model_dump_json())

            except Exception as e:
                logger.error("Error processing WebSocket frame: %s", e, exc_info=True)
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Processing error: {str(e)}"
                    })
                except Exception:
                    break
            finally:
                is_processing = False

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected: %s", websocket.client)
    except Exception as e:
        logger.warning("WebSocket exception for client %s: %s", websocket.client, e)
    finally:
        client_tracker.reset()
