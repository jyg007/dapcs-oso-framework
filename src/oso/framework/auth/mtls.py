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


"""mTLS (Mutual Transport Layer Security) Authentication Handler.

Attributes
----------
NAME : str
    Constaint equal to ``mtls``, the name of this handler.

HEADER_SSL_VERIFY : str
    Constant equal to ``X-SSL-VERIFY`` header key. This header's value should be
    set by the TLS terminator, with a `MTLS.SSL_VERIFY_SUCCESS` value being
    authorized.

HEADER_SSL_CERT : str
    Constant equal to ``X-SSL-CERT`` header key. This header's value should be
    set by the TLS terminator, with a url-encoded certificate string.

SSL_VERIFY_SUCCESS : str
    Constant equal to ``SUCCESS``. This is the authorized value.

SSL_VERIFY_MISSING : str
    Constant equal to ``FAILED: Header missing from request``. This is the
    default header value.

    .. note:

        Nginx tags the reason for failure after the ``FAILED: `` prefix on
        versions 1.11.7 and onwards. This class is mimicing that behavior. See
        https://nginx.org/en/docs/http/ngx_http_ssl_module.html for more
        details.

OPENSSH_FINGERPRINT_HEADER : str
    Constant equal to ``SHA256:``, which is the prefix for the OpenSSH fingerprint type.

MD5_FINGERPRINT_HEADER : str
    Constant equal to ``MD5:``, which is the prefix for the MD5 fingerprint type.
"""

from __future__ import annotations


from base64 import b64decode
from typing import Final
from urllib.parse import unquote_to_bytes

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.x509 import Certificate, load_pem_x509_certificate
from flask import Request

from oso.framework.core.logging import get_logger
from .common import EXT_NAME, BaseParserConfig


NAME: Final[str] = __name__.split(".")[-1]
HEADER_SSL_VERIFY: Final[str] = "X-SSL-CLIENT-VERIFY"
HEADER_SSL_CERT: Final[str] = "X-SSL-CERT"
SSL_VERIFY_SUCCESS: Final[str] = "SUCCESS"
SSL_VERIFY_MISSING: Final[str] = "FAILED: Header missing from request"
OPENSSH_FINGERPRINT_HEADER: Final[str] = "SHA256:"
MD5_FINGERPRINT_HEADER: Final[str] = "MD5:"

logger = get_logger(EXT_NAME + "-" + NAME)


class _MtlsConfig(BaseParserConfig):
    pass


def parse_allowlist(allowlist: list[str]) -> list[bytes]:
    """Parse allowlist."""
    return [load_fingerprint(fp) for fp in allowlist]


def load_fingerprint(hash: str) -> bytes:
    """Load fingerprint."""
    logger.debug(f"Loading {hash}")
    if hash.startswith(OPENSSH_FINGERPRINT_HEADER):
        hash = hash.removeprefix(OPENSSH_FINGERPRINT_HEADER)
        pad = "=" * (len(hash) % 4)
        return b64decode(hash + pad)
    raise TypeError("Invalid fingerprint format. Supported: OpenSSH.")


def parse(request: Request) -> dict:
    """Return an AuthResult."""
    data = {}
    data["errors"] = []
    data["authorized_header"] = request.headers.get(
        HEADER_SSL_VERIFY,
        SSL_VERIFY_MISSING,
    )
    data["authorized"] = data["authorized_header"] == SSL_VERIFY_SUCCESS
    if not data["authorized"]:
        data["errors"].append("Invalid or missing Nginx SSL verification")
        return data

    cert_string = request.headers.get(HEADER_SSL_CERT, "")
    try:
        data["cert"] = load_pem_x509_certificate(unquote_to_bytes(cert_string))
    except TypeError:
        data["errors"].append("Invalid or missing certificate")
        return data
    except Exception:
        data["errors"].append("Internal Server Error")
        return data

    data["fingerprint"] = data["_user"] = parse_user_fingerprint(data["cert"])
    data["subject"] = parse_user_subject(data["cert"])
    return data


def parse_user_fingerprint(cert: Certificate) -> bytes:
    """Calculate the user's public key fingerprint.

    Parameters
    ----------
    cert : `~cryptography.x509.Certificate`
        The user's public X.509 certificate.

    Returns
    -------
    str
        The user's public key fingerprint in OpenSSH format.
    """
    hash = hashes.Hash(hashes.SHA256())
    hash.update(
        b64decode(
            cert.public_key()
            .public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH,
            )
            .split(b" ")[1]
        )
    )
    return hash.finalize()


def parse_user_subject(cert: Certificate) -> str:
    """Retrive the certificate's subject line as a string.

    Parameters
    ----------
    cert : `cryptography.x509.Certificate`
        The user's public X.509 certificate.

    Returns
    -------
    str:
        The user's subject line in string format.
    """
    return cert.subject.rfc4514_string()
