from owlready2 import default_world, get_ontology
from settings import logger
from resources.da.da_cab_recommender import DaCabRecommender

from .base_recommendation import BaseRecommendation
from flask import current_app
import os
import json





class DAManager(BaseRecommendation):
    def __init__(self):
        self.root_path = current_app.config["ROOT_PATH"]
        self.owl_file_path = os.path.join(
            self.root_path, "resources/da/ontology/AlarmsOntoDA.owl"
        )
        self.json_file_path = os.path.join(
            self.root_path, 'resources/da/procedures/'
        )
        self.recommender = DaCabRecommender()

        super().__init__()

    def get_recommendation(self, request_data):
        context_data = request_data.get("context", {})
        event_data = request_data.get("event", {})
        derouting_plans, titles, descriptions = self.recommender.recommend(
            context_data, event_data
        )

        combined_fake_recommendations = [
            {
                "title": title,
                "description": description,
                "use_case": "DA",
                "agent_type": "IA",
                "actions": [derouting_plan],
            }
            for title, description, derouting_plan in zip(
                titles, descriptions, derouting_plans
            )
        ]

        return combined_fake_recommendations

 


    def get_procedure(self, event_type):
        min_speed = 180
        max_speed = 260  
        all_events = {
            "90 PRESS : CABIN ALT TOO HIGH": "90_PRESS_CABIN_ALT_TOO_HI",
            "ENG1: AUTO SHUTDOWN": "ENG1_AUTO_SHUTDOWN",
        }

        procedure_dict = {
            "procedure": [],
            "min_speed": min_speed,
            "max_speed": max_speed,
        }      

        #get alarm's json 
        if '90' in event_type:
            with open(self.json_file_path + 'proc_emerg_' + all_events[event_type] + '.json') as f:
                json_data = json.load(f)
                procedure_dict["procedure"] = self.recommender.extract_procedure(json_data)

        else:
            with open(self.json_file_path + 'proc_abnrml_' + all_events[event_type] + '.json') as f:
                json_data = json.load(f)
                procedure_dict["procedure"] = self.recommender.extract_procedure(json_data)

        return procedure_dict
        
 
