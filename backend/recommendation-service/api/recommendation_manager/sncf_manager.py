from .base_recommendation import BaseRecommendation


class SNCFManager(BaseRecommendation):

    def get_recommendation(self, request_args):
        # TODO: Add a call for get_transportation_plan
        return {"sncf_recommendation": "recommendation"}

    def get_transportation_plan(self, context, event):
        pass
