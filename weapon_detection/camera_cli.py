"""Interactive multi-camera selection CLI."""

import logging
import sys
from typing import Optional, Tuple

from weapon_detection.camera_source import (
    CameraManager,
    CameraSourceType,
    CameraInfo,
)

LOGGER = logging.getLogger("weapon-detect")


def print_header(title: str) -> None:
    """Print a formatted header."""
    print("\n" + "="*80)
    print(f"{title:^80}")
    print("="*80 + "\n")


def print_menu(options: list[str], title: str = "Select an option") -> int:
    """Display a menu and get user selection.
    
    Args:
        options: List of menu options
        title: Menu title
        
    Returns:
        Selected option index (0-based)
    """
    print(f"\n{title}:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): ").strip())
            if 1 <= choice <= len(options):
                return choice - 1
            print(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


def select_source_type() -> Optional[CameraSourceType]:
    """Let user select camera source type."""
    print_header("CAMERA SOURCE TYPE SELECTION")
    
    options = [
        "Webcam(s)",
        "IP Camera(s)",
        "HTTPS Stream",
        "RTSP Stream",
        "Video File",
        "Mixed (Different types)",
    ]
    
    choice = print_menu(options)
    
    source_type_map = {
        0: CameraSourceType.WEBCAM,
        1: CameraSourceType.IP_CAMERA,
        2: CameraSourceType.HTTPS_STREAM,
        3: CameraSourceType.RTSP_STREAM,
        4: CameraSourceType.FILE,
        5: None,  # Mixed mode
    }
    
    return source_type_map.get(choice)


def discover_and_select_webcams(manager: CameraManager) -> list[CameraInfo]:
    """Auto-discover and let user select webcams."""
    print("\nScanning for webcam(s)...")
    webcams = manager.sources[CameraSourceType.WEBCAM].discover()
    
    if not webcams:
        print("No webcams found!")
        return []
    
    print(f"Found {len(webcams)} webcam(s):")
    for i, cam in enumerate(webcams, 1):
        metadata = cam.metadata or {}
        print(f"  {i}. {cam.name} (ID: {cam.source_id})")
        if metadata:
            print(f"     Resolution: {metadata.get('width')}x{metadata.get('height')}, "
                  f"FPS: {metadata.get('fps')}")
    
    # Ask to select
    selected = []
    while True:
        try:
            choice_input = input("\nSelect webcam(s) to use (comma-separated numbers, e.g., '1,2'): ").strip()
            if not choice_input:
                break
            
            choices = [int(x.strip()) - 1 for x in choice_input.split(",")]
            for idx in choices:
                if 0 <= idx < len(webcams):
                    selected.append(webcams[idx])
                else:
                    print(f"Invalid index: {idx + 1}")
            
            if selected:
                break
        except ValueError:
            print("Invalid input. Please enter comma-separated numbers.")
    
    return selected


def add_ip_cameras_interactive(manager: CameraManager) -> list[CameraInfo]:
    """Interactively add IP camera(s)."""
    print_header("IP CAMERA CONFIGURATION")
    
    cameras = []
    print("Add IP camera(s). Enter 'done' when finished.\n")
    
    while True:
        print(f"\nCamera {len(cameras) + 1}:")
        
        ip = input("  Enter IP address (or 'done' to finish): ").strip()
        if ip.lower() == 'done':
            break
        
        if not ip:
            print("  IP address cannot be empty!")
            continue
        
        try:
            port_input = input("  Enter port (default: 8080): ").strip()
            port = int(port_input) if port_input else 8080
        except ValueError:
            print("  Invalid port number. Using default: 8080")
            port = 8080
        
        username = input("  Enter username (optional, press Enter to skip): ").strip() or None
        password = input("  Enter password (optional, press Enter to skip): ").strip() or None
        stream_path = input("  Enter stream path (default: /stream): ").strip() or "/stream"
        
        print("  Adding IP camera...")
        camera = manager.add_ip_camera(ip, port, username, password)
        
        # Validate
        if manager.validate_camera(camera):
            print(f"  ✓ Camera validated successfully!")
            cameras.append(camera)
        else:
            print(f"  ⚠ Warning: Could not validate camera at {ip}:{port}")
            use_anyway = input("    Use anyway? (y/n): ").strip().lower()
            if use_anyway == 'y':
                cameras.append(camera)
    
    return cameras


def add_https_streams_interactive(manager: CameraManager) -> list[CameraInfo]:
    """Interactively add HTTPS stream(s)."""
    print_header("HTTPS STREAM CONFIGURATION")
    
    streams = []
    print("Add HTTPS stream(s). Enter 'done' when finished.\n")
    
    while True:
        print(f"\nStream {len(streams) + 1}:")
        
        url = input("  Enter HTTPS URL (or 'done' to finish): ").strip()
        if url.lower() == 'done':
            break
        
        if not url:
            print("  URL cannot be empty!")
            continue
        
        name = input("  Enter stream name (optional): ").strip() or None
        
        print("  Adding HTTPS stream...")
        stream = manager.add_https_stream(url, name)
        
        # Validate
        if manager.validate_camera(stream):
            print(f"  ✓ Stream validated successfully!")
            streams.append(stream)
        else:
            print(f"  ⚠ Warning: Could not validate stream")
            use_anyway = input("    Use anyway? (y/n): ").strip().lower()
            if use_anyway == 'y':
                streams.append(stream)
    
    return streams


def add_rtsp_streams_interactive(manager: CameraManager) -> list[CameraInfo]:
    """Interactively add RTSP stream(s)."""
    print_header("RTSP STREAM CONFIGURATION")
    
    streams = []
    print("Add RTSP stream(s). Enter 'done' when finished.\n")
    
    while True:
        print(f"\nStream {len(streams) + 1}:")
        
        url = input("  Enter RTSP URL (or 'done' to finish): ").strip()
        if url.lower() == 'done':
            break
        
        if not url:
            print("  URL cannot be empty!")
            continue
        
        name = input("  Enter stream name (optional): ").strip() or None
        
        print("  Adding RTSP stream...")
        stream = manager.add_rtsp_stream(url, name)
        
        # Validate
        if manager.validate_camera(stream):
            print(f"  ✓ Stream validated successfully!")
            streams.append(stream)
        else:
            print(f"  ⚠ Warning: Could not validate stream")
            use_anyway = input("    Use anyway? (y/n): ").strip().lower()
            if use_anyway == 'y':
                streams.append(stream)
    
    return streams


def discover_and_select_video_files(manager: CameraManager) -> list[CameraInfo]:
    """Auto-discover and let user select video files."""
    print("\nScanning for video files...")
    files = manager.sources[CameraSourceType.FILE].discover()
    
    if not files:
        print("No video files found!")
        return []
    
    print(f"Found {len(files)} video file(s):")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file.name}")
    
    # Ask to select
    selected = []
    while True:
        try:
            choice_input = input(
                "\nSelect file(s) to use (comma-separated numbers, e.g., '1,2'): "
            ).strip()
            if not choice_input:
                break
            
            choices = [int(x.strip()) - 1 for x in choice_input.split(",")]
            for idx in choices:
                if 0 <= idx < len(files):
                    selected.append(files[idx])
                else:
                    print(f"Invalid index: {idx + 1}")
            
            if selected:
                break
        except ValueError:
            print("Invalid input. Please enter comma-separated numbers.")
    
    return selected


