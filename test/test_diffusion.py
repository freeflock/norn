import requests
from PIL import Image
from dotenv import load_dotenv
from ratatosk_errands.model import TextToImageInstructions, ImageToImageInstructions

from norn.diffusion import StableDiffusion3TextToImage, StableDiffusion3ImageToImage


def test_text_to_image():
    load_dotenv("../norn.env")
    instructions = TextToImageInstructions(
        prompt="a breathtaking oil painting of a green pasture with rolling hills",
        negative_prompt="",
        num_inference_steps=28,
        guidance_scale=7.0,
        width=1024,
        height=1024
    )
    model = StableDiffusion3TextToImage()
    image = model.text_to_image(instructions)
    image.save(f"data/text_to_image.png")


def test_image_to_image():
    load_dotenv("../norn.env")
    base_image = Image.open(f"data/text_to_image.png")
    instructions = ImageToImageInstructions(
        prompt="a flock of sheep",
        negative_prompt="",
        num_inference_steps=28,
        guidance_scale=7.0,
        width=1024,
        height=1024,
        base_image_identifier="image_to_image"
    )
    model = StableDiffusion3ImageToImage()
    image = model.image_to_image(instructions, base_image)
    image.save(f"data/image_to_image.png")
