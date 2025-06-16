==========================================
IBM Offline Signing Orchestrator Framework
==========================================

This repository contains code that would enable digital assets custodians to quickly bootstrap a plugin into the OSO stack.

* `oso.framework.auth`: RESTful authentication models (supported `mtls`)
* `oso.framework.config`: application configuration
* `oso.framework.core`: core code that can be shared between the OSO stack and plugin stack
* `oso.framework.data`: data classes that is moved between plugin code and OSO code
* `oso.framework.plugin`: plugin bootstrap library

-------
Concept
-------

The idea behind the plugin bootstrap is the ISV provides a ISV application implementation class and plugs that into the venv and configuration::

    # Implementation file, say in module "isv.plugin"
    >>> from oso.framework.plugin import PluginProtocol
        class ISVImpl(ISVBase):
            pass

    # Environment settings for ISV plugin bootstrap
    # In the python "module:class" format for string import

    $ export PLUGIN__APPLICATION='isv.plugin:ISVImpl'
    $ export APP__ENTRY='oso.framework.plugin.create_app'

    $ start-component

Sample implementations are defined under `oso.framework.plugin.test`, as a module and class.

-------------
Configuration
-------------

Configuration models are defined as `oso.framework.config.AutoLoadConfig`, subclassed or exported in a module that will be dynamically imported. On import, the subclass will register itself with `oso.framework.config.ConfigManager` exposing the environment variables it expects; along with the format, and validation of such.

The core configuration set is defined in `oso.framework.config.models`, which can be registered with an import::

    >>> from oso.framework.config.models import AppConfig  # noqa: F401
        # APP__NAME : str
        # APP__DEBUG : bool, default=False
        # APP__ROOT : `pathlib.Path`, default=/app-root

    >>> from oso.framework.config.models import CertsConfig  # noqa: F401
        # CERTS__CA : str
        # CERTS__APP_CRT : str
        # CERTS__APP_KEY : str

    >>> from oso.framework.config.models import LoggingConfig  # noqa: F401
        # LOGGING__LEVEL : str | int, default=info

Additional configurations are defined in modules::

    >>> from oso.framework.entrypoint.component import ComponentConfig  # noqa: F401
        # APP__ENTRY : str

    >>> from oso.framework.entrypoint.component import GunicornConfig  # noqa: F401
        # GUNICORN__WORKERS : int
        # GUNICORN__TIMEOUT : int
        # GUNICORN__LOGGER_CLASS : str, default=`.JsonGunicornLogger`

    >>> from oso.framework.plugin._extension import PluginConfig  # noqa: F401
        # PLUGIN__MODE : "frontend" | "backend"
        # PLUGIN__APPLICATION : str

    >>> from oso.framework.auth.common import AuthConfig  # noqa: F401
        # AUTH__PARSERS__n__TYPE : str
        # AUTH__PARSERS__n__ALLOWLIST: Json

    >>> from oso.framework.entrypoint.nginx import NginxConfig  # noqa: F401
        # NGINX__TIMEOUT : `datetime.timedelta`, default=60s

Notes
-----
Addendum
-----
There is consideration of keeping closed source and providing either a compiled wheel, docker image, or both. This way, we can share code between OSO proper and plugin more easily, making it be more consistent.

-----
Contributions
-----
This repository is maintained by the repository owners. Issues can be created and the repository can be forked with PRs created against the forked repository for suggestions which will be reviewed by the repository owners. Updates to this repo will need to conincide with changes required in the IBM Offline Signing Orchestrator.
