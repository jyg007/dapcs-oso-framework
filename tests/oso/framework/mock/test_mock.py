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
import logging
import sys
import time
import types

import pytest
from pydantic import ValidationError

import oso.framework.data.types as data_types
from oso.framework.data.types import V1_3
from oso.framework.entrypoint.mock import MockOSO

data_types.ComponentStatus = V1_3.ComponentStatus
data_types.DocumentList = V1_3.DocumentList


# Fake HTTP layer to simulate endpoint responses.
class FakeRequestException(Exception):
    """Simulate requests.RequestException."""

    pass


class FakeResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise FakeRequestException(f"HTTP Error {self.status_code}")

    def json(self):
        return json.loads(self.text)


class FakeRequests:
    RequestException = FakeRequestException

    def __init__(self, endpoint_responses=None, simulate_get_exception=False):
        self.endpoint_responses = (
            endpoint_responses if endpoint_responses is not None else {}
        )
        self.simulate_get_exception = simulate_get_exception
        self.logger = logging.getLogger()

    def get(self, url, **kwargs):
        if self.simulate_get_exception and url.endswith("/status"):
            raise self.RequestException("Simulated network error during GET")

        if url in self.endpoint_responses:
            status_code, text = self.endpoint_responses[url]
            response = FakeResponse(text, status_code=status_code)
        elif url.endswith("/status"):
            response = FakeResponse(
                json.dumps({"status_code": 200, "status": "OK", "errors": []}),
                status_code=200,
            )
        elif url.endswith("/documents"):
            response = FakeResponse(
                json.dumps(
                    {
                        "documents": [
                            {
                                "id": "doc1",
                                "content": "document content",
                                "metadata": "",
                            }
                        ],
                        "count": 1,
                    }
                ),
                status_code=200,
            )
        else:
            response = FakeResponse("{}", status_code=200)

        self.logger.debug(f"GET {url} response: {response.text}")
        return response

    def post(self, url, **kwargs):
        if url in self.endpoint_responses:
            status_code, text = self.endpoint_responses[url]
            response = FakeResponse(text, status_code=status_code)
        else:
            response = FakeResponse(
                json.dumps({"status_code": 200, "status": "OK", "errors": []}),
                status_code=200,
            )
        self.logger.debug(f"POST {url} response: {kwargs['data']}")
        return response


# Fake configuration objects
class FakeCerts:
    def export(self, path):
        pass

    crt_filename = "fake.crt"
    key_filename = "fake.key"
    ca_filename = "fake_ca.crt"


class FakeMockConfig:
    backend_endpoint = (
        "https://backend"  # Doesn't matter since its fake generated here in this test
    )
    frontend_endpoint = (
        "https://frontend"  # Doesn't matter since its fake generated here in this test
    )
    max_retries = 1


class FakeLogging:
    level_as_int = 10


class FakeConfig:
    certs = FakeCerts()
    mock = FakeMockConfig()
    logging = FakeLogging()


def fake_sleep(duration: float):
    # Skip actual sleeping during tests.
    pass


# Patch the "requests" module in sys.modules so that any "import requests"
# in our target code gets our fake module.
@pytest.fixture(autouse=True)
def patch_requests(monkeypatch):
    fake_instance = FakeRequests()
    fake_requests_module = types.ModuleType("requests")
    fake_requests_module.get = fake_instance.get
    fake_requests_module.post = fake_instance.post
    fake_requests_module.RequestException = FakeRequestException
    fake_requests_module.json = json
    monkeypatch.setitem(sys.modules, "requests", fake_requests_module)


@pytest.fixture
def fake_config() -> FakeConfig:
    return FakeConfig()


@pytest.fixture
def mock_oso_instance(fake_config, monkeypatch) -> MockOSO:
    monkeypatch.setattr(time, "sleep", fake_sleep)
    instance = MockOSO(fake_config)
    instance.requests = FakeRequests()
    return instance


@pytest.fixture
def mock_oso_instance_custom_requests(fake_config, monkeypatch) -> MockOSO:
    monkeypatch.setattr(time, "sleep", fake_sleep)
    instance = MockOSO(fake_config)
    return instance


