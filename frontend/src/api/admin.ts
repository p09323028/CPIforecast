import type { AdminStatus, TriggerResponse } from "@/types/api";
import { api } from "./client";

export const triggerRun = (token: string) =>
  api<TriggerResponse>("/api/admin/trigger", { method: "POST", token });

export const getAdminStatus = (runId: string, token: string) =>
  api<AdminStatus>(`/api/admin/status/${runId}`, { token });
