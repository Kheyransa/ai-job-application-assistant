from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

AnalysisItem = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
AnalysisList = Annotated[list[AnalysisItem], Field(max_length=30)]


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    match_score: int = Field(ge=0, le=100, description="Estimated alignment, not a hiring probability")
    matching_skills: AnalysisList = Field(description="Skills evidenced in the resume and requested by the job")
    missing_skills: AnalysisList = Field(description="Requested skills not evidenced in the resume")
    relevant_experience: AnalysisList = Field(description="Resume evidence relevant to this role")
    strengths: AnalysisList = Field(description="Candidate strengths supported by the provided text")
    gaps: AnalysisList = Field(description="Experience or qualification gaps")
    cv_improvements: AnalysisList = Field(description="Truthful, actionable resume improvements")
    interview_questions: AnalysisList = Field(description="Personalized practice questions")


class HealthResponse(BaseModel):
    status: Literal["healthy"] = "healthy"


class ErrorResponse(BaseModel):
    code: str = Field(description="Stable machine-readable error code")
    message: str = Field(description="Safe explanation of the failure")
