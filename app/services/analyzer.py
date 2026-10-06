from app.schemas.requests import AnalyzeRequest
from app.schemas.responses import AnalysisResponse
from app.services.ai_service import AIService


class JobApplicationAnalyzer:
    """Coordinate analysis without depending on a particular provider."""

    def __init__(self, ai_service: AIService) -> None:
        self._ai_service = ai_service

    async def analyze(self, request: AnalyzeRequest) -> AnalysisResponse:
        return await self._ai_service.analyze_resume(request.resume, request.job_description)
