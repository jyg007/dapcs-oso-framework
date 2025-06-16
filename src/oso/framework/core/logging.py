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
"""Logging."""


import logging
import sys
from typing import Any, Literal

import structlog
from flask import Flask, request, request_finished
from structlog.typing import EventDict

from oso.framework.exceptions import StartupException

from .singleton import Singleton

EXT_NAME: Literal["oso-logging"] = "oso-logging"


class LoggingFactory(metaclass=Singleton):
    """A logging factory that creates logger instances.

    Parameters
    ----------
    name : str, default="UNSET"
        The application's name.

    level : int, default=20
        The log level.
    """

    def __init__(self, name: str = "UNSET", level: int = logging.INFO) -> None:
        self.app = {"name": name}
        self.level = level

        timestamper = structlog.processors.TimeStamper(fmt="iso")

        self.json_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
            foreign_pre_chain=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.ExtraAdder(),
                timestamper,
            ],
        )

        root_handler = logging.StreamHandler(sys.stdout)
        root_handler.setFormatter(self.json_formatter)

        logging.basicConfig(
            format="%(message)s",
            level=level,
            handlers=[
                root_handler,
            ],
        )

        structlog.configure(
            processors=[
                structlog.stdlib.add_logger_name,
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_log_level,
                structlog.contextvars.merge_contextvars,
                timestamper,
                self._inject_app,
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.dict_tracebacks,
                structlog.processors.UnicodeDecoder(),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        self.logger = structlog.get_logger("oso.logging")
        self.logger.info("logging configured")
        self.logger.debug(f"Logging Level: {logging.getLevelName(level)}")

    @classmethod
    def init_app(cls, app: Flask) -> None:
        """Attach to `flask.Flask` application.

        Attributes
        ----------
        app : `flask.Flask`
            Application.
        """
        if cls not in cls._instances:
            raise AttributeError(f"{cls.__name__!r} is not initialized!")

        # Setup basic application
        app.extensions = getattr(app, "extensions", {})

        if EXT_NAME not in app.extensions:
            app.extensions[EXT_NAME] = {}

        if "self" in app.extensions[EXT_NAME]:
            raise StartupException("Plugin already initialized")

        app.extensions[EXT_NAME]["self"] = cls._instances[cls]
        request_finished.connect(cls._instances[cls]._log_request, app)
        return

    @staticmethod
    def get_logger(name: str, **kwargs) -> structlog.BoundLogger:
        """Return a logger.

        Returns
        -------
        `structlog.BoundLogger`
        """
        return structlog.get_logger(name, **kwargs)

    def _inject_app(self, _0, _1, event_dict: EventDict) -> EventDict:
        """Additional information in logs.

        Inject application information into each log. Can update the information
        globally via `LoggingFactory().app.update()` or on each logger with
        `LoggingFactory().get_logger(app={})`.
        """
        event_dict["app"] = self.app | (
            event_dict["app"] if "app" in event_dict else {}
        )
        return event_dict

    @staticmethod
    def _log_request(
        sender: Flask,
        response,
        **extras: dict[str, Any],
    ) -> None:
        """Log an incoming request."""
        sender.logger.info(f"[{response.status_code}] {request.path}")


def get_logger(name: str, **kwargs) -> structlog.BoundLogger:
    """Return a logger.

    Returns
    -------
    `structlog.BoundLogger`
    """
    return LoggingFactory.get_logger(name, **kwargs)
