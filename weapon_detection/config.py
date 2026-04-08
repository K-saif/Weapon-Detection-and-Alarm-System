"""Application configuration and CLI parsing."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()  # load .env variables for config


def _str_to_bool(value: str) -> bool:
    """Parses common CLI boolean representations."""
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value}")


def _normalize_key_value_args(raw_args: list[str], key_value_options: set[str]) -> list[str]:
    """Converts Ultralytics-like key=value tokens into argparse format."""
    normalized_args: list[str] = []
    for token in raw_args:
        if token.startswith("--") or "=" not in token:
            normalized_args.append(token)
            continue

        key, value = token.split("=", 1)
        key_name = key.strip().lstrip("-").replace("_", "-")
        if key_name not in key_value_options:
            normalized_args.append(token)
            continue

        normalized_args.append(f"--{key_name}")
        if key_name == "alert-classes":
            class_values = [part.strip() for part in value.split(",") if part.strip()]
            normalized_args.extend(class_values)
        else:
            normalized_args.append(value)
    return normalized_args

@dataclass(frozen=True)
class InferenceConfig:
    """Inference/runtime configuration."""

    source: int | str = 0
    weights: str = ""
    conf: float = 0.8
    alert_classes: tuple[int, ...] = (0, 1)
    persist_frames: int = 8
    cooldown_seconds: int = 60
    stale_frames: int = 30
    output_dir: str = "alerts"
    workers: int = 4
    device: str = "cpu"

@dataclass(frozen=True)
class EmailConfig:
    """Email alert credentials and receiver."""

    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender: str = ""
    password: str = ""
    receiver: str = ""


@dataclass(frozen=True)
class TelegramConfig:
    """Telegram bot alert configuration."""

    bot_token: str = ""
    chat_id: str = ""


@dataclass(frozen=True)
class AppConfig:
    """Application composition configuration."""

    inference: InferenceConfig
    email: EmailConfig
    telegram: TelegramConfig
    vlm: VLMConfig


@dataclass(frozen=True)
class VLMConfig:
    """VLM configuration for weapon description."""

    use_vlm: bool = False
    vlm_model: str = "paligemma"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parses CLI arguments in Ultralytics-like style."""
    parser = argparse.ArgumentParser(description="Weapon detection with scalable alerting")
    parser.add_argument("--weights", type=str, default="models/best.pt", help="model path")
    parser.add_argument("--source", type=str, default="0", help="video source")
    parser.add_argument("--conf", type=float, default=0.9, help="confidence threshold")
    parser.add_argument(
        "--alert_classes",
        type=int,
        nargs="+",
        default=[0],
        help="class ids that trigger alerts",
    )
    parser.add_argument(
        "--persist_frames",
        type=int,
        default=8,
        help="frames required before first alert",
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=60,
        help="seconds between alerts for the same track",
    )
    parser.add_argument(
        "--stale_frames",
        type=int,
        default=30,
        help="remove track state after these missing frames",
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="alerts", 
        help="snapshot directory"
        )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="max async workers for alert channels",
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["cpu", "gpu"],
        default="cpu",
        help="inference device for Ultralytics detection (cpu or gpu)",
    )
    parser.add_argument(
        "--use_vlm",
        type=_str_to_bool,
        default=False,
        help="enable VLM querying for detected weapons"
    )
    parser.add_argument(
        "--vlm_model",
        type=str,
        choices=["llava", "paligemma","qwen"],
        default="paligemma",
        help="names of the VLM models to use"
    )
    raw_args = list(sys.argv[1:] if argv is None else argv)
    key_value_options = {
        "weights",
        "source",
        "conf",
        "alert_classes",
        "persist_frames",
        "cooldown",
        "stale_frames",
        "output_dir",
        "workers",
        "device",
        "use_vlm",
        "vlm_model",
    }
    normalized_args = _normalize_key_value_args(raw_args, key_value_options)
    return parser.parse_args(normalized_args)


def build_default_config(args: argparse.Namespace) -> AppConfig:
    """Builds immutable application config from CLI args and env vars."""
    source_value: int | str
    source_value = int(args.source) if str(args.source).isdigit() else str(args.source)

    inference = InferenceConfig(
        source=source_value,
        weights=args.weights,
        conf=args.conf,
        alert_classes=tuple(args.alert_classes),
        persist_frames=args.persist_frames,
        cooldown_seconds=args.cooldown,
        stale_frames=args.stale_frames,
        output_dir=args.output_dir,
        workers=args.workers,
        device=args.device,
    )
    email = EmailConfig(
        smtp_server=os.getenv("ALERT_SMTP_SERVER", "smtp.gmail.com"),
        smtp_port=int(os.getenv("ALERT_SMTP_PORT", "587")),
        sender=os.getenv("ALERT_EMAIL_SENDER", ""),
        password=os.getenv("ALERT_EMAIL_PASS", ""),
        receiver=os.getenv("ALERT_EMAIL_RECEIVER", ""),
    )
    telegram = TelegramConfig(
        bot_token=os.getenv("ALERT_TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.getenv("ALERT_TELEGRAM_CHAT_ID", ""),
    )
    vlm = VLMConfig(
        use_vlm=args.use_vlm,
        vlm_model=args.vlm_model,
    )

    return AppConfig(
        inference=inference,
        email=email,
        telegram=telegram,
        vlm=vlm,
    )
