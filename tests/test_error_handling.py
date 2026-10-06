import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.exceptions.custom_exceptions import (
    ConfigurationError, InvalidAIResponse, NetworkError, ProviderError, ProviderTimeout,
)
from app.main import create_app


@pytest.mark.parametrize("error,status,code", [
    (ConfigurationError(), 503, "ai_not_configured"),
    (ProviderError(), 502, "provider_error"),
    (NetworkError(), 502, "provider_network_error"),
    (ProviderTimeout(), 504, "provider_timeout"),
    (InvalidAIResponse(), 502, "invalid_ai_response"),
    (RuntimeError("private diagnostic"), 500, "internal_error"),
])
def test_safe_errors(client, ai_mock, payload, error, status, code, caplog):
    ai_mock.analyze_resume.side_effect = error
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == status
    assert response.json()["code"] == code
    assert "private diagnostic" not in response.text + caplog.text
    assert payload["resume"] not in caplog.text


def test_unconfigured_app_runs(payload):
    with TestClient(create_app(Settings())) as client:
        assert client.get("/health").status_code == 200
        assert client.post("/api/v1/analyze", json=payload).status_code == 503


def test_not_found_is_consistent(client):
    response = client.get("/missing")
    assert response.status_code == 404
    assert set(response.json()) == {"code", "message"}
