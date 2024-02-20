from datetime import datetime

from api.event_manager.base_event_manager import BaseEventManager


class RTEEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "RTE"
        self.use_case_process = "cabProcess"

    def create_event(self, data):
        input_line = data["data"].get("line")
        event_id, _ = self.get_event_id(unique_by_fields={"line": input_line})
        data["id_event"] = str(event_id)
        start_date = data.get("start_date", datetime.now())
        end_date = data.get("end_date")
        # Create a new card (notification)
        of_response = self.create_card(start_date, end_date, data)
        data["of_uid"] = of_response.get("uid")
        # Trace in histric service
        self.trace_event(start_date, end_date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event
