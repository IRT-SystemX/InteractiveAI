"""
This module contains Flask routes and decorators for protecting routes with authorization tokens.

It utilizes the KeycloakOpenID library for token introspection and validation.
The protected decorator can be used to wrap Flask routes and ensure that a valid authorization
token is present in the request headers before allowing access to the route.

The get_use_cases function retrieves the entities ID associated with the user from the authorization token.

Note: This code assumes the presence of a Keycloak server and the appropriate configuration in the settings module.
"""

from functools import wraps

from flask import abort, request
from .custom_keycloak_openid import CustomKeycloakOpenID
from keycloak.exceptions import KeycloakError

from .settings import KEYCLOAK_SERVER_URL

keycloak = CustomKeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id="opfab-client",
    realm_name="dev",
    client_secret_key="opfab-keycloak-secret",
)


def protected(f):
    """
    Decorator that protects a Flask route by validating the authorization token

    :param f: The function to be decorated.
    :type f: function
    :returns: The decorated function.
    :rtype: function
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        """
        Wrapper function that validates the authorization token.

        :param args: Positional arguments passed to the wrapped function.
        :type args: tuple
        :param kwargs: Keyword arguments passed to the wrapped function.
        :type kwargs: dict
        :returns: The result of the wrapped function.
        :rtype: any
        :raises werkzeug.exceptions.HTTPException: If the token is missing or invalid.
        """
        token = request.headers.get("Authorization")
        if not token:
            abort(401, "Token is missing")

        try:
            _, token = token.split(" ", 1)
            introspection = keycloak.introspect(token=token)

            if not introspection.get("active", False):
                raise KeycloakError("Invalid Token")

        except (KeycloakError, ValueError) as e:
            abort(401, str(e))

        return f(*args, **kwargs)

    return decorated


def get_use_cases():
    """
    Get the entities ID (corresponds to use cases) associated with the user from the authorization token.

    :returns: A list of entities ID associated with the user.
    :rtype: list
    :raises werkzeug.exceptions.HTTPException: If the user doesn't have any valid entity.
    """
    token = request.headers.get("Authorization")
    if not token:
        abort(401, "Token is missing")

    try:
        _, token = token.split(" ", 1)
        introspection = keycloak.introspect(token=token)

        if not introspection.get("active"):
            abort(401, "Invalid token")

        entities_id = introspection.get("entitiesId", "")

        if not entities_id:
            abort(403, "Unauthorized: User doesn't have any valid entity")

        return entities_id.split(";")

    except (KeycloakError, ValueError) as e:
        abort(401, str(e))
