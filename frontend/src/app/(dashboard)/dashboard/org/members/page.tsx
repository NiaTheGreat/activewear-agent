"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useOrganizationStore } from "@/store/organizationStore";
import {
  useOrganizationMembers,
  useInviteMember,
  useUpdateMemberRole,
  useRemoveMember,
} from "@/hooks/useOrganizations";
import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
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
import { toast } from "sonner";
import { Users, Plus, Trash2 } from "lucide-react";
import type { OrganizationRole } from "@/types/api";

const inviteSchema = z.object({
  email: z.string().email("Invalid email address"),
  role: z.enum(["owner", "admin", "member", "viewer"]),
});

type InviteFormData = z.infer<typeof inviteSchema>;

export default function OrganizationMembersPage() {
  const { currentOrganization, isPersonalWorkspace } = useOrganizationStore();
  const [showInviteForm, setShowInviteForm] = useState(false);

  const { data: members, isLoading } = useOrganizationMembers(currentOrganization?.id);
  const inviteMember = useInviteMember(currentOrganization?.id || "");
  const updateRole = useUpdateMemberRole(currentOrganization?.id || "");
  const removeMember = useRemoveMember(currentOrganization?.id || "");

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

  if (isPersonalWorkspace() || !currentOrganization) {
    return (
      <div className="container mx-auto max-w-6xl px-4 py-8">
        <EmptyState
          icon={Users}
          title="No organization selected"
          description="Please select an organization to manage members"
        />
      </div>
    );
  }

  const onInvite = async (data: InviteFormData) => {
    try {
      await inviteMember.mutateAsync(data);
      toast.success(`Invited ${data.email} to ${currentOrganization.name}`);
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
      default:
        return "outline";
    }
  };

  return (
    <div className="container mx-auto max-w-5xl px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Team Members</h1>
        <p className="mt-1 text-muted-foreground">
          Manage members and roles for {currentOrganization.name}
        </p>
      </div>

      {/* Invite Form */}
      <div className="mb-6">
        {!showInviteForm ? (
          <Button onClick={() => setShowInviteForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Invite Member
          </Button>
        ) : (
          <form onSubmit={handleSubmit(onInvite)} className="space-y-4 rounded-lg border p-4">
            <h3 className="font-semibold">Invite New Member</h3>
            <div className="grid gap-4 sm:grid-cols-2">
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
                  onValueChange={(value) => setValue("role", value as OrganizationRole)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="member">Member</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="owner">Owner</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowInviteForm(false);
                  reset();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={inviteMember.isPending}>
                {inviteMember.isPending ? "Inviting..." : "Send Invite"}
              </Button>
            </div>
          </form>
        )}
      </div>

      {/* Members Table */}
      <div className="rounded-md border">
        {isLoading ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            Loading members...
          </div>
        ) : (members?.length ?? 0) === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            No members found. Invite someone to get started!
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Joined</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {members.map((member) => (
                <TableRow key={member.id}>
                  <TableCell className="font-medium">
                    {member.user_email}
                  </TableCell>
                  <TableCell>
                    {member.user_full_name || (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell>
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
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(member.joined_at).toLocaleDateString()}
                  </TableCell>
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
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}
