import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useSelectedRunId } from "@/hooks/useSelectedRunId";
import { useRun } from "@/hooks/useRuns";
import { useForecast } from "@/hooks/useForecast";
import ForecastChart from "@/components/charts/ForecastChart";
import ManifestPanel from "@/components/manifest/ManifestPanel";
import DownloadButtons from "@/components/downloads/DownloadButtons";
import ErrorPanel from "@/components/feedback/ErrorPanel";
import { ChartSkeleton } from "@/components/feedback/LoadingSkeleton";
import { zh, icon } from "@/lib/categories";
import { fmtMonth, fmtNum } from "@/lib/format";
import type { ForecastPayload } from "@/types/api";

export default function CategoryPage() {
  const { slug = "" } = useParams();
  const { runId } = useSelectedRunId();
  const { data: manifest } = useRun(runId);
  const { data, isLoading, isError, error, refetch } = useForecast(runId, slug);
  const [mode, setMode] = useState<"level" | "yoy">("level");

  if (!runId) {
    return (
      <ErrorPanel
        title="尚未有預測"
        detail="請先觸發一次預測，再回來查看此類別。"
      />
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-3">
        <Link to={`/?${runId ? `run_id=${runId}` : ""}`} className="text-sm text-indigo-600 hover:underline">
          ← 回儀表板
        </Link>
        <span className="text-3xl leading-none">{icon(slug)}</span>
        <h1 className="text-2xl font-semibold text-slate-900">{zh(slug)}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        <div className="space-y-3">
          <div className="rounded-lg border border-slate-200 bg-white p-4">
            <div className="inline-flex rounded-md border border-slate-200 bg-slate-50 p-0.5 text-xs">
              <TabBtn
                active={mode === "level"}
                onClick={() => setMode("level")}
                label="月度 CPI 水準"
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
              {data && mode === "level" && <ProbRisePanel data={data} />}
              {data && <ForecastChart data={data} mode={mode} />}
            </div>
          </div>
        </div>

        <div className="space-y-3">
          {data && <ManifestPanel forecast={data} manifest={manifest} />}
          {runId && <DownloadButtons runId={runId} category={slug} />}
        </div>
      </div>
    </div>
  );
}

function ProbRisePanel({ data }: { data: ForecastPayload }) {
  const prob = data.prob_rise_next_month;
  if (prob === null || data.last_actual_value === null || !data.next_forecast_date) {
    return null;
  }
  const pct = (prob * 100).toFixed(1);
  const color = prob >= 0.5 ? "text-rose-600 bg-rose-50" : "text-slate-600 bg-slate-100";
  return (
    <div className="mb-3 flex items-baseline justify-between rounded-md border border-slate-200 bg-white px-3 py-2 text-sm">
      <div>
        <span className="font-semibold text-slate-900">
          {fmtMonth(data.next_forecast_date)}
        </span>
        <span className="text-slate-500">
          {" "}
          上漲機率（vs. {fmtNum(data.last_actual_value)}）
        </span>
        <span className="ml-2 text-xs text-slate-400">
          由 10,000 條模擬路徑計算
        </span>
      </div>
      <div className={`rounded px-2 py-0.5 font-semibold ${color}`}>
        {pct}%
      </div>
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
