"""跑完 14 類別 + 寫盤 + 維護 manifest。"""
from __future__ import annotations

import logging
import traceback
from datetime import datetime, timezone
from typing import Callable, Optional

import pandas as pd

from . import data as data_mod
from . import model as model_mod
from . import rolling as rolling_mod
from . import storage
from . import summaries
from .categories import english_names

log = logging.getLogger(__name__)

ProgressCb = Callable[[int, int, str], None]


def _lib_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for mod_name in ("pmdarima", "statsmodels", "numpy", "pandas", "scipy"):
        try:
            mod = __import__(mod_name)
            versions[mod_name] = getattr(mod, "__version__", "unknown")
        except Exception:
            versions[mod_name] = "missing"
    return versions


def _decide_rolling_window(data_end: pd.Timestamp) -> tuple[int, pd.Timestamp, int]:
    """Pick forecast_year + start_end_date + n for the rolling YoY view.

    Default: forecast_year = data_end.year (since data is in-progress for that
    year); start_end_date = (forecast_year-1)-12-01; n = 12 (Dec of prior year
    through Nov of forecast year).
    """
    forecast_year = data_end.year
    start_end_date = pd.Timestamp(f"{forecast_year - 1}-12-01")
    return forecast_year, start_end_date, 12


def run_full(
    base_dir: str,
    run_id: str,
    *,
    dgbas_url: str = "",
    n_sim: int = model_mod.N_SIM,
    repetitions: int = model_mod.N_REPS,
    seed: int = model_mod.SEED,
    train_months: int = model_mod.TRAIN_MONTHS,
    progress_cb: Optional[ProgressCb] = None,
    keep_runs: int = 12,
    rolling_n: int = 12,
) -> dict:
    """Fetch DGBAS data and produce forecasts for all 14 categories.

    Writes per-category outputs + manifest.json + raw_cpi.csv.
    Updates latest.txt only if at least one category succeeded.
    """
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log.info("[run %s] starting", run_id)

    df, source_meta = data_mod.load_cleaned(dgbas_url)
    storage.write_raw_cpi(base_dir, run_id, df)

    end_date = pd.to_datetime(source_meta["data_end_date"])
    if end_date is None or pd.isna(end_date):
        raise RuntimeError("source data has no fully-observed month — aborting")

    forecast_year, start_end_date, n_rolling = _decide_rolling_window(end_date)
    log.info(
        "rolling YoY config: forecast_year=%d, start_end=%s, n=%d",
        forecast_year, start_end_date.strftime("%Y-%m"), n_rolling,
    )

    cats = english_names()
    total = len(cats)
    per_category: dict[str, dict] = {}

    for idx, cat in enumerate(cats, start=1):
        if progress_cb:
            try:
                progress_cb(idx, total, cat)
            except Exception:
                log.exception("progress_cb failed")
        log.info("[run %s] (%d/%d) fitting %s", run_id, idx, total, cat)
        try:
            series = df[cat]
            fit = model_mod.fit_tb1957_auto_arima(
                series, end_date=end_date, years=train_months // 12
            )
            paths = model_mod.simulate_paths(
                fit,
                end_date=end_date,
                horizon_months=n_sim,
                n_sim=repetitions,
                seed=seed,
            )
            monthly_df = summaries.monthly_quantiles(paths, series)
            yoy_df = summaries.yoy_quantiles(paths, series)

            # 滾動 YoY：對 n 個逐月推進的 end_date 各做一次配適 + 模擬
            try:
                rolling_result = rolling_mod.rolling_yoy_quantiles(
                    series,
                    start_end_date=start_end_date,
                    n=rolling_n,
                    forecast_year=forecast_year,
                    train_years=train_months // 12,
                    n_sim=repetitions,
                    seed=seed,
                )
                rolling_df = rolling_result.df
                rolling_info: dict = {
                    "forecast_year": rolling_result.forecast_year,
                    "base_actual": rolling_result.base_actual,
                    "actual_yoy": rolling_result.actual_yoy,
                    "start_end_date": rolling_result.start_end_date.strftime("%Y-%m-%d"),
                    "end_end_date": rolling_result.end_end_date.strftime("%Y-%m-%d"),
                    "n_iterations": int(len(rolling_df)),
                }
            except Exception:
                log.exception("rolling YoY failed for %s — recording empty", cat)
                rolling_df = None
                rolling_info = {"error": "rolling failed", "forecast_year": forecast_year}

            storage.write_category_outputs(
                base_dir, run_id, cat, monthly_df, yoy_df, paths, rolling_yoy_df=rolling_df
            )
            # 預存「下個月上漲機率」，讓線上 API 不必再讀 paths.parquet
            # （儀表板 14 類別併發讀 parquet 會把免費機記憶體打爆）。
            prob_rise_next_month = None
            last_actual_value = None
            next_forecast_date = None
            try:
                last_actual_value = float(series.dropna().iloc[-1])
                first_forecast = paths.iloc[0]
                next_forecast_date = paths.index.min().strftime("%Y-%m-%d")
                prob_rise_next_month = float(
                    (first_forecast > last_actual_value).mean()
                )
            except Exception:
                log.exception("prob_rise_next_month 計算失敗：%s", cat)
            per_category[cat] = {
                "status": "ok",
                "order": list(fit.order),
                "seasonal_order": list(fit.seasonal_order),
                "bic": fit.bic,
                "train_start": fit.train_start.strftime("%Y-%m-%d"),
                "train_end": fit.train_end.strftime("%Y-%m-%d"),
                "forecast_months": int(paths.shape[0]),
                "forecast_start": paths.index.min().strftime("%Y-%m-%d"),
                "forecast_end": paths.index.max().strftime("%Y-%m-%d"),
                "prob_rise_next_month": prob_rise_next_month,
                "last_actual_value": last_actual_value,
                "next_forecast_date": next_forecast_date,
                "rolling": rolling_info,
            }
        except Exception as exc:
            log.exception("[run %s] %s failed", run_id, cat)
            per_category[cat] = {
                "status": "failed",
                "error": str(exc),
                "traceback": traceback.format_exc(limit=4),
            }

    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    n_ok = sum(1 for v in per_category.values() if v.get("status") == "ok")

    manifest = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "data_end_date": source_meta["data_end_date"],
        "dgbas_url": source_meta["dgbas_url"],
        "fetched_at": source_meta["fetched_at"],
        "seed": seed,
        "n_sim": n_sim,
        "repetitions": repetitions,
        "train_months": train_months,
        "library_versions": _lib_versions(),
        "n_ok": n_ok,
        "n_failed": len(cats) - n_ok,
        "categories": per_category,
    }
    storage.write_manifest(base_dir, run_id, manifest)

    if n_ok > 0:
        storage.set_latest(base_dir, run_id)
        try:
            storage.prune_old_runs(base_dir, keep=keep_runs)
        except Exception:
            log.exception("prune_old_runs failed (non-fatal)")

    log.info(
        "[run %s] done ok=%d failed=%d", run_id, n_ok, len(cats) - n_ok
    )
    return manifest
