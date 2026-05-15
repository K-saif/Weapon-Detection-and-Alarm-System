"""Multi-camera detection orchestrator."""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from queue import Queue

import cv2
from ultralytics import YOLO

from weapon_detection.camera_source import CameraInfo, CameraSourceType
from weapon_detection.channels import EmailChannel, TelegramChannel
from weapon_detection.config import AppConfig
from weapon_detection.dispatcher import AlertDispatcher
from weapon_detection.events import AlertEvent
from weapon_detection.tracking import TrackLifecycle
from weapon_detection.vlm import load_model, query_model
from weapon_detection.paligemma import load_model_pali, query_model_pali
from weapon_detection.qwen import load_model_qwen, query_model_qwen

LOGGER = logging.getLogger("weapon-detect")


class CameraDetectionWorker:
    """Worker thread for processing a single camera feed."""
    
    def __init__(
        self,
        camera_info: CameraInfo,
        model: YOLO,
        config: AppConfig,
        dispatcher: AlertDispatcher,
        device: str = "0",
        output_dir: Path = None,
        vlm_model=None,
        vlm_processor=None,
    ):
        self.camera_info = camera_info
        self.model = model
        self.config = config
        self.dispatcher = dispatcher
        self.device = device
        self.output_dir = output_dir or Path("alerts")
        self.vlm_model = vlm_model
        self.vlm_processor = vlm_processor
        
        self.tracks = TrackLifecycle(
            persist_frames=config.inference.persist_frames,
            cooldown_seconds=config.inference.cooldown_seconds,
            stale_frames=config.inference.stale_frames,
        )
        
        self.thread: Optional[threading.Thread] = None
        self.running = False
        self.frame_count = 0
        self.stats = {
            "total_frames": 0,
            "weapons_detected": 0,
            "alerts_sent": 0,
            "last_detection": None,
            "fps": 0.0,
        }
    
    def _snapshot_path(self, track_id: int) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        camera_dir = self.output_dir / self.camera_info.source_id
        camera_dir.mkdir(parents=True, exist_ok=True)
        return camera_dir / f"weapon_track{track_id}_{timestamp}.jpg"
    
    def _json_path(self) -> Path:
        camera_dir = self.output_dir / self.camera_info.source_id
        camera_dir.mkdir(parents=True, exist_ok=True)
        return camera_dir / "alert_history.json"
    
    def _append_alert_history(self, alert_data: dict[str, object]) -> None:
        json_path = self._json_path()
        history: list[dict[str, object]] = []
        if json_path.exists():
            raw_content = json_path.read_text(encoding="utf-8").strip()
            if raw_content:
                parsed = json.loads(raw_content)
                if isinstance(parsed, list):
                    history = [item for item in parsed if isinstance(item, dict)]
                elif isinstance(parsed, dict):
                    history = [parsed]
        history.append(alert_data)
        json_path.write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    
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
        """Main detection loop for this camera."""
        self.running = True
        try:
            cap = cv2.VideoCapture(self.camera_info.connection_string)
            if not cap.isOpened():
                LOGGER.error(
                    f"Failed to open camera: {self.camera_info.name} "
                    f"({self.camera_info.connection_string})"
                )
                return
            
            LOGGER.info(f"Started detection worker for: {self.camera_info.name}")
            alert_classes = set(self.config.inference.alert_classes)
            frame_count = 0
            last_fps_time = time.time()
            fps_frames = 0
            
            while self.running:
                ret, frame = cap.read()
                if not ret:
                    LOGGER.warning(f"Failed to read frame from {self.camera_info.name}")
                    break
                
                frame_count += 1
                self.frame_count = frame_count
                self.stats["total_frames"] = frame_count
                fps_frames += 1
                
                # Calculate FPS every 30 frames
                current_time = time.time()
                if fps_frames >= 30:
                    elapsed = current_time - last_fps_time
                    self.stats["fps"] = 30 / elapsed if elapsed > 0 else 0
                    last_fps_time = current_time
                    fps_frames = 0
                
                try:
                    results = self.model.track(
                        frame,
                        conf=self.config.inference.conf,
                        persist=True,
                        device=self.device,
                    )
                    
                    for result in results:
                        boxes = result.boxes
                        if boxes.id is None:
                            continue
                        
                        for box, track_id_tensor in zip(boxes, boxes.id):
                            track_id = int(track_id_tensor)
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            self.tracks.update_seen(track_id, frame_count)
                            
                            if cls_id not in alert_classes:
                                continue
                            
                            self._draw_box(frame, box, track_id, conf)
                            self.tracks.increment_persistence(track_id)
                            
                            if not self.tracks.can_alert(track_id):
                                continue
                            
                            self.stats["weapons_detected"] += 1
                            self.stats["last_detection"] = datetime.now().isoformat()
                            self.stats["alerts_sent"] += 1
                            
                            snapshot = self._snapshot_path(track_id)
                            cv2.imwrite(str(snapshot), frame)
                            
                            LOGGER.warning(
                                f"[{self.camera_info.name}] Weapon detected | "
                                f"track_id={track_id} frame={frame_count}"
                            )
                            
                            vlm_description = None
                            if self.config.vlm.use_vlm:
                                try:
                                    if self.config.vlm.vlm_model == "llava":
                                        vlm_description = query_model(frame, self.vlm_model, self.vlm_processor)
                                    elif self.config.vlm.vlm_model == "paligemma":
                                        vlm_description = query_model_pali(frame, self.vlm_model, self.vlm_processor)
                                    elif self.config.vlm.vlm_model == "qwen":
                                        vlm_description = query_model_qwen(frame, self.vlm_model, self.vlm_processor)
                                except Exception as exc:
                                    LOGGER.exception(
                                        f"VLM query failed for {self.camera_info.name}, track_id={track_id}: {exc}"
                                    )
                            
                            if vlm_description:
                                LOGGER.info(
                                    f"[{self.camera_info.name}] VLM: {vlm_description}"
                                )
                            
                            event = AlertEvent(
                                frame_number=frame_count,
                                track_id=track_id,
                                snapshot_path=snapshot,
                                description=vlm_description,
                            )
                            self.dispatcher.dispatch(event)
                            
                            alert_data = {
                                "camera": self.camera_info.name,
                                "camera_source": self.camera_info.connection_string,
                                "snapshot_path": str(snapshot),
                                "confidence": conf,
                                "track_id": track_id,
                                "frame_number": frame_count,
                                "timestamp": datetime.now().isoformat(),
                                "description": vlm_description if self.config.vlm.use_vlm else None,
                            }
                            self._append_alert_history(alert_data)
                    
                    self.tracks.cleanup(frame_count)
                    
                except Exception as e:
                    LOGGER.exception(f"Error processing frame from {self.camera_info.name}: {e}")
                    
        except Exception as e:
            LOGGER.exception(f"Fatal error in detection worker for {self.camera_info.name}: {e}")
        finally:
            cap.release()
            LOGGER.info(f"Stopped detection worker for: {self.camera_info.name}")
            self.running = False
    
    def start(self) -> None:
        """Start the worker thread."""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run, daemon=False)
            self.thread.start()
    
    def stop(self) -> None:
        """Stop the worker thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def get_stats(self) -> dict[str, object]:
        """Get current worker statistics."""
        return {
            **self.stats,
            "camera_name": self.camera_info.name,
            "camera_type": self.camera_info.source_type.value,
        }


class MultiCameraDetectionRunner:
    """Orchestrates detection across multiple camera feeds."""
    
    def __init__(self, config: AppConfig, cameras: list[CameraInfo]) -> None:
        self.config = config
        self.cameras = cameras
        self.model = YOLO(config.inference.weights)
        self.detector_device = "cpu" if config.inference.device == "cpu" else "0"
        self.output_dir = Path(config.inference.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        channels = [
            EmailChannel(config.email),
            TelegramChannel(config.telegram),
        ]
        self.dispatcher = AlertDispatcher(channels=channels)
        
        # Load VLM models once, share across workers
        self.vlm_model = None
        self.vlm_processor = None
        if config.vlm.use_vlm:
            try:
                if config.vlm.vlm_model == "llava":
                    self.vlm_model, self.vlm_processor = load_model()
                elif config.vlm.vlm_model == "paligemma":
                    self.vlm_model, self.vlm_processor = load_model_pali()
                elif config.vlm.vlm_model == "qwen":
                    self.vlm_model, self.vlm_processor = load_model_qwen()
                LOGGER.info(f"Loaded VLM model: {config.vlm.vlm_model}")
            except Exception as e:
                LOGGER.error(f"Failed to load VLM model: {e}")
                self.vlm_model = None
                self.vlm_processor = None
        
        self.workers: list[CameraDetectionWorker] = []
        self._create_workers()
    
    def _create_workers(self) -> None:
        """Create detection workers for each camera."""
        for camera in self.cameras:
            worker = CameraDetectionWorker(
                camera_info=camera,
                model=self.model,
                config=self.config,
                dispatcher=self.dispatcher,
                device=self.detector_device,
                output_dir=self.output_dir,
                vlm_model=self.vlm_model,
                vlm_processor=self.vlm_processor,
            )
            self.workers.append(worker)
    
    def run(self) -> None:
        """Start all workers and monitor them."""
        LOGGER.info(f"Starting multi-camera detection with {len(self.cameras)} camera(s)")
        
        # Start all workers
        for worker in self.workers:
            worker.start()
        
        try:
            # Monitor workers
            while any(w.running for w in self.workers):
                time.sleep(1)
                self._print_stats()
        except KeyboardInterrupt:
            LOGGER.info("Received interrupt signal")
        finally:
            self.stop()
    
    def _print_stats(self) -> None:
        """Print statistics for all workers."""
        try:
            # Print every 30 seconds
            if not hasattr(self, "_last_stats_print"):
                self._last_stats_print = time.time()
            
            if time.time() - self._last_stats_print < 30:
                return
            
            self._last_stats_print = time.time()
            print("\n" + "="*80)
            print(f"{'DETECTION STATS':^80}")
            print("="*80)
            
            for worker in self.workers:
                stats = worker.get_stats()
                print(f"\n{stats['camera_name']} ({stats['camera_type']}):")
                print(f"  Frames: {stats['total_frames']}")
                print(f"  Weapons Detected: {stats['weapons_detected']}")
                print(f"  Alerts Sent: {stats['alerts_sent']}")
                print(f"  FPS: {stats['fps']:.1f}")
                if stats['last_detection']:
                    print(f"  Last Detection: {stats['last_detection']}")
            
            print("="*80 + "\n")
        except Exception as e:
            LOGGER.debug(f"Error printing stats: {e}")
    
    def stop(self) -> None:
        """Stop all workers."""
        LOGGER.info("Stopping all detection workers...")
        for worker in self.workers:
            worker.stop()
        self.dispatcher.close()
        LOGGER.info("All detection workers stopped")
