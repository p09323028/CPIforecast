import {
  monthlyCsvUrl,
  yoyCsvUrl,
  rollingYoyCsvUrl,
  pathsParquetUrl,
  rawCpiCsvUrl,
} from "@/api/forecast";

export default function DownloadButtons({
  runId,
  category,
}: {
  runId: string;
  category: string;
}) {
  const items: { label: string; href: string; note?: string }[] = [
    {
      label: "下載 CSV（月度分位數）",
      href: monthlyCsvUrl(runId, category),
      note: "lower_95 / median / upper_95 + actual",
    },
    {
      label: "下載 CSV（滾動年變動率）",
      href: rollingYoyCsvUrl(runId, category),
      note: "依使用資料截至時點各月份的 YoY 分位數",
    },
    {
      label: "下載 CSV（年度 YoY 摘要）",
      href: yoyCsvUrl(runId, category),
      note: "單一最新 end_date 的年 YoY",
    },
    {
      label: "下載 Parquet（10,000 模擬路徑）",
      href: pathsParquetUrl(runId, category),
      note: "DatetimeIndex × 10000 cols",
    },
    {
      label: "下載 raw_cpi.csv（本次訓練資料）",
      href: rawCpiCsvUrl(runId),
      note: "用此檔配 notebook 重現預測",
    },
  ];
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <h3 className="font-semibold text-slate-800 mb-3 text-sm">交叉檢查下載</h3>
      <ul className="flex flex-col gap-2">
        {items.map((it) => (
          <li key={it.href}>
            <a
              href={it.href}
              className="flex flex-col rounded-md border border-slate-200 px-3 py-2 hover:bg-slate-50"
              download
            >
              <span className="text-sm font-medium text-indigo-700">
                {it.label}
              </span>
              {it.note && (
                <span className="text-xs text-slate-500">{it.note}</span>
              )}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
