import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { usePriceForecast, usePriceLatestRun, usePriceRun } from "@/hooks/usePrices";
import ForecastChart from "@/components/charts/ForecastChart";
import ManifestPanel from "@/components/manifest/ManifestPanel";
import DownloadButtons from "@/components/downloads/DownloadButtons";
import ErrorPanel from "@/components/feedback/ErrorPanel";
import { ChartSkeleton } from "@/components/feedback/LoadingSkeleton";
import { fmtMonth, fmtNum } from "@/lib/format";
import type { ForecastPayload } from "@/types/api";

export default function PriceCategoryPage() {
  const { slug = "" } = useParams();
  const priceLatest = usePriceLatestRun();
  const runId = priceLatest.data?.run_id;
  const { data: manifest } = usePriceRun(runId);
  const { data, isLoading, isError, error, refetch } = usePriceForecast(
    runId,
    slug,
  );
  const [mode, setMode] = useState<"level" | "yoy">("level");

  if (priceLatest.isError) {
    return (
      <ErrorPanel
        title="尚未有價格預測"
        detail="請先用 scripts/forecast_prices.py 跑一次價格預測。"
      />
    );
  }

  const unit = data?.unit ?? undefined;
  const zh = data?.display_zh ?? slug;
  const icon = data?.icon ?? "💰";

  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-3">
        <Link to="/" className="text-sm text-indigo-600 hover:underline">
          ← 回儀表板
        </Link>
        <span className="text-3xl leading-none">{icon}</span>
        <h1 className="text-2xl font-semibold text-slate-900">{zh}</h1>
        {unit && <span className="text-sm text-slate-400">單位：{unit}</span>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        <div className="space-y-3">
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="inline-flex rounded-md border border-slate-200 bg-slate-50 p-0.5 text-xs">
              <TabBtn
                active={mode === "level"}
                onClick={() => setMode("level")}
                label="月度價格水準"
              />
              <TabBtn
                active={mode === "yoy"}
                onClick={() => setMode("yoy")}
                label="年度 YoY 滾動預測"
              />
            </div>
            <div className="mt-3">
              {isLoading && <ChartSkeleton />}
              {isError && (
                <ErrorPanel
                  title="無法載入預測"
                  detail={(error as Error)?.message}
                  onRetry={() => refetch()}
                />
              )}
              {data && mode === "level" && (
                <ProbRisePanel data={data} unit={unit} />
              )}
              {data && (
                <ForecastChart
                  data={data}
                  mode={mode}
                  seriesLabel="價格"
                  yAxisTitle={unit ? `價格（${unit}）` : "價格"}
                />
              )}
            </div>
          </div>
        </div>

        <div className="space-y-3">
          {data && <ManifestPanel forecast={data} manifest={manifest} />}
          {runId && (
            <DownloadButtons runId={runId} category={slug} variant="price" />
          )}
        </div>
      </div>
    </div>
  );
}

function ProbRisePanel({
  data,
  unit,
}: {
  data: ForecastPayload;
  unit?: string;
}) {
  const prob = data.prob_rise_next_month;
  if (
    prob === null ||
    data.last_actual_value === null ||
    !data.next_forecast_date
  ) {
    return null;
  }
  const pct = (prob * 100).toFixed(1);
  const color =
    prob >= 0.5 ? "text-rose-600 bg-rose-50" : "text-slate-600 bg-slate-100";
  const u = unit ? ` ${unit}` : "";
  return (
    <div className="mb-3 flex items-baseline justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
      <div>
        <span className="font-semibold text-slate-900">
          {fmtMonth(data.next_forecast_date)}
        </span>
        <span className="text-slate-500">
          {" "}
          上漲機率（vs. {fmtNum(data.last_actual_value)}
          {u}）
        </span>
        <span className="ml-2 text-xs text-slate-400">
          由 10,000 條模擬路徑計算
        </span>
      </div>
      <div className={`rounded px-2 py-0.5 font-semibold ${color}`}>{pct}%</div>
    </div>
  );
}

function TabBtn({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "px-3 py-1.5 rounded text-sm",
        active
          ? "bg-white shadow text-indigo-700 font-medium"
          : "text-slate-600 hover:text-slate-900",
      ].join(" ")}
    >
      {label}
    </button>
  );
}
