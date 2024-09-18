#!/bin/bash

# requires a docker-container buildx driver
docker buildx build --platform linux/amd64 --push -t josiahdc/norn:0.1 .
