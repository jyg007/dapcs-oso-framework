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
"""Mock IBM Offline Signing Orchestrator Flow."""

import contextlib
import os
import time

from pydantic import ValidationError

from oso.framework.config import AutoLoadConfig, ConfigManager
from oso.framework.core.logging import LoggingFactory, get_logger
from oso.framework.data import types


class _MockConfig(AutoLoadConfig, _config_prefix="mock"):  # noqa: F401
    backend_endpoint: str
    frontend_endpoint: str
    max_retries: int = 3


class MockOSO:
    """Define a mock that mocks an iteration."""

    def __init__(self, config):
        from pathlib import Path

        import requests

        self.requests = requests

        home_directory = Path(os.path.expanduser("~"))
        app_root_path = home_directory / ".app-root"

        config.certs.export(app_root_path)

        self.cert = (config.certs.crt_filename, config.certs.key_filename)
        self.verify = config.certs.ca_filename
        self.be_endpoint = config.mock.backend_endpoint
        self.fe_endpoint = config.mock.frontend_endpoint
        self.max_retries = config.mock.max_retries

        self.logger = get_logger(self.__class__.__name__)

    def _sleep(self, duration: float):
        self.logger.debug("Sleeping for {}".format(duration))
        time.sleep(duration)

    def _check_status(self, endpoint: str):
        for retry in range(1, self.max_retries + 1):
            self._sleep(5 ** (retry - 1))
            response = None
            try:
                response = self.requests.get(
                    f"{endpoint}/status",
                    verify=self.verify,
                    cert=self.cert,
                )
                response.raise_for_status()
            except self.requests.RequestException as e:
                self.logger.error(
                    "Status response FAIL: Error {}. Code {}. Retry {}/{}.".format(
                        e.__class__.__name__,
                        -1 if not response else response.status_code,
                        retry,
                        self.max_retries,
                    )
                )
                continue

            try:
                payload = response.json()
            except ValueError:
                self.logger.error(
                    "Invalid JSON from %s/status: %r", endpoint, response.text
                )
                raise

            if "status_code" not in payload:
                self.logger.warning(
                    "%s/status returned no status_code, falling back to HTTP %d",
                    endpoint,
                    response.status_code,
                )
                payload["status_code"] = response.status_code

            try:
                status = types.ComponentStatus.model_validate(payload)
            except ValidationError as ve:
                self.logger.error("ComponentStatus validation failed: %s", ve)
                raise

            if 200 <= status.status_code < 300:
                self.logger.info("Status OK: %d", status.status_code)
                return

            self.logger.error(
                "Status FAIL: {}. Retry {}/{}.",
                status.status_code,
                retry,
                self.max_retries,
            )

        self.logger.error("Max retries reached, stopping operation.")
        raise Exception

    def iteration(self, e1: str, e2: str):
        """Run a mock iteration. e1 -> e2."""
        self.logger.info("Mock Iteration Start")

        self._check_status(e1)
        response = self.requests.get(
            f"{e1}/documents",
            verify=self.verify,
            cert=self.cert,
        )

        try:
            json_data = str(response.text)
        except ValueError:
            self.logger.error("Invalid JSON from %s/documents: %r", e1, response.text)
            raise

        # Validate the data recieved from e1
        try:
            types.DocumentList.model_validate_json(json_data)
        except ValidationError as ve:
            self.logger.error("DocumentList validation failed: %s", ve)
            raise

        # Check e2 status endpoint and push data recieved from e1 to e2 plugin
        self._check_status(e2)
        response = self.requests.post(
            f"{e2}/documents",
            headers={
                "content-type": "application/json",
            },
            verify=self.verify,
            cert=self.cert,
            data=json_data,
        )

    def phase1(self):
        """Run a mock iteration. FE -> BE."""
        self.logger.info("Starting phase1, frontend to backend.")
        self.iteration(self.fe_endpoint, self.be_endpoint)

    def phase2(self):
        """Run a mock iteration. BE -> FE."""
        self.logger.info("Starting phase2, backend to frontend.")
        self.iteration(self.be_endpoint, self.fe_endpoint)


def main():
    """Entrypoint."""
    import signal
    import sys
    from threading import Lock

    from oso.framework.config.models import certs, logging  # noqa: F401

    config = ConfigManager.reload()
    logger = LoggingFactory("MOCK", config.logging.level_as_int).logger
    mock_oso = MockOSO(config)

    _lock = Lock()

    def _usr_handler(signum, frame):
        logger.debug(f"Signal: {signum} received.")
        with contextlib.suppress(ValidationError, Exception):
            if not _lock.acquire(blocking=False):
                logger.error(f"In process, ignoring signal {signum}.")
                return
            if signum == signal.SIGUSR1:
                mock_oso.phase1()
            elif signum == signal.SIGUSR2:
                mock_oso.phase2()
            else:
                sys.exit(0)
        _lock.release()

    signal.signal(signal.SIGUSR1, _usr_handler)
    signal.signal(signal.SIGUSR2, _usr_handler)

    logger.info("Available operations: SIGUSR1 SIGUSR2")
    logger.info("SIGINT, SIGTERM, SIGKILL to exit.")

    while True:
        logger.info("Ready to receive signals.")
        signal.pause()
        logger.debug("Signal process finished.")


if __name__ == "__main__":
    main()
