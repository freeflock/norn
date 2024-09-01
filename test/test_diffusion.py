import os

from PIL import Image
from ratatosk_errands.model import TextToImageInstructions, ImageToImageInstructions

from norn.diffusion import StableDiffusion3TextToImage, b64_encode_image, StableDiffusion3ImageToImage

OUTPUT_DIR = "/tmp/pasture_test_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def test_text_to_image():
    instructions = TextToImageInstructions(
        prompt="a breathtaking oil painting of a green pasture with rolling hills and grazing sheep",
        negative_prompt="goats",
        num_inference_steps=28,
        guidance_scale=7.0,
        width=1024,
        height=1024
    )
    model = StableDiffusion3TextToImage()
    image = model.text_to_image(instructions)
    image.save(f"{OUTPUT_DIR}/text_to_image.png")


def test_image_to_image():
    base_image = Image.open(f"{OUTPUT_DIR}/text_to_image.png")
    encoded_base_image = b64_encode_image(base_image)
    instructions = ImageToImageInstructions(
        prompt="goats grazing in a pasture",
        negative_prompt="sheep",
        num_inference_steps=28,
        guidance_scale=7.0,
        width=1024,
        height=1024,
        encoded_base_image=encoded_base_image
    )
    model = StableDiffusion3ImageToImage()
    image = model.image_to_image(instructions)
    image.save(f"{OUTPUT_DIR}/image_to_image.png")
