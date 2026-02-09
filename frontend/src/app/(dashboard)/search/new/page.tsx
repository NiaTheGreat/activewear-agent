"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { PageTransition } from "@/components/layout/PageTransition";
import { CriteriaForm } from "@/components/search/CriteriaForm";
import { useStartSearch } from "@/hooks/useSearch";
import { useOrganizationStore } from "@/store/organizationStore";
import { api } from "@/lib/api";
import type { SearchCriteria } from "@/types/api";

export default function NewSearchPage() {
  const router = useRouter();
  const startSearch = useStartSearch();
  const { getCurrentOrgId, isPersonalWorkspace } = useOrganizationStore();

  const handleSubmit = async (
    criteria: SearchCriteria,
    mode: string,
    maxManufacturers: number,
    presetName?: string
  ) => {
    try {
      if (presetName) {
        await api.presets.create({
          name: presetName,
          criteria: criteria as Record<string, unknown>,
        });
        toast.success(`Preset "${presetName}" saved!`);
      }

      const result = (await startSearch.mutateAsync({
        criteria: criteria as Record<string, unknown>,
        search_mode: mode,
        max_manufacturers: maxManufacturers,
        organization_id: getCurrentOrgId(), // Include organization context
      })) as { id: string };

      const searchType = isPersonalWorkspace() ? "Personal search" : "Team search";
      toast.success(`${searchType} started!`);
      router.push(`/search/${result.id}`);
    } catch (err) {
      toast.error(
        err instanceof Error ? err.message : "Failed to start search"
      );
    }
  };

  return (
    <PageTransition>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
            New Search
          </h1>
          <p className="text-gray-500 mt-1">
            Define your criteria to discover activewear manufacturers
          </p>
        </div>
        <CriteriaForm
          onSubmit={handleSubmit}
          isLoading={startSearch.isPending}
        />
      </div>
    </PageTransition>
  );
}
