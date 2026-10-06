"""Optional browser QA: requires Playwright and installed Microsoft Edge.

All analysis responses are intercepted; no live provider requests are made.
Run with: python scripts/check_frontend.py
"""

import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import expect, sync_playwright


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", str(port)],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(trust_env=False) as client:
            for _ in range(100):
                try:
                    if client.get(base + "/health").status_code == 200:
                        break
                except httpx.RequestError:
                    pass
                time.sleep(0.1)
            else:
                raise RuntimeError("Server did not start")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel="msedge", headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1050})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            result = {
                "match_score": 82, "matching_skills": ["Python", "<img src=x onerror=alert(1)>"],
                "missing_skills": [], "relevant_experience": ["Built fictional REST services"],
                "strengths": ["API development"], "gaps": ["Cloud experience not evidenced"],
                "cv_improvements": ["Describe project outcomes"],
                "interview_questions": ["How did you test your API?"],
            }
            mode = {"status": 200, "code": "", "abort": False, "hold": True}
            requests: list[dict[str, str]] = []
            pending = []

            def mock_analysis(route) -> None:
                requests.append(route.request.post_data_json)
                if mode["hold"]:
                    pending.append(route)
                    return
                if mode["abort"]:
                    route.abort("failed")
                else:
                    body = result if mode["status"] == 200 else {"code": mode["code"], "message": "safe error"}
                    route.fulfill(status=mode["status"], content_type="application/json", body=json.dumps(body))

            page.route("**/api/v1/analyze", mock_analysis)
            page.goto(base)
            page.get_by_role("button", name="Analyze match").click()
            expect(page.locator("#resume-error")).to_contain_text("at least 50")
            assert not requests
            page.get_by_role("button", name="Load sample").click()
            expect(page.locator("#status")).to_contain_text("Fictional samples loaded")
            resume = page.locator("#resume").input_value()
            assert resume == (root / "data/sample_resume.txt").read_text(encoding="utf-8")
            assert page.locator("#job_description").input_value() == (root / "data/sample_job_description.txt").read_text(encoding="utf-8")
            # Queue duplicate submits before fetch completes; only one should be sent.
            page.locator("#analysis-form").evaluate("form => { form.requestSubmit(); form.requestSubmit(); }")
            expect(page.locator("#analyze")).to_be_disabled()
            expect(page.locator("#spinner")).to_be_visible()
            # Let the intercepted request arrive while deliberately withholding its response.
            page.wait_for_timeout(100)
            assert len(pending) == 1
            pending[0].fulfill(status=200, content_type="application/json", body=json.dumps(result))
            mode["hold"] = False
            expect(page.locator("#results")).to_be_visible()
            expect(page.locator("#score")).to_have_text("82")
            assert len(requests) == 1
            assert set(requests[0]) == {"resume", "job_description"}
            expect(page.locator("#matching_skills")).to_contain_text("<img src=x onerror=alert(1)>")
            assert page.locator("#matching_skills img").count() == 0
            expect(page.locator("#missing_skills")).to_contain_text("No items identified")
            for status, code, message in (
                (422, "invalid_request", "Please check both documents"),
                (502, "provider_error", "could not complete"),
                (502, "invalid_ai_response", "unexpected format"),
                (502, "provider_network_error", "could not reach"),
                (504, "provider_timeout", "too long"),
                (503, "ai_not_configured", "not configured"),
            ):
                mode.update(status=status, code=code, abort=False)
                page.get_by_role("button", name="Analyze match").click()
                expect(page.locator("#error")).to_contain_text(message)
                assert page.locator("#resume").input_value() == resume
                expect(page.locator("#results")).to_be_hidden()
            mode["abort"] = True
            page.get_by_role("button", name="Analyze match").click()
            expect(page.locator("#error")).to_contain_text("Couldn’t connect")
            page.locator("#resume").fill("a" * 20001)
            page.get_by_role("button", name="Analyze match").click()
            expect(page.locator("#resume-error")).to_contain_text("20,000")
            page.locator("#resume").fill("1" * 60)
            page.get_by_role("button", name="Analyze match").click()
            expect(page.locator("#resume-error")).to_contain_text("20 letters")
            page.get_by_role("button", name="Load sample").click()
            expect(page.locator("#status")).to_contain_text("Fictional samples loaded")
            desktop = page.locator("#job_description").bounding_box()
            assert desktop["x"] > page.locator("#resume").bounding_box()["x"]
            artifact_dir = root / ".ui-checks"
            artifact_dir.mkdir(exist_ok=True)
            page.screenshot(path=str(artifact_dir / "desktop.png"), full_page=True)
            for width in (390, 320):
                page.set_viewport_size({"width": width, "height": 844})
                boxes = [page.locator("#" + name).bounding_box() for name in ("resume", "job_description")]
                assert boxes[1]["y"] > boxes[0]["y"] + boxes[0]["height"]
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            page.set_viewport_size({"width": 390, "height": 844})
            mode.update(status=200, abort=False)
            page.get_by_role("button", name="Analyze match").click()
            expect(page.locator("#results")).to_be_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            page.screenshot(path=str(artifact_dir / "mobile.png"), full_page=True)
            page.get_by_role("button", name="Clear", exact=True).click()
            expect(page.locator("#resume")).to_have_value("")
            expect(page.locator("#resume-count")).to_have_text("0 / 20,000")
            expect(page.locator("#resume")).to_be_focused()
            assert not errors, errors
            browser.close()
            print("UI checks passed: mocked success, safe text, empty lists, validation, provider errors, timeout, connection failure, duplicate prevention, samples, clear, focus, desktop and mobile (390/320 px). No live Gemini calls.")
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


if __name__ == "__main__":
    main()
