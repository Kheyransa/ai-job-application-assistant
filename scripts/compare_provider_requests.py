"""Compare exactly one minimal and one full sample request, without raw logging."""

import asyncio
import json
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.config import Settings
from app.main import create_app
from scripts.diagnose_analysis import RecordingTransport, inspect_response


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    settings = Settings.from_env()
    key = settings.ai_api_key.get_secret_value()
    sample = {name: (root / "data" / filename).read_text(encoding="utf-8") for name, filename in (
        ("resume", "sample_resume.txt"), ("job_description", "sample_job_description.txt"),
    )}

    def redact(value: str) -> str:
        if key:
            value = value.replace(key, "[REDACTED]")
        for text in sample.values():
            for fragment in [text, *text.splitlines()]:
                if len(fragment) >= 8:
                    value = value.replace(fragment, "[REDACTED DOCUMENT]")
        value = re.sub(r"(?i)bearer\s+\S+", "[REDACTED AUTH]", value)
        return re.sub(r"[A-Za-z0-9_.-]{24,}", "[REDACTED TOKEN]", value)

    class ComparisonTransport(RecordingTransport):
        async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
            self.body.clear()
            self.status = None
            payload = json.loads(request.content)
            print("Payload summary: " + json.dumps({
                "bytes": len(request.content), "model": payload["model"],
                "roles": [message["role"] for message in payload["messages"]],
                "message_characters": [len(message["content"]) for message in payload["messages"]],
                "temperature": payload.get("temperature", "omitted"),
                "max_tokens": payload.get("max_tokens", "omitted"),
                "response_format": payload.get("response_format", "omitted"),
                "stream_parameter": payload.get("stream", "omitted"),
            }))
            response = await super().handle_async_request(request)
            print(f"Upstream status: {response.status_code}")
            selected = {name: redact(response.headers[name]) for name in (
                "content-type", "server", "via", "retry-after", "date", "x-goog-request-id",
            ) if name in response.headers}
            print("Response headers: " + json.dumps(selected))
            if not response.is_success:
                try:
                    envelope = json.loads(self.body)
                    entries = envelope if isinstance(envelope, list) else [envelope]
                    errors = []
                    for entry in entries[:3]:
                        error = entry.get("error", entry) if isinstance(entry, dict) else {}
                        if isinstance(error, dict):
                            errors.append({name: error[name] for name in ("code", "status", "message") if name in error})
                    print("Redacted upstream error: " + redact(json.dumps(errors))[:2000])
                except ValueError:
                    print("Redacted non-JSON excerpt: " + json.dumps(redact(response.text[:4000])[:1000]))
            return response

    app = create_app(settings)
    async with app.router.lifespan_context(app):
        transport = ComparisonTransport()
        async with httpx.AsyncClient(transport=transport, trust_env=False, follow_redirects=False) as provider:
            app.state.http_client = provider
            print("MINIMAL REQUEST")
            try:
                await provider.post(settings.ai_api_url, headers={"Authorization": f"Bearer {key}"},
                    json={"model": settings.ai_model, "messages": [{"role": "user", "content": "Reply with OK."}], "max_tokens": 16},
                    timeout=settings.ai_timeout_seconds)
            except httpx.RequestError as exc:
                print(f"Network failure category: {type(exc).__name__}")
            print("FULL ANALYSIS REQUEST")
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://local") as api:
                response = await api.post("/api/v1/analyze", json=sample)
                print(f"Application status: {response.status_code}")
            inspect_response(transport.status, bytes(transport.body))


if __name__ == "__main__":
    asyncio.run(main())
