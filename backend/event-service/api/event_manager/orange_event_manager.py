import uuid
from datetime import datetime

from settings import logger

from ..models import EventModel
from .base_event_manager import BaseEventManager
import logging

class OrangeEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "ORANGE"
        self.use_case_process = "orangeProcess"
        self.created_cards_list = {}

    def get_event_id(self, id_app):
        if id_app:
            events_list = EventModel.query.filter_by(
                use_case=self.use_case
            ).all()

            for event in events_list:
                if event.data.get("id_app") == id_app:
                    event_id = event.id_event
                    logger.debug(
                        f"Found event: {event_id} containing line: {id_app}"
                    )
                    return str(event_id), False
        event_id = uuid.uuid4()
        logger.debug(f"Genrating event_id: {event_id}")
        return str(event_id), True

    def create_event(self, data):
        id_app = str(data["data"].get("id_app"))
        event_id, _ = self.get_event_id(id_app)

        data["id_event"] = str(event_id)
        start_date = data.get("start_date", datetime.now())
        end_date = data.get("end_date")
        # Create a new card (notification)
        of_response = self.create_card(start_date, end_date, data)
        data["of_uid"] = of_response.get("uid")

        self.created_cards_list[id_app] = {
            "id_event": data["id_event"],
        }

        # Trace in histric service
        self.trace_event(start_date, end_date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event

    def get_id_by_app_name(self, app_name):
        for entry in self.app_names_id:
            if entry["app_name"] == app_name:
                return entry["id"]
        return None

    def create_events_list(self, events_list):
        id_apps_list = {str(event["data"]["id_app"]) for event in events_list}

        created_events_list = []

        # set old event values
        for old_created_event_app_id, value in self.created_cards_list.items():
            if old_created_event_app_id not in id_apps_list:
                event_data = (EventModel.query.filter_by(id_event=value['id_event']).first()).to_dict()
                event_data["criticality"] = "ROUTINE"
                event_data["end_date"] = datetime.now()
                created_event = self.create_event(event_data)
                created_events_list.append(created_event)

        # set new events
        for event_data in events_list:
            created_event = self.create_event(event_data)
            created_events_list.append(created_event)

        return created_events_list
