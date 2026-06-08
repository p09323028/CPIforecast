import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useSelectedRunId } from "@/hooks/useSelectedRunId";
import { useRun, useLatestRun } from "@/hooks/useRuns";
import { useCategories } from "@/hooks/useCategories";
import { getForecast, reportXlsxUrl } from "@/api/forecast";
import CategoryCard from "@/components/cards/CategoryCard";
import PriceCard from "@/components/cards/PriceCard";
import { usePriceCategories, usePriceLatestRun } from "@/hooks/usePrices";
import EmptyState from "@/components/feedback/EmptyState";
import { CardSkeleton } from "@/components/feedback/LoadingSkeleton";
import { fmtDateTime } from "@/lib/format";
import { CATEGORY_ORDER } from "@/lib/categories";

export default function DashboardPage() {
  const { runId } = useSelectedRunId();
  const latest = useLatestRun();
  const { data: manifest } = useRun(runId);
  const { data: categories } = useCategories();
  const priceLatest = usePriceLatestRun();
  const { data: priceCategories } = usePriceCategories();
  const priceRunId = priceLatest.data?.run_id;
  const qc = useQueryClient();

  useEffect(() => {
    if (!runId || !categories) return;
    for (const c of categories) {
      qc.prefetchQuery({
        queryKey: ["forecast", runId, c.en],
        queryFn: () => getForecast(runId, c.en),
        staleTime: 5 * 60_000,
      });
    }
  }, [runId, categories, qc]);

  if (latest.isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {Array.from({ length: 14 }).map((_, i) => (
          <CardSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (!runId) {
    return (
      <EmptyState
        title="尚未有任何預測"
        description="請至「管理」頁面用 ADMIN_TOKEN 觸發第一次執行（約 6–9 分鐘）。"
        ctaLabel="前往管理頁"
        ctaTo="/admin"
      />
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
          <h1 className="text-xl font-semibold text-slate-900">
            台灣 CPI 預測（14 類別）
          </h1>
          <a
            href={reportXlsxUrl(runId)}
            className="inline-flex items-center gap-1.5 rounded-md border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 hover:bg-indigo-100 hover:border-indigo-300"
            download
          >
            <span aria-hidden>📊</span>
            下載月報 (xlsx)
          </a>
        </div>
        <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <Field label="資料更新至" value={manifest?.data_end_date ?? "—"} />
          <Field
            label="最近執行起始"
            value={fmtDateTime(manifest?.started_at)}
          />
          <Field
            label="執行完成"
            value={fmtDateTime(manifest?.finished_at)}
          />
          <Field
            label="成功 / 失敗"
            value={`${manifest?.n_ok ?? "—"} / ${manifest?.n_failed ?? "—"}`}
          />
        </div>
      </section>

      <section>
        <h2 className="text-sm font-medium text-slate-600 mb-3">
          點擊查看單一類別預測詳細
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {CATEGORY_ORDER.map((en) => (
            <CategoryCard key={en} runId={runId} en={en} />
          ))}
        </div>
      </section>

      {priceRunId && priceCategories && priceCategories.length > 0 && (
        <section>
          <h2 className="text-sm font-medium text-slate-600 mb-1">
            價格預測（實際價格，非指數）
          </h2>
          <p className="text-xs text-slate-400 mb-3">
            與 CPI 相同模型（SARIMA + 10,000 條蒙地卡羅，未來 18 個月）。
            年變動率＝當年平均價 ÷ 前年平均價 − 1。
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {priceCategories.map((item) => (
              <PriceCard key={item.en} runId={priceRunId} item={item} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-slate-500">{label}</div>
      <div className="font-medium text-slate-800">{value}</div>
    </div>
  );
}
