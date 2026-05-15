# Multi-Camera Weapon Detection System

This guide explains how to set up and use the multi-camera weapon detection system for monitoring multiple feeds simultaneously.

## Overview

The multi-camera system allows you to:
- Monitor **multiple camera feeds simultaneously** (webcams, IP cameras, HTTPS streams, RTSP streams, video files)
- **Auto-discover available cameras** by type
- Run **separate detection pipelines** for each camera in parallel threads
- Track weapons **per-camera** with independent alert histories
- **Mix different source types** (e.g., 2 webcams + 3 IP cameras + 1 HTTPS stream)

## Quick Start

### Option 1: Interactive Multi-Camera Mode (Recommended)

```bash
python main.py multi
```

This launches an interactive menu system where you can:
1. Select camera source type (Webcam, IP Camera, HTTPS Stream, RTSP, Video File, or Mixed)
2. Auto-discover available cameras
3. Add custom camera sources with credentials
4. Validate connections
5. Confirm and start detection

### Option 2: Single Camera Mode (Legacy)

```bash
python main.py --source 0  # Webcam
python main.py --source rtsp://192.168.1.100:554/stream  # RTSP stream
```

## Supported Camera Sources

### 1. **Webcam(s)**
- **Auto-Discovery**: Automatically finds all connected webcams
- **Usage**: `python main.py multi` → Select "Webcams"

```
Features:
- Automatic detection of all connected webcams
- Display resolution and FPS information
- Support for multiple webcams on the same system
```

### 2. **IP Cameras**
- **Manual Entry**: Manually add IP camera addresses
- **Authentication**: Supports username/password
- **Validation**: Test connection before starting

```
Configuration:
- IP Address: 192.168.1.100
- Port: 8080 (default)
- Stream Path: /stream (default)
- Username/Password: Optional
```

Example IP Camera URLs:
```
http://192.168.1.100:8080/stream  (without auth)
http://user:pass@192.168.1.100:8080/stream  (with auth)
```

### 3. **HTTPS Streams**
- Stream from secure HTTPS endpoints
- No credential support (use URL-embedded auth if needed)

Example:
```
https://camera.example.com/stream
https://yourserver.com:8443/video/feed
```

### 4. **RTSP Streams**
- Professional camera streams (RTSP protocol)
- Common in enterprise surveillance systems

Example:
```
rtsp://192.168.1.100:554/stream
rtsp://user:pass@192.168.1.100:554/Streaming/Channels/101
```

### 5. **Video Files**
- Process pre-recorded video files
- Auto-discovers `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv`, `.wmv`

## How Multi-Camera Detection Works

```
┌─────────────────────────────────────────────────────────┐
│           Multi-Camera Detection Pipeline                │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
           ┌─────────┐ ┌─────────┐ ┌─────────┐
           │ Camera 1│ │ Camera 2│ │ Camera N│
           │ Thread  │ │ Thread  │ │ Thread  │
           └────┬────┘ └────┬────┘ └────┬────┘
                │           │           │
    ┌───────────┼───────────┼───────────┤
    │  YOLO Detection Model (Shared)    │
    │  + VLM Model (Shared)             │
    └───────────┬───────────┬───────────┤
                │           │           │
    ┌───────────▼────────┬──▼──┬────────▼──────────┐
    │  Independent Tracking per Camera              │
    │  - Track lifecycle                            │
    │  - Cooldown & persistence management          │
    │  - Alert dispatch                             │
    └───────────┬────────┬─────┬───────────────────┘
                │        │     │
    ┌───────────▼────┬───▼──┬──▼────────────────┐
    │  Alert Channels (Shared)                  │
    │  - Email                                  │
    │  - Telegram                               │
    │  - Snapshots & Logs (per-camera)          │
    └───────────────┬───────────────────────────┘
```

### Key Features:

1. **Parallel Processing**: Each camera runs in a dedicated thread
2. **Shared Model**: YOLO and VLM models are loaded once and shared
3. **Independent Tracking**: Each camera has its own track lifecycle
4. **Per-Camera Alerts**: Alerts include camera identification
5. **Organized Output**: Snapshots and logs organized by camera ID
6. **Real-time Statistics**: Monitor FPS, detection counts per camera

