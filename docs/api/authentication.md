# Authentication

All InteractiveAI APIs require a bearer token. You must obtain a token before calling any endpoint, and include it in every request.

## Get a token

```http
POST http://{Platform_Server}:3200/auth/token
Content-Type: application/x-www-form-urlencoded
```

### Request body

| Field | Value |
|---|---|
| `username` | `publisher_test`
| `password` |`test` |
| `grant_type` | `password` |
| `clientId` | `opfab-client` |

### Example (curl)

```bash
curl -X POST http://{Platform_Server}:3200/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=publisher_test&password=test&grant_type=password&clientId=opfab-client"
```

### Response

```json
{
  "access_token": "<token>",
  "token_type": "Bearer",
  ...
}
```

The token to use in subsequent requests is: `{token_type} {access_token}` (e.g. `Bearer eyJ...`).

---

## Use the token

Include the token in the `Authorization` header of every API call:

```http
POST http://{Platform_Server}:3200/cab_event/api/v1/events
Authorization: Bearer eyJ...
Content-Type: application/json
```

---

## Python example

```python
import requests
import json

server_url = "{Platform_Server}"
username = "publisher_test"
password = "test"
client_id = "opfab-client"

token_url = f"http://{server_url}:3200/auth/token"

# Request token
response = requests.post(
    token_url,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data=f"username={username}&password={password}&grant_type=password&clientId={client_id}"
)

if response.status_code >= 500:
    raise ValueError(f"Token request failed with status code {response.status_code}")

data = response.json()
token = data["token_type"] + " " + data["access_token"]

# Use the token in subsequent requests
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

# Example: send an event
requests.post(
    f"http://{server_url}:3200/cab_event/api/v1/events",
    headers=headers,
    json={ ... }
)
```

---

## API base URLs

| Service | URL |
|---|---|
| Auth | `http://{Platform_Server}:3200/auth/token` |
| Event | `http://{Platform_Server}:3200/cab_event/api/v1/events` |
| Context | `http://{Platform_Server}:3200/cabcontext/api/v1/contexts` |
