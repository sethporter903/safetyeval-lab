from fastapi.testclient import TestClient

from app.main import app


def test_reviews_eval_result_and_returns_review_state() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "jailbreak_basic",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 1,
            },
        )
        run_id = create_response.json()["run_id"]
        result = client.get(f"/api/eval-runs/{run_id}/results").json()[0]

        review_response = client.patch(
            f"/api/eval-results/{result['result_id']}/review",
            json={
                "review_status": "review",
                "reviewer_notes": "Needs policy-owner review before inclusion in a release gate.",
            },
        )
        updated_result = client.get(f"/api/eval-runs/{run_id}/results").json()[0]

    assert review_response.status_code == 200
    review_payload = review_response.json()
    assert review_payload["result_id"] == result["result_id"]
    assert review_payload["review_status"] == "review"
    assert review_payload["reviewer_notes"] == "Needs policy-owner review before inclusion in a release gate."
    assert review_payload["reviewed_at"]

    assert updated_result["review_status"] == "review"
    assert updated_result["reviewer_notes"] == "Needs policy-owner review before inclusion in a release gate."
    assert updated_result["reviewed_at"]


def test_review_endpoint_validates_status() -> None:
    with TestClient(app) as client:
        response = client.patch(
            "/api/eval-results/1/review",
            json={"review_status": "maybe", "reviewer_notes": ""},
        )

    assert response.status_code == 422


def test_review_missing_result_returns_404() -> None:
    with TestClient(app) as client:
        response = client.patch(
            "/api/eval-results/999999/review",
            json={"review_status": "fail", "reviewer_notes": "Not acceptable."},
        )

    assert response.status_code == 404
