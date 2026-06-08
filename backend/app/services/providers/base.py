from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProviderResponse:
    output: str
    provider: str
    model: str


@dataclass(frozen=True)
class ProviderTestRequest:
    prompt: str
    model: str | None = None
    response_style: str = "safe"


class ModelProviderError(Exception):
    pass


class ProviderConfigurationError(ModelProviderError):
    pass


class BaseModelProvider(ABC):
    name: str
    display_name: str
    default_model: str
    requires_api_key: bool

    @abstractmethod
    def generate(self, prompt: str, model: str | None = None, response_style: str = "safe") -> ModelProviderResponse:
        raise NotImplementedError

    def metadata(self) -> dict[str, str | bool]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "default_model": self.default_model,
            "requires_api_key": self.requires_api_key,
        }
