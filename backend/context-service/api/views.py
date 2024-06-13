import importlib

from apiflask import APIBlueprint
from apiflask.views import MethodView
from cab_common_auth.decorators import (get_use_cases, protected,
                                        protected_admin)
from flask import request
from settings import logger
from sqlalchemy.exc import IntegrityError, OperationalError
from utils import load_usecases_db

from .models import UseCaseModel, db
from .schemas import ContextIn, ContextOut, UseCaseIn, UseCaseOut

api_bp = APIBlueprint("context-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):
    def get(self):
        return {"message": "Ok"}


class Context(MethodView):
    @api_bp.output(ContextOut)
    @protected
    def get(self, date):
        """Get a context"""
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        use_cases = get_use_cases()
        context_list = []
        for use_case in use_cases:
            context_manager = use_case_factory.get_context_manager(use_case)
            context_list.append(context_manager.get_context_with_date(date))
        return context_list


class Contexts(MethodView):
    @api_bp.output(ContextOut(many=True))
    @protected
    def get(self):
        """Get all contexts"""

        def get_context_list(use_case_factory, date_query_param, use_cases):
            context_list = []

            for use_case in use_cases:
                context_manager = use_case_factory.get_context_manager(
                    use_case
                )
                if date_query_param:
                    context_r = context_manager.get_contexts_with_date(
                        date_query_param
                    )
                else:
                    context_r = [context_manager.get_context()]
                context_list = context_list + context_r
            return context_list

        from flask import current_app

        use_case_factory = current_app.use_case_factory
        date_query_param = request.args.get("date")
        use_case_query_param = request.args.get("use_case")
        use_cases = get_use_cases()
        logger.error(use_cases)
        logger.error(use_case_query_param)

        if use_case_query_param and (use_case_query_param in use_cases):
            use_cases = [use_case_query_param]

        context_list = get_context_list(
            use_case_factory, date_query_param, use_cases
        )

        return context_list

    @api_bp.input(ContextIn)
    @api_bp.output(ContextOut, status_code=201)
    @protected
    def post(self, data):
        """Add an context"""
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        use_case = data.get("use_case")
        context_manager = use_case_factory.get_context_manager(use_case)
        return context_manager.set_context(data)


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
        context_manager_module = importlib.import_module(
            f"resources.{use_case_db.name}.context_manager"
        )
        context_manager_class = getattr(
            context_manager_module, f"{use_case_db.context_manager_class}"
        )
        context_manager_instance = context_manager_class()

        # register use case to use_case_factory
        use_case_factory.register_use_case(
            use_case_db.name, context_manager_instance
        )

        # Dynamically import the metadata schema class
        metadata_schema_module = importlib.import_module(
            f"resources.{use_case_db.name}.schemas"
        )
        getattr(metadata_schema_module, f"{use_case_db.metadata_schema_class}")

        # save use case to db
        # db.session.add(use_case_db)
        # db.session.commit()
        try:
            # Attempt to add the use case to the database
            db.session.add(use_case_db)
            db.session.commit()
        except IntegrityError as e:
            # If a unique constraint violation occurs, update the existing record
            db.session.rollback()
            existing_use_case = UseCaseModel.query.filter_by(name=use_case_db.name).first()
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
    "/context/<string:date>", view_func=Context.as_view("context")
)
api_bp.add_url_rule("/contexts", view_func=Contexts.as_view("contexts"))
api_bp.add_url_rule("/usecases", view_func=UseCases.as_view("usecases"))
api_bp.add_url_rule(
    "/usecase/<int:use_case_id>", view_func=UseCase.as_view("usecase")
)
