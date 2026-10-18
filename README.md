# HandVision AI — Real-Time Hand Detection, Tracking & Gesture Recognition

A real-time computer vision application that combines hand detection, multi-hand tracking, geometric gesture recognition, and interactive visualizations in a web-based interface.

Built with **Python, MediaPipe, OpenCV, FastAPI, React, and TypeScript**, the application processes webcam frames and visualizes detected hands, recognized gestures, and persistent tracking IDs.

Developed for the **Dheera AI Internship Assessment**.

---

## Features

### Core Computer Vision
* **Real-Time Hand Detection:** Detects hands using MediaPipe Hand Landmarker.
* **21 Hand Landmarks:** Extracts hand landmark coordinates for visualization and gesture analysis.
* **Bounding Boxes:** Calculates and displays normalized bounding boxes around detected hands.
* **Multi-Hand Detection:** Supports simultaneous detection of multiple hands (configurable up to 4 hands).
* **Persistent Tracking IDs:** Associates detected hands across frames using an IoU and distance-based tracking algorithm.

### Gesture Recognition
Recognizes common hand gestures using deterministic, scale-invariant geometric rules applied to hand landmarks:

| Gesture | Description |
| :--- | :--- |
| 👍 **Thumbs Up** | Thumb extended vertically while the other four fingers are curled |
| ✌️ **Peace Sign** | Index and middle fingers extended with angular separation ("V" shape) |
| ✋ **Open Palm** | All five fingers extended outward away from the palm |
| ✊ **Fist** | All fingers curled tightly toward the palm with thumb tucked |
| ☝️ **Pointing** | Index finger extended straight while others are curled |
| 🤟 **Three-Finger Gesture** | Three fingers extended (supports both W/3 and Scout/European 3 variants) |
| ❓ **Unknown** | Fallback when no supported gesture confidently matches or during transitions |

*Recognition accuracy depends on hand orientation, lighting, landmark quality, and finger visibility.*

### Interactive Visualizations
Choose between three live visualization modes:
* **Skeleton:** Displays hand landmarks, glowing bone linkage connections, and fingertip indicators.
* **Bounding Boxes:** Highlights detected hands with corner-bracketed boxes and displays persistent tracking IDs and handedness.
* **Heatmap:** Visualizes landmark locations through spatial intensity density using Gaussian radial gradients.

### Video Recording
* Record the live webcam feed composed together with detection overlays.
* Start, stop, and timer tracking directly through the workstation interface.
* Download the processed `.webm` video for later review.

### Performance and Usability
* CPU-based inference without requiring an NVIDIA GPU.
* Browser-based webcam access with mirroring option.
* High-performance WebSocket communication between frontend and backend.
* Telemetry displaying client FPS, backend inference latency (ms), and end-to-end roundtrip time.

---

## Tech Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Programming Language** | Python 3.11 / 3.12 | Computer vision and backend logic |
| **Hand Detection** | MediaPipe | Hand landmark detection model |
| **Image Processing** | OpenCV, NumPy | Frame decoding, color conversion, and vector math |
| **Backend API** | FastAPI | ASGI web framework and routing |
| **Streaming** | WebSockets | Low-latency binary frame transmission and JSON results |
| **Frontend** | React 18, TypeScript | Interactive workstation user interface |
| **Build Tool** | Vite 6 | Development server and production bundling |
| **Styling** | Tailwind CSS | Dark workstation aesthetic and responsive design |
| **Visualization** | HTML Canvas API | Landmarks, skeletons, bounding boxes, and heatmaps |
| **Webcam Feed** | Browser MediaDevices API | Native camera access and stream lifecycle |
| **Recording** | MediaRecorder API | Canvas composition video recording and downloading |
| **Testing** | Pytest | Automated unit and integration test suite |

---

## Architecture

