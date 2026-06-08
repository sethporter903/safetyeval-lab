from fastapi import APIRouter, HTTPException, status

from app.schemas.eval_suites import FileEvalSuiteRead, FileEvalSuiteSummary
from app.services.eval_suite_files import get_file_eval_suite, list_file_eval_suites

router = APIRouter(prefix="/eval-suites", tags=["eval suites"])


@router.get("", response_model=list[FileEvalSuiteSummary])
def list_eval_suites() -> list[FileEvalSuiteSummary]:
    return list_file_eval_suites()


@router.get("/{suite_name}", response_model=FileEvalSuiteRead)
def get_eval_suite(suite_name: str) -> FileEvalSuiteRead:
    suite = get_file_eval_suite(suite_name)
    if suite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eval suite not found")
    return suite
