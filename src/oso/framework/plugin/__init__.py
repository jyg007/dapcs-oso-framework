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
"""Plugin entrypoint.

Plugin Application should implement `.base.PluginProtocol`.
"""


from types import SimpleNamespace

from flask import Flask

from oso.framework.core.error import register_error_handlers

from .base import PluginProtocol
from .extension import current_oso_plugin, current_oso_plugin_app


def create_app() -> Flask:
    """Create and return the WSGI application for Gunicorn to use.

    ConfigManager and LoggingFactory should be ready to use before entry.
    """
    from oso.framework.auth.extension import AuthExtension
    from oso.framework.config import ConfigManager
    from oso.framework.core.logging import LoggingFactory

    from .extension import PluginExtension

    config = ConfigManager.config
    app = Flask(__name__)
    app.config.from_object(
        SimpleNamespace(
            app_name=f"{config.plugin.mode}_plugin",
            root_path="/dev/null",
            PROPAGATE_EXCEPTIONS=True,
        )
    )

    # Initialize extensions.
    with app.app_context():
        LoggingFactory.init_app(app)
        PluginExtension(config.plugin).init_app(app)
        AuthExtension(config.auth).init_app(app)
        register_error_handlers(app)

    return app


__all__ = [
    "PluginProtocol",
    "current_oso_plugin",
    "current_oso_plugin_app",
    "create_app",
]
