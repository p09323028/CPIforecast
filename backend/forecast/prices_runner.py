"""對「實際價格」Excel 跑與 CPI 完全相同的 SARIMA + 蒙地卡羅流程。

輸入：scripts/make_price_template.py 產生、使用者填好的 price_template.xlsx
輸出：與 CPI run 相同的目錄結構（每品項一個資料夾 + manifest.json + raw_cpi.csv），
      但寫到獨立的 PRICES_DATA_DIR，不與 CPI 混在一起。

每個品項都沿用 forecast.model / summaries / rolling，參數與 CPI 一致
（seed=1、10,000 條路徑、18 個月 horizon、12 年訓練窗）。
"""
from __future__ import annotations

import logging
import re
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import model as model_mod
from . import rolling as rolling_mod
from . import storage, summaries

log = logging.getLogger(__name__)

DATA_SHEET = "價格資料"
DATE_COL = "月份"

# 已知品項的固定英文 key（資料夾名／API 路徑用）。未列出的自動編號。
KNOWN_KEYS: dict[str, str] = {
    "雞蛋產地價格": "egg_farm",
    "雞蛋都市零售價格": "egg_retail",
}
# 卡片用的 emoji（前端找不到時用預設）。
ICON_BY_KEY: dict[str, str] = {
    "egg_farm": "🥚",
    "egg_retail": "🍳",
}


