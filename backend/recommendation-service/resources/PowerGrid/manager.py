import os

import requests
import urllib3
from api.manager.base_manager import BaseRecommendationManager
from settings import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class PowerGridManager(BaseRecommendationManager):
    """PowerGrid recomendation service

    Args:
        BaseRecommendationManager (): CAB recomendation service instance
    """

    def __init__(self):
        # Runtime value comes from the RL_AGENT_API_URL env var (set via
        # .secrets -> docker-compose.sh -> .env for local Docker, or extraEnv
        # for k8s). The fallback is a safe in-cluster default only.
        self.rl_agent_api_url = os.environ.get(
            "RL_AGENT_API_URL",
            "http://frontend:80/rl-api/recommendation",
        )
        self.rl_agent_api_token = os.environ.get("RL_AGENT_API_TOKEN", "")
        super().__init__()

    def get_recommendation(self, request_data):
        """Get IA agent recomendations

        Args:
            request_data (dict): A dictionary with keys "context" and "event"

        Returns:
            list[dict]: List of recomendations
        """
        logger.info("Getting RL agent recommendations from external API")
        return self._get_rl_parades(request_data)

    def _get_rl_parades(self, request_data):
        """Call the external RL agent API to get parade recommendations.

        Args:
            request_data (dict): Full request payload with keys "event" and "context"

        Returns:
            list[dict]: List of parade recommendations, empty on failure
        """
        try:
            headers = {}
            if self.rl_agent_api_token:
                headers["Authorization"] = f"Bearer {self.rl_agent_api_token}"
            response = requests.post(
                self.rl_agent_api_url,
                json=request_data,
                headers=headers,
                timeout=30,
                verify=False,  # SSL cert may not be trusted inside the container
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"RL agent returned {len(data)} recommendation(s)")
            return data
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error calling RL agent API: {e}")
            return []
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error calling RL agent API: {e} — response body: {e.response.text[:500] if e.response is not None else 'N/A'}")
            return []
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error calling RL agent API ({self.rl_agent_api_url}): {e}")
            return []
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling RL agent API ({self.rl_agent_api_url}) after 30s")
            return []
        except Exception as e:
            logger.error(f"Unexpected error calling RL agent API: {type(e).__name__}: {e}")
            return []
