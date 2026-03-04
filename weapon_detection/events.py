"""Domain events for alert processing."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AlertEvent:
    """Event payload sent to alert channels."""

    frame_number: int
    track_id: int
    snapshot_path: Path
