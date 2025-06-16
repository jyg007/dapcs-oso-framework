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
"""Common Application Config."""

from pathlib import Path

from .. import AutoLoadConfig


class BaseAppConfig(AutoLoadConfig, _config_prefix="app"):
    """Application's basic configuration.

    Picked from the environment variables prefixed with ``APP__``.

    Attributes
    ----------
    name : :obj:`str`, default: A
        The application's name.

        .. confval:: APP__NAME

    debug : bool
        Start the application in debug mode if set to ``True``.

        .. envvar:: APP__DEBUG

    root : `pathlib.Path`
        The application's root directory.

        .. envvar:: APP__ROOT
    """

    name: str
    debug: bool = False
    root: Path = Path("/app-root")
