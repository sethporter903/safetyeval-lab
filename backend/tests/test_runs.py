from fastapi.testclient import TestClient

from app.main import app


def test_mock_eval_run_completes() -> None:
    with TestClient(app) as client:
        providers = client.get("/api/v1/providers").json()
        suites = client.get("/api/v1/suites").json()
        starter_suite = next(suite for suite in suites if suite["name"] == "Starter Safety Smoke Suite")

        response = client.post(
            "/api/v1/runs",
            json={
                "suite_id": starter_suite["id"],
                "provider_id": providers[0]["id"],
                "model_name": "mock-safety-v1",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["total_cases"] == 3
    assert payload["passed_cases"] == 3
