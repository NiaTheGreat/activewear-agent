"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useSearchHistory } from "@/hooks/useSearch";
import { PageTransition } from "@/components/layout/PageTransition";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/common/EmptyState";
import { CardSkeleton } from "@/components/common/LoadingSkeleton";
import { formatDateTime } from "@/lib/utils";
import {
  Search,
  Factory,
  TrendingUp,
  Clock,
  ArrowRight,
  Plus,
} from "lucide-react";

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const router = useRouter();
  const { data: searches, isLoading } = useSearchHistory();

  const completedSearches = searches?.filter((s) => s.status === "completed") || [];
  const totalManufacturers = completedSearches.reduce(
    (sum, s) => sum + s.total_found,
    0
  );
  const recentSearches = searches?.slice(0, 5) || [];

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
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
              Welcome back{user?.full_name ? `, ${user.full_name}` : ""}
            </h1>
            <p className="text-gray-500 mt-1">
              Here&apos;s an overview of your manufacturer searches
            </p>
          </div>
          <Button onClick={() => router.push("/search/new")}>
            <Plus className="mr-2 h-4 w-4" />
            New Search
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-primary-50 p-3">
                  <Search className="h-5 w-5 text-primary-600" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {searches?.length || 0}
                  </p>
                  <p className="text-sm text-gray-500">Total Searches</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-success-50 p-3">
                  <Factory className="h-5 w-5 text-success-700" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {totalManufacturers}
                  </p>
                  <p className="text-sm text-gray-500">
                    Manufacturers Found
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-warning-50 p-3">
                  <TrendingUp className="h-5 w-5 text-warning-700" />
                </div>
                <div>
                  <p className="text-2xl font-semibold text-gray-900">
                    {completedSearches.length}
                  </p>
                  <p className="text-sm text-gray-500">Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Searches */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Searches</CardTitle>
                <CardDescription>
                  Your latest manufacturer discovery searches
                </CardDescription>
              </div>
              {searches && searches.length > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => router.push("/history")}
                >
                  View all
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <CardSkeleton key={i} />
                ))}
              </div>
            ) : recentSearches.length === 0 ? (
              <EmptyState
                icon={Clock}
                title="No searches yet"
                description="Start your first manufacturer search to discover activewear suppliers."
                actionLabel="Start Search"
                onAction={() => router.push("/search/new")}
              />
            ) : (
              <div className="space-y-3">
                {recentSearches.map((search) => (
                  <button
                    key={search.id}
                    onClick={() => router.push(`/search/${search.id}`)}
                    className="w-full flex items-center justify-between rounded-lg border border-gray-100 p-4 hover:bg-gray-50 transition-colors text-left"
                  >
                    <div className="flex items-center gap-4">
                      <div className="rounded-lg bg-gray-100 p-2">
                        <Search className="h-4 w-4 text-gray-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {(search.criteria as Record<string, unknown>)?.locations
                            ? (
                                (search.criteria as Record<string, string[]>)
                                  .locations || []
                              ).join(", ")
                            : "All Locations"}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatDateTime(search.created_at)}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-500">
                        {search.total_found} found
                      </span>
                      <Badge variant={statusVariant(search.status)}>
                        {search.status}
                      </Badge>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  );
}
