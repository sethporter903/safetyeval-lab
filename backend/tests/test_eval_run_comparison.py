from fastapi.testclient import TestClient

from app.main import app


def test_compares_two_eval_runs() -> None:
    with TestClient(app) as client:
        first = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "jailbreak_basic",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 2,
            },
        ).json()
        second = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "policy_compliance",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 2,
            },
        ).json()

        response = client.post(
            "/api/eval-runs/compare",
            json={"run_ids": [first["run_id"], second["run_id"]]},
        )

    assert response.status_code == 200
    payload = response.json()
    assert [run["run_id"] for run in payload["runs"]] == [first["run_id"], second["run_id"]]
    assert all("pass_rate" in run for run in payload["runs"])
    assert all("unsafe_rate" in run for run in payload["runs"])
    assert all("average_risk_score" in run for run in payload["runs"])
    categories = {item["category"] for item in payload["category_breakdown"]}
    assert categories == {"jailbreak", "policy_compliance"}


def test_compare_requires_two_runs() -> None:
    with TestClient(app) as client:
        response = client.post("/api/eval-runs/compare", json={"run_ids": [1]})

    assert response.status_code == 422


def test_compare_missing_run_returns_404() -> None:
    with TestClient(app) as client:
        response = client.post("/api/eval-runs/compare", json={"run_ids": [1, 999999]})

    assert response.status_code == 404
