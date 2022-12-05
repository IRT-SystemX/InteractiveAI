from .models import EventModel
import uuid
import logging


def get_event_id(input_line, use_case):
    if input_line:
        events_list = EventModel.query.filter_by(use_case=use_case).all()

        for event in events_list:
            if event.data["line"] == input_line:
                event_id = event.id_event
                logging.debug(f"Found event: {event_id} containing line: {input_line}")
                return str(event_id)
    event_id = uuid.uuid4()
    logging.debug(f"Genrating event_id: {event_id}")
    return str(event_id)
