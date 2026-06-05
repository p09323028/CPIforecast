"""主計總處 SDMX-JSON API 抓取、解析、樞紐成寬表。

2026-06 起資料來源由舊的靜態 XML（pr0101a3m.xml）改為 SDMX API：
    https://nstatdb.dgbas.gov.tw/dgbasAll/webMain.aspx?sdmx/A030101025/<fldids>...M.&startTime=...&endTime=...

回傳為 SDMX-JSON：
    data.structure.dimensions.series[0].values  -> 各序列對應的 fldid（依序）
    data.structure.dimensions.observation[0].values -> 月份清單（如 "2026-M5"）
    data.dataSets[0].series["k"].observations["i"] -> 第 k 序列、第 i 月的值 [value]
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import pandas as pd
import requests

from .categories import FLDID_TO_EN

log = logging.getLogger(__name__)

# DGBAS uses TWCA Secure SSL CA — not in certifi. Use the OS native trust
# store (Windows / macOS keychain / Linux system bundle) when available.
try:
    import truststore

    truststore.inject_into_ssl()
    log.debug("truststore: using OS-native CA bundle")
except ImportError:
    log.warning(
        "truststore not installed — falling back to certifi; DGBAS SSL may fail"
    )

# SDMX API 端點與查詢參數。
SDMX_ENDPOINT = "https://nstatdb.dgbas.gov.tw/dgbasAll/webMain.aspx"
DATASET_ID = "A030101025"
START_PERIOD = "1981-M1"


def _current_year_end_period() -> str:
    """endTime 取「當年 12 月」：永遠 >= 當月，未發布月份會回空值並被濾掉，
    因此每月只要重跑、不必手改 URL。"""
    return f"{datetime.now().year}-M12"


def build_url(start_period: str = START_PERIOD, end_period: str | None = None) -> str:
    """組合 14 類別的 SDMX 查詢網址。end_period 預設為當年 12 月。"""
    codes = "+".join(FLDID_TO_EN.keys())
    end = end_period or _current_year_end_period()
    return (
        f"{SDMX_ENDPOINT}?sdmx/{DATASET_ID}/{codes}...M."
        f"&startTime={start_period}&endTime={end}"
    )


# 模組載入時組出的預設網址（供 runner 預設參數與參考用）。實際抓取走 load_cleaned，
# url 為空時會即時重組，避免長壽的線上服務沿用啟動當下凍結的 endTime。
DEFAULT_URL = build_url()


def fetch_json(url: str = DEFAULT_URL, timeout: int = 60) -> dict:
    log.info("fetching DGBAS SDMX JSON: %s", url)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_sdmx_json(payload: dict) -> pd.DataFrame:
    """把 SDMX-JSON 解析成寬表：index=月初日期，columns=14 個英文類別名。

    依 fldid 代碼對應英文名（不靠中文品名）。未知代碼會被忽略。
    """
    structure = payload["data"]["structure"]["dimensions"]
    series_values = structure["series"][0]["values"]  # 依序對應 series key 0..n
    obs_values = structure["observation"][0]["values"]  # 月份清單

    dates: list[pd.Timestamp] = []
    for v in obs_values:
        year_str, month_str = v["id"].split("-M")
        dates.append(pd.Timestamp(int(year_str), int(month_str), 1))

    series = payload["data"]["dataSets"][0]["series"]
    columns: dict[str, list[float | None]] = {}
    for k, sval in enumerate(series_values):
        en = FLDID_TO_EN.get(str(sval["id"]))
        if en is None:
            log.warning("SDMX 回傳未知 fldid=%s，略過", sval["id"])
            continue
        obs = (series.get(str(k)) or {}).get("observations", {})
        col: list[float | None] = [None] * len(dates)
        for obs_idx, val in obs.items():
            i = int(obs_idx)
            v = val[0] if val else None
            # 尚未發布的月份 API 會回傳 0；CPI 指數恆為正，故 <=0 視為缺值。
            col[i] = float(v) if (v is not None and float(v) > 0) else None
        columns[en] = col

    wide = pd.DataFrame(columns, index=pd.DatetimeIndex(dates))
    wide = wide.sort_index().asfreq("MS")
    return wide


def select_categories(wide: pd.DataFrame) -> pd.DataFrame:
    """確認 14 個英文類別都在（parse 階段已用英文名建欄）。"""
    expected = list(FLDID_TO_EN.values())
    missing = [en for en in expected if en not in wide.columns]
    if missing:
        raise KeyError(
            f"SDMX 回傳缺少預期的類別：{missing}。可能來源結構或 fldid 代碼改變，請檢查。"
        )
    return wide[expected].sort_index().asfreq("MS").copy()


def load_cleaned(url: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Convenience: fetch + parse + select. Returns (df, meta).

    url 為空時即時組出最新查詢網址。
    """
    if not url:
        url = build_url()
    payload = fetch_json(url)
    wide = parse_sdmx_json(payload)
    df = select_categories(wide)
    df = df.dropna(how="all")
    last_actual = df.dropna(how="any").index.max()
    meta = {
        "dgbas_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_end_date": last_actual.strftime("%Y-%m-%d") if last_actual is not None else None,
        "rows": int(len(df)),
    }
    return df, meta
