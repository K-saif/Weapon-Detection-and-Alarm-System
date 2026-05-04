<div align="center">

# Weapon Detection and Alarm System

By using Ultralytics YOLO real-time weapon detection with tracking, cooldown-based alerts, persistence filtering, and multi-channel notifications (**Email**, **Telegram**). This Repo also Supports VLMs (**LLaVA**, **PaliGemma**, **Qwen**) for better insights of the incidents .

</div>


## <div>Quick Start</div>

<details open>
<summary><strong>Clone and Install</strong></summary>

```bash
git clone https://github.com/K-saif/Weapon-Detection-and-Alarm-System.git
cd Weapon-Detection-and-Alarm-System
pip install -r requirements.txt
```

> Notes:
> - `ultralytics` is required for the detection pipeline.
> - `requests` is required for Telegram alerts.
> - `transformers` and `accelerate` are needed for VLM features.

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

| Input | `source` |
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
python main.py source=0 conf=0.8 device=cpu

# Video file
python main.py source=path/to/video.mp4 conf=0.8 device=cpu

# RTSP camera
python main.py source=rtsp://user:pass@192.168.1.10:554/stream device=gpu
```

</details>


<details>
<summary><strong>Alert Logic</strong></summary>

The pipeline includes:

- Persistence gating: object must appear for `persist_frames` before alert.
- Cooldown timer: same track alerts again only after `cooldown` seconds.
- Stale cleanup: track state is removed after `stale_frames` missing frames.
- Async dispatch: alert channels run concurrently via thread pool.

**Note:** keep cooldown high to avoid spamming alerts, especially in crowded scenes.

</details>

## <div>Training Custom Models</div>
For training custom models follow the [Ultralytics YOLO training guide](https://docs.ultralytics.com/training/). After training, paste your best.pt into [models folder](models/)  or use `weights=path/to/best.pt`.

**Note:** This model was trained only for demonstration purposes on a small custom dataset. For best results, you should train on more representative dataset of weapons in various conditions.

## <div>Project Structure</div>

```text
|--main.py
|--models/
|   |--best.pt
|--weapon_detection/
|   |--__init__.py
|   |--cli.py
|   |--config.py
|   |--events.py
|   |--channels.py
|   |--dispatcher.py
|   |--tracking.py
|   |--runner.py

  ...
```


## <div>Dashboard UI (Under Development)</div>

A web-based dashboard is currently under development to provide real-time monitoring and visualization of weapon detection events. The dashboard will offer:

- Real-time video feed with detection overlays
- Live alert notifications and history
- System configuration and management interface
- Detection statistics and insights
- Easy access to incident snapshots and logs

Check the [Dashboard README](DASHBOARD_README.md) for setup and usage details.

## <div>CLI Options</div>

| Argument | Type | Default | Description |
|----|----|---|---|
| `weights` | `str` | `models/best.pt` | Path to the YOLO model weights file. |
| `source` | `int`/ `str` | `0` | Video input source (webcam index, file path, RTSP/HTTP stream URL). |
| `device` | `str` | `cpu` | Inference device: `cpu` or `gpu`. |
| `conf` | `float` | `0.4` | Detection confidence threshold. |
| `alert_classes` | `list[int]` | `0` | Class IDs that trigger alerts (comma-separated in CLI, e.g., `0,1`). |
| `persist_frames` | `int` | `8` | Frames required before the first alert for a tracked object. |
| `cooldown` | `int` | `60` | Seconds to wait before alerting again for the same track. |
| `stale_frames` | `int` | `30` | Missing frames before tracked state is removed. |
| `output_dir` | `str` | `alerts` | Directory used for saved snapshots and alert artifacts. |
| `workers` | `int` | `4` | Maximum async worker threads for alert channels. |
| `use_vlm` | `bool` | `false` | Enable VLM querying for detected weapons. |
| `vlm_model` | `str` | `paligemma` | VLM backend to use: `llava`, `paligemma`, or `qwen`. |

Example:

```bash
python main.py source=0 device=cpu conf=0.8 output_dir=alerts
```

## Future Enhancements
- Add person detection and tracking to correlate weapons with individuals.
- Implement a web dashboard for real-time monitoring and alert management.
- Support for lightweight models like onnx or tflite for edge deployment.

## <div>Contributing</div>
Contributions are welcome! Please open an issue or submit a pull request for bug fixes, improvements, or new features.

## <div>License</div>

This project is licensed under the [MIT License](LICENSE).
