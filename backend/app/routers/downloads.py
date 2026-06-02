from __future__ import annotations

import io
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from forecast import report as report_mod
from forecast import storage
from forecast.categories import english_names

from ..config import settings

router = APIRouter(prefix="/api/download", tags=["downloads"])


def _file_or_404(path: Path) -> Path:
    if not path.exists():
        raise HTTPException(404, f"file not found: {path.name}")
    return path


@router.get("/{run_id}/raw_cpi.csv")
def download_raw(run_id: str):
    path = _file_or_404(
        storage.run_dir(settings.DATA_DIR, run_id) / storage.RAW_CSV
    )
    return FileResponse(path, media_type="text/csv", filename=f"raw_cpi_{run_id}.csv")


@router.get("/{run_id}/{category}/monthly.csv")
def download_monthly(run_id: str, category: str):
    _check_category(category)
    path = _file_or_404(
        storage.category_dir(settings.DATA_DIR, run_id, category)
        / storage.MONTHLY_CSV
    )
    return FileResponse(
        path,
        media_type="text/csv",
        filename=f"{category}_monthly_{run_id}.csv",
    )


@router.get("/{run_id}/{category}/yoy.csv")
def download_yoy(run_id: str, category: str):
    _check_category(category)
    path = _file_or_404(
        storage.category_dir(settings.DATA_DIR, run_id, category) / storage.YOY_CSV
    )
    return FileResponse(
        path,
        media_type="text/csv",
        filename=f"{category}_yoy_{run_id}.csv",
    )


@router.get("/{run_id}/{category}/rolling_yoy.csv")
def download_rolling_yoy(run_id: str, category: str):
    _check_category(category)
    path = _file_or_404(
        storage.category_dir(settings.DATA_DIR, run_id, category)
        / storage.ROLLING_YOY_CSV
    )
    return FileResponse(
        path,
        media_type="text/csv",
        filename=f"{category}_rolling_yoy_{run_id}.csv",
    )


@router.get("/{run_id}/{category}/paths.parquet")
def download_paths(run_id: str, category: str):
    _check_category(category)
    path = _file_or_404(
        storage.category_dir(settings.DATA_DIR, run_id, category)
        / storage.PATHS_PARQUET
    )
    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=f"{category}_paths_{run_id}.parquet",
    )


def _check_category(category: str) -> None:
    if category not in english_names():
        raise HTTPException(400, f"unknown category: {category}")


@router.get("/{run_id}/report.xlsx")
def download_report(run_id: str):
    """產生格式化的台灣 CPI 預測月報 xlsx（仿 USDA TB-1957 格式）。"""
    try:
        manifest = storage.read_manifest(settings.DATA_DIR, run_id)
    except FileNotFoundError:
        raise HTTPException(404, f"run {run_id} not found")
    buf = io.BytesIO()
    try:
        report_mod.write_xlsx(settings.DATA_DIR, run_id, manifest, buf)
    except Exception as exc:
        raise HTTPException(500, f"報表產生失敗：{exc}")
    buf.seek(0)
    filename = f"CPI_forecast_report_{manifest.get('data_end_date', run_id)}.xlsx"
    return StreamingResponse(
        buf,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