```text
┌────────────────────────────────────────────────────────┐
│                     React Frontend                     │
│                                                        │
│  Webcam Feed │ Canvas Overlay │ Controls │ Telemetry   │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ WebSocket (/ws/detect)
                            │ Binary Webcam Frames
                            ▼
┌────────────────────────────────────────────────────────┐
│                    FastAPI Backend                     │
│                                                        │
│  Frame Decoding (OpenCV) │ Async Concurrency Lock      │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                 MediaPipe Hand Landmarker              │
│                                                        │
│  CPU Inference │ 21 3D Landmarks │ Handedness Labels   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                Computer Vision Pipeline                │
│                                                        │
│  Scale-Invariant Gesture Recognizer                    │
│  Multi-Hand Persistent Tracker (IoU + Centroid)        │
│  Bounding Box Generator                                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Structured Results                   │
│                                                        │
│  Landmarks │ Track IDs │ Gestures │ Latency Metrics    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Frontend Rendering                   │
│                                                        │
│  Skeleton │ Bounding Boxes │ Heatmap │ Composed Video  │
└────────────────────────────────────────────────────────┘
```

---

## Project Structure

```text
handvision-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── websocket.py         # WebSocket /ws/detect and /health
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── detection.py         # Pydantic v2 schemas
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── image_processing.py  # Frame decoding and resizing
│   │   ├── vision/
│   │   │   ├── __init__.py
│   │   │   ├── detector.py          # MediaPipe Hand Landmarker
│   │   │   ├── gestures.py          # Geometric gesture classifier
│   │   │   ├── tracker.py           # Persistent multi-hand tracker
│   │   │   └── heatmap.py           # Gaussian spatial heatmap
│   │   ├── config.py                # Environment configuration
│   │   └── main.py                  # FastAPI entry point
│   ├── tests/
│   │   ├── test_detection_schema.py # Schema tests
│   │   ├── test_gestures.py         # Gesture unit tests
│   │   ├── test_integration.py      # Health & WebSocket tests
│   │   └── test_tracker.py          # Tracking unit tests
│   ├── pytest.ini
│   ├── requirements.txt             # Pinned backend dependencies
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CameraView.tsx       # Aligned canvas & video feed
│   │   │   ├── ControlPanel.tsx     # Workstation controls
│   │   │   ├── DetectionModeSelector.tsx # Mode selector
│   │   │   ├── GesturePanel.tsx     # Active hand & gesture cards
│   │   │   ├── StatsPanel.tsx       # Latency, FPS, telemetry
│   │   │   └── StatusIndicator.tsx  # Socket & Camera pills
│   │   ├── hooks/
│   │   │   ├── useDetectionSocket.ts# Low-latency WebSocket client
│   │   │   ├── useRecorder.ts       # Canvas composed MediaRecorder
│   │   │   └── useWebcam.ts         # Camera lifecycle
│   │   ├── types/
│   │   │   └── detection.ts         # TypeScript definitions
│   │   ├── utils/
│   │   │   ├── drawing.ts           # Skeletons, bounding boxes, heatmaps
│   │   │   └── recording.ts         # Recording utilities
│   │   ├── App.tsx                  # Workstation layout
│   │   ├── index.css                # Dark theme styling
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── screenshots/                     # Directory for demo screenshots
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

Install the following on your system:
* **Python**: Version `3.11` or `3.12`.
* **Node.js**: Version `18+` or `20+` with `npm`.
* **Git**: Installed and available in your terminal.
* **Webcam**: Built-in laptop webcam or USB camera.

**Hardware Note:** The application is designed for standard CPU execution. A dedicated GPU is not required.

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/handvision-ai.git
cd handvision-ai
```

---

### 2. Set Up and Run the Backend (Terminal 1)

#### Windows (PowerShell)
```powershell
cd backend

# Create virtual environment
py -3.12 -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Linux / macOS (Bash)
```bash
cd backend

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> **Model Setup:** On first launch, the backend automatically downloads the official Google MediaPipe task model (`hand_landmarker.task`, 7.8 MB) and caches it locally in `backend/models/`. It will not redownload on subsequent startups.

#### Verify the Backend
* **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) (reports `status: "healthy"` and model readiness)
* **Interactive API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 3. Set Up and Run the Frontend (Terminal 2)

Open a **second terminal window**:

```bash
cd frontend

# Install node dependencies
npm install

# Start development server
npm run dev
```

