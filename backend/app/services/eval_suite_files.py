import json
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.schemas.eval_suites import FileEvalCase, FileEvalSuiteRead, FileEvalSuiteSummary

EVAL_SUITES_DIR = Path(__file__).resolve().parents[1] / "data" / "eval_suites"


def list_file_eval_suites() -> list[FileEvalSuiteSummary]:
    return [summarize_suite(path) for path in sorted(EVAL_SUITES_DIR.glob("*.jsonl"))]


def get_file_eval_suite(suite_name: str) -> FileEvalSuiteRead | None:
    path = _suite_path(suite_name)
    if path is None:
        return None

    cases = _read_cases(path)
    return FileEvalSuiteRead(
        name=path.stem,
        case_count=len(cases),
        categories=sorted({case.category for case in cases}),
        severities=sorted({case.severity for case in cases}),
        cases=cases,
    )


def summarize_suite(path: Path) -> FileEvalSuiteSummary:
    cases = _read_cases(path)
    return FileEvalSuiteSummary(
        name=path.stem,
        case_count=len(cases),
        categories=sorted({case.category for case in cases}),
        severities=sorted({case.severity for case in cases}),
    )


def _suite_path(suite_name: str) -> Path | None:
    clean_name = Path(suite_name).name
    candidate_name = clean_name if clean_name.endswith(".jsonl") else f"{clean_name}.jsonl"
    candidate = EVAL_SUITES_DIR / candidate_name
    if not candidate.is_file() or candidate.parent != EVAL_SUITES_DIR:
        return None
    return candidate


def _read_cases(path: Path) -> list[FileEvalCase]:
    cases: list[FileEvalCase] = []
    with path.open(encoding="utf-8") as suite_file:
        for line_number, line in enumerate(suite_file, start=1):
            if not line.strip():
                continue
            cases.append(_parse_case(path, line_number, line))
    return cases


def _parse_case(path: Path, line_number: int, line: str) -> FileEvalCase:
    try:
        payload: dict[str, Any] = json.loads(line)
        return FileEvalCase.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValueError(f"Invalid eval case in {path.name} on line {line_number}") from exc
