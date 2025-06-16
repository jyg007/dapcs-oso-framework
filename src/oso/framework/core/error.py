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
"""Error Handling."""

import json

from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.

    This function registers error handlers for standard HTTP exceptions and a catch-all
    error handler for non-HTTP exceptions.

    Args:
        app: The Flask application instance.
    """
    # Register error handler for standard HTTP exceptions.
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = json.dumps(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        )
        response.content_type = "application/json"
        return response

    # Catch-all error handler for non-HTTP exceptions.
    @app.errorhandler(Exception)
    def handle_exception(e):
        if isinstance(e, HTTPException):
            return e
        response = jsonify(
            {
                "code": 500,
                "name": "Internal Server Error",
                "description": str(e),
            }
        )
        return response, 500
