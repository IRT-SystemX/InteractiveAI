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
            self.root_path, "resources/da/ontology/final_populate_v20.rdf"
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
        onto_recommendation = None
        event_data = request_data.get("event", {})
        event_type = event_data.get("event_type")

        if event_type:
            logger.info("getting ontology recommendation")
            onto_recommendation = self.get_procedure(
                event_type)

        return {"da_recommendation": onto_recommendation}

    def get_procedure(self, event_type):
        # Load ontology
        DA_onto = get_ontology(self.owl_file_path).load()
        minSpeed = 180
        maxSpeed = 260
        alarms_query = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX cab: <http://www.dassault-aviation.com/ontologies/2023/10/FalconProcedures#>
            SELECT ?alarm
            WHERE {
                ?alarm rdf:type cab:Alarm .
            }
        """
        # Execute the query
        alarms = list(default_world.sparql(alarms_query))
        updated_alarms = []
        prefix = "final_populate_v20."
        for alarm in alarms:
            alarm_uri = str(alarm[0])
            if alarm_uri.startswith(prefix):
                alarm_n = alarm_uri[len(prefix):]
            else:
                alarm_n = alarm_uri
            updated_alarms.append(alarm_n) 

        all_events = {
            "90 PRESS: CABIN ALT TOO HIGH": updated_alarms[1],
            "38 ELEC: GEN 1+2+3 FAULT": updated_alarms[0],
                }
        print("PRINTING EVENTS")
        print(all_events)
        print("PRINTING alarm Name ")
        alarm_name = all_events[event_type]
        print(alarm_name)

        alarm_uri = "http://www.dassault-aviation.com/ontologies/2023/10/FalconProcedures#"+alarm_name
        procedure_query = f"""
            PREFIX core: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dcam: <http://purl.org/dc/dcam/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX term: <http://purl.org/dc/terms/>
            PREFIX x_1.1: <http://purl.org/dc/elements/1.1/>
            PREFIX xml: <http://www.w3.org/XML/1998/namespace>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX cab: <http://www.dassault-aviation.com/ontologies/2023/10/FalconProcedures#>
            SELECT ?blockIndex ?blockDescription ?blockAssign ?taskIndex ?taskText
            WHERE {{
                ?alarm rdf:type cab:Alarm .
                FILTER (?alarm = <{alarm_uri}>)
                ?alarm cab:HasProcedure ?procedure .
                ?procedure cab:HasProcedureElement ?procedureBlock .
                ?procedureBlock cab:HasDescription ?blockDescription .
                ?procedureBlock cab:HasBlockIndex ?blockIndex .
                ?procedureBlock cab:HasBlockElement ?blockElement .
                ?procedureBlock cab:IsAssignableBlock ?blockAssign .
                ?blockElement cab:TaskIndex ?taskIndex .
                ?blockElement cab:TaskText ?taskText .
            }} ORDER BY ?blockIndex
        """
        print("PRINTING PROCEDURE")
        
        results = list(default_world.sparql(procedure_query))
        print(results)
        updated_results = []
        for result in results:
            print("RESULT IN FOR LOOP")
            print(result)
            block_index, block_description, block_assign, task_index, task_text = result
            block_assign = block_assign.name if hasattr(block_assign, 'name') else block_assign
            if block_assign in ['ASSIGNABLE_CREW', 'ASSIGNABLE_LOCKED']:
                block_assign = False
            elif block_assign == 'ASSIGNABLE_FREE':
                block_assign = True
            updated_results.append([block_index, block_description, block_assign, task_index, task_text ])
            blocks = {}

            print("UPDATED RESULTS in FOR LOOP")
            print(updated_results)

        for row in updated_results:
            print("ROW IN 2ND FOR LOOP")
            block_index, block_description,block_assign, task_index, task_text = row
            print(row)
            if block_index not in blocks:
                blocks[block_index] = {"description": block_description, "assignable":block_assign, "tasks": []}
                print("block in 2nd for in if condition")
                print(blocks)
            blocks[block_index]["tasks"].append({"index": task_index, "text": task_text})
            print("blocks in 2Nd for loop")
        blocks_list = [{"index": index, "description": blocks[index]["description"], "assignable":blocks[index]["assignable"], "tasks": blocks[index]["tasks"]} for index in sorted(blocks)]
        print("BLOCKS LIST")
        print(blocks_list)
        final_result = {
            'Procedure': [
                {
                    'blockIndex': block['index'],
                    'enableAssistance':block['assignable'],
                    'blockText': block['description'],
                    'blockTasks': [
                        {
                            'taskIndex': task['index'],
                            'taskText': task['text']
                        } for task in block['tasks']
                    ]
                } for block in blocks_list
            ]
        }
        print("JSON PROCEDURE")
        print(final_result)
        return final_result
