import os

HOST_IP = os.getenv("HOST_IP")
URL_INTROSPECT = f"http://{HOST_IP}:3200/auth/check_token"
KEYCLOAK_SERVER_URL = "http://{HOST_IP}:3200/auth/"
AUTH_DISABLED = os.getenv("AUTH_DISABLED", "").lower() in ["true", "1"]
DEFAULT_USE_CASE = os.getenv("DEFAULT_USE_CASE")
