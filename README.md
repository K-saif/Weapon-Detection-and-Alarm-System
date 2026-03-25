<div align="center">

# Weapon Detection and Alarm System

Real-time weapon detection with tracking, cooldown-based alerts, persistence filtering, and multi-channel notifications (Email, Telegram). Also Supports VLM for better insights of the incidents.

</div>

**Note**: This project initally implemented by using yolov5 for detection, now the current repo supports yolov8, yolo11 and yolo26. ignore yolov5 folder as it is no longer needed.

## <div>Quick Start</div>

<details open>
<summary><strong>Install</strong></summary>

Create a Python environment (recommended) and install dependencies:

```bash
pip install ultralytics opencv-python requests
```

> Notes:
> - `ultralytics` is used by the runtime pipeline in `main.py`.
> - `requests` is required for Telegram alerts.

</details>

<details open>
<summary><strong>Setup Alerts</strong></summary>

#### Gmail Setup
1. Enable **2-Step Verification** in your [Google Account](https://myaccount.google.com/security)
2. Go to **App Passwords** (search in account settings)
3. Generate a new app password for "Mail"
4. Use this 16-character password as `ALERT_EMAIL_PASS`

#### Telegram Setup
1. Message [@BotFather](https://t.me/BotFather) on Telegram → send `/newbot`
2. Follow prompts to name your bot and get the **bot token**
3. Start a chat with your bot (send any message)
4. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
5. Find `"chat":{"id":XXXXXX}` — that number is your **chat ID**

Create a `.env` file in the `weapon_detection/` folder:

```bash
# weapon_detection/.env

# Email Configuration
ALERT_SMTP_SERVER=smtp.gmail.com
ALERT_SMTP_PORT=587
ALERT_EMAIL_SENDER=youremail@gmail.com
ALERT_EMAIL_PASS=your_16char_app_password
ALERT_EMAIL_RECEIVER=alert_receiver@gmail.com

# Telegram Configuration
ALERT_TELEGRAM_BOT_TOKEN=your_bot_token
ALERT_TELEGRAM_CHAT_ID=your_chat_id
```

> **Tip**: Leave a value empty to disable that channel.

</details>

<details open>
<summary><strong>Supported Inputs</strong></summary>

| Input | `--source` |
|---|---|
| Webcam | `0` (default) |
| Video file | `path/to/video.mp4` |
| RTSP stream | `rtsp://user:pass@ip:554/stream` |
| HTTP stream | `http://ip:8080/video` |

> Single images and image directories are **not** supported — the pipeline requires a continuous frame stream.

</details>

<details open>
<summary><strong>Run Detection</strong></summary>

```bash
# Webcam
python main.py --source 0 --conf 0.8

# Video file
python main.py --source path/to/video.mp4 --conf 0.8

# RTSP camera
python main.py --source rtsp://user:pass@192.168.1.10:554/stream 
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
- `weapon_detection/channels.py`: Email and Telegram alert channels.
- `weapon_detection/dispatcher.py`: async channel fan-out dispatcher.
- `weapon_detection/tracking.py`: persistence/cooldown/stale track lifecycle.
- `weapon_detection/runner.py`: end-to-end detection and alert orchestration.
- `weapon_detection/cli.py`: app startup and logging bootstrap.

## <div>CLI Options</div>

```bash
python main.py \
  --weights models/best.pt \
  --source 0 \
  --conf 0.8 \
  --alert-classes 0 1 \
  --persist-frames 8 \
  --cooldown 60 \
  --stale-frames 30 \
  --output-dir alerts \
  --workers 4 \
  --use_vlm False \
  --vlm_model llava/paligrmma
```



## <div>Troubleshooting</div>

- If `cv2` is missing: `pip install opencv-python`
- If `ultralytics` is missing: `pip install ultralytics`
- If Telegram alert is skipped: install `requests` and set Telegram env vars.

## <div>License</div>

This project is licensed under the [MIT License](LICENSE).
