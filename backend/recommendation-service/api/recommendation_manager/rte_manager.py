from .base_recommendation import BaseRecommendation
from resources.rte.rtegrid2op_poc_simulator.assistantManager import AgentManager
from owlready2 import *
import owlready2.sparql.parser


class RTEManager(AgentManager, BaseRecommendation):

    def get_recommendation(self, request_args):
        self.recommandate(request_args.get("context", {}))
        parades = self.getlistOfParadeInfo()
        return {"ia_recommendation": parades}

    def get_onto_recommendation(self, event_id, event_line, event_flow):
        # Loading ontology
        RTE_onto = get_ontology("Onto2grid_v1.2.owl").load()

        # Creation of the RDF instances
        issue_test = RTE_onto.Issue(event_id)
        powerline_test = RTE_onto.Powerline(event_line)
        rho_test = RTE_onto.Rho("rho_test")

        # Linking between the RDF instances
        issue_test.has_measurement.append(rho_test)
        rho_test.has_value = event_flow
        rho_test.is_about.append(powerline_test)

        # Updating the knowledge graph with RDF instances
        RTE_onto.save(file="Onto2grid_v1.2.owl", format="rdfxml")

        # Launching the reasoner to inference data
        RTE_onto_inferences = get_ontology("Onto2grid_v1.2.owl").load()
        with RTE_onto_inferences:
            sync_reasoner(infer_property_values=True)

        for i in RTE_onto_inferences.Powerline_overload_issue.instances(): print(i)

        print(RTE_onto_inferences.issue_test)

        if isinstance(issue_test, RTE_onto_inferences.Powerline_overload_issue):
            print("boucle if")
            exist = True

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

        # Display the action recommandation
        print("The recommanded action is:", RTE_onto_inferences.get_parents_of(set_bus_test))
        recommandation = RTE_onto_inferences.get_parents_of(set_bus_test)[0]

        return recommandation
