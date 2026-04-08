"""Flask server with integrated weapon detection using WeaponDetectionRunner."""

from flask import Flask, render_template, jsonify, request, Response, send_file
from flask_cors import CORS
import json
from pathlib import Path
import threading
from datetime import datetime
import cv2
import logging
import argparse
import os

# Import weapon detection components
from weapon_detection.config import build_default_config
from weapon_detection.runner import WeaponDetectionRunner
from weapon_detection.events import AlertEvent

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
detection_thread = None
is_running = False
current_source = None
frame_count = 0
current_frame = None
frame_lock = threading.Lock()
current_detections = []
detection_lock = threading.Lock()
unique_track_ids = set()  # Track unique detections
track_lock = threading.Lock()
session_alert_count = 0  # Count alerts in current session
alert_count_lock = threading.Lock()

# Global configuration state
config_lock = threading.Lock()
current_config = {
    "confidence_threshold": 0.9,
    "device": "cpu",
    "imgsz": 640,
    "alert_classes": [0, 1],
    "persist_frames": 8,
    "cooldown": 60,
    "stale_frames": 30,
    "output_dir": "alerts",
    "workers": 4,
    "weights": "models/best.pt",
    "use_vlm": False,
    "vlm_model": "paligemma"
}


def load_alert_history():
    """Load alert history from JSON file."""
    alert_file = Path("alerts/Alert_history.json")
    if alert_file.exists():
        try:
            with open(alert_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading alerts: {e}")
    return []


def run_detection_with_runner(source):
    """Run detection using original WeaponDetectionRunner."""
    global is_running, frame_count, current_source, current_frame, current_detections, unique_track_ids, session_alert_count
    
    try:
        logger.info(f"Starting detection with source: {source}")
        current_source = str(source)
        frame_count = 0
        
        # Reset unique track IDs for new detection session
        with track_lock:
            unique_track_ids.clear()
        
        # Reset alert count for new session
        with alert_count_lock:
            global session_alert_count
            session_alert_count = 0
        
        # Build config with the provided source and current config
        with config_lock:
            cfg_copy = current_config.copy()
        
        args = argparse.Namespace(
            source=source,
            weights=cfg_copy["weights"],
            conf=cfg_copy["confidence_threshold"],
            alert_classes=cfg_copy["alert_classes"],
            persist_frames=cfg_copy["persist_frames"],
            cooldown=cfg_copy["cooldown"],
            stale_frames=cfg_copy["stale_frames"],
            output_dir=cfg_copy["output_dir"],
            workers=cfg_copy["workers"],
            device=cfg_copy["device"],
            use_vlm=cfg_copy["use_vlm"],
            vlm_model=cfg_copy["vlm_model"]
        )
        config = build_default_config(args)
        
        # Create runner
        runner = WeaponDetectionRunner(config)
        
        # Open video capture
        cap = cv2.VideoCapture(config.inference.source)
        if not cap.isOpened():
            logger.error(f"Failed to open source: {source}")
            is_running = False
            return
        
        frame_num = 0
        alert_classes = set(config.inference.alert_classes)
        
        logger.info("Detection loop started")
        
        while is_running:
            ret, frame = cap.read()
            if not ret:
                logger.warning("Failed to read frame")
                break
            
            try:
                frame_num += 1
                frame_count = frame_num
                
                # Run tracking (original logic)
                results = runner.model.track(
                    frame,
                    conf=config.inference.conf,
                    persist=True,
                    device=runner.detector_device,
                )
                
                # Process results
                with detection_lock:
                    current_detections = []
                    
                    for result in results:
                        boxes = result.boxes
                        if boxes.id is None:
                            continue
                        
                        for box, track_id_tensor in zip(boxes, boxes.id):
                            track_id = int(track_id_tensor)
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            class_name = result.names[cls_id]
                            
                            # Track unique detections
                            with track_lock:
                                unique_track_ids.add(track_id)
                            
                            # Draw box on frame
                            runner._draw_box(frame, box, track_id, conf)
                            
                            # Store detection info
                            current_detections.append({
                                "class": class_name,
                                "confidence": conf,
                                "track_id": track_id,
                                "bbox": box.xyxy[0].tolist()
                            })
                            
                            # Handle alerting logic
                            runner.tracks.update_seen(track_id, frame_num)
                            if cls_id in alert_classes:
                                runner.tracks.increment_persistence(track_id)
                                
                                if runner.tracks.can_alert(track_id):
                                    logger.warning(f"Weapon detected | track_id={track_id}")
                                    # Save snapshot
                                    snapshot = runner._snapshot_path(track_id)
                                    cv2.imwrite(str(snapshot), frame)
                                    
                                    # Increment session alert count
                                    with alert_count_lock:
                                        session_alert_count += 1
                                    
                                    # Dispatch alert
                                    event = AlertEvent(
                                        frame_number=frame_num,
                                        track_id=track_id,
                                        snapshot_path=snapshot,
                                        description=None,
                                    )
                                    runner.dispatcher.dispatch(event)
                                    runner._append_alert_history({
                                        "snapshot_path": str(snapshot),
                                        "confidence": conf,
                                        "track_id": track_id,
                                        "frame_number": frame_num,
                                    })
                
                # Cleanup old tracks
                runner.tracks.cleanup(frame_num)
                
                # Store frame for streaming
                with frame_lock:
                    current_frame = frame.copy()
                
                if frame_num % 10 == 0:
                    logger.info(f"Frame {frame_num}: {len(current_detections)} detections")
                    
            except Exception as e:
                logger.error(f"Inference error: {e}")
        
        cap.release()
        runner.dispatcher.close()
        logger.info("Detection stopped")
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        is_running = False
    finally:
        is_running = False


@app.route("/")
def index():
    """Serve the dashboard."""
    return render_template("index.html")


@app.route("/alerts")
def alerts_page():
    """Serve the alerts page."""
    return render_template("alerts.html")


@app.route("/api/detections")
def get_detections():
    """Get current detections."""
    with detection_lock:
        with track_lock:
            unique_count = len(unique_track_ids)
        with alert_count_lock:
            session_alerts = session_alert_count
        return jsonify({
            "status": "running" if is_running else "stopped",
            "detections": current_detections.copy(),
            "frame_count": frame_count,
            "source": current_source or "None",
            "unique_detections": unique_count,
            "session_alerts": session_alerts,
            "timestamp": datetime.now().isoformat()
        })


@app.route("/api/video_feed")
def video_feed():
    """Stream video frames as MJPEG."""
    def generate():
        while is_running:
            with frame_lock:
                if current_frame is not None:
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', current_frame)
                    frame_bytes = buffer.tobytes()
                    
                    # Yield frame in MJPEG format
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n'
                           b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
                           + frame_bytes + b'\r\n')
            
            # Small delay to avoid overwhelming the client
            import time
            time.sleep(0.03)  # ~30 FPS
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/api/alerts")
def get_alerts():
    """Get all alerts."""
    alerts = load_alert_history()
    # Convert paths to API image endpoint
    for alert in alerts:
        if "snapshot_path" in alert:
            # Extract filename from path
            filename = alert["snapshot_path"].replace("\\", "/").split("/")[-1]
            # Update to use API image serving endpoint
            alert["snapshot_path"] = f"/api/image/{filename}"
    # Return all alerts (sorted by newest first)
    return jsonify(list(reversed(alerts)) if alerts else [])


