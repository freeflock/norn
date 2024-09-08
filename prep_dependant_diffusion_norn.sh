#!/bin/bash

LANGUAGE_NORN_IP=$(ping -c 1 language_norn | grep PING | awk '{print $3}' | tr -d '():')
ssh -i ~/.ssh/norn norn@diffusion_norn "echo '$LANGUAGE_NORN_IP gallery' | sudo tee -a /etc/hosts"
ssh -i ~/.ssh/norn norn@diffusion_norn "echo '$LANGUAGE_NORN_IP rabbit' | sudo tee -a /etc/hosts"

scp -i ~/.ssh/norn ~/freeflock/norn/diffusion_norn.env norn@diffusion_norn:/home/norn/norn/norn.env
