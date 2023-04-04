from ..models import EventModel
import uuid
import logging
from .base_event_manager import BaseEventManager


class SNCFEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "RTE"
        self.use_case_process = "sncfProcess"
        

    def get_event_id(self):
        event_id = uuid.uuid4()
        logging.debug(f"Genrating event_id: {event_id}")
        return str(event_id)
