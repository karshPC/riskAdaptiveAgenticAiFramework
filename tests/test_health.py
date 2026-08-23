"""Smoke tests for the API starter."""

from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint_returns_ok() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

