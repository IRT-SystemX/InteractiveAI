from .base_recommendation import BaseRecommendation


class RTEManager(BaseRecommendation):

    def get_recommendation(self, request_args):
        # TODO: Add a call for make_recommendation & get_onto_recommendation
        return {"rte_recommendation": "recommendation"}

    def make_recommendation(self, obs):
        pass

    def get_onto_recommendation(self, event_line, event_flow):
        pass
