"""Start a temporary Uvicorn process and verify the real HTTP surface."""

import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", trust_env=False, timeout=2) as client:
            for _ in range(100):
                if process.poll() is not None:
                    raise RuntimeError("Uvicorn exited before becoming ready")
                try:
                    response = client.get("/health")
                    if response.status_code == 200:
                        break
                except httpx.RequestError:
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("Uvicorn did not become ready")
            assert response.json() == {"status": "healthy"}
            for path in ("/docs", "/redoc", "/openapi.json"):
                assert client.get(path).status_code == 200, path
            schema = client.get("/openapi.json").json()
            assert "post" in schema["paths"]["/api/v1/analyze"]
            assert client.post("/api/v1/analyze", json={}).status_code == 422
            print("Uvicorn startup, /health, /docs, /redoc, OpenAPI and analysis registration verified.")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
