"""DGBAS XML 抓取、解析、樞紐成寬表。完全沿用 notebook 流程。"""
from __future__ import annotations

import io
import logging
from datetime import datetime, timezone

import pandas as pd
import requests

from .categories import CATEGORIES

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

DEFAULT_URL = (
    "https://ws.dgbas.gov.tw/001/Upload/461/relfile/11525/230543/pr0101a3m.xml"
)


def fetch_xml(url: str = DEFAULT_URL, timeout: int = 60) -> bytes:
    log.info("fetching DGBAS XML: %s", url)
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def parse_to_wide(xml_bytes: bytes) -> pd.DataFrame:
    """Parse XML and pivot to wide DataFrame indexed by month-start, columns=Item names."""
    data = pd.read_xml(io.BytesIO(xml_bytes))
    data["date"] = pd.to_datetime(
        data["TIME_PERIOD"].str.replace("M", "-", regex=False) + "-01"
    )
    data = data[(data["FREQ"] == "M") & (data["TYPE"] == "原始值")].copy()
    data["Item"] = data["Item"].str.replace("(指數基期：民國110年=100)", "", regex=False)
    data["Item_VALUE"] = pd.to_numeric(data["Item_VALUE"], errors="coerce")

    wide = (
        data.pivot_table(
            index="date", columns="Item", values="Item_VALUE", aggfunc="first"
        )
        .sort_index()
        .asfreq("MS")
    )
    return wide


def select_categories(wide: pd.DataFrame) -> pd.DataFrame:
    """Project wide df down to the 14 categories and rename to English."""
    missing = [zh for zh in CATEGORIES if zh not in wide.columns]
    if missing:
        raise KeyError(
            f"DGBAS XML 缺少預期的類別欄位：{missing}。可能來源結構改變，請檢查。"
        )
    selected = wide[list(CATEGORIES.keys())].rename(columns=CATEGORIES).copy()
    selected = selected.sort_index().asfreq("MS")
    return selected


def load_cleaned(url: str = DEFAULT_URL) -> tuple[pd.DataFrame, dict]:
    """Convenience: fetch + parse + select. Returns (df, meta)."""
    xml_bytes = fetch_xml(url)
    wide = parse_to_wide(xml_bytes)
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
