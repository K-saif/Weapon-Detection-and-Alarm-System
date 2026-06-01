"""Tracking state manager for lifecycle decisions."""

import time
from collections import defaultdict
from typing import Sequence


def _iou(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    """Computes intersection-over-union for two xyxy boxes."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union_area = area_a + area_b - inter_area
    if union_area <= 0.0:
        return 0.0
    return inter_area / union_area


def _center_distance(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    """Computes normalized center distance between two xyxy boxes."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    ax = (ax1 + ax2) / 2.0
    ay = (ay1 + ay2) / 2.0
    bx = (bx1 + bx2) / 2.0
    by = (by1 + by2) / 2.0

    aw = max(1.0, ax2 - ax1)
    ah = max(1.0, ay2 - ay1)
    bw = max(1.0, bx2 - bx1)
    bh = max(1.0, by2 - by1)
    scale = max(aw, ah, bw, bh)
    return (((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5) / scale


class TrackLifecycle:
    """Track-level persistence, cooldown, and stale-state management."""

    def __init__(self, persist_frames: int, cooldown_seconds: int, stale_frames: int) -> None:
        self.persist_frames = persist_frames
        self.cooldown_seconds = cooldown_seconds
        self.stale_frames = stale_frames
        self.persistence_count: dict[int, int] = defaultdict(int)
        self.last_seen_frame: dict[int, int] = {}
        self.last_alert_time: dict[int, float] = {}
        self.track_boxes: dict[int, tuple[float, float, float, float]] = {}
        self.track_classes: dict[int, int] = {}
        self.raw_to_stable: dict[int, int] = {}
        self.active_by_class: dict[int, int] = {}
        self.next_stable_id = 1

    def assign_stable_id(
        self,
        raw_track_id: int,
        frame_number: int,
        box_xyxy: Sequence[float],
        class_id: int,
    ) -> int:
        """Maps the tracker id onto a stable logical id for the same object."""
        active_stable_id = self.raw_to_stable.get(raw_track_id)
        if active_stable_id is not None and active_stable_id in self.track_boxes:
            self.update_seen(active_stable_id, frame_number)
            self.track_boxes[active_stable_id] = tuple(float(coord) for coord in box_xyxy)
            self.track_classes[active_stable_id] = class_id
            self.active_by_class[class_id] = active_stable_id
            return active_stable_id

        class_active_id = self.active_by_class.get(class_id)
        if class_active_id is not None and class_active_id in self.track_boxes:
            self.raw_to_stable[raw_track_id] = class_active_id
            self.track_boxes[class_active_id] = tuple(float(coord) for coord in box_xyxy)
            self.track_classes[class_active_id] = class_id
            self.update_seen(class_active_id, frame_number)
            return class_active_id

        best_track_id: int | None = None
        best_iou = 0.0
        best_distance = float("inf")
        candidate_box = tuple(float(coord) for coord in box_xyxy)

        for stable_id, previous_box in self.track_boxes.items():
            if self.track_classes.get(stable_id) != class_id:
                continue
            if frame_number - self.last_seen_frame.get(stable_id, frame_number) > self.stale_frames:
                continue

            score = _iou(previous_box, candidate_box)
            distance = _center_distance(previous_box, candidate_box)
            if score > best_iou or (score == best_iou and distance < best_distance):
                best_iou = score
                best_distance = distance
                best_track_id = stable_id

        if best_track_id is not None and (best_iou >= 0.15 or best_distance <= 0.75):
            stable_id = best_track_id
        else:
            stable_id = self.next_stable_id
            self.next_stable_id += 1

        self.raw_to_stable[raw_track_id] = stable_id
        self.track_boxes[stable_id] = candidate_box
        self.track_classes[stable_id] = class_id
        self.active_by_class[class_id] = stable_id
        self.update_seen(stable_id, frame_number)
        return stable_id

    def update_seen(self, track_id: int, frame_number: int) -> None:
        """Updates last-seen frame for the given track."""
        self.last_seen_frame[track_id] = frame_number

    def increment_persistence(self, track_id: int) -> int:
        """Increments persistence counter for a track."""
        self.persistence_count[track_id] += 1
        return self.persistence_count[track_id]

    def can_alert(self, track_id: int) -> bool:
        """Checks persistence and cooldown gates for alerting."""
        if self.persistence_count.get(track_id, 0) < self.persist_frames:
            return False

        now = time.time()
        elapsed = now - self.last_alert_time.get(track_id, 0.0)
        if elapsed < self.cooldown_seconds:
            return False

        self.last_alert_time[track_id] = now
        return True

    def cleanup(self, frame_number: int) -> None:
        """Removes stale track states that have disappeared."""
        stale_ids = [
            track_id
            for track_id, seen in self.last_seen_frame.items()
            if frame_number - seen > self.stale_frames
        ]
        for stale_id in stale_ids:
            stale_class = self.track_classes.get(stale_id)
            self.last_seen_frame.pop(stale_id, None)
            self.persistence_count.pop(stale_id, None)
            self.last_alert_time.pop(stale_id, None)
            self.track_boxes.pop(stale_id, None)
            self.track_classes.pop(stale_id, None)
            if stale_class is not None and self.active_by_class.get(stale_class) == stale_id:
                self.active_by_class.pop(stale_class, None)
            raw_ids_to_remove = [raw_id for raw_id, stable_id in self.raw_to_stable.items() if stable_id == stale_id]
            for raw_id in raw_ids_to_remove:
                self.raw_to_stable.pop(raw_id, None)
