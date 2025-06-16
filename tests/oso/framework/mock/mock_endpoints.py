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


import json
import sys

from flask import Flask, jsonify, request


def make_app(kind, sample_docs):
    app = Flask(f"{kind}-server")

    @app.route(f"/api/{kind}/v1alpha1/status", methods=["GET"])
    def status():
        return jsonify({"status_code": 200, "status": "OK", "errors": []})

    @app.route(f"/api/{kind}/v1alpha1/documents", methods=["GET", "POST"])
    def docs():
        if request.method == "GET":
            with open(sample_docs, "r") as f:
                return jsonify(json.load(f))
        else:
            payload = request.get_json(force=True)
            return jsonify(
                {"received": True, "count": len(payload.get("documents", []))}
            )

    return app


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python mock_endpoints.py [fe|be] PORT SAMPLE_JSON")
        sys.exit(1)

    kind, port, sample = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    app = make_app(kind, sample)
    app.run(port=port)