def select_cameras_interactive() -> list[CameraInfo]:
    """Interactively select cameras for detection."""
    print_header("WEAPON DETECTION - MULTI-CAMERA SETUP")
    
    manager = CameraManager()
    selected_cameras = []
    
    source_type = select_source_type()
    
    if source_type == CameraSourceType.WEBCAM:
        selected_cameras = discover_and_select_webcams(manager)
    
    elif source_type == CameraSourceType.IP_CAMERA:
        selected_cameras = add_ip_cameras_interactive(manager)
    
    elif source_type == CameraSourceType.HTTPS_STREAM:
        selected_cameras = add_https_streams_interactive(manager)
    
    elif source_type == CameraSourceType.RTSP_STREAM:
        selected_cameras = add_rtsp_streams_interactive(manager)
    
    elif source_type == CameraSourceType.FILE:
        selected_cameras = discover_and_select_video_files(manager)
    
    elif source_type is None:  # Mixed mode
        print_header("MIXED SOURCE MODE")
        
        # Webcams
        use_webcams = input("Include webcams? (y/n): ").strip().lower() == 'y'
        if use_webcams:
            selected_cameras.extend(discover_and_select_webcams(manager))
        
        # IP Cameras
        use_ip = input("Include IP cameras? (y/n): ").strip().lower() == 'y'
        if use_ip:
            selected_cameras.extend(add_ip_cameras_interactive(manager))
        
        # HTTPS Streams
        use_https = input("Include HTTPS streams? (y/n): ").strip().lower() == 'y'
        if use_https:
            selected_cameras.extend(add_https_streams_interactive(manager))
        
        # RTSP Streams
        use_rtsp = input("Include RTSP streams? (y/n): ").strip().lower() == 'y'
        if use_rtsp:
            selected_cameras.extend(add_rtsp_streams_interactive(manager))
        
        # Video Files
        use_files = input("Include video files? (y/n): ").strip().lower() == 'y'
        if use_files:
            selected_cameras.extend(discover_and_select_video_files(manager))
    
    return selected_cameras


def display_selected_cameras(cameras: list[CameraInfo]) -> None:
    """Display summary of selected cameras."""
    print_header("SELECTED CAMERAS")
    
    if not cameras:
        print("No cameras selected!")
        return
    
    for i, cam in enumerate(cameras, 1):
        print(f"{i}. {cam.name}")
        print(f"   Type: {cam.source_type.value}")
        print(f"   Source: {cam.connection_string}")
        print()
