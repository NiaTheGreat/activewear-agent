"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Manufacturer, ManufacturerUpdate } from "@/types/api";

export function useManufacturers(
  searchId: string | undefined,
  params?: {
    sort_by?: string;
    sort_dir?: string;
    favorites_only?: boolean;
    min_score?: number;
  }
) {
  return useQuery<Manufacturer[]>({
    queryKey: ["manufacturers", searchId, params],
    queryFn: () =>
      api.manufacturers.list(searchId!, params) as Promise<Manufacturer[]>,
    enabled: !!searchId,
  });
}

export function useManufacturer(id: string | undefined) {
  return useQuery<Manufacturer>({
    queryKey: ["manufacturer", id],
    queryFn: () => api.manufacturers.get(id!) as Promise<Manufacturer>,
    enabled: !!id,
  });
}

export function useUpdateManufacturer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ManufacturerUpdate }) =>
      api.manufacturers.update(id, data) as Promise<Manufacturer>,
    onSuccess: (data) => {
      queryClient.setQueryData(["manufacturer", data.id], data);
      queryClient.invalidateQueries({ queryKey: ["manufacturers"] });
    },
  });
}
