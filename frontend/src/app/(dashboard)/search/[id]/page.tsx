"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { PageTransition } from "@/components/layout/PageTransition";
import { SearchProgress } from "@/components/search/SearchProgress";
import { ManufacturerTable } from "@/components/results/ManufacturerTable";
import { useSearchStatus } from "@/hooks/useSearch";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { CardSkeleton } from "@/components/common/LoadingSkeleton";
import { ArrowLeft, RotateCcw } from "lucide-react";

export default function SearchDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { data: status, isLoading, refetch } = useSearchStatus(id);
  const [showResults, setShowResults] = useState(false);

  const isRunning =
    status?.status === "running" || status?.status === "pending";
  const isCompleted = status?.status === "completed";
  const isFailed = status?.status === "failed";

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/history")}
            >
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back
            </Button>
            <h1 className="text-xl font-semibold tracking-tight text-gray-900">
              Search Results
            </h1>
            {status && (
              <Badge
                variant={
                  isCompleted
                    ? "success"
                    : isFailed
                    ? "destructive"
                    : "warning"
                }
              >
                {status.status}
              </Badge>
            )}
          </div>
          {isFailed && (
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              <RotateCcw className="mr-1 h-4 w-4" />
              Retry
            </Button>
          )}
        </div>

        {isLoading ? (
          <CardSkeleton />
        ) : isRunning ? (
          <SearchProgress
            searchId={id}
            onComplete={() => setShowResults(true)}
          />
        ) : null}

        {(isCompleted || showResults) && <ManufacturerTable searchId={id} />}
      </div>
    </PageTransition>
  );
}
