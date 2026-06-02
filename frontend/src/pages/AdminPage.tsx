import { useAdminToken } from "@/hooks/useAdminToken";
import { useTriggerRun } from "@/hooks/useTriggerRun";
import AdminTokenField from "@/components/admin/AdminTokenField";
import ProgressBar from "@/components/admin/ProgressBar";

export default function AdminPage() {
  const { token } = useAdminToken();
  const { trigger, status } = useTriggerRun();
  const running = status?.state === "running";

  return (
    <div className="max-w-2xl space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">管理頁面</h1>
        <p className="mt-1 text-sm text-slate-600">
          觸發一次完整預測：從主計總處 dataset 6019 抓取最新 CPI 月資料，
          對 14 類別配適 SARIMA 並做 10,000 次蒙地卡羅模擬。預計需時 6–9 分鐘。
        </p>
      </header>

      <section className="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
        <AdminTokenField />
        <button
          type="button"
          disabled={!token || running || trigger.isPending}
          onClick={() => trigger.mutate()}
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {running ? "執行中…" : "重新抓取資料並預測"}
        </button>
        {!token && (
          <p className="text-xs text-amber-600">
            請先輸入 ADMIN_TOKEN 才能觸發。
          </p>
        )}
      </section>

      {status && (
        <section className="space-y-2">
          <h2 className="text-sm font-medium text-slate-600">執行進度</h2>
          <ProgressBar status={status} />
          <p className="text-xs text-slate-400 font-mono break-all">
            run_id: {status.run_id}
          </p>
        </section>
      )}

      <section className="text-xs text-slate-500 leading-relaxed border-t border-slate-200 pt-4">
        <p>
          說明：執行成功會自動更新「最新執行」指標，並會自動清除超出保留數量的舊
          run（預設保留 12 個）。任何時候都可以從「執行歷程」回看歷史 run。
        </p>
        <p className="mt-1">
          若失敗，會在進度區塊顯示錯誤訊息；最常見原因是 DGBAS 來源 URL 變更或網路問題。
        </p>
      </section>
    </div>
  );
}
