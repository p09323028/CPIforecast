import { API_BASE_URL } from "@/lib/env";

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
    message: string,
  ) {
    super(message);
  }
}

export async function api<T>(
  path: string,
  init?: RequestInit & { token?: string },
): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Accept", "application/json");
  if (init?.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (init?.token) headers.set("Authorization", `Bearer ${init.token}`);
  const res = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      /* ignore */
    }
    const detail =
      (body as { detail?: string | { detail?: string } } | null)?.detail;
    const message =
      typeof detail === "string"
        ? detail
        : typeof detail === "object" && detail !== null && "detail" in detail
          ? (detail.detail ?? res.statusText)
          : res.statusText;
    throw new ApiError(res.status, body, message);
  }
  return (await res.json()) as T;
}

export const downloadUrl = (path: string): string => `${API_BASE_URL}${path}`;
