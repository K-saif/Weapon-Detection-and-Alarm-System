import torch
import logging
from transformers import AutoProcessor, LlavaForConditionalGeneration, BitsAndBytesConfig
from PIL import Image

LOGGER = logging.getLogger("weapon-detect")

def load_model():
    # ------------------ CONFIG ------------------
    model_id = "llava-hf/llava-1.5-7b-hf"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )

    # ------------------ LOAD MODEL ------------------
    LOGGER.debug("Loading Llava model")

    model = LlavaForConditionalGeneration.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto",
        low_cpu_mem_usage=True,
        max_memory={0: "7GiB", "cpu": "20GiB"}
    )

    processor = AutoProcessor.from_pretrained(model_id)

    LOGGER.debug("Llava model loaded")
    return model, processor

def query_model(image_path, model, processor):

    # ------------------ LOAD IMAGE ------------------
    image = Image.open(image_path).convert("RGB")

    prompt = "you are an export image analyst working in crime branch. describe the appearance (cloths color, style, and skin color, beard, hair color etc.) of the person holding the weapon"

    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ],
        },
    ]

    # process input
    inputs = processor(
        text=processor.apply_chat_template(conversation, add_generation_prompt=True),
        images=image,
        return_tensors="pt"
    )

    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    # inference
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7
        )

    # decode
    result = processor.decode(output[0], skip_special_tokens=True)

    # clean response (remove USER/ASSISTANT if present)
    if "ASSISTANT:" in result:
        result = result.split("ASSISTANT:")[-1].strip()

    LOGGER.debug("Llava response: %s", result)
    return result

