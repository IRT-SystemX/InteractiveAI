
from functools import wraps

from flask import abort, request
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakError

from .settings import KEYCLOAK_SERVER_URL

keycloak = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                          client_id='opfab-client',
                          realm_name="dev",
                          client_secret_key="opfab-keycloak-secret")


def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            abort(401, 'Token is missing')

        _, token = token.split(" ", 1)
        try:
            intorspection = keycloak.introspect(token=token)

            if not intorspection.get("active", False):
                raise KeycloakError("Invalid Token")

        except KeycloakError as e:
            abort(401, str(e))
        return f(*args, **kwargs)
    return decorated
