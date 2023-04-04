import uuid
from .base_event_manager import BaseEventManager
from datetime import datetime
from ..models import EventModel
from settings import logger

class SNCFEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "SNCF"
        self.use_case_process = "sncfProcess"

    def get_event_id(self, data):
        id_train = data["data"].get("id_train")
        event_type = data["data"].get("event_type")
        if id_train and event_type:
            events_list = EventModel.query.filter_by(
                use_case=self.use_case).all()
            logger.info(events_list)
            logger.info(id_train)
            logger.info(event_type)

            for event in events_list:
                logger.info(event.data.get("id_train") == id_train and event.data.get("event_type") == event_type)
                if event.data.get("id_train") == id_train and event.data.get("event_type") == event_type:
                    event_id = event.id_event
                    logger.debug(f"Found event: {event_id} for: {id_train}")
                    return str(event_id)
        event_id = uuid.uuid4()
        logger.debug(f"Genrating event_id: {event_id}")
        return str(event_id)

    def create_event(self, data):
        event_id = self.get_event_id(data)
        data["id_event"] = str(event_id)
        logger.info(event_id)
        date = data.get("date", datetime.now())
        # Create a new card (notification)
        self.create_card(date, data)
        # Trace in histric service
        self.trace_event(date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event
