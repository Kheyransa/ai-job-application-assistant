import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_analyzer
from app.schemas.requests import AnalyzeRequest
from app.schemas.responses import AnalysisResponse, ErrorResponse, HealthResponse
from app.services.analyzer import JobApplicationAnalyzer

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse, tags=["Health"], summary="Check application liveness",
            description="Reports process health without contacting the AI provider.")
async def health() -> HealthResponse:
    return HealthResponse()


@router.post(
    "/api/v1/analyze", response_model=AnalysisResponse, tags=["Analysis"],
    summary="Compare a resume with a job description",
    description="Returns a validated semantic analysis. Documents are sent to the configured AI provider.",
    responses={status: {"model": ErrorResponse, "description": description} for status, description in {
        422: "Invalid request", 503: "AI configuration missing", 502: "Provider or response failure",
        504: "Provider timeout", 500: "Unexpected internal failure",
    }.items()},
)
async def analyze(
    request: AnalyzeRequest,
    analyzer: Annotated[JobApplicationAnalyzer, Depends(get_analyzer)],
) -> AnalysisResponse:
    logger.info("Analysis request accepted")
    result = await analyzer.analyze(request)
    logger.info("Analysis request completed")
    return result
