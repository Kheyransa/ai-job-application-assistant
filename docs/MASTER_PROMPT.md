You are a senior Python software engineer and software architect. Build a complete, runnable, well-structured AI project from scratch.

I want you to create the entire project, including source code, tests, documentation, configuration files, sample data, and everything necessary to run it locally.

Do not only provide examples or pseudocode. Create the actual files in the workspace.

==================================================
PROJECT
==================================================

Project name:

AI Job Application Assistant

The application helps a user analyze how well their CV/resume matches a specific job description.

The user provides:

1. Resume/CV text
2. Job description text

The application analyzes them and returns:

- overall match score
- matching skills
- missing skills
- relevant experience
- strengths
- weaknesses/gaps
- CV improvement suggestions
- personalized interview questions

The project should demonstrate real-world software engineering practices while remaining small and understandable.

The application must use an LLM/AI provider for semantic analysis and generation, but the AI provider must be abstracted behind a service interface so that the provider can easily be changed later.

Do NOT build or train a machine-learning model from scratch.

==================================================
MAIN TECHNOLOGY
==================================================

Use:

- Python 3.11+
- FastAPI
- Pydantic
- pytest
- pytest-mock or unittest.mock
- Uvicorn
- python-dotenv
- an HTTP client such as httpx if needed
- an external LLM API through a provider abstraction

Use type hints throughout the project.

Avoid unnecessary dependencies.

Do not use a frontend unless it is genuinely necessary. The main interface should be the FastAPI API and Swagger UI.

==================================================
API DOCUMENTATION
==================================================

Use FastAPI properly so that OpenAPI documentation is automatically generated.

The application must provide:

Swagger UI:

/docs

ReDoc:

/redoc

The API should have clear endpoint descriptions, request models, response models, field descriptions, and useful HTTP status codes.

At minimum implement:

GET /health

POST /api/v1/analyze

The /health endpoint should return a simple health response.

The /api/v1/analyze endpoint should accept a resume and job description and return the structured analysis.

==================================================
EXPECTED API INPUT
==================================================

Create a Pydantic request model similar to:

AnalyzeRequest

Fields:

resume: string
job_description: string

Validation requirements:

- resume must not be empty
- job_description must not be empty
- reasonable minimum length
- reasonable maximum length
- strip unnecessary whitespace
- reject obviously invalid input
- provide useful validation error messages

Do not over-engineer validation.

==================================================
EXPECTED API OUTPUT
==================================================

Create a strongly typed Pydantic response model.

The response should contain approximately:

match_score: integer from 0 to 100

matching_skills: list of strings

missing_skills: list of strings

relevant_experience: list of strings

strengths: list of strings

gaps: list of strings

cv_improvements: list of strings

interview_questions: list of strings

The exact schema can be improved if you have a better design, but the response must be predictable and validated.

Do not simply return an unstructured string from the AI.

==================================================
AI SERVICE ARCHITECTURE
==================================================

This is very important.

Do not tightly couple the entire application to one AI provider.

Create an abstraction/interface for the AI service.

For example, use an abstract base class or protocol such as:

AIService

with a method conceptually similar to:

analyze_resume(resume, job_description)

Then create a concrete implementation such as:

LLMAIService

The application/service layer should depend on the abstraction rather than directly calling the external provider.

This should make it possible to replace the AI provider later.

Use dependency injection where appropriate.

Do not create unnecessary abstractions.

==================================================
AI PROVIDER
==================================================

The actual AI provider must be configurable.

Do NOT hardcode API keys.

Do NOT assume that the user has an OpenAI API subscription.

Do NOT create code that requires a paid API unless explicitly configured.

Read API configuration from environment variables.

For example:

AI_API_KEY
AI_API_URL
AI_MODEL

The exact names can be chosen sensibly.

Create:

.env.example

with placeholder values.

Create:

.env

only if needed locally, but make sure it is ignored by Git.

The real API key must NEVER appear in source code.

The application should fail gracefully if the required AI configuration is missing.

