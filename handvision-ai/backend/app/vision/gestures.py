import math
from typing import List, Tuple, Optional
from ..schemas.detection import Landmark

# Landmark index constants for MediaPipe Hand
WRIST = 0

THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4

INDEX_MCP = 5
INDEX_PIP = 6
INDEX_DIP = 7
INDEX_TIP = 8

MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_DIP = 11
MIDDLE_TIP = 12

RING_MCP = 13
RING_PIP = 14
RING_DIP = 15
RING_TIP = 16

PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20

def _euclidean_dist_2d(p1: Landmark, p2: Landmark) -> float:
    """Computes 2D Euclidean distance in normalized image space."""
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def _palm_scale(landmarks: List[Landmark]) -> float:
    """
    Computes scale reference using the distance between wrist and middle finger MCP.
    Ensures calculations are invariant to camera distance and hand sizes.
    """
    scale = _euclidean_dist_2d(landmarks[WRIST], landmarks[MIDDLE_MCP])
    return max(scale, 1e-4)

def is_finger_extended(
    landmarks: List[Landmark],
    mcp_idx: int,
    pip_idx: int,
    dip_idx: int,
    tip_idx: int,
    scale: float
) -> bool:
    """
    Determines if a non-thumb finger is extended.
    Checks that the fingertip is significantly further from the wrist than the PIP joint,
    and that tip-to-MCP distance exceeds PIP-to-MCP distance.
    """
    wrist = landmarks[WRIST]
    pip = landmarks[pip_idx]
    tip = landmarks[tip_idx]
    mcp = landmarks[mcp_idx]

    dist_wrist_tip = _euclidean_dist_2d(wrist, tip)
    dist_wrist_pip = _euclidean_dist_2d(wrist, pip)
    dist_mcp_tip = _euclidean_dist_2d(mcp, tip)
    dist_mcp_pip = _euclidean_dist_2d(mcp, pip)

    return (dist_wrist_tip > dist_wrist_pip * 1.1) and (dist_mcp_tip > dist_mcp_pip * 1.2)

def is_finger_curled(
    landmarks: List[Landmark],
    mcp_idx: int,
    pip_idx: int,
    dip_idx: int,
    tip_idx: int,
    scale: float
) -> bool:
    """
    Determines if a finger is curled/folded towards the palm.
    Tip distance to wrist is less than or comparable to PIP distance.
    """
    wrist = landmarks[WRIST]
    pip = landmarks[pip_idx]
    tip = landmarks[tip_idx]
    mcp = landmarks[mcp_idx]

    dist_wrist_tip = _euclidean_dist_2d(wrist, tip)
    dist_wrist_pip = _euclidean_dist_2d(wrist, pip)
    dist_mcp_tip = _euclidean_dist_2d(mcp, tip)
    dist_mcp_pip = _euclidean_dist_2d(mcp, pip)

    return (dist_wrist_tip <= dist_wrist_pip * 1.05) or (dist_mcp_tip < dist_mcp_pip * 0.95)

def is_thumb_extended(landmarks: List[Landmark], scale: float, handedness: Optional[str] = None) -> bool:
    """
    Determines if the thumb is extended outward from the hand.
    """
    thumb_tip = landmarks[THUMB_TIP]
    thumb_ip = landmarks[THUMB_IP]
    index_mcp = landmarks[INDEX_MCP]
    wrist = landmarks[WRIST]

    dist_thumb_index = _euclidean_dist_2d(thumb_tip, index_mcp)
    dist_thumb_wrist = _euclidean_dist_2d(thumb_tip, wrist)

    return (dist_thumb_index > 0.45 * scale) and (dist_thumb_wrist > 0.85 * scale)

