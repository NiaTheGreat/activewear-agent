"use client";

import { useState } from "react";
import { useOrganizations } from "@/hooks/useOrganizations";
import { usePipelines } from "@/hooks/usePipelines";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Building2, Loader2 } from "lucide-react";

interface CopyToOrganizationDialogProps {
  trigger: React.ReactNode;
  manufacturerName: string;
  onCopy: (organizationId: string, pipelineIds?: string[]) => Promise<void>;
  isPending?: boolean;
}

export function CopyToOrganizationDialog({
  trigger,
  manufacturerName,
  onCopy,
  isPending = false,
}: CopyToOrganizationDialogProps) {
  const [open, setOpen] = useState(false);
  const [selectedOrgId, setSelectedOrgId] = useState<string>("");
  const [selectedPipelineIds, setSelectedPipelineIds] = useState<string[]>([]);

  const { data: organizations, isLoading: orgsLoading } = useOrganizations();
  const { data: pipelines, isLoading: pipelinesLoading } = usePipelines(
    selectedOrgId || undefined
  );

  const handleCopy = async () => {
    if (!selectedOrgId) return;

    try {
      await onCopy(
        selectedOrgId,
        selectedPipelineIds.length > 0 ? selectedPipelineIds : undefined
      );
      setOpen(false);
      setSelectedOrgId("");
      setSelectedPipelineIds([]);
    } catch (error) {
      // Error handling is done by the parent component
      console.error("Copy failed:", error);
    }
  };

  const togglePipeline = (pipelineId: string) => {
    setSelectedPipelineIds((prev) =>
      prev.includes(pipelineId)
        ? prev.filter((id) => id !== pipelineId)
        : [...prev, pipelineId]
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Copy to Organization</DialogTitle>
          <DialogDescription>
            Copy "{manufacturerName}" to a team workspace
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Organization Selection */}
          <div className="space-y-2">
            <Label htmlFor="organization">Organization</Label>
            {orgsLoading ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : !organizations || organizations.length === 0 ? (
              <div className="rounded-lg border border-dashed p-4 text-center">
                <Building2 className="mx-auto h-8 w-8 text-muted-foreground" />
                <p className="mt-2 text-sm text-muted-foreground">
                  You're not a member of any organizations yet
                </p>
              </div>
            ) : (
              <Select value={selectedOrgId} onValueChange={setSelectedOrgId}>
                <SelectTrigger id="organization">
                  <SelectValue placeholder="Select an organization" />
                </SelectTrigger>
                <SelectContent>
                  {organizations.map((org) => (
                    <SelectItem key={org.id} value={org.id}>
                      {org.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {/* Pipeline Selection (optional) */}
          {selectedOrgId && (
            <div className="space-y-2">
              <Label>Add to Pipelines (optional)</Label>
              {pipelinesLoading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : !pipelines || pipelines.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No pipelines in this organization yet
                </p>
              ) : (
                <div className="space-y-2 rounded-lg border p-3">
                  {pipelines.map((pipeline) => (
                    <div key={pipeline.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={`pipeline-${pipeline.id}`}
                        checked={selectedPipelineIds.includes(pipeline.id)}
                        onCheckedChange={() => togglePipeline(pipeline.id)}
                      />
                      <label
                        htmlFor={`pipeline-${pipeline.id}`}
                        className="flex-1 cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                      >
                        <span className="mr-2">{pipeline.icon || "📁"}</span>
                        {pipeline.name}
                      </label>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={isPending}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleCopy}
            disabled={!selectedOrgId || isPending}
          >
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Copy to Organization
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
