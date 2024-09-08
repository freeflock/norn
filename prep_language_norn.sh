#!/bin/bash

ssh -i ~/.ssh/norn norn@language_norn "echo '0.0.0.0 gallery' | sudo tee -a /etc/hosts"
ssh -i ~/.ssh/norn norn@language_norn "echo '0.0.0.0 rabbit' | sudo tee -a /etc/hosts"

scp -i ~/.ssh/norn ~/freeflock/norn/language_norn.env norn@language_norn:/home/norn/norn/norn.env
scp -i ~/.ssh/norn ~/freeflock/gallery/gallery.env norn@language_norn:/home/norn/gallery/gallery.env
scp -i ~/.ssh/norn ~/freeflock/ratatosk/ratatosk.env norn@language_norn:/home/norn/ratatosk/ratatosk.env

ssh -i ~/.ssh/norn norn@language_norn "cd /home/norn/ratatosk/rabbit; docker compose up -d"
ssh -i ~/.ssh/norn norn@language_norn "cd /home/norn/gallery; docker compose up -d"
