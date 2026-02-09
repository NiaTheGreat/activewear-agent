import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Organization } from "@/types/api";

interface OrganizationStore {
  // Current selected organization (null = personal workspace)
  currentOrganization: Organization | null;
  setCurrentOrganization: (org: Organization | null) => void;

  // List of user's organizations
  organizations: Organization[];
  setOrganizations: (orgs: Organization[]) => void;

  // Helper to check if in personal workspace
  isPersonalWorkspace: () => boolean;

  // Helper to get current org ID or null
  getCurrentOrgId: () => string | undefined;
}

export const useOrganizationStore = create<OrganizationStore>()(
  persist(
    (set, get) => ({
      currentOrganization: null,
      organizations: [],

      setCurrentOrganization: (org) => set({ currentOrganization: org }),

      setOrganizations: (orgs) => set({ organizations: orgs }),

      isPersonalWorkspace: () => get().currentOrganization === null,

      getCurrentOrgId: () => get().currentOrganization?.id,
    }),
    {
      name: "organization-storage",
    }
  )
);
