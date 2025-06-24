# IBM Offline Signing Orchestrator Framework

This repository contains code that would enable digital assets custodians to quickly bootstrap a plugin into the OSO stack.

* `oso.framework.auth`: RESTful authentication models (supported `mtls`)
* `oso.framework.config`: application configuration
* `oso.framework.core`: core code that can be shared between the OSO stack and plugin stack
* `oso.framework.data`: data classes that is moved between plugin code and OSO code
* `oso.framework.plugin`: plugin bootstrap library

## Table of Contents

- [IBM Offline Signing Orchestrator Framework](#ibm-offline-signing-orchestrator-framework)
  - [Table of Contents](#table-of-contents)
  - [Documentation](#documentation)
  - [Introduction](#introduction)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Clone \& Install](#clone--install)
  - [Developing Contracts](#developing-contracts)
  - [Developing a Plugin](#developing-a-plugin)
    - [1. Implement the `PluginProtocol`](#1-implement-the-pluginprotocol)
    - [2. Configure environment variables](#2-configure-environment-variables)
    - [3. Build and run locally](#3-build-and-run-locally)
  - [Configuration Models](#configuration-models)
  - [Addons](#addons)
    - [1. Addon Configuartion](#1-addon-configuartion)
    - [2. Enabling an Addon in your Contract](#2-enabling-an-addon-in-your-contract)
  - [Authentication](#authentication)
    - [1. How it Works](#1-how-it-works)
    - [2. mTLS Parser](#2-mtls-parser)
    - [3. Allowlist Configuration](#3-allowlist-configuration)
  - [Podman Play \& Testing](#podman-play--testing)
    - [1. Build your images](#1-build-your-images)
    - [2. (Re)generate certs \& ConfigMap](#2-regenerate-certs--configmap)
    - [3. Start up your pods](#3-start-up-your-pods)
    - [4. Reload on code/config changes](#4-reload-on-codeconfig-changes)
    - [5. Tear down](#5-tear-down)
    - [6. Unit tests](#6-unit-tests)
  - [Mock Iteration](#mock-iteration)
    - [Running the Mock Iteration](#running-the-mock-iteration)
      - [1. Start the mock service](#1-start-the-mock-service)
      - [2. Trigger mock iterations using signals](#2-trigger-mock-iterations-using-signals)
      - [3. Expected Output](#3-expected-output)
  - [Building and Unpacking a Python Wheel File](#building-and-unpacking-a-python-wheel-file)
  - [License](#license)

## Documentation

The complete project documentation, built with Sphinx, is available on GitHub Pages.

[**Explore the Documentation**](https://ibm.github.io/dapcs-oso-framework/)

## Introduction

The IBM Offline Signing Orchestrator Framework is a library that both Offline Signing Orchestrator components and Independent Software Vendors (ISVs) plugins can utilize to quickly bootstrap a plugin into the OSO stack. By providing a reusable codebase and a standardized protocol that ISVs must adhere to, this framework streamlines the integration process, making it highly likely for plugins to work with OSO, thereby reducing the burden on both the IBM development team and ISV development team.

This framework is a reusable Python package that:

1. **Bootstraps** your component behind an NGINX mTLS reverse proxy
2. **Starts** your Flask app with Gunicorn
3. **Exposes** a standard plugin protocol for OSO to call
4. **Serializes**/**deserializes** OSO’s versioned `DocumentList` schema

By conforming to `oso.framework.plugin.base.PluginProtocol`, ISV developers only need to implement two methods and they immediately get:

* `/status` endpoint
* `/documents` GET/POST routing
* JSON ↔ pydantic type validation
* Retry, backoff, logging, error-handling

## Getting Started

### Prerequisites

* **Python 3.11+**
* **[`uv`](https://github.com/astral-sh/uv)** CLI helper
* **[`podman`](https://podman.io/)** (for local kube play)
* **[`openssl-devel`](https://www.openssl.org)** & `make` (for certs & play)
* **[`Rust`](https://www.rust-lang.org/)**
* **[`Cargo`](https://doc.rust-lang.org/cargo/getting-started/installation.html)**
* **[`libsodium-devel`](https://doc.libsodium.org/installation)**
* **[`gcc & gcc-c++`](https://gcc.gnu.org/install/)**
* **[`s390x`](https://www.ibm.com/docs/en/linux-on-systems?topic=linux-s390x)**
* **[`Terraform`](https://developer.hashicorp.com/terraform/downloads)** & **[HPVS provider](https://www.ibm.com/docs/en/hpvs/2.1.x?topic=servers-setting-up-configuring-hyper-protect-virtual)** (for contract deployment)

### Clone & Install

```bash
git clone https://github.com/IBM/dapcs-oso-framework.git
cd dapcs-oso-framework
GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1 uv sync   # creates venv & installs ibm-oso-framework entrypoints
```

## Developing Contracts

The `contracts/` directory should contain the YAML templates, terraform snippets, and helper scripts that:

1. Render your frontend/backend PodSpecs (`*.yml.tftpl`) with `tpl.*` variables
2. Generate a Kubernetes ConfigMap containing your plugin's ENV setting
3. Encrypt and package the workloads for HPVS

Directory Layout

```text
contracts/
├── frontend/
│   ├── frontend/                   # Contains frontend podman play yaml
│   ├── frontend.yml.tftpl          # PodSpec template for your frontend-plugin workload
│   ├── terraform.tf                # Terraform module configuration
│   ├── variables.tf                # Terraform variable definitions
│   ├── terraform.tfvars.template   # Example variable values for frontend
│   ├── user_data_common.tf         # Shared cloud-init / userdata snippets
│   └── user_data_frontend.tf       # Frontend-specific userdata / init script
├── grep11/
│   ├── certs/                      # Generated grep11 certs and keys
│   ├── docker-compose/             # Docker compose yaml
│   ├── grep11-c16.yml.tftpl        # (optional) PodSpec template for grep11 service
│   ├── certs.tf                    # mTLS certificate generation via Terraform
│   ├── terraform.tf                # Terraform module configuration
│   ├── variables.tf                # Terraform variable definitions
│   └── terraform.tfvars.template   # Example variable values for grep11
├── backend/
│   ├── backend/                    # Contains backend user-data
│   ├── backend.yml.tftpl           # PodSpec template for your backend-plugin workload
│   ├── terraform.tf                # Terraform module configuration
│   ├── variables.tf                # Terraform variable definitions
│   ├── terraform.tfvars.template   # Example variable values for backend
│   └── user_data_backend.tf        # Backend-specific userdata / init script
├── output/
│   ├── frontend/                   # Encrypted workload artifacts for frontend
│   ├── grep11/                     # Encrypted workload artifacts for grep11
│   └── backend/                    # Encrypted workload artifacts for backend
├── common.sh                       # Shared helper functions for the create-*.sh scripts
├── create-frontend.sh              # Render & encrypt your frontend contract
├── create-grep11.sh                # Render & encrypt your grep11 contract
├── create-backend.sh               # Render & encrypt your backend contract
└── get_workloads.sh                # Aggregate all encrypted outputs into one payload
```

To get started, `cd contracts` to read over the contract support in the [README](contracts/README.md) and follow its steps to:

* Create and populate `terraform.tfvars` under the appropriate folders. Examples are available under `terraform.tfvars.template`
* Run `create-frontend.sh`, `create-grep11.sh`, `create-backend.sh`
* Verify the encrypted workloads in `output/`

Once the encrypted workloads are generated, return here to continue on the plugin development reading.

## Developing a Plugin

### 1. Implement the `PluginProtocol`

Create a class in your module that inherits from `oso.framework.plugin._base.PluginProtocol` and implements:

* `to_oso(self) → V1_3.DocumentList`
* `to_isv(self, oso: V1_3.DocumentList) → flask.Response`
* `status(self) → V1_3.ComponentStatus`

  ```python
  from oso.framework.plugin._base import PluginProtocol
  from oso.framework.data.types import V1_3

  class MyPlugin(PluginProtocol):
      def __init__(self, plugin_config):
          super().__init__()
          # your init here...

      def to_oso(self):
          # collect and return a V1_3.DocumentList
          ...

      def to_isv(self, oso):
          # handle signed documents and return a flask.Response
          ...

      def status(self):
          # return a V1_3.ComponentStatus
          ...
  ```

### 2. Configure environment variables

```bash
  export APP__NAME="my-plugin"
  export APP__ENTRY="oso.framework.plugin:create_app"
  export PLUGIN__MODE="frontend"                  # or "backend"
  export PLUGIN__APPLICATION="my.module:MyPlugin"
  # (optional) mTLS auth
  export AUTH__PARSERS__0__TYPE="oso.framework.auth.mtls"
  export AUTH__PARSERS__0__ALLOWLIST='{"component":["SHA256:…"]}'
```

### 3. Build and run locally

```bash
podman build -t oso-plugin:local --target plugin -f Containerfile .
uv run start-component    # boots your Flask/Gunicorn app
uv run start-proxy        # boots the NGINX mTLS proxy
```

## Configuration Models

Configuration models are defined as `oso.framework.config.AutoLoadConfig`, subclassed or exported in a module that will be dynamically imported. On import, the subclass will register itself with `oso.framework.config.ConfigManager` exposing the environment variables it expects; along with the format, and validation of such.

```bash
from oso.framework.config.models import AppConfig  # noqa: F401
# APP__NAME : str
# APP__DEBUG : bool, default=False
# APP__ROOT : `pathlib.Path`, default=/app-root

from oso.framework.config.models import CertsConfig  # noqa: F401
# CERTS__CA : str
# CERTS__APP_CRT : str
# CERTS__APP_KEY : str

from oso.framework.config.models import LoggingConfig  # noqa: F401
# LOGGING__LEVEL : str | int, default=info
```

Additional configurations are defined in modules::

```bash
from oso.framework.entrypoint.component import ComponentConfig  # noqa: F401
# APP__ENTRY : str

from oso.framework.entrypoint.component import GunicornConfig  # noqa: F401
# GUNICORN__WORKERS : int
# GUNICORN__TIMEOUT : int
# GUNICORN__LOGGER_CLASS : str, default=`.JsonGunicornLogger`

from oso.framework.plugin._extension import PluginConfig  # noqa: F401
# PLUGIN__MODE : "frontend" | "backend"
# PLUGIN__APPLICATION : str

from oso.framework.auth.common import AuthConfig  # noqa: F401
# AUTH__PARSERS__n__TYPE : str
# AUTH__PARSERS__n__ALLOWLIST: Json

from oso.framework.entrypoint.nginx import NginxConfig  # noqa: F401
# NGINX__TIMEOUT : `datetime.timedelta`, default=60s
```

Notes:

Since the models are registered on import-time, there are side-effects that may occur during the initial bootstrap:

* Having a module define or import an `oso.framework.config.AutoLoadConfig` that is not associated with the module will add required configuration and result in a `StartupException` if the Environment Variables are not exported.

## Addons

The framework supports **addons**—small, reusable components you can attach to any plugin (for example, a signing-server client, a metrics emitter, etc.).  An addon lets you share functionality across multiple plugins without duplicating TLS, HTTP or config logic.

### 1. Addon Configuartion

All addons live under `src/oso/framework/plugin/addons`.  Each one consists of:

1. A `Config` class deriving from `BaseAddonConfig`
2. An `Addon` class implementing the `AddonProtocol`

```python
# src/oso/framework/plugin/addons/signing_server.py

from typing import Any, Callable, ClassVar, Literal
from oso.framework.plugin.addons.main import AddonProtocol, BaseAddonConfig

NAME: Literal["SigningServer"] = "SigningServer"

def configure(
    framework_config: Any,
    addon_config: SigningServerConfig
) -> SigningServerAddon:
    """Factory that returns the addon instance."""
    return SigningServerAddon(framework_config, addon_config)

class SigningServerConfig(BaseAddonConfig):
    """Signing-Server-specific settings."""
    extra: str

class SigningServerAddon(AddonProtocol):
    """A SigningServer addon example."""

    NAME: ClassVar[str]       = NAME
    configure: ClassVar[Callable] = configure

    def __init__(self, framework_config: Any, addon_config: SigningServerConfig):
        self.config = addon_config
        # e.g. initialize HTTP client, load keystore, etc.
```

The framework will:

1. Discover your `SigningServerConfig` via pydantic-settings
2. Instantiate `SigningServerAddon` by calling your configure(...)
3. Make the resulting `AddonProtocol` available on startup

### 2. Enabling an Addon in your Contract

To wire an addon into your deployed plugin, set its env-vars in your HPVS contract template (*.yml.tftpl):

```yaml
# contracts/backend/backend.yml.tftpl
- name: PLUGIN__ADDONS__0__TYPE
  value: "oso.framework.plugin.addons.signing_server"
- name: PLUGIN__ADDONS__0__EXTRA
  value: ${tpl.grep11_extra}
# … you can add as many PLUGIN__ADDONS__0__<FIELD> as your Config defines
```

* `PLUGIN__ADDONS__<index>__TYPE` must point to your addon’s module path.
* Each field on your `BaseAddonConfig` becomes `PLUGIN__ADDONS__<index>__<UPPER_FIELDNAME>`.
* You may declare multiple addons by incrementing the index: `PLUGIN__ADDONS__1__TYPE`, etc.

When `start-component` runs, the framework will parse your addon env-vars, validate them, instantiate your addon, and inject it into your plugin before serving any requests.

## Authentication

The framework provides a pluggable auth layer so your plugin endpoints are secured out of the box. All that needs to be done is to configure it via environment variables and decorate your view making it nice to have no TLS boilerplate.

### 1. How it Works

* **Flask Extension**

  On startup you call:

  ```python
  from oso.framework.auth.extension import AuthExtension
  AuthExtension(app.config.auth).init_app(app)
  ```

  This registers a `before_request` hook that runs each configured parser and saves the results in `flask.g["oso-auth"]`

* **RequireAuth decorater**

  ```python
  from oso.framework.auth.extension import RequireAuth

  @RequireAuth("mtls", "component")
  def my_endpoint(...)
      ...
  ```

  * If the parser's `authorized=False`, returns **401 Unauthorized**
  * If the user isn't in the named allowlist, returns **403 Forbidden**

### 2. mTLS Parser

The framework provides an `mTLS` parser in `oso.framework.auth.mtls` that is designed for an NGINX TLS-terminator that  verifies client certs and forwards two headers:

```http
X-SSL-CLIENT-VERIFY: SUCCESS
X-SSL-CERT: <URL-encoded PEM certificate>
```

The parser will:

* Read those two headers
* Check whether `X-SSL-Client-VERIFY == SUCCESS`
* Decodes `X-SSL-CERT` into a `cryptography.x509.Certificate`
* Computes an OpenSSH-style SHA-256 fingerprint of the client's public key
* Expose that raw fingerprint bytes as `AuthResult["_user"]` for allowlist checks

### 3. Allowlist Configuration

You configure which client certificates are allowed via environment variables:

```bash
export AUTH__PARSERS__0__TYPE="oso.framework.auth.mtls"
export AUTH__PARSERS__0__ALLOWLIST='{"component":["SHA256:…", "SHA256:…"]}'
```

The framework will parse the JSON provided, strip the `SHA256:` prefix, base64-pad if needed, and decode to raw bytes for fast comparsions.

## Podman Play & Testing

You can exercise your plugin locally using Podman’s Kubernetes-style “play” mode. The Makefile provides a handful of targets to:

1. build the three container images (runtime, builder, plugin)
2. generate TLS cert/key pairs and a ConfigMap
3. stand up your plugin + proxy as pods
4. reload or tear them down when you change code or config
5. spin up/down the mock‐OSO iteration function

### 1. Build your images

```bash
# Build the runtime, builder, and plugin images
make containerize
```

This will produce:

* oso-runtime (from Containerfile --target runtime)
* oso-builder (–target builder)
* oso-plugin (–target plugin)

### 2. (Re)generate certs & ConfigMap

By default your plugin expects:

* a CA certificate (oso-ca.crt)
* an “app” key+cert pair (app.key / app.crt)
* a “user” key+cert pair  (user.key / user.crt)

All four get generated under deploy/local/ when you run:

```bash
# keys + certs → deploy/local/{oso-ca,app,user}.{key,csr,crt}
# + render deploy/local/cm.yaml from those certs + your env settings
make play-local-up
```

You can control the plugin settings by exporting:

```bash
export APP_NAME="my-plugin"                           # default: "test"
export APP_ENTRY="oso.framework.plugin:create_app"    # entrypoint factory
export PLUGIN_APP="my.module:MyPlugin"                # your PluginProtocol impl
export PLUGIN_MODE="frontend"                         # or "backend"
# For a fresh cm.yaml even if it already exists:
export REGEN_CM=1
```

### 3. Start up your pods

```bash
# Launch your plugin + reverse proxy
make play-local-up
```

Under the covers this runs:

* `podman kube play --configmap deploy/local/cm.yaml deploy/local/play.yaml`

### 4. Reload on code/config changes

```bash
make play-local-reload
```

This sequence tears down & recreates the two pods with your updated image or `cm.yaml`.

### 5. Tear down

```bash
make play-local-down
```

This will:

* `podman kube down deploy/local/play.yaml`
* remove the `local` volume

### 6. Unit tests

```bash
make unit-test
```

Or directly:

```bash
uv sync --extra=test
uv run pytest
```

## Mock Iteration

The framework includes a lightweight mock OSO harness to help you excerise plugins that will not utilize Framework, hence there is a mock iteration tool to validate their data. This allows for an e2e smoke test of the plugin's HTTP API (`/status` and `/documents` endpoints).

To use the mock iteration function, the developer must set environment variables as below before hand:

```bash
# Set frontend and backend endpoints for testing
export MOCK__FRONTEND_ENDPOINT="<your_frontend_endpoint>"
export MOCK__BACKEND_ENDPOINT="<your_backend_endpoint>"

# Load certificates for secure communication
export CERTS__CA="$(< /path/to/ca_cert.pem)"
export CERTS__APP_CRT="$(< /path/to/server_cert.pem)"
export CERTS__APP_KEY="$(< /path/to/server_key.pem)"
export LOGGING__LEVEL=debug
```

Please make sure the endpoints are running the server setup from the ISV end. Once the above variables are defined, a podman container for the mock generated and applied like this:

```bash
make play-mock-up     # Start the mock container (use -B to refresh configmap)
make play-mock-down   # Tear down the container
```

### Running the Mock Iteration

Once the container is up:

#### 1. Start the mock service

```bash
  uv run start-mock
```

#### 2. Trigger mock iterations using signals

* Frontend → Backend: `kill -SIGUSR1 $(pgrep -f start-mock)`
* Backend → Frontend: `kill -SIGUSR2 $(pgrep -f start-mock)`

#### 3. Expected Output

If everything is working correctly, you should see logs like:

```json
{"event": "Status OK: 200", "logger": "MockOSO", "level": "info", "timestamp": "2025-05-15T19:11:21.119020Z", "app": {"name": "MOCK"}}
{"event": "Status OK: 200", "logger": "MockOSO", "level": "info", "timestamp": "2025-05-15T19:11:22.126998Z", "app": {"name": "MOCK"}}
```

This confirms that:

* The `/status` and `/documents` endpoints are reachable (You will notice two `Status OK: 200` for both the endpoints).
* The plugin is correctly ingesting and responding with the expected dataset.

## Building and Unpacking a Python Wheel File

If you need to build a Python wheel (`.whl`) file for this project, perhaps for distribution or inspection, follow these steps:

1. **Install the `wheel` package:**
    First, ensure you have the `wheel` package installed in your Python environment. You can do this using `uv`:

    ```bash
    uv pip install wheel
    ```

2. **Build the wheel file:**
    Navigate to the root directory of the project and use `uv build` with the `--wheel` flag. This will compile your project into a wheel file and place it in a `dist/` directory.

    ```bash
    uv build --wheel
    ```

    You should see output similar to "Successfully built **dist/ibm\_oso\_framework-0.0.0-py3-none-any.whl**" (the version number might vary).

3. **Locate the generated wheel file:**
    The wheel file will be located in the newly created `dist/` directory. You can confirm its presence by listing the contents:

    ```bash
    ls dist/
    ```

    You should see your `.whl` file listed, for example: `ibm_oso_framework-0.0.0-py3-none-any.whl`.

4. **Unpack the wheel file (Optional):**
    If you want to inspect the contents of the built wheel file, you can unpack it. First, activate your virtual environment if you haven't already:

    ```bash
    uv venv # If you don't have a virtual environment or it's not active
    source .venv/bin/activate
    ```

    Then, navigate into the `dist/` directory and use the `wheel unpack` command:

    ```bash
    cd dist/
    wheel unpack ibm_oso_framework-0.0.0-py3-none-any.whl
    ```

    **Note:** Replace `ibm_oso_framework-0.0.0-py3-none-any.whl` with the actual filename of your wheel if it differs.

    This command will create a new directory (e.g., `ibm_oso_framework-0.0.0/`) containing the unpacked contents of the wheel. You can then navigate into this directory and explore the project structure:

    ```bash
    cd ibm_oso_framework-0.0.0/
    ls
    tree .
    ```

## License

This project is licensed under the [`Apache 2.0 License`](LICENSE).
