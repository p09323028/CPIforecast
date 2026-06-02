import type { AdminStatus } from "@/types/api";
import { zh } from "@/lib/categories";

export default function ProgressBar({ status }: { status: AdminStatus }) {
  const pct =
    status.total > 0
      ? Math.round((status.current_index / status.total) * 100)
      : 0;
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-baseline justify-between text-sm">
        <span className="font-semibold text-slate-800">
          {status.state === "running" ? "執行中" : status.state}
        </span>
        <span className="text-slate-500">
          {status.current_index} / {status.total}
        </span>
      </div>
      <div className="mt-2 h-2 w-full rounded bg-slate-100 overflow-hidden">
        <div
          className="h-2 bg-indigo-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      {status.current_category && (
        <p className="mt-2 text-xs text-slate-500">
          當前類別：
          <span className="font-medium text-slate-700">
            {zh(status.current_category)}
          </span>{" "}
          <span className="font-mono">{status.current_category}</span>
        </p>
      )}
      {status.error && (
        <p className="mt-2 text-xs text-red-600">錯誤：{status.error}</p>
      )}
    </div>
  );
}
