import { Link, NavLink, useLocation } from "react-router-dom";
import RunSelector from "./RunSelector";

const links = [
  { to: "/", label: "儀表板" },
  { to: "/method", label: "方法說明" },
  { to: "/runs", label: "執行歷程" },
  { to: "/admin", label: "管理" },
];

export default function TopBar() {
  const { search } = useLocation();
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-4">
        <Link to={`/${search}`} className="font-bold text-lg text-slate-900">
          食品類物價(指數)預測平台
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={`${l.to}${l.to === "/" ? search : ""}`}
              end={l.to === "/"}
              className={({ isActive }) =>
                [
                  "px-3 py-1.5 rounded-md",
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100",
                ].join(" ")
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto">
          <RunSelector />
        </div>
      </div>
    </header>
  );
}
