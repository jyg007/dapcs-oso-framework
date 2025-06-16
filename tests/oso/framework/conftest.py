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


import importlib
import sys

import pytest


@pytest.fixture(scope="function")
def _cleanup():
    to_removes = [
        k
        for k in sys.modules.keys()
        if k.startswith("oso") or k.startswith("tests.oso")
    ]
    for to_remove in to_removes:
        del sys.modules[to_remove]


@pytest.fixture(scope="function")
def ConfigManager(_cleanup):
    # Clear cached config
    import oso.framework.config

    importlib.reload(oso.framework.config)
    return oso.framework.config.ConfigManager


@pytest.fixture(scope="function")
def LoggingFactory(_cleanup, ConfigManager):
    assert ConfigManager
    # Register logging config type
    # Clear logging singleton
    import oso.framework.core.logging
    from oso.framework.config.models import logging  # noqa: F401

    importlib.reload(oso.framework.core.logging)
    return oso.framework.core.logging.LoggingFactory
