import os
import logging.config


CARDS_PUBLICATION_SERVICE = os.getenv('CARDS_PUBLICATION_SERVICE')
GATEWAY_SERVICE = os.getenv('GATEWAY_SERVICE')
HISTORIC_SERVICE = os.getenv('HISTORIC_SERVICE')


DEFAULT_LOGGING = {
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
}
logging.config.dictConfig(DEFAULT_LOGGING)

logger = logging.getLogger(__name__)
