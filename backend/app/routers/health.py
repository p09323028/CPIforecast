from __future__ import annotations

from fastapi import APIRouter

from ..config import settings
from forecast import storage

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health() -> dict:
    latest = storage.get_latest_run_id(settings.DATA_DIR)
    return {
        "status": "ok",
        "latest_run_id": latest,
        "data_dir": settings.DATA_DIR,
    }
