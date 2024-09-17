#!/bin/bash

# requires a docker-container buildx driver
docker buildx build --platform linux/arm64/v8,linux/amd64 --push -t josiahdc/norn:0.1 .
