import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-10 text-center">
      <h1 className="text-2xl font-semibold text-slate-900">頁面不存在</h1>
      <Link
        to="/"
        className="mt-4 inline-block text-indigo-600 hover:underline"
      >
        回到儀表板
      </Link>
    </div>
  );
}
