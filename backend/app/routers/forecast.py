from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException

from forecast import storage
from forecast.categories import english_names

from ..config import settings

router = APIRouter(prefix="/api/forecast", tags=["forecast"])


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise HTTPException(404, f"missing file: {path.name}")
    return pd.read_csv(path)


@router.get("/{run_id}/{category}")
def get_forecast(run_id: str, category: str) -> dict:
    if category not in english_names():
        raise HTTPException(400, f"unknown category: {category}")
    try:
        manifest = storage.read_manifest(settings.DATA_DIR, run_id)
    except FileNotFoundError:
        raise HTTPException(404, f"run {run_id} not found")
    cat_info = manifest.get("categories", {}).get(category)
    if not cat_info:
        raise HTTPException(404, "category not in this run")
    if cat_info.get("status") != "ok":
        raise HTTPException(
            409,
            {"detail": "category failed in this run", "error": cat_info.get("error")},
        )

    cdir = storage.category_dir(settings.DATA_DIR, run_id, category)
    monthly_df = _read_csv(cdir / storage.MONTHLY_CSV)
    yoy_df = _read_csv(cdir / storage.YOY_CSV)
    raw_df = _read_csv(storage.run_dir(settings.DATA_DIR, run_id) / storage.RAW_CSV)

    raw_df["date"] = pd.to_datetime(raw_df["date"])
    history = raw_df[["date", category]].dropna()
    history_payload = [
        {"date": d.strftime("%Y-%m-%d"), "value": float(v)}
        for d, v in zip(history["date"].tail(60), history[category].tail(60))
    ]

    # 從 10,000 條模擬路徑算「下個月上漲機率」
    prob_rise_next_month = None
    last_actual_value = None
    next_forecast_date = None
    paths_path = cdir / storage.PATHS_PARQUET
    if paths_path.exists() and not history.empty:
        try:
            paths_df = pd.read_parquet(paths_path)
            last_actual_value = float(history[category].iloc[-1])
            first_forecast = paths_df.iloc[0]
            next_forecast_date = paths_df.index.min().strftime("%Y-%m-%d")
            prob_rise_next_month = float((first_forecast > last_actual_value).mean())
        except Exception:
            prob_rise_next_month = None

    monthly_payload = []
    for _, row in monthly_df.iterrows():
        monthly_payload.append(
            {
                "date": pd.to_datetime(row["date"]).strftime("%Y-%m-%d"),
                "lower_95": _opt_float(row.get("lower_95")),
                "median": _opt_float(row.get("median")),
                "upper_95": _opt_float(row.get("upper_95")),
                "actual": _opt_float(row.get("actual")),
            }
        )

    annual_yoy_payload = []
    for _, row in yoy_df.iterrows():
        annual_yoy_payload.append(
            {
                "year": int(row["year"]),
                "lower_95": float(row["lower_95"]),
                "median": float(row["median"]),
                "upper_95": float(row["upper_95"]),
                "base_actual": float(row["base_actual"]),
            }
        )

    rolling_info = cat_info.get("rolling") or {}
    rolling_payload = []
    rolling_path = cdir / storage.ROLLING_YOY_CSV
    if rolling_path.exists():
        rolling_df = pd.read_csv(rolling_path)
        for _, row in rolling_df.iterrows():
            rolling_payload.append(
                {
                    "end_date": str(row.get("end_date")),
                    "effective_end": str(row.get("effective_end", "")),
                    "lower_95": _opt_float(row.get("lower_95")),
                    "median": _opt_float(row.get("median")),
                    "upper_95": _opt_float(row.get("upper_95")),
                    "bic": _opt_float(row.get("bic")),
                    "order": _parse_tuple(row.get("order")),
                    "seasonal_order": _parse_tuple(row.get("seasonal_order")),
                }
            )

    return {
        "category": category,
        "order": cat_info.get("order"),
        "seasonal_order": cat_info.get("seasonal_order"),
        "bic": cat_info.get("bic"),
        "train_start": cat_info.get("train_start"),
        "train_end": cat_info.get("train_end"),
        "data_end_date": manifest.get("data_end_date"),
        "history": history_payload,
        "monthly": monthly_payload,
        "prob_rise_next_month": prob_rise_next_month,
        "last_actual_value": last_actual_value,
        "next_forecast_date": next_forecast_date,
        "annual_yoy": annual_yoy_payload,
        "rolling_yoy": {
            "forecast_year": rolling_info.get("forecast_year"),
            "base_actual": rolling_info.get("base_actual"),
            "actual_yoy": rolling_info.get("actual_yoy"),
            "start_end_date": rolling_info.get("start_end_date"),
            "end_end_date": rolling_info.get("end_end_date"),
            "n_iterations": rolling_info.get("n_iterations"),
            "points": rolling_payload,
        },
    }


def _parse_tuple(v) -> list[int] | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, str):
        # CSV writes tuples like "[0, 1, 2]" via Python list repr
        try:
            import ast
            parsed = ast.literal_eval(v)
            if isinstance(parsed, (list, tuple)):
                return [int(x) for x in parsed]
        except Exception:
            return None
    return None


def _opt_float(v) -> float | None:
    try:
        if v is None or pd.isna(v):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None
