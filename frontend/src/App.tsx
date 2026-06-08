import { Route, Routes } from "react-router-dom";
import TopBar from "@/components/layout/TopBar";
import DashboardPage from "@/pages/DashboardPage";
import CategoryPage from "@/pages/CategoryPage";
import PriceCategoryPage from "@/pages/PriceCategoryPage";
import RunsPage from "@/pages/RunsPage";
import AdminPage from "@/pages/AdminPage";
import MethodPage from "@/pages/MethodPage";
import NotFoundPage from "@/pages/NotFoundPage";

export default function App() {
  return (
    <div className="min-h-full flex flex-col">
      <TopBar />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/method" element={<MethodPage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/price/:slug" element={<PriceCategoryPage />} />
          <Route path="/runs" element={<RunsPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <footer className="text-center text-xs text-slate-500 py-6">
        資料來源：行政院主計總處 dataset 6019 ・ 模型 USDA TB-1957 SARIMA + Monte Carlo
      </footer>
    </div>
  );
}
