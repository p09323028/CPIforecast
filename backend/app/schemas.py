from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CategoryPair(BaseModel):
    en: str
    zh: str


class RunSummary(BaseModel):
    run_id: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    data_end_date: Optional[str] = None
    n_ok: Optional[int] = None
    n_failed: Optional[int] = None


class RunIdResponse(BaseModel):
    run_id: str


class ForecastPoint(BaseModel):
    date: str
    value: float


class MonthlyBand(BaseModel):
    date: str
    lower_95: Optional[float] = None
    median: Optional[float] = None
    upper_95: Optional[float] = None
    actual: Optional[float] = None


class YoyBand(BaseModel):
    year: int
    lower_95: float
    median: float
    upper_95: float
    base_actual: float


class ForecastPayload(BaseModel):
    category: str
    order: list[int]
    seasonal_order: list[int]
    bic: float
    history: list[ForecastPoint]
    monthly: list[MonthlyBand]
    yoy: list[YoyBand]


class AdminStatus(BaseModel):
    run_id: str
    state: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    current_index: int = 0
    total: int = 0
    current_category: Optional[str] = None
    error: Optional[str] = None


class TriggerResponse(BaseModel):
    run_id: str
    started_at: str
