from .base_recommendation import BaseRecommendation
from flask import current_app
import os
from resources.sncf.sncf_cab_recommender import SncfCabRecommender


class SNCFManager(BaseRecommendation):
    
    def __init__(self) -> None:
        super().__init__()
        self.root_path = current_app.config["ROOT_PATH"]
        
        self.recommender = SncfCabRecommender()

    def get_recommendation(self, request_data):
        context_data = request_data.get("context", {})
        event_data = request_data.get("event", {})

        
        ai_transport_plan, ai_title, ai_description  = self.recommender.recommend(context_data,event_data)
        ai_recommendation = {
            "title": ai_title,
            "description": ai_description,
            "use_case": "SNCF",
            "agent_type": "IA",
            "actions": [ai_transport_plan]
            }
        
        fake_transport_plan, fake_title, fake_description  = self.recommender.recommend(context_data,event_data,fake=True)
        fake_recommendation = {
            "title": fake_title,
            "description": fake_description,
            "use_case": "SNCF",
            "agent_type": "IA",
            "actions": [fake_transport_plan],
        }

        recommendation = [fake_recommendation, ai_recommendation]

        return recommendation
