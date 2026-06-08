"""非 CPI 的「實際價格」預測 API，與 CPI 端點對稱，但讀 PRICES_DATA_DIR。

輸出格式與 /api/forecast 完全相同（共用 build_forecast_payload），
所以前端卡片/圖表可直接沿用。
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from forecast import storage

from ..config import settings
from .forecast import build_forecast_payload

router = APIRouter(prefix="/api/prices", tags=["prices"])

PRICES_DIR = settings.PRICES_DATA_DIR


def _file_or_404(path: Path) -> Path:
    if not path.exists():
        raise HTTPException(404, f"file not found: {path.name}")
    return path


def _latest_manifest() -> dict:
    rid = storage.get_latest_run_id(PRICES_DIR)
    if not rid:
        raise HTTPException(404, "no price forecast available yet")
    try:
        return storage.read_manifest(PRICES_DIR, rid)
    except FileNotFoundError:
        raise HTTPException(404, "price manifest missing")


@router.get("/categories")
def list_price_items() -> list[dict]:
    """回傳 [{en, zh, unit, icon}]（en=資料夾 key），對齊前端 category 介面。"""
    manifest = _latest_manifest()
    return [
        {"en": it["key"], "zh": it["zh"], "unit": it.get("unit"), "icon": it.get("icon")}
        for it in manifest.get("items", [])
    ]


@router.get("/runs/latest")
def latest_price_run() -> dict:
    rid = storage.get_latest_run_id(PRICES_DIR)
    if not rid:
        raise HTTPException(404, "no price forecast available yet")
    return {"run_id": rid}


@router.get("/runs/{run_id}")
def get_price_run(run_id: str) -> dict:
    try:
        return storage.read_manifest(PRICES_DIR, run_id)
    except FileNotFoundError:
        raise HTTPException(404, f"run {run_id} not found")


@router.get("/forecast/{run_id}/{item}")
def get_price_forecast(run_id: str, item: str) -> dict:
    payload = build_forecast_payload(PRICES_DIR, run_id, item)
    # 補上品項中文名與單位（CPI payload 沒有這些欄位）
    try:
        manifest = storage.read_manifest(PRICES_DIR, run_id)
        info = manifest.get("categories", {}).get(item, {})
        payload["display_zh"] = info.get("display_zh")
        payload["unit"] = info.get("unit")
        payload["icon"] = info.get("icon")
    except FileNotFoundError:
        pass
    return payload


@router.get("/download/{run_id}/prices.csv")
def download_price_raw(run_id: str):
    path = _file_or_404(storage.run_dir(PRICES_DIR, run_id) / storage.RAW_CSV)
    return FileResponse(path, media_type="text/csv", filename=f"prices_{run_id}.csv")


@router.get("/download/{run_id}/{item}/monthly.csv")
def download_price_monthly(run_id: str, item: str):
    path = _file_or_404(
        storage.category_dir(PRICES_DIR, run_id, item) / storage.MONTHLY_CSV
    )
    return FileResponse(
        path, media_type="text/csv", filename=f"{item}_monthly_{run_id}.csv"
    )


@router.get("/download/{run_id}/{item}/yoy.csv")
def download_price_yoy(run_id: str, item: str):
    path = _file_or_404(
        storage.category_dir(PRICES_DIR, run_id, item) / storage.YOY_CSV
    )
    return FileResponse(
        path, media_type="text/csv", filename=f"{item}_yoy_{run_id}.csv"
    )


@router.get("/download/{run_id}/{item}/rolling_yoy.csv")
def download_price_rolling(run_id: str, item: str):
    path = _file_or_404(
        storage.category_dir(PRICES_DIR, run_id, item) / storage.ROLLING_YOY_CSV
    )
    return FileResponse(
        path, media_type="text/csv", filename=f"{item}_rolling_yoy_{run_id}.csv"
    )


@router.get("/download/{run_id}/{item}/paths.parquet")
def download_price_paths(run_id: str, item: str):
    path = _file_or_404(
        storage.category_dir(PRICES_DIR, run_id, item) / storage.PATHS_PARQUET
    )
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=f"{item}_paths_{run_id}.parquet",
    )
