from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.base import BaseModelProvider
from app.services.providers.mock import MockProvider
from app.services.providers.openai_provider import OpenAIProvider

_PROVIDERS: dict[str, type[BaseModelProvider]] = {
    MockProvider.name: MockProvider,
    OpenAIProvider.name: OpenAIProvider,
    AnthropicProvider.name: AnthropicProvider,
}


def list_providers() -> list[BaseModelProvider]:
    return [provider_class() for provider_class in _PROVIDERS.values()]


def get_provider(provider_name: str) -> BaseModelProvider:
    provider_class = _PROVIDERS.get(provider_name.lower())
    if provider_class is None:
        supported = ", ".join(sorted(_PROVIDERS))
        raise ValueError(f"Unsupported provider '{provider_name}'. Supported providers: {supported}.")
    return provider_class()
