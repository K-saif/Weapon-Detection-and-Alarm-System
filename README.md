
<div align="center">


  **Open in**
  <br>
  <div>
    <a href="https://colab.research.google.com/drive/1u9rAhzFOoPc7SD-XDmrhU7Rv0U3lkg7B?usp=share_link"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>
    <a href="https://www.kaggle.com/saifkhan04/weapon-detection-mail-alerts"><img src="https://kaggle.com/static/images/open-in-kaggle.svg" alt="Open In Kaggle"></a>
    
  </div>

  <br>
  <p>
   It is a YOLOv5 🚀 weapon detection model trained on custom dataset for detecting the weapons in real life and alarm system.
  </p>

</div>




## <div align="center">Quick Start Examples</div>

<details open>
<summary>Install</summary>

Clone repo and install [requirements.txt](https://github.com/ultralytics/yolov5/blob/master/requirements.txt) in a
[**Python>=3.7.0**](https://www.python.org/) environment, including
[**PyTorch>=1.7**](https://pytorch.org/get-started/locally/).

```bash
git clone https://github.com/K-saif/Weapon-Detection-Mail-Alerts.git  # clone
cd Weapon-Detection-Mail-Alerts
pip install -r requirements.txt  # install
```
</details>

<details open>
<summary>Mail Bot</summary>


**Step-1:**
For sending automatic Email first we need to turn on 2-step verification to get a 16 character password that we can use to log in to Gmail using Python, follow the steps in this [Doc file](https://drive.google.com/file/d/1yLKMochNeVhoaeUE0a09QvECEYpjoBbH/view?usp=share_link).

**step-2:**
Copy and paste that password in the [auto_mail.py](https://github.com/K-saif/Weapon-Detection-Mail-Alerts/blob/bcd0e3f60c66db6210600df0eef02bed06b659f4/auto_mail.py)

<kbd>
<img align="left" width="300" height="300" src="https://user-images.githubusercontent.com/110802306/216804975-514c8388-5537-49bd-b4af-706d57198b3f.png">
</kbd>

</details>


<details>
<summary>Training</summary>
For training, use below command 

```bash
python train.py --img 640 --batch 16 --epochs 30 --data custom_data.yaml --weights '' --cache
```
Note: provide file name and path properly


<kbd>
<img align="left" width="300" height="300" src="https://user-images.githubusercontent.com/110802306/216806567-8c9ff57e-b891-44e8-b527-585b1f019c9e.png">
</kbd>



</details>

<details>
<summary>Training Results</summary>

**Graphs:**

<kbd>
<img width="800" src="https://user-images.githubusercontent.com/110802306/216755099-15837611-b1bc-47af-9a2b-da78716a3fba.png">
</kbd>

**Output:**

<kbd>
<img width="600" src="https://user-images.githubusercontent.com/110802306/216756077-d4a55c94-d15d-4b80-a179-72f89c34ab15.jpg">
</kbd>
</details>


<details>
<summary>Inference with detect.py</summary>

`detect.py` runs inference on a variety of sources and saving results to `runs/detect`.

```bash
python detect.py --source 0  # webcam
                          img.jpg  # image
                          vid.mp4  # video
                          path/  # directory
                          'path/*.jpg'  # glob
                          'https://youtu.be/'  # YouTube
                          'rtsp://abc.com/weapon.mp4'  # RTSP, RTMP, HTTP stream
```
</details>

<details>
<summary>Detection</summary>
For detection, use below command

```bash
python detect.py --weights best.pt --img 640 --conf 0.25 --source image.jpg
```
Note: provide file name and path properly
</details>



## <div align="center">Environments</div>

Get started in seconds with our verified environments. Click each icon below for details.

<div align="center">
  <a href="https://colab.research.google.com/drive/1u9rAhzFOoPc7SD-XDmrhU7Rv0U3lkg7B?usp=share_link">
    <img src="https://github.com/ultralytics/yolov5/releases/download/v1.0/logo-colab-small.png" width="10%" /></a>
  <img src="https://github.com/ultralytics/assets/raw/master/social/logo-transparent.png" width="5%" alt="" />
  <a href="https://www.kaggle.com/saifkhan04/weapon-detection-mail-alerts">
    <img src="https://github.com/ultralytics/yolov5/releases/download/v1.0/logo-kaggle-small.png" width="10%" /></a>
  <img src="https://github.com/ultralytics/assets/raw/master/social/logo-transparent.png" width="5%" alt="" />
</div>


## <div align="center">Contribute</div>

Our Contributors are,

<!-- SVG image from https://opencollective.com/ultralytics/contributors.svg?width=990 -->
<a href="https://github.com/ultralytics/yolov5/graphs/contributors"><img src="" /></a>



## <div align="center">Contact</div>
