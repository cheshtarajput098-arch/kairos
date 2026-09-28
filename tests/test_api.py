"""Unit tests for FastAPI endpoints, middlewares, error envelope, security headers."""
import pytest
from fastapi.testclient import TestClient

from kairos.api.app import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_endpoint() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "kairos"}


def test_readiness_endpoint() -> None:
    response = client.get("/v1/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "service": "kairos"}


def test_security_headers_present() -> None:
    response = client.get("/v1/health")
    assert "Content-Security-Policy" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"


def test_request_id_middleware() -> None:
    response = client.get("/v1/health", headers={"X-Request-ID": "test-req-777"})
    assert response.headers["X-Request-ID"] == "test-req-777"

    response_gen = client.get("/v1/health")
    assert "X-Request-ID" in response_gen.headers


def test_error_envelope_no_stack_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    # Trigger an internal error endpoint to test custom exception handler
    @app.get("/v1/test-error")
    async def error_route() -> None:
        raise ValueError("Secret internal calculation failure!")

    response = client.get("/v1/test-error", headers={"X-Request-ID": "err-req-999"})
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert data["error"]["message"] == "An internal server error occurred."
    assert data["error"]["request_id"] == "err-req-999"
    # Ensure stack trace / secret internal message is NOT exposed to client
    assert "Secret internal calculation failure!" not in response.text
