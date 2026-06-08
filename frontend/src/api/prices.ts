import type { ForecastPayload, RunManifest } from "@/types/api";
import { api, downloadUrl } from "./client";

export interface PriceCategory {
  en: string; // 後端資料夾 key，例：egg_farm
  zh: string;
  unit?: string | null;
  icon?: string | null;
}

export const listPriceCategories = () =>
  api<PriceCategory[]>("/api/prices/categories");

export const getPriceLatestRun = () =>
  api<{ run_id: string }>("/api/prices/runs/latest");

export const getPriceForecast = (runId: string, item: string) =>
  api<ForecastPayload>(`/api/prices/forecast/${runId}/${item}`);

export const getPriceRun = (runId: string) =>
  api<RunManifest>(`/api/prices/runs/${runId}`);

export const priceMonthlyCsvUrl = (runId: string, item: string) =>
  downloadUrl(`/api/prices/download/${runId}/${item}/monthly.csv`);

export const priceYoyCsvUrl = (runId: string, item: string) =>
  downloadUrl(`/api/prices/download/${runId}/${item}/yoy.csv`);

export const priceRollingYoyCsvUrl = (runId: string, item: string) =>
  downloadUrl(`/api/prices/download/${runId}/${item}/rolling_yoy.csv`);

export const pricePathsParquetUrl = (runId: string, item: string) =>
  downloadUrl(`/api/prices/download/${runId}/${item}/paths.parquet`);

export const priceRawCsvUrl = (runId: string) =>
  downloadUrl(`/api/prices/download/${runId}/prices.csv`);
