# UI Installation Instructions

## Option 1: Streamlit Web UI (Recommended)

Streamlit provides a modern, interactive web dashboard.

### Installation
```bash
pip install streamlit
```

### Running the UI
```bash
streamlit run streamlit_app.py
```

This will open in your browser at `http://localhost:8501`

### Features
- 📊 Dashboard with detection statistics
- 🎥 Live detection interface
- ⚙️ Configuration panel for alerts and detection
- 📋 Alert history with filtering and export
- ℹ️ System status and about page

---

## Option 2: Quick Start Script

Run both the detection backend and UI together:

```bash
# Terminal 1: Start detection
python main.py --source 0 --vlm qwen

# Terminal 2: Start web dashboard
streamlit run streamlit_app.py
```

---

## Usage Guide

### Dashboard
- View total detections and today's stats
- See recent alerts in real-time
- Monitor system status

### Live Detection
- Configure confidence threshold (0-1)
- Select input source (webcam, video, image)
- Adjust detection parameters

### Configuration
- Select detection classes (knife, gun, pistol)
- Enable/configure email alerts
- Enable/configure Telegram alerts
- Choose VLM model (LLaVA, PaliGemma, Qwen)

### Alert History
- View all detected weapons
- Filter by class and time range
- Export alerts to CSV
- Sort by newest or oldest

---

## Example Commands

```bash
# Run with webcam and Telegram alerts
python main.py --source 0 --alert-channels telegram

# Run with video file
python main.py --source video.mp4

# Run with VLM analysis
python main.py --source 0 --vlm qwen

# Run with custom confidence threshold
python main.py --source 0 --conf 0.6

# Start UI only (if detection is running separately)
streamlit run streamlit_app.py
```
