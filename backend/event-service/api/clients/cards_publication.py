import requests
import json

url = "http://localhost:2102/cards"




class CardPubClient:
    def __init__(self) -> None:
        self.base_url = "http://localhost:2102"

    def create_card(self, token, id, severity, timestamp_date, description):
        url = f"{self.base_url}/cards"
        payload = json.dumps({
            "publisher": "publisher_test",
            "processVersion": "2",
            "process": "eventProcess",
            "processInstanceId": id,
            "state": "messageState",
            "groupRecipients": [
                "Dispatcher"
            ],
            "severity": severity,
            "startDate": timestamp_date,
            "summary": {
                "key": description
            },
            "title": {
                "key": "New event"
            },
            "data": {
                "message": "High cogntive charge detected"
            }
        })
        headers = {
            'Authorization': f"Bearer {token}",
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
