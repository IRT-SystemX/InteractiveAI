from owlready2 import default_world, get_ontology
from settings import logger
import json

from .base_recommendation import BaseRecommendation


class DAManager(BaseRecommendation):

    def __init__(self):
        self.owl_file_path = "/code/resources/da/ontology/AlarmsOntoDA.owl"
        super().__init__()

    def get_recommendation(self, request_data):
        onto_recommendation = None
        event_data = request_data.get("event", {})
        event_type = event_data.get("event_type")

        if event_type:
            logger.info("getting ontology recommendation")
            onto_recommendation = self.get_procedure(
                event_type)

        return {"da_recommendation": onto_recommendation}

    def get_procedure(self, event_type):
        minSpeed = 180
        maxSpeed = 260
        all_events = {
            '90 PRESS : ALT TOO HIGH': 'procedure_90_PRESS_CABIN_ALT_TOO_HI',
            'ENG1: AUTO SHUTDOWN': 'procedure_ENG1_AUTO_SHUTDOWN'
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
        procedure = list(default_world.sparql("""
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

            """))

        # jsonify & add index
        procedure_dict = {"Procedure": [], 'minSpeed': minSpeed, 'maxSpeed': maxSpeed}

        for i, sub_list in enumerate(procedure):
            task_dict = {"TaskIndex": i + 1, "TaskText": sub_list[0]}

            procedure_dict["Procedure"].append(task_dict)

        # Convertir le dictionnaire en format JSON
        json_string = json.dumps(procedure_dict)

        return json_string

