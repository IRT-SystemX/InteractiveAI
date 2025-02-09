# Installing prequisites
## Update packages
sudo apt update

## Install python (> 3.6 && =<3.10 )
sudo apt install python3-pip
sudo apt install python-is-python3 

## Install Docker
sudo apt install docker.io 

## Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

## Add docker permissions to user 
newgrp docker
sudo usermod -aG docker $USER