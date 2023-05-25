#! /bin/sh
HOST_IP=`ip -4 addr show scope global dev docker0 | grep inet | awk '{print \$2}' | cut -d / -f 1`
echo "HOST_IP=${HOST_IP}" > .env

docker-compose -f "docker-compose-recommendation-service.yml" up