Do not expose the API key in errors or API responses.

==================================================
AI RESPONSE
==================================================

The AI should be instructed to return structured JSON matching the expected response schema.

The application must validate the AI response before returning it to the user.

Handle:

- malformed JSON
- missing fields
- incorrect field types
- invalid match score
- empty AI responses
- provider errors
- timeout errors
- network errors

Do not blindly trust the AI output.

If possible, use Pydantic to validate the AI-generated response.

==================================================
BUSINESS LOGIC
==================================================

Separate business logic from API routing.

Do NOT put everything inside main.py.

Create an appropriate service layer.

For example:

API layer
    ↓
Application/service layer
    ↓
AI service
    ↓
External AI provider

The application/service layer should coordinate the analysis.

The API layer should mainly handle:

- HTTP requests
- validation
- dependency injection
- HTTP responses

The service layer should handle application logic.

The AI provider should handle communication with the external LLM.

==================================================
OOP REQUIREMENTS
==================================================

Use OOP appropriately.

The project must demonstrate real use of:

- classes
- encapsulation
- separation of responsibilities
- composition
- dependency injection
- abstraction/interface where useful

Possible classes may include:

JobApplicationAnalyzer
AIService
LLMAIService
Configuration/Settings
Custom exception classes

Do NOT create classes just to artificially satisfy an OOP requirement.

Each class must have a clear responsibility.

Keep the design understandable to a university student.

==================================================
PROJECT STRUCTURE
==================================================

Use a clean structure similar to:

project-root/
│
├── app/
│   ├── init.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── init.py
│   │   └── routes.py
│   │
│   ├── schemas/
│   │   ├── init.py
│   │   ├── requests.py
│   │   └── responses.py
│   │
│   ├── services/
│   │   ├── init.py
│   │   ├── analyzer.py
│   │   ├── ai_service.py
│   │   └── llm_service.py
│   │
│   ├── core/
│   │   ├── init.py
│   │   └── config.py
│   │
│   ├── exceptions/
│   │   ├── init.py
│   │   └── custom_exceptions.py
│   │
│   └── dependencies.py
│
├── tests/
│   ├── init.py
│   ├── test_validation.py
│   ├── test_analyzer.py
│   ├── test_ai_service.py
│   ├── test_api.py
│   └── test_error_handling.py
│
├── data/
│   ├── sample_resume.txt
│   └── sample_job_description.txt
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── PROMPTS.md
└── pyproject.toml

You may adjust the structure if there is a clearly better simple architecture.

Do not over-engineer it.

==================================================
CONFIGURATION
==================================================

Use environment variables for configuration.

Create a clean settings/configuration class.

The application should read configuration safely.

At minimum support:

- AI API key
- AI API URL/provider
- AI model
- application environment if useful

Use .env locally.

Never commit secrets.

==================================================
ERROR HANDLING
==================================================

Implement professional error handling.

Handle at least:

1. Invalid request data
2. Missing AI configuration
3. AI provider failure
4. Network failure
5. AI timeout
6. Invalid AI response
7. Unexpected internal error

Use custom exceptions where useful.

Return appropriate HTTP status codes.

Do not expose stack traces to API users.

Do not expose sensitive configuration.

Use FastAPI exception handlers where appropriate.

Errors should have consistent JSON responses.

==================================================
LOGGING
==================================================

Add basic application logging.

Log useful information such as:

- application startup
- requests at an appropriate level
- AI provider errors
- unexpected exceptions

Do NOT log:

- API keys
- complete CV contents
- sensitive personal information
- full job application data

Keep logging simple.

==================================================
TESTING
==================================================

Testing is a major requirement.

Use pytest.

Create meaningful unit and API tests.

The complete test suite must be runnable with:

pytest

Tests must NOT require a real paid AI API.

Mock the external AI service/provider.

Test at least:

