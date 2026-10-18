import pytest
from app.schemas.detection import Landmark
from app.vision.gestures import (
    classify_gesture,
    is_thumbs_up,
    is_peace_sign,
    is_open_palm,
    is_fist,
    is_pointing,
    is_three_fingers,
)

def create_base_hand(wrist=(0.5, 0.8, 0.0), scale=0.2) -> list[Landmark]:
    """Creates a default baseline 21-landmark hand centered at wrist."""
    wx, wy, wz = wrist
    lms = []
    for _ in range(21):
        lms.append(Landmark(x=wx, y=wy, z=wz))
    # Set middle MCP (index 9) to establish palm scale
    lms[9] = Landmark(x=wx, y=wy - scale, z=wz)
    return lms

def make_open_palm_fixture() -> list[Landmark]:
    """Generates synthetic landmarks for Open Palm (all 5 fingers extended outward)."""
    lms = create_base_hand()
    # Wrist
    lms[0] = Landmark(x=0.5, y=0.8, z=0.0)

    # Thumb: extending left/up
    lms[1] = Landmark(x=0.45, y=0.75, z=0.0)
    lms[2] = Landmark(x=0.40, y=0.70, z=0.0)
    lms[3] = Landmark(x=0.35, y=0.65, z=0.0)
    lms[4] = Landmark(x=0.30, y=0.60, z=0.0)  # Tip far from index MCP

    # Index: extended straight up
    lms[5] = Landmark(x=0.42, y=0.60, z=0.0)  # MCP
    lms[6] = Landmark(x=0.42, y=0.50, z=0.0)  # PIP
    lms[7] = Landmark(x=0.42, y=0.40, z=0.0)  # DIP
    lms[8] = Landmark(x=0.42, y=0.30, z=0.0)  # TIP

    # Middle: extended straight up
    lms[9] = Landmark(x=0.50, y=0.58, z=0.0)  # MCP
    lms[10] = Landmark(x=0.50, y=0.48, z=0.0)  # PIP
    lms[11] = Landmark(x=0.50, y=0.38, z=0.0)  # DIP
    lms[12] = Landmark(x=0.50, y=0.28, z=0.0)  # TIP

    # Ring: extended straight up
    lms[13] = Landmark(x=0.58, y=0.60, z=0.0)  # MCP
    lms[14] = Landmark(x=0.58, y=0.50, z=0.0)  # PIP
    lms[15] = Landmark(x=0.58, y=0.40, z=0.0)  # DIP
    lms[16] = Landmark(x=0.58, y=0.30, z=0.0)  # TIP

    # Pinky: extended straight up
    lms[17] = Landmark(x=0.65, y=0.65, z=0.0)  # MCP
    lms[18] = Landmark(x=0.65, y=0.55, z=0.0)  # PIP
    lms[19] = Landmark(x=0.65, y=0.45, z=0.0)  # DIP
    lms[20] = Landmark(x=0.65, y=0.35, z=0.0)  # TIP

    return lms

def make_fist_fixture() -> list[Landmark]:
    """Generates synthetic landmarks for Fist (all 5 fingers curled)."""
    lms = create_base_hand()
    lms[0] = Landmark(x=0.5, y=0.8, z=0.0)

    # Thumb curled over palm
    lms[1] = Landmark(x=0.46, y=0.76, z=0.0)
    lms[2] = Landmark(x=0.44, y=0.72, z=0.0)
    lms[3] = Landmark(x=0.46, y=0.70, z=0.0)
    lms[4] = Landmark(x=0.48, y=0.70, z=0.0)  # Tip tucked

    # Index curled
    lms[5] = Landmark(x=0.44, y=0.65, z=0.0)
    lms[6] = Landmark(x=0.44, y=0.58, z=0.0)
    lms[7] = Landmark(x=0.46, y=0.62, z=0.0)
    lms[8] = Landmark(x=0.46, y=0.68, z=0.0)  # Tip curled back down toward wrist

    # Middle curled
    lms[9] = Landmark(x=0.50, y=0.63, z=0.0)
    lms[10] = Landmark(x=0.50, y=0.56, z=0.0)
    lms[11] = Landmark(x=0.50, y=0.62, z=0.0)
    lms[12] = Landmark(x=0.50, y=0.68, z=0.0)

    # Ring curled
    lms[13] = Landmark(x=0.56, y=0.65, z=0.0)
    lms[14] = Landmark(x=0.56, y=0.58, z=0.0)
    lms[15] = Landmark(x=0.56, y=0.62, z=0.0)
    lms[16] = Landmark(x=0.56, y=0.68, z=0.0)

    # Pinky curled
    lms[17] = Landmark(x=0.62, y=0.68, z=0.0)
    lms[18] = Landmark(x=0.62, y=0.61, z=0.0)
    lms[19] = Landmark(x=0.62, y=0.65, z=0.0)
    lms[20] = Landmark(x=0.62, y=0.70, z=0.0)

    return lms

