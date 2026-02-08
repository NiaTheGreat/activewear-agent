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
import { ContactTimeline } from "./ContactTimeline";
import { AddActivityDialog } from "./AddActivityDialog";
import { useUpdateManufacturer, useDeleteManufacturer } from "@/hooks/useManufacturers";
import { useActivities } from "@/hooks/useActivities";
import { MANUFACTURER_STATUSES } from "@/lib/constants";
import { formatDateTime } from "@/lib/utils";
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
  Trash2,
  X,
  Pencil,
  CalendarClock,
  MessageSquarePlus,
  Kanban,
} from "lucide-react";

interface ManufacturerCardProps {
  manufacturer: Manufacturer;
  open: boolean;
  onClose: () => void;
}

export function ManufacturerCard({
  manufacturer: initialMfg,
  open,
  onClose,
}: ManufacturerCardProps) {
  // Local copy so the dialog reflects updates immediately after save
  const [mfg, setMfg] = useState(initialMfg);
  const [userNotes, setUserNotes] = useState(mfg.user_notes || "");
  const [tagInput, setTagInput] = useState("");
  const [tags, setTags] = useState<string[]>(mfg.user_tags || []);
  const updateMfg = useUpdateManufacturer();
  const deleteMfg = useDeleteManufacturer();

  // Sync when a different manufacturer is opened
  if (initialMfg.id !== mfg.id) {
    setMfg(initialMfg);
    setUserNotes(initialMfg.user_notes || "");
    setTags(initialMfg.user_tags || []);
  }

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(mfg.name);
  const [editWebsite, setEditWebsite] = useState(mfg.website);
  const [editLocation, setEditLocation] = useState(mfg.location || "");
  const [editEmail, setEditEmail] = useState(mfg.contact?.email || "");
  const [editPhone, setEditPhone] = useState(mfg.contact?.phone || "");
  const [editAddress, setEditAddress] = useState(mfg.contact?.address || "");
  const [editMaterials, setEditMaterials] = useState<string[]>(mfg.materials || []);
  const [editMaterialInput, setEditMaterialInput] = useState("");
  const [editProdMethods, setEditProdMethods] = useState<string[]>(mfg.production_methods || []);
  const [editProdMethodInput, setEditProdMethodInput] = useState("");
  const [editCertifications, setEditCertifications] = useState<string[]>(mfg.certifications || []);
  const [editCertInput, setEditCertInput] = useState("");
  const [editMoq, setEditMoq] = useState(mfg.moq?.toString() || "");
  const [editMoqDescription, setEditMoqDescription] = useState(mfg.moq_description || "");
  const [editNotes, setEditNotes] = useState(mfg.notes || "");

  // Contact tracking state
  const [showAddActivity, setShowAddActivity] = useState(false);
  const { data: activities = [] } = useActivities(open ? mfg.id : undefined);

  const handleStatusChange = async (newStatus: string) => {
    try {
      const updated = await updateMfg.mutateAsync({
        id: mfg.id,
        data: { status: newStatus },
      });
      setMfg(updated);
    } catch {
      toast.error("Failed to update status");
    }
  };

  const handleFollowupChange = async (value: string) => {
    try {
      const updated = await updateMfg.mutateAsync({
        id: mfg.id,
        data: {
          next_followup_date: value ? new Date(value).toISOString() : null,
        },
      });
      setMfg(updated);
    } catch {
      toast.error("Failed to update follow-up date");
    }
  };

  const handleAddToPipeline = async () => {
    try {
      const updated = await updateMfg.mutateAsync({
        id: mfg.id,
        data: { status: "new" },
      });
      setMfg(updated);
      toast.success("Added to pipeline");
    } catch {
      toast.error("Failed to add to pipeline");
    }
  };

  const handleRemoveFromPipeline = async () => {
    try {
      const updated = await updateMfg.mutateAsync({
        id: mfg.id,
        data: { status: null },
      });
      setMfg(updated);
      toast.success("Removed from pipeline");
    } catch {
      toast.error("Failed to remove from pipeline");
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${mfg.name}"? This cannot be undone.`)) return;
    try {
      await deleteMfg.mutateAsync(mfg.id);
      toast.success("Manufacturer deleted");
      onClose();
    } catch {
      toast.error("Failed to delete manufacturer");
    }
  };

  const handleSaveNotes = async () => {
    try {
      const updated = await updateMfg.mutateAsync({
        id: mfg.id,
        data: { user_notes: userNotes },
      });
      setMfg(updated);
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

  const handleStartEdit = () => {
    setEditName(mfg.name);
    setEditWebsite(mfg.website);
    setEditLocation(mfg.location || "");
    setEditEmail(mfg.contact?.email || "");
    setEditPhone(mfg.contact?.phone || "");
    setEditAddress(mfg.contact?.address || "");
    setEditMaterials(mfg.materials || []);
    setEditProdMethods(mfg.production_methods || []);
    setEditCertifications(mfg.certifications || []);
    setEditMoq(mfg.moq?.toString() || "");
    setEditMoqDescription(mfg.moq_description || "");
    setEditNotes(mfg.notes || "");
    setIsEditing(true);
  };

  const handleCancelEdit = () => setIsEditing(false);

  const handleSaveEdit = async () => {
    if (!editName.trim()) {
      toast.error("Name is required");
      return;
    }
    if (!editWebsite.trim()) {
      toast.error("Website is required");
      return;
    }
    const moqNum = editMoq ? parseInt(editMoq) : null;
    if (editMoq && (isNaN(moqNum!) || moqNum! < 0)) {
      toast.error("MOQ must be a non-negative number");
      return;
    }

    const contact: Record<string, string> = {};
    if (editEmail.trim()) contact.email = editEmail.trim();
    if (editPhone.trim()) contact.phone = editPhone.trim();
    if (editAddress.trim()) contact.address = editAddress.trim();

    try {
      const updated = await updateMfg.mutateAsync({
        id: mfg.id,
        data: {
          name: editName.trim(),
          website: editWebsite.trim(),
          location: editLocation.trim() || null,
          contact: Object.keys(contact).length > 0 ? contact : null,
          materials: editMaterials.length > 0 ? editMaterials : null,
          production_methods: editProdMethods.length > 0 ? editProdMethods : null,
          certifications: editCertifications.length > 0 ? editCertifications : null,
          moq: moqNum,
          moq_description: editMoqDescription.trim() || null,
          notes: editNotes.trim() || null,
        },
      });
      setMfg(updated);
      toast.success("Manufacturer updated");
      setIsEditing(false);
    } catch {
      toast.error("Failed to save changes");
    }
  };

  const addToList = (
    list: string[],
    setList: (v: string[]) => void,
    inputValue: string,
    setInput: (v: string) => void
  ) => {
    const val = inputValue.trim();
    if (val && !list.includes(val)) {
      setList([...list, val]);
      setInput("");
    }
  };

  const removeFromList = (
    list: string[],
    setList: (v: string[]) => void,
    item: string
  ) => {
    setList(list.filter((i) => i !== item));
  };

  const scoreColor =
    mfg.match_score >= 70
      ? "text-success-700 bg-success-50"
      : mfg.match_score >= 40
      ? "text-warning-700 bg-warning-50"
      : "text-error-700 bg-error-50";

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) { setIsEditing(false); onClose(); } }}>
      <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
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
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={isEditing ? handleCancelEdit : handleStartEdit}
                title={isEditing ? "Cancel editing" : "Edit manufacturer"}
              >
                {isEditing ? <X className="h-4 w-4" /> : <Pencil className="h-4 w-4" />}
              </Button>
              <FavoriteButton
                isFavorite={mfg.is_favorite}
                onToggle={handleToggleFavorite}
              />
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 mt-2">
          {isEditing ? (
            <div className="space-y-5">
              {/* Name */}
              <div className="space-y-1">
                <Label htmlFor="editName">Name *</Label>
                <Input id="editName" value={editName} onChange={(e) => setEditName(e.target.value)} />
              </div>

              {/* Website */}
              <div className="space-y-1">
                <Label htmlFor="editWebsite">Website *</Label>
                <Input id="editWebsite" value={editWebsite} onChange={(e) => setEditWebsite(e.target.value)} />
              </div>

              {/* Location */}
              <div className="space-y-1">
                <Label htmlFor="editLocation">Location</Label>
                <Input id="editLocation" value={editLocation} onChange={(e) => setEditLocation(e.target.value)} placeholder="e.g. China, Vietnam" />
              </div>

              <Separator />

              {/* Contact */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700">Contact</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label htmlFor="editEmail" className="text-xs">Email</Label>
                    <Input id="editEmail" type="email" value={editEmail} onChange={(e) => setEditEmail(e.target.value)} placeholder="email@example.com" />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor="editPhone" className="text-xs">Phone</Label>
                    <Input id="editPhone" value={editPhone} onChange={(e) => setEditPhone(e.target.value)} placeholder="+1 555-0100" />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label htmlFor="editAddress" className="text-xs">Address</Label>
                  <Input id="editAddress" value={editAddress} onChange={(e) => setEditAddress(e.target.value)} placeholder="Street address" />
                </div>
              </div>

              <Separator />

              {/* Materials */}
              <div>
                <Label>Materials</Label>
                <div className="flex flex-wrap gap-1 mt-1 mb-2">
                  {editMaterials.map((m) => (
                    <span key={m} className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs">
                      {m}
                      <button onClick={() => removeFromList(editMaterials, setEditMaterials, m)} className="hover:text-gray-900">
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input placeholder="Add material..." value={editMaterialInput} onChange={(e) => setEditMaterialInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addToList(editMaterials, setEditMaterials, editMaterialInput, setEditMaterialInput))} className="flex-1" />
                  <Button variant="outline" size="sm" onClick={() => addToList(editMaterials, setEditMaterials, editMaterialInput, setEditMaterialInput)} disabled={!editMaterialInput.trim()}>Add</Button>
                </div>
              </div>

              {/* Production Methods */}
              <div>
                <Label>Production Methods</Label>
                <div className="flex flex-wrap gap-1 mt-1 mb-2">
                  {editProdMethods.map((m) => (
                    <span key={m} className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs">
                      {m}
                      <button onClick={() => removeFromList(editProdMethods, setEditProdMethods, m)} className="hover:text-gray-900">
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input placeholder="Add production method..." value={editProdMethodInput} onChange={(e) => setEditProdMethodInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addToList(editProdMethods, setEditProdMethods, editProdMethodInput, setEditProdMethodInput))} className="flex-1" />
                  <Button variant="outline" size="sm" onClick={() => addToList(editProdMethods, setEditProdMethods, editProdMethodInput, setEditProdMethodInput)} disabled={!editProdMethodInput.trim()}>Add</Button>
                </div>
              </div>

              {/* Certifications */}
              <div>
                <Label>Certifications</Label>
                <div className="flex flex-wrap gap-1 mt-1 mb-2">
                  {editCertifications.map((c) => (
                    <span key={c} className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-primary-50 text-primary-700 text-xs">
                      {c}
                      <button onClick={() => removeFromList(editCertifications, setEditCertifications, c)} className="hover:text-primary-900">
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input placeholder="Add certification..." value={editCertInput} onChange={(e) => setEditCertInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addToList(editCertifications, setEditCertifications, editCertInput, setEditCertInput))} className="flex-1" />
                  <Button variant="outline" size="sm" onClick={() => addToList(editCertifications, setEditCertifications, editCertInput, setEditCertInput)} disabled={!editCertInput.trim()}>Add</Button>
                </div>
              </div>

              <Separator />

              {/* MOQ */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label htmlFor="editMoq">MOQ (units)</Label>
                  <Input id="editMoq" type="number" value={editMoq} onChange={(e) => setEditMoq(e.target.value)} min={0} placeholder="e.g. 500" />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="editMoqDesc">MOQ Description</Label>
                  <Input id="editMoqDesc" value={editMoqDescription} onChange={(e) => setEditMoqDescription(e.target.value)} placeholder="e.g. Flexible for first order" />
                </div>
              </div>

              {/* Agent Notes */}
              <div className="space-y-1">
                <Label htmlFor="editAgentNotes">Agent Notes</Label>
                <Textarea id="editAgentNotes" value={editNotes} onChange={(e) => setEditNotes(e.target.value)} rows={3} placeholder="Notes about this manufacturer..." />
              </div>

              <Separator />

              {/* Save / Cancel */}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={handleCancelEdit}>Cancel</Button>
                <Button onClick={handleSaveEdit} disabled={updateMfg.isPending}>
                  <Save className="mr-1 h-3 w-3" />
                  {updateMfg.isPending ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </div>
          ) : (
            <>
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
            </>
          )}

          <Separator />

          {/* Pipeline */}
          {mfg.status == null ? (
            <div className="flex items-center justify-between rounded-lg border border-dashed border-gray-300 p-4">
              <p className="text-sm text-gray-500">Not in pipeline yet</p>
              <Button variant="outline" size="sm" onClick={handleAddToPipeline}>
                <Kanban className="mr-1 h-3 w-3" />
                Add to Pipeline
              </Button>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label htmlFor="mfgStatus" className="text-sm font-medium text-gray-700">
                    Pipeline Status
                  </Label>
                  <select
                    id="mfgStatus"
                    value={mfg.status}
                    onChange={(e) => handleStatusChange(e.target.value)}
                    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                  >
                    {MANUFACTURER_STATUSES.map((s) => (
                      <option key={s.value} value={s.value}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-1">
                  <Label htmlFor="mfgFollowup" className="text-sm font-medium text-gray-700 flex items-center gap-1">
                    <CalendarClock className="h-3.5 w-3.5 text-gray-400" />
                    Next Follow-up
                  </Label>
                  <Input
                    id="mfgFollowup"
                    type="datetime-local"
                    value={
                      mfg.next_followup_date
                        ? new Date(mfg.next_followup_date)
                            .toISOString()
                            .slice(0, 16)
                        : ""
                    }
                    onChange={(e) => handleFollowupChange(e.target.value)}
                  />
                  {mfg.next_followup_date && (
                    <p className="text-xs text-amber-600">
                      {formatDateTime(mfg.next_followup_date)}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={handleRemoveFromPipeline}
                  className="text-xs text-gray-400 hover:text-red-500 transition-colors"
                >
                  Remove from pipeline
                </button>
              </div>

              <Separator />

              {/* Contact History */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-sm font-medium text-gray-700">
                    Contact History
                  </h4>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAddActivity(true)}
                  >
                    <MessageSquarePlus className="mr-1 h-3 w-3" />
                    Log Activity
                  </Button>
                </div>
                <ContactTimeline
                  activities={activities}
                  manufacturerId={mfg.id}
                />
              </div>

              <AddActivityDialog
                manufacturerId={mfg.id}
                open={showAddActivity}
                onClose={() => setShowAddActivity(false)}
              />
            </>
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

          <Separator />

          {/* Delete */}
          <div className="flex justify-end">
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={deleteMfg.isPending}
            >
              <Trash2 className="mr-1 h-3 w-3" />
              Delete Manufacturer
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
