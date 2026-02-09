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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  useOrganizationMembers,
  useInviteMember,
  useUpdateMemberRole,
  useRemoveMember,
} from "@/hooks/useOrganizations";
import { toast } from "sonner";
import { Users, Plus, Trash2 } from "lucide-react";
import type { OrganizationRole } from "@/types/api";

const inviteSchema = z.object({
  email: z.string().email("Invalid email address"),
  role: z.enum(["owner", "admin", "member", "viewer"]),
});

type InviteFormData = z.infer<typeof inviteSchema>;

interface OrganizationMembersDialogProps {
  organizationId: string;
  organizationName: string;
  currentUserRole?: OrganizationRole;
  trigger?: React.ReactNode;
}

export function OrganizationMembersDialog({
  organizationId,
  organizationName,
  currentUserRole,
  trigger,
}: OrganizationMembersDialogProps) {
  const [open, setOpen] = useState(false);
  const [showInviteForm, setShowInviteForm] = useState(false);

  const { data: members, isLoading } = useOrganizationMembers(
    open ? organizationId : undefined
  );
  const inviteMember = useInviteMember(organizationId);
  const updateRole = useUpdateMemberRole(organizationId);
  const removeMember = useRemoveMember(organizationId);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch,
  } = useForm<InviteFormData>({
    resolver: zodResolver(inviteSchema),
    defaultValues: { role: "member" },
  });

  const selectedRole = watch("role");

  const canInvite = currentUserRole === "owner" || currentUserRole === "admin";
  const canChangeRoles = currentUserRole === "owner";
  const canRemove = currentUserRole === "owner" || currentUserRole === "admin";

  const onInvite = async (data: InviteFormData) => {
    try {
      await inviteMember.mutateAsync(data);
      toast.success(`Invited ${data.email} to ${organizationName}`);
      reset();
      setShowInviteForm(false);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to invite member");
    }
  };

  const handleRoleChange = async (memberId: string, newRole: OrganizationRole) => {
    try {
      await updateRole.mutateAsync({ memberId, data: { role: newRole } });
      toast.success("Role updated successfully");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to update role");
    }
  };

  const handleRemoveMember = async (memberId: string, memberEmail: string) => {
    if (!confirm(`Remove ${memberEmail} from this organization?`)) return;

    try {
      await removeMember.mutateAsync(memberId);
      toast.success("Member removed");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to remove member");
    }
  };

  const getRoleBadgeVariant = (role: OrganizationRole) => {
    switch (role) {
      case "owner":
        return "default";
      case "admin":
        return "secondary";
      case "member":
        return "outline";
      case "viewer":
        return "outline";
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm">
            <Users className="mr-2 h-4 w-4" />
            Members
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>Organization Members</DialogTitle>
          <DialogDescription>
            Manage members and roles for {organizationName}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Invite Form */}
          {canInvite && (
            <div>
              {!showInviteForm ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowInviteForm(true)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Invite Member
                </Button>
              ) : (
                <form onSubmit={handleSubmit(onInvite)} className="space-y-3 rounded-lg border p-4">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="grid gap-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="user@example.com"
                        {...register("email")}
                      />
                      {errors.email && (
                        <p className="text-sm text-red-500">{errors.email.message}</p>
                      )}
                    </div>

                    <div className="grid gap-2">
                      <Label htmlFor="role">Role</Label>
                      <Select
                        value={selectedRole}
                        onValueChange={(value) =>
                          setValue("role", value as OrganizationRole)
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="member">Member</SelectItem>
                          <SelectItem value="admin">Admin</SelectItem>
                          {currentUserRole === "owner" && (
                            <SelectItem value="owner">Owner</SelectItem>
                          )}
                          <SelectItem value="viewer">Viewer</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setShowInviteForm(false);
                        reset();
                      }}
                    >
                      Cancel
                    </Button>
                    <Button type="submit" size="sm" disabled={inviteMember.isPending}>
                      {inviteMember.isPending ? "Inviting..." : "Send Invite"}
                    </Button>
                  </div>
                </form>
              )}
            </div>
          )}

          {/* Members Table */}
          <div className="max-h-[400px] overflow-auto rounded-md border">
            {isLoading ? (
              <div className="p-8 text-center text-sm text-muted-foreground">
                Loading members...
              </div>
            ) : !members || members.length === 0 ? (
              <div className="p-8 text-center text-sm text-muted-foreground">
                No members found
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Joined</TableHead>
                    {canRemove && <TableHead className="w-[50px]"></TableHead>}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {members.map((member) => (
                    <TableRow key={member.id}>
                      <TableCell className="font-medium">
                        {member.user_email}
                      </TableCell>
                      <TableCell>
                        {member.user_full_name || <span className="text-muted-foreground">—</span>}
                      </TableCell>
                      <TableCell>
                        {canChangeRoles ? (
                          <Select
                            value={member.role}
                            onValueChange={(value) =>
                              handleRoleChange(member.id, value as OrganizationRole)
                            }
                            disabled={updateRole.isPending}
                          >
                            <SelectTrigger className="w-[120px]">
                              <Badge variant={getRoleBadgeVariant(member.role)}>
                                {member.role}
                              </Badge>
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="owner">Owner</SelectItem>
                              <SelectItem value="admin">Admin</SelectItem>
                              <SelectItem value="member">Member</SelectItem>
                              <SelectItem value="viewer">Viewer</SelectItem>
                            </SelectContent>
                          </Select>
                        ) : (
                          <Badge variant={getRoleBadgeVariant(member.role)}>
                            {member.role}
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(member.joined_at).toLocaleDateString()}
                      </TableCell>
                      {canRemove && (
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() =>
                              handleRemoveMember(member.id, member.user_email || "this member")
                            }
                            disabled={removeMember.isPending}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </TableCell>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
