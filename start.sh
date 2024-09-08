#!/bin/bash

source .venv/bin/activate
cd ./packages || exit
python3 -m norn.main
