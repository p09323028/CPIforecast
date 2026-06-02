import type { ForecastPayload, RunManifest } from "@/types/api";
import { fmtDate, fmtDateTime, fmtNum } from "@/lib/format";

export default function ManifestPanel({
  forecast,
  manifest,
}: {
  forecast: ForecastPayload;
  manifest?: RunManifest;
}) {
  const orderText = `(${forecast.order.join(",")})(${forecast.seasonal_order.join(",")})`;
  return (
    <aside className="rounded-lg border border-slate-200 bg-white p-4 text-sm">
      <h3 className="font-semibold text-slate-800 mb-3">模型資訊</h3>
      <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1.5 text-slate-700">
        <dt className="text-slate-500">ARIMA 階數</dt>
        <dd className="font-mono">{orderText}</dd>
        <dt className="text-slate-500">BIC</dt>
        <dd className="font-mono">{fmtNum(forecast.bic, 3)}</dd>
        <dt className="text-slate-500">訓練資料</dt>
        <dd>
          {fmtDate(forecast.train_start)} ~ {fmtDate(forecast.train_end)}
        </dd>
        <dt className="text-slate-500">資料截至</dt>
        <dd>{forecast.data_end_date ?? "—"}</dd>
        {manifest && (
          <>
            <dt className="text-slate-500">seed</dt>
            <dd className="font-mono">{manifest.seed ?? "—"}</dd>
            <dt className="text-slate-500">n_sim（月數）</dt>
            <dd className="font-mono">{manifest.n_sim ?? "—"}</dd>
            <dt className="text-slate-500">repetitions</dt>
            <dd className="font-mono">
              {manifest.repetitions?.toLocaleString() ?? "—"}
            </dd>
            <dt className="text-slate-500">train_months</dt>
            <dd className="font-mono">{manifest.train_months ?? "—"}</dd>
            <dt className="text-slate-500">run 起始</dt>
            <dd>{fmtDateTime(manifest.started_at)}</dd>
            {manifest.library_versions && (
              <>
                <dt className="text-slate-500">pmdarima</dt>
                <dd className="font-mono">
                  {manifest.library_versions.pmdarima}
                </dd>
                <dt className="text-slate-500">statsmodels</dt>
                <dd className="font-mono">
                  {manifest.library_versions.statsmodels}
                </dd>
              </>
            )}
          </>
        )}
      </dl>
    </aside>
  );
}
