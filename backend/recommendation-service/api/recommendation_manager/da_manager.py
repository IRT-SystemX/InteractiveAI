from owlready2 import default_world, get_ontology
from settings import logger
from resources.da.da_cab_recommender import DaCabRecommender

from .base_recommendation import BaseRecommendation
from flask import current_app
import os


class DAManager(BaseRecommendation):
    def __init__(self):
        self.root_path = current_app.config["ROOT_PATH"]
        self.owl_file_path = os.path.join(
            self.root_path, "resources/da/ontology/AlarmsOntoDA.owl"
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
            "90 PRESS : CABIN ALT TOO HIGH": "procedure_90_PRESS_CABIN_ALT_TOO_HI",
            "ENG1: AUTO SHUTDOWN": "procedure_ENG1_AUTO_SHUTDOWN",
        }
        # Load ontology

        DA_onto = get_ontology(self.owl_file_path).load()

        # Update checkList object property assertion to actual event
        # get instance of check list from ontology + procedure depending on event
        mycheckList = DA_onto.CheckList("checkList")
        myProcedure = DA_onto.AlarmProcedure(all_events[event_type])

        # Empty checkList relation if exists
        mycheckList.HasCurrentCheckListProcedure = []
        # add property
        mycheckList.HasCurrentCheckListProcedure.append(myProcedure)
        # save ontology
        DA_onto.save(self.owl_file_path)

        # request procedure from ontology
        procedure = list(
            default_world.sparql(
                """
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX cab: <http://www.semanticweb.org/scdsahv/ontologies/2022/5/untitled-ontology-5#>
        SELECT ?taskText
        WHERE { 
          ?checklist rdf:type cab:CheckList .
          ?checklist cab:HasCurrentCheckListProcedure ?procedure .  
          ?procedure cab:HasProcedureElement ?procedureTask .  
          ?procedureTask cab:TaskIndex ?taskIndex .    
          ?procedureTask cab:TaskText ?taskText .    
        } ORDER BY ?taskIndex

            """
            )
        )

        # jsonify & add index
        procedure_dict = {
            "procedure": [],
            "min_speed": min_speed,
            "max_speed": max_speed,
        }

        for i, sub_list in enumerate(procedure):
            task_dict = {"TaskIndex": i + 1, "TaskText": sub_list[0]}

            procedure_dict["procedure"].append(task_dict)

        return procedure_dict
