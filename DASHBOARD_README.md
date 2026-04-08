<div align="center">

# Dashboard UI - Real-Time Monitoring

A web-based dashboard for the Weapon Detection and Alarm System providing real-time visualization, monitoring, and management of detection events.

</div>

## Overview

The dashboard provides a centralized interface to monitor weapon detection events in real-time. It displays live video feeds with detection overlays, alert history, system statistics, and configuration management.

## Features

- **Real-Time Video Feed**: Live streaming video with detection bounding boxes and confidence scores
- **Alert Notifications**: Instant notifications when weapons are detected
- **Alert History**: Searchable and filterable log of all detection events
- **Incident Snapshots**: View captured images of detected weapons
- **System Statistics**: Real-time metrics and detection analytics
- **Configuration Panel**: Adjust detection parameters without restarting the system
- **Multi-Channel Alerts**: Monitor email and Telegram alert status
- **Track Information**: View detailed tracking data for detected objects

## Setup

### Prerequisites

Ensure you have installed the main system dependencies:

```bash
pip install -r requirements.txt
```

The dashboard requires:
- Python 3.8+
- Flask (included in requirements.txt)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. The dashboard files are already included in the project:
   - `dashboard.html` — Web UI interface
   - `app.py` — Flask backend server

2. No additional installation is required beyond the main system setup.

## Running the Dashboard

### Start the Dashboard Server

```bash
python app.py
```

The server will start on `http://localhost:5000` or the configured port.

### Access the Dashboard

Open your web browser and navigate to:

```
http://localhost:5000
```


## Configuration

### Dashboard Settings

Edit configuration in `app.py` or `.env` file (if supported):

| Setting | Description | Default |
|---------|-------------|---------|
| `HOST` | Dashboard server host | `localhost` |
| `PORT` | Dashboard server port | `5000` |
| `DEBUG` | Enable Flask debug mode | `False` |
| `UPDATE_INTERVAL` | Real-time update frequency (ms) | `1000` |

### Alert Display

The dashboard connects to the alert system through:
- `/alerts/Alert_history.json` — Alert history log
- Real-time event streaming from the detection system

## Usage Guide (Under development)

### Dashboard Layout

**Header:**
- System status indicator
- Navigation menu
- Settings access

**Main Panel:**
- Live video feed with detections
- Current frame statistics
- Active tracked objects

**Alert Section:**
- Recent alerts (last 24 hours)
- Alert statistics
- Filtered alert history

**System Info:**
- Detection model information
- FPS and latency metrics
- Connected channels status

### Viewing Alerts

1. Navigate to the **Alerts** tab
2. View the alert history table
3. Click on any alert to view:
   - Timestamp
   - Detection class and confidence
   - Snapshot of detection
   - Track ID and duration

### Filtering and Search

Use the search and filter options to find specific events:

- **Date Range**: Filter by time period
- **Confidence**: Filter by detection confidence threshold
- **Class**: Filter by detected weapon type
- **Status**: Filter by alert status (sent, pending, failed)

### Configuration Panel

Access system settings from the dashboard:

1. Click **Settings** in the header
2. Adjust detection parameters:
   - Confidence threshold
   - Persistence frames
   - Cooldown duration
   - Alert channels
3. Changes take effect immediately or on next detection cycle


## API Endpoints (Advanced)

If you want to integrate the dashboard with external systems, the following endpoints are available:

| Endpoint | Method | Description |
|----------|--------|---|
| `/api/alerts` | GET | Get alert history |
| `/api/stats` | GET | Get system statistics |
| `/api/video` | GET | Get video stream |
| `/api/config` | GET/POST | Get/update configuration |

## Development

### Frontend

The dashboard frontend is built with:
- **HTML5** for structure
- **CSS3** for styling and responsive design
- **JavaScript (Vanilla JS)** for interactivity and real-time updates

### Backend

The backend (`app.py`) uses:
- **Flask** for web server
- **JSON** for data interchange
- **Threading** for real-time updates

### Customization

To customize the dashboard:

1. Edit `dashboard.html` for UI changes
2. Modify `app.py` for backend logic
3. Update styles in the `<style>` section
4. Add new API endpoints as needed

## Future Enhancements

- Export reports and incident logs
- User authentication and role-based access
- Multi-user support with permissions
- Advanced analytics and heatmaps
- Mobile-responsive design improvements
- Integration with external alerting systems
- Machine learning-based anomaly detection
- Database backend for scalability

## Support

For issues or feature requests related to the dashboard:

1. Check the [main README](README.md) for general system documentation
2. Review troubleshooting section above
3. Open an issue in the project repository

## License

This dashboard is part of the Weapon Detection and Alarm System, licensed under the [MIT License](LICENSE).
