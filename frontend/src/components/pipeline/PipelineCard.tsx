"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { MoreVertical, Edit, Trash2, Star } from "lucide-react";
import type { Pipeline } from "@/types/api";

interface PipelineCardProps {
  pipeline: Pipeline;
  onEdit?: () => void;
  onDelete?: () => void;
}

export function PipelineCard({ pipeline, onEdit, onDelete }: PipelineCardProps) {
  return (
    <Card className="group relative overflow-hidden transition-all hover:shadow-md">
      <Link href={`/dashboard/pipelines/${pipeline.id}`}>
        <CardContent className="p-6">
          {/* Color Bar */}
          <div
            className="absolute left-0 top-0 h-full w-1"
            style={{ backgroundColor: pipeline.color || "#3B82F6" }}
          />

          {/* Header */}
          <div className="mb-3 flex items-start justify-between">
            <div className="flex items-center gap-2">
              {pipeline.icon && (
                <span className="text-2xl">{pipeline.icon}</span>
              )}
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold">{pipeline.name}</h3>
                  {pipeline.is_default && (
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Star className="h-3 w-3" />
                      Default
                    </Badge>
                  )}
                </div>
                {pipeline.description && (
                  <p className="mt-1 text-sm text-muted-foreground line-clamp-2">
                    {pipeline.description}
                  </p>
                )}
              </div>
            </div>

            {/* Actions Menu */}
            {(onEdit || onDelete) && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild onClick={(e) => e.preventDefault()}>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="opacity-0 transition-opacity group-hover:opacity-100"
                  >
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {onEdit && (
                    <DropdownMenuItem onClick={(e) => {
                      e.preventDefault();
                      onEdit();
                    }}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </DropdownMenuItem>
                  )}
                  {onEdit && onDelete && <DropdownMenuSeparator />}
                  {onDelete && (
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.preventDefault();
                        onDelete();
                      }}
                      className="text-destructive"
                    >
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>

          {/* Stats */}
          <div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
            <div>
              <span className="font-semibold text-foreground">
                {pipeline.manufacturer_count || 0}
              </span>{" "}
              manufacturers
            </div>
            <div>
              Created {new Date(pipeline.created_at).toLocaleDateString()}
            </div>
          </div>
        </CardContent>
      </Link>
    </Card>
  );
}
