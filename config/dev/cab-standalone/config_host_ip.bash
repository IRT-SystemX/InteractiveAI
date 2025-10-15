#!/bin/bash

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

echo "HOST_IP=${HOST_IP}" > .env
