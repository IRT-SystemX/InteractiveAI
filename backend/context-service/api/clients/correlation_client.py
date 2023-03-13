import requests
import json
from settings import CORRELATION_SERVICE, logger


class CorrelationClient:
    def __init__(self) -> None:
        self.base_url = CORRELATION_SERVICE

    def send_correlation(self, correlation_app_payload):
        url = f"{self.base_url}/api/v1/correlation"
        payload = json.dumps(correlation_app_payload)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info("correlation request sent")
        response.raise_for_status()
