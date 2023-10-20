"""
Custom Keycloak OpenID

This module extends the functionality of the Python-Keycloak library by providing a custom KeycloakOpenID subclass,
which allows customization of the URL used for token introspection.

Example Usage:
    from .settings import URL_INTROSPECT

    # Import the CustomKeycloakOpenID class
    from custom_keycloak_openid import CustomKeycloakOpenID

    # Create an instance of CustomKeycloakOpenID
    keycloak = CustomKeycloakOpenID()

    # Customize the URL_INTROSPECT
    keycloak.URL_INTROSPECT = URL_INTROSPECT

    # Introspect a user token using the custom URL_INTROSPECT
    token_info = keycloak.introspect(token, rpt, token_type_hint)

    # Handle exceptions
    try:
        # Perform token introspection
        token_info = keycloak.introspect(token, rpt, token_type_hint)
        print(token_info)
    except KeycloakRPTNotFound as e:
        print("Error: RPT not found.")
    except KeycloakPostError as e:
        print("Error: Unable to perform POST request to the introspection endpoint.")
    except Exception as e:
        print("Error:", str(e))

"""

from keycloak.exceptions import (
    KeycloakPostError,
    KeycloakRPTNotFound,
    raise_error_from_response,
)
from keycloak.keycloak_openid import KeycloakOpenID

from .settings import URL_INTROSPECT


class CustomKeycloakOpenID(KeycloakOpenID):
    def introspect(self, token, rpt=None, token_type_hint=None):
        """Introspect the user token.

        The introspection endpoint is used to retrieve the active state of a token.
        It is can only be invoked by confidential clients.

        https://tools.ietf.org/html/rfc7662

        :param token: Access token
        :type token: str
        :param rpt: Requesting party token
        :type rpt: str
        :param token_type_hint: Token type hint
        :type token_type_hint: str

        :returns: Token info
        :rtype: dict
        :raises KeycloakRPTNotFound: In case of RPT not specified
        """
        params_path = {"realm-name": self.realm_name}
        payload = {"client_id": self.client_id, "token": token}

        if token_type_hint == "requesting_party_token":
            if rpt:
                payload |= {"token": rpt, "token_type_hint": token_type_hint}
                self.connection.add_param_headers("Authorization", f"Bearer {token}")
            else:
                raise KeycloakRPTNotFound("Can't found RPT.")

        payload = self._add_secret_key(payload)

        data_raw = self.connection.raw_post(
            URL_INTROSPECT.format(**params_path), data=payload
        )
        return raise_error_from_response(data_raw, KeycloakPostError)
