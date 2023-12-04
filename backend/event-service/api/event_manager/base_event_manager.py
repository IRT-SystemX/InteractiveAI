import uuid

from settings import logger
from datetime import datetime
from ..clients.cards_publication import CardPubClient
from ..clients.historic import HistoricClient
from ..models import EventModel, db


class BaseEventManager:
    def __init__(self) -> None:
        self.severity_map = {
            "ND": "ND",
            "HIGH": "ALARM",
            "MEDIUM": "ACTION",
            "LOW": "COMPLIANT",
            "ROUTINE": "INFORMATION",
        }

    def get_event_id(self):
        event_id = uuid.uuid4()
        logger.debug(f"Genrating event_id: {event_id}")
        return str(event_id)

    def save_event_db(self, data):
        logger.info(data)
        event = EventModel(**data)
        db.session.merge(event)
        db.session.commit()
        return data

    def trace_event(self, start_date, end_date, data):
        historic_client = HistoricClient()
        data["start_date"] = start_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        if end_date:
            data["end_date"] = end_date.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        historic_client.create_trace(data)
        data["start_date"] = start_date
        data["end_date"] = end_date

    def create_card(self, start_date, end_date, data):
        card_pub_client = CardPubClient()
        severity = self.severity_map[data.get("criticality")]

        timestamp_start_date = int(round(start_date.timestamp() * 1000))
        data["start_date"] = timestamp_start_date

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
                "parameters": {"summary": data["description"]},
            },
            "title": {
                "key": self.use_case_process + ".title",
                "parameters": {"title": data["title"]},
            },
            "data": {"metadata": data["data"]},
        }

        return card_pub_client.create_card(card_payload)

    def create_event(self, data):
        event_id = self.get_event_id()
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

    def create_events_list(self, events_list):
        created_events_list = []
        for event_data in events_list:
            if event_data["use_case"] == self.use_case:
                created_event = self.create_event(event_data)
                created_events_list.append(created_event)
        return created_events_list
