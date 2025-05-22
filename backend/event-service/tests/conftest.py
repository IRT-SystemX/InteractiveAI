from datetime import datetime

import pytest

from api.models import EventModel, UseCaseModel, db
from api.utils import load_usecases_db
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
def PowerGrid_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch(
        "cab_common_auth.decorators.keycloak.introspect",
        return_value={
            "exp": 1684333261,
            "iat": 1683728461,
            "jti": "716b02d4-29ba-41bd-85b2-8004cec1a033",
            "iss": "http://192.168.211.95:3200/realms/dev",
            "aud": "account",
            "sub": "PowerGrid_user",
            "typ": "Bearer",
            "azp": "opfab-client",
            "session_state": "8976b125-39a8-4bdf-b523-7e0dcbcdd3b4",
            "given_name": "",
            "family_name": "",
            "preferred_username": "PowerGrid_user",
            "email_verified": False,
            "acr": "1",
            "realm_access": {"roles": ["offline_access", "uma_authorization"]},
            "resource_access": {
                "account": {
                    "roles": [
                        "manage-account",
                        "manage-account-links",
                        "view-profile",
                    ]
                }
            },
            "scope": "email profile",
            "sid": "8976b125-39a8-4bdf-b523-7e0dcbcdd3b4",
            "groups": "Dispatcher;ReadOnly;Supervisor",
            "entitiesId": "PowerGrid",
            "client_id": "opfab-client",
            "username": "PowerGrid_user",
            "active": True,
        },
    )


@pytest.fixture
def mock_of_create_cards_request(requests_mock):
    mock_response_cards = {"id": "string", "uid": "string"}
    requests_mock.post("http://op/cards", json=mock_response_cards)
    mock_response_historic = {}
    requests_mock.post("http://historic/api/v1/traces", json=mock_response_historic)


@pytest.fixture(scope="function")
def create_usecases(client):
    with client.application.app_context():
        from flask import current_app

        db.create_all()

        PowerGrid_use_case = UseCaseModel(
            name="PowerGrid",
            event_manager_class="PowerGridEventManager",
            metadata_schema_class="MetadataSchemaPowerGrid",
        )

        db.session.add(PowerGrid_use_case)
        db.session.commit()
        # add use_case_factory
        use_case_factory = current_app.use_case_factory

        # Load use cases from the database
        load_usecases_db(use_case_factory)


@pytest.fixture(scope="function")
def create_events(client, create_usecases, PowerGrid_auth_mocker):
    with client.application.app_context():
        db.create_all()
        event1 = EventModel(
            id_event="123",
            use_case="PowerGrid",
            title="Test Event 1",
            description="This is a test event",
            start_date=datetime.now(),
            criticality="HIGH",
            data={"event_type": "KPI"},
        )
        event2 = EventModel(
            id_event="456",
            use_case="ATM",
            title="Test Event 2",
            description="This is another test event",
            start_date=datetime.now(),
            criticality="LOW",
            data={"category": "test"},
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()
