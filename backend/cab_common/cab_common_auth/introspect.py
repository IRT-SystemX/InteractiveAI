from keycloak.exceptions import (KeycloakPostError, KeycloakRPTNotFound,
                                 raise_error_from_response)
from keycloak.keycloak_openid import KeycloakOpenID

from .settings import URL_INTROSPECT


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
            payload.update({"token": rpt, "token_type_hint": token_type_hint})
            self.connection.add_param_headers(
                "Authorization", "Bearer " + token)
        else:
            raise KeycloakRPTNotFound("Can't found RPT.")

    payload = self._add_secret_key(payload)

    data_raw = self.connection.raw_post(
        URL_INTROSPECT.format(**params_path), data=payload)
    return raise_error_from_response(data_raw, KeycloakPostError)


KeycloakOpenID.introspect = introspect
