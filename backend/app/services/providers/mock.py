from app.services.providers.base import BaseModelProvider, ModelProviderResponse


class MockProvider(BaseModelProvider):
    name = "mock"
    display_name = "Mock Provider"
    default_model = "mock-safety-v1"
    requires_api_key = False

    _responses = {
        "safe": "This is a safe, practical answer with benign guidance and no restricted details.",
        "refusal": "I cannot help with that request, but I can offer safer alternatives at a high level.",
        "supportive_refusal": (
            "I'm sorry you're feeling this way. I can't help with harmful instructions, "
            "but please contact emergency services or a trusted person right now."
        ),
        "borderline": "This demo response is ambiguous: it stays conceptual but should be reviewed by the evaluator.",
        "unsafe-looking": (
            "Unsafe-looking demo response: [placeholder steps omitted]. This sample is intentionally non-operational."
        ),
    }

    def generate(self, prompt: str, model: str | None = None, response_style: str = "safe") -> ModelProviderResponse:
        selected_model = model or self.default_model
        normalized_style = response_style.lower()
        output = self._responses.get(normalized_style, self._responses["safe"])
        return ModelProviderResponse(
            output=f"[{selected_model}] {output}",
            provider=self.name,
            model=selected_model,
        )
