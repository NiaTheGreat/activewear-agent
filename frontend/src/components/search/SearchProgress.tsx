"use client";

import { useSearchStatus } from "@/hooks/useSearch";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScoreAnimatedNumber } from "@/components/results/ScoreAnimatedNumber";
import { Loader2, CheckCircle2, XCircle, Factory } from "lucide-react";

interface SearchProgressProps {
  searchId: string;
  onComplete?: () => void;
}

export function SearchProgress({ searchId, onComplete }: SearchProgressProps) {
  const { data: status } = useSearchStatus(searchId);

  if (!status) {
    return (
      <Card>
        <CardContent className="py-12 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-primary-500" />
        </CardContent>
      </Card>
    );
  }

  const isRunning = status.status === "running" || status.status === "pending";
  const isCompleted = status.status === "completed";
  const isFailed = status.status === "failed";

  if (isCompleted && onComplete) {
    setTimeout(onComplete, 500);
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            {isRunning && (
              <Loader2 className="h-5 w-5 animate-spin text-primary-500" />
            )}
            {isCompleted && (
              <CheckCircle2 className="h-5 w-5 text-success-500" />
            )}
            {isFailed && <XCircle className="h-5 w-5 text-error-500" />}
            Search Progress
          </CardTitle>
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
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Progress</span>
            <span className="font-medium text-gray-900">
              {status.progress}%
            </span>
          </div>
          <Progress value={status.progress} className="h-3" />
        </div>

        {/* Current Step */}
        {status.current_step && (
          <div className="rounded-lg bg-gray-50 p-4">
            <p className="text-sm font-medium text-gray-700">
              {status.current_step}
            </p>
            {status.current_detail && (
              <p className="text-xs text-gray-500 mt-1">
                {status.current_detail}
              </p>
            )}
          </div>
        )}

        {/* Manufacturers Found */}
        <div className="flex items-center gap-3 rounded-lg border border-gray-200 p-4">
          <div className="rounded-lg bg-primary-50 p-2">
            <Factory className="h-5 w-5 text-primary-600" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Manufacturers Found</p>
            <p className="text-2xl font-semibold text-gray-900">
              <ScoreAnimatedNumber value={status.total_found} />
            </p>
          </div>
        </div>

        {/* Error */}
        {isFailed && status.error_message && (
          <div className="rounded-lg bg-error-50 border border-error-500/20 p-4">
            <p className="text-sm text-error-700">{status.error_message}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
