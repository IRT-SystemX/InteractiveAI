import uuid
from datetime import datetime

from apiflask import APIBlueprint
from flask.views import MethodView

from .clients.cards_publication import CardPubClient
from .clients.historic import HistoricClient
from .clients.keycloak import KeycloakClient
from .models import EventModel, db
from .schemas import EventIn, EventOut

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
    def get(self):
        """Get all events"""
        return EventModel.query.all()

    @api_bp.input(EventIn)
    @api_bp.output(EventOut, status_code=201)
    def post(self, data):
        """Add an event"""
        event_id = uuid.uuid4()
        data["id_event"] = str(event_id)
        # TODO: this authenetication should be removed once this service is integrated into the same gateway as operatorFabric
        keycloak_client = KeycloakClient()
        login_response = keycloak_client.login()

        card_pub_client = CardPubClient()
        severity = severity_map[data.get("criticality")]
        date = data.get("date", datetime.now())
        timestamp_date = int(round((date).timestamp()*1000))
        data["date"] = timestamp_date

        card_pub_client.create_card(login_response.get("access_token"),
                                    data["id_event"],
                                    severity,
                                    timestamp_date,
                                    data["title"],
                                    data["description"],
                                    data["data"])
        historic_client = HistoricClient()
        data["date"] = date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        historic_client.create_trace(data)
        data["date"] = date

        # Save event to database
        event = EventModel(**data)
        db.session.add(event)
        db.session.commit()
        return event


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/events", view_func=Events.as_view("events"))
