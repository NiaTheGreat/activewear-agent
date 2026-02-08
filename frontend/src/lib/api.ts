import { API_URL } from "./constants";
import type { ManufacturerUpdate, ManufacturerCreate, ContactActivityCreate, ContactActivityUpdate } from "@/types/api";

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
    }) =>
      request("/api/search/run", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    status: (id: string) => request(`/api/search/${id}/status`),
    get: (id: string) => request(`/api/search/${id}`),
    history: () => request("/api/search/history"),
    delete: (id: string) =>
      request(`/api/search/${id}`, { method: "DELETE" }),
  },
  manufacturers: {
    listAll: (
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
};