1. Valid request validation
2. Empty resume
3. Empty job description
4. Resume too short
5. Job description too short
6. Excessively long input
7. Whitespace handling
8. Valid AI response
9. Malformed AI response
10. AI provider failure
11. AI timeout/network error
12. Analyzer service behavior
13. /health endpoint
14. /api/v1/analyze endpoint
15. Invalid API request
16. Appropriate HTTP error responses

Tests must test actual behavior.

Do NOT create meaningless tests just to increase test count.

Use fixtures where appropriate.

Mock external dependencies.

The test suite should work without an internet connection if possible.

After implementing the tests, RUN THEM.

If tests fail, diagnose and fix the implementation.

Do not simply change tests to hide implementation problems.

==================================================
SAMPLE DATA
==================================================

Create small realistic sample files:

data/sample_resume.txt

data/sample_job_description.txt

The sample resume should describe a fictional candidate.

The sample job description should describe a fictional software/AI-related position.

Do not use real people's private information.

These files should make it easy to test the application manually.

==================================================
SECURITY
==================================================

Follow basic security practices.

Requirements:

- no hardcoded secrets
- .env in .gitignore
- .env.example included
- no API key in README
- no API key in tests
- no sensitive information in logs
- validate user input
- do not execute user-provided text as code
- do not construct shell commands from user input
- avoid unsafe deserialization

==================================================
CODE QUALITY
==================================================

Follow good Python practices.

Use:

- type hints
- clear names
- small focused functions
- appropriate docstrings
- PEP 8 style
- sensible imports
- modular design
- meaningful exception messages

Avoid:

- duplicated code
- giant functions
- giant files
- global mutable state
- unnecessary dependencies
- unnecessary inheritance
- unnecessary design patterns
- commented-out dead code
- placeholder TODOs in the final implementation

The code should be understandable, not artificially complicated.

==================================================
README
==================================================

Create a professional README.md.

It must include:

# Project title

## Overview

Explain the problem and solution.

## Features

List the main features.

## Architecture

Explain the architecture in simple language.

Include an ASCII architecture diagram if useful.

For example:

Client
  ↓
FastAPI
  ↓
Validation
  ↓
Analyzer Service
  ↓
AI Service
  ↓
LLM Provider

## Technologies

List technologies used.

## Project Structure

Explain important directories.

## Installation

Explain how to clone/install the project.

## Environment Variables

Explain .env and .env.example.

Never include a real API key.

## Running the Application

Show the command needed to start FastAPI.

For example:

uvicorn app.main:app --reload

## Swagger

Explain:

http://127.0.0.1:8000/docs

## ReDoc

Explain:

http://127.0.0.1:8000/redoc

## Running Tests

Explain:

pytest

## Example Request

Provide a safe example.

## Example Response

Provide a representative response.

## Error Handling

Explain the main handled errors.

## Security

Explain how secrets are protected.

## Limitations

Be honest about limitations.

## Future Improvements

Suggest realistic future improvements.

==================================================
PROMPTS.MD
==================================================

Create a PROMPTS.md file.

This file should document the AI-assisted development process.

Include:

1. The master development prompt
2. Short descriptions of important follow-up instructions if any were needed
3. The purpose of using AI during development

Do not claim that code was manually written if it was AI-generated.

Keep the documentation honest.

==================================================
GIT/GITHUB READINESS
==================================================

Prepare the project for GitHub.

Create a proper .gitignore.

It should exclude at least:

.env
pycache/
.pytest_cache/
.venv/
venv/
*.pyc
coverage files
IDE-specific files where appropriate

Do not include:

- API keys
- secrets
- personal information
- unnecessary generated files

Create a requirements.txt containing the dependencies actually required by the project.

If useful, also create pyproject.toml for project configuration.

==================================================
HEALTH ENDPOINT
==================================================

Implement:

GET /health

Return a simple structured response such as:

{
    "status": "healthy"
}

The endpoint must be tested.

==================================================
ANALYZE ENDPOINT
==================================================

Implement:

POST /api/v1/analyze

Request:

{
    "resume": "...",
    "job_description": "..."
}

Response:

