"use client";

import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { ScoreAnimatedNumber } from "./ScoreAnimatedNumber";
import { Info } from "lucide-react";
import type { ScoringBreakdown as ScoringBreakdownType } from "@/types/api";

interface ScoringBreakdownProps {
  breakdown: ScoringBreakdownType;
  totalScore: number;
}

const categories = [
  { key: "location", label: "Location", max: 25, color: "bg-blue-500" },
  { key: "moq", label: "MOQ", max: 20, color: "bg-violet-500" },
  {
    key: "certifications",
    label: "Certifications",
    max: 25,
    color: "bg-emerald-500",
  },
  { key: "materials", label: "Materials", max: 15, color: "bg-amber-500" },
  {
    key: "production",
    label: "Production",
    max: 15,
    color: "bg-rose-500",
  },
];

export function ScoringBreakdown({
  breakdown,
  totalScore,
}: ScoringBreakdownProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700">Score Breakdown</h4>
        <div className="text-2xl font-bold text-primary-600">
          <ScoreAnimatedNumber value={totalScore} decimals={1} />
          <span className="text-sm font-normal text-gray-400">/100</span>
        </div>
      </div>

      <div className="space-y-3">
        {categories.map((cat) => {
          const data = breakdown[cat.key] as
            | { score: number; max: number; reason?: string }
            | undefined;
          const score = data?.score ?? 0;
          const percentage = (score / cat.max) * 100;

          return (
            <div key={cat.key} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-1">
                  <span className="text-gray-600">{cat.label}</span>
                  {data?.reason && (
                    <Tooltip>
                      <TooltipTrigger>
                        <Info className="h-3 w-3 text-gray-400" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs">{data.reason}</p>
                      </TooltipContent>
                    </Tooltip>
                  )}
                </div>
                <span className="font-medium text-gray-900">
                  {score}/{cat.max}
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className={`h-full rounded-full ${cat.color} transition-all duration-700 ease-out`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Bonuses */}
      {breakdown.bonuses &&
        typeof breakdown.bonuses === "object" &&
        "score" in breakdown.bonuses &&
        breakdown.bonuses.score > 0 && (
          <div className="rounded-lg bg-success-50 p-3 mt-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-success-700 font-medium">Bonuses</span>
              <span className="font-medium text-success-700">
                +{(breakdown.bonuses as { score: number }).score}
              </span>
            </div>
            {(breakdown.bonuses as { details?: string[] }).details && (
              <ul className="mt-1 text-xs text-success-700 space-y-0.5">
                {(breakdown.bonuses as { details: string[] }).details.map(
                  (d, i) => (
                    <li key={i}>{d}</li>
                  )
                )}
              </ul>
            )}
          </div>
        )}

      {/* Deductions */}
      {breakdown.deductions &&
        typeof breakdown.deductions === "object" &&
        "score" in breakdown.deductions &&
        breakdown.deductions.score > 0 && (
          <div className="rounded-lg bg-error-50 p-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-error-700 font-medium">Deductions</span>
              <span className="font-medium text-error-700">
                -{(breakdown.deductions as { score: number }).score}
              </span>
            </div>
          </div>
        )}
    </div>
  );
}
