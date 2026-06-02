from __future__ import annotations

from fastapi import APIRouter

from forecast.categories import display_pairs

router = APIRouter(prefix="/api", tags=["categories"])


@router.get("/categories")
def list_categories() -> list[dict]:
    return display_pairs()
