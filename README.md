<div align="center">

# Weapon Detection and Alarm System

By using Ultralytics YOLO real-time weapon detection with tracking, cooldown-based alerts, persistence filtering, and multi-channel notifications (**Email, Telegram**). This Repo also Supports VLMs for better insights of the incidents (**LLaVA**, **PaliGemma**, **Qwen**).

</div>


## <div>Quick Start</div>

<details open>
<summary><strong>Install</strong></summary>

Create a Python environment (recommended) and install dependencies:

```bash
pip install ultralytics opencv-python requests
```
if you have GPU resources and want to use VLM features, also install:

```bash
pip install transformers accelerate
```

> Notes:
> - `ultralytics` is required for the detection pipeline.
> - `requests` is required for Telegram alerts.
> - `transformers` and `accelerate` are needed only if using VLM features.

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
python main.py --source 0 --conf 0.8 --device cpu

# Video file
python main.py --source path/to/video.mp4 --conf 0.8 --device cpu

# RTSP camera
python main.py --source rtsp://user:pass@192.168.1.10:554/stream --device gpu
```

</details>

<details>
<summary><strong>Train Custom Model</strong></summary>

For training custom models follow the [Ultralytics YOLO training guide](https://docs.ultralytics.com/training/). After training, paste your best.pt into [models folder](models/)  or use `--weights path/to/best.pt`.

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


## <div>CLI Options</div>

```bash
python main.py \
  --weights models/best.pt \
  --source 0 \
  --device cpu \
  --conf 0.8 \
  --alert-classes 0 1 \
  --persist-frames 8 \
  --cooldown 60 \
  --stale-frames 30 \
  --output-dir alerts \
  --workers 4 \
  --use_vlm False \
  --vlm_model llava/paligrmma/qwen
```

## <div>Contributing</div>
Contributions are welcome! Please open an issue or submit a pull request for bug fixes, improvements, or new features.

## <div>License</div>

This project is licensed under the [MIT License](LICENSE).
