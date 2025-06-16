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
"""Common Logging Configuration."""

import logging
import re
from functools import cached_property
from typing import Annotated

from pydantic import Field

from .. import AutoLoadConfig


class LoggingConfig(AutoLoadConfig, _config_prefix="logging"):
    """Logging configuration.

    Attributes
    ----------
    level : str, default=INFO, envvar=LOGGING__LEVEL
        Logging level.
    """

    level: Annotated[
        str,
        Field(
            default=logging.getLevelName(logging.INFO),
            pattern=re.compile(
                rf"^(?:-?\d+|{'|'.join(logging.getLevelNamesMapping().keys())})$",
                flags=re.IGNORECASE,
            ),
            validate_default=True,
        ),
    ]

    @cached_property
    def level_as_int(self) -> int:
        """Logging level as integer.

        Return a valid logging level [0, inf]. Value is validated by regex during init.

        Returns
        -------
        int
            The logging level to use in integer form.
        """
        try:
            return logging.getLevelNamesMapping()[self.level.upper()]
        except KeyError:
            return max(0, int(self.level))
