import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from transformers.image_utils import load_image

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


def query_model_qwen(image, model, processor):
    image = load_image(image).convert("RGB")
    prompt = "you are an export image analyst working in crime branch. in short, describe the appearance (cloths color, style, and skin color, beard, hair color etc.) of the person holding the weapon and keep the answer short"

    # # 🔄 Prepare inputs
    # inputs = processor.apply_chat_template(
    #     messages,
    #     add_generation_prompt=True,
    #     tokenize=True,
    #     return_dict=True,
    #     return_tensors="pt",
    # )

    # inputs = {k: v.to(device) for k, v in inputs.items()}

    # # 🚀 Generate response
    # with torch.no_grad():
    #     outputs = model.generate(
    #         **inputs,
    #         max_new_tokens=60,
    #         do_sample=False
    #     )

    # response = processor.decode(
    #     outputs[0][inputs["input_ids"].shape[-1]:]
    # )

    # return response

        # process inputs
    model_inputs = processor(
        text=prompt,
        images=image,
        return_tensors="pt"
    ).to(model.device)

    # ⚠️ bfloat16 conversion only if GPU supports it
    model_inputs = {k: v.to(device) for k, v in model_inputs.items()}

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