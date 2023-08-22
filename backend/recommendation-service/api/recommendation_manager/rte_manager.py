from owlready2 import default_world, get_ontology, sync_reasoner
from resources.rte.rtegrid2op_poc_simulator.assistantManager import \
    AgentManager, AgentType
from settings import logger

from .base_recommendation import BaseRecommendation
from flask import current_app
import os


class RTEManager(AgentManager, BaseRecommendation):
    def __init__(self):
        self.root_path = current_app.config['ROOT_PATH']
        self.owl_file_path = os.path.join(
            self.root_path, "resources/rte/ontology/Onto2grid_v1.2.owl")
        super().__init__()

    def get_recommendation(self, request_data):

        self.recommendate(request_data.get("context", {}))
        logger.info("getting parades")
        parades = self.getlistOfParadeInfo()

        onto_recommendation = None
        event_data = request_data.get("event", {})
        event_id = event_data.get("event_id")
        event_line = event_data.get("event_line")
        event_flow = event_data.get("event_flow")
        if event_id and event_line and event_flow:
            logger.info("getting ontology recommendation")
            onto_recommendation = self.get_onto_recommendation(
                event_id, event_line, event_flow)
        # both parades & onto_recommendation should be lists on the same format
        return parades + onto_recommendation

    def get_onto_recommendation(self, event_id, event_line, event_flow):
        # Loading ontology
        RTE_onto = get_ontology(self.owl_file_path).load()

        # Creation of the RDF instances
        issue_test = RTE_onto.Issue(event_id)
        powerline_test = RTE_onto.Powerline(event_line)
        rho_test = RTE_onto.Rho("rho_test")

        # Linking between the RDF instances
        issue_test.has_measurement.append(rho_test)
        rho_test.has_value = event_flow
        rho_test.is_about.append(powerline_test)

        # Updating the knowledge graph with RDF instances
        RTE_onto.save(file=self.owl_file_path, format="rdfxml")

        # Launching the reasoner to inference data
        RTE_onto_inferences = get_ontology(self.owl_file_path).load()
        with RTE_onto_inferences:
            sync_reasoner(infer_property_values=True)

        for i in RTE_onto_inferences.Powerline_overload_issue.instances():
            print(i)

        print(RTE_onto_inferences.issue_test)

        if isinstance(issue_test, RTE_onto_inferences.Powerline_overload_issue):
            results = list(default_world.sparql("""
                    SELECT DISTINCT ?similarIssue ?line ?rhovalue ?pastAction
                    { 
                        ?similarIssue a Onto2grid_v1.2:Powerline_overload_issue .
                        ?similarIssue Onto2grid_v1.2:is_associated_with ?pastAction .
                        ?rho a Onto2grid_v1.2:Rho .
                        ?rho Onto2grid_v1.2:has_value ?rhovalue .
                        ?rho  Onto2grid_v1.2:is_about ?line
                        ?similarIssue Onto2grid_v1.2:has_measurement ?rho .
                    }
                    """))
            print("Here is a list of similar situations:", results)

        # Updating the knowledge graph by including an RDF triple <issue_test, associated_with, Change_bus_vect_test>
        set_bus_test = RTE_onto_inferences.Change_bus_vect("set_bus_test")
        issue_test.is_associated_with.append(set_bus_test)

        action = str(RTE_onto_inferences.get_parents_of(set_bus_test)[0])

        if action == 'Onto2grid_v1.2.Change_bus_vect':
            Titre = "Changer le bus"
        elif action == "Onto2grid_v1.2.Disconnect_line":
            Titre = "Deconnecter la ligne"
        else:
            Titre = "Parade non identifiée"

        recommendation = {"Title":Titre, "Description": "", "Use_case":"RTE", "Agent_type": AgentType.onto.name, "Action": {}}
        return [recommendation]
