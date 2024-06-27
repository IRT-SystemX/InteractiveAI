import uuid

from apiflask import APIBlueprint
from apiflask.views import MethodView
from cab_common_auth.decorators import protected_admin
from sqlalchemy.exc import OperationalError

from .models import FeedbackModel, db
from .schemas import FeedbackIn, FeedbackOut

api_bp = APIBlueprint("context-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):

    def get(self):
        return {"message": "Ok"}


class Feedback(MethodView):

    @api_bp.output(FeedbackOut(many=True))
    def get(self):
        """Get all feedback"""
        return FeedbackModel.query.all()

    @api_bp.input(FeedbackIn)
    @api_bp.output(FeedbackOut, status_code=201)
    def post(self, data):
        """Add a feedback"""
        feedback_id = uuid.uuid4()
        data["id_feedback"] = str(feedback_id)
        feedback = FeedbackModel(**data)
        db.session.add(feedback)
        db.session.commit()
        return feedback


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
api_bp.add_url_rule("/feedbacks", view_func=Feedback.as_view("feedbacks"))
