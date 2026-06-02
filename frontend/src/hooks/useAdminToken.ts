import { useCallback, useEffect, useState } from "react";

const KEY = "cpi_admin_token";

export function useAdminToken() {
  const [token, setToken] = useState<string>(() => {
    if (typeof window === "undefined") return "";
    return window.localStorage.getItem(KEY) ?? "";
  });

  useEffect(() => {
    if (token) window.localStorage.setItem(KEY, token);
    else window.localStorage.removeItem(KEY);
  }, [token]);

  const clear = useCallback(() => setToken(""), []);
  return { token, setToken, clear };
}
