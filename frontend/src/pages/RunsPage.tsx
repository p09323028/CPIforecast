import { useNavigate } from "react-router-dom";
import { useRuns, useLatestRun } from "@/hooks/useRuns";
import { fmtDateTime } from "@/lib/format";
import { RowSkeleton } from "@/components/feedback/LoadingSkeleton";
import EmptyState from "@/components/feedback/EmptyState";

export default function RunsPage() {
  const { data: runs, isLoading } = useRuns();
  const { data: latest } = useLatestRun();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <RowSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (!runs?.length) {
    return (
      <EmptyState
        title="尚無執行紀錄"
        description="預測完成後，每次執行會出現在這裡。"
        ctaLabel="觸發第一次執行"
        ctaTo="/admin"
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th className="px-4 py-2">Run ID</th>
            <th className="px-4 py-2">起始</th>
            <th className="px-4 py-2">完成</th>
            <th className="px-4 py-2">資料截至</th>
            <th className="px-4 py-2">成功</th>
            <th className="px-4 py-2">失敗</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {runs.map((r) => (
            <tr key={r.run_id} className="hover:bg-slate-50">
              <td className="px-4 py-2 font-mono text-xs">
                {r.run_id}
                {latest?.run_id === r.run_id && (
                  <span className="ml-2 rounded bg-indigo-50 text-indigo-700 px-1.5 py-0.5 text-[10px]">
                    最新
                  </span>
                )}
              </td>
              <td className="px-4 py-2 text-slate-700">
                {fmtDateTime(r.started_at)}
              </td>
              <td className="px-4 py-2 text-slate-700">
                {fmtDateTime(r.finished_at)}
              </td>
              <td className="px-4 py-2">{r.data_end_date ?? "—"}</td>
              <td className="px-4 py-2 text-emerald-700">{r.n_ok ?? "—"}</td>
              <td className="px-4 py-2 text-red-700">{r.n_failed ?? "—"}</td>
              <td className="px-4 py-2">
                <button
                  type="button"
                  onClick={() => navigate(`/?run_id=${r.run_id}`)}
                  className="text-indigo-600 hover:underline text-xs"
                >
                  檢視
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
