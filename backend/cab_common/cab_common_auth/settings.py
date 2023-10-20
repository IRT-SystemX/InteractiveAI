import os

import logging.config

HOST_IP = os.getenv("HOST_IP")

URL_INTROSPECT = os.getenv(
    "URL_INTROSPECT", f"http://{HOST_IP}:3200/auth/check_token"
)
KEYCLOAK_SERVER_URL = os.getenv(
    "KEYCLOAK_SERVER_URL", f"http://{HOST_IP}:3200/auth/"
)

AUTH_DISABLED = os.getenv("AUTH_DISABLED", "").lower() in ["true", "1"]
DEFAULT_USE_CASE = os.getenv("DEFAULT_USE_CASE")

DEFAULT_LOGGING = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "default",
        }
    },
    "root": {"level": "DEBUG", "handlers": ["wsgi"]},
}
logging.config.dictConfig(DEFAULT_LOGGING)

logger = logging.getLogger(__name__)
