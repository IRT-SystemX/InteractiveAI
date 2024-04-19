import importlib

from api.exceptions import InvalidUseCase
from apiflask import APIBlueprint
from apiflask.views import MethodView
from cab_common_auth.decorators import (get_use_cases, protected,
                                        protected_admin)
from settings import logger
from sqlalchemy.exc import IntegrityError

from .models import EventModel, UseCaseModel, db
from .schemas import EventIn, EventOut, UseCaseIn, UseCaseOut

api_bp = APIBlueprint("event-api", __name__, url_prefix="/api/v1")


class HealthCheck(MethodView):
    def get(self):
        return {"message": "Ok"}


class Event(MethodView):
    @api_bp.output(EventOut)
    @protected
    def get(self, event_id):
        """Get an event by ID"""
        event = EventModel.query.get(event_id)
        if event:
            return event

        return {"error": "Event not found"}, 404

    @protected
    def delete(self, event_id):
        """Delete an event by ID"""
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        use_cases = get_use_cases()
        for use_case in use_cases:
            try:
                event_manager = use_case_factory.get_event_manager(use_case)
            except InvalidUseCase:
                logger.error(f"Invalid use case {use_case} detected")

        return event_manager.delete_event(event_id)


class Events(MethodView):
    @api_bp.output(EventOut(many=True))
    @protected
    def get(self):
        """Get all events"""
        use_cases = get_use_cases()
        return EventModel.query.filter(EventModel.use_case.in_(use_cases))

    @api_bp.input(EventIn)
    @api_bp.output(EventOut, status_code=201)
    @protected
    def post(self, data):
        """Add an event"""
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        use_case = data["use_case"]
        try:
            event_manager = use_case_factory.get_event_manager(use_case)
        except InvalidUseCase as invalid_use_case:
            logger.error(f"Invalid use case {use_case} detected")
            raise invalid_use_case
        event = event_manager.create_event(data)
        return event


class EventsList(MethodView):
    @api_bp.input(EventIn(many=True))
    @api_bp.output(EventOut(many=True), status_code=201)
    @protected
    def post(self, data):
        """Add an event"""
        from flask import current_app

        use_case_factory = current_app.use_case_factory
        use_cases = get_use_cases()
        events_list = []
        for use_case in use_cases:
            event_manager = use_case_factory.get_event_manager(use_case)
            # Ensure parent_event_id is processed for each event in the list
            for event_data in data:
                event_data["parent_event_id"] = event_data.get(
                    "parent_event_id"
                )
            events = event_manager.create_events_list(data)
            events_list += events
        return events_list


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
        event_manager_module = importlib.import_module(
            f"resources.{use_case_db.name}.event_manager"
        )
        event_manager_class = getattr(
            event_manager_module, f"{use_case_db.event_manager_class}"
        )
        event_manager_instance = event_manager_class()

        # register use case to use_case_factory
        use_case_factory.register_use_case(
            use_case_db.name, event_manager_instance
        )

        # Dynamically import the metadata schema class
        metadata_schema_module = importlib.import_module(
            f"resources.{use_case_db.name}.schemas"
        )
        getattr(metadata_schema_module, f"{use_case_db.metadata_schema_class}")

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


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/event/<event_id>", view_func=Event.as_view("event"))
api_bp.add_url_rule("/events", view_func=Events.as_view("events"))
api_bp.add_url_rule(
    "/events-list", view_func=EventsList.as_view("events-list")
)
api_bp.add_url_rule("/usecases", view_func=UseCases.as_view("usecases"))
api_bp.add_url_rule(
    "/usecase/<int:use_case_id>", view_func=UseCase.as_view("usecase")
)