## Output Structure

When running multi-camera mode, outputs are organized as:

```
alerts/
├── webcam_0/
│   ├── weapon_track0_20250515_120000.jpg
│   ├── weapon_track1_20250515_120030.jpg
│   └── alert_history.json
├── ipcam_192.168.1.100/
│   ├── weapon_track0_20250515_120000.jpg
│   └── alert_history.json
└── https_stream_1234567890/
    ├── weapon_track0_20250515_120000.jpg
    └── alert_history.json
```

Alert history per camera:
```json
[
  {
    "camera": "IP Camera 192.168.1.100:8080",
    "camera_source": "http://192.168.1.100:8080/stream",
    "snapshot_path": "alerts/ipcam_192.168.1.100/weapon_track0_20250515_120000.jpg",
    "confidence": 0.95,
    "track_id": 0,
    "frame_number": 1234,
    "timestamp": "2025-05-15T12:00:00.123456",
    "description": "Person holding a rifle in standing position"
  }
]
```

## Command Examples

### Example 1: Start Interactive Multi-Camera Setup
```bash
python main.py multi
```

### Example 2: Single Webcam (Traditional Mode)
```bash
python main.py --source 0 --conf 0.9
```

### Example 3: RTSP Stream (Single)
```bash
python main.py --source "rtsp://192.168.1.100:554/stream" --device gpu
```

### Example 4: Video File Processing
```bash
python main.py --source "path/to/video.mp4" --device gpu
```

## Configuration Parameters

Common parameters to use with any mode:

```bash
python main.py [multi] [OPTIONS]

Options:
  --source SOURCE           Single camera source (single mode only)
  --weights WEIGHTS         Path to YOLO model (default: models/best.pt)
  --conf CONFIDENCE         Detection confidence (0-1, default: 0.9)
  --alert_classes CLASS_IDS Classes to alert on (default: 0)
  --device {cpu,gpu}        Inference device (default: cpu)
  --output_dir DIR          Output directory for alerts (default: alerts)
  --cooldown SECONDS        Alert cooldown per track (default: 60)
  --persist_frames FRAMES   Frames before first alert (default: 8)
  --use_vlm {true,false}    Enable VLM descriptions (default: false)
  --vlm_model {llava,paligemma,qwen}  VLM model to use
  --workers WORKERS         Alert workers (default: 4)
```

## Multi-Camera Workflow

### Step 1: Start Interactive Setup
```bash
python main.py multi
```

### Step 2: Select Source Type
```
================================================================================
                       CAMERA SOURCE TYPE SELECTION
================================================================================

Select an option:
  1. Webcam(s)
  2. IP Camera(s)
  3. HTTPS Stream
  4. RTSP Stream
  5. Video File
  6. Mixed (Different types)

Enter your choice (number): 
```

### Step 3: Configure Cameras
Depending on selection, follow prompts to add cameras.

**For Webcams:**
```
Scanning for webcam(s)...
Found 2 webcam(s):
  1. Webcam 1 (ID: webcam_0)
     Resolution: 1920x1080, FPS: 30
  2. Webcam 2 (ID: webcam_1)
     Resolution: 1280x720, FPS: 30

Select webcam(s) to use (comma-separated numbers, e.g., '1,2'): 1,2
```

**For IP Cameras:**
```
Camera 1:
  Enter IP address (or 'done' to finish): 192.168.1.100
  Enter port (default: 8080): 8080
  Enter username (optional, press Enter to skip): admin
  Enter password (optional, press Enter to skip): password123
  Enter stream path (default: /stream): /stream
  Adding IP camera...
  ✓ Camera validated successfully!
```

### Step 4: Review and Confirm
```
================================================================================
                            SELECTED CAMERAS
================================================================================

1. Webcam 1
   Type: webcam
   Source: 0

2. IP Camera 192.168.1.100:8080
   Type: ip_camera
   Source: http://admin:****@192.168.1.100:8080/stream

Proceed with these cameras? (y/n): y
```

