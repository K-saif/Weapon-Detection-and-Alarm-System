"""Runtime orchestrator for detection and alerting."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

import cv2
from ultralytics import YOLO

from weapon_detection.channels import EmailChannel, TelegramChannel
from weapon_detection.config import AppConfig
from weapon_detection.dispatcher import AlertDispatcher
from weapon_detection.events import AlertEvent
from weapon_detection.tracking import TrackLifecycle
from weapon_detection.vlm import load_model, query_model

LOGGER = logging.getLogger("weapon-detect")


class WeaponDetectionRunner:
    """High-level runtime orchestrator for detection and alerts."""

    def __init__(self, config: AppConfig) -> None:
        self.cfg = config
        self.model = YOLO(self.cfg.inference.weights)
        self.output_dir = Path(self.cfg.inference.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        channels = [
            EmailChannel(self.cfg.email),
            TelegramChannel(self.cfg.telegram),
        ]
        self.dispatcher = AlertDispatcher(channels=channels, workers=self.cfg.workers)
        self.tracks = TrackLifecycle(
            persist_frames=self.cfg.inference.persist_frames,
            cooldown_seconds=self.cfg.inference.cooldown_seconds,
            stale_frames=self.cfg.inference.stale_frames,
        )

    def _snapshot_path(self, track_id: int) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"weapon_track{track_id}_{timestamp}.jpg"

    def _draw_box(self, frame, box, track_id: int, conf: float) -> None:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(
            frame,
            f"Weapon ID:{track_id} {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2,
        )

    def run(self) -> None:
        """Executes video capture, tracking, and alert emission loop."""
        cap = cv2.VideoCapture(self.cfg.inference.source)
        frame_number = 0
        alert_classes = set(self.cfg.inference.alert_classes)
        vlm_model, vlm_processor = load_model() if self.cfg.vlm.use_vlm else (None, None)

        LOGGER.info("Starting detection with tracking")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_number += 1
            results = self.model.track(frame, conf=self.cfg.inference.conf, persist=True)

            for result in results:
                boxes = result.boxes
                if boxes.id is None:
                    continue

                for box, track_id_tensor in zip(boxes, boxes.id):
                    track_id = int(track_id_tensor)
                    cls_id = int(box.cls[0])
                    conf = float(box.conf[0])
                    self.tracks.update_seen(track_id, frame_number)

                    if cls_id not in alert_classes:
                        continue

                    self._draw_box(frame, box, track_id, conf)
                    self.tracks.increment_persistence(track_id)

                    if not self.tracks.can_alert(track_id):
                        continue

                    snapshot = self._snapshot_path(track_id)
                    cv2.imwrite(str(snapshot), frame)
                    event = AlertEvent(
                        frame_number=frame_number,
                        track_id=track_id,
                        snapshot_path=snapshot,
                    )
                    LOGGER.warning(
                        "Weapon detected | track_id=%d frame=%d", track_id, frame_number
                    )
                    self.dispatcher.dispatch(event)

                    vlm_description = query_model(snapshot, vlm_model, vlm_processor) if self.cfg.vlm.use_vlm else None
                    if vlm_description:
                        LOGGER.info("VLM description for track_id=%d: %s", track_id, vlm_description)

            self.tracks.cleanup(frame_number)
            cv2.imshow("Weapon Detection + Tracking", frame)

            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.dispatcher.close()
