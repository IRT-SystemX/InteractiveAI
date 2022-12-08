import uuid

from apiflask import APIBlueprint
from flask.views import MethodView

from .models import TraceModel, db
from .schemas import TraceIn, TraceOut

api_bp = APIBlueprint("context-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):

    def get(self):
        return


class Trace(MethodView):

    @api_bp.output(TraceOut(many=True))
    def get(self):
        """Get all traces"""
        return TraceModel.query.all()

    @api_bp.input(TraceIn)
    @api_bp.output(TraceOut, status_code=201)
    def post(self, data):
        """Add an traces"""
        trace_id = uuid.uuid4()
        data["id_trace"] = str(trace_id)
        trace = TraceModel(**data)
        db.session.add(trace)
        db.session.commit()
        return trace


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/traces", view_func=Trace.as_view("traces"))
