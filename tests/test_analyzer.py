import asyncio

from app.schemas.requests import AnalyzeRequest
from app.services.analyzer import JobApplicationAnalyzer


def test_analyzer_delegates(payload, ai_mock):
    request = AnalyzeRequest(**payload)
    result = asyncio.run(JobApplicationAnalyzer(ai_mock).analyze(request))
    ai_mock.analyze_resume.assert_awaited_once_with(request.resume, request.job_description)
    assert result.match_score == 82
