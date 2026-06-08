from pydantic import BaseModel, Field


class ProviderRead(BaseModel):
    name: str
    display_name: str
    default_model: str
    requires_api_key: bool


class ProviderTestCreate(BaseModel):
    provider: str = "mock"
    prompt: str = "Provide a safe response to this placeholder evaluation prompt."
    model: str | None = None
    response_style: str = Field(default="safe", pattern="^(safe|refusal|supportive_refusal|borderline|unsafe-looking)$")


class ProviderTestRead(BaseModel):
    provider: str
    model: str | None
    ok: bool
    output: str | None = None
    error: str | None = None
