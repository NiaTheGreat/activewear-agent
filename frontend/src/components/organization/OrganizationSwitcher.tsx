"use client";

import { useEffect } from "react";
import { Check, ChevronsUpDown, Building2, User, Plus } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { useOrganizations } from "@/hooks/useOrganizations";
import { useOrganizationStore } from "@/store/organizationStore";
import { CreateOrganizationDialog } from "./CreateOrganizationDialog";
import { cn } from "@/lib/utils";

export function OrganizationSwitcher() {
  const { data: organizations, isLoading } = useOrganizations();
  const {
    currentOrganization,
    setCurrentOrganization,
    setOrganizations: setStoreOrganizations,
  } = useOrganizationStore();

  // Sync organizations from API to store
  useEffect(() => {
    if (organizations) {
      setStoreOrganizations(organizations);
    }
  }, [organizations, setStoreOrganizations]);

  const handleSelect = (orgId: string | null) => {
    if (orgId === null) {
      setCurrentOrganization(null);
    } else {
      const org = organizations?.find((o) => o.id === orgId);
      if (org) {
        setCurrentOrganization(org);
      }
    }
  };

  const displayName = currentOrganization
    ? currentOrganization.name
    : "Personal Workspace";

  const displayIcon = currentOrganization ? (
    <Building2 className="h-4 w-4" />
  ) : (
    <User className="h-4 w-4" />
  );

  if (isLoading) {
    return (
      <div className="flex h-9 items-center rounded-md border border-input bg-background px-3">
        <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <span className="ml-2 text-sm">Loading...</span>
      </div>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="w-full justify-between"
        >
          <div className="flex items-center gap-2 truncate">
            {displayIcon}
            <span className="truncate">{displayName}</span>
          </div>
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[280px]" align="start">
        <DropdownMenuLabel>Switch Workspace</DropdownMenuLabel>
        <DropdownMenuSeparator />

        {/* Personal Workspace */}
        <DropdownMenuItem
          onClick={() => handleSelect(null)}
          className="cursor-pointer"
        >
          <User className="mr-2 h-4 w-4" />
          <span className="flex-1">Personal Workspace</span>
          {!currentOrganization && (
            <Check className="h-4 w-4 text-primary" />
          )}
        </DropdownMenuItem>

        {/* Organizations */}
        {organizations && organizations.length > 0 && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuLabel className="text-xs text-muted-foreground">
              Organizations
            </DropdownMenuLabel>
            {organizations.map((org) => (
              <DropdownMenuItem
                key={org.id}
                onClick={() => handleSelect(org.id)}
                className="cursor-pointer"
              >
                <Building2 className="mr-2 h-4 w-4" />
                <div className="flex-1 truncate">
                  <div className="truncate">{org.name}</div>
                  {org.member_count !== undefined && (
                    <div className="text-xs text-muted-foreground">
                      {org.member_count} {org.member_count === 1 ? "member" : "members"}
                    </div>
                  )}
                </div>
                {currentOrganization?.id === org.id && (
                  <Check className="h-4 w-4 text-primary" />
                )}
              </DropdownMenuItem>
            ))}
          </>
        )}

        <DropdownMenuSeparator />
        <CreateOrganizationDialog
          trigger={
            <DropdownMenuItem
              onSelect={(e) => e.preventDefault()}
              className="cursor-pointer"
            >
              <Plus className="mr-2 h-4 w-4" />
              Create Organization
            </DropdownMenuItem>
          }
        />
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
