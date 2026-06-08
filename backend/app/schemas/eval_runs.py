from pydantic import BaseModel, Field


class FileEvalRunCreate(BaseModel):
    suite_name: str
    provider: str = "mock"
    model: str | None = None
    max_cases: int | None = Field(default=None, gt=0)


class FileEvalRunSummary(BaseModel):
    run_id: int
    suite_name: str
    provider: str
    model: str
    status: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float


class EvalRunDetail(BaseModel):
    run_id: int
    suite_name: str
    provider: str
    model: str
    status: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    created_at: str


class EvalResultDetail(BaseModel):
    result_id: int
    case_id: int
    case_title: str
    category: str
    severity: str
    prompt: str
    expected_behavior: str
    model_response: str
    verdict: str
    score: float
    safety_label: str
    risk_score: int
    refusal_detected: bool
    safe_alternative_detected: bool
    rationale: str
    review_status: str
    reviewer_notes: str
    reviewed_at: str | None


class EvalResultReviewUpdate(BaseModel):
    review_status: str = Field(pattern="^(pass|review|fail)$")
    reviewer_notes: str = ""


class EvalResultReviewRead(BaseModel):
    result_id: int
    review_status: str
    reviewer_notes: str
    reviewed_at: str


class FailedCaseSummary(BaseModel):
    result_id: int
    case_id: int
    case_title: str
    category: str
    severity: str
    safety_label: str
    risk_score: int
    rationale: str


class EvalRunScoreSummary(BaseModel):
    run_id: int
    total_cases: int
    pass_rate: float
    unsafe_rate: float
    borderline_rate: float
    average_risk_score: float
    severity_weighted_risk_score: float
    failure_rate_by_category: dict[str, float]
    refusal_quality_score: float
    top_failed_cases: list[FailedCaseSummary]


class EvalRunCompareCreate(BaseModel):
    run_ids: list[int] = Field(min_length=2)


class EvalRunComparisonItem(BaseModel):
    run_id: int
    suite_name: str
    provider: str
    model: str
    status: str
    total_cases: int
    pass_rate: float
    unsafe_rate: float
    average_risk_score: float
    failure_rate_by_category: dict[str, float]


class EvalRunCategoryComparison(BaseModel):
    category: str
    failure_rates: dict[str, float]


class EvalRunComparisonRead(BaseModel):
    runs: list[EvalRunComparisonItem]
    category_breakdown: list[EvalRunCategoryComparison]
