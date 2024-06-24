import pytest
from api.models import UseCaseModel, db
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
def rte_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch(
        "cab_common_auth.decorators.keycloak.introspect",
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
            "entitiesId": "RTE",
            "client_id": "opfab-client",
            "username": "rte_user",
            "active": True,
        },
    )


@pytest.fixture
def da_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch(
        "cab_common_auth.decorators.keycloak.introspect",
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
            "sid": "bd3b8610-1d05-4bdd-916b-61dcfe6d5e72",
            "groups": "RTE;ADMIN;ReadOnly",
            "entitiesId": "DA",
            "client_id": "opfab-client",
            "username": "da_user",
            "active": True,
        },
    )


@pytest.fixture
def sncf_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch(
        "cab_common_auth.decorators.keycloak.introspect",
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
            "sid": "0dee604d-5c03-416c-8d95-59b0aa95b61a",
            "entitiesId": "SNCF",
            "client_id": "opfab-client",
            "username": "sncf_user",
            "active": True,
        },
    )


@pytest.fixture
def orange_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch(
        "cab_common_auth.decorators.keycloak.introspect",
        return_value={
            "exp": 1684766859,
            "iat": 1684162059,
            "jti": "418dee2b-aac6-452e-a90f-32278e34a22b",
            "iss": "http://192.168.211.95:3200/realms/dev",
            "aud": "account",
            "sub": "orange_user",
            "typ": "Bearer",
            "azp": "opfab-client",
            "session_state": "5297805d-fc73-4d94-97fc-0c5a52c41440",
            "preferred_username": "orange_user",
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
            "sid": "5297805d-fc73-4d94-97fc-0c5a52c41440",
            "groups": "RTE;ADMIN;ReadOnly",
            "entitiesId": "ORANGE",
            "client_id": "opfab-client",
            "username": "orange_user",
            "active": True,
        },
    )


@pytest.fixture(scope="function")
def create_usecases(client):
    with client.application.app_context():
        from flask import current_app

        db.create_all()

        da_use_case = UseCaseModel(name="DA", manager_class="DAManager")
        rte_use_case = UseCaseModel(name="RTE", manager_class="RTEManager")
        sncf_use_case = UseCaseModel(name="SNCF", manager_class="SNCFManager")

        db.session.add(da_use_case)
        db.session.add(rte_use_case)
        db.session.add(sncf_use_case)
        db.session.commit()
        # add use_case_factory
        use_case_factory = current_app.use_case_factory

        # Load use cases from the database
        load_usecases_db(use_case_factory)
