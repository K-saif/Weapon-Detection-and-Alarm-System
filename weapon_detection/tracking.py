"""Tracking state manager for lifecycle decisions."""

import time
from collections import defaultdict


class TrackLifecycle:
    """Track-level persistence, cooldown, and stale-state management."""

    def __init__(self, persist_frames: int, cooldown_seconds: int, stale_frames: int) -> None:
        self.persist_frames = persist_frames
        self.cooldown_seconds = cooldown_seconds
        self.stale_frames = stale_frames
        self.persistence_count: dict[int, int] = defaultdict(int)
        self.last_seen_frame: dict[int, int] = {}
        self.last_alert_time: dict[int, float] = {}

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
            self.last_seen_frame.pop(stale_id, None)
            self.persistence_count.pop(stale_id, None)
            self.last_alert_time.pop(stale_id, None)
