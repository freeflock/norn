INITIAL_BOOT_INDICATOR=/etc/initial_boot_complete
if [ ! -f "$INITIAL_BOOT_INDICATOR" ]; then
    sudo apt -y update
    sudo apt -y upgrade

    sudo apt -y install python3.11
    sudo apt -y install python3.11-venv

    # ssh
    echo "PasswordAuthentication no" | sudo tee /etc/ssh/sshd_config.d/no_password.conf
    echo "PermitRootLogin no" | sudo tee /etc/ssh/sshd_config.d/no_root_login.conf

    # user
    sudo adduser --disabled-password --gecos "" --shell /bin/bash --home /home/norn norn
    sudo usermod -a -G sudo norn
    sudo echo "norn ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/nopassword
    sudo -u norn /bin/bash -c "mkdir -p /home/norn/.ssh"
    sudo cp /root/.ssh/authorized_keys /home/norn/.ssh/authorized_keys
    sudo chown norn:norn /home/norn/.ssh/authorized_keys
    sudo -u norn /bin/bash -c "ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ''"

    # security
    sudo apt -y install fail2ban
    sudo systemctl start fail2ban
    sudo systemctl enable fail2ban

    # docker
    sudo usermod -aG docker norn
    newgrp docker
    sudo systemctl enable docker.service
    sudo systemctl enable containerd.service

    sudo tee /etc/docker/daemon.json <<EOF
{
"log-driver": "json-file",
"log-opts": {
  "max-size": "10m",
  "max-file": "3"
}
}
EOF

    # norn
    sudo -u norn /bin/bash -c "git clone https://github.com/freeflock/norn.git ~/norn"
    sudo -u norn /bin/bash -c "cd ~/norn && python3.11 -m venv .venv"
    sudo -u norn /bin/bash -c "cd ~/norn && source .venv/bin/activate && pip install -r requirements.txt"
    sudo -u norn /bin/bash -c "cd ~/norn && source .venv/bin/activate && pip install -r requirements-no-build-isolation.txt --no-build-isolation"

    sudo -u norn /bin/bash -c "git clone https://github.com/freeflock/gallery.git ~/gallery"
    sudo -u norn /bin/bash -c "git clone https://github.com/freeflock/ratatosk.git ~/ratatosk"

    sudo touch "$INITIAL_BOOT_INDICATOR"
    sudo reboot
fi
