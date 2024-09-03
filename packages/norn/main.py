import os
from io import BytesIO

import requests
from PIL import Image
from loguru import logger
from ratatosk_errands.adapter import Rabbit
from ratatosk_errands.model import Errand, TextToImageInstructions, ImageToImageInstructions, ChatInstructions

from norn.diffusion import StableDiffusion3TextToImage, StableDiffusion3ImageToImage
from norn.language import Hermes3Chat

RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_PORT = int(os.getenv("RABBIT_PORT"))
RABBIT_USERNAME = os.getenv("RABBIT_USERNAME")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")

GALLERY_HOST = os.getenv("GALLERY_HOST")
GALLERY_PORT = int(os.getenv("GALLERY_PORT"))
GALLERY_KEY = os.getenv("GALLERY_KEY")

MODEL_TYPE = os.getenv("MODEL_TYPE")
logger.info(f"( ) initializing model: {MODEL_TYPE}")
diffusion_model: StableDiffusion3TextToImage | StableDiffusion3ImageToImage | None = None
language_model: Hermes3Chat | None = None
if MODEL_TYPE == "diffusion":
    diffusion_model = StableDiffusion3TextToImage()
    language_model = None
elif MODEL_TYPE == "language":
    diffusion_model = None
    language_model = Hermes3Chat()
else:
    raise ValueError(f"invalid model type specified in MODEL_TYPE env var: {MODEL_TYPE}")
logger.info(f"(*) initialized model")


def upload_image_to_gallery(identifier: str, image: Image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    headers = {"gallery_key": GALLERY_KEY}
    files = {"file": (f"{identifier}.png", buffer, "image/png")}
    response = requests.post(f"http://{GALLERY_HOST}:{GALLERY_PORT}/upload", files=files, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"bad status code from gallery upload: {response.status_code}")


def download_image_from_gallery(identifier: str) -> Image:
    headers = {"gallery_key": GALLERY_KEY}
    response = requests.post(f"http://{GALLERY_HOST}:{GALLERY_PORT}/download",
                             json={"file_name": f"{identifier}.png"},
                             headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"bad status code from gallery download: {response.status_code}")
    image = Image.open(BytesIO(response.content))
    return image


def receive_language_errand(ch, method, properties, body):
    try:
        logger.info(f"( ) starting errand: {body}")
        errand = Errand.model_validate_json(body)
        if not isinstance(errand.instructions, ChatInstructions):
            raise ValueError(f"unknown errand instructions on errand: {errand}")
        response = language_model.chat(errand.instructions)
        logger.info(response)
        logger.info(f"(*) completed errand: {errand.identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")


def receive_diffusion_errand(ch, method, properties, body):
    global diffusion_model
    try:
        logger.info(f"( ) starting errand: {body}")
        errand = Errand.model_validate_json(body)
        if isinstance(errand.instructions, TextToImageInstructions):
            if not isinstance(diffusion_model, StableDiffusion3TextToImage):
                logger.info(f"( ) initializing stable diffusion 3 text to image model")
                diffusion_model = StableDiffusion3TextToImage()
                logger.info(f"(*) initialized stable diffusion 3 text to image model")
            image = diffusion_model.text_to_image(errand.instructions)
            logger.info(f"uploading image")
            upload_image_to_gallery(errand.identifier, image)
        elif isinstance(errand.instructions, ImageToImageInstructions):
            if not isinstance(diffusion_model, StableDiffusion3ImageToImage):
                logger.info(f"( ) initializing stable diffusion 3 image to image model")
                diffusion_model = StableDiffusion3ImageToImage()
                logger.info(f"(*) initialized stable diffusion 3 image to image model")
            base_image = download_image_from_gallery(errand.instructions.base_image_identifier)
            image = diffusion_model.image_to_image(errand.instructions, base_image)
            logger.info(f"uploading image")
            upload_image_to_gallery(errand.identifier, image)
        else:
            raise ValueError(f"unknown errand instructions on errand: {errand}")
        logger.info(f"(*) completed errand: {errand.identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")


def main():
    with Rabbit(RABBIT_HOST, RABBIT_PORT, RABBIT_USERNAME, RABBIT_PASSWORD) as rabbit:
        if MODEL_TYPE == "diffusion":
            rabbit.channel.queue_declare(queue="diffusion")
            rabbit.channel.basic_consume(queue="diffusion",
                                         auto_ack=True,
                                         on_message_callback=receive_diffusion_errand)
        elif MODEL_TYPE == "language":
            rabbit.channel.queue_declare(queue="language")
            rabbit.channel.basic_consume(queue="language",
                                         auto_ack=True,
                                         on_message_callback=receive_language_errand)
        else:
            raise ValueError(f"invalid model type specified in MODEL_TYPE env var: {MODEL_TYPE}")
        logger.info(f"setup complete, listening for errands")
        rabbit.channel.start_consuming()


if __name__ == '__main__':
    main()
