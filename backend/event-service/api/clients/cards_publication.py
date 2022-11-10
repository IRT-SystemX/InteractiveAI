import requests
import json
from settings import CARDS_PUBLICATION_SERVICE


class CardPubClient:
    def __init__(self) -> None:
        self.base_url = CARDS_PUBLICATION_SERVICE

    def create_card(self, token, id, severity, timestamp_date, title, description, metadata):
        url = f"{self.base_url}/cards"
        payload = json.dumps({
            "publisher": "publisher_test",
            "processVersion": "1",
            "process": "eventProcess",
            "processInstanceId": id,
            "state": "messageState",
            "groupRecipients": [
                "Dispatcher"
            ],
            "severity": severity,
            "startDate": timestamp_date,
            "summary": {
                "key": "eventProcess.summary",
                "parameters": {"summary": description}
            },
            "title": {
                "key": "eventProcess.title",
                "parameters": {"title": title}
            },
            "data": {
                "metadata": metadata
            }
        })
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()
