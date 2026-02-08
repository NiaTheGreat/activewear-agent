"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateActivity } from "@/hooks/useActivities";
import { ACTIVITY_TYPES } from "@/lib/constants";
import { toast } from "sonner";
import type { ActivityType } from "@/types/api";
import { Save } from "lucide-react";

interface AddActivityDialogProps {
  manufacturerId: string;
  open: boolean;
  onClose: () => void;
}

export function AddActivityDialog({
  manufacturerId,
  open,
  onClose,
}: AddActivityDialogProps) {
  const createActivity = useCreateActivity();

  const [activityType, setActivityType] = useState<ActivityType>("email");
  const [subject, setSubject] = useState("");
  const [content, setContent] = useState("");
  const [contactDate, setContactDate] = useState(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  });
  const [reminderDate, setReminderDate] = useState("");

  const resetForm = () => {
    setActivityType("email");
    setSubject("");
    setContent("");
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    setContactDate(now.toISOString().slice(0, 16));
    setReminderDate("");
  };

  const handleSubmit = async () => {
    if (!subject.trim()) {
      toast.error("Subject is required");
      return;
    }
    if (!contactDate) {
      toast.error("Date is required");
      return;
    }

    try {
      await createActivity.mutateAsync({
        manufacturerId,
        data: {
          activity_type: activityType,
          subject: subject.trim(),
          content: content.trim() || undefined,
          contact_date: new Date(contactDate).toISOString(),
          reminder_date: reminderDate
            ? new Date(reminderDate).toISOString()
            : undefined,
        },
      });
      toast.success("Activity logged");
      resetForm();
      onClose();
    } catch {
      toast.error("Failed to log activity");
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Log Activity</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 mt-2">
          {/* Activity Type */}
          <div className="space-y-1">
            <Label htmlFor="activityType">Type</Label>
            <select
              id="activityType"
              value={activityType}
              onChange={(e) => setActivityType(e.target.value as ActivityType)}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              {ACTIVITY_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* Subject */}
          <div className="space-y-1">
            <Label htmlFor="actSubject">Subject *</Label>
            <Input
              id="actSubject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="e.g. Initial outreach email"
            />
          </div>

          {/* Date */}
          <div className="space-y-1">
            <Label htmlFor="actDate">Date *</Label>
            <Input
              id="actDate"
              type="datetime-local"
              value={contactDate}
              onChange={(e) => setContactDate(e.target.value)}
            />
          </div>

          {/* Content */}
          <div className="space-y-1">
            <Label htmlFor="actContent">Details</Label>
            <Textarea
              id="actContent"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Notes about this interaction..."
              rows={3}
            />
          </div>

          {/* Reminder */}
          <div className="space-y-1">
            <Label htmlFor="actReminder">Follow-up Reminder</Label>
            <Input
              id="actReminder"
              type="datetime-local"
              value={reminderDate}
              onChange={(e) => setReminderDate(e.target.value)}
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={createActivity.isPending}
            >
              <Save className="mr-1 h-3 w-3" />
              {createActivity.isPending ? "Saving..." : "Log Activity"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
