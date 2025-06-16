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
"""Common Authentication Types."""


from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, Final, Literal, Protocol, TypedDict, override

from flask import Request
from pydantic import Json
from typing_extensions import runtime_checkable

from oso.framework.config import (
    AutoLoadConfig,
    ImportableConfig,
    ImportListMixin,
)

EXT_NAME: Final[Literal["oso-auth"]] = "oso-auth"
ALLOWLIST: Final[Literal["allowlist"]] = "allowlist"


class BaseParserConfig(ImportableConfig):
    """A parser's base configuration.

    Attributes
    ----------
    allowlist : collections.abc.Mapping[str, list[str]]
        A mapping of allowlist keys to allowlist filter values. Loaded from envvar
        the key should be in the format of ``AUTH_name_ALLOWLIST_key``, and
        the value should be in the format of a JSON object.
    """

    allowlist: Json[Mapping[str, Sequence[str]]]


@override
class AuthConfig(
    AutoLoadConfig,
    ImportListMixin({"parsers": BaseParserConfig}),
    _config_prefix="auth",
):
    """Container for parser configs.

    Attributes
    ----------
    parsers : list[BaseParserConfig]
        Parser configs, discriminated by type.
    """

    pass


class AuthResult(TypedDict):
    """Parser's authentication result.

    Attributes
    ----------
    authorized : bool
        Whether a ``HTTP 401: Unauthorized`` should be raised.
    errors : list[str]
        A list of errors that may help with debugging.
    _user : typing.Any
        The authorized user to check against the allowlist, if any.
    """

    authorized: bool
    errors: list[str]
    _user: Any


@runtime_checkable
class AuthParser(Protocol):
    """Required Parser implementation details."""

    def parse(self, request: Request) -> AuthResult:
        """Parse a given request into an :class:`AuthResult`.

        Parameters
        ----------
        request : flask.Request
            Incoming request.

        Returns
        -------
        :class:`AuthResult`
            The authentication result.
        """
        ...

    def parse_allowlist(self, allowlist: list[str]) -> list[Any]:
        """Parse input allowlist.

        Given an allowlist configuration, parse it into a format that
        :func:`~oso.framework.auth.extension.RequireAuth` can utilize to raise
        ``HTTP 403: Forbidden``.

        Parameters
        ----------
        allowlist : list[str]
            Input configuration as a list of strings.

        Returns
        -------
        list[typing.Any]
            A list of allowed users to compare a request's :attr:`AuthResult._user` to.
        """
        ...

    NAME: ClassVar[str]
