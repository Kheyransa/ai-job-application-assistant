import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.mark.parametrize("url", ["ftp://localhost", "https://user:password@localhost/chat", "https://localhost/chat?credential=value"])
def test_unsafe_urls_rejected(url):
    with pytest.raises(ValidationError):
        Settings(ai_api_url=url)


def test_environment_loading(monkeypatch):
    monkeypatch.setenv("AI_API_URL", "http://localhost:9999/chat")
    monkeypatch.setenv("AI_MODEL", " local-model ")
    monkeypatch.setenv("PORT", "9000")
    settings = Settings.from_env()
    assert settings.ai_model == "local-model"
    assert settings.port == 9000
