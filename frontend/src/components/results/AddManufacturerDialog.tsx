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
import { useCreateManualManufacturer } from "@/hooks/useManufacturers";
import { toast } from "sonner";
import { Save } from "lucide-react";

interface AddManufacturerDialogProps {
  open: boolean;
  onClose: () => void;
}

export function AddManufacturerDialog({
  open,
  onClose,
}: AddManufacturerDialogProps) {
  const createMfg = useCreateManualManufacturer();

  const [name, setName] = useState("");
  const [website, setWebsite] = useState("");
  const [location, setLocation] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");

  const resetForm = () => {
    setName("");
    setWebsite("");
    setLocation("");
    setEmail("");
    setPhone("");
    setNotes("");
  };

  const handleSubmit = async () => {
    if (!name.trim()) {
      toast.error("Name is required");
      return;
    }

    const contact: Record<string, string> = {};
    if (email.trim()) contact.email = email.trim();
    if (phone.trim()) contact.phone = phone.trim();

    try {
      await createMfg.mutateAsync({
        name: name.trim(),
        website: website.trim() || undefined,
        location: location.trim() || undefined,
        contact: Object.keys(contact).length > 0 ? contact : undefined,
        notes: notes.trim() || undefined,
      });
      toast.success("Manufacturer added to pipeline");
      resetForm();
      onClose();
    } catch {
      toast.error("Failed to add manufacturer");
    }
  };

  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose(); }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add Manufacturer</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 mt-2">
          <div className="space-y-1">
            <Label htmlFor="mfgName">Name *</Label>
            <Input
              id="mfgName"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Acme Activewear Co."
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="mfgWebsite">Website</Label>
            <Input
              id="mfgWebsite"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              placeholder="e.g. https://acme-activewear.com"
            />
          </div>

          <div className="space-y-1">
            <Label htmlFor="mfgLocation">Location</Label>
            <Input
              id="mfgLocation"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Vietnam"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="mfgEmail" className="text-xs">Email</Label>
              <Input
                id="mfgEmail"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@example.com"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="mfgPhone" className="text-xs">Phone</Label>
              <Input
                id="mfgPhone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+1 555-0100"
              />
            </div>
          </div>

          <div className="space-y-1">
            <Label htmlFor="mfgNotes">Notes</Label>
            <Textarea
              id="mfgNotes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any notes about this manufacturer..."
              rows={2}
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={createMfg.isPending}>
              <Save className="mr-1 h-3 w-3" />
              {createMfg.isPending ? "Adding..." : "Add to Pipeline"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
