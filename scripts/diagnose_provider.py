"""Send one tiny synthetic request; display only redacted provider diagnostics."""

import json
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.core.config import Settings


def safe_diagnostic(body: bytes, key: str, prompt: str) -> str:
    """Extract only error fields, accepting Google's object or array envelopes."""
    try:
        envelope = json.loads(body)
        entries = envelope if isinstance(envelope, list) else [envelope]
        errors = []
        for entry in entries[:5]:
            if not isinstance(entry, dict):
                continue
            error = entry.get("error", entry)
            if isinstance(error, dict):
                errors.append({name: error[name] for name in ("code", "status", "message") if name in error})
        output = json.dumps(errors, ensure_ascii=True)
        if not errors or not any(errors):
            return "Provider returned no recognized error fields; raw body withheld."
    except (ValueError, TypeError):
        return "Provider returned a non-JSON error; raw body withheld."
    output = output.replace(key, "[REDACTED]").replace(prompt, "[REDACTED INPUT]")
    output = re.sub(r"[A-Za-z0-9_.-]{24,}", "[REDACTED TOKEN]", output)
    return output[:2000]


def main() -> None:
    settings = Settings.from_env()
    key = settings.ai_api_key.get_secret_value()
    if not settings.ai_api_url or not settings.ai_model or not key:
        raise SystemExit("Diagnostic requires a configured endpoint, model and credential.")
    prompt = "Reply with OK."
    try:
        with httpx.Client(trust_env=False, follow_redirects=False) as client:
            response = client.post(
                settings.ai_api_url,
                headers={"Authorization": f"Bearer {key}"},
                json={"model": settings.ai_model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 16},
                timeout=settings.ai_timeout_seconds,
            )
        print(f"Provider HTTP status: {response.status_code}")
        # Only select response metadata; never display request/authorization headers.
        for name in ("content-type", "server", "via"):
            value = response.headers.get(name)
            if value:
                print(f"{name}: {value.replace(key, '[REDACTED]')[:300]}")
        if response.is_success:
            print("Live minimal Gemini request succeeded. No document analysis was requested.")
            return
        diagnostic = safe_diagnostic(response.content, key, prompt)
        print(diagnostic)
        if "non-JSON" in diagnostic:
            excerpt = response.text[:4000].replace(key, "[REDACTED]")
            excerpt = excerpt.replace(prompt, "[REDACTED INPUT]")
            excerpt = re.sub(r"(?i)bearer\s+\S+", "[REDACTED AUTH]", excerpt)
            excerpt = re.sub(r"[A-Za-z0-9_.-]{24,}", "[REDACTED TOKEN]", excerpt)
            # JSON escaping makes HTML and terminal control characters inert.
            print("Redacted body excerpt: " + json.dumps(excerpt[:1000], ensure_ascii=True))
    except httpx.RequestError as exc:
        print(f"Diagnostic network failure: {type(exc).__name__}; details withheld.")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
