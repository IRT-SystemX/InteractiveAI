import requests


class KeycloakClient:
    def __init__(self) -> None:
        self.base_url = "http://localhost:2002"

    def login(self):
        url = f"{self.base_url}/auth/token"

        payload = 'grant_type=password&username=publisher_test&password=test&clientId=opfab-client'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()
