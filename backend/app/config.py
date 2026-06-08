from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ADMIN_TOKEN: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    # 留空＝自動組出最新的 SDMX 查詢網址（含當年 endTime）；
    # 只有要覆蓋來源時才填整段 SDMX URL。
    DGBAS_URL: str = ""
    DATA_DIR: str = "./data/forecasts"
    # 非 CPI 的「實際價格」預測（例：雞蛋產地價格），與 CPI 分開存放。
    PRICES_DATA_DIR: str = "./data/forecasts_prices"
    KEEP_RUNS: int = 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
