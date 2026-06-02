import { useState } from "react";
import { useAdminToken } from "@/hooks/useAdminToken";

export default function AdminTokenField() {
  const { token, setToken } = useAdminToken();
  const [show, setShow] = useState(false);
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-slate-700">管理者密碼</span>
      <div className="flex gap-2">
        <input
          type={show ? "text" : "password"}
          value={token}
          onChange={(e) => setToken(e.target.value)}
          autoComplete="off"
          className="flex-1 rounded border border-slate-300 px-3 py-2 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
          placeholder="貼上 ADMIN_TOKEN"
        />
        <button
          type="button"
          onClick={() => setShow((v) => !v)}
          className="rounded border border-slate-300 px-3 text-xs text-slate-700 hover:bg-slate-50"
        >
          {show ? "隱藏" : "顯示"}
        </button>
      </div>
      <span className="text-xs text-slate-500">
        密碼僅儲存在你的瀏覽器 localStorage，未送出至第三方。
      </span>
    </label>
  );
}
