from apiflask import APIBlueprint
from flask.views import MethodView
from flask import request
from .schemas import ContextIn, ContextOut
from .context_manager import ContextManager

api_bp = APIBlueprint("context-api", __name__, url_prefix="/api/v1")
context_manager = ContextManager()

class HealthCheck(MethodView):

    def get(self):
        return


class Contexts(MethodView):

    @api_bp.output(ContextOut(many=True))
    def get(self):
        """Get all contexts"""
        date_query_param = request.args.get('date')
        if date_query_param:
            return context_manager.get_context_with_date(date_query_param)
        
        return context_manager.get_context()

    @api_bp.input(ContextIn)
    @api_bp.output(ContextOut, status_code=201)
    def post(self, data):
        """Add an context"""
        return context_manager.set_context(data)


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/contexts", view_func=Contexts.as_view("contexts"))
