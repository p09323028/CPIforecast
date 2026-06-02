import { useMemo } from "react";
import Plot from "react-plotly.js";
import type { Data, Layout, Config } from "plotly.js-dist-min";
import type { ForecastPayload } from "@/types/api";

type Mode = "level" | "yoy";

const FONT =
  '"Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif';

export default function ForecastChart({
  data,
  mode,
  height = 480,
}: {
  data: ForecastPayload;
  mode: Mode;
  height?: number;
}) {
  const { traces, layout } = useMemo(() => {
    if (mode === "level") return buildLevelTraces(data);
    return buildYoyTraces(data);
  }, [data, mode]);

  const config: Partial<Config> = {
    locale: "zh-TW",
    displaylogo: false,
    responsive: true,
    modeBarButtonsToRemove: ["lasso2d", "select2d"],
  };

  return (
    <div className="plotly-container w-full" style={{ minHeight: height }}>
      <Plot
        data={traces}
        layout={{ ...layout, height, autosize: true }}
        config={config}
        useResizeHandler
        style={{ width: "100%" }}
      />
    </div>
  );
}

function buildLevelTraces(data: ForecastPayload): {
  traces: Data[];
  layout: Partial<Layout>;
} {
  // 歷史與預測各自獨立的 X 範圍；hoverdistance:1 + 同色 connector 讓
  // hover 邊界不會 snap 到鄰近 trace。
  const histX = data.history.map((h) => h.date);
  const histY = data.history.map((h) => h.value);

  const fc = data.monthly.filter((m) => m.median !== null);
  const fX = fc.map((m) => m.date);
  const fLower = fc.map((m) => m.lower_95 as number);
  const fMedian = fc.map((m) => m.median as number);
  const fUpper = fc.map((m) => m.upper_95 as number);
  const forecastInterval = fc.map((m) => [
    m.lower_95 as number,
    m.upper_95 as number,
  ]);

  const traces: Data[] = [
    {
      name: "實際 CPI",
      x: histX,
      y: histY,
      mode: "lines",
      line: { color: "#0f172a", width: 2 },
      hovertemplate: "%{x|%Y-%m}<br>實際 CPI %{y:.2f}<extra></extra>",
      type: "scatter",
    },
    {
      name: "95% 上限值",
      x: fX,
      y: fUpper,
      mode: "lines",
      line: { width: 0, color: "rgba(99,102,241,0.0)" },
      showlegend: false,
      hoverinfo: "skip",
      type: "scatter",
    },
    {
      name: "95% 預測區間",
      x: fX,
      y: fLower,
      mode: "lines",
      line: { width: 0, color: "rgba(99,102,241,0.0)" },
      fill: "tonexty",
      fillcolor: "rgba(99,102,241,0.20)",
      hoverinfo: "skip",
      type: "scatter",
    },
    {
      name: "預測",
      x: fX,
      y: fMedian,
      customdata: forecastInterval as any,
      mode: "lines",
      line: { color: "#4f46e5", width: 2 },
      hovertemplate:
        "%{x|%Y-%m}<br>中位數 %{y:.2f}<br>95% 預測區間 [%{customdata[0]:.2f}, %{customdata[1]:.2f}]<extra></extra>",
      type: "scatter",
    },
  ];

  const layout: Partial<Layout> = {
    font: { family: FONT },
    xaxis: { type: "date", title: { text: "月份" } },
    yaxis: { title: { text: "CPI 指數（基期 110 年=100）" } },
    // 改用 closest — 每個 trace 獨立顯示，徹底避免邊界 snap 跨範圍
    hovermode: "closest",
    margin: { l: 64, r: 24, t: 24, b: 56 },
    legend: { orientation: "h", y: -0.18 },
    paper_bgcolor: "white",
    plot_bgcolor: "white",
  };
  return { traces, layout };
}

function buildYoyTraces(data: ForecastPayload): {
  traces: Data[];
  layout: Partial<Layout>;
} {
  const rolling = data.rolling_yoy;
  const forecastYear = rolling.forecast_year ?? "—";
  // 保留所有 X 軸位置；effective_end 與 end_date 不同的（cached）點留 null
  const hasNewData = (p: (typeof rolling.points)[number]) =>
    p.median !== null &&
    p.lower_95 !== null &&
    p.upper_95 !== null &&
    (!p.effective_end || p.effective_end === p.end_date);
  const x = rolling.points.map((p) => p.end_date.slice(0, 7)); // YYYY-MM
  const lower = rolling.points.map((p) =>
    hasNewData(p) ? (p.lower_95 as number) : null,
  );
  const median = rolling.points.map((p) =>
    hasNewData(p) ? (p.median as number) : null,
  );
  const upper = rolling.points.map((p) =>
    hasNewData(p) ? (p.upper_95 as number) : null,
  );

  const yoyInterval: Array<[number | null, number | null]> = rolling.points.map(
    (p) =>
      hasNewData(p)
        ? [p.lower_95 as number, p.upper_95 as number]
        : [null, null],
  );

  const traces: Data[] = [
    {
      name: "95% 上限值",
      x,
      y: upper,
      mode: "lines+markers",
      line: { width: 0, color: "rgba(99,102,241,0.0)" },
      marker: { size: 0 },
      showlegend: false,
      hoverinfo: "skip",
      type: "scatter",
    },
    {
      name: "95% 預測區間",
      x,
      y: lower,
      mode: "lines+markers",
      line: { width: 0, color: "rgba(99,102,241,0.0)" },
      marker: { size: 0 },
      fill: "tonexty",
      fillcolor: "rgba(99,102,241,0.25)",
      showlegend: true,
      hoverinfo: "skip",
      type: "scatter",
    },
    {
      name: "預測",
      x,
      y: median,
      customdata: yoyInterval as any,
      mode: "lines+markers",
      line: { color: "#4f46e5", width: 2, dash: "dash" },
      marker: { size: 7 },
      hovertemplate:
        "資料截至 %{x}<br>中位數 %{y:.2f}%<br>95% 預測區間 [%{customdata[0]:.2f}%, %{customdata[1]:.2f}%]<extra></extra>",
      type: "scatter",
    },
  ];

  if (rolling.actual_yoy !== null && rolling.actual_yoy !== undefined && x.length) {
    traces.push({
      name: "實際年變動率",
      x,
      y: x.map(() => rolling.actual_yoy as number),
      mode: "lines",
      line: { color: "#0f172a", width: 1.5 },
      hovertemplate: "%{y:.2f}%<extra></extra>",
      type: "scatter",
    });
  }

  const layout: Partial<Layout> = {
    title: {
      text: `${forecastYear} 年年變動率（依「使用資料截至時點」滾動預測）`,
      font: { family: FONT, size: 14 },
      x: 0,
      xanchor: "left",
    },
    font: { family: FONT },
    xaxis: { title: { text: "使用資料截至時點" }, type: "category" },
    yaxis: {
      title: { text: "年變動率 (%)" },
      ticksuffix: "%",
      zeroline: false,
    },
    hovermode: "x unified",
    margin: { l: 64, r: 24, t: 48, b: 56 },
    legend: { orientation: "h", y: -0.18 },
    paper_bgcolor: "white",
    plot_bgcolor: "white",
  };
  return { traces, layout };
}
