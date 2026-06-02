import { useQuery } from "@tanstack/react-query";
import { getLatestRun, getRun, listRuns } from "@/api/runs";

export const useRuns = () =>
  useQuery({ queryKey: ["runs"], queryFn: listRuns });

export const useLatestRun = () =>
  useQuery({
    queryKey: ["latest-run"],
    queryFn: getLatestRun,
    retry: (failureCount, error) => {
      const status = (error as { status?: number } | null)?.status;
      if (status === 404) return false;
      return failureCount < 2;
    },
  });

export const useRun = (runId?: string) =>
  useQuery({
    queryKey: ["run", runId],
    queryFn: () => getRun(runId!),
    enabled: !!runId,
  });
