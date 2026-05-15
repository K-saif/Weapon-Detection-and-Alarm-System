"""Camera source abstraction and enumeration."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import subprocess
import os

import cv2

LOGGER = logging.getLogger("weapon-detect")


class CameraSourceType(str, Enum):
    """Supported camera source types."""
    
    WEBCAM = "webcam"
    IP_CAMERA = "ip_camera"
    HTTPS_STREAM = "https_stream"
    RTSP_STREAM = "rtsp_stream"
    FILE = "file"
    CUSTOM_URL = "custom_url"


@dataclass
class CameraInfo:
    """Information about a camera source."""
    
    source_id: str  # unique identifier
    name: str  # display name
    source_type: CameraSourceType
    connection_string: str  # actual cv2.VideoCapture input
    metadata: dict[str, object] = None  # extra info
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class CameraSource(ABC):
    """Abstract base class for camera source discovery and management."""
    
    @abstractmethod
    def discover(self) -> list[CameraInfo]:
        """Discover available camera sources of this type."""
        pass
    
    @abstractmethod
    def validate(self, camera_info: CameraInfo) -> bool:
        """Validate that a camera source is accessible."""
        pass


class WebcamSource(CameraSource):
    """Discovers and manages webcam sources."""
    
    def discover(self) -> list[CameraInfo]:
        """Discover connected webcams."""
        cameras = []
        
        # Try indices 0-10 for common webcam configurations
        for idx in range(10):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                cameras.append(CameraInfo(
                    source_id=f"webcam_{idx}",
                    name=f"Webcam {len(cameras) + 1}",
                    source_type=CameraSourceType.WEBCAM,
                    connection_string=str(idx),
                    metadata={
                        "index": idx,
                        "width": width,
                        "height": height,
                        "fps": fps,
                    }
                ))
                cap.release()
            else:
                # Stop searching after first missing index
                if idx > 0 and not cameras:
                    break
                if cameras:
                    break
        
        return cameras
    
    def validate(self, camera_info: CameraInfo) -> bool:
        """Check if webcam is still accessible."""
        try:
            cap = cv2.VideoCapture(int(camera_info.connection_string))
            is_open = cap.isOpened()
            cap.release()
            return is_open
        except Exception:
            return False


class IPCameraSource(CameraSource):
    """Manages IP camera source discovery and validation."""
    
    def __init__(self, ip_range: str = None):
        """Initialize with IP range for discovery.
        
        Args:
            ip_range: IP range to scan (e.g., "192.168.1.1-254") or None for manual entry
        """
        self.ip_range = ip_range
    
    def discover(self) -> list[CameraInfo]:
        """Discover IP cameras on network (interactive mode).
        
        Returns an empty list; users should manually add IP cameras via add_ip_camera().
        """
        # Passive discovery - user provides IP addresses manually
        return []
    
    def add_ip_camera(self, ip: str, port: int = 8080, username: str = None,
                      password: str = None, stream_path: str = "/stream") -> CameraInfo:
        """Create an IP camera source manually.
        
        Args:
            ip: IP address of camera
            port: Camera service port (default: 8080)
            username: Optional username for authentication
            password: Optional password for authentication
            stream_path: Path to stream endpoint
            
        Returns:
            CameraInfo for the IP camera
        """
        # Build connection string
        if username and password:
            connection_string = f"http://{username}:{password}@{ip}:{port}{stream_path}"
        else:
            connection_string = f"http://{ip}:{port}{stream_path}"
        
        camera_info = CameraInfo(
            source_id=f"ipcam_{ip}",
            name=f"IP Camera {ip}:{port}",
            source_type=CameraSourceType.IP_CAMERA,
            connection_string=connection_string,
            metadata={
                "ip": ip,
                "port": port,
                "username": username,
                "stream_path": stream_path,
            }
        )
        return camera_info
    
    def validate(self, camera_info: CameraInfo) -> bool:
        """Verify IP camera is accessible via HTTP request."""
        try:
            import requests
            # Try a quick HEAD request to test connectivity
            response = requests.head(
                camera_info.connection_string,
                timeout=5
            )
            return response.status_code < 400
        except Exception as e:
            LOGGER.debug(f"IP camera validation failed: {e}")
            return False


class HTTPSStreamSource(CameraSource):
    """Manages HTTPS stream source discovery and validation."""
    
    def discover(self) -> list[CameraInfo]:
        """Discover HTTPS streams (typically empty - user provides URLs)."""
        return []
    
    def add_https_stream(self, url: str, name: str = None) -> CameraInfo:
        """Add an HTTPS stream source.
        
        Args:
            url: Full HTTPS URL to stream
            name: Display name for the stream
            
        Returns:
            CameraInfo for the HTTPS stream
        """
        if name is None:
            name = f"HTTPS Stream {url[:30]}..."
        
        return CameraInfo(
            source_id=f"https_stream_{hash(url)}",
            name=name,
            source_type=CameraSourceType.HTTPS_STREAM,
            connection_string=url,
            metadata={"url": url}
        )
    
    def validate(self, camera_info: CameraInfo) -> bool:
        """Verify HTTPS stream is accessible."""
        try:
            cap = cv2.VideoCapture(camera_info.connection_string)
            ret, _ = cap.read()
            cap.release()
            return ret
        except Exception as e:
            LOGGER.debug(f"HTTPS stream validation failed: {e}")
            return False


class RTSPStreamSource(CameraSource):
    """Manages RTSP stream source discovery and validation."""
    
    def discover(self) -> list[CameraInfo]:
        """RTSP streams are typically provided manually."""
        return []
    
    def add_rtsp_stream(self, url: str, name: str = None) -> CameraInfo:
        """Add an RTSP stream source.
        
        Args:
            url: Full RTSP URL to stream
            name: Display name for the stream
            
        Returns:
            CameraInfo for the RTSP stream
        """
        if name is None:
            name = f"RTSP Stream {url[:30]}..."
        
        return CameraInfo(
            source_id=f"rtsp_stream_{hash(url)}",
            name=name,
            source_type=CameraSourceType.RTSP_STREAM,
            connection_string=url,
            metadata={"url": url}
        )
    
    def validate(self, camera_info: CameraInfo) -> bool:
        """Verify RTSP stream is accessible."""
        try:
            cap = cv2.VideoCapture(camera_info.connection_string)
            ret, _ = cap.read()
            cap.release()
            return ret
        except Exception as e:
            LOGGER.debug(f"RTSP stream validation failed: {e}")
            return False


class FileSource(CameraSource):
    """Manages video file sources."""
    
    def discover(self) -> list[CameraInfo]:
        """Discover video files in current directory."""
        cameras = []
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
        
        for filename in os.listdir('.'):
            if os.path.splitext(filename)[1].lower() in video_extensions:
                cameras.append(CameraInfo(
                    source_id=f"file_{filename}",
                    name=f"Video File: {filename}",
                    source_type=CameraSourceType.FILE,
                    connection_string=filename,
                    metadata={"filename": filename}
                ))
        
        return cameras
    
    def validate(self, camera_info: CameraInfo) -> bool:
        """Check if video file exists and is readable."""
        try:
            cap = cv2.VideoCapture(camera_info.connection_string)
            is_open = cap.isOpened()
            cap.release()
            return is_open
        except Exception:
            return False


class CameraManager:
    """Unified camera manager for discovering and managing multiple sources."""
    
    def __init__(self):
        self.sources: dict[CameraSourceType, CameraSource] = {
            CameraSourceType.WEBCAM: WebcamSource(),
            CameraSourceType.IP_CAMERA: IPCameraSource(),
            CameraSourceType.HTTPS_STREAM: HTTPSStreamSource(),
            CameraSourceType.RTSP_STREAM: RTSPStreamSource(),
            CameraSourceType.FILE: FileSource(),
        }
        self.discovered_cameras: list[CameraInfo] = []
    
    def discover_all(self) -> list[CameraInfo]:
        """Discover all available camera sources."""
        self.discovered_cameras = []
        
        # Discover webcams
        try:
            webcams = self.sources[CameraSourceType.WEBCAM].discover()
            self.discovered_cameras.extend(webcams)
            LOGGER.info(f"Discovered {len(webcams)} webcam(s)")
        except Exception as e:
            LOGGER.error(f"Error discovering webcams: {e}")
        
        # Discover local video files
        try:
            files = self.sources[CameraSourceType.FILE].discover()
            self.discovered_cameras.extend(files)
            LOGGER.info(f"Discovered {len(files)} video file(s)")
        except Exception as e:
            LOGGER.error(f"Error discovering video files: {e}")
        
        return self.discovered_cameras
    
    def add_ip_camera(self, ip: str, port: int = 8080, username: str = None,
                      password: str = None) -> CameraInfo:
        """Add IP camera manually."""
        camera = self.sources[CameraSourceType.IP_CAMERA].add_ip_camera(
            ip, port, username, password
        )
        self.discovered_cameras.append(camera)
        return camera
    
    def add_https_stream(self, url: str, name: str = None) -> CameraInfo:
        """Add HTTPS stream manually."""
        camera = self.sources[CameraSourceType.HTTPS_STREAM].add_https_stream(url, name)
        self.discovered_cameras.append(camera)
        return camera
    
    def add_rtsp_stream(self, url: str, name: str = None) -> CameraInfo:
        """Add RTSP stream manually."""
        camera = self.sources[CameraSourceType.RTSP_STREAM].add_rtsp_stream(url, name)
        self.discovered_cameras.append(camera)
        return camera
    
    def validate_camera(self, camera_info: CameraInfo) -> bool:
        """Validate a camera source."""
        source = self.sources.get(camera_info.source_type)
        if source:
            return source.validate(camera_info)
        return False
    
    def get_cameras_by_type(self, source_type: CameraSourceType) -> list[CameraInfo]:
        """Get all discovered cameras of a specific type."""
        return [c for c in self.discovered_cameras if c.source_type == source_type]
