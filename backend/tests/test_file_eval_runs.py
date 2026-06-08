from fastapi.testclient import TestClient

from app.main import app


def test_executes_file_eval_run_with_mock_provider() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "jailbreak_basic",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 2,
            },
        )

        assert response.status_code == 201
        payload = response.json()
        assert payload["suite_name"] == "jailbreak_basic"
        assert payload["provider"] == "mock"
        assert payload["status"] == "completed"
        assert payload["total_cases"] == 2
        assert payload["passed_cases"] == 2
        assert payload["failed_cases"] == 0
        assert payload["pass_rate"] == 1.0

        run_response = client.get(f"/api/v1/runs/{payload['run_id']}")

    assert run_response.status_code == 200
    run_payload = run_response.json()
    assert run_payload["total_cases"] == 2
    assert len(run_payload["results"]) == 2
    assert all(result["output"] for result in run_payload["results"])


def test_executes_answer_safely_file_eval_run() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "policy_compliance.jsonl",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 1,
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert payload["total_cases"] == 1
    assert payload["passed_cases"] == 1


def test_file_eval_run_missing_suite_returns_404() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "missing_suite",
                "provider": "mock",
                "model": "mock-safety-v1",
            },
        )

    assert response.status_code == 404


def test_file_eval_run_missing_provider_key_returns_clear_error(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "policy_compliance",
                "provider": "openai",
                "model": "gpt-4o-mini",
                "max_cases": 1,
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "OPENAI_API_KEY is not set."


def test_get_file_eval_run_detail_results_and_summary() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "jailbreak_basic",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 2,
            },
        )
        run_id = create_response.json()["run_id"]

        detail_response = client.get(f"/api/eval-runs/{run_id}")
        results_response = client.get(f"/api/eval-runs/{run_id}/results")
        summary_response = client.get(f"/api/eval-runs/{run_id}/summary")

    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["run_id"] == run_id
    assert detail["suite_name"] == "jailbreak_basic"
    assert detail["total_cases"] == 2
    assert detail["passed_cases"] == 2

    assert results_response.status_code == 200
    results = results_response.json()
    assert len(results) == 2
    assert all(result["safety_label"] == "safe" for result in results)
    assert all("risk_score" in result for result in results)
    assert all(result["refusal_detected"] is True for result in results)
    assert all(result["safe_alternative_detected"] is True for result in results)

    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["run_id"] == run_id
    assert summary["total_cases"] == 2
    assert summary["pass_rate"] == 1.0
    assert summary["unsafe_rate"] == 0.0
    assert summary["borderline_rate"] == 0.0
    assert summary["average_risk_score"] >= 0
    assert summary["severity_weighted_risk_score"] >= 0
    assert summary["failure_rate_by_category"] == {"jailbreak": 0.0}
    assert summary["refusal_quality_score"] > 0
    assert summary["top_failed_cases"] == []


def test_eval_run_scoring_endpoints_return_404_for_missing_run() -> None:
    with TestClient(app) as client:
        detail_response = client.get("/api/eval-runs/999999")
        results_response = client.get("/api/eval-runs/999999/results")
        summary_response = client.get("/api/eval-runs/999999/summary")

    assert detail_response.status_code == 404
    assert results_response.status_code == 404
    assert summary_response.status_code == 404


def test_get_eval_run_markdown_report() -> None:
    with TestClient(app) as client:
        create_response = client.post(
            "/api/eval-runs",
            json={
                "suite_name": "jailbreak_basic",
                "provider": "mock",
                "model": "mock-safety-v1",
                "max_cases": 2,
            },
        )
        run_id = create_response.json()["run_id"]

        response = client.get(f"/api/eval-runs/{run_id}/report.md")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/markdown")
    assert f"safetyeval-run-{run_id}-report.md" in response.headers["content-disposition"]
    report = response.text
    for section in [
        "## Executive Summary",
        "## Methodology",
        "## Eval Suite",
        "## Model Tested",
        "## Key Metrics",
        "## Category Breakdown",
        "## High-Risk Findings",
        "## Example Failures",
        "## Limitations",
        "## Recommendations",
    ]:
        assert section in report
    assert "mock-safety-v1" in report
    assert "jailbreak_basic" in report


def test_eval_run_markdown_report_returns_404_for_missing_run() -> None:
    with TestClient(app) as client:
        response = client.get("/api/eval-runs/999999/report.md")

    assert response.status_code == 404
