import json
import os

from api.manager.base_manager import BaseRecommendationManager
from owlready2 import get_ontology
from settings import logger

from .PowerGridgrid2op_poc_simulator.assistant_manager import AgentManager, AgentType


class PowerGridManager(BaseRecommendationManager):
    """PowerGrid recomendation service

    Args:
        BaseRecommendationManager (): CAB recomendation service instance
    """

    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.owl_file_path = os.path.join(
            script_dir, "ontology/Grid2onto_v2_3_1.owl"
        )
        self.rl_agent_manager = AgentManager()
        super().__init__()

    def get_recommendation(self, request_data):
        """Get IA agent and ontology recomendations

        Args:
            request_data (dict): A dictionary with keys "context" and "event"

        Returns:
            list[dict]: List of recomendations
        """
        self.rl_agent_manager.create_recommendation(
            request_data.get("context", {}).get("observation")
        )

        logger.info("Getting parades")
        parades = self.rl_agent_manager.get_list_of_parade_info()

        onto_recommendation = []
        event_data = request_data.get("event", {})
        event_line = event_data.get("line")
        if event_line:
            logger.info("Getting ontology recommendation")
            onto_recommendation = self.get_onto_recommendation(event_line)
            logger.info(onto_recommendation)
            print(onto_recommendation)
        # both parades & onto_recommendation should be lists on the same format
        return parades + onto_recommendation

    def get_onto_recommendation(self, event_line):
        """Get Ontology recomendations

        Args:
            event_line (string): Line name

        Returns:
            dict: One ontology recomendation
        """
        # Default output
        output_json = {
            "title": "Default Ontology Recommendation",
            "description": (
                "No recommendation has been found for this overload, because "
                "it has not been observed in the past."
            ),
            "use_case": "PowerGrid",
            "agent_type": AgentType.onto.name,
            "actions": [{}],
            "kpis": {
                "type_of_the_reco": "Null",
                "efficiency_of_the_reco": 1.99999,
            },
        }

        # Loading ontology
        rte_onto = get_ontology(self.owl_file_path).load()

        # Get all powerlines
        powerlines_query = """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX x_1.1: <http://purl.org/dc/elements/1.1/>
            PREFIX xml: <http://www.w3.org/XML/1998/namespace>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX cab: <http://www.semanticweb.org/emna.amdouni/ontologies/2023/0/Grid2Onto#>

            SELECT DISTINCT ?line
            WHERE {{
                ?line rdf:type cab:Powerline .
            }}
        """

        powerlines_list = list(rte_onto.world.sparql(powerlines_query))

        our_powerline = "powerline_" + event_line

        selected_powerline = None

        for powerline in powerlines_list:

            if our_powerline in str(powerline[0]):
                selected_powerline = str(powerline[0])
                break

        if selected_powerline is not None:
            parts_prefix = selected_powerline.split(".")
            prefix_onto = parts_prefix[0] + "."
            selected_powerline = selected_powerline.replace(prefix_onto, "")

            selected_powerline_iri = (
                "http://www.semanticweb.org/emna.amdouni/ontologies/2023/0/Grid2Onto#"
                + selected_powerline
            )

            # Get all similar situations
            similar_situations_query = """
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX x_1.1: <http://purl.org/dc/elements/1.1/>
                PREFIX xml: <http://www.w3.org/XML/1998/namespace>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX cab: <http://www.semanticweb.org/emna.amdouni/ontologies/2023/0/Grid2Onto#>
            
                SELECT DISTINCT ?similarIssue ?line ?pastActionText ?actionDictVal ?category ?efficacity 
                            {{ 
                                ?similarIssue a cab:Powerline_overload_issue .
                                ?similarIssue cab:is_associated_with ?pastAction .
                                ?pastAction cab:has_initial_value ?pastActionText .
                                ?pastAction rdf:type ?category .
                                ?actionDict a cab:Action_dict .
                                ?pastAction cab:has_part ?actionDict .
                                ?actionDict cab:has_initial_value ?actionDictVal .
                                ?initial a cab:Initial_situation . 
                                ?initial cab:has_part ?pastAction .
                                ?line a cab:Powerline . 
                                ?initial cab:is_about ?line . 
                                ?rho a  cab:Rho .
                                ?similarIssue cab:has_measurement ?rho .
                                ?rho cab:has_final_value ?efficacity
                                FILTER (?category != <http://www.w3.org/2002/07/owl#NamedIndividual>)
                                FILTER (?line = <{line}>)
                            }}
                    """.format(
                line=selected_powerline_iri
            )

            similar_situations = list(
                rte_onto.world.sparql(similar_situations_query)
            )
            if similar_situations:
                # compute number of situations and rho max
                distinct_recommendations = set()
                rho_max = min(sublist[-1] for sublist in similar_situations)

                for situation in similar_situations:
                    recommendation = str(situation[2])
                    action = str(situation[3])
                    action = action.replace("'", '"')
                    action = action.replace("False", "false").replace(
                        "True", "true"
                    )
                    action_dict = json.loads(action)

                    category = str(situation[4])
                    category = category.replace(prefix_onto, "")
                    efficacity = situation[4]
                    if recommendation not in distinct_recommendations:
                        distinct_recommendations.add(recommendation)

                        nb_past_actions_query = f"""
                            PREFIX owl: <http://www.w3.org/2002/07/owl#>
                            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                            PREFIX x_1.1: <http://purl.org/dc/elements/1.1/>
                            PREFIX xml: <http://www.w3.org/XML/1998/namespace>
                            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                            PREFIX cab: <http://www.semanticweb.org/emna.amdouni/ontologies/2023/0/Grid2Onto#>  

                        SELECT (COUNT(?pastActionText) AS ?count)
                        WHERE {{
                            ?similarIssue a cab:Powerline_overload_issue .
                            ?similarIssue cab:is_associated_with ?pastAction .
                            ?pastAction cab:has_initial_value ?pastActionText .
                            ?initial a cab:Initial_situation . 
                            ?initial cab:has_part ?pastAction .
                            ?line a cab:Powerline . 
                            ?initial cab:is_about ?line . 
                            FILTER (?line = <{selected_powerline_iri}> && CONTAINS(?pastActionText, '{recommendation}'))
                        }}
                        """
                        nb_similar_situations = list(
                            rte_onto.world.sparql(nb_past_actions_query)
                        )[0][0]
                        output_json = {
                            "title": recommendation,
                            "description": f"This pattern has been observed {nb_similar_situations} times in the past.",
                            "use_case": "PowerGrid",
                            "agent_type": AgentType.onto.name,
                            "actions": [action_dict],
                            "kpis": {
                                "type_of_the_reco": category,
                                "efficiency_of_the_reco": rho_max,
                            },
                        }

        return [output_json]
