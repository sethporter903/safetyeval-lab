from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models.entities import EvalCase, EvalRun, EvalSuite, ModelProvider
from app.schemas.entities import (
    EvalCaseCreate,
    EvalCaseRead,
    EvalRunCreate,
    EvalRunRead,
    EvalSuiteCreate,
    EvalSuiteRead,
    ModelProviderRead,
    SummaryRead,
)
from app.services.runs import create_eval_run

router = APIRouter()


@router.get("/summary", response_model=SummaryRead)
def get_summary(db: Session = Depends(get_db)) -> SummaryRead:
    suite_count = db.scalar(select(func.count(EvalSuite.id))) or 0
    case_count = db.scalar(select(func.count(EvalCase.id))) or 0
    run_count = db.scalar(select(func.count(EvalRun.id))) or 0
    provider_count = db.scalar(select(func.count(ModelProvider.id))) or 0
    latest_run = db.scalar(select(EvalRun).order_by(EvalRun.created_at.desc()).limit(1))

    return SummaryRead(
        suite_count=suite_count,
        case_count=case_count,
        run_count=run_count,
        provider_count=provider_count,
        latest_pass_rate=latest_run.pass_rate if latest_run else 0.0,
    )


@router.get("/providers", response_model=list[ModelProviderRead])
def list_providers(db: Session = Depends(get_db)) -> list[ModelProvider]:
    return list(db.scalars(select(ModelProvider).order_by(ModelProvider.name)))


@router.get("/suites", response_model=list[EvalSuiteRead])
def list_suites(db: Session = Depends(get_db)) -> list[EvalSuite]:
    return list(
        db.scalars(
            select(EvalSuite).options(selectinload(EvalSuite.cases)).order_by(EvalSuite.created_at.desc())
        )
    )


@router.post("/suites", response_model=EvalSuiteRead, status_code=status.HTTP_201_CREATED)
def create_suite(payload: EvalSuiteCreate, db: Session = Depends(get_db)) -> EvalSuite:
    suite = EvalSuite(**payload.model_dump())
    db.add(suite)
    db.commit()
    db.refresh(suite)
    return suite


@router.get("/suites/{suite_id}", response_model=EvalSuiteRead)
def get_suite(suite_id: int, db: Session = Depends(get_db)) -> EvalSuite:
    suite = db.scalar(select(EvalSuite).where(EvalSuite.id == suite_id).options(selectinload(EvalSuite.cases)))
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eval suite not found")
    return suite


@router.post("/suites/{suite_id}/cases", response_model=EvalCaseRead, status_code=status.HTTP_201_CREATED)
def create_case(suite_id: int, payload: EvalCaseCreate, db: Session = Depends(get_db)) -> EvalCase:
    suite = db.get(EvalSuite, suite_id)
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eval suite not found")

    case = EvalCase(suite_id=suite_id, **payload.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.post("/runs", response_model=EvalRunRead, status_code=status.HTTP_201_CREATED)
def run_suite(payload: EvalRunCreate, db: Session = Depends(get_db)) -> EvalRun:
    try:
        run = create_eval_run(db, payload.suite_id, payload.provider_id, payload.model_name)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return db.scalar(select(EvalRun).where(EvalRun.id == run.id).options(selectinload(EvalRun.results)))


@router.get("/runs", response_model=list[EvalRunRead])
def list_runs(db: Session = Depends(get_db)) -> list[EvalRun]:
    return list(
        db.scalars(select(EvalRun).options(selectinload(EvalRun.results)).order_by(EvalRun.created_at.desc()))
    )


@router.get("/runs/{run_id}", response_model=EvalRunRead)
def get_run(run_id: int, db: Session = Depends(get_db)) -> EvalRun:
    run = db.scalar(select(EvalRun).where(EvalRun.id == run_id).options(selectinload(EvalRun.results)))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eval run not found")
    return run

