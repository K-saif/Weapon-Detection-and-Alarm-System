"""CLI entrypoint for the weapon detection application."""

import logging

from weapon_detection.config import build_default_config, parse_args
from weapon_detection.runner import WeaponDetectionRunner


def main() -> None:
    """Runs CLI startup and starts detection pipeline."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    args = parse_args()
    config = build_default_config(args)
    logging.getLogger("weapon-detect").debug("Configs are: %s", config)
    WeaponDetectionRunner(config).run()
