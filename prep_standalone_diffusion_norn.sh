#!/bin/bash

ssh -i ~/.ssh/norn norn@diffusion_norn "echo '0.0.0.0 gallery' | sudo tee -a /etc/hosts"
ssh -i ~/.ssh/norn norn@diffusion_norn "echo '0.0.0.0 rabbit' | sudo tee -a /etc/hosts"

scp -i ~/.ssh/norn ~/freeflock/norn/diffusion_norn.env norn@diffusion_norn:/home/norn/norn/norn.env
scp -i ~/.ssh/norn ~/freeflock/gallery/gallery.env norn@diffusion_norn:/home/norn/gallery/gallery.env
scp -i ~/.ssh/norn ~/freeflock/ratatosk/ratatosk.env norn@diffusion_norn:/home/norn/ratatosk/ratatosk.env

ssh -i ~/.ssh/norn norn@diffusion_norn "cd /home/norn/ratatosk/rabbit; docker compose up -d"
ssh -i ~/.ssh/norn norn@diffusion_norn "cd /home/norn/gallery; docker compose up -d"
