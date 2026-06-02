import dayjs from "dayjs";
import "dayjs/locale/zh-tw";
dayjs.locale("zh-tw");

export const fmtNum = (v: number | null | undefined, digits = 2): string => {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return v.toLocaleString("zh-TW", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};

export const fmtPct = (v: number | null | undefined, digits = 2): string => {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  const sign = v > 0 ? "+" : "";
  return `${sign}${v.toFixed(digits)}%`;
};

export const fmtDate = (iso: string | null | undefined): string => {
  if (!iso) return "—";
  return dayjs(iso).format("YYYY-MM-DD");
};

export const fmtMonth = (iso: string): string => dayjs(iso).format("YYYY-MM");

export const fmtDateTime = (iso: string | null | undefined): string => {
  if (!iso) return "—";
  return dayjs(iso).format("YYYY-MM-DD HH:mm");
};
