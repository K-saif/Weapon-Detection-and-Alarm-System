# UI Documentation - Weapon Detection System

## Overview
The Weapon Detection System provides a modern, responsive web-based interface for real-time weapon detection monitoring and alert management.

## Pages

### 1. Dashboard (`/`)
**Main monitoring interface** for the weapon detection system.

**Features:**
- **Live Video Feed** - Real-time camera stream with detection overlays
- **Detection Statistics** - Total detections, confidence metrics, and tracking information
- **System Status** - Current system state and operational information
- **Quick Actions** - Buttons to start/stop detection, access alerts, and system settings
- **Performance Metrics** - FPS, processing time, and detection accuracy

**Controls:**
- Use the control panel to manage detection parameters
- Access detailed alert history from the dashboard
- Monitor system performance in real-time

### 2. Alerts History (`/alerts`)
**Comprehensive alert management** interface for viewing all detected weapon alerts.

**Features:**
- **Alert Cards Grid** - Visual card layout showing all weapon detection alerts
- **Alert Thumbnails** - Snapshot previews of each detected weapon
- **Filtering Options** - Sort by newest/oldest/confidence and filter by confidence levels
- **Statistics Bar** - Displays total alerts, average confidence, and unique detections
- **Image Lightbox** - Click on alert thumbnails to view full-sized images with navigation
- **Alert Details Modal** - View complete alert information including:
  - Confidence score
  - Track ID
  - Frame number
  - Snapshot path
  - Timestamp
  - All additional metadata from the alert JSON

**Controls:**
- **Sort By** - Newest First, Oldest First, Highest Confidence
- **Filter** - All Alerts, High Confidence (>90%), Medium Confidence (70-90%)
- **Refresh** - Manually refresh the alert list
- **Clear All** - Remove all alerts from history
- **Download** - Save individual alert snapshots
- **Details** - View complete alert information in a modal
- **Image Preview** - Click thumbnails to open lightbox viewer with keyboard navigation

**Keyboard Shortcuts (in Lightbox/Details):**
- `Escape` - Close modal
- `Arrow Left/Right` - Navigate between images (lightbox only)

## Styling & Theme

**Color Scheme:**
- Primary Background: `#0a0e27` (Dark Blue)
- Secondary Background: `#1a1f3a` (Lighter Blue)
- Accent Color: `#667eea` (Purple Blue Gradient)
- Danger Color: `#ef4444` (Red)
- Text: `#e0e0e0` (Light Gray)

**Design Features:**
- Modern gradient headers
- Dark theme optimized for 24/7 monitoring
- Responsive grid layouts
- Smooth hover transitions and animations
- Card-based component design

## API Endpoints

The UI communicates with the backend API at `http://localhost:5000/api`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/alerts` | GET | Retrieve all alerts |
| `/api/clear-alerts` | POST | Clear all alerts from history |
| `/api/status` | GET | Get system status (dashboard) |
| `/api/stream` | GET | Video stream endpoint |

## File Structure

```
templates/
├── index.html       # Dashboard page
└── alerts.html      # Alerts history page
```

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (responsive design)

## Features Overview

### Alert Cards
Each alert card displays:
- Detection snapshot (if available)
- Weapon detection badge
- Confidence percentage
- Track ID
- Frame number
- Download and Details buttons

### Image Lightbox
- Navigate between alert images
- View metadata (confidence, track ID, frame)
- Click outside or press Escape to close
- Arrow keys for navigation

### Details Modal
- Displays all fields from alert JSON
- Formatted field names and values
- Image preview integration
- Scrollable for long content

## Customization

To modify the UI theme or styling:
1. Edit CSS variables in the `<style>` sections
2. Update color values for theme changes
3. Modify responsive breakpoints for different screen sizes

## Performance Considerations

- Auto-refresh alerts every 5 seconds
- Lazy loading for images
- Optimized CSS animations
- Minimal DOM operations
- Efficient event handling

---

**Version:** 1.0  
**Last Updated:** April 2026
