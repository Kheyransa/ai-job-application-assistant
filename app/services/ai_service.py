from typing import Protocol

from app.schemas.responses import AnalysisResponse


class AIService(Protocol):
    async def analyze_resume(self, resume: str, job_description: str) -> AnalysisResponse:
        """Return a validated semantic comparison of the supplied documents."""
        ...
