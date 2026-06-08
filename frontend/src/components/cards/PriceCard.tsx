import { Link } from "react-router-dom";
import type { PriceCategory } from "@/api/prices";
import { usePriceForecast } from "@/hooks/usePrices";
import { fmtNum, fmtPct, fmtMonth } from "@/lib/format";

export default function PriceCard({
  runId,
  item,
}: {
  runId: string;
  item: PriceCategory;
}) {
  const { data, isLoading, isError } = usePriceForecast(runId, item.en);

  return (
    <Link
      to={`/price/${item.en}`}
      className="block rounded-lg border border-slate-200 bg-white p-4 hover:border-indigo-300 hover:shadow-sm transition"
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold text-slate-800">{item.zh}</span>
        <span className="text-2xl leading-none">{item.icon ?? "💰"}</span>
      </div>
      {item.unit && (
        <div className="mt-0.5 text-xs text-slate-400">單位：{item.unit}</div>
      )}
      <div className="mt-3 text-xs text-slate-500">
        {isLoading && <span>載入中…</span>}
        {isError && <span className="text-red-600">無法載入</span>}
        {data && <PriceBody data={data} unit={item.unit} />}
      </div>
    </Link>
  );
}

function PriceBody({
  data,
  unit,
}: {
  data: NonNullable<ReturnType<typeof usePriceForecast>["data"]>;
  unit?: string | null;
}) {
  const lastActual = data.history[data.history.length - 1];
  const nextMonth = data.monthly.find((m) => m.median !== null);
  const rolling = data.rolling_yoy;
  const latestRollingPoint = [...rolling.points]
    .reverse()
    .find((p) => p.median !== null);
  const u = unit ? ` ${unit}` : "";

  return (
    <div className="grid grid-cols-2 gap-2 text-xs">
      <div>
        <div className="text-slate-400">
          最新實際{lastActual ? `(${fmtMonth(lastActual.date)})` : ""}
        </div>
        <div className="text-slate-800 font-medium">
          {fmtNum(lastActual?.value)}
          {lastActual ? u : ""}
        </div>
      </div>
      <div>
        <div className="text-slate-400">
          下個月{nextMonth ? `(${fmtMonth(nextMonth.date)})` : ""}
          <br />
          預測中位數
        </div>
        <div className="text-slate-800 font-medium">
          {fmtNum(nextMonth?.median)}
          {nextMonth ? u : ""}
        </div>
      </div>
      {latestRollingPoint && rolling.forecast_year && (
        <div className="col-span-2">
          <div className="text-slate-400">
            {rolling.forecast_year}年價格年變動率預測
          </div>
          <div className="text-slate-800 font-medium">
            {fmtPct(latestRollingPoint.median)}
          </div>
        </div>
      )}
    </div>
  );
}
