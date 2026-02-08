"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useDeleteActivity } from "@/hooks/useActivities";
import { formatDateTime } from "@/lib/utils";
import { toast } from "sonner";
import type { ContactActivity } from "@/types/api";
import {
  Mail,
  Phone,
  Users,
  FileText,
  Package,
  StickyNote,
  Trash2,
} from "lucide-react";

const ACTIVITY_ICONS: Record<string, typeof Mail> = {
  email: Mail,
  call: Phone,
  meeting: Users,
  quote_received: FileText,
  sample_requested: Package,
  note: StickyNote,
};

const ACTIVITY_COLORS: Record<string, string> = {
  email: "bg-blue-100 text-blue-700",
  call: "bg-green-100 text-green-700",
  meeting: "bg-purple-100 text-purple-700",
  quote_received: "bg-amber-100 text-amber-700",
  sample_requested: "bg-orange-100 text-orange-700",
  note: "bg-gray-100 text-gray-700",
};

interface ContactTimelineProps {
  activities: ContactActivity[];
  manufacturerId: string;
}

export function ContactTimeline({
  activities,
  manufacturerId,
}: ContactTimelineProps) {
  const deleteActivity = useDeleteActivity();

  const handleDelete = async (activityId: string) => {
    if (!confirm("Delete this activity?")) return;
    try {
      await deleteActivity.mutateAsync({ activityId, manufacturerId });
      toast.success("Activity deleted");
    } catch {
      toast.error("Failed to delete activity");
    }
  };

  if (activities.length === 0) {
    return (
      <p className="text-sm text-gray-400 italic py-4">No activities yet.</p>
    );
  }

  return (
    <div className="relative space-y-0">
      {/* Vertical line */}
      <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-gray-200" />

      {activities.map((activity) => {
        const Icon = ACTIVITY_ICONS[activity.activity_type] || StickyNote;
        const colorClass =
          ACTIVITY_COLORS[activity.activity_type] ||
          "bg-gray-100 text-gray-700";

        return (
          <div key={activity.id} className="relative flex gap-3 pb-4">
            {/* Icon dot */}
            <div
              className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${colorClass}`}
            >
              <Icon className="h-4 w-4" />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0 pt-0.5">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {activity.subject}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Badge variant="outline" className="text-xs">
                      {activity.activity_type.replace("_", " ")}
                    </Badge>
                    <span className="text-xs text-gray-400">
                      {formatDateTime(activity.contact_date)}
                    </span>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 shrink-0"
                  onClick={() => handleDelete(activity.id)}
                >
                  <Trash2 className="h-3 w-3 text-gray-400" />
                </Button>
              </div>
              {activity.content && (
                <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">
                  {activity.content}
                </p>
              )}
              {activity.reminder_date && (
                <p className="text-xs text-amber-600 mt-1">
                  Reminder: {formatDateTime(activity.reminder_date)}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
