import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from transformers.image_utils import load_image
from pathlib import Path
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model_qwen():
    print("Loading model...")
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")
    model = AutoModelForImageTextToText.from_pretrained(
        "Qwen/Qwen2.5-VL-3B-Instruct",
        torch_dtype=torch.float16
    ).to(device)
    model.eval()
    print("Model loaded ✅")
    return model, processor


def query_model_qwen(image_path, model, processor):
    image = Image.open(image_path).convert("RGB")

    prompt = "You are an expert crime analyst. Briefly describe the appearance (clothes, color, beard, hair, etc.) of the person holding the weapon."

    # ✅ Correct message format (VERY IMPORTANT)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    # ✅ Apply chat template
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )

    # ✅ Move to device
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=60,
            do_sample=True,
            temperature=0.7
        )

    response = processor.decode(
        outputs[0][input_len:],
        skip_special_tokens=True
    )

    return response

