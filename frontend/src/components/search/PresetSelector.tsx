"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { CriteriaPreset, SearchCriteria } from "@/types/api";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Bookmark } from "lucide-react";

interface PresetSelectorProps {
  onSelect: (criteria: SearchCriteria) => void;
}

export function PresetSelector({ onSelect }: PresetSelectorProps) {
  const { data: presets } = useQuery<CriteriaPreset[]>({
    queryKey: ["presets"],
    queryFn: () => api.presets.list() as Promise<CriteriaPreset[]>,
  });

  if (!presets || presets.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      <Bookmark className="h-4 w-4 text-gray-400" />
      <Select
        onValueChange={(id) => {
          const preset = presets.find((p) => p.id === id);
          if (preset) onSelect(preset.criteria);
        }}
      >
        <SelectTrigger className="w-[200px]">
          <SelectValue placeholder="Load from preset" />
        </SelectTrigger>
        <SelectContent>
          {presets.map((preset) => (
            <SelectItem key={preset.id} value={preset.id}>
              {preset.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
