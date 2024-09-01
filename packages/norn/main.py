import os
from io import BytesIO

import requests
from PIL import Image
from loguru import logger
from ratatosk_errands.adapter import Rabbit
from ratatosk_errands.model import Errand, TextToImageInstructions, ImageToImageInstructions

from norn.diffusion import StableDiffusion3TextToImage, StableDiffusion3ImageToImage

RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_PORT = int(os.getenv("RABBIT_PORT"))
RABBIT_USERNAME = os.getenv("RABBIT_USERNAME")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")

GALLERY_HOST = os.getenv("GALLERY_HOST")
GALLERY_PORT = int(os.getenv("GALLERY_PORT"))
GALLERY_KEY = os.getenv("GALLERY_KEY")

pipe: StableDiffusion3TextToImage | StableDiffusion3ImageToImage | None = None


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
    global pipe
    try:
        logger.info(f"( ) starting errand: {body}")
        errand = Errand.model_validate_json(body)
        if isinstance(errand.instructions, TextToImageInstructions):
            if not isinstance(pipe, StableDiffusion3TextToImage):
                pipe = StableDiffusion3TextToImage()
            image = pipe.text_to_image(errand.instructions)
        elif isinstance(errand.instructions, ImageToImageInstructions):
            if not isinstance(pipe, StableDiffusion3ImageToImage):
                pipe = StableDiffusion3ImageToImage()
            image = pipe.image_to_image(errand.instructions)
        else:
            raise ValueError(f"unknown errand instructions on errand: {errand}")
        logger.info(f"uploading image")
        upload_image_to_gallery(errand.identifier, image)
        logger.info(f"(*) completed errand: {errand.identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")


def main():
    with Rabbit(RABBIT_HOST, RABBIT_PORT, RABBIT_USERNAME, RABBIT_PASSWORD) as rabbit:
        rabbit.channel.queue_declare(queue="errand")
        rabbit.channel.basic_consume(queue="errand",
                                     auto_ack=True,
                                     on_message_callback=receive_errand)
        rabbit.channel.start_consuming()


if __name__ == '__main__':
    main()
