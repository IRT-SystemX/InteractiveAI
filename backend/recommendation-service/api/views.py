from apiflask import APIBlueprint
from cab_common_auth.decorators import get_use_cases, protected
from flask import request, jsonify, abort
from apiflask.views import MethodView

from .schemas import RecommendationAsk
from settings import logger


api_bp = APIBlueprint("recommendation-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):

    def get(self):
        return {"message": "Ok"}


class RecommendationView(MethodView):

    @api_bp.input(RecommendationAsk)
    @protected
    def post(self, data):
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
        from flask import current_app
        use_case_factory = current_app.use_case_factory
        # Create an instance of the appropriate use case class using the factory
        use_case = use_case_factory.get_use_case(use_case_name)

        # Call the appropriate method on the use case
        result = use_case.get_recommendation(data)

        # Return the result as JSON
        return jsonify(result)


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule(
    "/recommendation", view_func=RecommendationView.as_view("recommendation"))
