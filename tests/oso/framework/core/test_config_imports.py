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

import pytest
from pydantic import ValidationError, create_model


class TestConfigImports:
    def test_imports(self, monkeypatch, ConfigManager):
        from oso.framework.config import (
            AutoLoadConfig,
            ImportListMixin,
        )

        monkeypatch.setenv("test__0__type", "tests.oso.framework.core.config_ns.c4")
        monkeypatch.setenv("test__0__two", "two")
        monkeypatch.setenv("test__1__type", "tests.oso.framework.core.config_ns.c5")
        monkeypatch.setenv("test__1__two", "two")

        from tests.oso.framework.core.config_ns import c2

        _a = create_model(
            "_a",
            __base__=(
                AutoLoadConfig,
                ImportListMixin({"test": c2._cfg_inner_abc}),
            ),
        )

        assert _a
        with pytest.raises(ValidationError):
            ConfigManager.reload()

        monkeypatch.setenv("test__0__four", "four")
        monkeypatch.setenv("test__1__five", "five")

        assert json.loads(ConfigManager.reload().model_dump_json()) == {
            "test": [
                {
                    "type": "tests.oso.framework.core.config_ns.c4",
                    "two": "two",
                    "four": "four",
                },
                {
                    "type": "tests.oso.framework.core.config_ns.c5",
                    "two": "two",
                    "five": "five",
                },
            ]
        }
