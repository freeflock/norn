INITIAL_BOOT_INDICATOR=/etc/initial_boot_complete
if [ ! -f "$INITIAL_BOOT_INDICATOR" ]; then
    sudo apt -y update
    sudo apt -y upgrade

    # ssh
    echo "PasswordAuthentication no" | sudo tee /etc/ssh/sshd_config.d/no_password.conf
    echo "PermitRootLogin no" | sudo tee /etc/ssh/sshd_config.d/no_root_login.conf

    # user
    sudo adduser --disabled-password --gecos "" --shell /bin/bash --home /home/josiah josiah
    sudo usermod -a -G sudo josiah
    sudo echo "josiah ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/nopassword
    sudo -u josiah mkdir -p /home/josiah/.ssh
    sudo cp /root/.ssh/authorized_keys /home/josiah/.ssh/authorized_keys
    sudo chown josiah:josiah /home/josiah/.ssh/authorized_keys

    # security
    sudo apt -y install fail2ban
    sudo systemctl start fail2ban
    sudo systemctl enable fail2ban

    # docker
    sudo usermod -aG docker josiah
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

    sudo apt -y install python3.11

    sudo touch "$INITIAL_BOOT_INDICATOR"
    sudo reboot
fi
