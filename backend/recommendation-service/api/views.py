from apiflask import APIBlueprint
from cab_common_auth.decorators import get_use_cases, protected
from flask import request, jsonify, abort
from flask.views import MethodView

from .schemas import RecommendationAsk, BaseRecommendation
from settings import logger
from .utils import UseCaseFactory
from .recommendation_manager.da_manager import DAManager
from .recommendation_manager.rte_manager import RTEManager
from .recommendation_manager.sncf_manager import SNCFManager


api_bp = APIBlueprint("recommendation-api", __name__, url_prefix="/api/v1")
factory = UseCaseFactory()
factory.register_use_case('DA', DAManager())
factory.register_use_case('RTE', RTEManager())
factory.register_use_case('SNCF', SNCFManager())


class HealthCheck(MethodView):

    def get(self):
        return


class RecommendationView(MethodView):

    @api_bp.output(BaseRecommendation)
    @protected
    def get(self):
        """Get recommendation"""
        # Get data from the request
        request_use_case = request.args.get('use_case')
        token_use_case_list = get_use_cases()
        if len(token_use_case_list) > 1 and not request_use_case:
            return abort(400, "User registred for more than one entity, specify use_case")
        elif request_use_case:
            use_case_name = request_use_case
        else:
            use_case_name = token_use_case_list[0]

        # Create an instance of the appropriate use case class using the factory
        use_case = factory.get_use_case(use_case_name)

        # Call the appropriate method on the use case
        result = use_case.get_recommendation(request.args)

        # Return the result as JSON
        return jsonify(result)


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule(
    "/recommendation", view_func=RecommendationView.as_view("recommendation"))
