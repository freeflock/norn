FROM pytorch/pytorch:2.4.1-cuda12.4-cudnn9-devel
WORKDIR /atelier

RUN apt -y update
RUN apt -y install git

COPY ./requirements.txt /atelier/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /atelier/requirements.txt

COPY ./requirements-no-build-isolation.txt /atelier/requirements-no-build-isolation.txt
RUN pip install -r requirements-no-build-isolation.txt --no-build-isolation

RUN pip install diffusers@git+https://github.com/huggingface/diffusers

COPY ./packages/norn /atelier/norn

CMD ["python3", "-m", "norn.main"]
