"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { useCreatePipeline } from "@/hooks/usePipelines";
import { toast } from "sonner";
import { Plus } from "lucide-react";

const schema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  description: z.string().max(1000).optional(),
  color: z.string().regex(/^#[0-9A-F]{6}$/i, "Must be a valid hex color").optional(),
  icon: z.string().max(50).optional(),
  is_default: z.boolean().optional(),
});

type FormData = z.infer<typeof schema>;

const PRESET_COLORS = [
  { name: "Blue", value: "#3B82F6" },
  { name: "Green", value: "#10B981" },
  { name: "Orange", value: "#F59E0B" },
  { name: "Purple", value: "#8B5CF6" },
  { name: "Red", value: "#EF4444" },
  { name: "Pink", value: "#EC4899" },
];

const PRESET_ICONS = ["📌", "🎯", "🌱", "🔄", "⭐", "🚀", "💎", "🏆"];

interface CreatePipelineDialogProps {
  organizationId: string;
  trigger?: React.ReactNode;
}

export function CreatePipelineDialog({
  organizationId,
  trigger,
}: CreatePipelineDialogProps) {
  const [open, setOpen] = useState(false);
  const createPipeline = useCreatePipeline(organizationId);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      color: PRESET_COLORS[0].value,
      icon: PRESET_ICONS[0],
      is_default: false,
    },
  });

  const selectedColor = watch("color");
  const selectedIcon = watch("icon");
  const isDefault = watch("is_default");

  const onSubmit = async (data: FormData) => {
    try {
      await createPipeline.mutateAsync(data);
      toast.success("Pipeline created successfully!");
      reset();
      setOpen(false);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to create pipeline");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Create Pipeline
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Create Pipeline</DialogTitle>
            <DialogDescription>
              Create a new pipeline to organize manufacturers.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="name">Pipeline Name</Label>
              <Input
                id="name"
                placeholder="Q1 2026 Production"
                {...register("name")}
              />
              {errors.name && (
                <p className="text-sm text-red-500">{errors.name.message}</p>
              )}
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">Description (optional)</Label>
              <Textarea
                id="description"
                placeholder="What is this pipeline for?"
                rows={2}
                {...register("description")}
              />
            </div>

            {/* Icon Picker */}
            <div className="grid gap-2">
              <Label>Icon</Label>
              <div className="flex flex-wrap gap-2">
                {PRESET_ICONS.map((icon) => (
                  <button
                    key={icon}
                    type="button"
                    onClick={() => setValue("icon", icon)}
                    className={`h-10 w-10 rounded border text-xl transition-colors ${
                      selectedIcon === icon
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50"
                    }`}
                  >
                    {icon}
                  </button>
                ))}
              </div>
            </div>

            {/* Color Picker */}
            <div className="grid gap-2">
              <Label>Color</Label>
              <div className="flex flex-wrap gap-2">
                {PRESET_COLORS.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => setValue("color", color.value)}
                    className={`h-10 w-10 rounded border transition-all ${
                      selectedColor === color.value
                        ? "scale-110 ring-2 ring-primary ring-offset-2"
                        : "hover:scale-105"
                    }`}
                    style={{ backgroundColor: color.value }}
                    title={color.name}
                  />
                ))}
              </div>
              <Input
                placeholder="#3B82F6"
                {...register("color")}
                className="w-32"
              />
              {errors.color && (
                <p className="text-sm text-red-500">{errors.color.message}</p>
              )}
            </div>

            {/* Default Pipeline */}
            <div className="flex items-center space-x-2">
              <Checkbox
                id="is_default"
                checked={isDefault}
                onCheckedChange={(checked) =>
                  setValue("is_default", checked === true)
                }
              />
              <Label
                htmlFor="is_default"
                className="text-sm font-normal leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Set as default pipeline (auto-add new manufacturers)
              </Label>
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createPipeline.isPending}>
              {createPipeline.isPending ? "Creating..." : "Create Pipeline"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
