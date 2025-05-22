# backend/recommendation-service/resources/RTE/manager.py

from api.manager.base_manager import BaseRecommendationManager

class ATMManager(BaseRecommendationManager):
    def __init__(self):
        super().__init__()

    def get_recommendation(self, request_data):
        """
        Override to provide recommendations specific to the ATM use case.
        
        This method generates and returns recommendations tailored for ATM.
        """
        action_dict = {"action 1": "do something", "action 2": "do nothing"}

        output_json = {
            "title": "recommendation",
            "description": "description",
            "use_case": "ATM",
            "agent_type": "agent_type",
            "actions": [action_dict],
        }

        return [output_json]