# AI-assisted development record

## Purpose

AI generated the implementation, tests, sample data and documentation from the
user's specification, then used local checks to identify implementation problems.
This project is not represented as manually authored code. The development AI
and the runtime LLM provider are separate: runtime credentials are user-configured.

## Master development prompt

The complete, verbatim user specification is preserved in
[docs/MASTER_PROMPT.md](docs/MASTER_PROMPT.md). It requests a small, complete,
runnable **AI Job Application Assistant** using Python 3.11+, FastAPI, Pydantic,
pytest, an injectable AI abstraction, structured analysis, safe errors, samples,
documentation and actual verification. It prohibits training a model, secrets,
paid-provider assumptions, unnecessary infrastructure and pseudocode-only output.

## Follow-up instructions

No user follow-up instructions were needed for the initial implementation. Decisions were to use
a configurable chat-completions adapter, a shared lifespan-managed HTTP client,
strict Pydantic output validation, safe error envelopes and offline HTTP mocks.
Local dependency installation and verification were part of the original request.

Subsequent user requests diagnosed the configured Gemini provider using safe live
diagnostics and selected a lightweight model after a full validated analysis.
The user then requested a plain HTML, CSS and JavaScript frontend served by the
existing FastAPI app, retaining provider configuration and strict validation.
AI implemented the interface and verified it with mocked browser responses,
mobile layout checks and the existing Python suite. UI verification made no
live provider requests.

## Runtime analysis prompt

`app/services/llm_service.py` defines the runtime system prompt. It asks the LLM
to compare only supplied evidence, treat documents as untrusted, avoid invented
qualifications and protected-characteristic inferences, and return schema-matching
JSON. Input validation, error handling and output validation remain Python code.
