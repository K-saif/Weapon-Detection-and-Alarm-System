"""Asynchronous dispatch utilities for alert channels."""

from concurrent.futures import ThreadPoolExecutor

from weapon_detection.channels import AlertChannel
from weapon_detection.events import AlertEvent


class AlertDispatcher:
    """Asynchronous fan-out dispatcher for alert channels."""

    def __init__(self, channels: list[AlertChannel], workers: int = 4) -> None:
        self.channels = channels
        self.pool = ThreadPoolExecutor(max_workers=max(1, workers))

    def dispatch(self, event: AlertEvent) -> None:
        for channel in self.channels:
            self.pool.submit(channel.send, event)

    def close(self) -> None:
        self.pool.shutdown(wait=False, cancel_futures=False)
