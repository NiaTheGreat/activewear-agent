"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { SearchResponse, SearchStatus } from "@/types/api";

export function useSearchHistory() {
  return useQuery<SearchResponse[]>({
    queryKey: ["search-history"],
    queryFn: () => api.search.history() as Promise<SearchResponse[]>,
  });
}

export function useSearchStatus(searchId: string | undefined, enabled = true) {
  return useQuery<SearchStatus>({
    queryKey: ["search-status", searchId],
    queryFn: () => api.search.status(searchId!) as Promise<SearchStatus>,
    enabled: !!searchId && enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "running" || status === "pending") return 2000;
      return false;
    },
  });
}

export function useSearchDetail(searchId: string | undefined) {
  return useQuery<SearchResponse>({
    queryKey: ["search", searchId],
    queryFn: () => api.search.get(searchId!) as Promise<SearchResponse>,
    enabled: !!searchId,
  });
}

export function useStartSearch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      criteria: Record<string, unknown>;
      criteria_preset_id?: string;
      search_mode?: string;
      max_manufacturers?: number;
      organization_id?: string;
    }) => api.search.run(data) as Promise<SearchResponse>,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["search-history"] });
    },
  });
}

export function useDeleteSearch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.search.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["search-history"] });
    },
  });
}
