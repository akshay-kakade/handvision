import os
from pathlib import Path
from pydantic import BaseModel, Field

class Settings(BaseModel):
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    # Hand detection settings
    MAX_HANDS: int = int(os.getenv("MAX_HANDS", "4"))
    MIN_DETECTION_CONFIDENCE: float = float(os.getenv("MIN_DETECTION_CONFIDENCE", "0.5"))
    MIN_PRESENCE_CONFIDENCE: float = float(os.getenv("MIN_PRESENCE_CONFIDENCE", "0.5"))
    MIN_TRACKING_CONFIDENCE: float = float(os.getenv("MIN_TRACKING_CONFIDENCE", "0.5"))

    # Tracking parameters
    TRACK_MAX_DISAPPEARED: int = int(os.getenv("TRACK_MAX_DISAPPEARED", "15"))
    TRACK_DISTANCE_THRESHOLD: float = float(os.getenv("TRACK_DISTANCE_THRESHOLD", "0.25"))
    TRACK_IOU_THRESHOLD: float = float(os.getenv("TRACK_IOU_THRESHOLD", "0.2"))

    # Frame processing
    MAX_FRAME_WIDTH: int = int(os.getenv("MAX_FRAME_WIDTH", "640"))
    MAX_FRAME_HEIGHT: int = int(os.getenv("MAX_FRAME_HEIGHT", "480"))

    # MediaPipe Task Model Asset
    # Official Google MediaPipe Hand Landmarker model url:
    MODEL_URL: str = (
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        "hand_landmarker/float16/1/hand_landmarker.task"
    )
    # Stored locally inside backend/models
    MODEL_DIR: Path = Path(__file__).resolve().parent.parent / "models"
    MODEL_FILENAME: str = "hand_landmarker.task"

    @property
    def MODEL_PATH(self) -> Path:
        return self.MODEL_DIR / self.MODEL_FILENAME

settings = Settings()
