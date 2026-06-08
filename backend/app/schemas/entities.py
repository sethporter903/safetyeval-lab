from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvalCaseBase(BaseModel):
    title: str
    prompt: str
    category: str
    expected_behavior: str
    severity: str = "medium"


class EvalCaseCreate(EvalCaseBase):
    pass


class EvalCaseRead(EvalCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suite_id: int
    created_at: datetime


class EvalSuiteCreate(BaseModel):
    name: str
    description: str | None = None
    policy_version: str = "starter-v1"


class EvalSuiteRead(EvalSuiteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    cases: list[EvalCaseRead] = []


class ModelProviderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    provider_type: str
    base_url: str | None
    is_active: bool


class EvalRunCreate(BaseModel):
    suite_id: int
    provider_id: int
    model_name: str = "mock-safety-v1"


class EvalResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    output: str
    verdict: str
    score: float
    rationale: str
    created_at: datetime


class EvalRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    suite_id: int
    provider_id: int
    model_name: str
    status: str
    pass_rate: float
    total_cases: int
    passed_cases: int
    created_at: datetime
    results: list[EvalResultRead] = []


class SummaryRead(BaseModel):
    suite_count: int
    case_count: int
    run_count: int
    provider_count: int
    latest_pass_rate: float

