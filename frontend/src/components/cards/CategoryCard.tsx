import { Link, useSearchParams } from "react-router-dom";
import { useForecast } from "@/hooks/useForecast";
import { fmtNum, fmtPct } from "@/lib/format";
import { zh, icon } from "@/lib/categories";

export default function CategoryCard({
  runId,
  en,
}: {
  runId: string;
  en: string;
}) {
  const { data, isLoading, isError } = useForecast(runId, en);
  const [params] = useSearchParams();
  const search = params.toString() ? `?${params.toString()}` : "";

  return (
    <Link
      to={`/category/${en}${search}`}
      className="block rounded-lg border border-slate-200 bg-white p-4 hover:border-indigo-300 hover:shadow-sm transition"
    >
      <div className="flex items-center justify-between">
        <span className="font-semibold text-slate-800">{zh(en)}</span>
        <span className="text-2xl leading-none">{icon(en)}</span>
      </div>
      <div className="mt-3 text-xs text-slate-500">
        {isLoading && <span>載入中…</span>}
        {isError && <span className="text-red-600">無法載入</span>}
        {data && <CardBody data={data} />}
      </div>
    </Link>
  );
}

function CardBody({ data }: { data: NonNullable<ReturnType<typeof useForecast>["data"]> }) {
  const lastActual = data.history[data.history.length - 1];
  const nextMonth = data.monthly.find((m) => m.median !== null);
  const rolling = data.rolling_yoy;
  const latestRollingPoint = [...rolling.points]
    .reverse()
    .find((p) => p.median !== null);
  return (
    <div className="grid grid-cols-2 gap-2 text-xs">
      <div>
        <div className="text-slate-400">最新實際</div>
        <div className="text-slate-800 font-medium">
          {fmtNum(lastActual?.value)}
        </div>
      </div>
      <div>
        <div className="text-slate-400">下個月中位數</div>
        <div className="text-slate-800 font-medium">
          {fmtNum(nextMonth?.median)}
        </div>
      </div>
      {latestRollingPoint && rolling.forecast_year && (
        <div className="col-span-2">
          <div className="text-slate-400">
            {rolling.forecast_year}年年變動率預測值
          </div>
          <div className="text-slate-800 font-medium">
            {fmtPct(latestRollingPoint.median)}
          </div>
        </div>
      )}
    </div>
  );
}
