#
# (c) Copyright IBM Corp. 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest
from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

from oso.framework.core.error import register_error_handlers


# Define a custom exception for API errors.
class InvalidAPIUsage(Exception):

    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or {})
        rv["message"] = self.message
        return rv


# Define a custom HTTPException for Conflict (409).
class ConflictException(HTTPException):
    code = 409
    description = "Conflict Error Trigger"


# Register a custom error handler for InvalidAPIUsage.
def register_custom_error_handlers(app):
    @app.errorhandler(InvalidAPIUsage)
    def handle_invalid_api_usage(e):
        response = jsonify(e.to_dict())
        response.status_code = e.status_code
        return response


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True

    register_error_handlers(app)
    register_custom_error_handlers(app)

    @app.route("/api/bad_request")
    def bad_request():
        abort(400, description="Bad Request Trigger")

    @app.route("/api/unauthorized")
    def unauthorized():
        abort(401, description="Unauthorized Access Trigger")

    @app.route("/api/forbidden")
    def forbidden():
        abort(403, description="Forbidden Access Trigger")

    @app.route("/api/conflict")
    def conflict():
        raise ConflictException()

    @app.route("/api/get_only", methods=["GET"])
    def get_only():
        return jsonify({"message": "This endpoint only accepts GET requests"})

    @app.route("/api/internal_error")
    def internal_error():
        raise ValueError("Internal Server Error Trigger")

    @app.route("/api/test")
    def test_error():
        raise ValueError("Test exception to see JSON response")

    @app.route("/api/user")
    def user_api():
        if not request.args.get("user_id"):
            raise InvalidAPIUsage("No user id provided!", status_code=400)
        raise InvalidAPIUsage("No such user!", status_code=404)

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_bad_request(client):
    response = client.get("/api/bad_request")
    data = response.get_json()
    assert response.status_code == 400
    assert data["code"] == 400
    assert "Bad Request" in data["name"]
    assert "Bad Request Trigger" in data["description"]


def test_unauthorized(client):
    response = client.get("/api/unauthorized")
    data = response.get_json()
    assert response.status_code == 401
    assert data["code"] == 401
    assert "Unauthorized" in data["name"]
    assert "Unauthorized Access Trigger" in data["description"]


def test_forbidden(client):
    response = client.get("/api/forbidden")
    data = response.get_json()
    assert response.status_code == 403
    assert data["code"] == 403
    assert "Forbidden" in data["name"]
    assert "Forbidden Access Trigger" in data["description"]


def test_conflict(client):
    response = client.get("/api/conflict")
    data = response.get_json()
    assert response.status_code == 409
    assert data["code"] == 409
    assert "Conflict" in data["name"]
    assert "Conflict Error Trigger" in data["description"]


def test_method_not_allowed(client):
    response = client.post("/api/get_only")
    data = response.get_json()
    assert response.status_code == 405
    assert data["code"] == 405
    assert "Method Not Allowed" in data["name"]


def test_internal_error(client):
    response = client.get("/api/internal_error")
    data = response.get_json()
    assert response.status_code == 500
    assert data["code"] == 500
    assert "Internal Server Error" in data["name"]
    assert "Internal Server Error Trigger" in data["description"]


def test_test_error(client):
    response = client.get("/api/test")
    data = response.get_json()
    assert response.status_code == 500
    assert data["code"] == 500
    assert "Internal Server Error" in data["name"]
    assert "Test exception to see JSON response" in data["description"]


def test_user_api_no_param(client):
    response = client.get("/api/user")
    data = response.get_json()
    assert response.status_code == 400
    assert "No user id provided!" in data.get("message", "")


def test_user_api_with_param(client):
    response = client.get("/api/user?user_id=123")
    data = response.get_json()
    assert response.status_code == 404
    assert "No such user!" in data.get("message", "")
