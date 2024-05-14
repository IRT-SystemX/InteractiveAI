from .base_recommendation import BaseRecommendation
from flask import current_app
import os
from resources.sncf.ia_flatland.src.flatland_ai.recommender import Recommender
from owlready2 import default_world, get_ontology
from marshmallow.exceptions import ValidationError


class SNCFManager(BaseRecommendation):

    def __init__(self) -> None:
        super().__init__()
        self.root_path = current_app.config["ROOT_PATH"]
        self.root_path = current_app.config["ROOT_PATH"]
        self.owl_file_path = os.path.join(
            self.root_path, "resources/sncf/ontology/final_populate_v1.owl"
        )
        self.graph_module_path = os.path.join(
            self.root_path, "resources/sncf/ia_flatland/models/graph_module.pkl"
        )
        self.ai_model_path = os.path.join(self.root_path, "resources/sncf/ia_flatland/models/ppo_flatland_cab.zip")
        self.recommender = Recommender(self.graph_module_path,self.ai_model_path)

    def get_recommendation(self, request_data):
        context_data = request_data.get("context", {})
        event_data = request_data.get("event", {})

        
        ai_transport_plan, ai_title, ai_description = (
            self.recommender.recommend(context_data, event_data, model="idle")
        )
        ai_recommendation = {
            "title": ai_title,
            "description": ai_description,
            "use_case": "SNCF",
            "agent_type": "IA",
            "actions": [ai_transport_plan],
        }
        

        heuristic_transport_plan, heuristic_title, heuristic_description = (
            self.recommender.recommend(context_data, event_data, model="heuristic")
        )
        heuristic_recommendation = {
            "title": heuristic_title,
            "description": heuristic_description,
            "use_case": "SNCF",
            "agent_type": "Heuristic",
            "actions": [heuristic_transport_plan],
        }

        
        fake_transport_plan, fake_title, fake_description = (
            self.recommender.recommend(context_data, event_data, model="fake")
        )
        fake_recommendation = {
            "title": "banalisation : " + fake_title,
            "description": fake_description,
            "use_case": "SNCF",
            "agent_type": "Fake",
            "actions": [fake_transport_plan],
        }
        

        recommendation = [fake_recommendation, ai_recommendation, heuristic_recommendation]

        return recommendation

    def get_procedure(self, event_type):
        if event_type != "PASSENGER":
            raise ValidationError("Invalid event_type")
        # Load ontology
        onto = get_ontology(self.owl_file_path).load()

        # save ontology
        onto.save(self.owl_file_path)

        # request procedure from ontology
        procedure = list(
            default_world.sparql(
                """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xml: <http://www.w3.org/XML/1998/namespace>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX cab: <http://www.semanticweb.org/scdsahv/ontologies/2022/5/untitled-ontology-5#>
SELECT ?blockIndex ?blockDescription ?taskIndex ?taskText
WHERE { 
  ?alarm rdf:type cab:Alarm .
  ?alarm cab:HasProcedure ?procedure .  
  ?procedure cab:HasProcedureElement ?procedureBlock .  
  ?procedureBlock cab:HasDescription ?blockDescription .    
  ?procedureBlock cab:HasBlockIndex ?blockIndex .    
  ?procedureBlock cab:HasBlockElement ?blockElement .
  ?blockElement cab:TaskIndex ?taskIndex .
  ?blockElement cab:TaskText ?taskText . 
} ORDER BY ?blockIndex
    """
            )
        )

        blocks = {}
        for row in procedure:
            block_index, block_description, task_index, task_text = row
            if block_index not in blocks:
                blocks[block_index] = {
                    "description": block_description,
                    "tasks": [],
                }
            blocks[block_index]["tasks"].append(
                {"index": task_index, "text": task_text}
            )
        blocks_list = [
            {
                "index": index,
                "description": blocks[index]["description"],
                "tasks": blocks[index]["tasks"],
            }
            for index in sorted(blocks)
        ]

        result = {
            "procedure": [
                {
                    "blockIndex": block["index"],
                    "blockText": block["description"],
                    "tasks": [
                        {"taskIndex": task["index"], "taskText": task["text"]}
                        for task in block["tasks"]
                    ],
                }
                for block in blocks_list
            ]
        }
        return result