def _parse_header(h: str) -> tuple[str, str | None]:
    """'雞蛋產地價格(元/台斤)' → ('雞蛋產地價格', '元/台斤')。"""
    m = re.match(r"^(.*?)\s*[(（](.*?)[)）]\s*$", str(h).strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return str(h).strip(), None


def _read_prices(xlsx_path: str | Path) -> tuple[pd.DataFrame, list[dict]]:
    """讀 Excel，回傳 (寬表 DataFrame[index=date, cols=key], items meta)。"""
    df = pd.read_excel(xlsx_path, sheet_name=DATA_SHEET)
    if DATE_COL not in df.columns:
        raise RuntimeError(f"找不到「{DATE_COL}」欄，請確認用的是範本格式")
    df[DATE_COL] = pd.to_datetime(df[DATE_COL])
    df = df.set_index(DATE_COL).sort_index()

    items: list[dict] = []
    rename: dict[str, str] = {}
    idx = 0
    for col in df.columns:
        if df[col].notna().sum() == 0:
            continue  # 空欄（未填的範例欄）跳過
        idx += 1
        zh, unit = _parse_header(col)
        key = KNOWN_KEYS.get(zh, f"item{idx}")
        rename[col] = key
        items.append({"key": key, "zh": zh, "unit": unit, "icon": ICON_BY_KEY.get(key, "💰")})

    if not items:
        raise RuntimeError("Excel 沒有任何已填資料的品項欄")

    wide = df[list(rename.keys())].rename(columns=rename).astype(float)
    return wide, items


def run_prices(
    xlsx_path: str | Path,
    base_dir: str,
    *,
    run_id: str | None = None,
    seed: int = model_mod.SEED,
    repetitions: int = model_mod.N_REPS,
    n_sim: int = model_mod.N_SIM,
    train_months: int = model_mod.TRAIN_MONTHS,
    keep_runs: int = 12,
) -> dict:
    """對 Excel 內每個品項跑預測，輸出到 base_dir，回傳 manifest。"""
    run_id = run_id or storage.new_run_id()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    log.info("[price-run %s] starting", run_id)

    wide, items = _read_prices(xlsx_path)
    storage.write_raw_cpi(base_dir, run_id, wide)  # 檔名 raw_cpi.csv（內部沿用）

    per_item: dict[str, dict] = {}
    overall_end: pd.Timestamp | None = None

    for it in items:
        key, zh = it["key"], it["zh"]
        log.info("[price-run %s] fitting %s (%s)", run_id, key, zh)
        try:
            series = wide[key].dropna().sort_index().asfreq("MS")
            end_date = series.dropna().index.max()
            forecast_year = end_date.year
            overall_end = end_date if overall_end is None else max(overall_end, end_date)

            fit = model_mod.fit_tb1957_auto_arima(
                series, end_date=end_date, years=train_months // 12
            )
            paths = model_mod.simulate_paths(
                fit, end_date=end_date, horizon_months=n_sim, n_sim=repetitions, seed=seed
            )
            monthly_df = summaries.monthly_quantiles(paths, series)
            yoy_df = summaries.yoy_quantiles(paths, series)

            start_end_date = pd.Timestamp(f"{forecast_year - 1}-12-01")
            try:
                rr = rolling_mod.rolling_yoy_quantiles(
                    series,
                    start_end_date=start_end_date,
                    n=12,
                    forecast_year=forecast_year,
                    train_years=train_months // 12,
                    n_sim=repetitions,
                    seed=seed,
                )
                rolling_df = rr.df
                rolling_info: dict = {
                    "forecast_year": rr.forecast_year,
                    "base_actual": rr.base_actual,
                    "actual_yoy": rr.actual_yoy,
                    "start_end_date": rr.start_end_date.strftime("%Y-%m-%d"),
                    "end_end_date": rr.end_end_date.strftime("%Y-%m-%d"),
                    "n_iterations": int(len(rolling_df)),
                }
            except Exception:
                log.exception("rolling YoY failed for %s", key)
                rolling_df = None
                rolling_info = {"error": "rolling failed", "forecast_year": forecast_year}

            storage.write_category_outputs(
                base_dir, run_id, key, monthly_df, yoy_df, paths, rolling_yoy_df=rolling_df
            )

            last_actual_value = float(series.dropna().iloc[-1])
            first_forecast = paths.iloc[0]
            next_forecast_date = paths.index.min().strftime("%Y-%m-%d")
            prob_rise_next_month = float((first_forecast > last_actual_value).mean())

            per_item[key] = {
                "status": "ok",
                "display_zh": zh,
                "unit": it["unit"],
                "icon": it["icon"],
                "order": list(fit.order),
                "seasonal_order": list(fit.seasonal_order),
                "bic": fit.bic,
                "train_start": fit.train_start.strftime("%Y-%m-%d"),
                "train_end": fit.train_end.strftime("%Y-%m-%d"),
                "data_end_date": end_date.strftime("%Y-%m-%d"),
                "forecast_months": int(paths.shape[0]),
                "forecast_start": paths.index.min().strftime("%Y-%m-%d"),
                "forecast_end": paths.index.max().strftime("%Y-%m-%d"),
                "prob_rise_next_month": prob_rise_next_month,
                "last_actual_value": last_actual_value,
                "next_forecast_date": next_forecast_date,
                "rolling": rolling_info,
            }
        except Exception as exc:
            log.exception("[price-run %s] %s failed", run_id, key)
            per_item[key] = {
                "status": "failed",
                "display_zh": zh,
                "unit": it["unit"],
                "icon": it["icon"],
                "error": str(exc),
                "traceback": traceback.format_exc(limit=4),
            }

    finished_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    n_ok = sum(1 for v in per_item.values() if v.get("status") == "ok")

    manifest = {
        "run_id": run_id,
        "kind": "prices",
        "started_at": started_at,
        "finished_at": finished_at,
        "data_end_date": overall_end.strftime("%Y-%m-%d") if overall_end is not None else None,
        "source_file": Path(xlsx_path).name,
        "seed": seed,
        "n_sim": n_sim,
        "repetitions": repetitions,
        "train_months": train_months,
        "library_versions": _lib_versions(),
        "n_ok": n_ok,
        "n_failed": len(items) - n_ok,
        "items": [
            {"key": it["key"], "zh": it["zh"], "unit": it["unit"], "icon": it["icon"]}
            for it in items
        ],
        "categories": per_item,
    }
    storage.write_manifest(base_dir, run_id, manifest)

    if n_ok > 0:
        storage.set_latest(base_dir, run_id)
        try:
            storage.prune_old_runs(base_dir, keep=keep_runs)
        except Exception:
            log.exception("prune_old_runs failed (non-fatal)")

    log.info("[price-run %s] done ok=%d failed=%d", run_id, n_ok, len(items) - n_ok)
    return manifest


def _lib_versions() -> dict:
    import numpy
    import pmdarima
    import scipy
    import statsmodels

    return {
        "pmdarima": pmdarima.__version__,
        "statsmodels": statsmodels.__version__,
        "numpy": numpy.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
    }
