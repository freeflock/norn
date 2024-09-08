import torch
from PIL import Image
from diffusers import AutoPipelineForImage2Image, \
    AutoPipelineForText2Image, FluxImg2ImgPipeline
from ratatosk_errands.model import TextToImageInstructions, ImageToImageInstructions

from norn.huggingface import ensure_huggingface_hub_login


class StableDiffusion3TextToImage:
    def __init__(self):
        ensure_huggingface_hub_login()
        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/stable-diffusion-3-medium-diffusers",
            device_map="balanced",
            torch_dtype=torch.float16)

    def text_to_image(self, instructions: TextToImageInstructions) -> Image:
        image = self.pipe(
            prompt=instructions.prompt,
            negative_prompt="" if instructions.negative_prompt is None else instructions.negative_prompt,
            num_inference_steps=28 if instructions.num_inference_steps is None else instructions.num_inference_steps,
            guidance_scale=7.0 if instructions.guidance_scale is None else instructions.guidance_scale,
            width=1024 if instructions.width is None else instructions.width,
            height=1024 if instructions.height is None else instructions.height
        ).images[0]
        return image


class StableDiffusion3ImageToImage:
    def __init__(self):
        ensure_huggingface_hub_login()
        self.pipe = AutoPipelineForImage2Image.from_pretrained(
            "stabilityai/stable-diffusion-3-medium-diffusers",
            device_map="balanced",
            torch_dtype=torch.float16)

    def image_to_image(self, instructions: ImageToImageInstructions, base_image: Image) -> Image:
        image = self.pipe(
            prompt=instructions.prompt,
            image=base_image,
            negative_prompt="" if instructions.negative_prompt is None else instructions.negative_prompt,
            num_inference_steps=28 if instructions.num_inference_steps is None else instructions.num_inference_steps,
            guidance_scale=7.0 if instructions.guidance_scale is None else instructions.guidance_scale
        ).images[0]
        return image


class FluxTextToImage:
    def __init__(self):
        ensure_huggingface_hub_login()
        self.pipe = AutoPipelineForText2Image.from_pretrained("black-forest-labs/FLUX.1-dev",
                                                              device_map="balanced",
                                                              torch_dtype=torch.bfloat16)

    def text_to_image(self, instructions: TextToImageInstructions) -> Image:
        image = self.pipe(
            prompt=instructions.prompt,
            num_inference_steps=50 if instructions.num_inference_steps is None else instructions.num_inference_steps,
            guidance_scale=3.5 if instructions.guidance_scale is None else instructions.guidance_scale,
            width=1024 if instructions.width is None else instructions.width,
            height=1024 if instructions.height is None else instructions.height
        ).images[0]
        return image


class FluxImageToImage:
    def __init__(self):
        ensure_huggingface_hub_login()
        self.pipe = FluxImg2ImgPipeline.from_pretrained("black-forest-labs/FLUX.1-dev",
                                                        device_map="balanced",
                                                        torch_dtype=torch.bfloat16)

    def image_to_image(self, instructions: ImageToImageInstructions, base_image: Image) -> Image:
        image = self.pipe(
            prompt=instructions.prompt,
            image=base_image,
            strength=0.95 if instructions.strength is None else instructions.strength,
            num_inference_steps=50 if instructions.num_inference_steps is None else instructions.num_inference_steps,
            guidance_scale=0.0 if instructions.guidance_scale is None else instructions.guidance_scale
        ).images[0]
        return image
