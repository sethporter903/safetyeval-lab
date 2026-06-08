from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import EvalResult, EvalRun, EvalSuite, ModelProvider
from app.services.evaluator import evaluate_output
from app.services.providers import generate_for_eval_case, get_provider_client


def create_eval_run(db: Session, suite_id: int, provider_id: int, model_name: str) -> EvalRun:
    suite = db.scalar(select(EvalSuite).where(EvalSuite.id == suite_id).options(selectinload(EvalSuite.cases)))
    if suite is None:
        raise ValueError("Eval suite not found")

    provider = db.get(ModelProvider, provider_id)
    if provider is None or not provider.is_active:
        raise ValueError("Active model provider not found")

    run = EvalRun(
        suite_id=suite.id,
        provider_id=provider.id,
        model_name=model_name,
        status="running",
        total_cases=len(suite.cases),
    )
    db.add(run)
    db.flush()

    client = get_provider_client(provider)
    passed_cases = 0

    for case in suite.cases:
        response = generate_for_eval_case(client, case, model_name)
        verdict, score, rationale = evaluate_output(case, response.output)
        if verdict == "pass":
            passed_cases += 1
        db.add(
            EvalResult(
                run_id=run.id,
                case_id=case.id,
                output=response.output,
                verdict=verdict,
                score=score,
                rationale=rationale,
            )
        )

    run.status = "completed"
    run.passed_cases = passed_cases
    run.pass_rate = passed_cases / run.total_cases if run.total_cases else 0.0
    db.commit()
    db.refresh(run)
    return run
