import uuid
from datetime import datetime

from settings import logger

from ..clients.cards_publication import CardPubClient
from ..clients.historic import HistoricClient
from ..models import EventModel, db


class BaseEventManager:
    def __init__(self) -> None:
        self.severity_map = {
            "HIGH": "ALARM",
            "MEDIUM": "ACTION",
            "LOW": "COMPLIANT",
            "ROUTINE": "INFORMATION",
        }

    def uniqueness_condition(self, event, unique_by_fields):
        """
        Check if the given event satisfies uniqueness conditions.

        :param event: Event data to check
        :type event: dict
        :param unique_by_fields: Dictionary specifying uniqueness conditions
        :type unique_by_fields: dict
        :return: True if conditions are satisfied, False otherwise
        :rtype: bool
        """
        for key, value in unique_by_fields.items():
            if event.get(key) != value:
                return False
        return True

    def get_event_id(self, unique_by_fields=None):
        """_summary_

        :param unique_by_fields: _description_, defaults to None
        :type unique_by_fields: _type_, optional
        :return: _description_
        :rtype: _type_
        """
        if unique_by_fields:
            events_list = EventModel.query.filter_by(
                use_case=self.use_case
            ).all()

            for event in events_list:
                if self.uniqueness_condition(event.data, unique_by_fields):
                    event_id = event.id_event
                    logger.debug(
                        f"Found similar event: {event_id} based on: {unique_by_fields}"
                    )
                    return str(event_id), False

        event_id = uuid.uuid4()
        logger.debug(f"Generating event_id: {event_id}")
        return str(event_id), True

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
        severity = self.severity_map.get(
            data.get("criticality"), "INFORMATION"
        )
        criticality = data.get("criticality")

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
            "data": {
                "metadata": data["data"],
                "criticality": criticality,
                "parent_event_id": data.get("parent_event_id"),
            },
        }

        return card_pub_client.create_card(card_payload)

    def create_event(self, data):
        event_id = self.get_event_id()
        data["id_event"] = str(event_id)

        # Set parent_event_id if provided
        data["parent_event_id"] = data.get("parent_event_id")

        start_date = data.get("start_date", datetime.now())
        end_date = data.get("end_date")
        # Create a new card (notification)
        of_response = self.create_card(start_date, end_date, data)
        data["of_uid"] = of_response.get("uid")
        # Trace in historic service
        self.trace_event(start_date, end_date, data)

        # Save event to database
        event = self.save_event_db(data)
        return event

    def create_events_list(self, events_list):
        created_events_list = []
        for event_data in events_list:
            if event_data["use_case"] == self.use_case:
                # Set parent_event_id if provided
                event_data["parent_event_id"] = event_data.get(
                    "parent_event_id"
                )
                created_event = self.create_event(event_data)
                created_events_list.append(created_event)
        return created_events_list
