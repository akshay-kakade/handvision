import json
import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "HandVision AI"
    assert data["status"] == "online"

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "detector_initialized" in data
    assert "model_loaded" in data
    assert data["version"] == "1.0.0"

def test_websocket_connect_and_frame(client):
    # Create synthetic test frame
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    _, encoded = cv2.imencode(".jpg", img)
    raw_bytes = encoded.tobytes()

    with client.websocket_connect("/ws/detect") as ws:
        # Send raw image bytes
        ws.send_bytes(raw_bytes)
        response_text = ws.receive_text()
        data = json.loads(response_text)

        assert data["type"] == "detection_result"
        assert "timestamp" in data
        assert "processing_ms" in data
        assert data["frame_width"] == 640
        assert data["frame_height"] == 480
        assert data["hands_detected"] == 0
        assert isinstance(data["hands"], list)

def test_websocket_malformed_payload(client):
    with client.websocket_connect("/ws/detect") as ws:
        # Send garbage binary data (not a valid image)
        ws.send_bytes(b"not_an_image_corrupt_data")
        response_text = ws.receive_json()

        assert response_text["type"] == "error"
        assert "message" in response_text
