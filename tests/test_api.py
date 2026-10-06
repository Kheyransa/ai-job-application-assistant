def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analysis(client, payload, analysis_data, ai_mock):
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 200
    assert response.json() == analysis_data
    ai_mock.analyze_resume.assert_awaited_once()


def test_invalid_request(client, payload, ai_mock):
    payload["resume"] = "private-invalid-value"
    response = client.post("/api/v1/analyze", json=payload)
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"
    assert payload["resume"] not in response.text
    ai_mock.analyze_resume.assert_not_awaited()


def test_documentation_and_registration(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/analyze"]["post"]
    assert "200" in operation["responses"]
    assert "422" in operation["responses"]
    assert "AnalysisResponse" in schema["components"]["schemas"]


def test_malformed_json(client):
    response = client.post("/api/v1/analyze", content="{", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_request"
