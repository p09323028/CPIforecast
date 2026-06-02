import type { ForecastPayload } from "@/types/api";
import { api, downloadUrl } from "./client";

export const getForecast = (runId: string, category: string) =>
  api<ForecastPayload>(`/api/forecast/${runId}/${category}`);

export const monthlyCsvUrl = (runId: string, category: string) =>
  downloadUrl(`/api/download/${runId}/${category}/monthly.csv`);

export const yoyCsvUrl = (runId: string, category: string) =>
  downloadUrl(`/api/download/${runId}/${category}/yoy.csv`);

export const rollingYoyCsvUrl = (runId: string, category: string) =>
  downloadUrl(`/api/download/${runId}/${category}/rolling_yoy.csv`);

export const pathsParquetUrl = (runId: string, category: string) =>
  downloadUrl(`/api/download/${runId}/${category}/paths.parquet`);

export const rawCpiCsvUrl = (runId: string) =>
  downloadUrl(`/api/download/${runId}/raw_cpi.csv`);

export const reportXlsxUrl = (runId: string) =>
  downloadUrl(`/api/download/${runId}/report.xlsx`);
