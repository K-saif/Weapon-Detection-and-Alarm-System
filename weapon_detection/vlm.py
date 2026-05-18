import torch
import logging
from PIL import Image
from transformers import (
    AutoProcessor,
    LlavaForConditionalGeneration,
    BitsAndBytesConfig,
    AutoModelForImageTextToText,
    PaliGemmaProcessor,
    PaliGemmaForConditionalGeneration,
)
LOGGER = logging.getLogger("weapon-detect")
device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    model_id = "llava-hf/llava-1.5-7b-hf"
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
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

def query_model(image, model, processor):
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



# ------------------ Qwen Model Functions ------------------
def load_model_qwen():
    LOGGER.debug("Loading Qwen model")
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")
    model = AutoModelForImageTextToText.from_pretrained(
        "Qwen/Qwen2.5-VL-3B-Instruct",
        torch_dtype=torch.float16
    ).to(device)
    model.eval()
    LOGGER.debug("Qwen model loaded")
    return model, processor

def query_model_qwen(image, model, processor):
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


# ------------------ PaliGemma Model Functions ------------------
def load_model_pali():
    model_id = "google/paligemma2-3b-mix-448"
    LOGGER.debug("Loading PaliGemma model")
    model = PaliGemmaForConditionalGeneration.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    ).eval()
    processor = PaliGemmaProcessor.from_pretrained(model_id)
    LOGGER.debug("PaliGemma model loaded")
    return model, processor

def query_model_pali(image, model, processor):
    prompt = "<image> color of the person's cloth."
    # process inputs
    model_inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    ).to(model.device)
    # ⚠️ bfloat16 conversion only if GPU supports it
    model_inputs = {k: v.to(torch.bfloat16) if v.dtype == torch.float32 else v for k, v in model_inputs.items()}
    input_len = model_inputs["input_ids"].shape[-1]
    # inference
    with torch.inference_mode():
        generation = model.generate(
            **model_inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7
        )
        # remove prompt tokens
        generation = generation[0][input_len:]
        decoded = processor.decode(generation, skip_special_tokens=True)
    return decoded