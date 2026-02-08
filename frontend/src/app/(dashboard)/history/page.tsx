"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { PageTransition } from "@/components/layout/PageTransition";
import { useSearchHistory, useDeleteSearch } from "@/hooks/useSearch";
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
import { TableSkeleton } from "@/components/common/LoadingSkeleton";
import { EmptyState } from "@/components/common/EmptyState";
import { formatDateTime } from "@/lib/utils";
import { Clock, Trash2, ExternalLink } from "lucide-react";

export default function HistoryPage() {
  const router = useRouter();
  const { data: searches, isLoading } = useSearchHistory();
  const deleteSearch = useDeleteSearch();

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this search and all its results?")) return;
    try {
      await deleteSearch.mutateAsync(id);
      toast.success("Search deleted");
    } catch {
      toast.error("Failed to delete search");
    }
  };

  const statusVariant = (status: string) => {
    switch (status) {
      case "completed":
        return "success" as const;
      case "running":
      case "pending":
        return "warning" as const;
      case "failed":
        return "destructive" as const;
      default:
        return "secondary" as const;
    }
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
              Search History
            </h1>
            <p className="text-gray-500 mt-1">
              View and manage your past searches
            </p>
          </div>
          <Button onClick={() => router.push("/search/new")}>
            New Search
          </Button>
        </div>

        {isLoading ? (
          <TableSkeleton rows={5} />
        ) : !searches || searches.length === 0 ? (
          <EmptyState
            icon={Clock}
            title="No search history"
            description="Your completed searches will appear here."
            actionLabel="Start a Search"
            onAction={() => router.push("/search/new")}
          />
        ) : (
          <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
            <Table>
              <TableHeader>
                <TableRow className="bg-gray-50/50">
                  <TableHead>Date</TableHead>
                  <TableHead>Locations</TableHead>
                  <TableHead>Mode</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Found</TableHead>
                  <TableHead className="w-20" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {searches.map((search) => {
                  const criteria = search.criteria as Record<string, unknown>;
                  const locations = (criteria?.locations as string[]) || [];
                  return (
                    <TableRow
                      key={search.id}
                      className="cursor-pointer"
                      onClick={() => router.push(`/search/${search.id}`)}
                    >
                      <TableCell className="text-sm text-gray-600">
                        {formatDateTime(search.created_at)}
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-gray-700">
                          {locations.length > 0
                            ? locations.slice(0, 3).join(", ")
                            : "All"}
                          {locations.length > 3 &&
                            ` +${locations.length - 3}`}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {search.search_mode}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusVariant(search.status)}>
                          {search.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm font-medium text-gray-900">
                        {search.total_found}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              router.push(`/search/${search.id}`);
                            }}
                          >
                            <ExternalLink className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => handleDelete(search.id, e)}
                            className="text-gray-400 hover:text-error-500"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </PageTransition>
  );
}
