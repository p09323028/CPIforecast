import { useQuery } from "@tanstack/react-query";
import { getForecast } from "@/api/forecast";

export const useForecast = (runId: string | undefined, category: string) =>
  useQuery({
    queryKey: ["forecast", runId, category],
    queryFn: () => getForecast(runId!, category),
    enabled: !!runId && !!category,
    retry: (failureCount, error) => {
      const status = (error as { status?: number } | null)?.status;
      if (status && [404, 409].includes(status)) return false;
      return failureCount < 1;
    },
  });
