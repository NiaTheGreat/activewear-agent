"use client";

import { useState } from "react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { ScoringBreakdown } from "./ScoringBreakdown";
import { FavoriteButton } from "./FavoriteButton";
import { useUpdateManufacturer } from "@/hooks/useManufacturers";
import type { Manufacturer } from "@/types/api";
import {
  Globe,
  MapPin,
  Mail,
  Phone,
  Package,
  Award,
  Layers,
  Scissors,
  ExternalLink,
  Save,
  Tag,
  X,
} from "lucide-react";

interface ManufacturerCardProps {
  manufacturer: Manufacturer;
  open: boolean;
  onClose: () => void;
}

export function ManufacturerCard({
  manufacturer: mfg,
  open,
  onClose,
}: ManufacturerCardProps) {
  const [userNotes, setUserNotes] = useState(mfg.user_notes || "");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>(mfg.user_tags || []);
  const updateMfg = useUpdateManufacturer();

  const handleSaveNotes = async () => {
    try {
      await updateMfg.mutateAsync({
        id: mfg.id,
        data: { user_notes: userNotes },
      });
      toast.success("Notes saved");
    } catch {
      toast.error("Failed to save notes");
    }
  };

  const handleAddTag = () => {
    const tag = tagInput.trim();
    if (tag && !tags.includes(tag)) {
      const newTags = [...tags, tag];
      setTags(newTags);
      setTagInput("");
      updateMfg.mutate({ id: mfg.id, data: { user_tags: newTags } });
    }
  };

  const handleRemoveTag = (tag: string) => {
    const newTags = tags.filter((t) => t !== tag);
    setTags(newTags);
    updateMfg.mutate({ id: mfg.id, data: { user_tags: newTags } });
  };

  const handleToggleFavorite = () => {
    updateMfg.mutate({
      id: mfg.id,
      data: { is_favorite: !mfg.is_favorite },
    });
  };

  const scoreColor =
    mfg.match_score >= 70
      ? "text-success-700 bg-success-50"
      : mfg.match_score >= 40
      ? "text-warning-700 bg-warning-50"
      : "text-error-700 bg-error-50";

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <div className="flex items-start justify-between pr-8">
            <div>
              <DialogTitle className="text-xl">{mfg.name}</DialogTitle>
              <div className="flex items-center gap-2 mt-1 text-sm text-gray-500">
                {mfg.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {mfg.location}
                  </span>
                )}
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-semibold ${scoreColor}`}
                >
                  Score: {mfg.match_score.toFixed(1)}
                </span>
              </div>
            </div>
            <FavoriteButton
              isFavorite={mfg.is_favorite}
              onToggle={handleToggleFavorite}
            />
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-2">
          {/* Overview */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {mfg.website && (
              <a
                href={mfg.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700"
              >
                <Globe className="h-4 w-4" />
                Visit Website
                <ExternalLink className="h-3 w-3" />
              </a>
            )}
            {mfg.source_url && (
              <a
                href={mfg.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700"
              >
                <ExternalLink className="h-4 w-4" />
                Source
              </a>
            )}
          </div>

          {/* Contact */}
          {mfg.contact && Object.keys(mfg.contact).length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Contact
              </h4>
              <div className="rounded-lg bg-gray-50 p-4 space-y-2">
                {mfg.contact.email && (
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="h-4 w-4 text-gray-400" />
                    <a
                      href={`mailto:${mfg.contact.email}`}
                      className="text-primary-600 hover:underline"
                    >
                      {mfg.contact.email}
                    </a>
                  </div>
                )}
                {mfg.contact.phone && (
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="h-4 w-4 text-gray-400" />
                    <span className="text-gray-700">{mfg.contact.phone}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          <Separator />

          {/* Capabilities */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {mfg.materials && mfg.materials.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Layers className="h-4 w-4 text-gray-400" />
                  Materials
                </h4>
                <div className="flex flex-wrap gap-1">
                  {mfg.materials.map((m) => (
                    <Badge key={m} variant="secondary">
                      {m}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {mfg.production_methods && mfg.production_methods.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Scissors className="h-4 w-4 text-gray-400" />
                  Production Methods
                </h4>
                <div className="flex flex-wrap gap-1">
                  {mfg.production_methods.map((m) => (
                    <Badge key={m} variant="secondary">
                      {m}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {mfg.certifications && mfg.certifications.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Award className="h-4 w-4 text-gray-400" />
                  Certifications
                </h4>
                <div className="flex flex-wrap gap-1">
                  {mfg.certifications.map((c) => (
                    <Badge key={c} variant="default">
                      {c}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {(mfg.moq || mfg.moq_description) && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <Package className="h-4 w-4 text-gray-400" />
                  MOQ
                </h4>
                <p className="text-sm text-gray-600">
                  {mfg.moq ? `${mfg.moq.toLocaleString()} units` : ""}
                  {mfg.moq_description ? ` (${mfg.moq_description})` : ""}
                </p>
              </div>
            )}
          </div>

          {/* Agent Notes */}
          {mfg.notes && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">
                Agent Notes
              </h4>
              <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
                {mfg.notes}
              </p>
            </div>
          )}

          <Separator />

          {/* Scoring Breakdown */}
          {mfg.scoring_breakdown && (
            <ScoringBreakdown
              breakdown={mfg.scoring_breakdown}
              totalScore={mfg.match_score}
            />
          )}

          <Separator />

          {/* User Tags */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
              <Tag className="h-4 w-4 text-gray-400" />
              Tags
            </h4>
            <div className="flex flex-wrap gap-1 mb-2">
              {tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary-50 text-primary-700 text-xs"
                >
                  {tag}
                  <button
                    onClick={() => handleRemoveTag(tag)}
                    className="hover:text-primary-900"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Add tag..."
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddTag())}
                className="flex-1"
              />
              <Button
                variant="outline"
                size="sm"
                onClick={handleAddTag}
                disabled={!tagInput.trim()}
              >
                Add
              </Button>
            </div>
          </div>

          {/* User Notes */}
          <div>
            <Label htmlFor="userNotes">Your Notes</Label>
            <Textarea
              id="userNotes"
              value={userNotes}
              onChange={(e) => setUserNotes(e.target.value)}
              placeholder="Add your notes about this manufacturer..."
              rows={3}
              className="mt-1"
            />
            <Button
              size="sm"
              onClick={handleSaveNotes}
              disabled={updateMfg.isPending}
              className="mt-2"
            >
              <Save className="mr-1 h-3 w-3" />
              Save Notes
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