### Step 5: Monitor Detection
```
================================================================================
                            DETECTION STATS
================================================================================

Webcam 1 (webcam):
  Frames: 1524
  Weapons Detected: 3
  Alerts Sent: 3
  FPS: 29.8
  Last Detection: 2025-05-15T12:05:32.123456

IP Camera 192.168.1.100:8080 (ip_camera):
  Frames: 1512
  Weapons Detected: 1
  Alerts Sent: 1
  FPS: 28.5
  Last Detection: 2025-05-15T12:05:28.987654

================================================================================
```

## Troubleshooting

### Issue: "No cameras found"
**Solutions:**
- For webcams: Check camera permissions and if camera is not already in use
- For IP cameras: Test connectivity with `ping 192.168.1.100`
- For streams: Verify URL format and network access

### Issue: Low FPS on Multiple Cameras
**Solutions:**
- Switch from CPU to GPU: `--device gpu`
- Reduce resolution at camera source if possible
- Reduce confidence threshold: `--conf 0.7`
- Check CPU usage and available resources

### Issue: Connection Timeout for IP Cameras
**Solutions:**
- Verify IP address is correct
- Check firewall allows port 8080 (or your port)
- Test with browser: `http://192.168.1.100:8080/stream`
- Check camera stream path (may vary by manufacturer)

### Issue: Alert Frequency Issues
**Solutions:**
- Adjust cooldown: `--cooldown 30` (seconds between alerts)
- Adjust persistence: `--persist_frames 5` (frames before alert)

## Performance Tips

1. **GPU Acceleration**: Use GPU for YOLO if available
   ```bash
   python main.py multi --device gpu
   ```

2. **Balance Quality vs Speed**: Lower confidence threshold = more detections
   ```bash
   python main.py multi --conf 0.7  # More sensitive
   ```

3. **Limit VLM Usage**: VLM queries are slower, use selectively
   ```bash
   python main.py multi --use_vlm false
   ```

4. **Resource Monitoring**: Monitor system resources
   - Watch CPU/memory per thread
   - Each camera adds ~20-30% overhead (CPU-based)
   - GPU-based: minimal per-camera overhead

## Advanced Configuration

### Running with Environment Variables
Create `.env` file in `weapon_detection/` folder:

```env
ALERT_EMAIL_SENDER=your-email@gmail.com
ALERT_EMAIL_PASS=your-app-password
ALERT_TELEGRAM_BOT_TOKEN=your-bot-token
ALERT_TELEGRAM_CHAT_ID=your-chat-id
```

Then run:
```bash
python main.py multi
```

### Programmatic Usage

```python
from weapon_detection.multi_camera_runner import MultiCameraDetectionRunner
from weapon_detection.config import AppConfig, InferenceConfig, EmailConfig, TelegramConfig, VLMConfig
from weapon_detection.camera_source import CameraInfo, CameraSourceType

# Create camera configs
cameras = [
    CameraInfo(
        source_id="webcam_0",
        name="Front Door Webcam",
        source_type=CameraSourceType.WEBCAM,
        connection_string="0"
    ),
    CameraInfo(
        source_id="ipcam_lobby",
        name="Lobby IP Camera",
        source_type=CameraSourceType.IP_CAMERA,
        connection_string="http://192.168.1.100:8080/stream"
    ),
]

# Create config
config = AppConfig(
    inference=InferenceConfig(device="gpu", conf=0.9),
    email=EmailConfig(sender="alert@example.com"),
    telegram=TelegramConfig(bot_token="TOKEN"),
    vlm=VLMConfig(use_vlm=False),
)

# Run detection
runner = MultiCameraDetectionRunner(config, cameras)
runner.run()
```

## Migration from Single to Multi-Camera

If you have existing single-camera setup:

1. **Keep Single Mode**: Commands still work the same
   ```bash
   python main.py --source 0 --device gpu
   ```

2. **Switch to Multi Mode**: Simply use `multi` command
   ```bash
   python main.py multi
   ```

3. **Mix Both**: Run single camera in one terminal, multi-camera in another

## Next Steps - UI Integration

The multi-camera terminal system is ready. UI integration will include:
- Web dashboard for camera management
- Real-time feed display
- Alert timeline per camera
- Statistics dashboard
- Configuration management interface

For now, all multi-camera functionality is terminal-based with robust threading and management.
