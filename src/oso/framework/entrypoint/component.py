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
"""Component Entrypoint."""


from typing import Any, Callable, override

from gunicorn.app.base import BaseApplication
from gunicorn.config import Config as GunicornOptions
from gunicorn.glogging import Logger as GunicornLogger
from pydantic import Field
from pydantic.types import ImportString

from oso.framework.config import AutoLoadConfig, ConfigManager
from oso.framework.core.logging import LoggingFactory


class ComponentConfig(AutoLoadConfig, _config_prefix="app"):
    """Require an entrypoint.

    Attributes
    ----------
    entry : `pydantic.ImportString`, envvar=APP__ENTRY
        The python import string that points to the function returning a `flask.Flask`
        application, or the instance itself.
    """

    entry: ImportString


class GunicornConfig(AutoLoadConfig, _config_prefix="gunicorn"):
    """Common Gunicorn configuration.

    Attributes
    ----------
    workers : int, default=1, envvar=GUNICORN__WORKERS
        Number of workers gunicorn should utilize.

    timeout : int, default=0, envvar=GUNICORN__TIMEOUT
        Timeout in seconds, with 0 being infinite.

    logger_class : str, default=`.JsonGunicornLogger`, envvar=GUNICORN__LOGGER_CLASS
        Logger type to use for Gunicorn. Defaults to a structured logging class with
        the same configuration as main application.
    """

    workers: int = Field(default=1, gt=0)
    timeout: int = Field(default=0, ge=0)
    logger_class: str = "oso.framework.entrypoint.component.JsonGunicornLogger"


class JsonGunicornLogger(GunicornLogger):
    """Use the format of the main application's structured logs."""

    def _set_handler(self, log, output, fmt, stream=None):
        _ = fmt
        fmt_override = LoggingFactory().json_formatter
        super()._set_handler(
            log,
            output,
            fmt_override,
            stream,
        )


class Entry(BaseApplication):
    """Main Application Entry.

    Attributes
    ----------
    cfg : `gunicorn.config.Config`
        Gunicorn's configuration set.

    options : `typing.Any`
        Cached rendered configuration.

    Parameters
    ----------
    options : `typing.Any`
        The parsed configuration.
    """

    cfg: GunicornOptions

    def __init__(self, options: Any):
        self.options = options
        super().__init__()

    @override
    def load_config(self):
        config = {
            key: value
            for key, value in self.options.gunicorn
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

        # Set some overrides
        self.cfg.set("bind", "127.0.0.1:8080")

    @override
    def load(self):
        if isinstance(self.options.app.entry, (Callable)):
            return self.options.app.entry()
        return self.options.app.entry


def main() -> None:
    """Entrypoint."""
    from oso.framework.auth.common import AuthConfig  # noqa: F401
    from oso.framework.config.models import app, logging  # noqa: F401

    config = ConfigManager.reload()
    LoggingFactory(config.app.name, config.logging.level_as_int)
    Entry(config).run()
