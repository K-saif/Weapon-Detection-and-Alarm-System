"""Multi-camera entry point."""

import logging
import sys
import argparse

from weapon_detection.config import (
    build_default_config,
    parse_args,
    AppConfig,
    InferenceConfig,
)
from weapon_detection.runner import WeaponDetectionRunner
from weapon_detection.multi_camera_runner import MultiCameraDetectionRunner
from weapon_detection.camera_source import CameraInfo, CameraSourceType
from weapon_detection.camera_cli import select_cameras_interactive, display_selected_cameras


def main_multi_camera() -> None:
    """Entry point for multi-camera detection."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    logger = logging.getLogger("weapon-detect")
    
    # Parse base CLI arguments
    args = parse_args()
    print(sys.argv)

    # Interactive multi-camera mode
    cameras = select_cameras_interactive()
    
    if not cameras:
        logger.error("No cameras selected. Exiting.")
        sys.exit(1)
    
    display_selected_cameras(cameras)
    
    confirm = input("\nProceed with these cameras? (y/n): ").strip().lower()
    if confirm != 'y':
        logger.info("Multi-camera setup cancelled.")
        sys.exit(0)
    
    # Build config from parsed args
    config = build_default_config(args)
    
    # Create MultiCameraDetectionRunner
    runner = MultiCameraDetectionRunner(config, cameras)
    runner.run()

if __name__ == "__main__":
    main_multi_camera()
