"""Alert transport channel implementations."""

from __future__ import annotations

import importlib
import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from weapon_detection.config import EmailConfig, TelegramConfig
from weapon_detection.events import AlertEvent


LOGGER = logging.getLogger("weapon-detect")


class AlertChannel(Protocol):
    """Alert transport interface."""

    def send(self, event: AlertEvent) -> None:
        """Sends an alert for the supplied event."""


class EmailChannel:
    """SMTP email alert channel."""

    def __init__(self, config: EmailConfig) -> None:
        self.config = config

    def send(self, event: AlertEvent) -> None:
        msg = EmailMessage()
        msg["Subject"] = f"⚠️ Weapon Detected (Track ID: {event.track_id})"
        msg["From"] = self.config.sender
        msg["To"] = self.config.receiver
        msg.set_content(
            "Weapon detected at frame "
            f"{event.frame_number}\nTrack ID: {event.track_id}"
            f"\nDescription: {event.description}" if event.description else ""
        )

        with event.snapshot_path.open("rb") as image_file:
            msg.add_attachment(
                image_file.read(),
                maintype="image",
                subtype="jpeg",
                filename=event.snapshot_path.name,
            )

        try:
            smtp = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            smtp.starttls()
            smtp.login(self.config.sender, self.config.password)
            smtp.send_message(msg)
            smtp.quit()
            LOGGER.info("Email sent for track_id=%d", event.track_id)
        except Exception as exc:
            LOGGER.error("Email failed for track_id=%d: %s", event.track_id, exc)


class TelegramChannel:
    """Telegram bot alert channel."""

    def __init__(self, config: TelegramConfig) -> None:
        self.config = config

    @property
    def enabled(self) -> bool:
        return bool(self.config.bot_token and self.config.chat_id)

    def send(self, event: AlertEvent) -> None:
        if not self.enabled:
            return

        try:
            requests_module = importlib.import_module("requests")
        except ImportError:
            LOGGER.warning("Telegram skipped: requests package missing")
            return

        url = f"https://api.telegram.org/bot{self.config.bot_token}/sendPhoto"
        caption = (
            "⚠️ Weapon detected at frame "
            f"{event.frame_number} (Track ID: {event.track_id})"
            f"\nDescription: {event.description}" if event.description else ""
        )

        try:
            with event.snapshot_path.open("rb") as photo:
                files = {"photo": photo}
                data = {"chat_id": self.config.chat_id, "caption": caption}
                response = requests_module.post(url, data=data, files=files, timeout=15)
            response.raise_for_status()
            LOGGER.info("Telegram sent for track_id=%d", event.track_id)
        except Exception as exc:
            LOGGER.error("Telegram failed for track_id=%d: %s", event.track_id, exc)
