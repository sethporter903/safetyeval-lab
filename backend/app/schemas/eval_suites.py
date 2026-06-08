from pydantic import BaseModel, ConfigDict


class FileEvalCase(BaseModel):
    id: str
    category: str
    prompt: str
    expected_behavior: str
    severity: str
    tags: list[str]


class FileEvalSuiteSummary(BaseModel):
    name: str
    case_count: int
    categories: list[str]
    severities: list[str]


class FileEvalSuiteRead(FileEvalSuiteSummary):
    model_config = ConfigDict(from_attributes=True)

    cases: list[FileEvalCase]
