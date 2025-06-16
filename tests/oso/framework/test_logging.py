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


import logging
import secrets

import pytest
from pydantic import ValidationError


class TestLogging:
    @pytest.mark.parametrize("level", logging.getLevelNamesMapping().keys())
    def test_inst_with_logging_level_str(
        self,
        monkeypatch,
        level,
        ConfigManager,
        LoggingFactory,
    ):
        monkeypatch.setenv("LOGGING__LEVEL", level)

        ext = LoggingFactory(
            level=ConfigManager.reload().logging.level_as_int,
        )
        assert ext.level == logging.getLevelNamesMapping()[level]

    @pytest.mark.parametrize("level", [secrets.randbelow(200) - 100 for _ in range(10)])
    def test_inst_with_logging_level_int(
        self,
        monkeypatch,
        level,
        ConfigManager,
        LoggingFactory,
    ):
        monkeypatch.setenv("LOGGING__LEVEL", str(level))

        ext = LoggingFactory(
            level=ConfigManager.reload().logging.level_as_int,
        )
        assert ext.level == max(0, int(level))

    @pytest.mark.parametrize(
        "level", [secrets.token_urlsafe(secrets.randbelow(10) + 1) for _ in range(10)]
    )
    def test_inst_with_logging_level_invalid(
        self,
        monkeypatch,
        level,
        ConfigManager,
        LoggingFactory,
    ):
        monkeypatch.setenv("LOGGING__LEVEL", str(level))

        with pytest.raises(ValidationError):
            LoggingFactory(level=ConfigManager.reload().logging.level)
