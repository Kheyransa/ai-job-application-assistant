import asyncio
import json

import httpx
import pytest

from app.core.config import Settings
from app.exceptions.custom_exceptions import (
    ConfigurationError, InvalidAIResponse, NetworkError, ProviderError, ProviderTimeout,
)
from app.services.llm_service import LLMAIService, MAX_RESPONSE_BYTES


def run_provider(handler, payload, settings=None):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            service = LLMAIService(settings or Settings(ai_api_url="http://localhost:9999/chat", ai_model="local-model"), client)
            return await service.analyze_resume(**payload)
    return asyncio.run(run())


def test_valid_provider_response(payload, provider_envelope):
    def handler(request):
        body = json.loads(request.content)
        assert body["model"] == "local-model"
        assert "Authorization" not in request.headers
        assert json.loads(body["messages"][1]["content"]) == payload
        assert "untrusted" in body["messages"][0]["content"]
        return httpx.Response(200, json=provider_envelope)
    assert run_provider(handler, payload).match_score == 82


@pytest.mark.parametrize("envelope", [
    {}, {"choices": []}, {"choices": None},
    {"choices": [{"message": {"content": ""}}]},
    {"choices": [{"message": {"content": "not json"}}]},
    {"choices": [{"message": {"content": "{}"}}]},
    {"choices": [{"message": {"content": None}}]},
])
def test_invalid_envelope(payload, envelope):
    with pytest.raises(InvalidAIResponse):
        run_provider(lambda _: httpx.Response(200, json=envelope), payload)


@pytest.mark.parametrize("field,value", [("match_score", 101), ("match_score", "82"), ("strengths", "text"), ("gaps", [12])])
def test_invalid_generated_fields(payload, analysis_data, field, value):
    analysis_data[field] = value
    envelope = {"choices": [{"message": {"content": json.dumps(analysis_data)}}]}
    with pytest.raises(InvalidAIResponse):
        run_provider(lambda _: httpx.Response(200, json=envelope), payload)


def test_malformed_provider_json(payload):
    with pytest.raises(InvalidAIResponse):
        run_provider(lambda _: httpx.Response(200, content=b"not-json"), payload)


def test_response_size_limit(payload):
    with pytest.raises(InvalidAIResponse):
        run_provider(lambda _: httpx.Response(200, content=b" " * (MAX_RESPONSE_BYTES + 1)), payload)


@pytest.mark.parametrize("status", [401, 429, 500, 503, 302])
def test_provider_failure(payload, status):
    with pytest.raises(ProviderError):
        run_provider(lambda _: httpx.Response(status, text="private provider diagnostic"), payload)


@pytest.mark.parametrize("error,expected", [(httpx.ReadTimeout, ProviderTimeout), (httpx.ConnectError, NetworkError)])
def test_network_failures(payload, error, expected):
    def handler(request):
        raise error("private diagnostic", request=request)
    with pytest.raises(expected):
        run_provider(handler, payload)


def test_missing_configuration_never_calls_provider(payload):
    def handler(request):
        pytest.fail("Unconfigured service must not send data")
    with pytest.raises(ConfigurationError):
        run_provider(handler, payload, Settings())
