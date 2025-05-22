# backend/event-service/resources/ATM/event_manager.py

from api.event_manager.base_event_manager import BaseEventManager

class ATMEventManager(BaseEventManager):
    def __init__(self):
        super().__init__()
        self.use_case = "ATM"
        self.use_case_process = "cabProcess"
    
    # Optional: Customize Event Uniqueness
    def get_unique_fields(self, data):
        """
        Override to specify unique fields for event uniqueness.
        
        This method specifies the fields on which InteractiveAI will ensure event uniqueness.
        """
        id_plane = data["data"].get("id_plane")
        event_type = data["data"].get("event_type")
        return {"id_plane": id_plane, "event_type": event_type}