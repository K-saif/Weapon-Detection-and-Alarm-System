# Simple Dashboard - Quick Start

A lightweight web-based dashboard for real-time weapon detection with integrated inference engine.

## ✨ Features

✅ **Integrated Detection** - Full inference runs on dashboard start  
✅ Simple, clean dark UI  
✅ Real-time detection display  
✅ Input source selection (webcam, video file, RTSP stream)  
✅ Live alert display  
✅ Minimal dependencies  
✅ Single command to run (no need for two terminals!)

## 📦 Installation

```bash
pip install -r requirements.txt
```

This installs:
- `flask` - Web server
- `flask-cors` - Cross-origin requests  
- `opencv-python` - Video processing
- `ultralytics` - YOLO detection
- Other dependencies

## 🚀 Quick Start (ONE Command!)

### Windows
```bash
run_dashboard.bat
```

### Linux/Mac
```bash
./run_dashboard.sh
```

### Manual Start
```bash
python app.py
```

Then open: **http://localhost:5000**

## 📖 Usage

1. **Open Dashboard**: Go to http://localhost:5000
2. **Select Input Source**: 
   - Choose from dropdown (Webcam/Camera/Video/RTSP)
   - Or enter custom path
3. **Click "▶️ Start"**: Detection begins immediately
4. **View Results**:
   - Real-time detections displayed
   - Frame count updates in real-time
   - Recent alerts shown below
5. **Click "⏹️ Stop"**: Stop detection

**That's it!** No need to run separate commands.

## 📁 Project Structure

```
.
├── app.py                      # Flask + Detection (integrated)
├── models/
│   └── best.pt                 # YOLO model
├── templates/
│   └── index.html              # Dashboard UI
├── alerts/
│   └── Alert_history.json      # Alert history
├── run_dashboard.bat           # Windows launcher
├── run_dashboard.sh            # Linux/Mac launcher
└── requirements.txt            # Dependencies
```

## 🔌 API Endpoints

- `GET /` - Dashboard page
- `GET /api/detections` - Current detections & frames
- `GET /api/alerts` - Recent alerts
- `GET /api/stats` - Detection statistics  
- `POST /api/start` - Start detection with source
- `POST /api/stop` - Stop detection
- `GET /api/config` - Get configuration
- `POST /api/config` - Update configuration

## 🎥 Supported Sources

| Input | Example | Usage |
|-------|---------|-------|
| Webcam | `0` | Default camera |
| Camera | `/dev/video0` | Specific camera |
| Video | `video.mp4` | Video file path |
| RTSP | `rtsp://...` | IP camera stream |
| Image | `image.jpg` | Single image |

## ⚙️ How It Works

1. **Dashboard Runs**: Flask server starts on port 5000
2. **You Click Start**: Selects source and starts detection thread
3. **Live Inference**: YOLO model processes frames in background
4. **Real-Time Display**: Results update every 500ms on dashboard
5. **Auto-Save**: Detections logged to `alerts/Alert_history.json`

## 🆘 Troubleshooting

**"Models/best.pt not found"?**
- Make sure model file exists: `ls models/best.pt`

**Webcam not detected?**
- Try `0` for default webcam
- Try `/dev/video0` on Linux
- Check if another app is using camera

**Port 5000 already in use?**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

**Slow detection?**
- Check GPU availability (CUDA)
- Reduce image size in config
- Lower confidence threshold

## ⚡ Performance

- Real-time processing on CPU
- GPU acceleration available (if installed)
- ~30 FPS on modern GPU
- ~5-10 FPS on CPU

## 📝 Notes

- Dashboard updates every 500ms
- Alerts refresh every 2 seconds
- Supports webcam, video files, and streaming sources
- All detections logged automatically
