from .base_recommendation import BaseRecommendation


class DAManager(BaseRecommendation):

    def get_recommendation(self, request_args):
        # TODO: Add a call for get_procedure
        return {"da_recommendation": "recommendation"}

    def get_procedure(self, event_type):
        pass
