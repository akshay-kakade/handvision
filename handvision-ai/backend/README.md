# HandVision AI — Backend Service

High-performance, real-time hand detection, persistent tracking, and geometric gesture recognition built with FastAPI, OpenCV, and Google MediaPipe.

## Architecture

- **`app/vision/detector.py`**: MediaPipe Hand Landmarker integration supporting CPU inference and multi-hand detection (up to 4 hands).
- **`app/vision/gestures.py`**: Modular, scale-invariant geometric gesture classifier recognizing 6 key gestures + Unknown.
- **`app/vision/tracker.py`**: Persistent hand tracker using bounding-box IoU, normalized center distance, and configurable disappearance timeout.
- **`app/vision/heatmap.py`**: Spatial landmark intensity heatmap generator applying 2D Gaussian kernels.
- **`app/api/websocket.py`**: WebSocket endpoint `/ws/detect` for zero-lag frame streaming with thread-safe inference and per-client tracking state.
- **`app/main.py`**: Application entrypoint with lifecycle warming and CORS.

## Setup & Running

### 1. Create Virtual Environment
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Server
```bash
# Windows / Linux / macOS
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Health check is available at: `http://localhost:8000/health`
Interactive API documentation: `http://localhost:8000/docs`

## Running Tests
```bash
pytest tests/ -v
```
