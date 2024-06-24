import importlib

from api.utils import load_usecases_db
from apiflask import APIBlueprint, HTTPError
from apiflask.views import MethodView
from cab_common_auth.decorators import (
    get_use_cases,
    protected,
    protected_admin,
)
from flask import abort, jsonify, request
from marshmallow.exceptions import ValidationError
from settings import logger
from sqlalchemy.exc import IntegrityError, OperationalError

from .exceptions import InvalidUseCase
from .models import UseCaseModel, db
from .schemas import (
    ProcedureOut,
    RecommendationAsk,
    RecommendationOut,
    UseCaseIn,
    UseCaseOut,
)

api_bp = APIBlueprint("recommendation-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):

    def get(self):
        return {"message": "Ok"}


class RecommendationView(MethodView):

    @api_bp.input(RecommendationAsk)
    @api_bp.output(RecommendationOut(many=True), status_code=201)
    @protected
    def post(self, data):
        """Get recommendation"""
        # Get data from the request
        request_use_case = request.args.get("use_case")
        token_use_case_list = get_use_cases()
        if len(token_use_case_list) > 1 and not request_use_case:
            return abort(
                400,
                "User registred for more than one entity, specify use_case",
            )
        elif request_use_case:
            use_case_name = request_use_case
        else:
            use_case_name = token_use_case_list[0]
        from flask import current_app

        use_case_factory = current_app.use_case_factory

        try:
            manager = use_case_factory.get_recommendation_manager(
                use_case_name
            )
        except InvalidUseCase as invalid_use_case:
            logger.error(f"Invalid use case {use_case_name} detected")
            raise invalid_use_case

        # Call the appropriate method on the use case
        result = manager.get_recommendation(data)

        # Return the result as JSON
        return jsonify(result)


class ProcedureView(MethodView):

    @api_bp.input(RecommendationAsk)
    @api_bp.output(ProcedureOut(many=True), status_code=201)
    @protected
    def post(self, data):
        """Get procedure"""
        # Get data from the request
        request_use_case = request.args.get("use_case")
        token_use_case_list = get_use_cases()
        if len(token_use_case_list) > 1 and not request_use_case:
            return abort(
                400,
                "User registred for more than one entity, specify use_case",
            )
        elif request_use_case:
            use_case_name = request_use_case
        else:
            use_case_name = token_use_case_list[0]
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        # Create an instance of the appropriate use case class using the factory
        use_case = use_case_factory.get_use_case(use_case_name)

        # Call the appropriate method on the use case
        event_data = data.get("event", {})
        event_type = event_data.get("event_type")
        try:
            result = use_case.get_procedure(event_type)
            # Return the result as JSON
            return jsonify(result)
        except ValidationError as e:
            raise HTTPError(400, message=e.messages[0])


class UseCases(MethodView):
    @api_bp.output(UseCaseOut(many=True))
    @protected_admin
    def get(self):
        """Get all events"""
        return UseCaseModel.query.all()

    @api_bp.input(UseCaseIn)
    @api_bp.output(UseCaseOut, status_code=201)
    @protected_admin
    def post(self, data):
        """Add an event"""
        from flask import current_app

        use_case_factory = current_app.use_case_factory

        use_case_db = UseCaseModel(**data)

        # Dynamically import the event manager class
        manager_module = importlib.import_module(
            f"resources.{use_case_db.name}.manager"
        )
        manager_class = getattr(manager_module, f"{use_case_db.manager_class}")
        manager_instance = manager_class()

        # register use case to use_case_factory
        use_case_factory.register_use_case(use_case_db.name, manager_instance)

        # save use case to db
        try:
            # Attempt to add the use case to the database
            db.session.add(use_case_db)
            db.session.commit()
        except IntegrityError:
            # If a unique constraint violation occurs, update the existing record
            db.session.rollback()
            existing_use_case = UseCaseModel.query.filter_by(
                name=use_case_db.name
            ).first()
            existing_use_case.__dict__.update(use_case_db.__dict__)

            db.session.commit()
        return use_case_db


class UseCase(MethodView):
    @api_bp.output(UseCaseOut, status_code=204)
    @protected
    def delete(self, use_case_id):
        """Delete an event by ID"""
        use_case = UseCaseModel.query.get(use_case_id)

        if use_case:
            db.session.delete(use_case)
            db.session.commit()
            return None, 204  # No content, indicating successful deletion
        else:
            return {"error": "Use case not found"}, 404


class DeleteDataService(MethodView):
    @protected_admin
    def delete(self):
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        try:
            # unregister all use_cases
            use_case_factory.unregister_all_use_cases()
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
            load_usecases_db(use_case_factory)
            return {"error": str(e)}, 500


api_bp.add_url_rule(
    "/delete_all_data", view_func=DeleteDataService.as_view("delete_data")
)
api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule(
    "/recommendation", view_func=RecommendationView.as_view("recommendation")
)
api_bp.add_url_rule("/procedure", view_func=ProcedureView.as_view("procedure"))


api_bp.add_url_rule("/usecases", view_func=UseCases.as_view("usecases"))
api_bp.add_url_rule(
    "/usecase/<int:use_case_id>", view_func=UseCase.as_view("usecase")
)
