"""SARIMA + Monte Carlo 模擬。參數與 notebook 完全一致。"""
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd
import pmdarima as pm

log = logging.getLogger(__name__)

TRAIN_YEARS = 12
TRAIN_MONTHS = TRAIN_YEARS * 12
N_SIM = 20
N_REPS = 10_000
SEED = 1


@dataclass
class FitResult:
    model: pm.ARIMA
    order: tuple[int, int, int]
    seasonal_order: tuple[int, int, int, int]
    bic: float
    train_start: pd.Timestamp
    train_end: pd.Timestamp


def fit_tb1957_auto_arima(
    y: pd.Series,
    end_date: pd.Timestamp,
    years: int = TRAIN_YEARS,
) -> FitResult:
    """Replicate notebook: train on last `years*12` months ending at end_date."""
    y = y.copy()
    start_date = end_date - pd.DateOffset(months=years * 12 - 1)
    y_train = y.loc[start_date:end_date].dropna()
    model = pm.auto_arima(
        y_train,
        m=12,
        start_p=0, max_p=12,
        start_q=0, max_q=12,
        max_d=4,
        seasonal=True,
        start_P=0, max_P=2,
        start_Q=0, max_Q=2,
        max_D=1,
        information_criterion="bic",
        trace=False,
        error_action="ignore",
        suppress_warnings=True,
    )
    return FitResult(
        model=model,
        order=tuple(model.order),
        seasonal_order=tuple(model.seasonal_order),
        bic=float(model.bic()),
        train_start=y_train.index.min(),
        train_end=y_train.index.max(),
    )


def simulate_paths(
    fit: FitResult,
    end_date: pd.Timestamp,
    horizon_months: int = N_SIM,
    n_sim: int = N_REPS,
    seed: int = SEED,
) -> pd.DataFrame:
    """Run notebook's arima_res_.simulate with anchor='end'.

    Returns a DataFrame with DatetimeIndex (the `horizon_months` months after
    end_date) and columns 0..n_sim-1.
    """
    sim = fit.model.arima_res_.simulate(
        nsimulations=horizon_months,
        repetitions=n_sim,
        anchor="end",
        random_state=seed,
    )
    # statsmodels returns a DataFrame with a (y, sim_id) MultiIndex column.
    if isinstance(sim, pd.DataFrame):
        sim_df = sim.copy()
        if isinstance(sim_df.columns, pd.MultiIndex):
            sim_df.columns = list(range(sim_df.shape[1]))
        else:
            sim_df.columns = list(range(sim_df.shape[1]))
    else:
        idx = pd.date_range(
            end_date + pd.DateOffset(months=1), periods=horizon_months, freq="MS"
        )
        sim_df = pd.DataFrame(sim, index=idx, columns=list(range(n_sim)))

    sim_df.index = pd.date_range(
        end_date + pd.DateOffset(months=1), periods=horizon_months, freq="MS"
    )
    sim_df.index.name = "date"
    return sim_df
