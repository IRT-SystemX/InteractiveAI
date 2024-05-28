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
            self.root_path, "resources/rte/ontology/Grid2onto_v2_3.owl"
        )
        self.onto_iao_file = os.path.join(
            self.root_path, "resources/rte/ontology/iao_module.owl"
        )
        self.onto_bfo_file = os.path.join(
            self.root_path, "resources/rte/ontology/bfo_module.owl"
        )
        super().__init__()

    def get_recommendation(self, request_data):
        self.recommendate(request_data.get("context", {}).get("observation"))
        logger.info("Getting parades")
        parades = self.getlistOfParadeInfo()

        onto_recommendation = []
        event_data = request_data.get("event", {})
        event_id = event_data.get("event_id")
        event_line = event_data.get("line")
        event_flow = event_data.get("flux")
        if event_line:
            logger.info("Getting ontology recommendation")
            onto_recommendation = self.get_onto_recommendation(event_line)
            logger.info(onto_recommendation)
            print(onto_recommendation)
        # both parades & onto_recommendation should be lists on the same format
        return parades + onto_recommendation

    def get_onto_recommendation(self, event_line):
        # Default output
        output_json = {
            "title":"Parade ontologique par defaut",
            "description":"Aucune recommandation n'a pu être générée",
            "use_case":"RTE",
            "agent_type":AgentType.onto.name,
            "actions":[{}],
            "kpis":{
            "type_of_the_reco":"Null",
            "efficiency_of_the_reco":1.99999
            }
        }

        # Loading ontology
        RTE_onto = get_ontology(self.owl_file_path).load()
        onto_iao = get_ontology(self.onto_iao_file).load()
        onto_bfo = get_ontology(self.onto_bfo_file).load()
        RTE_onto.imported_ontologies.append(onto_iao)
        RTE_onto.imported_ontologies.append(onto_bfo)
        RTE_onto.save(file=self.owl_file_path, format="rdfxml")

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

        powerlines_list = list(RTE_onto.world.sparql(powerlines_query))

        our_powerline = "powerline_"+event_line

        selected_powerline = None

        for powerline in powerlines_list:

            if our_powerline in str(powerline[0]) :
                selected_powerline = str(powerline[0])
                break  

        if selected_powerline is not None:      
            parts_prefix = selected_powerline.split('.')
            prefix_onto = parts_prefix[0] + '.' 
            selected_powerline = selected_powerline.replace(prefix_onto,"")

            selected_powerline_iri = "http://www.semanticweb.org/emna.amdouni/ontologies/2023/0/Grid2Onto#" + selected_powerline

            ## Get all similar situations
            similar_situations_query = """
                PREFIX owl: <http://www.w3.org/2002/07/owl#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX x_1.1: <http://purl.org/dc/elements/1.1/>
                PREFIX xml: <http://www.w3.org/XML/1998/namespace>
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                PREFIX cab: <http://www.semanticweb.org/emna.amdouni/ontologies/2023/0/Grid2Onto#>
            
            SELECT DISTINCT ?similarIssue ?line ?pastActionText ?category ?efficacity 
                        {{ 
                            ?similarIssue a cab:Powerline_overload_issue .
                            ?similarIssue cab:is_associated_with ?pastAction .
                            ?pastAction cab:has_initial_value ?pastActionText .
                            ?pastAction rdf:type ?category .
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
                    """.format(line=selected_powerline_iri)

            similar_situations = list(RTE_onto.world.sparql(similar_situations_query))
            if similar_situations:
                # compute number of situations and rho max
                distinct_recommendations = set()
                rho_max = min(sublist[-1] for sublist in similar_situations)

                for situation in similar_situations:
                    recommendation = str(situation[2])
                    category = str(situation[3])
                    category = category.replace(prefix_onto,"")
                    efficacity = situation[4]
                    if recommendation not in distinct_recommendations:
                        distinct_recommendations.add(recommendation)

                        nb_past_Actions_query = f"""
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
                        nb_similar_situations = list(RTE_onto.world.sparql(nb_past_Actions_query))[0][0]
                        output_json = {
                            "title":recommendation,
                            "description":f"Cette parade a été rencontrée {nb_similar_situations} fois dans le passé.",
                            "use_case":"RTE",
                            "agent_type":AgentType.onto.name,
                            "actions":[{}],
                            "kpis":{
                            "type_of_the_reco":category,
                            "efficiency_of_the_reco":rho_max
                            }
                        }

        return [output_json]
