import numpy as np
import pandas as pd

from forecast.summaries import monthly_quantiles, yoy_quantiles


def _paths(start: str, months: int, n_sim: int, base: float, scale: float) -> pd.DataFrame:
    idx = pd.date_range(start, periods=months, freq="MS")
    rng = np.random.default_rng(0)
    arr = rng.normal(loc=base, scale=scale, size=(months, n_sim))
    return pd.DataFrame(arr, index=idx, columns=list(range(n_sim)))


def test_monthly_quantiles_shape_and_actual():
    history = pd.Series(
        np.arange(100.0, 124.0),
        index=pd.date_range("2024-01-01", periods=24, freq="MS"),
    )
    paths = _paths("2026-01-01", 12, 100, base=125.0, scale=2.0)
    out = monthly_quantiles(paths, history)
    # 24 history rows + 12 forecast rows
    assert len(out) == 36
    assert out["actual"].dropna().iloc[-1] == 123.0
    assert pd.notna(out["median"].iloc[-1])
    # lower < median < upper
    fc = out.dropna(subset=["median"])
    assert (fc["lower_95"] < fc["median"]).all()
    assert (fc["median"] < fc["upper_95"]).all()


def test_yoy_quantiles_requires_full_prior_year():
    history = pd.Series(
        np.full(24, 100.0),
        index=pd.date_range("2024-01-01", periods=24, freq="MS"),
    )
    paths = _paths("2026-01-01", 12, 500, base=110.0, scale=1.0)
    out = yoy_quantiles(paths, history)
    assert 2026 in out.index
    assert (out.loc[2026, "lower_95"] < out.loc[2026, "median"] < out.loc[2026, "upper_95"])
