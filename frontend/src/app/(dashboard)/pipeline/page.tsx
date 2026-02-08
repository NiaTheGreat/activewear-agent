"use client";

import { useState } from "react";
import { PageTransition } from "@/components/layout/PageTransition";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ManufacturerCard } from "@/components/results/ManufacturerCard";
import { AddManufacturerDialog } from "@/components/results/AddManufacturerDialog";
import { useAllManufacturers, useUpdateManufacturer } from "@/hooks/useManufacturers";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { MANUFACTURER_STATUSES } from "@/lib/constants";
import { formatDateTime } from "@/lib/utils";
import { toast } from "sonner";
import type { Manufacturer } from "@/types/api";
import { Kanban, MapPin, CalendarClock, Plus } from "lucide-react";

const STATUS_COLORS: Record<string, string> = {
  new: "bg-gray-100 text-gray-800 border-gray-300",
  contacted: "bg-blue-50 text-blue-800 border-blue-300",
  quoted: "bg-amber-50 text-amber-800 border-amber-300",
  negotiating: "bg-purple-50 text-purple-800 border-purple-300",
  won: "bg-green-50 text-green-800 border-green-300",
  lost: "bg-red-50 text-red-800 border-red-300",
};

const SECTION_COLORS: Record<string, string> = {
  new: "border-l-gray-400",
  contacted: "border-l-blue-400",
  quoted: "border-l-amber-400",
  negotiating: "border-l-purple-400",
  won: "border-l-green-400",
  lost: "border-l-red-400",
};

export default function PipelinePage() {
  const [selectedMfg, setSelectedMfg] = useState<Manufacturer | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);

  const { data: manufacturers, isLoading } = useAllManufacturers({
    sort_by: "match_score",
    sort_dir: "desc",
  });

  const updateMfg = useUpdateManufacturer();

  const handleStatusChange = async (mfg: Manufacturer, newStatus: string) => {
    try {
      await updateMfg.mutateAsync({
        id: mfg.id,
        data: { status: newStatus },
      });
    } catch {
      toast.error("Failed to update status");
    }
  };

  // Only manufacturers explicitly added to pipeline (status != null)
  const pipelineManufacturers = (manufacturers || []).filter((m) => m.status != null);

  // Group by status
  const grouped = MANUFACTURER_STATUSES.reduce(
    (acc, { value }) => {
      acc[value] = pipelineManufacturers.filter((m) => m.status === value);
      return acc;
    },
    {} as Record<string, Manufacturer[]>
  );

  const scoreBadgeVariant = (score: number) => {
    if (score >= 70) return "success" as const;
    if (score >= 40) return "warning" as const;
    return "destructive" as const;
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Pipeline</h1>
            <p className="text-sm text-gray-500 mt-1">
              Track manufacturers through your sourcing pipeline
            </p>
          </div>
          <Button onClick={() => setShowAddDialog(true)}>
            <Plus className="mr-1 h-4 w-4" />
            Add Manufacturer
          </Button>
        </div>

        <AddManufacturerDialog
          open={showAddDialog}
          onClose={() => setShowAddDialog(false)}
        />

        {isLoading ? (
          <TableSkeleton rows={6} />
        ) : pipelineManufacturers.length === 0 ? (
          <EmptyState
            icon={Kanban}
            title="No manufacturers in pipeline"
            description="Add manufacturers to the pipeline from their detail card to start tracking them."
          />
        ) : (
          <div className="space-y-6">
            {MANUFACTURER_STATUSES.map(({ value, label }) => {
              const items = grouped[value];
              return (
                <div key={value}>
                  <div className="flex items-center gap-2 mb-3">
                    <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                      {label}
                    </h2>
                    <span className="text-xs text-gray-400 bg-gray-100 rounded-full px-2 py-0.5">
                      {items.length}
                    </span>
                  </div>

                  {items.length === 0 ? (
                    <p className="text-sm text-gray-400 italic pl-4 pb-2">
                      No manufacturers in this stage.
                    </p>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                      {items.map((mfg) => (
                        <div
                          key={mfg.id}
                          className={`rounded-lg border border-gray-200 bg-white p-4 border-l-4 ${SECTION_COLORS[value] || "border-l-gray-400"} cursor-pointer hover:shadow-sm transition-shadow`}
                          onClick={() => setSelectedMfg(mfg)}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="min-w-0">
                              <p className="font-medium text-gray-900 truncate">
                                {mfg.name}
                              </p>
                              {mfg.location && (
                                <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                                  <MapPin className="h-3 w-3" />
                                  {mfg.location}
                                </p>
                              )}
                            </div>
                            <Badge variant={scoreBadgeVariant(mfg.match_score)}>
                              {mfg.match_score.toFixed(1)}
                            </Badge>
                          </div>

                          <div className="mt-3 flex items-center justify-between gap-2">
                            <select
                              value={mfg.status || "new"}
                              onChange={(e) => {
                                e.stopPropagation();
                                handleStatusChange(mfg, e.target.value);
                              }}
                              onClick={(e) => e.stopPropagation()}
                              className={`text-xs font-medium rounded-md border px-2 py-1 ${STATUS_COLORS[mfg.status || "new"]} focus:outline-none focus:ring-1 focus:ring-ring`}
                            >
                              {MANUFACTURER_STATUSES.map((s) => (
                                <option key={s.value} value={s.value}>
                                  {s.label}
                                </option>
                              ))}
                            </select>

                            {mfg.next_followup_date && (
                              <span className="text-xs text-amber-600 flex items-center gap-1">
                                <CalendarClock className="h-3 w-3" />
                                {formatDateTime(mfg.next_followup_date)}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {selectedMfg && (
          <ManufacturerCard
            manufacturer={selectedMfg}
            open={!!selectedMfg}
            onClose={() => setSelectedMfg(null)}
          />
        )}
      </div>
    </PageTransition>
  );
}
