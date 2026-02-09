import { API_URL } from "./constants";
import type {
  ManufacturerUpdate,
  ManufacturerCreate,
  ContactActivityCreate,
  ContactActivityUpdate,
  Organization,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationMember,
  OrganizationMemberCreate,
  OrganizationMemberUpdate,
  Pipeline,
  PipelineCreate,
  PipelineUpdate,
  PipelineManufacturer,
  AddManufacturerToPipeline,
  UpdatePipelineManufacturer,
} from "@/types/api";

async function request<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("token") : null;

  const config: RequestInit = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  };

  const response = await fetch(`${API_URL}${endpoint}`, config);

  if (response.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

export const api = {
  auth: {
    register: (data: {
      email: string;
      password: string;
      full_name?: string;
      company_name?: string;
    }) =>
      request("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    login: (email: string, password: string) =>
      request<{ access_token: string; token_type: string }>(
        "/api/auth/login",
        {
          method: "POST",
          body: JSON.stringify({ email, password }),
        }
      ),
    me: () =>
      request<{
        id: string;
        email: string;
        full_name?: string;
        company_name?: string;
        is_active: boolean;
        created_at: string;
      }>("/api/auth/me"),
  },
  presets: {
    list: () => request("/api/presets"),
    create: (data: {
      name: string;
      description?: string;
      criteria: Record<string, unknown>;
      is_public?: boolean;
    }) =>
      request("/api/presets", { method: "POST", body: JSON.stringify(data) }),
    get: (id: string) => request(`/api/presets/${id}`),
    update: (
      id: string,
      data: {
        name?: string;
        description?: string;
        criteria?: Record<string, unknown>;
        is_public?: boolean;
      }
    ) =>
      request(`/api/presets/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request(`/api/presets/${id}`, { method: "DELETE" }),
  },
  search: {
    run: (data: {
      criteria: Record<string, unknown>;
      criteria_preset_id?: string;
      search_mode?: string;
      max_manufacturers?: number;
      organization_id?: string;
    }) =>
      request("/api/search/run", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    status: (id: string) => request(`/api/search/${id}/status`),
    get: (id: string) => request(`/api/search/${id}`),
    history: (organizationId?: string) => {
      const query = organizationId ? `?organization_id=${organizationId}` : "";
      return request(`/api/search/history${query}`);
    },
    delete: (id: string) =>
      request(`/api/search/${id}`, { method: "DELETE" }),
  },
  manufacturers: {
    listAll: (
      params?: {
        organization_id?: string;
        sort_by?: string;
        sort_dir?: string;
        favorites_only?: boolean;
        min_score?: number;
      }
    ) => {
      const query = params
        ? `?${new URLSearchParams(
            Object.entries(params)
              .filter(([, v]) => v !== undefined)
              .map(([k, v]) => [k, String(v)])
          )}`
        : "";
      return request(`/api/manufacturers${query}`);
    },
    list: (
      searchId: string,
      params?: {
        sort_by?: string;
        sort_dir?: string;
        favorites_only?: boolean;
        min_score?: number;
      }
    ) => {
      const query = params
        ? `?${new URLSearchParams(
            Object.entries(params)
              .filter(([, v]) => v !== undefined)
              .map(([k, v]) => [k, String(v)])
          )}`
        : "";
      return request(`/api/search/${searchId}/manufacturers${query}`);
    },
    createManual: (data: ManufacturerCreate) =>
      request(`/api/manufacturers/manual`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    get: (id: string) => request(`/api/manufacturers/${id}`),
    update: (id: string, data: ManufacturerUpdate) =>
      request(`/api/manufacturers/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request(`/api/manufacturers/${id}`, { method: "DELETE" }),
    copyToOrganization: (
      manufacturerId: string,
      data: { organization_id: string; pipeline_ids?: string[] }
    ) =>
      request(`/api/manufacturers/${manufacturerId}/copy-to-organization`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    exportCsv: async (favoritesOnly?: boolean) => {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const params = new URLSearchParams();
      if (favoritesOnly) params.set("favorites_only", "true");
      const res = await fetch(
        `${API_URL}/api/manufacturers/export/csv?${params}`,
        {
          headers: {
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        }
      );
      if (!res.ok) throw new Error("Export failed");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = favoritesOnly ? "favorites.csv" : "manufacturers.csv";
      a.click();
      URL.revokeObjectURL(url);
    },
  },
  activities: {
    list: (manufacturerId: string) =>
      request(`/api/manufacturers/${manufacturerId}/activities`),
    create: (manufacturerId: string, data: ContactActivityCreate) =>
      request(`/api/manufacturers/${manufacturerId}/activities`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    update: (activityId: string, data: ContactActivityUpdate) =>
      request(`/api/activities/${activityId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (activityId: string) =>
      request(`/api/activities/${activityId}`, { method: "DELETE" }),
  },
  organizations: {
    list: () => request<Organization[]>("/api/organizations"),
    create: (data: OrganizationCreate) =>
      request("/api/organizations", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    get: (id: string) => request<Organization>(`/api/organizations/${id}`),
    update: (id: string, data: OrganizationUpdate) =>
      request(`/api/organizations/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request(`/api/organizations/${id}`, { method: "DELETE" }),
    // Members
    listMembers: (orgId: string) =>
      request<OrganizationMember[]>(`/api/organizations/${orgId}/members`),
    inviteMember: (orgId: string, data: OrganizationMemberCreate) =>
      request(`/api/organizations/${orgId}/members`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    updateMemberRole: (orgId: string, memberId: string, data: OrganizationMemberUpdate) =>
      request(`/api/organizations/${orgId}/members/${memberId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    removeMember: (orgId: string, memberId: string) =>
      request(`/api/organizations/${orgId}/members/${memberId}`, {
        method: "DELETE",
      }),
  },
  pipelines: {
    list: (orgId: string) =>
      request<Pipeline[]>(`/api/organizations/${orgId}/pipelines`),
    create: (orgId: string, data: PipelineCreate) =>
      request(`/api/organizations/${orgId}/pipelines`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    get: (id: string) => request<Pipeline>(`/api/pipelines/${id}`),
    update: (id: string, data: PipelineUpdate) =>
      request(`/api/pipelines/${id}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      request(`/api/pipelines/${id}`, { method: "DELETE" }),
    // Pipeline-Manufacturer relationships
    listManufacturers: (pipelineId: string) =>
      request<PipelineManufacturer[]>(`/api/pipelines/${pipelineId}/manufacturers`),
    addManufacturer: (pipelineId: string, data: AddManufacturerToPipeline) =>
      request(`/api/pipelines/${pipelineId}/manufacturers`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    updateManufacturer: (pmId: string, data: UpdatePipelineManufacturer) =>
      request(`/api/pipeline-manufacturers/${pmId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    removeManufacturer: (pmId: string) =>
      request(`/api/pipeline-manufacturers/${pmId}`, { method: "DELETE" }),
  },
};