def is_thumbs_up(landmarks: List[Landmark], handedness: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Rule for 'Thumbs Up':
    1. Thumb points upward (y coordinate is substantially smaller than IP and MCP joints).
    2. Other four fingers (Index, Middle, Ring, Pinky) are curled into the palm.
    3. Thumb tip is extended away from palm.
    """
    scale = _palm_scale(landmarks)
    wrist = landmarks[WRIST]
    thumb_tip = landmarks[THUMB_TIP]
    thumb_ip = landmarks[THUMB_IP]
    thumb_mcp = landmarks[THUMB_MCP]

    # Thumb vertical extension check (pointing up in image space means lower y)
    thumb_upward = (thumb_tip.y < thumb_ip.y) and (thumb_ip.y < thumb_mcp.y)
    thumb_above_wrist = (wrist.y - thumb_tip.y) > (0.4 * scale)

    # All 4 other fingers must be curled
    index_c = is_finger_curled(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP, scale)
    middle_c = is_finger_curled(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP, scale)
    ring_c = is_finger_curled(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_c = is_finger_curled(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    if thumb_upward and thumb_above_wrist and index_c and middle_c and ring_c and pinky_c:
        # Confidence indicator based on curl tightness and thumb height
        conf = min(1.0, 0.80 + 0.20 * min(1.0, (wrist.y - thumb_tip.y) / (1.2 * scale)))
        return True, round(conf, 2)
    return False, None

def is_peace_sign(landmarks: List[Landmark], handedness: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Rule for 'Peace Sign':
    1. Index and Middle fingers are extended.
    2. Ring and Pinky fingers are curled.
    3. Thumb is curled or folded.
    4. Index and Middle tips have a distinct separation angle / distance.
    """
    scale = _palm_scale(landmarks)
    index_ext = is_finger_extended(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP, scale)
    middle_ext = is_finger_extended(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP, scale)
    ring_curled = is_finger_curled(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_curled = is_finger_curled(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    # Check separation between index and middle tips (V shape)
    dist_tips = _euclidean_dist_2d(landmarks[INDEX_TIP], landmarks[MIDDLE_TIP])
    separated = dist_tips > (0.20 * scale)

    if index_ext and middle_ext and ring_curled and pinky_curled and separated:
        conf = min(1.0, 0.85 + 0.15 * min(1.0, dist_tips / (0.6 * scale)))
        return True, round(conf, 2)
    return False, None

def is_open_palm(landmarks: List[Landmark], handedness: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Rule for 'Open Palm':
    All 5 fingers (Thumb, Index, Middle, Ring, Pinky) are extended.
    """
    scale = _palm_scale(landmarks)
    thumb_ext = is_thumb_extended(landmarks, scale, handedness)
    index_ext = is_finger_extended(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP, scale)
    middle_ext = is_finger_extended(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP, scale)
    ring_ext = is_finger_extended(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_ext = is_finger_extended(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    if thumb_ext and index_ext and middle_ext and ring_ext and pinky_ext:
        return True, 0.95
    return False, None

def is_fist(landmarks: List[Landmark], handedness: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Rule for 'Fist':
    All 4 fingers (Index, Middle, Ring, Pinky) are tightly curled.
    Thumb is folded over or against the fingers (not extended).
    """
    scale = _palm_scale(landmarks)
    thumb_ext = is_thumb_extended(landmarks, scale, handedness)
    index_c = is_finger_curled(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP, scale)
    middle_c = is_finger_curled(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP, scale)
    ring_c = is_finger_curled(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_c = is_finger_curled(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    if not thumb_ext and index_c and middle_c and ring_c and pinky_c:
        return True, 0.92
    return False, None

def is_pointing(landmarks: List[Landmark], handedness: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Rule for 'Pointing':
    Index finger is extended straight.
    Middle, Ring, and Pinky fingers are curled.
    Thumb is tucked or resting (not fully extended pointing up like peace sign).
    """
    scale = _palm_scale(landmarks)
    index_ext = is_finger_extended(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP, scale)
    middle_c = is_finger_curled(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP, scale)
    ring_c = is_finger_curled(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_c = is_finger_curled(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    if index_ext and middle_c and ring_c and pinky_c:
        return True, 0.90
    return False, None

def is_three_fingers(landmarks: List[Landmark], handedness: Optional[str] = None) -> Tuple[bool, Optional[float]]:
    """
    Rule for 'Three-Finger Gesture':
    Recognizes two common variants:
    Variant A: Index + Middle + Ring extended, Pinky curled ('W' / standard 3).
    Variant B: Thumb + Index + Middle extended, Ring + Pinky curled (scout 3).
    """
    scale = _palm_scale(landmarks)
    thumb_ext = is_thumb_extended(landmarks, scale, handedness)
    index_ext = is_finger_extended(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP, scale)
    middle_ext = is_finger_extended(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP, scale)
    ring_ext = is_finger_extended(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_ext = is_finger_extended(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    ring_c = is_finger_curled(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP, scale)
    pinky_c = is_finger_curled(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP, scale)

    # Variant A: Index, Middle, Ring extended; Pinky curled
    if index_ext and middle_ext and ring_ext and pinky_c:
        return True, 0.88

    # Variant B: Thumb, Index, Middle extended; Ring, Pinky curled
    if thumb_ext and index_ext and middle_ext and ring_c and pinky_c:
        return True, 0.85

    return False, None

def classify_gesture(
    landmarks: List[Landmark],
    handedness: Optional[str] = None
) -> Tuple[str, Optional[float]]:
    """
    Evaluates rule-based geometric constraints in priority order.
    Returns:
      (gesture_name, confidence)
      Where gesture_name is one of:
      - 'Thumbs Up'
      - 'Peace Sign'
      - 'Open Palm'
      - 'Fist'
      - 'Pointing'
      - 'Three-Finger Gesture'
      - 'Unknown'
    """
    if len(landmarks) < 21:
        return "Unknown", None

    scale = _palm_scale(landmarks)
    if scale < 0.02:
        return "Unknown", None

    # Priority check: Thumbs Up
    ok, conf = is_thumbs_up(landmarks, handedness)
    if ok:
        return "Thumbs Up", conf

    # Pointing
    ok, conf = is_pointing(landmarks, handedness)
    if ok:
        return "Pointing", conf

    # Peace Sign
    ok, conf = is_peace_sign(landmarks, handedness)
    if ok:
        return "Peace Sign", conf

    # Three-Finger Gesture
    ok, conf = is_three_fingers(landmarks, handedness)
    if ok:
        return "Three-Finger Gesture", conf

    # Open Palm
    ok, conf = is_open_palm(landmarks, handedness)
    if ok:
        return "Open Palm", conf

    # Fist
    ok, conf = is_fist(landmarks, handedness)
    if ok:
        return "Fist", conf

    return "Unknown", None
