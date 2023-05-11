from datetime import datetime
import pytest

from api.models import db, EventModel
from app import create_app
import config
import requests_mock


@pytest.fixture(scope="module")
def app():
    app = create_app(config.TestConfig)

    with app.app_context():
        yield app


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture
def auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch('cab_common_auth.decorators.keycloak.introspect',
                 return_value={
                     "exp": 1684333261,
                     "iat": 1683728461,
                     "jti": "716b02d4-29ba-41bd-85b2-8004cec1a033",
                     "iss": "http://192.168.211.95:3200/realms/dev",
                     "aud": "account",
                     "sub": "rte_user",
                     "typ": "Bearer",
                     "azp": "opfab-client",
                     "session_state": "8976b125-39a8-4bdf-b523-7e0dcbcdd3b4",
                     "given_name": "",
                     "family_name": "",
                     "preferred_username": "rte_user",
                     "email_verified": False,
                     "acr": "1",
                     "realm_access": {
                         "roles": [
                             "offline_access",
                             "uma_authorization"
                         ]
                     },
                     "resource_access": {
                         "account": {
                             "roles": [
                                 "manage-account",
                                 "manage-account-links",
                                 "view-profile"
                             ]
                         }
                     },
                     "scope": "email profile",
                     "sid": "8976b125-39a8-4bdf-b523-7e0dcbcdd3b4",
                     "groups": "Dispatcher;ReadOnly;Supervisor",
                     "entitiesId": "RTE",
                     "client_id": "opfab-client",
                     "username": "rte_user",
                     "active": True
                 })


@pytest.fixture
def mock_operator_fabric_cards_api_request(requests_mock):

    mock_response_cards = {
        "id": "string",
        "uid": "string"
    }
    requests_mock.post('http://op/cards', json=mock_response_cards)

    mock_response_historic = {}
    requests_mock.post('http://historic/api/v1/traces',
                       json=mock_response_historic)


@ pytest.fixture
def create_events(client, auth_mocker):
    db.create_all()
    event1 = EventModel(id_event='123', use_case='RTE', title='Test Event 1',
                        description='This is a test event', date=datetime.now(), criticality='HIGH',
                        data={'event_type': 'KPI'})
    event2 = EventModel(id_event='456', use_case='DA', title='Test Event 2',
                        description='This is another test event', date=datetime.now(), criticality='LOW',
                        data={'category': 'test'})
    db.session.add(event1)
    db.session.add(event2)
    db.session.commit()
