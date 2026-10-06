from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid", str_strip_whitespace=True,
        json_schema_extra={"examples": [{
            "resume": "Python developer with FastAPI, PostgreSQL and pytest experience building tested REST services.",
            "job_description": "Seeking a Python developer with FastAPI and pytest skills. Docker and cloud deployment are desirable.",
        }]},
    )

    resume: str = Field(min_length=50, max_length=20000, description="Resume text, 50–20,000 characters after trimming")
    job_description: str = Field(min_length=50, max_length=20000, description="Job description text, 50–20,000 characters after trimming")

    @field_validator("resume", "job_description")
    @classmethod
    def meaningful_text(cls, value: str) -> str:
        if sum(character.isalpha() for character in value) < 20:
            raise ValueError("Provide meaningful text with at least 20 letters")
        if any(ord(character) < 32 and character not in "\n\r\t" for character in value):
            raise ValueError("Text contains unsupported control characters")
        return value
