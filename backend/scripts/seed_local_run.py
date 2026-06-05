"""Run one full forecast locally and write to data/ — useful before first
boot of the API so the dashboard isn't empty.

Usage:
    cd backend
    python scripts/seed_local_run.py
"""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from forecast import storage  # noqa: E402
from forecast.runner import run_full  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> None:
    base = os.environ.get("DATA_DIR", "./data/forecasts")
    # 留空＝自動組出最新 SDMX 查詢網址（每月不必手改）。
    url = os.environ.get("DGBAS_URL", "")
    run_id = storage.new_run_id()
    print(f"starting local run {run_id} → {base}")
    run_full(base, run_id, dgbas_url=url)
    print("done. latest =", storage.get_latest_run_id(base))


if __name__ == "__main__":
    main()
