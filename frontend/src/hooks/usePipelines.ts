import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  Pipeline,
  PipelineCreate,
  PipelineUpdate,
  PipelineManufacturer,
  AddManufacturerToPipeline,
  UpdatePipelineManufacturer,
} from "@/types/api";

export function usePipelines(orgId: string | undefined) {
  return useQuery<Pipeline[]>({
    queryKey: ["organizations", orgId, "pipelines"],
    queryFn: () => api.pipelines.list(orgId!),
    enabled: !!orgId,
  });
}

export function usePipeline(id: string | undefined) {
  return useQuery<Pipeline>({
    queryKey: ["pipelines", id],
    queryFn: () => api.pipelines.get(id!),
    enabled: !!id,
  });
}

export function useCreatePipeline(orgId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PipelineCreate) => api.pipelines.create(orgId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organizations", orgId, "pipelines"],
      });
    },
  });
}

export function useUpdatePipeline(pipelineId: string, orgId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: PipelineUpdate) =>
      api.pipelines.update(pipelineId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organizations", orgId, "pipelines"],
      });
      queryClient.invalidateQueries({ queryKey: ["pipelines", pipelineId] });
    },
  });
}

export function useDeletePipeline(orgId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (pipelineId: string) => api.pipelines.delete(pipelineId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["organizations", orgId, "pipelines"],
      });
    },
  });
}

// Pipeline-Manufacturer relationships

export function usePipelineManufacturers(pipelineId: string | undefined) {
  return useQuery<PipelineManufacturer[]>({
    queryKey: ["pipelines", pipelineId, "manufacturers"],
    queryFn: () => api.pipelines.listManufacturers(pipelineId!),
    enabled: !!pipelineId,
  });
}

export function useAddManufacturerToPipeline(pipelineId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AddManufacturerToPipeline) =>
      api.pipelines.addManufacturer(pipelineId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["pipelines", pipelineId, "manufacturers"],
      });
      queryClient.invalidateQueries({ queryKey: ["pipelines", pipelineId] });
    },
  });
}

export function useUpdatePipelineManufacturer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      pmId,
      data,
    }: {
      pmId: string;
      data: UpdatePipelineManufacturer;
    }) => api.pipelines.updateManufacturer(pmId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipelines"] });
    },
  });
}

export function useRemoveManufacturerFromPipeline() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (pmId: string) => api.pipelines.removeManufacturer(pmId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["pipelines"] });
    },
  });
}
