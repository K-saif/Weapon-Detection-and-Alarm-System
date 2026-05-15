"""CLI entrypoint for the weapon detection application."""

import logging
import sys

from weapon_detection.config import build_default_config, parse_args
from weapon_detection.runner import WeaponDetectionRunner


def main() -> None:
    """Runs CLI startup and starts detection pipeline."""
    print("Starting Weapon Detection and Alarm System...")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    
    logger = logging.getLogger("weapon-detect")
    
    print(sys.argv)
    # Check if multi-camera mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == "multi":
        # Route to multi-camera CLI
        from weapon_detection.multi_camera_cli import main_multi_camera
        # Remove "multi" from argv before passing to multi_camera_cli
        sys.argv.pop(1)
        print("Starting in multi-camera mode...")
        main_multi_camera()
    else:
        # Single camera mode (original behavior)
        args = parse_args()
        config = build_default_config(args)
        logger.debug("Configs are: %s", config)
        WeaponDetectionRunner(config).run()
