from sqlalchemy.orm import Session

from app.schemas.eval_runs import (
    EvalRunCategoryComparison,
    EvalRunCompareCreate,
    EvalRunComparisonItem,
    EvalRunComparisonRead,
)
from app.services.scoring import get_eval_run_detail, score_eval_run


def compare_eval_runs(db: Session, payload: EvalRunCompareCreate) -> EvalRunComparisonRead:
    run_items: list[EvalRunComparisonItem] = []
    all_categories: set[str] = set()

    for run_id in payload.run_ids:
        detail = get_eval_run_detail(db, run_id)
        summary = score_eval_run(db, run_id)
        all_categories.update(summary.failure_rate_by_category)
        run_items.append(
            EvalRunComparisonItem(
                run_id=detail.run_id,
                suite_name=detail.suite_name,
                provider=detail.provider,
                model=detail.model,
                status=detail.status,
                total_cases=summary.total_cases,
                pass_rate=summary.pass_rate,
                unsafe_rate=summary.unsafe_rate,
                average_risk_score=summary.average_risk_score,
                failure_rate_by_category=summary.failure_rate_by_category,
            )
        )

    category_breakdown = [
        EvalRunCategoryComparison(
            category=category,
            failure_rates={
                str(item.run_id): item.failure_rate_by_category.get(category, 0.0)
                for item in run_items
            },
        )
        for category in sorted(all_categories)
    ]

    return EvalRunComparisonRead(runs=run_items, category_breakdown=category_breakdown)
