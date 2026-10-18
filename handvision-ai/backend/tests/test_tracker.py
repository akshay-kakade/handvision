import pytest
from app.schemas.detection import BoundingBox, Landmark
from app.vision.tracker import HandTracker

def make_dummy_hand(cx: float, cy: float, handedness: str = "Right") -> dict:
    """Creates a synthetic detected hand dict around a given center point."""
    lms = []
    # Point 0: wrist
    lms.append(Landmark(x=cx, y=cy + 0.1, z=0.0))
    # Points 1 to 8
    for _ in range(8):
        lms.append(Landmark(x=cx, y=cy, z=0.0))
    # Point 9: middle MCP
    lms.append(Landmark(x=cx, y=cy - 0.1, z=0.0))
    # Points 10 to 20
    for _ in range(11):
        lms.append(Landmark(x=cx, y=cy - 0.15, z=0.0))

    box = BoundingBox(
        x=max(0.0, cx - 0.1),
        y=max(0.0, cy - 0.15),
        width=0.2,
        height=0.3
    )

    return {
        "landmarks": lms,
        "bbox": box,
        "handedness": handedness,
        "handedness_confidence": 0.95
    }

def test_assign_new_id():
    tracker = HandTracker()
    hand = make_dummy_hand(0.5, 0.5)
    ids = tracker.update([hand])

    assert len(ids) == 1
    assert ids[0] == 1
    assert 1 in tracker.tracks

def test_preserve_id_during_movement():
    tracker = HandTracker()
    # Frame 1: Hand at (0.5, 0.5)
    ids_f1 = tracker.update([make_dummy_hand(0.5, 0.5)])
    assert ids_f1 == [1]

    # Frame 2: Hand moves smoothly to (0.52, 0.52)
    ids_f2 = tracker.update([make_dummy_hand(0.52, 0.52)])
    assert ids_f2 == [1]

    # Frame 3: Hand moves to (0.54, 0.53)
    ids_f3 = tracker.update([make_dummy_hand(0.54, 0.53)])
    assert ids_f3 == [1]

def test_track_two_hands_simultaneously():
    tracker = HandTracker()
    hand_left = make_dummy_hand(0.3, 0.5, handedness="Left")
    hand_right = make_dummy_hand(0.7, 0.5, handedness="Right")

    # Frame 1: Both hands present
    ids_f1 = tracker.update([hand_left, hand_right])
    assert len(ids_f1) == 2
    assert ids_f1[0] != ids_f1[1]

    # Frame 2: Both move slightly
    hand_left_moved = make_dummy_hand(0.32, 0.51, handedness="Left")
    hand_right_moved = make_dummy_hand(0.68, 0.49, handedness="Right")
    ids_f2 = tracker.update([hand_left_moved, hand_right_moved])

    assert ids_f2 == ids_f1

def test_handle_reordered_detections():
    tracker = HandTracker()
    hand_a = make_dummy_hand(0.2, 0.5, handedness="Left")
    hand_b = make_dummy_hand(0.8, 0.5, handedness="Right")

    ids_f1 = tracker.update([hand_a, hand_b])
    id_a, id_b = ids_f1[0], ids_f1[1]

    # In next frame, detector returns hand_b first, hand_a second
    ids_f2 = tracker.update([
        make_dummy_hand(0.79, 0.51, handedness="Right"),
        make_dummy_hand(0.21, 0.49, handedness="Left")
    ])

    # Should match correct tracks regardless of index order
    assert ids_f2[0] == id_b
    assert ids_f2[1] == id_a

def test_handle_temporary_missing_detection():
    tracker = HandTracker(max_disappeared=5)
    hand = make_dummy_hand(0.5, 0.5)

    # Frame 1: Hand detected
    ids_f1 = tracker.update([hand])
    assert ids_f1 == [1]

    # Frame 2 & 3: Detection temporarily lost (e.g. motion blur)
    tracker.update([])
    tracker.update([])

    # Track still exists (disappeared count = 2)
    assert 1 in tracker.tracks
    assert tracker.tracks[1].disappeared == 2

    # Frame 4: Hand re-appears near previous position
    ids_f4 = tracker.update([make_dummy_hand(0.51, 0.51)])
    assert ids_f4 == [1]
    assert tracker.tracks[1].disappeared == 0

def test_remove_stale_tracks():
    tracker = HandTracker(max_disappeared=3)
    tracker.update([make_dummy_hand(0.5, 0.5)])
    assert 1 in tracker.tracks

    # Miss 4 consecutive frames (exceeding max_disappeared=3)
    tracker.update([])
    tracker.update([])
    tracker.update([])
    tracker.update([])

    # Track 1 should be removed
    assert 1 not in tracker.tracks

def test_assign_id_to_newly_appearing_hand():
    tracker = HandTracker()
    # Start with 1 hand
    ids_f1 = tracker.update([make_dummy_hand(0.3, 0.5)])
    assert ids_f1 == [1]

    # Second hand appears in another part of screen
    ids_f2 = tracker.update([
        make_dummy_hand(0.31, 0.51),
        make_dummy_hand(0.80, 0.50)
    ])
    assert len(ids_f2) == 2
    assert ids_f2[0] == 1
    assert ids_f2[1] == 2
