"""Environment-backed settings; loading never enables a paid provider by default."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, field_validator


class Settings(BaseModel):
    ai_api_url: str = ""
    ai_model: str = ""
    ai_api_key: SecretStr = SecretStr("")
    ai_timeout_seconds: float = Field(default=30, gt=0, le=300)
    host: str = "127.0.0.1"
    port: int = Field(default=8000, ge=1, le=65535)

    @field_validator("ai_api_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()
        if value:
            from urllib.parse import urlsplit

            parsed = urlsplit(value)
            if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                    or parsed.username or parsed.password or parsed.query or parsed.fragment):
                raise ValueError("Use an HTTP(S) endpoint without embedded credentials or query parameters")
        return value

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
        return cls(
            ai_api_url=os.getenv("AI_API_URL", ""),
            ai_model=os.getenv("AI_MODEL", "").strip(),
            ai_api_key=SecretStr(os.getenv("AI_API_KEY", "")),
            ai_timeout_seconds=os.getenv("AI_TIMEOUT_SECONDS", "30"),
            host=os.getenv("HOST", "127.0.0.1"),
            port=os.getenv("PORT", "8000"),
        )
