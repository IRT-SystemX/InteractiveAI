from apiflask import APIBlueprint
from cab_common_auth.decorators import protected
from .recommendation_manager import RecommendationManager
from flask import request
from flask.views import MethodView

from .schemas import RecommendationAsk, Recommendation
from settings import logger
api_bp = APIBlueprint("recommendation-api", __name__, url_prefix="/api/v1")
recommendation_manager = RecommendationManager()


class HealthCheck(MethodView):

    def get(self):
        return


class RecommendationView(MethodView):

    @api_bp.output(Recommendation)
    @protected
    def get(self):
        """Get recommendation matrix"""
        return {"recommendation": []}


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule(
    "/recommendation", view_func=RecommendationView.as_view("recommendation"))
