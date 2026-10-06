import json

import pytest

from scripts.diagnose_provider import safe_diagnostic


@pytest.mark.parametrize("array", [False, True])
def test_error_envelope_redaction(array: bool) -> None:
    # A synthetic marker, not a credential.
    marker = "sensitive-marker"
    error = {"error": {"code": 503, "status": "UNAVAILABLE", "message": f"Busy {marker} Reply with OK.", "details": "withheld"}}
    body = json.dumps([error] if array else error).encode()
    output = safe_diagnostic(body, marker, "Reply with OK.")
    assert "UNAVAILABLE" in output
    assert marker not in output
    assert "Reply with OK." not in output
    assert "details" not in output


def test_unknown_body_withheld() -> None:
    assert "raw body withheld" in safe_diagnostic(b"private diagnostic", "marker", "input")
