import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.dependencies import get_analyzer
from app.main import create_app
from app.schemas.responses import AnalysisResponse
from app.services.analyzer import JobApplicationAnalyzer


@pytest.fixture
def payload() -> dict[str, str]:
    return {
        "resume": "Python developer with FastAPI, PostgreSQL and pytest experience building tested REST services.",
        "job_description": "Seeking a Python developer with FastAPI and pytest skills. Docker and cloud deployment are desirable.",
    }


@pytest.fixture
def analysis_data() -> dict[str, object]:
    return {
        "match_score": 82, "matching_skills": ["Python", "FastAPI", "pytest"],
        "missing_skills": ["Docker"], "relevant_experience": ["Built tested REST services"],
        "strengths": ["API development"], "gaps": ["Cloud deployment not evidenced"],
        "cv_improvements": ["Add measurable outcomes for API projects"],
        "interview_questions": ["How did you test your FastAPI endpoints?"],
    }


@pytest.fixture
def provider_envelope(analysis_data: dict[str, object]) -> dict[str, object]:
    return {"choices": [{"message": {"content": json.dumps(analysis_data)}}]}


@pytest.fixture
def ai_mock(analysis_data: dict[str, object]) -> AsyncMock:
    return AsyncMock(analyze_resume=AsyncMock(return_value=AnalysisResponse(**analysis_data)))


@pytest.fixture
def client(ai_mock: AsyncMock):
    app = create_app(Settings())
    app.dependency_overrides[get_analyzer] = lambda: JobApplicationAnalyzer(ai_mock)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
