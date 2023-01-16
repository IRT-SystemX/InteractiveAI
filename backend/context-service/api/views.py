from apiflask import APIBlueprint
from cab_common_auth.decorators import protected
from flask import request
from flask.views import MethodView

from .context_manager import ContextManager
from .schemas import ContextIn, ContextOut

api_bp = APIBlueprint("context-api", __name__, url_prefix="/api/v1")
context_manager = ContextManager()


class HealthCheck(MethodView):

    def get(self):
        return


class Context(MethodView):

    @api_bp.output(ContextOut)
    @protected
    def get(self, date):
        """Get a context"""
        return context_manager.get_context_with_date(date)


class Contexts(MethodView):

    @api_bp.output(ContextOut(many=True))
    @protected
    def get(self):
        """Get all contexts"""
        date_query_param = request.args.get('date')
        if date_query_param:
            return context_manager.get_contexts_with_date(date_query_param)

        return context_manager.get_context()

    @api_bp.input(ContextIn)
    @api_bp.output(ContextOut, status_code=201)
    @protected
    def post(self, data):
        """Add an context"""
        return context_manager.set_context(data)


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule('/context/<string:date>',
                    view_func=Context.as_view('context'))
api_bp.add_url_rule("/contexts", view_func=Contexts.as_view("contexts"))
