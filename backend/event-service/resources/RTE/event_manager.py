import uuid
from datetime import datetime

from settings import logger

from api.models import EventModel
from api.event_manager.base_event_manager import BaseEventManager


class RTEEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "RTE"
        self.use_case_process = "rteProcess"

    def get_event_id(self, input_line):
        if input_line:
            events_list = EventModel.query.filter_by(
                use_case=self.use_case
            ).all()

            for event in events_list:
                if event.data.get("line") == input_line:
                    event_id = event.id_event
                    logger.debug(
                        f"Found event: {event_id} containing line: {input_line}"
                    )
                    return str(event_id)
        event_id = uuid.uuid4()
        logger.debug(f"Genrating event_id: {event_id}")
        return str(event_id)

    def create_event(self, data):
        input_line = data["data"].get("line")
        event_id = self.get_event_id(input_line)
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
