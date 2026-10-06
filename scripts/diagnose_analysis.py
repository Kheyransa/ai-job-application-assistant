"""One full sample analysis through the API, with stage-only diagnostics."""

import asyncio
import json
import sys
from pathlib import Path

import httpx
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.config import Settings
from app.main import create_app
from app.schemas.responses import AnalysisResponse
from app.services.llm_service import MAX_RESPONSE_BYTES


class RecordingTransport(httpx.AsyncBaseTransport):
    def __init__(self) -> None:
        self.inner = httpx.AsyncHTTPTransport(retries=0)
        self.status: int | None = None
        self.body = bytearray()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        response = await self.inner.handle_async_request(request)
        self.status = response.status_code
        async for chunk in response.aiter_bytes():
            self.body.extend(chunk)
            if len(self.body) > MAX_RESPONSE_BYTES:
                break
        await response.aclose()
        # aiter_bytes has already decoded compression. Do not decode it twice.
        headers = {name: value for name, value in response.headers.items()
                   if name.lower() not in {"content-encoding", "content-length", "transfer-encoding"}}
        return httpx.Response(response.status_code, headers=headers, content=bytes(self.body))

    async def aclose(self) -> None:
        await self.inner.aclose()


def inspect_response(status: int | None, body: bytes) -> None:
    print(f"Upstream HTTP status: {status}")
    if status is None or not 200 <= status < 300:
        print("Failure stage: upstream HTTP/network; no generated analysis to validate.")
        return
    try:
        envelope = json.loads(body)
        content = envelope["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise TypeError()
    except (ValueError, KeyError, IndexError, TypeError):
        print("Failure stage: response-envelope parsing; missing/invalid choices[0].message.content.")
        return
    fenced = content.strip().startswith("```")
    print(f"Generated content starts with markdown fence: {fenced}")
    try:
        json.loads(content)
    except ValueError:
        print("Failure stage: generated-content JSON parsing.")
        if fenced:
            inner = content.strip().splitlines()
            if len(inner) >= 3 and inner[-1].strip() == "```":
                content = "\n".join(inner[1:-1])
                print("Inspecting fenced payload against unchanged strict schema.")
            else:
                return
        else:
            return
    try:
        AnalysisResponse.model_validate_json(content)
    except ValidationError as exc:
        print("Strict schema validation failed:")
        known = set(AnalysisResponse.model_fields)
        for error in exc.errors(include_input=False, include_context=False, include_url=False):
            location = error["loc"]
            field = location[0] if location and location[0] in known else "[unknown field]"
            print(f"  field={field}; type={error['type']}")
    else:
        print("Strict schema validation passed.")


async def main() -> None:
    root = Path(__file__).resolve().parents[1]
    settings = Settings.from_env()
    app = create_app(settings)
    transport = RecordingTransport()
    payload = {
        "resume": (root / "data/sample_resume.txt").read_text(encoding="utf-8"),
        "job_description": (root / "data/sample_job_description.txt").read_text(encoding="utf-8"),
    }
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, trust_env=False, follow_redirects=False) as provider:
            app.state.http_client = provider
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://local") as api:
                response = await api.post("/api/v1/analyze", json=payload)
                print(f"Full API HTTP status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Safe API error code: {response.json().get('code', 'unknown')}")
    inspect_response(transport.status, bytes(transport.body))


if __name__ == "__main__":
    asyncio.run(main())
