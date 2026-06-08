from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.eval_results import router as eval_results_router
from app.api.eval_runs import router as eval_runs_router
from app.api.eval_suites import router as eval_suites_router
from app.api.providers import router as providers_router
from app.api.routes import router as api_router
from app.core.config import settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}


app.include_router(api_router, prefix="/api/v1")
app.include_router(eval_suites_router, prefix="/api")
app.include_router(providers_router, prefix="/api")
app.include_router(eval_runs_router, prefix="/api")
app.include_router(eval_results_router, prefix="/api")
