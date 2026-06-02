"""檔案路徑、原子寫入、latest pointer。"""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

LATEST_FILE = "latest.txt"
MANIFEST_FILE = "manifest.json"
RAW_CSV = "raw_cpi.csv"
MONTHLY_CSV = "quantiles_monthly.csv"
YOY_CSV = "quantiles_yoy.csv"
ROLLING_YOY_CSV = "rolling_yoy.csv"
PATHS_PARQUET = "paths.parquet"


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def data_dir(base: str | os.PathLike) -> Path:
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    (p / "runs").mkdir(exist_ok=True)
    return p


def run_dir(base: str | os.PathLike, run_id: str) -> Path:
    p = data_dir(base) / "runs" / run_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def category_dir(base: str | os.PathLike, run_id: str, category: str) -> Path:
    p = run_dir(base, run_id) / category
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_manifest(base: str | os.PathLike, run_id: str, manifest: dict) -> None:
    path = run_dir(base, run_id) / MANIFEST_FILE
    tmp = path.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, default=str)
    os.replace(tmp, path)


def read_manifest(base: str | os.PathLike, run_id: str) -> dict:
    path = run_dir(base, run_id) / MANIFEST_FILE
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_raw_cpi(base: str | os.PathLike, run_id: str, df: pd.DataFrame) -> None:
    path = run_dir(base, run_id) / RAW_CSV
    df.to_csv(path, index_label="date")


def write_category_outputs(
    base: str | os.PathLike,
    run_id: str,
    category: str,
    monthly_df: pd.DataFrame,
    yoy_df: pd.DataFrame,
    paths_df: pd.DataFrame,
    rolling_yoy_df: pd.DataFrame | None = None,
) -> None:
    cdir = category_dir(base, run_id, category)
    monthly_df.to_csv(cdir / MONTHLY_CSV, index_label="date")
    yoy_df.to_csv(cdir / YOY_CSV, index_label="year")
    paths_df.to_parquet(cdir / PATHS_PARQUET, compression="snappy")
    if rolling_yoy_df is not None and not rolling_yoy_df.empty:
        rolling_yoy_df.to_csv(cdir / ROLLING_YOY_CSV, index_label="end_date")


def set_latest(base: str | os.PathLike, run_id: str) -> None:
    path = data_dir(base) / LATEST_FILE
    tmp = path.with_suffix(".txt.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(run_id)
    os.replace(tmp, path)


def get_latest_run_id(base: str | os.PathLike) -> str | None:
    path = data_dir(base) / LATEST_FILE
    if not path.exists():
        return None
    rid = path.read_text(encoding="utf-8").strip()
    return rid or None


def list_run_ids(base: str | os.PathLike) -> list[str]:
    runs_root = data_dir(base) / "runs"
    if not runs_root.exists():
        return []
    return sorted(
        [p.name for p in runs_root.iterdir() if p.is_dir()],
        reverse=True,
    )


def prune_old_runs(base: str | os.PathLike, keep: int = 12) -> list[str]:
    """Delete the oldest runs while keeping `keep` most recent.

    Never deletes the run pointed at by latest.txt.
    """
    latest = get_latest_run_id(base)
    runs = list_run_ids(base)
    to_delete = runs[keep:]
    deleted: list[str] = []
    for rid in to_delete:
        if rid == latest:
            continue
        shutil.rmtree(data_dir(base) / "runs" / rid, ignore_errors=True)
        deleted.append(rid)
    return deleted
