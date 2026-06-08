from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.entities import EvalResult
from app.schemas.eval_runs import EvalResultReviewRead, EvalResultReviewUpdate


class EvalResultNotFoundError(Exception):
    pass


def review_eval_result(db: Session, result_id: int, payload: EvalResultReviewUpdate) -> EvalResultReviewRead:
    result = db.get(EvalResult, result_id)
    if result is None:
        raise EvalResultNotFoundError(f"Eval result {result_id} was not found.")

    result.review_status = payload.review_status
    result.reviewer_notes = payload.reviewer_notes
    result.reviewed_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(result)

    return EvalResultReviewRead(
        result_id=result.id,
        review_status=result.review_status,
        reviewer_notes=result.reviewer_notes or "",
        reviewed_at=result.reviewed_at.isoformat(),
    )
