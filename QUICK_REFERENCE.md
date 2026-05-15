# Quick Reference - Multi-Camera System

## 🚀 Start Here

### Launch Multi-Camera Interactive Setup
```bash
python main.py multi
```

### Launch Single Camera (Backward Compatible)
```bash
python main.py --source 0
```

## 📁 New Files Created

```
weapon_detection/
├── camera_source.py         # Camera source abstraction & discovery
├── multi_camera_runner.py   # Multi-threaded detection orchestrator
├── camera_cli.py            # Interactive camera selection UI
└── multi_camera_cli.py      # Multi-camera entry point
```

## 📚 Documentation Files

```
MULTI_CAMERA_README.md              # Full user guide (detailed)
MULTI_CAMERA_IMPLEMENTATION.md      # Technical implementation details
QUICK_REFERENCE.md                  # This file!
```

## 🎯 Supported Camera Types

| Type | Discovery | Example |
|------|-----------|---------|
| **Webcam** | Auto | 0, 1, 2 |
| **IP Camera** | Manual | http://192.168.1.100:8080/stream |
| **HTTPS Stream** | Manual | https://camera.example.com/stream |
| **RTSP Stream** | Manual | rtsp://192.168.1.100:554/stream |
| **Video File** | Auto | /path/to/video.mp4 |
| **Mixed** | Both | Combine any types |

## 🔄 Usage Patterns

### Pattern 1: Interactive Multi-Camera (Recommended)
```bash
# Start
python main.py multi

# Then select:
# 1. Camera source type
# 2. Configure cameras (auto-discover or manual)
# 3. Validate connections
# 4. Confirm and start

# Monitor console output for real-time stats
```

### Pattern 2: Single Webcam (Legacy)
```bash
python main.py --source 0 --device gpu
```

### Pattern 3: IP Camera Feed
```bash
python main.py --source "http://192.168.1.100:8080/stream" --conf 0.9
```

### Pattern 4: Video File Processing
```bash
python main.py --source "path/to/video.mp4" --device gpu
```

## ⚙️ Common Parameters

```bash
python main.py [multi] \
  --source 0 \
  --device cpu \
  --conf 0.9 \
  --cooldown 60 \
  --use_vlm false
```

| Parameter | Default | Notes |
|-----------|---------|-------|
| --source | 0 | Single camera source (ignored in multi mode) |
| --device | cpu | Use 'gpu' for faster processing |
| --conf | 0.9 | Confidence threshold (0-1) |
| --cooldown | 60 | Seconds between alerts for same track |
| --persist_frames | 8 | Frames before triggering alert |
| --use_vlm | false | Enable VLM descriptions |
| --vlm_model | paligemma | llava, paligemma, or qwen |
| --device | cpu | Inference device |
| --output_dir | alerts | Where to save snapshots |

## 📊 Output Structure

```
alerts/
├── webcam_0/
│   ├── weapon_track*.jpg
│   └── alert_history.json
├── ipcam_192.168.1.100/
│   ├── weapon_track*.jpg
│   └── alert_history.json
└── https_stream_*/
    ├── weapon_track*.jpg
    └── alert_history.json
```

## 📈 Console Statistics Output

Every 30 seconds:
```
================================================================================
                            DETECTION STATS
================================================================================

Camera 1 (type):
  Frames: 1234
  Weapons Detected: 5
  Alerts Sent: 5
  FPS: 29.8
  Last Detection: 2025-05-15T12:05:32.123456

Camera 2 (type):
  Frames: 1200
  Weapons Detected: 2
  Alerts Sent: 2
  FPS: 25.3
  Last Detection: 2025-05-15T12:04:15.654321
```

## 🔧 Code Examples

### Using Multi-Camera Programmatically
```python
from weapon_detection.multi_camera_runner import MultiCameraDetectionRunner
from weapon_detection.config import AppConfig, InferenceConfig
from weapon_detection.camera_source import CameraInfo, CameraSourceType

# Define cameras
cameras = [
    CameraInfo(
        source_id="webcam_0",
        name="Front Door",
        source_type=CameraSourceType.WEBCAM,
        connection_string="0"
    ),
    CameraInfo(
        source_id="ipcam_lobby",
        name="Lobby",
        source_type=CameraSourceType.IP_CAMERA,
        connection_string="http://192.168.1.100:8080/stream"
    ),
]

# Create config
config = AppConfig(
    inference=InferenceConfig(device="gpu"),
    email=None,  # or configure
    telegram=None,  # or configure
    vlm=None,  # or configure
)

# Run
runner = MultiCameraDetectionRunner(config, cameras)
runner.run()
```

## 🐛 Troubleshooting Quick Fixes

| Issue | Fix |
|-------|-----|
| No cameras found | Check device permissions, camera not in use |
| Low FPS | Switch to GPU, reduce resolution at source |
| Connection timeout | Check IP, firewall, stream path |
| High CPU usage | Lower confidence `--conf 0.7`, disable VLM |
| Memory issues | Reduce number of cameras, use GPU |

## 🔑 Key Architecture Points

1. **Shared Models**: YOLO & VLM loaded once, shared across threads
2. **Independent Tracking**: Each camera has own track lifecycle
3. **Per-Camera Alerts**: Snapshots and logs organized by camera
4. **Thread-Safe**: All operations are thread-safe
5. **Graceful Shutdown**: Ctrl+C stops all workers cleanly

## 📞 Alert Configuration

Create `.env` in `weapon_detection/` folder:
```env
ALERT_EMAIL_SENDER=your-email@gmail.com
ALERT_EMAIL_PASS=your-app-password
ALERT_TELEGRAM_BOT_TOKEN=your-bot-token
ALERT_TELEGRAM_CHAT_ID=your-chat-id
```

## 🎓 Learning Path

1. **Start**: `python main.py multi` (interactive)
2. **Read**: [MULTI_CAMERA_README.md](MULTI_CAMERA_README.md) for details
3. **Experiment**: Try different camera types
4. **Optimize**: Use `--device gpu` and tune parameters
5. **Integrate**: Add web UI (future step)
6. **Deploy**: Run as background service

## 📚 Full Documentation

- **User Guide**: [MULTI_CAMERA_README.md](MULTI_CAMERA_README.md)
- **Implementation Details**: [MULTI_CAMERA_IMPLEMENTATION.md](MULTI_CAMERA_IMPLEMENTATION.md)
- **Original README**: [README.md](README.md)

## ✅ What's Ready Now

✅ Terminal-based multi-camera support  
✅ 6+ camera source types  
✅ Auto-discovery  
✅ Interactive CLI  
✅ Per-camera tracking & alerts  
✅ Real-time statistics  
✅ Backward compatible  
✅ Production-ready threading  

## 🚧 Future (For UI Integration)

🔄 Web dashboard with camera feeds  
🔄 REST API for camera management  
🔄 Database persistence  
🔄 Historical alert viewing  
🔄 Real-time WebSocket updates  

---

**You're ready to detect weapons across multiple cameras!** 🎯