@app.route("/api/image/<filename>")
def get_image(filename):
    """Serve alert images."""
    try:
        image_path = Path("alerts") / filename
        if image_path.exists():
            return send_file(str(image_path), mimetype='image/jpeg')
        else:
            logger.warning(f"Image not found: {image_path}")
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats")
def get_stats():
    """Get detection statistics."""
    alerts = load_alert_history()
    
    return jsonify({
        "total_detections": len(alerts),
        "recent_alerts": alerts[-10:] if alerts else []
    })


@app.route("/api/start", methods=["POST"])
def start_detection():
    """Start detection with specified source."""
    global detection_thread, is_running, current_detections
    
    if is_running:
        return jsonify({"error": "Detection already running"}), 400
    
    data = request.json
    source = data.get("source", "0")
    
    logger.info(f"Starting detection with source: {source}")
    
    try:
        is_running = True
        current_detections = []
        
        # Start detection with WeaponDetectionRunner
        detection_thread = threading.Thread(target=run_detection_with_runner, args=(source,), daemon=True)
        detection_thread.start()
        
        return jsonify({"status": "started", "source": source})
    except Exception as e:
        is_running = False
        logger.error(f"Error starting detection: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop", methods=["POST"])
def stop_detection():
    """Stop detection."""
    global is_running
    
    logger.info("Stopping detection")
    is_running = False
    
    return jsonify({"status": "stopped"})


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration."""
    with config_lock:
        return jsonify(current_config.copy())


@app.route("/api/config", methods=["POST"])
def set_config():
    """Update configuration."""
    data = request.json
    
    # Validate and update config
    with config_lock:
        for key, value in data.items():
            if key in current_config:
                # Type validation
                if key == "alert_classes" and not isinstance(value, list):
                    return jsonify({"error": f"Invalid type for {key}"}), 400
                if key in ["confidence_threshold", "imgsz"] and not isinstance(value, (int, float)):
                    return jsonify({"error": f"Invalid type for {key}"}), 400
                
                current_config[key] = value
                logger.info(f"Config updated: {key} = {value}")
            else:
                logger.warning(f"Unknown config key: {key}")
    
    logger.info(f"Configuration updated: {data}")
    return jsonify({"status": "updated", "config": current_config.copy()})


@app.route("/api/clear-alerts", methods=["POST"])
def clear_alerts():
    """Clear all alert history."""
    try:
        alert_file = Path("alerts/Alert_history.json")
        if alert_file.exists():
            with open(alert_file, "w") as f:
                json.dump([], f)
            logger.info("Alert history cleared")
            return jsonify({"status": "cleared"})
        return jsonify({"status": "no alerts to clear"})
    except Exception as e:
        logger.error(f"Error clearing alerts: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        logger.info("Starting Flask server on http://0.0.0.0:5000")
        app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)
    finally:
        is_running = False
