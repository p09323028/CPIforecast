"""滾動 YoY 預測 — 對應 notebook 的 get_result() 迴圈。

對 n 個逐月推進的 end_date，每個都重做 SARIMA 配適 + 蒙地卡羅模擬，
然後算 forecast_year 年的年平均 YoY% 分位數。

優化：若某個 end_date 超過實際資料末端（data_end），train 切片內容會與
data_end 一致，所以 cache fit 結果不重做。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from . import model as model_mod

log = logging.getLogger(__name__)


@dataclass
class RollingYoyResult:
    df: pd.DataFrame          # index=end_date, cols=[lower_95,median,upper_95,order,seasonal_order,bic]
    base_actual: Optional[float]
    actual_yoy: Optional[float]
    forecast_year: int
    start_end_date: pd.Timestamp
    end_end_date: pd.Timestamp


def _months_to_year_end(current: pd.Timestamp, forecast_year: int) -> int:
    """模擬要跑多少個月才能涵蓋到 forecast_year 年底。"""
    target = pd.Timestamp(f"{forecast_year}-12-01")
    if current >= target:
        return 1
    diff = (target.year - current.year) * 12 + (target.month - current.month)
    return diff


def rolling_yoy_quantiles(
    series: pd.Series,
    *,
    start_end_date: pd.Timestamp,
    n: int = 12,
    forecast_year: int,
    train_years: int = 12,
    n_sim: int = model_mod.N_REPS,
    seed: int = model_mod.SEED,
) -> RollingYoyResult:
    """跑 n 個 end_date 的 rolling 預測，回傳 RollingYoyResult。"""
    series = series.dropna().sort_index().asfreq("MS")
    data_end = series.index.max()

    # base = 前一年實際年平均
    prior_year = forecast_year - 1
    prior_actuals = series[series.index.year == prior_year]
    if len(prior_actuals) < 12:
        log.warning(
            "rolling: 缺少完整 %d 年實際資料 → base_actual=None", prior_year
        )
        base_actual = None
    else:
        base_actual = float(prior_actuals.mean())

    # 若 forecast_year 已完整 → 算實際 YoY 供圖上比較
    forecast_actuals = series[series.index.year == forecast_year]
    if base_actual is not None and len(forecast_actuals) >= 12:
        actual_yoy = float(forecast_actuals.mean() / base_actual * 100.0 - 100.0)
    else:
        actual_yoy = None

    cached_end: Optional[pd.Timestamp] = None
    cached_fit = None
    cached_paths: Optional[pd.DataFrame] = None
    rows: list[dict] = []

    for i in range(n):
        current = start_end_date + pd.DateOffset(months=i)
        # 超過實際資料的部分，y_train 切片內容會與 data_end 一致 → 快取
        effective_end = min(current, data_end)

        if cached_end != effective_end:
            try:
                fit = model_mod.fit_tb1957_auto_arima(
                    series, end_date=effective_end, years=train_years
                )
            except Exception as exc:
                log.exception(
                    "rolling: fit failed at effective_end=%s",
                    effective_end.strftime("%Y-%m-%d"),
                )
                # 寫入失敗列並繼續
                rows.append(
                    {
                        "end_date": current.strftime("%Y-%m-%d"),
                        "effective_end": effective_end.strftime("%Y-%m-%d"),
                        "lower_95": None,
                        "median": None,
                        "upper_95": None,
                        "order": None,
                        "seasonal_order": None,
                        "bic": None,
                        "error": str(exc),
                    }
                )
                continue

            horizon = _months_to_year_end(effective_end, forecast_year)
            # 模擬至少跑到 forecast_year 年底
            paths = model_mod.simulate_paths(
                fit,
                end_date=effective_end,
                horizon_months=max(horizon, model_mod.N_SIM),
                n_sim=n_sim,
                seed=seed,
            )
            cached_end = effective_end
            cached_fit = fit
            cached_paths = paths
        else:
            fit = cached_fit
            paths = cached_paths

        # 將 forecast_year 年的「實際 + 模擬」合在一起算每條路徑的年平均
        forecast_year_paths = paths.loc[paths.index.year == forecast_year]
        actuals_in_year = series[series.index.year == forecast_year]

        if not actuals_in_year.empty:
            # 排除模擬中與實際重疊的月份
            actual_months = set(actuals_in_year.index)
            forecast_year_paths = forecast_year_paths.loc[
                ~forecast_year_paths.index.isin(actual_months)
            ]
            actual_sum = float(actuals_in_year.sum())
            n_actual = int(len(actuals_in_year))
            if forecast_year_paths.empty:
                year_avg_per_path = pd.Series(
                    actual_sum / n_actual, index=paths.columns
                )
            else:
                year_avg_per_path = (
                    actual_sum + forecast_year_paths.sum(axis=0)
                ) / (n_actual + forecast_year_paths.shape[0])
        else:
            year_avg_per_path = forecast_year_paths.mean(axis=0)

        if base_actual is None:
            l = m = u = None
        else:
            yoy_per_path = year_avg_per_path / base_actual * 100.0 - 100.0
            l = float(yoy_per_path.quantile(0.025))
            m = float(yoy_per_path.quantile(0.500))
            u = float(yoy_per_path.quantile(0.975))

        rows.append(
            {
                "end_date": current.strftime("%Y-%m-%d"),
                "effective_end": effective_end.strftime("%Y-%m-%d"),
                "lower_95": l,
                "median": m,
                "upper_95": u,
                "order": list(fit.order),
                "seasonal_order": list(fit.seasonal_order),
                "bic": fit.bic,
            }
        )

    df = pd.DataFrame(rows).set_index("end_date") if rows else pd.DataFrame()
    return RollingYoyResult(
        df=df,
        base_actual=base_actual,
        actual_yoy=actual_yoy,
        forecast_year=forecast_year,
        start_end_date=start_end_date,
        end_end_date=start_end_date + pd.DateOffset(months=n - 1),
    )
