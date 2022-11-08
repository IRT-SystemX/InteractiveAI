import logging
from datetime import datetime
from apiflask import APIBlueprint, abort
from flask.views import MethodView

from .schemas import EventIn, EventOut
from .clients.keycloak import KeycloakClient
from .clients.cards_publication import CardPubClient
api_bp = APIBlueprint("event-api", __name__, url_prefix="/api/v1")

events = []

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


class Event(MethodView):

    @api_bp.output(EventOut)
    def get(self, event_id):
        """Get a event"""
        if event_id > len(events) - 1:
            abort(404)
        return events[event_id]

    @api_bp.input(EventIn(partial=True))
    @api_bp.output(EventOut)
    def patch(self, event_id, data):
        """Update a event"""
        if event_id > len(events) - 1:
            abort(404)
        for attr, value in data.items():
            events[event_id][attr] = value
        return events[event_id]


class Events(MethodView):

    @api_bp.output(EventOut(many=True))
    def get(self):
        """Get all events"""
        print(events)
        return events

    @api_bp.input(EventIn)
    @api_bp.output(EventOut, status_code=201)
    def post(self, data):
        """Add an event"""
        logging.info(data)
        event_id = len(events)
        data["id_event"] = str(event_id)
        # TODO: this authenetication should be removed once this service is integrated into the same gateway as operatorFabric
        keycloak_client = KeycloakClient()
        login_response = keycloak_client.login()

        card_pub_client = CardPubClient()
        severity = severity_map[data.get("criticality")]
        date = data.get("date", datetime.now())
        timestamp_date = int(round((date).timestamp()*1000))

        card_pub_client.create_card(
            login_response.get("access_token"), data["id_event"], severity, timestamp_date, data["description"])

        events.append(data)
        return events[-1]


api_bp.add_url_rule("/health", view_func=HealthCheck.as_view("health"))
api_bp.add_url_rule("/events/<int:event_id>", view_func=Event.as_view("event"))
api_bp.add_url_rule("/events", view_func=Events.as_view("events"))
