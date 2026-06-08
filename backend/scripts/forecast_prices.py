"""讀填好的價格 Excel，跑預測，輸出到 PRICES_DATA_DIR。

用法：
    python scripts/forecast_prices.py
    python scripts/forecast_prices.py path/to/price_template.xlsx
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import settings  # noqa: E402
from forecast import prices_runner  # noqa: E402

DEFAULT_XLSX = ROOT / "data" / "price_inputs" / "price_template.xlsx"


def main() -> None:
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_XLSX
    if not xlsx.exists():
        raise SystemExit(f"找不到 Excel：{xlsx}")
    base_dir = str(ROOT / settings.PRICES_DATA_DIR.lstrip("./"))
    print(f"reading {xlsx}")
    print(f"output  {base_dir}")
    manifest = prices_runner.run_prices(
        xlsx, base_dir, keep_runs=settings.KEEP_RUNS
    )
    print(
        f"done. run={manifest['run_id']} ok={manifest['n_ok']} "
        f"failed={manifest['n_failed']} items={[i['key'] for i in manifest['items']]}"
    )


if __name__ == "__main__":
    main()
