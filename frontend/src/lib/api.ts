import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "/api/v1";

export const TOKEN_KEYS = {
  access: "suvyon_access_token",
  refresh: "suvyon_refresh_token",
} as const;

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEYS.access);
}

export function getRefreshToken() {
  return localStorage.getItem(TOKEN_KEYS.refresh);
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEYS.access, access);
  localStorage.setItem(TOKEN_KEYS.refresh, refresh);
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEYS.access);
  localStorage.removeItem(TOKEN_KEYS.refresh);
}

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120_000,
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${API_BASE}/auth/refresh`, {
      refresh_token: refresh,
    });
    setTokens(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    clearTokens();
    return null;
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      refreshing ??= refreshAccessToken().finally(() => {
        refreshing = null;
      });
      const token = await refreshing;
      if (token) {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      }
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

export function getErrorMessage(error: unknown, fallback = "Something went wrong.") {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg || JSON.stringify(d)).join(", ");
    }
    const message = error.message || fallback;
    if (!error.response && /network error/i.test(message)) {
      return (
        "The API did not finish the request (timeout or dropped connection). " +
        "Sending email from the Vercel app uses Render, which blocks Gmail SMTP on the free plan. " +
        "Drafts still work. Set RESEND_API_KEY or SENDGRID_API_KEY on Render, or upgrade the instance."
      );
    }
    return message;
  }
  if (error instanceof Error) return error.message;
  return fallback;
}
