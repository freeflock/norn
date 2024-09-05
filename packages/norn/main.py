import json
import os
from io import BytesIO

import requests
from PIL import Image
from loguru import logger
from ratatosk_errands.adapter import Rabbit
from ratatosk_errands.model import Errand, Echo, TextToImageInstructions, ImageToImageInstructions, ChatInstructions, \
    DiffusionReply, ChatReply

from norn.diffusion import StableDiffusion3TextToImage, StableDiffusion3ImageToImage, FluxTextToImage
from norn.language import Hermes3Chat

RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_PORT = int(os.getenv("RABBIT_PORT"))
RABBIT_USERNAME = os.getenv("RABBIT_USERNAME")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")

GALLERY_HOST = os.getenv("GALLERY_HOST")
GALLERY_PORT = int(os.getenv("GALLERY_PORT"))
GALLERY_KEY = os.getenv("GALLERY_KEY")

MODEL_TYPES = json.loads(os.getenv("MODEL_TYPES"))
logger.info(f"( ) initializing norn with model types: {MODEL_TYPES}")
model: (StableDiffusion3TextToImage |
        StableDiffusion3ImageToImage |
        FluxTextToImage |
        Hermes3Chat |
        None) = None

choice_text_to_image_model = FluxTextToImage
choice_image_to_image_model = StableDiffusion3ImageToImage
choice_chat_model = Hermes3Chat

if "text_to_image" in MODEL_TYPES:
    model = choice_text_to_image_model()
if "image_to_image" in MODEL_TYPES:
    model = choice_image_to_image_model()
if "chat" in MODEL_TYPES:
    model = choice_chat_model()
logger.info(f"(*) initialized model types")


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


def receive_chat_errand(channel, method, properties, body):
    global model
    try:
        logger.info(f"( ) receiving errand: {body}")
        errand = Errand.model_validate_json(body)
        if not isinstance(errand.instructions, ChatInstructions):
            raise ValueError(f"unknown errand instructions on errand: {errand}")

        if not isinstance(model, choice_chat_model):
            logger.info(f"swapping model")
            model = choice_chat_model()

        logger.info(f"running inference")
        reply_message = model.chat(errand.instructions)

        logger.info(f"emitting echo")
        reply = ChatReply(message=reply_message)
        echo = Echo(errand=errand, reply=reply)
        channel.basic_publish(exchange="", routing_key="echo", body=echo.model_dump_json())

        logger.info(f"(*) completed errand: {errand.errand_identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")
    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def receive_text_to_image_errand(channel, method, properties, body):
    global model
    try:
        logger.info(f"( ) receiving errand: {body}")
        errand = Errand.model_validate_json(body)
        if not isinstance(errand.instructions, TextToImageInstructions):
            raise ValueError(f"unknown errand instructions on errand: {errand}")

        if not isinstance(model, choice_text_to_image_model):
            logger.info(f"swapping model")
            model = choice_text_to_image_model()

        logger.info(f"running inference")
        image = model.text_to_image(errand.instructions)

        logger.info(f"uploading image")
        upload_image_to_gallery(errand.instructions.image_identifier, image)

        logger.info(f"emitting echo")
        reply = DiffusionReply(image_identifier=errand.instructions.image_identifier)
        echo = Echo(errand=errand, reply=reply)
        channel.basic_publish(exchange="", routing_key="echo", body=echo.model_dump_json())

        logger.info(f"(*) completed errand: {errand.errand_identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")
    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def receive_image_to_image_errand(channel, method, properties, body):
    global model
    try:
        logger.info(f"( ) receiving errand: {body}")
        errand = Errand.model_validate_json(body)
        if not isinstance(errand.instructions, ImageToImageInstructions):
            raise ValueError(f"unknown errand instructions on errand: {errand}")

        if not isinstance(model, choice_image_to_image_model):
            logger.info(f"swapping model")
            model = choice_image_to_image_model()

        logger.info(f"downloading base image")
        base_image = download_image_from_gallery(errand.instructions.base_image_identifier)

        logger.info(f"running inference")
        image = model.image_to_image(errand.instructions, base_image)

        logger.info(f"uploading image")
        upload_image_to_gallery(errand.instructions.image_identifier, image)

        logger.info(f"emitting echo")
        reply = DiffusionReply(image_identifier=errand.instructions.image_identifier)
        echo = Echo(errand=errand, reply=reply)
        channel.basic_publish(exchange="", routing_key="echo", body=echo.model_dump_json())

        logger.info(f"(*) completed errand: {errand.errand_identifier}")
    except Exception as error:
        logger.error(f"(!) errand failed with error: {error}")
    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main():
    with Rabbit(RABBIT_HOST, RABBIT_PORT, RABBIT_USERNAME, RABBIT_PASSWORD) as rabbit:
        rabbit.channel.basic_qos(prefetch_count=1)
        rabbit.channel.queue_declare(queue="echo")
        rabbit.channel.queue_declare(queue="text_to_image")
        rabbit.channel.queue_declare(queue="image_to_image")
        rabbit.channel.queue_declare(queue="chat")
        if "text_to_image" in MODEL_TYPES:
            rabbit.channel.basic_consume(queue="text_to_image", on_message_callback=receive_text_to_image_errand)
        if "image_to_image" in MODEL_TYPES:
            rabbit.channel.basic_consume(queue="image_to_image", on_message_callback=receive_image_to_image_errand)
        if "chat" in MODEL_TYPES:
            rabbit.channel.basic_consume(queue="chat", on_message_callback=receive_chat_errand)
        logger.info(f"setup complete, listening for errands")
        rabbit.channel.start_consuming()


if __name__ == '__main__':
    main()
