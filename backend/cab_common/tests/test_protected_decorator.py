import pytest
from ..cab_common_auth.decorators import protected
from flask import Flask


def test_protected_decorator_valid_token(valid_token, mock_keycloak_introspect):
    # Create a Flask app for testing
    app = Flask(__name__)

    # Create a route protected by the decorator
    @app.route("/protected", methods=["GET"])
    @protected
    def protected_route():
        return "Success"

    # Simulate a valid request with a valid token
    with app.test_client() as client:
        response = client.get(
            "/protected", headers={"Authorization": f"Bearer {valid_token}"}
        )
        assert response.status_code == 200
        assert response.data == b"Success"


def test_protected_decorator_missing_token():
    # Create a Flask app for testing
    app = Flask(__name__)

    # Create a route protected by the decorator
    @app.route("/protected", methods=["GET"])
    @protected
    def protected_route():
        return "Success"

    # Simulate a request without a token
    with app.test_client() as client:
        response = client.get("/protected")
        assert response.status_code == 401


def test_protected_decorator_invalid_token():
    # Create a Flask app for testing
    app = Flask(__name__)

    # Create a route protected by the decorator
    @app.route("/protected", methods=["GET"])
    @protected
    def protected_route():
        return "Success"

    # Simulate a request with an invalid token
    with app.test_client() as client:
        response = client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid_token"},
            json={"use_case": "example"},
        )
        assert response.status_code == 401
