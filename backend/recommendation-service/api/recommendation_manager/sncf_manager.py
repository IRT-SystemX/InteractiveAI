from resources.sncf.hypervisor import Hypervisor
from .base_recommendation import BaseRecommendation
from flask import current_app
import os


class SNCFManager(BaseRecommendation):
    def __init__(self) -> None:
        super().__init__()
        self.root_path = current_app.config['ROOT_PATH']
        self.hypervisor_path = os.path.join(
            self.root_path, "resources/sncf/hypervisor.pth")
        self.hypervisor = Hypervisor()
        self.hypervisor.load(self.hypervisor_path)

    def get_recommendation(self, request_data):
        context_data = request_data.get("context", {})
        raw_position_agents = context_data.get("position_agents")
        raw_list_of_target = context_data.get("list_of_target")
        direction_agents = context_data.get("direction_agents")

        event_data = request_data.get("event", {})

        malfunction_agent = event_data.get("agent_id")
        malfunction_position = tuple(event_data.get("agent_position"))
        malfunction_delay = event_data.get("delay")

        position_agents = [tuple(value)
                           for value in raw_position_agents.values()]

        list_of_target = [[tuple(target) for target in agent_targets]
                          for agent_targets in raw_list_of_target.values()]

        ai_actions, ai_description = self.hypervisor.recommend(position_agents,
                                                   direction_agents,
                                                   list_of_target,
                                                   malfunction_agent,
                                                   malfunction_position,
                                                   malfunction_delay)
        ai_recommendation = {
            "title": "Modification de plan de transport",
            "description": ai_description,
            "use_case": "SNCF",
            "agent_type": "IA",
            "actions": [{"transportation_plan":ai_actions}]
            }
        
        #optimal_recommendation = {
        #    "title": "optimal recommendation",
        #    "description": optimal_description,
        #    "use_case": "SNCF",
        #    "agent_type": "IA",
        #    "actions": [{"transportation_plan": optimal_actions}]
        #    }

        recommendation = [ai_recommendation]#optimal_recommendation,

        return recommendation