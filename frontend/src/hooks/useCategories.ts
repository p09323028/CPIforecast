import { useQuery } from "@tanstack/react-query";
import { listCategories } from "@/api/categories";

export const useCategories = () =>
  useQuery({
    queryKey: ["categories"],
    queryFn: listCategories,
    staleTime: Infinity,
  });
