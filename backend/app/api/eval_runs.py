from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.eval_runs import (
    EvalResultDetail,
    EvalRunCompareCreate,
    EvalRunComparisonRead,
    EvalRunDetail,
    EvalRunScoreSummary,
    FileEvalRunCreate,
    FileEvalRunSummary,
)
from app.services.comparison import compare_eval_runs
from app.services.eval_run_executor import EvalSuiteNotFoundError, execute_file_eval_run
from app.services.providers import ModelProviderError, ProviderConfigurationError
from app.services.reporting import build_eval_run_markdown_report
from app.services.scoring import EvalRunNotFoundError, get_eval_run_detail, get_eval_run_results, score_eval_run

router = APIRouter(prefix="/eval-runs", tags=["eval runs"])


@router.post("", response_model=FileEvalRunSummary, status_code=status.HTTP_201_CREATED)
def create_eval_run(payload: FileEvalRunCreate, db: Session = Depends(get_db)) -> FileEvalRunSummary:
    try:
        return execute_file_eval_run(db, payload)
    except EvalSuiteNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (ModelProviderError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/compare", response_model=EvalRunComparisonRead)
def compare_runs(payload: EvalRunCompareCreate, db: Session = Depends(get_db)) -> EvalRunComparisonRead:
    try:
        return compare_eval_runs(db, payload)
    except EvalRunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{run_id}", response_model=EvalRunDetail)
def get_eval_run(run_id: int, db: Session = Depends(get_db)) -> EvalRunDetail:
    try:
        return get_eval_run_detail(db, run_id)
    except EvalRunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{run_id}/results", response_model=list[EvalResultDetail])
def get_eval_run_result_details(run_id: int, db: Session = Depends(get_db)) -> list[EvalResultDetail]:
    try:
        return get_eval_run_results(db, run_id)
    except EvalRunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{run_id}/summary", response_model=EvalRunScoreSummary)
def get_eval_run_score_summary(run_id: int, db: Session = Depends(get_db)) -> EvalRunScoreSummary:
    try:
        return score_eval_run(db, run_id)
    except EvalRunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{run_id}/report.md", response_class=Response)
def get_eval_run_markdown_report(run_id: int, db: Session = Depends(get_db)) -> Response:
    try:
        report = build_eval_run_markdown_report(db, run_id)
    except EvalRunNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(
        content=report,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="safetyeval-run-{run_id}-report.md"'},
    )
