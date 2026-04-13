from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.modules.health import routers


def _build_client() -> TestClient:
    """
    Helper function to build a FastAPI TestClient with the health router registered.

    Returns:
        TestClient: Configured test client instance with the health router.
    """
    app = FastAPI()
    app.include_router(routers.router)
    return TestClient(app)


def test_health_check_returns_ok_status():
    """
    Test that the health check endpoint (GET /health/) returns HTTP 200 and
    the JSON payload {'status': 'ok'}.
    """
    client = _build_client()

    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_db_connection_returns_connected_status(monkeypatch):
    """
    Test that the health DB endpoint returns connected status when the
    database engine's connect succeeds. Should return HTTP 200 and
    {'status': 'Database connected'}.
    """

    class _Conn:
        def execute(self, _query):
            return None

    class _ContextManager:
        def __enter__(self):
            return _Conn()

        def __exit__(self, exc_type, exc, tb):
            return False

    class _Engine:
        def connect(self):
            return _ContextManager()

    monkeypatch.setattr(routers, "engine", _Engine())
    client = _build_client()

    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "Database connected"}


def test_db_connection_returns_error_when_engine_raises(monkeypatch):
    """
    Test that the health DB endpoint returns an error JSON with the exception message
    when database engine.connect() raises a RuntimeError. Should still return HTTP 200
    and a JSON with an 'error' field.
    """

    class _Engine:
        def connect(self):
            raise RuntimeError("db down")

    monkeypatch.setattr(routers, "engine", _Engine())
    client = _build_client()

    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"error": "db down"}
