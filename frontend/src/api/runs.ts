import type { RunManifest, RunSummary } from "@/types/api";
import { api } from "./client";

export const listRuns = () => api<RunSummary[]>("/api/runs");
export const getLatestRun = () => api<{ run_id: string }>("/api/runs/latest");
export const getRun = (runId: string) =>
  api<RunManifest>(`/api/runs/${runId}`);
