#!/bin/bash
export CARDS_PUBLICATION_SERVICE="http://172.18.91.224:2102"
export GATEWAY_SERVICE="http://172.18.91.224:2002"
source ../../cab_venv/Scripts/activate
python -m flask run --host=0.0.0.0 --reload