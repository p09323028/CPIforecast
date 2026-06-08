import { useQuery } from "@tanstack/react-query";
import {
  getPriceForecast,
  getPriceLatestRun,
  getPriceRun,
  listPriceCategories,
} from "@/api/prices";

export const usePriceLatestRun = () =>
  useQuery({
    queryKey: ["price-latest"],
    queryFn: getPriceLatestRun,
    retry: false, // 沒有任何價格 run 時直接 404，不用重試
  });

export const usePriceCategories = () =>
  useQuery({
    queryKey: ["price-categories"],
    queryFn: listPriceCategories,
    retry: false,
    staleTime: Infinity,
  });

export const usePriceForecast = (runId: string | undefined, item: string) =>
  useQuery({
    queryKey: ["price-forecast", runId, item],
    queryFn: () => getPriceForecast(runId!, item),
    enabled: !!runId && !!item,
  });

export const usePriceRun = (runId: string | undefined) =>
  useQuery({
    queryKey: ["price-run", runId],
    queryFn: () => getPriceRun(runId!),
    enabled: !!runId,
  });
