import requests
import json
from settings import CARDS_PUBLICATION_SERVICE, logger


class CardPubClient:
    def __init__(self) -> None:
        self.base_url = CARDS_PUBLICATION_SERVICE

    def create_card(self, card_payload):
        url = f"{self.base_url}/cards"
        payload = json.dumps(card_payload)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(response.status_code)
        response.raise_for_status()
