"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Manufacturer, ManufacturerCreate, ManufacturerUpdate } from "@/types/api";

export function useAllManufacturers(
  params?: {
    sort_by?: string;
    sort_dir?: string;
    favorites_only?: boolean;
    min_score?: number;
  }
) {
  return useQuery<Manufacturer[]>({
    queryKey: ["manufacturers", "all", params],
    queryFn: () =>
      api.manufacturers.listAll(params) as Promise<Manufacturer[]>,
  });
}

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

export function useCreateManualManufacturer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ManufacturerCreate) =>
      api.manufacturers.createManual(data) as Promise<Manufacturer>,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["manufacturers"] });
    },
  });
}

export function useDeleteManufacturer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.manufacturers.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["manufacturers"] });
    },
  });
}

export function useCopyManufacturerToOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      manufacturerId,
      organizationId,
      pipelineIds,
    }: {
      manufacturerId: string;
      organizationId: string;
      pipelineIds?: string[];
    }) =>
      api.manufacturers.copyToOrganization(manufacturerId, {
        organization_id: organizationId,
        pipeline_ids: pipelineIds,
      }) as Promise<Manufacturer>,
    onSuccess: (data, variables) => {
      // Invalidate manufacturers list for the target organization
      queryClient.invalidateQueries({
        queryKey: ["manufacturers", "all", { organization_id: variables.organizationId }],
      });
      // Invalidate pipelines to update manufacturer counts
      queryClient.invalidateQueries({
        queryKey: ["organizations", variables.organizationId, "pipelines"],
      });
      // If added to specific pipelines, invalidate those too
      if (variables.pipelineIds) {
        variables.pipelineIds.forEach((pipelineId) => {
          queryClient.invalidateQueries({
            queryKey: ["pipelines", pipelineId, "manufacturers"],
          });
        });
      }
    },
  });
}
