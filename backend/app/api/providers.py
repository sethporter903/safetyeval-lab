from fastapi import APIRouter

from app.schemas.providers import ProviderRead, ProviderTestCreate, ProviderTestRead
from app.services.providers import ModelProviderError, ProviderConfigurationError, get_provider, list_providers

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("", response_model=list[ProviderRead])
def get_providers() -> list[ProviderRead]:
    return [ProviderRead(**provider.metadata()) for provider in list_providers()]


@router.post("/test", response_model=ProviderTestRead)
def test_provider(payload: ProviderTestCreate) -> ProviderTestRead:
    try:
        provider = get_provider(payload.provider)
        response = provider.generate(
            prompt=payload.prompt,
            model=payload.model,
            response_style=payload.response_style,
        )
    except (ProviderConfigurationError, ModelProviderError, ValueError) as exc:
        return ProviderTestRead(
            provider=payload.provider,
            model=payload.model,
            ok=False,
            error=str(exc),
        )

    return ProviderTestRead(
        provider=response.provider,
        model=response.model,
        ok=True,
        output=response.output,
    )
