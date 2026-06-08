from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.eval_runs import EvalResultReviewRead, EvalResultReviewUpdate
from app.services.reviews import EvalResultNotFoundError, review_eval_result

router = APIRouter(prefix="/eval-results", tags=["eval results"])


@router.patch("/{result_id}/review", response_model=EvalResultReviewRead)
def update_eval_result_review(
    result_id: int,
    payload: EvalResultReviewUpdate,
    db: Session = Depends(get_db),
) -> EvalResultReviewRead:
    try:
        return review_eval_result(db, result_id, payload)
    except EvalResultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