{
    "match_score": 82,
    "matching_skills": [...],
    "missing_skills": [...],
    "relevant_experience": [...],
    "strengths": [...],
    "gaps": [...],
    "cv_improvements": [...],
    "interview_questions": [...]
}

Use proper Pydantic schemas.

==================================================
SWAGGER / OPENAPI
==================================================

Make the Swagger UI useful.

Add:

- endpoint summaries
- descriptions
- request schemas
- response schemas
- meaningful status codes
- examples where useful

The application should automatically expose:

/docs

and:

/redoc

==================================================
DEPLOYMENT READINESS
==================================================

The application should be easy to deploy to a free hosting platform.

Do not require Docker unless it is genuinely useful.

Make sure the application can bind to a host and configurable port when deployed.

Do not hardcode localhost into application logic.

If necessary, support:

HOST
PORT

through environment variables.

Include deployment notes in README.

Do not actually deploy the application unless deployment tools/credentials are available.

==================================================
IMPORTANT AI DESIGN DECISION
==================================================

The application should not rely entirely on an LLM for deterministic validation.

For example:

Input validation should be handled by Pydantic.

API errors should be handled by the application.

AI response validation should be handled by Pydantic.

The LLM should be responsible for semantic analysis and natural-language recommendations.

Keep deterministic responsibilities in normal Python code.

==================================================
MANUAL TESTABILITY
==================================================

Make it easy for me to test the project.

After implementation, explain:

1. How to create a virtual environment
2. How to install dependencies
3. How to configure the .env file
4. How to start the server
5. How to open Swagger
6. How to run the tests
7. How to test the sample data

==================================================
DEVELOPMENT PROCESS
==================================================

Do NOT stop after creating the first version.

Follow this process:

STEP 1:
Inspect the workspace and determine whether it is empty or already contains files.

STEP 2:
Create the project structure.

STEP 3:
Implement configuration.

STEP 4:
Implement Pydantic schemas and validation.

STEP 5:
Implement custom exceptions and error handling.

STEP 6:
Implement the AI service abstraction.

STEP 7:
Implement the concrete LLM service.

STEP 8:
Implement the analyzer/application service.

STEP 9:
Implement FastAPI routes.

STEP 10:
Implement Swagger/OpenAPI metadata and examples.

STEP 11:
Create sample data.

STEP 12:
Create comprehensive tests with mocked AI dependencies.

STEP 13:
Run the complete test suite.

STEP 14:
Fix all failures.

STEP 15:
Run the application and verify the API if possible.

STEP 16:
Review the project for:
- OOP
- validation
- testing
- error handling
- security
- clean architecture
- type hints
- documentation
- GitHub readiness

STEP 17:
Create the final README.md.

STEP 18:
Create PROMPTS.md.

STEP 19:
Perform a final code review.

Do not declare the project complete if there are obvious errors.

==================================================
IMPORTANT CONSTRAINTS
==================================================

Keep the project small enough for a university assignment.

Do not add:
- authentication
- databases
- microservices
- queues
- Kubernetes
- complicated frontend
- unnecessary design patterns

unless they are genuinely necessary.

The goal is a small but professional project, not a huge production system.

The code should demonstrate quality rather than complexity.

==================================================
FINAL REQUIREMENT
==================================================

When you finish:

1. Make sure all files exist.
2. Run pytest.
3. Fix failing tests.
4. Verify imports.
5. Verify the FastAPI application can start.
6. Verify /health.
7. Verify /docs exists.
8. Verify /redoc exists.
9. Verify the analyze endpoint is correctly registered.
10. Verify no secrets are committed.
11. Verify .gitignore exists.
12. Verify README.md exists.
13. Verify PROMPTS.md exists.
14. Verify requirements.txt exists.
15. Give me a concise summary of:
   - files created
   - architecture
   - main features
   - tests
   - test results
   - commands needed to run the project
   - any remaining configuration I need to provide

Do not replace implementation with pseudocode.

Do not leave major features as TODOs.

Build the actual working project.