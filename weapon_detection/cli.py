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
    args = parse_args()
    config = build_default_config(args)
    WeaponDetectionRunner(config).run()
