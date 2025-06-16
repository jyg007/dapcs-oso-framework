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


from collections.abc import Mapping, Sequence
from random import choice, randint
from string import ascii_lowercase

import pytest
from pydantic import BaseModel, ImportString
from pydantic.fields import FieldInfo

from oso.framework.config import (
    ImportableConfig,
)
from oso.framework.config._manager import (
    _construct_intermediary,
    _isimportable,
)


class TestConfigUtils:
    @pytest.mark.parametrize(
        "kls",
        [
            (None, False),
            ("", False),
            (ImportString, True),
            (Sequence[ImportString], True),
            (list[ImportString], True),
            (BaseModel, False),
            (Mapping[str, str], False),
            (Mapping[ImportString, str], False),
            (Mapping[ImportString, ImportString], False),
            (ImportableConfig, True),
            (list[ImportableConfig], True),
        ],
    )
    def test_isimportable(self, kls):
        assert _isimportable(kls[0]) == kls[1]

    @pytest.mark.parametrize(
        "rand_string",
        [
            "".join([choice(ascii_lowercase) for _ in range(randint(5, 10))])
            for _ in range(10)
        ],
    )
    @pytest.mark.parametrize(
        "rand_path",
        [[choice(ascii_lowercase) for _ in range(randint(3, 10))] for _ in range(10)],
    )
    def test_construct(self, rand_string, rand_path):
        model = _construct_intermediary(
            FieldInfo.from_annotated_attribute(
                annotation=str,
                default=rand_string,
            ),
            *rand_path,
        )
        iter = model()
        for key in rand_path:
            assert hasattr(iter, key)
            iter = getattr(iter, key)
        assert iter == rand_string
