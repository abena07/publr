import { getToken } from "./auth";

const BASE = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? res.statusText);
  }
  return res.json();
}

export const api = {
  me: () => request<{
    id: string;
    instagram_connected: boolean;
    gdrive_connected: boolean;
    gdrive_folder_id: string | null;
    has_cloudinary: boolean;
  }>("/me"),

  photos: () => request<{ photos: string[] }>("/api/photos"),

  gdriveConnect: () => request<{ status: string }>("/settings/gdrive/connect", { method: "POST" }),

  gdriveDisconnect: () => request<{ status: string }>("/settings/gdrive/disconnect", { method: "DELETE" }),

  gdriveSetFolder: (folder_id: string) =>
    request<{ gdrive_folder_id: string }>("/settings/gdrive", {
      method: "PUT",
      body: JSON.stringify({ folder_id }),
    }),

  cloudinaryGet: () =>
    request<{ has_custom_credentials: boolean; cloud_name: string | null }>("/settings/cloudinary"),

  cloudinarySet: (cloud_name: string, api_key: string, api_secret: string) =>
    request<{ status: string }>("/settings/cloudinary", {
      method: "PUT",
      body: JSON.stringify({ cloud_name, api_key, api_secret }),
    }),

  cloudinaryRemove: () => request<{ status: string }>("/settings/cloudinary", { method: "DELETE" }),

  waitlistCount: () => request<{ count: number; remaining: number }>("/api/waitlist/count"),

  waitlistJoin: (google_email: string) =>
    request<{ position: number; in_beta: boolean }>("/api/waitlist", {
      method: "POST",
      body: JSON.stringify({ google_email }),
    }),
};
