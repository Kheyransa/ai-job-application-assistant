from pathlib import Path


def test_interface_and_static_assets(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Job Application Assistant" in response.text
    assert 'id="resume"' in response.text
    for asset in ("/static/styles.css", "/static/app.js"):
        assert client.get(asset).status_code == 200


def test_samples_match_project_files(client):
    response = client.get("/ui/samples")
    assert response.status_code == 200
    root = Path(__file__).resolve().parents[1]
    assert response.json() == {
        "resume": (root / "data/sample_resume.txt").read_text(encoding="utf-8"),
        "job_description": (root / "data/sample_job_description.txt").read_text(encoding="utf-8"),
    }


def test_configuration_is_not_served(client):
    for path in ("/.env", "/static/.env", "/static/../.env", "/data/../.env"):
        assert client.get(path).status_code == 404
