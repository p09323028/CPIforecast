import type { CategoryPair } from "@/types/api";
import { api } from "./client";

export const listCategories = () => api<CategoryPair[]>("/api/categories");
