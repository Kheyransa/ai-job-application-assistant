from fastapi import Request

from app.services.analyzer import JobApplicationAnalyzer
from app.services.llm_service import LLMAIService


def get_analyzer(request: Request) -> JobApplicationAnalyzer:
    return JobApplicationAnalyzer(LLMAIService(request.app.state.settings, request.app.state.http_client))
