#!/bin/bash

echo "Usage: "
echo "   1: ./docker-compose.sh"
echo "   2: ./docker-compose.sh <pathToExternalEnvironmentFile>"

echo USER_ID="$(id -u)" > .env
echo USER_GID="$(id -g)" >> .env
# create directory for bundle storage if not existing
mkdir -p businessconfig-storage
if [ "$#" -eq 0 ]; then
  echo CONFIG_PATH=./ >> .env
  echo SPRING_PROFILES_ACTIVE=docker >> .env
else
  EXTERNAL_CONFIGURATION_FILE=$1
  CONFIG_PATH=$(dirname "$1")
  cat ${EXTERNAL_CONFIGURATION_FILE} >> .env
  echo CONFIG_PATH="$CONFIG_PATH" >> .env
fi

# Function to get the IP address of the docker network interface
get_docker_ip() {
    if [[ "$OSTYPE" == "linux-gnu" ]]; then
        # Linux
        ip -4 addr show scope global dev docker0 | grep inet | awk '{print $2}' | cut -d / -f 1
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        docker network inspect bridge --format='{{range .IPAM.Config}}{{.Gateway}}{{end}}'
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        # Windows
        docker network inspect bridge --format='{{range .IPAM.Config}}{{.Gateway}}{{end}}'
    else
        echo "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if HOST_IP is manually set
if [[ -z "$HOST_IP" ]]; then
    # If not set, retrieve the IP address
    HOST_IP=$(get_docker_ip)
fi

echo "HOST_IP=${HOST_IP}" >> .env

cat .env
docker compose up -d
