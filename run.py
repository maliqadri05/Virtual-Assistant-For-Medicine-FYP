from transformers import pipeline
from PIL import Image
import requests
import torch

pipe = pipeline(
    "image-text-to-text",
    model="google/medgemma-4b-it",
    torch_dtype=torch.bfloat16,
    device="cuda",
)

# Image attribution: Stillwaterising, CC0, via Wikimedia Commons
# image_url = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Chest_Xray_PA_3-8-2010.png"
# image = Image.open(requests.get(image_url, headers={"User-Agent": "example"}, stream=True).raw)

image_url = "Postmortem-supine-plain-chest-X-ray-No-pneumothorax-or-pleural-effusion-was-detectable.png"
image = Image.open(image_url, "r", None)

messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": "You are an expert radiologist."}]
    },
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this X-ray"},
            {"type": "image", "image": image}
        ]
    }
]

output = pipe(text=messages, max_new_tokens=200)
print(output[0]["generated_text"][-1]["content"])