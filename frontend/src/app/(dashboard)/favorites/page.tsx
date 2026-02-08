"use client";

import { useState } from "react";
import { PageTransition } from "@/components/layout/PageTransition";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { ManufacturerCard } from "@/components/results/ManufacturerCard";
import { FavoriteButton } from "@/components/results/FavoriteButton";
import { useAllManufacturers, useUpdateManufacturer } from "@/hooks/useManufacturers";
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { api } from "@/lib/api";
import { toast } from "sonner";
import type { Manufacturer } from "@/types/api";
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Heart,
  Filter,
  Download,
} from "lucide-react";

export default function FavoritesPage() {
  const [sortBy, setSortBy] = useState("match_score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [minScore, setMinScore] = useState(0);
  const [selectedMfg, setSelectedMfg] = useState<Manufacturer | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const { data: manufacturers, isLoading } = useAllManufacturers({
    sort_by: sortBy,
    sort_dir: sortDir,
    favorites_only: true,
    min_score: minScore > 0 ? minScore : undefined,
  });

  const updateMfg = useUpdateManufacturer();

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortDir("desc");
    }
  };

  const SortIcon = ({ column }: { column: string }) => {
    if (sortBy !== column) return <ArrowUpDown className="h-3 w-3" />;
    return sortDir === "desc" ? (
      <ArrowDown className="h-3 w-3" />
    ) : (
      <ArrowUp className="h-3 w-3" />
    );
  };

  const scoreBadgeVariant = (score: number) => {
    if (score >= 70) return "success" as const;
    if (score >= 40) return "warning" as const;
    return "destructive" as const;
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Favorites</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manufacturers you've saved as favorites
          </p>
        </div>

        {isLoading ? (
          <TableSkeleton rows={8} />
        ) : !manufacturers || manufacturers.length === 0 ? (
          <EmptyState
            icon={Heart}
            title="No favorites yet"
            description="Star manufacturers from your search results to save them here."
          />
        ) : (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500">
                {manufacturers.length} favorite{manufacturers.length !== 1 ? "s" : ""}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    try {
                      await api.manufacturers.exportCsv(true);
                      toast.success("CSV downloaded");
                    } catch {
                      toast.error("Export failed");
                    }
                  }}
                >
                  <Download className="mr-1 h-3 w-3" />
                  Export CSV
                </Button>
                <Button
                  variant={showFilters ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <Filter className="mr-1 h-3 w-3" />
                  Filters
                </Button>
              </div>
            </div>

            {showFilters && (
              <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Minimum Score</span>
                    <span className="font-medium text-gray-900">{minScore}</span>
                  </div>
                  <Slider
                    value={[minScore]}
                    onValueChange={([v]) => setMinScore(v)}
                    max={100}
                    step={5}
                  />
                </div>
              </div>
            )}

            {/* Table */}
            <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="bg-gray-50/50">
                    <TableHead className="w-10" />
                    <TableHead>
                      <button
                        className="flex items-center gap-1 hover:text-gray-900"
                        onClick={() => handleSort("name")}
                      >
                        Name <SortIcon column="name" />
                      </button>
                    </TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>
                      <button
                        className="flex items-center gap-1 hover:text-gray-900"
                        onClick={() => handleSort("match_score")}
                      >
                        Score <SortIcon column="match_score" />
                      </button>
                    </TableHead>
                    <TableHead>MOQ</TableHead>
                    <TableHead>Certifications</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {manufacturers.map((mfg) => (
                    <TableRow
                      key={mfg.id}
                      className="cursor-pointer"
                      onClick={() => setSelectedMfg(mfg)}
                    >
                      <TableCell>
                        <FavoriteButton
                          isFavorite={mfg.is_favorite}
                          onToggle={() =>
                            updateMfg.mutate({
                              id: mfg.id,
                              data: { is_favorite: !mfg.is_favorite },
                            })
                          }
                          size="sm"
                        />
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium text-gray-900">{mfg.name}</p>
                          {mfg.website && (
                            <p className="text-xs text-gray-400 truncate max-w-[200px]">
                              {mfg.website}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">
                          {mfg.location || "N/A"}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant={scoreBadgeVariant(mfg.match_score)}>
                          {mfg.match_score.toFixed(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-600">
                          {mfg.moq ? mfg.moq.toLocaleString() : "N/A"}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1 max-w-[200px]">
                          {mfg.certifications?.slice(0, 2).map((c) => (
                            <Badge key={c} variant="outline" className="text-xs">
                              {c}
                            </Badge>
                          ))}
                          {(mfg.certifications?.length || 0) > 2 && (
                            <Badge variant="outline" className="text-xs">
                              +{(mfg.certifications?.length || 0) - 2}
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>

            {/* Detail Dialog */}
            {selectedMfg && (
              <ManufacturerCard
                manufacturer={selectedMfg}
                open={!!selectedMfg}
                onClose={() => setSelectedMfg(null)}
              />
            )}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
