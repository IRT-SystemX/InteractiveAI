from resources.sncf.hypervisor import Hypervisor
from .base_recommendation import BaseRecommendation


class SNCFManager(BaseRecommendation):
    def __init__(self) -> None:
        super().__init__()
        self.hypervisor = Hypervisor()
        self.hypervisor.load("/code/resources/sncf/hypervisor.pth")

    def get_recommendation(self, request_data):
        context_data = request_data.get("context", {})
        raw_position_agents = context_data.get("position_agents")
        raw_list_of_target = context_data.get("list_of_target")
        direction_agents = context_data.get("direction_agents")

        event_data = request_data.get("event", {})

        malfunction_agent = event_data.get("malfunction_agent")
        malfunction_position = tuple(event_data.get("malfunction_position"))
        malfunction_delay = event_data.get("malfunction_delay")

        position_agents = [tuple(value)
                           for value in raw_position_agents.values()]
        list_of_target = [tuple(value)
                          for value in raw_list_of_target.values()]
        recommendation = self.hypervisor.recommend(position_agents,
                                                   direction_agents,
                                                   list_of_target,
                                                   malfunction_agent,
                                                   malfunction_position,
                                                   malfunction_delay)

        return {"recommendation": recommendation}
