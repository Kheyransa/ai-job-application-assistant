import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from app.api.routes import router
from app.core.config import Settings
from app.exceptions.custom_exceptions import ApplicationError

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
        # HTTP client logs can include configured URLs; disable their request logging.
        logging.getLogger("httpx").setLevel(logging.WARNING)
        application.state.settings = settings or Settings.from_env()
        async with httpx.AsyncClient(follow_redirects=False, trust_env=False) as client:
            application.state.http_client = client
            logger.info("AI Job Application Assistant started")
            yield

    application = FastAPI(
        title="AI Job Application Assistant", version="1.0.0",
        description="Evidence-based resume comparison with a configurable LLM provider.",
        lifespan=lifespan,
    )
    application.include_router(router)
    static_directory = Path(__file__).resolve().parent / "static"
    application.mount("/static", StaticFiles(directory=static_directory), name="static")

    @application.get("/", include_in_schema=False)
    async def interface() -> FileResponse:
        return FileResponse(static_directory / "index.html")

    @application.get("/ui/samples", include_in_schema=False)
    async def samples() -> dict[str, str]:
        directory = Path(__file__).resolve().parents[1] / "data"
        return {
            "resume": (directory / "sample_resume.txt").read_text(encoding="utf-8"),
            "job_description": (directory / "sample_job_description.txt").read_text(encoding="utf-8"),
        }

    @application.exception_handler(ApplicationError)
    async def application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"code": exc.code, "message": exc.message})

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Never echo rejected values (which can contain the full resume).
        messages = []
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"])
            messages.append(f"{location}: {error['msg']}")
        return JSONResponse(status_code=422, content={"code": "invalid_request", "message": "; ".join(messages)})

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"code": "http_error", "message": "HTTP request could not be handled."}, headers=exc.headers)

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Exception strings and tracebacks can contain provider payloads or credentials.
        logger.error("Unexpected application failure (%s)", type(exc).__name__)
        return JSONResponse(status_code=500, content={"code": "internal_error", "message": "An unexpected internal error occurred."})

    return application


app = create_app()
