"use client";

import { useState } from "react";
import { useOrganizationStore } from "@/store/organizationStore";
import { usePipelines, useDeletePipeline } from "@/hooks/usePipelines";
import { PipelineCard } from "@/components/pipeline/PipelineCard";
import { CreatePipelineDialog } from "@/components/pipeline/CreatePipelineDialog";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/common/EmptyState";
import { LoadingSkeleton } from "@/components/common/LoadingSkeleton";
import { toast } from "sonner";
import { FolderKanban } from "lucide-react";

export default function OrganizationPipelinesPage() {
  const { currentOrganization, isPersonalWorkspace } = useOrganizationStore();
  const { data: pipelines, isLoading } = usePipelines(currentOrganization?.id);
  const deletePipeline = useDeletePipeline(currentOrganization?.id || "");

  if (isPersonalWorkspace() || !currentOrganization) {
    return (
      <div className="container mx-auto max-w-6xl px-4 py-8">
        <EmptyState
          icon={FolderKanban}
          title="No organization selected"
          description="Please select an organization to view pipelines"
        />
      </div>
    );
  }

  const handleDelete = async (pipelineId: string) => {
    if (!confirm("Delete this pipeline? Manufacturers won't be deleted, just removed from this pipeline.")) {
      return;
    }

    try {
      await deletePipeline.mutateAsync(pipelineId);
      toast.success("Pipeline deleted");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to delete pipeline");
    }
  };

  return (
    <div className="container mx-auto max-w-6xl px-4 py-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pipelines</h1>
          <p className="mt-1 text-muted-foreground">
            Organize manufacturers into different collections
          </p>
        </div>
        <CreatePipelineDialog organizationId={currentOrganization.id} />
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <LoadingSkeleton key={i} className="h-32" />
          ))}
        </div>
      ) : !pipelines || pipelines.length === 0 ? (
        <EmptyState
          icon={FolderKanban}
          title="No pipelines yet"
          description="Create your first pipeline to start organizing manufacturers"
          action={
            <CreatePipelineDialog
              organizationId={currentOrganization.id}
              trigger={<Button>Create Pipeline</Button>}
            />
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {pipelines.map((pipeline) => (
            <PipelineCard
              key={pipeline.id}
              pipeline={pipeline}
              onDelete={() => handleDelete(pipeline.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
