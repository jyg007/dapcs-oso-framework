import os
import pytest
import builtins
import importlib

from unittest import mock
from datetime import timedelta

from oso.framework.entrypoint import nginx


@pytest.fixture
def fake_fifo(tmp_path):
    return tmp_path / "fifo"


def test_nginx_logs_parsing(monkeypatch, fake_fifo):
    line = '2023/10/10 00:00:00 [info] 1234#0: Starting, pid: 1234, detail: "value"'
    open_mock = mock.mock_open(read_data=line + "\n")

    logger_mock = mock.Mock()
    monkeypatch.setattr(nginx, "get_logger", lambda _: logger_mock)
    monkeypatch.setattr(builtins, "open", open_mock)
    monkeypatch.setattr(os, "mkfifo", lambda _: None)

    nginx.nginx_logs(fake_fifo)
    assert logger_mock.log.called
    call_args = logger_mock.log.call_args[1]
    assert call_args["level"] == nginx.logging.INFO
    assert call_args["event"] == "Starting"
    assert call_args["nginx"]["pid"] == "1234"
    assert call_args["nginx"]["detail"] == "value"


def test_main_nginx_missing(monkeypatch, tmp_path):
    from oso.framework import config as config_module

    mock_config = mock.Mock()
    mock_config.app.root = tmp_path
    mock_config.app.name = "app"
    mock_config.app.debug = False
    mock_config.logging.level_as_int = 20
    mock_config.nginx.timeout = timedelta(seconds=10)

    monkeypatch.setattr(config_module.ConfigManager, "reload", lambda: mock_config)

    from oso.framework.entrypoint import nginx as nginx_module

    importlib.reload(nginx_module)

    monkeypatch.setattr(nginx_module.shutil, "which", lambda _: None)
    monkeypatch.setattr(nginx_module, "get_logger", lambda _: mock.Mock())

    with pytest.raises(
        nginx_module.StartupException, match="Could not find nginx executable."
    ):
        nginx_module.main()
