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

model: StableDiffusion3TextToImage | StableDiffusion3ImageToImage | Hermes3Chat | None = None


def upload_image_to_gallery(image_name: str, image: Image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    headers = {"gallery_key": GALLERY_KEY}
    files = {"file": (f"{image_name}.png", buffer, "image/png")}
    response = requests.post(f"http://{GALLERY_HOST}:{GALLERY_PORT}/upload", files=files, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"bad status code from gallery upload: {response.status_code}")


def receive_errand(ch, method, properties, body):
    global model
    try:
        logger.info(f"( ) starting errand: {body}")
        errand = Errand.model_validate_json(body)
        if isinstance(errand.instructions, TextToImageInstructions):
            if not isinstance(model, StableDiffusion3TextToImage):
                model = StableDiffusion3TextToImage()
                logger.info(f"loaded stable diffusion 3 text to image model")
            image = model.text_to_image(errand.instructions)
            logger.info(f"uploading image")
            upload_image_to_gallery(errand.identifier, image)
        elif isinstance(errand.instructions, ImageToImageInstructions):
            if not isinstance(model, StableDiffusion3ImageToImage):
                model = StableDiffusion3ImageToImage()
                logger.info(f"loaded stable diffusion 3 image to image model")
            image = model.image_to_image(errand.instructions)
            logger.info(f"uploading image")
            upload_image_to_gallery(errand.identifier, image)
        elif isinstance(errand.instructions, ChatInstructions):
            if not isinstance(model, Hermes3Chat):
                model = Hermes3Chat()
                logger.info(f"loaded hermes 3 chat model")
            response = model.chat(errand.instructions)
            logger.info(response)
        else:
            raise ValueError(f"unknown errand instructions on errand: {errand}")
        logger.info(f"(*) completed errand: {errand.identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")


def main():
    with Rabbit(RABBIT_HOST, RABBIT_PORT, RABBIT_USERNAME, RABBIT_PASSWORD) as rabbit:
        rabbit.channel.queue_declare(queue="errand")
        rabbit.channel.basic_consume(queue="errand",
                                     auto_ack=True,
                                     on_message_callback=receive_errand)
        logger.info(f"setup complete, listening for errands")
        rabbit.channel.start_consuming()


if __name__ == '__main__':
    main()
