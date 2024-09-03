import torch
from PIL import Image
from diffusers import AutoPipelineForImage2Image, \
    AutoPipelineForText2Image
from ratatosk_errands.model import TextToImageInstructions, ImageToImageInstructions

from norn.huggingface import ensure_huggingface_hub_login


class StableDiffusion3TextToImage:
    def __init__(self):
        ensure_huggingface_hub_login()
        self.text_to_image_pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-3-medium-diffusers",
            device_map="balanced",
            torch_dtype=torch.float16)

    def text_to_image(self, instructions: TextToImageInstructions) -> Image:
        image = self.text_to_image_pipe(
            prompt=instructions.prompt,
            negative_prompt=instructions.negative_prompt,
            num_inference_steps=instructions.num_inference_steps,
            guidance_scale=instructions.guidance_scale,
            width=instructions.width,
            height=instructions.height
        ).images[0]
        return image


class StableDiffusion3ImageToImage:
    def __init__(self):
        ensure_huggingface_hub_login()
        self.image_to_image_pipe = AutoPipelineForImage2Image.from_pretrained(
            "stabilityai/stable-diffusion-3-medium-diffusers",
            device_map="balanced",
            torch_dtype=torch.float16)

    def image_to_image(self, instructions: ImageToImageInstructions, base_image: Image) -> Image:
        image = self.image_to_image_pipe(
            prompt=instructions.prompt,
            negative_prompt=instructions.negative_prompt,
            num_inference_steps=instructions.num_inference_steps,
            guidance_scale=instructions.guidance_scale,
            image=base_image
        ).images[0]
        return image
