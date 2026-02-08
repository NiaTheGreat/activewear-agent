"use client";

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
    <Tabs value={value} onValueChange={onChange}>
      <TabsList className="grid w-full grid-cols-3">
        {modes.map((mode) => (
          <Tooltip key={mode.value}>
            <TooltipTrigger asChild>
              <TabsTrigger value={mode.value} className="gap-2">
                <mode.icon className="h-4 w-4" />
                {mode.label}
              </TabsTrigger>
            </TooltipTrigger>
            <TooltipContent>
              <p>{mode.description}</p>
            </TooltipContent>
          </Tooltip>
        ))}
      </TabsList>
    </Tabs>
  );
}
