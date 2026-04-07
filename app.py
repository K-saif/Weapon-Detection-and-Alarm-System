"""Flask server with integrated weapon detection using WeaponDetectionRunner."""

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import json
from pathlib import Path
import threading
from datetime import datetime
import cv2
import logging
import argparse

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
    global is_running, frame_count, current_source, current_frame, current_detections
    
    try:
        logger.info(f"Starting detection with source: {source}")
        current_source = str(source)
        frame_count = 0
        
        # Build config with the provided source
        args = argparse.Namespace(
            source=source,
            weights="models/best.pt",
            conf=0.4,
            alert_classes=[0, 1],
            persist_frames=8,
            cooldown=60,
            stale_frames=30,
            output_dir="alerts",
            workers=4,
            device="cpu",
            use_vlm=False,
            vlm_model="paligemma"
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


@app.route("/api/detections")
def get_detections():
    """Get current detections."""
    with detection_lock:
        return jsonify({
            "status": "running" if is_running else "stopped",
            "detections": current_detections.copy(),
            "frame_count": frame_count,
            "source": current_source or "None",
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
    """Get recent alerts."""
    alerts = load_alert_history()
    # Return last 20 alerts
    return jsonify(alerts[-20:] if alerts else [])


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
    return jsonify({
        "confidence_threshold": 0.5,
        "device": "auto",
        "imgsz": 640,
        "alert_classes": ["gun", "pistol", "knife"]
    })


@app.route("/api/config", methods=["POST"])
def set_config():
    """Update configuration."""
    data = request.json
    logger.info(f"Configuration updated: {data}")
    return jsonify({"status": "updated", "config": data})


if __name__ == "__main__":
    try:
        logger.info("Starting Flask server on http://0.0.0.0:5000")
        app.run(debug=False, host="0.0.0.0", port=5000, threaded=True)
    finally:
        is_running = False
