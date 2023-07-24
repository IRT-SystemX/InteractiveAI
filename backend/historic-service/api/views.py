import uuid

from apiflask import APIBlueprint
from apiflask.views import MethodView
from flask import request
from .models import TraceModel, db
from .schemas import TraceIn, TraceOut
from .filters import filter_trace
api_bp = APIBlueprint("context-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):

    def get(self):
        return {"message": "Ok"}


class Trace(MethodView):

    @api_bp.output(TraceOut(many=True))
    def get(self):
        """Get all traces"""
        return (filter_trace(TraceModel.query, request.args)).all()

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
