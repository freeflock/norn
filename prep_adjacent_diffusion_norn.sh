#!/bin/bash

NORN_HOSTNAME=diffusion_norn_two
LEADER_HOSTNAME=diffusion_norn
LEADER_IP=$(ping -c 1 $LEADER_HOSTNAME | grep PING | awk '{print $3}' | tr -d '():')
ssh -i ~/.ssh/norn norn@$NORN_HOSTNAME "echo '$LEADER_IP gallery' | sudo tee -a /etc/hosts"
ssh -i ~/.ssh/norn norn@$NORN_HOSTNAME "echo '$LEADER_IP rabbit' | sudo tee -a /etc/hosts"

scp -i ~/.ssh/norn ~/freeflock/norn/env/diffusion_norn.env norn@$NORN_HOSTNAME:/home/norn/norn/norn.env
