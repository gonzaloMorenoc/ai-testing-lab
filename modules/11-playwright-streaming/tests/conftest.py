from __future__ import annotations

import socket

import pytest


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def server_url() -> str:
    port = _free_port()
    try:
        from src.mock_chat_server import start_server
        start_server(port)
    except ImportError:
        pytest.skip("fastapi or uvicorn not installed — install with: pip install fastapi uvicorn")
    return f"http://127.0.0.1:{port}"
