"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  ContactActivity,
  ContactActivityCreate,
  ContactActivityUpdate,
} from "@/types/api";

export function useActivities(manufacturerId: string | undefined) {
  return useQuery<ContactActivity[]>({
    queryKey: ["activities", manufacturerId],
    queryFn: () =>
      api.activities.list(manufacturerId!) as Promise<ContactActivity[]>,
    enabled: !!manufacturerId,
  });
}

export function useCreateActivity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      manufacturerId,
      data,
    }: {
      manufacturerId: string;
      data: ContactActivityCreate;
    }) =>
      api.activities.create(manufacturerId, data) as Promise<ContactActivity>,
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["activities", data.manufacturer_id],
      });
    },
  });
}

export function useUpdateActivity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      activityId,
      data,
    }: {
      activityId: string;
      data: ContactActivityUpdate;
    }) =>
      api.activities.update(activityId, data) as Promise<ContactActivity>,
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["activities", data.manufacturer_id],
      });
    },
  });
}

export function useDeleteActivity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      activityId,
      manufacturerId,
    }: {
      activityId: string;
      manufacturerId: string;
    }) => api.activities.delete(activityId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ["activities", variables.manufacturerId],
      });
    },
  });
}
