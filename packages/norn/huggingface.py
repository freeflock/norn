import os

from huggingface_hub import login

INNER_LOGGED_IN = False


def ensure_huggingface_hub_login():
    global INNER_LOGGED_IN
    if not INNER_LOGGED_IN:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("unable to login to huggingface hub, please specify an HF_TOKEN env var")
        login(token=token)
        INNER_LOGGED_IN = True