Open your browser at:
**[http://localhost:5173](http://localhost:5173)**

Allow webcam access when prompted by your browser.

---

## Running Tests

Activate the backend virtual environment, then execute Pytest:

```powershell
cd backend
pytest tests/ -v
```

All 23 automated unit and integration tests validate:
- Gesture classification accuracy for all 6 gestures and invalid landmark inputs.
- Multi-hand tracking persistence, disappearance recovery, and timeout cleanup.
- Detection schemas, bounding box bounds, and `/health` output.
- WebSocket frame decoding and error recovery.

To verify frontend TypeScript types and build:

```bash
cd frontend
npm run build
```

---

## Usage

1. Start both the backend and frontend servers.
2. Open **`http://localhost:5173`** in your browser.
3. Click **"Initialize Webcam"** and grant camera permissions.
4. Place one or more hands in the camera view.
5. View detected landmarks, bounding boxes, tracking IDs, and recognized gestures.
6. Switch between **Skeleton**, **Bounding Boxes**, and **Heatmap** modes.
7. Click **"Start Recording"** to capture video with overlays, then **"Stop Recording"** and **"Download Video"**.
8. Toggle **"Mirror Camera Feed"** for a natural mirrored experience.

---

## Implementation Details

### Gesture Recognition
Gesture classification uses geometric heuristics applied to hand landmarks rather than a separately trained neural network.
- **Scale Invariance:** Distances and curl thresholds are normalized by the dynamic palm scale $S = \text{distance}(\text{Wrist}, \text{Middle MCP})$, ensuring consistent recognition regardless of hand distance from the camera.
- **Degenerate Palm Gating:** Hands with collapsed or invalid geometry are safely assigned to `Unknown`.

### Multi-Hand Tracking
The tracking module associates incoming detections across consecutive frames to maintain persistent integer IDs:
- Computes pair-matching costs combining normalized Euclidean center distance and bounding box IoU.
- Retains tracks during temporary dropouts for up to 15 missing frames (`TRACK_MAX_DISAPPEARED`).
- Handles reordered detections and prevents duplicate ID assignments in the same frame.

### Heatmap Visualization
Renders a spatial intensity density map based on detected landmark positions:
- Uses 2D Gaussian kernels placing higher intensity weights on fingertips and palm centers.
- Visualized on the frontend using hardware-accelerated radial gradients and additive composite blending.

### Video Recording
The browser's `MediaRecorder` API captures a composite canvas at 30 FPS merging the webcam video stream and overlay graphics simultaneously, producing a downloadable `.webm` file.

---

## Known Limitations

* **Extreme Hand Rotations:** Lateral or upside-down orientations may report `Unknown` if vertical finger alignment is lost.
* **Hand Overlaps:** Direct co-planar overlapping hands may temporarily merge into a single detection until separation occurs.
* **Hardware Variations:** Inference latency depends on laptop CPU performance and the number of visible hands.
* **Lighting & Occlusion:** Dim environments or fingers occluded by the palm can lower landmark confidence.

---

## AI-Assisted Development

AI coding assistance was used for scaffolding, algorithmic formulation, and test coverage generation:
* **Tool Used:** Google Antigravity (Powered by Gemini 3.8 Flash High).
* **Applied Areas:** Derivation of scale-invariant geometric rules, async WebSocket concurrency architecture, offscreen canvas recording pipeline, and synthetic landmark test fixtures.
* **Validation:** All generated logic was executed, tested (23/23 Pytest passed), type-checked, and validated on live webcam streams.

---

## Screenshots and Demo

### Demo Video
<!-- Paste your 1-2 minute video link below -->
**Demo video:** 

---

### Screenshots

<!-- Add your application screenshots below -->

#### Skeleton Mode
<!-- Image placeholder for Skeleton Mode -->


#### Bounding Box Mode
<!-- Image placeholder for Bounding Box Mode -->


#### Heatmap Mode
<!-- Image placeholder for Heatmap Mode -->


---

## Internship Assessment

Developed as part of the **Dheera AI Internship Assessment — Hand Detection and Tracking System**.

The project demonstrates real-time computer vision, low-latency WebSocket streaming, modular geometric gesture recognition, persistent multi-hand tracking, and interactive browser visualization.

---

## License

MIT License — see [LICENSE](LICENSE) for details.#   h a n d v i s i o n  
 