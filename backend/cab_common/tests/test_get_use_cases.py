import pytest
from ..cab_common_auth.decorators import get_use_cases
from werkzeug.exceptions import HTTPException


def test_get_use_cases_valid_token(app, mock_keycloak_introspect, valid_token):
    # Create a test client using the Flask app
    app.test_client()

    # Set the request headers
    headers = {"Authorization": f"Bearer {valid_token}"}
    with app.test_request_context(headers=headers):
        # Call the get_use_cases function
        use_cases = get_use_cases()

    # Assert the expected result
    assert use_cases == ["SNCF"]


def test_get_use_cases_invalid_token(app, mock_keycloak_introspect):
    # Create a test client using the Flask app
    app.test_client()

    # Set the request headers
    headers = {"Authorization": "Bearer invalid_token"}
    with pytest.raises(HTTPException) as exception_info:
        with app.test_request_context(headers=headers):
            # Call the get_use_cases function
            get_use_cases()
    # Assert the expected exception status code (401)
    assert exception_info.value.code == 401
