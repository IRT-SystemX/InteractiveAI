# backend/event-service/resources/Railway/event_manager.py

from api.event_manager.base_event_manager import BaseEventManager

class RailwayEventManager(BaseEventManager):
    def __init__(self):
        super().__init__()
        self.use_case = "Railway"
        self.use_case_process = "cabProcess"
    
    # Optional: Customize Event Uniqueness
    def get_unique_fields(self, data):
        id_train = data["data"].get("id_train")
        event_type = data["data"].get("event_type")
        return {"id_train": id_train, "event_type": event_type}
