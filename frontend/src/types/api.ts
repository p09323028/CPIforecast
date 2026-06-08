export interface CategoryPair {
  en: string;
  zh: string;
}

export interface RunSummary {
  run_id: string;
  started_at?: string | null;
  finished_at?: string | null;
  data_end_date?: string | null;
  n_ok?: number;
  n_failed?: number;
}

export interface RunManifestCategory {
  status: "ok" | "failed";
  order?: [number, number, number];
  seasonal_order?: [number, number, number, number];
  bic?: number;
  train_start?: string;
  train_end?: string;
  forecast_months?: number;
  forecast_start?: string;
  forecast_end?: string;
  error?: string;
}

export interface RunManifest extends RunSummary {
  dgbas_url?: string;
  fetched_at?: string;
  seed?: number;
  n_sim?: number;
  repetitions?: number;
  train_months?: number;
  library_versions?: Record<string, string>;
  categories?: Record<string, RunManifestCategory>;
}

export interface ForecastPoint {
  date: string;
  value: number;
}

export interface MonthlyBand {
  date: string;
  lower_95: number | null;
  median: number | null;
  upper_95: number | null;
  actual: number | null;
}

export interface AnnualYoy {
  year: number;
  lower_95: number;
  median: number;
  upper_95: number;
  base_actual: number;
}

export interface RollingYoyPoint {
  end_date: string;
  effective_end?: string;
  lower_95: number | null;
  median: number | null;
  upper_95: number | null;
  bic: number | null;
  order: number[] | null;
  seasonal_order: number[] | null;
}

export interface RollingYoy {
  forecast_year: number | null;
  base_actual: number | null;
  actual_yoy: number | null;
  start_end_date: string | null;
  end_end_date: string | null;
  n_iterations: number | null;
  points: RollingYoyPoint[];
}

export interface ForecastPayload {
  category: string;
  order: [number, number, number];
  seasonal_order: [number, number, number, number];
  bic: number;
  train_start?: string;
  train_end?: string;
  data_end_date?: string;
  history: ForecastPoint[];
  monthly: MonthlyBand[];
  prob_rise_next_month: number | null;
  last_actual_value: number | null;
  next_forecast_date: string | null;
  annual_yoy: AnnualYoy[];
  rolling_yoy: RollingYoy;
  // 僅價格預測（/api/prices）會帶以下欄位
  display_zh?: string | null;
  unit?: string | null;
  icon?: string | null;
}

export interface AdminStatus {
  run_id: string;
  state: "running" | "done" | "failed" | "unknown";
  started_at?: string | null;
  finished_at?: string | null;
  current_index: number;
  total: number;
  current_category?: string | null;
  error?: string | null;
}

export interface TriggerResponse {
  run_id: string;
  started_at: string;
}
