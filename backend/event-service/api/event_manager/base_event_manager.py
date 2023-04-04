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
            "ROUTINE": "INFORMATION"
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

    def trace_event(self, date, data):
        historic_client = HistoricClient()
        data["date"] = date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        historic_client.create_trace(data)
        data["date"] = date

    def create_card(self, date, data):
        card_pub_client = CardPubClient()
        severity = self.severity_map[data.get("criticality")]

        timestamp_date = int(round((date).timestamp()*1000))
        data["date"] = timestamp_date

        card_payload = {
            "publisher": "publisher_test",
            "processVersion": "1",
            "process": self.use_case_process,
            "processInstanceId": data["id_event"],
            "state": "messageState",
            "entityRecipients": [self.use_case],
            "severity": severity,
            "startDate": timestamp_date,
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

    def create_event(self, data):
        event_id = self.get_event_id()
        data["id_event"] = str(event_id)
        date = data.get("date", datetime.now())
        # Create a new card (notification)
        self.create_card(date, data)
        # Trace in histric service
        self.trace_event(date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event
