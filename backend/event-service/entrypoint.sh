#!/bin/bash
# export CARDS_PUBLICATION_SERVICE="http://cards-publication:8080"
# export GATEWAY_SERVICE="http://web-ui:80"
#flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade
flask run --host=0.0.0.0 --reload
