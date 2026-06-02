import { useRuns } from "@/hooks/useRuns";
import { useSelectedRunId } from "@/hooks/useSelectedRunId";
import { fmtDateTime } from "@/lib/format";

export default function RunSelector() {
  const { data: runs, isLoading } = useRuns();
  const { runId, setRunId, isLatest } = useSelectedRunId();

  if (isLoading || !runs?.length) {
    return <span className="text-xs text-slate-400">尚未有執行</span>;
  }

  return (
    <label className="flex items-center gap-2 text-xs text-slate-600">
      <span>檢視執行</span>
      <select
        value={runId ?? ""}
        onChange={(e) => setRunId(e.target.value || null)}
        className="rounded border border-slate-300 bg-white px-2 py-1 text-xs"
      >
        {runs.map((r, i) => (
          <option key={r.run_id} value={r.run_id}>
            {i === 0 ? "（最新）" : ""}
            {fmtDateTime(r.started_at)} ・ {r.data_end_date ?? "?"}
          </option>
        ))}
      </select>
      {!isLatest && (
        <button
          type="button"
          onClick={() => setRunId(null)}
          className="text-indigo-600 hover:underline"
        >
          回到最新
        </button>
      )}
    </label>
  );
}
