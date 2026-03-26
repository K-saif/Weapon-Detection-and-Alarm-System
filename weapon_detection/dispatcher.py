"""Asynchronous dispatch utilities for alert channels."""

from concurrent.futures import ThreadPoolExecutor
import logging

try:
    import winsound
except ImportError:  # pragma: no cover - non-Windows fallback
    winsound = None

from weapon_detection.channels import AlertChannel
from weapon_detection.events import AlertEvent


LOGGER = logging.getLogger("weapon-detect")


class AlertDispatcher:
    """Asynchronous fan-out dispatcher for alert channels."""

    def __init__(self, channels: list[AlertChannel], workers: int = 4) -> None:
        self.channels = channels
        self.pool = ThreadPoolExecutor(max_workers=max(1, workers))

    def _play_system_alert_sound(self) -> None:
        """Plays a short blocking system alert sound before channel dispatch."""
        if winsound is None:
            return

        try:
            winsound.Beep(1200, 2000)
        except RuntimeError as exc:
            LOGGER.warning("Alert sound failed: %s", exc)

    def dispatch(self, event: AlertEvent) -> None:
        self._play_system_alert_sound()
        for channel in self.channels:
            self.pool.submit(channel.send, event)

    def close(self) -> None:
        self.pool.shutdown(wait=False, cancel_futures=False)
