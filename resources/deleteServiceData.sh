#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

servicename=$1
url=$2

if [ -z $url ]; then
    url="http://localhost"
fi

if [ -z $servicename ]; then
    echo "Usage : deleteServiceData servicename cab_url"
else
    source ./getToken.sh "admin" $url
    echo "Sending delete request to $url:3200/$servicename/api/v1/delete_all_data"
    curl -X DELETE $url:3200/$servicename/api/v1/delete_all_data -H "Content-type:application/json" -H "Authorization:Bearer $token" -v
    echo ""
fi
