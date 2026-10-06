# AI Job Application Assistant

## Overview

A small Python API that compares a resume with a job description using an external
LLM. It returns a predictable, validated analysis rather than free-form model text.
No model is trained, and no paid service is enabled automatically.

## Features

- Match score, matching and missing skills, relevant experience, strengths and gaps.
- Truthful CV improvements and personalized interview practice questions.
- Input and AI-output validation, safe errors, bounded provider responses and timeouts.
- Swagger, ReDoc, fictional samples and offline mocked tests.

## Architecture

```text
Client -> FastAPI routes -> Pydantic request validation
       -> JobApplicationAnalyzer -> AIService interface
       -> LLMAIService -> configured chat-completions endpoint
       -> Pydantic response validation -> client
```

`JobApplicationAnalyzer` composes an `AIService` rather than depending on a vendor.
`LLMAIService` owns HTTP communication and response validation. FastAPI injects the
analyzer; a lifespan-managed async HTTP client is reused and closed at shutdown.
To replace the provider, implement `AIService.analyze_resume` and change
`app/dependencies.py`. Tests demonstrate injection with an async mock.

## Technologies

Python 3.11+, FastAPI, Pydantic 2, HTTPX, Uvicorn, python-dotenv and pytest.
The interface uses plain HTML, CSS and JavaScript served by FastAPI. There is
no Node build step, separate frontend server, database or Docker requirement.

## Project Structure

```text
app/
  api/routes.py                HTTP endpoints
  core/config.py               Environment settings
  schemas/                     Request, response and error contracts
  services/                    Interface, analyzer and LLM adapter
  exceptions/                  Safe typed failures
  dependencies.py              Dependency injection
  main.py                      App factory, lifespan and error handlers
  __main__.py                  Configurable server launcher
  static/                      HTML interface, styles and browser JavaScript
tests/                         Unit and API tests with mocked HTTP/AI
data/                          Fictional resume and job description
scripts/analyze_sample.py      Sample submission client
PROMPTS.md                     Honest development provenance
```

## Installation

Clone your repository or open this project directory. On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If activation is unavailable, use `.\.venv\Scripts\python.exe` directly.
On macOS/Linux, activate with `source .venv/bin/activate` and copy the example
with `cp .env.example .env`. Installing dependencies needs network access;
the tests themselves do not.

## Environment Variables

Edit the ignored `.env` file. Existing environment variables take precedence.

| Variable | Meaning | Default |
| --- | --- | --- |
| `AI_API_URL` | Full HTTP(S) chat-completions endpoint | Empty |
| `AI_MODEL` | Model identifier available at that endpoint | Empty |
| `AI_API_KEY` | Optional bearer credential | Empty |
| `AI_TIMEOUT_SECONDS` | HTTP timeout in seconds, greater than 0 and at most 300 | 30 |
| `HOST` | Bind address for `python -m app` | 127.0.0.1 |
| `PORT` | Bind port for `python -m app` | 8000 |

You can use a locally running LLM server exposing the required protocol, with
no API key. For example, set a local endpoint URL and the model name you have
installed. Alternatively explicitly configure a hosted provider; its charges and
data handling policies apply. Nothing contacts a provider until analysis is requested.

The adapter sends `model`, `messages` and `temperature`, and expects the provider
envelope `{"choices":[{"message":{"content":"<JSON analysis>"}}]}`.
The system message includes the analysis JSON schema. The endpoint must support
this protocol and return JSON content without markdown. Other protocols need a
different adapter. There is no fake-analysis fallback.

Without an endpoint or model, the application still starts and `/health` works;
analysis returns 503. Malformed environment settings fail at startup so deployment
configuration mistakes are visible. Configuration errors never expose keys via HTTP.

## Running the Application

```powershell
python -m app
```

Or for development with automatic reload:

```powershell
uvicorn app.main:app --reload
```

The Uvicorn CLI uses its own `--host` and `--port` flags; `HOST` and `PORT`
are read by the `python -m app` launcher.

## Web Interface

Start with `python -m app`, then open http://127.0.0.1:8000/.
If you use the already-installed workspace environment without activation:

```powershell
.\.venv\Scripts\python.exe -m app
```

Paste your resume and job description, or select **Load sample** for the project's
fictional documents. Select **Analyze match** to request a real backend analysis.
The responsive interface shows counts, input guidance, loading state, safe errors,
an AI match estimate, and all recommendation categories. Inputs stay in the page
on failure. **Clear** removes the inputs and displayed results. Nothing is saved
in browser storage; reloading the page discards its inputs. Documents are sent
to the configured provider through the backend. Provider credentials never enter
the frontend. Keyboard focus and status/error announcements support navigation.

The existing `/docs`, `/redoc`, `/health` and `/api/v1/analyze` remain available.
`/ui/samples` exposes only the fictional sample files. `/static` exposes only
`app/static`, never the project root or `.env`.

## Swagger

Open http://127.0.0.1:8000/docs. Expand `POST /api/v1/analyze`, select
**Try it out**, enter the two text fields and execute.

