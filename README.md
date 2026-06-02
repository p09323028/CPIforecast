# 台灣 CPI 預測平台

針對行政院主計總處 [dataset 6019](https://data.gov.tw/dataset/6019) 月頻 CPI，
對 14 類別（食物類、外食費、肉/豬/牛/雞、水產品、蛋/雞蛋、乳/鮮乳、蔬菜、水果、食用油）
依 USDA TB-1957 方法配適 SARIMA + 10,000 次蒙地卡羅模擬，並提供網站平台檢視與下載。

- 後端：FastAPI（Python，沿用原 notebook 之 `pmdarima` + `statsmodels`，產出與 notebook 完全等價）
- 前端：React + Vite + TypeScript + Plotly.js + Tailwind
- 部署：Render（Web Service + Cron Job + Static Site + Persistent Disk）
- 儲存：純檔案（Parquet / CSV / JSON），無資料庫

> 原始 notebook `CPIforecast.ipynb` 不動。本平台只是把 notebook 邏輯包成可重複呼叫的服務。

## 目錄結構

```
CPIforecast/
├── CPIforecast.ipynb     # 原本的 notebook（用來交叉檢查網站結果）
├── backend/              # FastAPI app + 預測模組
└── frontend/             # React SPA
```

## 本地開發

### 1. 後端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# 編輯 .env，把 ADMIN_TOKEN 改成 ≥32 字元的隨機字串

# 先跑一次預測，產生 data/forecasts/ 資料（約 6–9 分鐘）
python scripts/seed_local_run.py

# 啟動 API
uvicorn app.main:app --reload
# → http://localhost:8000
```

API 文件自動產生於 `http://localhost:8000/docs`。

### 2. 前端

```powershell
cd frontend
npm ci
Copy-Item .env.example .env   # 預設指向 http://localhost:8000

npm run dev
# → http://localhost:5173
```

### 3. 自我測試

```powershell
# 後端單元測試
cd backend
pytest

# 前端型別檢查
cd ../frontend
npm run typecheck
```

## 主要 API 端點

| Method | Path | 用途 |
|---|---|---|
| GET | `/api/health` | 服務狀態 + 最新 run_id |
| GET | `/api/runs` | 列出所有執行（新→舊） |
| GET | `/api/runs/latest` | 取得最新 run_id |
| GET | `/api/runs/{run_id}` | 完整 manifest（含每類別 order/BIC/status） |
| GET | `/api/categories` | 14 類別中英對應 |
| GET | `/api/forecast/{run_id}/{category}` | 圖表用 JSON |
| GET | `/api/download/{run_id}/{category}/monthly.csv` | 月度分位數 CSV |
| GET | `/api/download/{run_id}/{category}/yoy.csv` | YoY 年變動率 CSV |
| GET | `/api/download/{run_id}/{category}/paths.parquet` | 10,000 條完整模擬路徑 |
| GET | `/api/download/{run_id}/raw_cpi.csv` | 本次訓練資料 |
| POST | `/api/admin/trigger` 🔒 | 觸發背景重算 |
| GET | `/api/admin/status/{run_id}` 🔒 | 執行進度（給前端輪詢） |

🔒 = 需 `Authorization: Bearer <ADMIN_TOKEN>`。

## 與 notebook 交叉檢查

平台每次執行會把以下檔案放在 `data/forecasts/runs/{run_id}/`：

- `manifest.json`：完整 metadata（seed、n_sim、repetitions、各類別 ARIMA order/BIC、套件版本）
- `raw_cpi.csv`：本次抓到的 14 類別月度 CPI（用於 notebook 重現訓練資料）
- `{category}/quantiles_monthly.csv`：月度 0.025 / 0.5 / 0.975 分位數
- `{category}/quantiles_yoy.csv`：年度 YoY% 0.025 / 0.5 / 0.975 分位數
- `{category}/paths.parquet`：完整 10,000 條模擬路徑

在 `CPIforecast.ipynb` 中可這樣比對：

```python
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

# 1. 用網站下載的 raw_cpi.csv，重現訓練資料
df = pd.read_csv("raw_cpi_<run_id>.csv", index_col="date", parse_dates=True).asfreq("MS")

# 2. 用 manifest.json 內的 order/seasonal_order 重現模型
order = (0, 1, 2)            # 從 manifest.categories.Food.order 取得
seasonal_order = (1, 0, 1, 12)  # 從 manifest.categories.Food.seasonal_order

y_train = df["Food"].dropna().iloc[-144:]
res = SARIMAX(y_train, order=order, seasonal_order=seasonal_order).fit()

# 3. 用相同 seed 重現模擬路徑
sim = res.simulate(nsimulations=20, repetitions=10_000, anchor="end", random_state=1)

# 4. 與網站下載的 Parquet 比對
website_paths = pd.read_parquet("Food_paths_<run_id>.parquet")
# sim 與 website_paths 應 element-wise 等值（取至小數第 6 位）
```

## Render 部署

倉庫包含 `backend/render.yaml`，定義三個服務：

1. **cpi-api**（FastAPI Web Service）— 掛載 1 GB persistent disk 於 `/var/data`
2. **cpi-monthly-recompute**（Cron Job）— 每月 7 號 19:00 UTC（台北 8 號 03:00）自動觸發
3. **cpi-frontend**（Static Site）— 由 `frontend/` 編譯出 `dist/`

部署步驟：

1. 推到 GitHub
2. Render → New → Blueprint，選你的 repo
3. 三個服務需手動填入的環境變數：
   - `cpi-api`：`ADMIN_TOKEN`（≥32 字元）、`FRONTEND_ORIGIN`（前端網址）
   - `cpi-monthly-recompute`：`WEB_URL`（後端網址，如 `https://cpi-api.onrender.com`）、`ADMIN_TOKEN`
   - `cpi-frontend`：`VITE_API_BASE_URL`（後端網址）
4. 第一次部署完成後，連到前端 → 管理頁 → 觸發第一次預測

> Render Free / Starter 方案的 Web Service 在閒置時可能會休眠；觸發預測前可先連到首頁喚醒它。

## 邊界情境

- **DGBAS XML URL 變更**：改 `DGBAS_URL` 環境變數即可，不需重新部署。
- **單一類別預測失敗**：runner try/except 包住每類別，manifest 會記 `{"status":"failed","error":...}`；其餘類別正常顯示，前端對應頁顯示「此類別於本次執行失敗」。
- **執行中重啟**：startup 不會把缺 `finished_at` 的 run 晉升為最新；下次觸發會建立新 run。
- **磁碟容量**：每 run ≈ 30 MB，`KEEP_RUNS=12` 預設約 360 MB；可調整。

## 授權與致謝

- 原始預測流程：`CPIforecast.ipynb`（使用者實作）
- 模型方法：USDA TB-1957 SARIMA 配適
- 資料來源：行政院主計總處 dataset 6019
