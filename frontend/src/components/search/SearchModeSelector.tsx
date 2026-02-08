"use client";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Wand2, PenTool, Blend } from "lucide-react";

interface SearchModeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

const modes = [
  {
    value: "auto",
    label: "Auto",
    icon: Wand2,
    description: "AI generates search queries automatically",
  },
  {
    value: "manual",
    label: "Manual",
    icon: PenTool,
    description: "You provide custom search queries",
  },
  {
    value: "hybrid",
    label: "Hybrid",
    icon: Blend,
    description: "AI queries + your custom queries",
  },
];

export function SearchModeSelector({
  value,
  onChange,
}: SearchModeSelectorProps) {
  return (
    <div className="grid w-full grid-cols-3 gap-1 rounded-lg bg-gray-100 p-1">
      {modes.map((mode) => {
        const isActive = value === mode.value;
        return (
          <Tooltip key={mode.value}>
            <TooltipTrigger asChild>
              <button
                type="button"
                onClick={() => onChange(mode.value)}
                className={`inline-flex items-center justify-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-all ${
                  isActive
                    ? "bg-primary-600 text-white shadow-sm"
                    : "text-gray-500 hover:text-gray-700"
                }`}
              >
                <mode.icon className="h-4 w-4" />
                {mode.label}
              </button>
            </TooltipTrigger>
            <TooltipContent>
              <p>{mode.description}</p>
            </TooltipContent>
          </Tooltip>
        );
      })}
    </div>
  );
}
