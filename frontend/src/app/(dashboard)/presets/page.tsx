"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { CriteriaPreset, SearchCriteria } from "@/types/api";
import { PageTransition } from "@/components/layout/PageTransition";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/common/EmptyState";
import { CardSkeleton } from "@/components/common/LoadingSkeleton";
import {
  Bookmark,
  Plus,
  Trash2,
  Pencil,
  Play,
  Loader2,
} from "lucide-react";

export default function PresetsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [showDialog, setShowDialog] = useState(false);
  const [editingPreset, setEditingPreset] = useState<CriteriaPreset | null>(
    null
  );
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [criteriaJson, setCriteriaJson] = useState("{}");

  const { data: presets, isLoading } = useQuery<CriteriaPreset[]>({
    queryKey: ["presets"],
    queryFn: () => api.presets.list() as Promise<CriteriaPreset[]>,
  });

  const createPreset = useMutation({
    mutationFn: (data: {
      name: string;
      description?: string;
      criteria: Record<string, unknown>;
    }) => api.presets.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["presets"] });
      toast.success("Preset created");
      closeDialog();
    },
    onError: () => toast.error("Failed to create preset"),
  });

  const updatePreset = useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: {
        name?: string;
        description?: string;
        criteria?: Record<string, unknown>;
      };
    }) => api.presets.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["presets"] });
      toast.success("Preset updated");
      closeDialog();
    },
    onError: () => toast.error("Failed to update preset"),
  });

  const deletePreset = useMutation({
    mutationFn: (id: string) => api.presets.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["presets"] });
      toast.success("Preset deleted");
    },
    onError: () => toast.error("Failed to delete preset"),
  });

  const openCreate = () => {
    setEditingPreset(null);
    setName("");
    setDescription("");
    setCriteriaJson(
      JSON.stringify(
        {
          locations: [],
          certifications_of_interest: [],
          materials: [],
          production_methods: [],
        },
        null,
        2
      )
    );
    setShowDialog(true);
  };

  const openEdit = (preset: CriteriaPreset) => {
    setEditingPreset(preset);
    setName(preset.name);
    setDescription(preset.description || "");
    setCriteriaJson(JSON.stringify(preset.criteria, null, 2));
    setShowDialog(true);
  };

  const closeDialog = () => {
    setShowDialog(false);
    setEditingPreset(null);
  };

  const handleSubmit = () => {
    let criteria: Record<string, unknown>;
    try {
      criteria = JSON.parse(criteriaJson);
    } catch {
      toast.error("Invalid JSON in criteria");
      return;
    }

    if (editingPreset) {
      updatePreset.mutate({
        id: editingPreset.id,
        data: { name, description: description || undefined, criteria },
      });
    } else {
      createPreset.mutate({
        name,
        description: description || undefined,
        criteria,
      });
    }
  };

  const handleUsePreset = (preset: CriteriaPreset) => {
    // Store in session for the new search page to pick up
    sessionStorage.setItem("preset-criteria", JSON.stringify(preset.criteria));
    router.push("/search/new");
  };

  const formatCriteria = (criteria: SearchCriteria) => {
    const parts: string[] = [];
    if (criteria.locations?.length)
      parts.push(`${criteria.locations.length} locations`);
    if (criteria.materials?.length)
      parts.push(`${criteria.materials.length} materials`);
    if (criteria.certifications_of_interest?.length)
      parts.push(`${criteria.certifications_of_interest.length} certs`);
    if (criteria.budget_tier) {
      const tier = Array.isArray(criteria.budget_tier)
        ? criteria.budget_tier.join(", ")
        : criteria.budget_tier;
      parts.push(tier);
    }
    return parts.join(" | ") || "No criteria defined";
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
              Search Presets
            </h1>
            <p className="text-gray-500 mt-1">
              Save and reuse search criteria for quick access
            </p>
          </div>
          <Button onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            New Preset
          </Button>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : !presets || presets.length === 0 ? (
          <EmptyState
            icon={Bookmark}
            title="No presets yet"
            description="Create presets to save your common search criteria."
            actionLabel="Create Preset"
            onAction={openCreate}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {presets.map((preset) => (
              <Card key={preset.id} className="group">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">
                        {preset.name}
                      </CardTitle>
                      {preset.description && (
                        <CardDescription className="mt-1">
                          {preset.description}
                        </CardDescription>
                      )}
                    </div>
                    {preset.is_public && (
                      <Badge variant="outline">Public</Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-gray-500 mb-4">
                    {formatCriteria(preset.criteria)}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      onClick={() => handleUsePreset(preset)}
                    >
                      <Play className="mr-1 h-3 w-3" />
                      Use
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openEdit(preset)}
                    >
                      <Pencil className="mr-1 h-3 w-3" />
                      Edit
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (confirm("Delete this preset?"))
                          deletePreset.mutate(preset.id);
                      }}
                      className="text-gray-400 hover:text-error-500 ml-auto"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Create/Edit Dialog */}
        <Dialog open={showDialog} onOpenChange={(o) => !o && closeDialog()}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingPreset ? "Edit Preset" : "New Preset"}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <Label htmlFor="presetName">Name</Label>
                <Input
                  id="presetName"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Vietnam Recycled Polyester"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="presetDesc">Description</Label>
                <Input
                  id="presetDesc"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Optional description"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="presetCriteria">Criteria (JSON)</Label>
                <Textarea
                  id="presetCriteria"
                  value={criteriaJson}
                  onChange={(e) => setCriteriaJson(e.target.value)}
                  rows={10}
                  className="font-mono text-xs"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={closeDialog}>
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={
                  !name.trim() ||
                  createPreset.isPending ||
                  updatePreset.isPending
                }
              >
                {(createPreset.isPending || updatePreset.isPending) && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                {editingPreset ? "Update" : "Create"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </PageTransition>
  );
}
