from datetime import datetime

import pytest
from api.models import ContextModel, db
from app import create_app


@pytest.fixture(scope="function")
def app():
    app = create_app("test")
    with app.app_context():
        # Create the database tables
        db.create_all()

        yield app

        use_case_factory = app.use_case_factory
        orange_factory = use_case_factory.get_context_manager("ORANGE")
        orange_factory.correaltion_manager.correlation_request_process.terminate()

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
def orange_auth_mocker(client, mocker):
    # Mock the keycloak.introspect method to return a valid response
    mocker.patch('cab_common_auth.decorators.keycloak.introspect',
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
                     "sid": "5297805d-fc73-4d94-97fc-0c5a52c41440",
                     "groups": "RTE;ADMIN;ReadOnly",
                     "entitiesId": "ORANGE",
                     "client_id": "opfab-client",
                     "username": "orange_user",
                     "active": True
                 })


@pytest.fixture(scope='function')
def create_contexts(client, rte_auth_mocker):
    with client.application.app_context():
        db.create_all()
        context1 = ContextModel(
            id_context='123',
            use_case='RTE',
            date=datetime.now(),
            data={"observation": {"rho": 11}}
        )
        context2 = ContextModel(
            id_context='456',
            use_case='DA',
            date=datetime.now(),
            data={}
        )
        db.session.add(context1)
        db.session.add(context2)
        db.session.commit()