# Test cases for the Mock OSO iteration.
class TestMockIteration:
    def test_phase1_success(self, mock_oso_instance):
        """
        Test that the phase1 iteration (frontend-to-backend)
        completes without exception.
        """
        try:
            mock_oso_instance.phase1()
        except Exception as e:
            pytest.fail(f"Phase1 raised an exception: {e}")

    def test_phase2_success(self, mock_oso_instance):
        """
        Test that the phase2 iteration (backend-to-frontend)
        completes without exception.
        """
        try:
            mock_oso_instance.phase2()
        except Exception as e:
            pytest.fail(f"Phase2 raised an exception: {e}")

    def test_iteration_success(self, mock_oso_instance):
        """
        Directly test that an iteration call completes without exception
        when both endpoints return success statuses.
        """
        try:
            mock_oso_instance.iteration("https://frontend", "http://backend")
        except Exception as e:
            pytest.fail(f"Iteration raised an exception: {e}")

    def test_status_failure(self, fake_config, monkeypatch):
        """
        Test that an iteration raises an exception when the status endpoint
        repeatedly fails.
        We simulate failure by using FakeRequests with simulate_get_exception=True.
        """
        monkeypatch.setattr(time, "sleep", fake_sleep)
        m = MockOSO(fake_config)
        m.requests = FakeRequests(simulate_get_exception=True)
        with pytest.raises(Exception):
            m.phase1()


class TestMockOSOCoverage:
    def test_status_get_exception(self, mock_oso_instance_custom_requests):
        """Covers 'if not response' path."""
        mock_oso_instance_custom_requests.requests = FakeRequests(
            simulate_get_exception=True
        )
        mock_oso_instance_custom_requests.max_retries = 1

        with pytest.raises(Exception):
            mock_oso_instance_custom_requests._check_status("https://test-endpoint")

    def test_status_invalid_json(self, mock_oso_instance_custom_requests):
        """Covers 'ValueError' from response.json()."""
        mock_oso_instance_custom_requests.requests = FakeRequests(
            endpoint_responses={
                "https://test-endpoint/status": (200, "THIS IS NOT VALID JSON CONTENT")
            }
        )
        mock_oso_instance_custom_requests.max_retries = 1

        with pytest.raises(json.JSONDecodeError):
            mock_oso_instance_custom_requests._check_status("https://test-endpoint")

    def test_status_missing_code(self, mock_oso_instance_custom_requests):
        """Covers 'if "status_code" not in payload:'."""
        mock_oso_instance_custom_requests.requests = FakeRequests(
            endpoint_responses={
                "https://test-endpoint/status": (
                    200,
                    json.dumps({"status": "OK", "errors": []}),
                )
            }
        )
        mock_oso_instance_custom_requests.max_retries = 1

        mock_oso_instance_custom_requests._check_status("https://test-endpoint")

    def test_status_component_validation(self, mock_oso_instance_custom_requests):
        """Covers 'ValidationError' for ComponentStatus."""
        mock_oso_instance_custom_requests.requests = FakeRequests(
            endpoint_responses={
                "https://test-endpoint/status": (
                    200,
                    json.dumps({"status_code": 200, "status": 123}),
                )
            }
        )
        mock_oso_instance_custom_requests.max_retries = 1

        with pytest.raises(ValidationError):
            mock_oso_instance_custom_requests._check_status("https://test-endpoint")

    def test_status_non_2xx_with_retries(self, mock_oso_instance_custom_requests):
        """Covers non-2xx status code with retries."""
        mock_oso_instance_custom_requests.requests = FakeRequests(
            endpoint_responses={
                "https://test-endpoint/status": (
                    200,
                    json.dumps({"status_code": 400, "status": "BAD_REQUEST"}),
                )
            }
        )
        mock_oso_instance_custom_requests.max_retries = 2

        with pytest.raises(Exception):
            mock_oso_instance_custom_requests._check_status("https://test-endpoint")

    def test_iteration_document_validation(self, mock_oso_instance_custom_requests):
        """Covers 'ValidationError' for DocumentList."""
        mock_oso_instance_custom_requests.requests = FakeRequests(
            endpoint_responses={
                "https://frontend/documents": (
                    200,
                    json.dumps({"documents": [{"id": "doc1", "content": 123}]}),
                )
            }
        )
        mock_oso_instance_custom_requests.max_retries = 1

        with pytest.raises(ValidationError):
            mock_oso_instance_custom_requests.iteration(
                "https://frontend", "https://backend"
            )
