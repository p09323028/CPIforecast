import { useSearchParams } from "react-router-dom";
import { useLatestRun } from "./useRuns";

export function useSelectedRunId(): {
  runId: string | undefined;
  setRunId: (rid: string | null) => void;
  isLatest: boolean;
} {
  const [params, setParams] = useSearchParams();
  const queryRid = params.get("run_id") || undefined;
  const { data: latest } = useLatestRun();
  const latestRid = latest?.run_id;
  const runId = queryRid ?? latestRid;
  const setRunId = (rid: string | null) => {
    const next = new URLSearchParams(params);
    if (!rid || rid === latestRid) next.delete("run_id");
    else next.set("run_id", rid);
    setParams(next, { replace: false });
  };
  return {
    runId,
    setRunId,
    isLatest: !queryRid || queryRid === latestRid,
  };
}
