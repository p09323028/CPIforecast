from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ADMIN_TOKEN: str = ""
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    DGBAS_URL: str = (
        "https://ws.dgbas.gov.tw/001/Upload/461/relfile/11525/230543/pr0101a3m.xml"
    )
    DATA_DIR: str = "./data/forecasts"
    KEEP_RUNS: int = 12

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
