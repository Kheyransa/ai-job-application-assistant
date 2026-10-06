"""Submit fictional sample documents to a running local server."""

import json
from pathlib import Path

import httpx

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    payload = {
        "resume": (root / "data/sample_resume.txt").read_text(encoding="utf-8"),
        "job_description": (root / "data/sample_job_description.txt").read_text(encoding="utf-8"),
    }
    response = httpx.post("http://127.0.0.1:8000/api/v1/analyze", json=payload, timeout=310)
    print(json.dumps(response.json(), indent=2))
    response.raise_for_status()
