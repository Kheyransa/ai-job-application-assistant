import pytest
from pydantic import ValidationError

from app.schemas.requests import AnalyzeRequest
from app.schemas.responses import AnalysisResponse


def test_valid_and_trimmed(payload):
    payload["resume"] = " \n" + payload["resume"] + "\t "
    request = AnalyzeRequest(**payload)
    assert request.resume == payload["resume"].strip()


@pytest.mark.parametrize("field", ["resume", "job_description"])
@pytest.mark.parametrize("value", ["", "   ", "too short", "a" * 20001, "1" * 60, "Developer " * 8 + "\x00"])
def test_invalid_text(payload, field, value):
    payload[field] = value
    with pytest.raises(ValidationError):
        AnalyzeRequest(**payload)


def test_request_type_and_extra_fields(payload):
    with pytest.raises(ValidationError):
        AnalyzeRequest(**payload, unexpected="value")
    payload["resume"] = 123
    with pytest.raises(ValidationError):
        AnalyzeRequest(**payload)


@pytest.mark.parametrize("score", [-1, 101, "82", True, 82.5])
def test_score_is_strict(analysis_data, score):
    analysis_data["match_score"] = score
    with pytest.raises(ValidationError):
        AnalysisResponse(**analysis_data)


def test_blank_list_item_rejected(analysis_data):
    analysis_data["strengths"] = ["   "]
    with pytest.raises(ValidationError):
        AnalysisResponse(**analysis_data)
