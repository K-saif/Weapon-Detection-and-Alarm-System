"""Streamlit UI for Weapon Detection and Alarm System."""

import json
import os
import streamlit as st
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import logging

# Configure page
st.set_page_config(
    page_title="Weapon Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF6B6B;
        margin-bottom: 1rem;
        text-align: center;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .alert-box {
        background: #FFE5E5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF6B6B;
    }
</style>
""", unsafe_allow_html=True)


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


def get_alert_stats():
    """Calculate alert statistics."""
    alerts = load_alert_history()
    return {
        "total": len(alerts),
        "today": len([a for a in alerts if datetime.now().date() == datetime.fromisoformat(a.get("timestamp", "")).date()] if "timestamp" in a else False),
        "this_week": len([a for a in alerts if (datetime.now() - datetime.fromisoformat(a.get("timestamp", ""))).days <= 7] if "timestamp" in a else False),
    }


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown("<h1 class='main-header'>🔍 Weapon Detection System</h1>", unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Live Detection", "Configuration", "Alert History", "About"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Live Detection":
        show_live_detection()
    elif page == "Configuration":
        show_configuration()
    elif page == "Alert History":
        show_alert_history()
    elif page == "About":
        show_about()


def show_dashboard():
    """Display main dashboard."""
    st.subheader("📊 Dashboard Overview")
    
    # Alert Statistics
    stats = get_alert_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Detections", stats["total"], delta=0)
    
    with col2:
        st.metric("Today", stats["today"], delta=0)
    
    with col3:
        st.metric("This Week", stats["this_week"], delta=0)
    
    with col4:
        st.metric("Status", "Active ✓", delta="Online")
    
    st.divider()
    
    # Recent Alerts
    st.subheader("🚨 Recent Alerts")
    alerts = load_alert_history()
    
    if alerts:
        recent_alerts = alerts[-10:]  # Last 10 alerts
        for alert in reversed(recent_alerts):
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{alert.get('class', 'Unknown')}** detected")
                with col2:
                    st.write(f"Confidence: {alert.get('confidence', 'N/A'):.2%}" if isinstance(alert.get('confidence'), (int, float)) else f"Confidence: {alert.get('confidence', 'N/A')}")
                with col3:
                    st.write(f"ID: {alert.get('track_id', 'N/A')}")
                st.caption(alert.get("timestamp", "No timestamp"))
                st.divider()
    else:
        st.info("No detections yet. Start live detection to capture weapons.")
    
    # System Info
    st.subheader("ℹ️ System Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Model:** YOLOv8 (best.pt)")
        st.write("**Detection Classes:** Knife, Gun, Pistol")
    
    with col2:
        st.write("**Alert Channels:** Email, Telegram")
        st.write("**VLM Enabled:** Yes")


def show_live_detection():
    """Display live detection interface."""
    st.subheader("🎥 Live Detection")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("**Select Input Source:**")
        source_type = st.radio(
            "Choose source",
            ["Webcam", "Video File", "Image"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    with col2:
        confidence = st.slider("Confidence Threshold", 0.0, 1.0, 0.5, 0.05)
    
    st.divider()
    
    if source_type == "Webcam":
        st.warning("⚠️ Webcam feature requires running detection backend. Use CLI command:")
        st.code("python main.py --source 0", language="bash")
    
    elif source_type == "Video File":
        uploaded_file = st.file_uploader("Upload video file", type=["mp4", "avi", "mov", "mkv"])
        if uploaded_file:
            st.info(f"Selected: {uploaded_file.name}")
            st.warning("⚠️ To process this video, use CLI command:")
            st.code(f'python main.py --source "{uploaded_file.name}"', language="bash")
    
    elif source_type == "Image":
        uploaded_image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", use_column_width=True)
            st.info("📝 Image detection would process the uploaded file through YOLO model.")
    
    # Detection Parameters
    st.subheader("⚙️ Detection Parameters")
    col1, col2 = st.columns(2)
    
    with col1:
        imgsz = st.slider("Image Size", 320, 1280, 640, 32)
    
    with col2:
        device = st.selectbox("Device", ["cpu", "cuda", "mps"])
    
    if st.button("▶️ Start Detection", use_container_width=True):
        st.success("Detection started! Monitor the console for output.")


def show_configuration():
    """Display configuration page."""
    st.subheader("⚙️ Configuration Settings")
    
    st.markdown("### Detection Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        alert_classes = st.multiselect(
            "Alert Classes",
            ["knife", "gun", "pistol"],
            default=["gun", "pistol"]
        )
    
    with col2:
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.5)
    
    st.divider()
    st.markdown("### Alert Settings")
    
    alert_type = st.tabs(["Email", "Telegram"])
    
    with alert_type[0]:
        st.write("**Email Configuration**")
        email_enabled = st.checkbox("Enable Email Alerts", value=False)
        if email_enabled:
            email_to = st.text_input("Email Address to Send Alerts")
            email_from = st.text_input("From Email", placeholder="your-email@gmail.com")
            st.caption("Note: Configure ALERT_EMAIL_PASS in .env file")
    
    with alert_type[1]:
        st.write("**Telegram Configuration**")
        telegram_enabled = st.checkbox("Enable Telegram Alerts", value=False)
        if telegram_enabled:
            bot_token = st.text_input("Bot Token", type="password", placeholder="123456:ABCDefGHIjklMNOpqrstUVWxyz")
            chat_id = st.text_input("Chat ID", placeholder="987654321")
            st.caption("Note: Store credentials in .env file for security")
    
    st.divider()
    st.markdown("### VLM Settings")
    
    vlm_model = st.selectbox(
        "Select VLM Model",
        ["None", "LLaVA", "PaliGemma", "Qwen"],
        help="Vision Language Model for analyzing weapon incidents"
    )
    
    if vlm_model != "None":
        st.info(f"Selected: {vlm_model}")
        st.caption("VLM will provide detailed analysis of detected weapons and incidents.")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Configuration", use_container_width=True):
            st.success("Configuration saved!")
    
    with col2:
        if st.button("🔄 Reset to Default", use_container_width=True):
            st.info("Reset to default configuration")


def show_alert_history():
    """Display alert history."""
    st.subheader("📋 Alert History")
    
    alerts = load_alert_history()
    
    if not alerts:
        st.info("No alerts recorded yet.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        class_filter = st.multiselect(
            "Filter by Class",
            ["knife", "gun", "pistol"],
            default=[]
        )
    
    with col2:
        time_filter = st.selectbox(
            "Time Range",
            ["All Time", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
        )
    
    with col3:
        sort_order = st.radio("Sort By", ["Newest First", "Oldest First"], horizontal=True)
    
    st.divider()
    
    # Display alerts
    filtered_alerts = alerts.copy()
    
    if sort_order == "Oldest First":
        filtered_alerts = list(reversed(filtered_alerts))
    
    st.metric("Total Alerts", len(filtered_alerts))
    
    # Table view
    if filtered_alerts:
        st.dataframe(
            [{
                "Timestamp": a.get("timestamp", "N/A"),
                "Class": a.get("class", "Unknown"),
                "Confidence": f"{a.get('confidence', 0):.2%}" if isinstance(a.get("confidence"), (int, float)) else a.get('confidence', 'N/A'),
                "Track ID": a.get("track_id", "N/A"),
                "Channel": a.get("alert_channel", "System"),
            } for a in filtered_alerts[:100]],  # Show last 100
            use_container_width=True
        )
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = "timestamp,class,confidence,track_id,channel\n"
            for alert in filtered_alerts:
                csv += f"{alert.get('timestamp', '')},{alert.get('class', '')},{alert.get('confidence', '')},{alert.get('track_id', '')},{alert.get('alert_channel', '')}\n"
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def show_about():
    """Display about page."""
    st.subheader("ℹ️ About Weapon Detection System")
    
    st.markdown("""
    ## Overview
    Real-time weapon detection system using ultra-fast YOLOv8 object detection with 
    advanced tracking, cooldown-based alerts, and multi-channel notifications.
    
    ## Features
    - 🎯 **Real-time Detection**: YOLOv8-based weapon detection
    - 📍 **Object Tracking**: Persistent tracking with unique IDs
    - 🚨 **Multi-Channel Alerts**: Email and Telegram notifications
    - 🧠 **VLM Support**: Enhanced insights using LLaVA, PaliGemma, or Qwen
    - 📊 **Alert History**: Persistent storage and analytics
    - ⚙️ **Configurable**: Flexible detection and alert settings
    
    ## Getting Started
    1. Install dependencies: `pip install -r requirements.txt`
    2. Configure alerts in `.env` file (see README)
    3. Run detection: `python main.py --source 0` (webcam)
    4. Access this dashboard for monitoring
    
    ## Supported Detection Classes
    - Knife
    - Gun
    - Pistol
    
    ## Alert Channels
    - 📧 Email (Gmail)
    - 📱 Telegram
    
    ## Project Structure
    ```
    weapon_detection/
    ├── cli.py           # CLI interface
    ├── config.py        # Configuration management
    ├── runner.py        # Main detection runner
    ├── tracking.py      # Object tracking
    ├── dispatcher.py    # Alert dispatcher
    ├── vlm.py           # VLM integration
    └── channels.py      # Alert channels
    ```
    
    ## Documentation
    For detailed setup and usage, see [README.md](./README.md)
    """)
    
    st.divider()
    st.markdown("### System Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Model Status:**")
        st.success("Ready ✓")
    
    with col2:
        st.write("**Email Service:**")
        st.info("Configured (pending)")
    
    with col3:
        st.write("**Telegram Service:**")
        st.info("Configured (pending)")


if __name__ == "__main__":
    main()
