#!/bin/bash
export FLASK_APP="app:create_app('test')"
export FLASK_ENV="development"
# Disable authentication
export AUTH_DISABLED="True"
# Create a default use case to replace user detection from JWT
# This option is used only with AUTH_DISABLED="True"
export DEFAULT_USE_CASE="ATM"
# Start python app on default port (5000)
python -m flask run --host=0.0.0.0 --reload