def make_thumbs_up_fixture() -> list[Landmark]:
    """Generates synthetic landmarks for Thumbs Up (thumb pointing up, fingers curled)."""
    lms = make_fist_fixture()
    # Thumb pointing upward
    lms[1] = Landmark(x=0.42, y=0.70, z=0.0)
    lms[2] = Landmark(x=0.40, y=0.60, z=0.0)
    lms[3] = Landmark(x=0.38, y=0.48, z=0.0)
    lms[4] = Landmark(x=0.38, y=0.35, z=0.0)  # High thumb tip
    return lms

def make_pointing_fixture() -> list[Landmark]:
    """Generates synthetic landmarks for Pointing (Index extended, others curled)."""
    lms = make_fist_fixture()
    # Extend index finger straight up
    lms[5] = Landmark(x=0.44, y=0.62, z=0.0)
    lms[6] = Landmark(x=0.44, y=0.50, z=0.0)
    lms[7] = Landmark(x=0.44, y=0.40, z=0.0)
    lms[8] = Landmark(x=0.44, y=0.28, z=0.0)
    return lms

def make_peace_sign_fixture() -> list[Landmark]:
    """Generates synthetic landmarks for Peace Sign (Index & Middle extended with separation, others curled)."""
    lms = make_fist_fixture()
    # Index extended pointing slightly left
    lms[5] = Landmark(x=0.44, y=0.62, z=0.0)
    lms[6] = Landmark(x=0.40, y=0.50, z=0.0)
    lms[7] = Landmark(x=0.36, y=0.40, z=0.0)
    lms[8] = Landmark(x=0.32, y=0.30, z=0.0)

    # Middle extended pointing slightly right
    lms[9] = Landmark(x=0.50, y=0.60, z=0.0)
    lms[10] = Landmark(x=0.52, y=0.48, z=0.0)
    lms[11] = Landmark(x=0.55, y=0.38, z=0.0)
    lms[12] = Landmark(x=0.58, y=0.28, z=0.0)

    return lms

def make_three_fingers_fixture() -> list[Landmark]:
    """Generates synthetic landmarks for Three-Finger Gesture (Index, Middle, Ring extended)."""
    lms = make_peace_sign_fixture()
    # Also extend Ring finger
    lms[13] = Landmark(x=0.56, y=0.62, z=0.0)
    lms[14] = Landmark(x=0.62, y=0.50, z=0.0)
    lms[15] = Landmark(x=0.66, y=0.40, z=0.0)
    lms[16] = Landmark(x=0.70, y=0.30, z=0.0)
    return lms

def test_thumbs_up_recognition():
    lms = make_thumbs_up_fixture()
    gesture, conf = classify_gesture(lms)
    assert gesture == "Thumbs Up"
    assert conf is not None and conf > 0.7

def test_peace_sign_recognition():
    lms = make_peace_sign_fixture()
    gesture, conf = classify_gesture(lms)
    assert gesture == "Peace Sign"
    assert conf is not None and conf > 0.7

def test_open_palm_recognition():
    lms = make_open_palm_fixture()
    gesture, conf = classify_gesture(lms)
    assert gesture == "Open Palm"
    assert conf is not None and conf >= 0.9

def test_fist_recognition():
    lms = make_fist_fixture()
    gesture, conf = classify_gesture(lms)
    assert gesture == "Fist"
    assert conf is not None and conf >= 0.85

def test_pointing_recognition():
    lms = make_pointing_fixture()
    gesture, conf = classify_gesture(lms)
    assert gesture == "Pointing"
    assert conf is not None and conf >= 0.8

def test_three_fingers_recognition():
    lms = make_three_fingers_fixture()
    gesture, conf = classify_gesture(lms)
    assert gesture == "Three-Finger Gesture"
    assert conf is not None and conf >= 0.8

def test_unknown_or_invalid_landmarks():
    # Empty list
    gesture, conf = classify_gesture([])
    assert gesture == "Unknown"
    assert conf is None

    # Partial landmarks (< 21)
    gesture, conf = classify_gesture([Landmark(x=0.5, y=0.5, z=0.0)] * 10)
    assert gesture == "Unknown"
    assert conf is None

    # Ambiguous input (e.g. all points at exactly 0.5)
    gesture, _ = classify_gesture([Landmark(x=0.5, y=0.5, z=0.0)] * 21)
    assert gesture == "Unknown"
