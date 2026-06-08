from datetime import datetime
from typing import List

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class EvalSuite(TimestampMixin, Base):
    __tablename__ = "eval_suites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    policy_version: Mapped[str] = mapped_column(String(80), default="starter-v1")

    cases: Mapped[List["EvalCase"]] = relationship(back_populates="suite", cascade="all, delete-orphan")
    runs: Mapped[List["EvalRun"]] = relationship(back_populates="suite")


class EvalCase(TimestampMixin, Base):
    __tablename__ = "eval_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    suite_id: Mapped[int] = mapped_column(ForeignKey("eval_suites.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False)
    expected_behavior: Mapped[str] = mapped_column(String(120), nullable=False)
    severity: Mapped[str] = mapped_column(String(40), default="medium")

    suite: Mapped[EvalSuite] = relationship(back_populates="cases")
    results: Mapped[List["EvalResult"]] = relationship(back_populates="case")


class ModelProvider(TimestampMixin, Base):
    __tablename__ = "model_providers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(80), nullable=False, default="mock")
    base_url: Mapped[str] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    runs: Mapped[List["EvalRun"]] = relationship(back_populates="provider")


class EvalRun(TimestampMixin, Base):
    __tablename__ = "eval_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    suite_id: Mapped[int] = mapped_column(ForeignKey("eval_suites.id"), nullable=False)
    provider_id: Mapped[int] = mapped_column(ForeignKey("model_providers.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="queued")
    pass_rate: Mapped[float] = mapped_column(Float, default=0.0)
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)

    suite: Mapped[EvalSuite] = relationship(back_populates="runs")
    provider: Mapped[ModelProvider] = relationship(back_populates="runs")
    results: Mapped[List["EvalResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class EvalResult(TimestampMixin, Base):
    __tablename__ = "eval_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    case_id: Mapped[int] = mapped_column(ForeignKey("eval_cases.id"), nullable=False)
    output: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(String(40), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    review_status: Mapped[str] = mapped_column(String(40), default="unreviewed")
    reviewer_notes: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    run: Mapped[EvalRun] = relationship(back_populates="results")
    case: Mapped[EvalCase] = relationship(back_populates="results")
