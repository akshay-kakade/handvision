import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.websocket import router as api_router, get_detector

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("handvision-ai")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for warm-up and resource cleanup."""
    logger.info("Initializing HandVision AI backend on port %d...", settings.PORT)
    try:
        # Pre-initialize detector during startup
        detector = get_detector()
        if detector.is_initialized:
            logger.info("Hand detector warmed up successfully (Mode: %s)", detector.api_mode)
        else:
            logger.warning("Hand detector initialization deferred or degraded")
    except Exception as e:
        logger.error("Failed to warm up detector: %s", e)

    yield

    logger.info("Shutting down HandVision AI backend...")
    detector = get_detector()
    detector.close()
    logger.info("Detector resources cleaned up.")

app = FastAPI(
    title="HandVision AI Backend",
    description="Real-Time Hand Detection, Tracking & Gesture Recognition API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API and WebSocket routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "app": "HandVision AI",
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/detect"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
