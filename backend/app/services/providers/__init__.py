from app.models.entities import EvalCase, ModelProvider
from app.services.providers.base import (
    BaseModelProvider,
    ModelProviderError,
    ModelProviderResponse,
    ProviderConfigurationError,
    ProviderTestRequest,
)
from app.services.providers.registry import get_provider, list_providers


def get_provider_client(provider: ModelProvider) -> BaseModelProvider:
    return get_provider(provider.provider_type)


def generate_for_eval_case(
    provider: BaseModelProvider,
    case: EvalCase,
    model_name: str,
) -> ModelProviderResponse:
    response_style = _response_style_for_expected_behavior(case.expected_behavior)
    return provider.generate(
        prompt=case.prompt,
        model=model_name,
        response_style=response_style,
    )


def _response_style_for_expected_behavior(expected_behavior: str) -> str:
    normalized = expected_behavior.lower()
    if normalized == "answer":
        return "safe"
    if normalized == "supportive_refusal":
        return "supportive_refusal"
    if normalized in {"refuse", "refuse_and_redirect"}:
        return "refusal"
    return "borderline"


__all__ = [
    "BaseModelProvider",
    "ModelProviderError",
    "ModelProviderResponse",
    "ProviderConfigurationError",
    "ProviderTestRequest",
    "generate_for_eval_case",
    "get_provider",
    "get_provider_client",
    "list_providers",
]
