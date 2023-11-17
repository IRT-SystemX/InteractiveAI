from datetime import datetime


import pytest
from api.models import EventModel, db
from app import create_app


@pytest.fixture(scope="function")
def app():
    app = create_app("test")
    with app.app_context():
        # Create the database tables
        db.create_all()

        yield app

        # Clean up the database after the test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture
def rte_auth_mocker(client, mocker):
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
def da_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch('cab_common_auth.decorators.keycloak.introspect',
                 return_value={
                     "exp": 1684401219,
                     "iat": 1683796419,
                     "jti": "a28734f6-f5c8-4130-8fb7-573d75c39d8c",
                     "iss": "http://192.168.211.95:3200/realms/dev",
                     "aud": "account",
                     "sub": "da_user",
                     "typ": "Bearer",
                     "azp": "opfab-client",
                     "session_state": "bd3b8610-1d05-4bdd-916b-61dcfe6d5e72",
                     "preferred_username": "da_user",
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
                     "sid": "bd3b8610-1d05-4bdd-916b-61dcfe6d5e72",
                     "groups": "RTE;ADMIN;ReadOnly",
                     "entitiesId": "DA",
                     "client_id": "opfab-client",
                     "username": "da_user",
                     "active": True
                 })


@pytest.fixture
def sncf_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch('cab_common_auth.decorators.keycloak.introspect',
                 return_value={
                     "exp": 1684413915,
                     "iat": 1683809115,
                     "jti": "6f63636a-625a-4926-9684-6d5ed3b80e2a",
                     "iss": "http://192.168.211.95:3200/realms/dev",
                     "aud": "account",
                     "sub": "sncf_user",
                     "typ": "Bearer",
                     "azp": "opfab-client",
                     "session_state": "0dee604d-5c03-416c-8d95-59b0aa95b61a",
                     "preferred_username": "sncf_user",
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
                     "sid": "0dee604d-5c03-416c-8d95-59b0aa95b61a",
                     "entitiesId": "SNCF",
                     "client_id": "opfab-client",
                     "username": "sncf_user",
                     "active": True
                 })


@pytest.fixture
def mock_of_create_cards_request(requests_mock):
    mock_response_cards = {"id": "string", "uid": "string"}
    requests_mock.post('http://op/cards', json=mock_response_cards)
    mock_response_historic = {}
    requests_mock.post('http://historic/api/v1/traces',
                       json=mock_response_historic)


@pytest.fixture(scope='function')
def create_events(client, rte_auth_mocker):
    with client.application.app_context():
        db.create_all()
        event1 = EventModel(
            id_event='123',
            use_case='RTE',
            title='Test Event 1',
            description='This is a test event',
            start_date=datetime.now(),
            criticality='HIGH',
            data={'event_type': 'KPI'}
        )
        event2 = EventModel(
            id_event='456',
            use_case='DA',
            title='Test Event 2',
            description='This is another test event',
            start_date=datetime.now(),
            criticality='LOW',
            data={'category': 'test'}
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()
