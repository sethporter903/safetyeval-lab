from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import EvalCase, EvalResult, EvalRun, EvalSuite, ModelProvider
from app.schemas.eval_runs import FileEvalRunCreate, FileEvalRunSummary
from app.schemas.eval_suites import FileEvalCase, FileEvalSuiteRead
from app.services.eval_suite_files import get_file_eval_suite
from app.services.evaluator import grade_safety_response
from app.services.llm_judge import grade_with_optional_llm_judge
from app.services.providers import BaseModelProvider, ModelProviderError, ProviderConfigurationError, get_provider


class EvalRunExecutionError(Exception):
    pass


class EvalSuiteNotFoundError(EvalRunExecutionError):
    pass


def execute_file_eval_run(db: Session, request: FileEvalRunCreate) -> FileEvalRunSummary:
    suite = get_file_eval_suite(request.suite_name)
    if suite is None:
        raise EvalSuiteNotFoundError(f"Eval suite '{request.suite_name}' was not found.")

    selected_cases = suite.cases[: request.max_cases] if request.max_cases else suite.cases
    provider = get_provider(request.provider)
    model_name = request.model or provider.default_model

    db_suite = _ensure_db_suite(db, suite)
    db_provider = _ensure_db_provider(db, provider)
    db_cases = [_ensure_db_case(db, db_suite, file_case) for file_case in selected_cases]

    run = EvalRun(
        suite_id=db_suite.id,
        provider_id=db_provider.id,
        model_name=model_name,
        status="running",
        total_cases=len(db_cases),
    )
    db.add(run)
    db.flush()

    passed_cases = 0
    try:
        for file_case, db_case in zip(selected_cases, db_cases, strict=True):
            response = provider.generate(
                prompt=file_case.prompt,
                model=model_name,
                response_style=_response_style_for_case(file_case),
            )
            rule_grade = grade_safety_response(
                prompt=file_case.prompt,
                output=response.output,
                expected_behavior=file_case.expected_behavior,
            )
            final_grade = grade_with_optional_llm_judge(
                provider=provider,
                model=model_name,
                case=file_case,
                model_response=response.output,
                rule_grade=rule_grade,
                enabled=settings.llm_judge_enabled,
            )
            verdict = "pass" if final_grade.passed else "fail"
            score = 1.0 if final_grade.passed else 0.0
            rationale = (
                f"Rule grader: {rule_grade.rationale} "
                f"safety_label={rule_grade.safety_label}; risk_score={rule_grade.risk_score}; "
                f"refusal_detected={rule_grade.refusal_detected}; "
                f"safe_alternative_detected={rule_grade.safe_alternative_detected}. "
                f"LLM judge: {final_grade.rationale} "
                f"judge_score={final_grade.score}; fallback_used={final_grade.fallback_used}."
            )
            if verdict == "pass":
                passed_cases += 1

            db.add(
                EvalResult(
                    run_id=run.id,
                    case_id=db_case.id,
                    output=response.output,
                    verdict=verdict,
                    score=score,
                    rationale=rationale,
                )
            )
    except (ModelProviderError, ProviderConfigurationError):
        run.status = "failed"
        db.commit()
        raise

    run.status = "completed"
    run.passed_cases = passed_cases
    run.pass_rate = passed_cases / run.total_cases if run.total_cases else 0.0
    db.commit()
    db.refresh(run)

    return FileEvalRunSummary(
        run_id=run.id,
        suite_name=suite.name,
        provider=provider.name,
        model=model_name,
        status=run.status,
        total_cases=run.total_cases,
        passed_cases=run.passed_cases,
        failed_cases=run.total_cases - run.passed_cases,
        pass_rate=run.pass_rate,
    )


def _ensure_db_suite(db: Session, suite: FileEvalSuiteRead) -> EvalSuite:
    db_suite = db.scalar(select(EvalSuite).where(EvalSuite.name == suite.name))
    if db_suite is not None:
        return db_suite

    db_suite = EvalSuite(
        name=suite.name,
        description=f"File-backed eval suite loaded from {suite.name}.jsonl.",
        policy_version="jsonl-v1",
    )
    db.add(db_suite)
    db.flush()
    return db_suite


def _ensure_db_provider(db: Session, provider: BaseModelProvider) -> ModelProvider:
    db_provider = db.scalar(select(ModelProvider).where(ModelProvider.provider_type == provider.name))
    if db_provider is not None:
        return db_provider

    db_provider = ModelProvider(
        name=provider.display_name,
        provider_type=provider.name,
        base_url=None,
        is_active=True,
    )
    db.add(db_provider)
    db.flush()
    return db_provider


def _ensure_db_case(db: Session, suite: EvalSuite, file_case: FileEvalCase) -> EvalCase:
    db_case = db.scalar(
        select(EvalCase).where(
            EvalCase.suite_id == suite.id,
            EvalCase.title == file_case.id,
        )
    )
    if db_case is None:
        db_case = EvalCase(
            suite_id=suite.id,
            title=file_case.id,
            prompt=file_case.prompt,
            category=file_case.category,
            expected_behavior=file_case.expected_behavior,
            severity=file_case.severity,
        )
        db.add(db_case)
        db.flush()
        return db_case

    db_case.prompt = file_case.prompt
    db_case.category = file_case.category
    db_case.expected_behavior = file_case.expected_behavior
    db_case.severity = file_case.severity
    db.flush()
    return db_case


def _response_style_for_case(case: FileEvalCase) -> str:
    if case.expected_behavior == "answer_safely":
        return "safe"
    if case.expected_behavior == "refuse_and_redirect":
        return "refusal"
    return "borderline"
