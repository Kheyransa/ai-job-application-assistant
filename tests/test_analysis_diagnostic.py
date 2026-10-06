import asyncio
import gzip

import httpx

from scripts.diagnose_analysis import RecordingTransport, inspect_response


def test_compressed_upstream_error_is_not_misclassified() -> None:
    async def run() -> None:
        transport = RecordingTransport()
        await transport.inner.aclose()
        body = b'{"error":{"code":503,"status":"UNAVAILABLE"}}'
        transport.inner = httpx.MockTransport(lambda _: httpx.Response(
            503, headers={"content-encoding": "gzip"}, content=gzip.compress(body),
        ))
        async with httpx.AsyncClient(transport=transport) as client:
            response = await client.post("https://example.test/chat")
        assert response.status_code == 503
        assert response.content == body
        assert bytes(transport.body) == body
    asyncio.run(run())


def test_upstream_failure_stops_content_inspection(capsys) -> None:
    inspect_response(503, b"private provider body")
    output = capsys.readouterr().out
    assert "upstream HTTP/network" in output
    assert "private provider body" not in output
