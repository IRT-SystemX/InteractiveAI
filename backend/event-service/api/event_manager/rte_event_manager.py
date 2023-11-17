import logging
import uuid
from datetime import datetime
from ..clients.cards_publication import CardPubClient
from ..clients.historic import HistoricClient
from ..models import EventModel, db
from .base_event_manager import BaseEventManager


class RTEEventManager(BaseEventManager):
    def __init__(self) -> None:
        super().__init__()
        self.use_case = "RTE"
        self.use_case_process = "rteProcess"

    def get_event_id(self, input_line):
        if input_line:
            events_list = EventModel.query.filter_by(
                use_case=self.use_case).all()

            for event in events_list:
                if event.data.get("line") == input_line:
                    event_id = event.id_event
                    logging.debug(
                        f"Found event: {event_id} containing line: {input_line}")
                    return str(event_id)
        event_id = uuid.uuid4()
        logging.debug(f"Genrating event_id: {event_id}")
        return str(event_id)

    def create_event(self, data):
        input_line = data["data"].get("line")
        event_id = self.get_event_id(input_line)
        data["id_event"] = str(event_id)

        # Create a new card (notification)
        card_pub_client = CardPubClient()
        severity = self.severity_map[data.get("criticality")]
        start_date = data.get("start_date", datetime.now())
        timestamp_start_date = int(round(start_date.timestamp()*1000))
        data["start_date"] = timestamp_start_date

        end_date = data.get("end_date")
        timestamp_end_date = None
        if end_date:
            timestamp_end_date = int(round((end_date).timestamp() * 1000))
            data["end_date"] = timestamp_end_date

        card_payload = {
            "publisher": "publisher_test",
            "processVersion": "1",
            "process": self.use_case_process,
            "processInstanceId": data["id_event"],
            "state": "messageState",
            "entityRecipients": [self.use_case],
            "severity": severity,
            "startDate": timestamp_start_date,
            "endDate": timestamp_end_date,
            "summary": {
                "key": self.use_case_process + ".summary",
                "parameters": {"summary": data["description"]}
            },
            "title": {
                "key": self.use_case_process + ".title",
                "parameters": {"title": data["title"]}
            },
            "data": {
                "metadata": data["data"]
            }
        }

        card_pub_client.create_card(card_payload)
        # Trace in histric service
        self.trace_event(start_date, end_date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event
