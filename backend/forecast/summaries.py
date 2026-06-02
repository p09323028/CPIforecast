"""產出月度分位數 + 年度 YoY% 分位數。沿用 notebook 的計算邏輯。"""
from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_quantiles(
    paths: pd.DataFrame,
    history: pd.Series,
    history_tail_months: int = 24,
) -> pd.DataFrame:
    """Compute 0.025/0.5/0.975 quantiles per forecast month and prepend
    `history_tail_months` historical actuals (with NaN bands).

    Returns columns: date (index), lower_95, median, upper_95, actual
    """
    q_low = paths.quantile(0.025, axis=1)
    q_med = paths.quantile(0.500, axis=1)
    q_high = paths.quantile(0.975, axis=1)
    forecast_df = pd.DataFrame(
        {
            "lower_95": q_low,
            "median": q_med,
            "upper_95": q_high,
            "actual": np.nan,
        }
    )

    hist_tail = history.dropna().iloc[-history_tail_months:]
    hist_df = pd.DataFrame(
        {
            "lower_95": np.nan,
            "median": np.nan,
            "upper_95": np.nan,
            "actual": hist_tail.values,
        },
        index=hist_tail.index,
    )

    out = pd.concat([hist_df, forecast_df], axis=0)
    out.index.name = "date"
    return out


def yoy_quantiles(
    paths: pd.DataFrame,
    history: pd.Series,
) -> pd.DataFrame:
    """For each forecast year fully or partially covered by the simulations,
    compute (annual avg of that year) / (prior year's actual annual avg) - 1
    per simulation path, then take 0.025/0.5/0.975 quantiles.

    Only emits years for which we have ≥ 1 forecast month and a complete prior
    year actual (12 months of actual data in year-1).

    Returns columns: year (index), lower_95, median, upper_95, base_actual
    """
    rows: list[dict] = []
    years = sorted({d.year for d in paths.index})
    history = history.dropna()

    for year in years:
        prior_year = year - 1
        prior_actuals = history[
            (history.index.year == prior_year)
        ]
        if len(prior_actuals) < 12:
            continue
        base = float(prior_actuals.mean())

        year_paths = paths.loc[paths.index.year == year]
        if year_paths.empty:
            continue

        actuals_in_year = history[history.index.year == year]

        if not actuals_in_year.empty:
            actual_months = set(actuals_in_year.index)
            forecast_months_in_year = [
                d for d in year_paths.index if d not in actual_months
            ]
            year_paths = year_paths.loc[forecast_months_in_year]
            if year_paths.empty:
                continue
            actual_sum = float(actuals_in_year.sum())
            n_actual = int(len(actuals_in_year))
            combined_year_avg_per_path = (
                actual_sum + year_paths.sum(axis=0)
            ) / (n_actual + year_paths.shape[0])
        else:
            combined_year_avg_per_path = year_paths.mean(axis=0)

        yoy_per_path = combined_year_avg_per_path / base * 100.0 - 100.0
        rows.append(
            {
                "year": year,
                "lower_95": float(yoy_per_path.quantile(0.025)),
                "median": float(yoy_per_path.quantile(0.5)),
                "upper_95": float(yoy_per_path.quantile(0.975)),
                "base_actual": base,
            }
        )

    df = pd.DataFrame(rows).set_index("year")
    return df
