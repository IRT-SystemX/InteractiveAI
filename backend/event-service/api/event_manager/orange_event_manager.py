import uuid
from datetime import datetime

from settings import logger

from ..models import EventModel
from .base_event_manager import BaseEventManager


class OrangeEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "ORANGE"
        self.use_case_process = "orangeProcess"

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
                    return str(event_id)
        event_id = uuid.uuid4()
        logger.debug(f"Genrating event_id: {event_id}")
        return str(event_id)

    def create_event(self, data):
        id_app = data["data"].get("id_app")
        event_id = self.get_event_id(id_app)
        data["id_event"] = str(event_id)
        start_date = data.get("start_date", datetime.now())
        end_date = data.get("end_date")
        # Create a new card (notification)
        self.create_card(start_date, end_date, data)
        # Trace in histric service
        self.trace_event(start_date, end_date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event
