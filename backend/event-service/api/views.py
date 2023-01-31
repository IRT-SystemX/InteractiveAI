from datetime import datetime

from apiflask import APIBlueprint
from cab_common_auth.decorators import get_use_cases, protected
from flask.views import MethodView

from .clients.cards_publication import CardPubClient
from .clients.historic import HistoricClient
from .models import EventModel, db
from .schemas import EventIn, EventOut
from .utils import get_event_id

api_bp = APIBlueprint("event-api", __name__, url_prefix="/api/v1")


severity_map = {
    "ND": "ND",
    "HIGH": "ALARM",
    "MEDIUM": "ACTION",
    "LOW": "COMPLIANT",
    "ROUTINE": "INFORMATION"
}


class HealthCheck(MethodView):

    def get(self):
        return


class Events(MethodView):

    @api_bp.output(EventOut(many=True))
    @protected
    def get(self):
        """Get all events"""
        use_cases = get_use_cases()
        return EventModel.query.filter(EventModel.use_case.in_(use_cases))

    @api_bp.input(EventIn)
    @api_bp.output(EventOut, status_code=201)
    @protected
    def post(self, data):
        """Add an event"""
        use_case = data["use_case"]
        input_line = data["data"].get("line")
        event_id = get_event_id(input_line, use_case)
        data["id_event"] = str(event_id)

        # Create a new card (notification)
        card_pub_client = CardPubClient()
        severity = severity_map[data.get("criticality")]
        date = data.get("date", datetime.now())
        timestamp_date = int(round((date).timestamp()*1000))
        data["date"] = timestamp_date

        use_case_process = {
            "RTE": "rteProcess",
            "SNCF": "sncfProcess",
            "DA/FW": "daProcess",
            "ORANGE": "orangeProcess"
        }

        card_payload = {
            "publisher": "publisher_test",
            "processVersion": "1",
            "process": use_case_process[use_case],
            "processInstanceId": data["id_event"],
            "state": "messageState",
            # "groupRecipients": [
            #     "Dispatcher"
            # ],
            "entityRecipients": [use_case],
            "severity": severity,
            "startDate": timestamp_date,
            "summary": {
                "key": use_case_process[use_case] + ".summary",
                "parameters": {"summary": data["description"]}
            },
            "title": {
                "key": use_case_process[use_case] + ".title",
                "parameters": {"title": data["title"]}
            },
            "data": {
                "metadata": data["data"]
            }
        }

        card_pub_client.create_card(card_payload)
        # Trace in histric service
        historic_client = HistoricClient()
        data["date"] = date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        historic_client.create_trace(data)
        data["date"] = date

        # Save event to database
        event = EventModel(**data)
        db.session.merge(event)
        db.session.commit()
        return event


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/events", view_func=Events.as_view("events"))
