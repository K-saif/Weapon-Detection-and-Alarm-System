<div align="center">

# Weapon Detection and Alarm System

Real-time weapon detection with tracking, cooldown-based alerts, persistence filtering, and multi-channel notifications (Email, Telegram, SMS).

</div>

**Note**: This project initally used yolov5 for detection, now the current repo uses yolov8, yolo11 and yolo26. ignoe yolov5 folder as it is no longer used.

## <div>Quick Start</div>

<details open>
<summary><strong>Install</strong></summary>

Create a Python environment (recommended) and install dependencies:

```bash
pip install ultralytics opencv-python requests twilio
```

> Notes:
> - `ultralytics` is used by the runtime pipeline in `main.py`.
> - `requests` is required for Telegram alerts.
> - `twilio` is required for SMS alerts.

</details>

<details open>
<summary><strong>Run Detection</strong></summary>

Run with webcam:

```bash
python main.py --weights best.pt --source 0 --conf 0.4
```

Run with video file:

```bash
python main.py --weights best.pt --source path/to/video.mp4 --conf 0.4
```

</details>

<details>
<summary><strong>Alert Logic</strong></summary>

The pipeline includes:

- Persistence gating: object must appear for `--persist-frames` before alert.
- Cooldown timer: same track alerts again only after `--cooldown` seconds.
- Stale cleanup: track state is removed after `--stale-frames` missing frames.
- Async dispatch: alert channels run concurrently via thread pool.

</details>

## <div>Project Structure</div>

```text
main.py
weapon_detection/
  __init__.py
  cli.py
  config.py
  events.py
  channels.py
  dispatcher.py
  tracking.py
  runner.py
yolov5/
  ...
```

### Module Responsibilities

- `weapon_detection/config.py`: CLI arguments + immutable app config.
- `weapon_detection/events.py`: alert event dataclass.
- `weapon_detection/channels.py`: Email, Telegram, and Twilio SMS channels.
- `weapon_detection/dispatcher.py`: async channel fan-out dispatcher.
- `weapon_detection/tracking.py`: persistence/cooldown/stale track lifecycle.
- `weapon_detection/runner.py`: end-to-end detection and alert orchestration.
- `weapon_detection/cli.py`: app startup and logging bootstrap.

## <div>CLI Options</div>

```bash
python main.py \
  --weights best.pt \
  --source 0 \
  --conf 0.4 \
  --alert-classes 0 1 \
  --persist-frames 8 \
  --cooldown 60 \
  --stale-frames 30 \
  --output-dir alerts \
  --workers 4
```

## <div>Alert Configuration</div>

Set environment variables before running:

### Email

- `ALERT_SMTP_SERVER` (default: `smtp.gmail.com`)
- `ALERT_SMTP_PORT` (default: `587`)
- `ALERT_EMAIL_SENDER`
- `ALERT_EMAIL_PASS`
- `ALERT_EMAIL_RECEIVER`

### Telegram

- `ALERT_TELEGRAM_BOT_TOKEN`
- `ALERT_TELEGRAM_CHAT_ID`

### Twilio SMS

- `ALERT_TWILIO_ACCOUNT_SID`
- `ALERT_TWILIO_AUTH_TOKEN`
- `ALERT_TWILIO_FROM_NUMBER`
- `ALERT_TWILIO_TO_NUMBER`

## <div">Examples</div>

Only Email alerts:

```bash
set ALERT_EMAIL_SENDER=youremail@gmail.com
set ALERT_EMAIL_PASS=your_app_password
set ALERT_EMAIL_RECEIVER=alert_receiver@gmail.com
python main.py --weights best.pt --source 0
```

Email + Telegram + SMS:

```bash
set ALERT_EMAIL_SENDER=youremail@gmail.com
set ALERT_EMAIL_PASS=your_app_password
set ALERT_EMAIL_RECEIVER=alert_receiver@gmail.com
set ALERT_TELEGRAM_BOT_TOKEN=your_bot_token
set ALERT_TELEGRAM_CHAT_ID=your_chat_id
set ALERT_TWILIO_ACCOUNT_SID=your_sid
set ALERT_TWILIO_AUTH_TOKEN=your_token
set ALERT_TWILIO_FROM_NUMBER=+10000000000
set ALERT_TWILIO_TO_NUMBER=+10000000001
python main.py --weights best.pt --source 0
```

## <div>Troubleshooting</div>

- If `cv2` is missing: `pip install opencv-python`
- If `ultralytics` is missing: `pip install ultralytics`
- If Telegram alert is skipped: install `requests` and set Telegram env vars.
- If SMS alert is skipped: install `twilio` and set Twilio env vars.

## <div>License</div>

This project is licensed under the [MIT License](LICENSE).
