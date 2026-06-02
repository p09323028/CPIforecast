import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";
import { getAdminStatus, triggerRun } from "@/api/admin";
import { useAdminToken } from "./useAdminToken";

export function useTriggerRun() {
  const { token } = useAdminToken();
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  const trigger = useMutation({
    mutationFn: () => triggerRun(token),
    onSuccess: ({ run_id }) => {
      setActiveRunId(run_id);
      toast.success("已啟動預測，將顯示進度");
    },
    onError: (err) => {
      const status = (err as { status?: number } | null)?.status;
      const message = (err as Error).message;
      if (status === 401) toast.error("管理者密碼錯誤");
      else if (status === 409) toast.error("已有執行中的任務");
      else toast.error(`觸發失敗：${message}`);
    },
  });

  const status = useQuery({
    queryKey: ["admin-status", activeRunId],
    queryFn: () => getAdminStatus(activeRunId!, token),
    enabled: !!activeRunId && !!token,
    refetchInterval: (q) =>
      q.state.data?.state === "running" ? 2000 : false,
  });

  useEffect(() => {
    const state = status.data?.state;
    if (!state || !activeRunId) return;
    if (state === "done") {
      toast.success("預測完成");
      qc.invalidateQueries({ queryKey: ["runs"] });
      qc.invalidateQueries({ queryKey: ["latest-run"] });
      qc.invalidateQueries({ queryKey: ["forecast"] });
      navigate(`/?run_id=${activeRunId}`);
    } else if (state === "failed") {
      toast.error(status.data?.error ?? "預測失敗");
    }
  }, [status.data?.state, status.data?.error, activeRunId, navigate, qc]);

  return { trigger, status: status.data, activeRunId };
}
