import uuid

from apiflask import APIBlueprint
from apiflask.views import MethodView
from cab_common_auth.decorators import protected_admin
from flask import request
from sqlalchemy.exc import OperationalError

from .filters import filter_trace
from .models import TraceModel, db
from .schemas import TraceIn, TraceOut

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


class DeleteDataService(MethodView):
    @protected_admin
    def delete(self):
        try:
            # Delete all records from all models
            for mapper in db.Model.registry.mappers:
                model = mapper.class_
                if hasattr(model, "__tablename__"):
                    db.session.query(model).delete()
            db.session.commit()
            return {"message": "All data deleted successfully"}, 200
        except OperationalError as e:
            db.session.rollback()
            return {"error": str(e)}, 500
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


api_bp.add_url_rule(
    "/delete_all_data", view_func=DeleteDataService.as_view("delete_data")
)
api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/traces", view_func=Trace.as_view("traces"))
