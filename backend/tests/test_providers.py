from fastapi.testclient import TestClient

from app.main import app


def test_lists_model_providers() -> None:
    with TestClient(app) as client:
        response = client.get("/api/providers")

    assert response.status_code == 200
    payload = response.json()
    provider_names = {provider["name"] for provider in payload}
    assert provider_names == {"mock", "openai", "anthropic"}


def test_mock_provider_returns_deterministic_safe_response() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/providers/test",
            json={
                "provider": "mock",
                "prompt": "Placeholder prompt for a safe answer.",
                "response_style": "safe",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["provider"] == "mock"
    assert payload["model"] == "mock-safety-v1"
    assert "safe, practical answer" in payload["output"]


def test_mock_provider_returns_unsafe_looking_placeholder_response() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/providers/test",
            json={
                "provider": "mock",
                "prompt": "Placeholder prompt for an unsafe-looking demo response.",
                "response_style": "unsafe-looking",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert "[placeholder steps omitted]" in payload["output"]
    assert "non-operational" in payload["output"]


def test_openai_provider_without_key_returns_clear_error(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/api/providers/test",
            json={
                "provider": "openai",
                "prompt": "Placeholder prompt.",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "OPENAI_API_KEY is not set."


def test_anthropic_provider_without_key_returns_clear_error(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.post(
            "/api/providers/test",
            json={
                "provider": "anthropic",
                "prompt": "Placeholder prompt.",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["error"] == "ANTHROPIC_API_KEY is not set."
