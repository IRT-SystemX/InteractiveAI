"""
INESCTEC | InteractiveAI — Python client
Equivalent of the Postman collection: INESCTEC | InteractiveAI
"""

import requests
import urllib3

# The server certificate hostname doesn't match — suppress the SSL warning
# (same behaviour as Postman's "SSL certificate verification" toggle off)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = "https://wesenss.inesctec.pt/api/v1"

# Replace with a fresh token when the current one expires
TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiI2NjVmY2Y4OWEzOTRiNzZiMGI0NTRmNjYiLCJhdWQiOlsiZmFzdGFwaS11c2"
    "VyczphdXRoIl0sImV4cCI6MTc4ODE4Mjc5MH0"
    ".-LI10Tkay4QYlcwD7Jpm_otdM3yFY0SYtW4peIK5LM4"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get(path: str) -> dict:
    """Perform an authenticated GET request and return the parsed JSON."""
    url = f"{BASE_URL}{path}"
    response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
    response.raise_for_status()
    return response.json()


# ---------------------------------------------------------------------------
# API calls
# ---------------------------------------------------------------------------


def ask_event_agent_id(event_id: int = 885) -> dict:
    """
    [GET] /agent_event/list/{event_id}
    → List agents associated with the given event.
    """
    return _get(f"/agent_event/list/{event_id}")


def ask_latest_data_per_event_per_agent(event_id: int = 885, agent_id: int = 161) -> dict:
    """
    [GET] /event_product/latest_data_agent/{event_id}/{agent_id}
    → Retrieve the latest data produced by a specific agent for a given event.
    """
    return _get(f"/event_product/latest_data_agent/{event_id}/{agent_id}")


# ---------------------------------------------------------------------------
# Main — run all requests and print results
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("=== Ask Event Agent ID (event 885) ===")
    result = ask_event_agent_id(event_id=885)
    print(json.dumps(result, indent=2))

    print("\n=== Latest data per event/agent (event 885, agent 161) ===")
    result = ask_latest_data_per_event_per_agent(event_id=885, agent_id=161)
    print(json.dumps(result, indent=2))
