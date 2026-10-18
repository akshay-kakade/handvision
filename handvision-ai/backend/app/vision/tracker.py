import math
from typing import List, Dict, Tuple, Optional, Any
from ..schemas.detection import BoundingBox, Landmark

def _calculate_iou(box_a: BoundingBox, box_b: BoundingBox) -> float:
    """Computes Intersection over Union (IoU) of two normalized bounding boxes."""
    x_a = max(box_a.x, box_b.x)
    y_a = max(box_a.y, box_b.y)
    x_b = min(box_a.x + box_a.width, box_b.x + box_b.width)
    y_b = min(box_a.y + box_a.height, box_b.y + box_b.height)

    inter_width = max(0.0, x_b - x_a)
    inter_height = max(0.0, y_b - y_a)
    inter_area = inter_width * inter_height

    area_a = max(0.0, box_a.width * box_a.height)
    area_b = max(0.0, box_b.width * box_b.height)
    union_area = area_a + area_b - inter_area

    if union_area <= 1e-6:
        return 0.0
    return inter_area / union_area

def _center_point(landmarks: List[Landmark]) -> Tuple[float, float]:
    """Calculates hand center as the midpoint between wrist (0) and middle MCP (9)."""
    if len(landmarks) > 9:
        cx = (landmarks[0].x + landmarks[9].x) / 2.0
        cy = (landmarks[0].y + landmarks[9].y) / 2.0
        return cx, cy
    elif len(landmarks) > 0:
        return landmarks[0].x, landmarks[0].y
    return 0.5, 0.5

class TrackedHand:
    def __init__(
        self,
        track_id: int,
        center: Tuple[float, float],
        bbox: BoundingBox,
        handedness: Optional[str] = None
    ):
        self.track_id = track_id
        self.center = center
        self.bbox = bbox
        self.handedness = handedness
        self.disappeared = 0

    def update(
        self,
        center: Tuple[float, float],
        bbox: BoundingBox,
        handedness: Optional[str] = None
    ) -> None:
        self.center = center
        self.bbox = bbox
        if handedness is not None:
            self.handedness = handedness
        self.disappeared = 0

class HandTracker:
    """
    Lightweight, persistent multi-hand tracker.
    
    Associates incoming detections across consecutive frames using:
    - Bounding-box IoU (Intersection over Union)
    - Normalized Euclidean distance of hand center
    - Handedness consistency check
    
    Assigns persistent integer IDs and gracefully removes tracks
    when hands leave the camera frame after `max_disappeared` frames.
    
    Known limitations:
    - When two hands overlap heavily or cross paths with identical handedness,
      track identity may swap.
    - Long disappearances beyond `max_disappeared` frames will cause a returning
      hand to be assigned a new ID.
    """
    def __init__(
        self,
        max_disappeared: int = 15,
        max_distance: float = 0.35,
        min_iou: float = 0.15
    ):
        self.next_id = 1
        self.tracks: Dict[int, TrackedHand] = {}
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        self.min_iou = min_iou

    def register(
        self,
        center: Tuple[float, float],
        bbox: BoundingBox,
        handedness: Optional[str] = None
    ) -> int:
        track_id = self.next_id
        self.next_id += 1
        self.tracks[track_id] = TrackedHand(track_id, center, bbox, handedness)
        return track_id

    def deregister(self, track_id: int) -> None:
        if track_id in self.tracks:
            del self.tracks[track_id]

    def reset(self) -> None:
        """Clears all active tracks and resets ID counter."""
        self.tracks.clear()
        self.next_id = 1

    def update(
        self,
        detected_hands: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Updates tracks with the current frame's detections.
        
        Args:
            detected_hands: list of dicts with keys:
                - 'landmarks': List[Landmark]
                - 'bbox': BoundingBox
                - 'handedness': Optional[str]
                
        Returns:
            List of track_ids corresponding to each detected hand in order.
        """
        # If no detections received in this frame
        if len(detected_hands) == 0:
            tracks_to_remove = []
            for track_id, track in self.tracks.items():
                track.disappeared += 1
                if track.disappeared > self.max_disappeared:
                    tracks_to_remove.append(track_id)
            for track_id in tracks_to_remove:
                self.deregister(track_id)
            return []

        # If no existing tracks, register all detections as new
        if len(self.tracks) == 0:
            assigned_ids = []
            for det in detected_hands:
                center = _center_point(det["landmarks"])
                new_id = self.register(center, det["bbox"], det.get("handedness"))
                assigned_ids.append(new_id)
            return assigned_ids

        # Both existing tracks and new detections exist
        track_ids = list(self.tracks.keys())
        det_centers = [_center_point(det["landmarks"]) for det in detected_hands]

        # Build pair cost list
        cost_list: List[Tuple[float, int, int]] = []
        for t_idx, t_id in enumerate(track_ids):
            track = self.tracks[t_id]
            for d_idx, det in enumerate(detected_hands):
                d_center = det_centers[d_idx]
                d_box = det["bbox"]

                # 1. Euclidean distance of centers
                dist = math.hypot(track.center[0] - d_center[0], track.center[1] - d_center[1])
                
                # 2. Bounding box IoU
                iou = _calculate_iou(track.bbox, d_box)

                # 3. Handedness agreement
                hand_penalty = 0.0
                if track.handedness and det.get("handedness"):
                    if track.handedness != det.get("handedness"):
                        hand_penalty = 0.35

                # Cost metric: lower is better
                cost = (1.0 - iou) * 0.5 + min(1.0, dist / self.max_distance) * 0.5 + hand_penalty
                cost_list.append((cost, t_idx, d_idx))

        # Sort candidate matches by lowest cost
        cost_list.sort(key=lambda x: x[0])

        used_tracks = set()
        used_dets = set()
        assigned_map: Dict[int, int] = {}  # detection index -> track_id

        for cost, t_idx, d_idx in cost_list:
            if t_idx in used_tracks or d_idx in used_dets:
                continue

            t_id = track_ids[t_idx]
            track = self.tracks[t_id]
            d_center = det_centers[d_idx]
            dist = math.hypot(track.center[0] - d_center[0], track.center[1] - d_center[1])
            iou = _calculate_iou(track.bbox, detected_hands[d_idx]["bbox"])

            # Gating: must have either close center distance or non-zero IoU
            if dist > self.max_distance and iou < self.min_iou:
                continue

            # Accept match
            track.update(d_center, detected_hands[d_idx]["bbox"], detected_hands[d_idx].get("handedness"))
            used_tracks.add(t_idx)
            used_dets.add(d_idx)
            assigned_map[d_idx] = t_id

        # Any unmatched existing tracks increment disappeared counter
        tracks_to_remove = []
        for t_idx, t_id in enumerate(track_ids):
            if t_idx not in used_tracks:
                self.tracks[t_id].disappeared += 1
                if self.tracks[t_id].disappeared > self.max_disappeared:
                    tracks_to_remove.append(t_id)
        for track_id in tracks_to_remove:
            self.deregister(track_id)

        # Any unmatched new detections register as new tracks
        for d_idx, det in enumerate(detected_hands):
            if d_idx not in used_dets:
                new_id = self.register(
                    det_centers[d_idx],
                    det["bbox"],
                    det.get("handedness")
                )
                assigned_map[d_idx] = new_id

        return [assigned_map[i] for i in range(len(detected_hands))]
