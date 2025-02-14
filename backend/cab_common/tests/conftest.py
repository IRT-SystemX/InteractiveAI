import pytest
from flask import Flask

from ..cab_common_auth.custom_keycloak_openid import CustomKeycloakOpenID

VALID_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJSbXFOVTNLN0x4ck5SRmtIVTJxcTZZcTEya1RDaXNtRkw5U2NwbkNPeDBjIn0.eyJleHAiOjE2ODYyMjU5NjYsImlhdCI6MTY4NTYyMTE2NiwianRpIjoiYTQ3OTMyYmYtOTUxZC00YWU4LWJkZGUtNTdmMTc5MDQyYTYwIiwiaXNzIjoiaHR0cDovLzE3Mi4xNy4wLjE6MzIwMC9hdXRoL3JlYWxtcy9kZXYiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoic25jZl91c2VyIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoib3BmYWItY2xpZW50Iiwic2Vzc2lvbl9zdGF0ZSI6IjJjZGVlYWE0LTNkOWUtNGZkMS05NjA0LTFkYjY1MDdkNjE2OCIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoiZW1haWwgcHJvZmlsZSIsInNpZCI6IjJjZGVlYWE0LTNkOWUtNGZkMS05NjA0LTFkYjY1MDdkNjE2OCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoic25jZl91c2VyIiwiZW50aXRpZXNJZCI6IlNOQ0YifQ.M0wTHfv3aI29i8LVSt6B3IEfwR9KVqHxatuUxI1EW2DJTcXdnm7hnvNRJN4yETwYmt8qbIpI3hdcQ5C39RGjbaMBsfSwO9SWonzP-E3hV-o-Jww1ZmoCy-kel9ODWaktvMnGY3SpS2hzs-XH2MOx0If2EC9e37heFyg0gTig0SU5DJikvoLQHE02OvztfqYKKYiMPJjzMgnYrMjF7H6J8Kb_w2UAgtVVZyqnlWeuLn2KMjlU9u_iK1BcWfRxj6jH2my3Usd78NBwqfSTKVI-ZTGjp0oVgm7HHyTDwOmOF95EI9Y6s28NIfIHLc53c-cu6AA9G_6CA-ZtqWbpf6L9AQ"


@pytest.fixture(scope="module")
def mock_keycloak_openid():
    return CustomKeycloakOpenID(
        server_url="http://example.com",
        client_id="client_id",
        realm_name="realm",
        client_secret_key="client_secret",
    )


@pytest.fixture(scope="function")
def mock_keycloak_introspect(mocker):
    # Mock the introspect method of CustomKeycloakOpenID for testing
    def mock_introspect(token):
        # Simulate the behavior of introspect method for testing purposes
        if token == VALID_TOKEN:
            valid_introspect = {
                "exp": 1686238116,
                "iat": 1685633316,
                "jti": "91ee1b13-35c7-4509-a306-033a74abb9d4",
                "iss": "http://192.168.208.57:3200/auth/realms/dev",
                "aud": "account",
                "sub": "railway_user",
                "typ": "Bearer",
                "azp": "opfab-client",
                "session_state": "420008f7-52de-4174-a7fa-36afcc5ec78e",
                "preferred_username": "railway_user",
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
                "sid": "420008f7-52de-4174-a7fa-36afcc5ec78e",
                "entitiesId": "Railway",
                "client_id": "opfab-client",
                "username": "railway_user",
                "active": True,
            }
            return valid_introspect

        return {"active": False}

    mocker.patch.object(CustomKeycloakOpenID, "introspect", side_effect=mock_introspect)


@pytest.fixture(scope="function")
def mock_keycloak_introspect_error(mocker):
    # Mock the introspect method of CustomKeycloakOpenID to raise an error for testing
    def mock_introspect(token):
        raise Exception("Error occurred during introspection")

    mocker.patch.object(CustomKeycloakOpenID, "introspect", side_effect=mock_introspect)


@pytest.fixture(scope="function")
def valid_token():
    return VALID_TOKEN


@pytest.fixture(scope="function")
def app():
    return Flask(__name__)
