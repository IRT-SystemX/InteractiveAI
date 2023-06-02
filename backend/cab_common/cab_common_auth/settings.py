import os

HOST_IP = os.getenv("HOST_IP")
URL_INTROSPECT = f"http://{HOST_IP}:3200/auth/check_token"
KEYCLOAK_SERVER_URL = "http://{HOST_IP}:3200/auth/"