## ReDoc

Open http://127.0.0.1:8000/redoc for the generated reference documentation.
The OpenAPI schema is at `/openapi.json`.

## Running Tests

```powershell
pytest
```

Tests cover both input fields, whitespace, length and meaningful-text checks;
strict score and list validation; analyzer delegation; HTTP envelopes, malformed
JSON, invalid fields, size limits, provider failures, network errors and timeouts;
health, analysis, generated docs and safe error responses. No real provider calls
or credentials are used. `httpx.MockTransport` tests the actual adapter protocol.

Initial verification on Python 3.13: **59 tests passed**; dependency consistency and
Python compilation passed. A real Uvicorn process served `/health`, `/docs`,
`/redoc` and OpenAPI successfully. You can repeat the server check with
`python scripts/verify_server.py`. The installed Starlette release emits a
deprecation warning for its HTTPX-based test client; it does not affect these
test results. No live LLM call was made during that initial verification.

Optional UI checks use Playwright with installed Microsoft Edge. Playwright is
only a verification tool and is not required to run the app:

```powershell
python -m pip install playwright
python scripts/check_frontend.py
```

This starts a temporary local server, intercepts analysis requests with explicit
test responses, and checks success, safe text rendering, empty lists, validation,
provider errors, timeout and connection failures, duplicate prevention, samples,
clear, focus, and desktop/mobile layout. It makes no live Gemini calls. Screenshots
are written to ignored `.ui-checks/` for local review.

Frontend verification: **68 pytest tests passed**. Headless Edge checks passed
for the scenarios above, including mobile widths of 390 and 320 pixels with no
horizontal overflow. Desktop and mobile screenshots were visually reviewed.
No live provider request was made while adding the interface.

## Example Request

```json
{
  "resume": "Python developer with FastAPI, PostgreSQL and pytest experience building tested REST services.",
  "job_description": "Seeking a Python developer with FastAPI and pytest skills. Docker and cloud deployment are desirable."
}
```

Both inputs must contain 50–20,000 characters after trimming and at least 20
letters. Unsupported control characters and unknown fields are rejected.

With the server running and an AI endpoint configured, submit the sample files:

```powershell
python scripts/analyze_sample.py
```

This script uses the default local port. If you change the server port, use
Swagger at your new address to paste `data/sample_resume.txt` and
`data/sample_job_description.txt`.

## Example Response

This is illustrative; actual recommendations depend on the configured model.

```json
{
  "match_score": 82,
  "matching_skills": ["Python", "FastAPI", "pytest"],
  "missing_skills": ["Docker"],
  "relevant_experience": ["Built tested REST services"],
  "strengths": ["API development"],
  "gaps": ["Cloud deployment not evidenced"],
  "cv_improvements": ["Add measurable outcomes for API projects"],
  "interview_questions": ["How did you test your FastAPI endpoints?"]
}
```

## Error Handling

Errors consistently use `{"code":"...","message":"..."}`.

| Status | Error |
| --- | --- |
| 422 | Invalid input or malformed request JSON |
| 503 | Missing AI endpoint/model |
| 502 | Provider status error, network failure or invalid AI response |
| 504 | Provider timeout |
| 500 | Unexpected application error |

Provider bodies, credentials, exception text and stack traces are never returned.
The health endpoint reports process liveness, not provider availability.

## Security

Secrets stay in environment variables or ignored `.env` files. No real credentials
or private candidate information are included. Logs contain lifecycle events,
analysis start/completion, safe provider status codes and failure categories;
they do not contain documents or provider error bodies. User text is serialized
as JSON and never executed. The prompt marks documents as untrusted data.
Pydantic validates every generated field. Redirects are disabled to avoid passing
authorization to another endpoint. Use HTTPS for remote providers.

## Deployment Notes

Install `requirements.txt`, set environment variables using the host's secret
settings, and start with `python -m app`. Set `HOST=0.0.0.0` and the platform's
assigned `PORT`. A platform may alternatively run Uvicorn with explicit host/port
flags. No deployment has been performed. Swagger's UI loads its standard assets
from a CDN, so viewing it may need internet even though the API runs locally.

## Limitations

Scores are subjective estimates, not hiring decisions or probabilities. Models
may hallucinate or follow malicious document instructions despite the prompt;
schema validation checks structure, not factual truth. Review outputs against
the resume. Missing skills mean not evidenced, not proven absent. Documents are
sent to your chosen provider; consider its retention policy before sending private
information. Inputs are text only. No authentication, rate limiting, retries or
storage is provided. Place request-size and access limits at a reverse proxy
before public use; field-length validation occurs after JSON parsing. The provider
response is limited to 256 KB. HTTP timeouts apply to network operations rather
than a total analysis deadline. There is no live-provider integration test.

## Future Improvements

Add opt-in integration tests for a local model, evidence citations to improve
reviewability, a second provider adapter, and deployment-level access/rate limits
if the project is exposed publicly.
