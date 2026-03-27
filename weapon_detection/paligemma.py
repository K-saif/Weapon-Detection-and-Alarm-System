from transformers import (
    PaliGemmaProcessor,
    PaliGemmaForConditionalGeneration,
)
from transformers.image_utils import load_image
import torch
import logging

LOGGER = logging.getLogger("weapon-detect")

# ------------------ LOAD MODEL ------------------
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