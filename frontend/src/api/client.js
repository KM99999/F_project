// Thin fetch wrapper around the backend API.
// Reads the token from localStorage and attaches it as a Bearer header.

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const TOKEN_KEY = "recibos_token";

// Build a URL for an uploaded media file. /media is served at the site root
// (not under /api), so strip a trailing "/api" from the API base.
export function mediaUrl(path) {
  if (!path) return null;
  if (!path.startsWith("/")) return path;
  return `${API_URL.replace(/\/api$/, "")}${path}`;
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = "Error de servidor.";
    try {
      const data = await res.json();
      detail = data.detail ?? detail;
    } catch {
      // response had no JSON body
    }
    const error = new Error(detail);
    error.status = res.status;
    throw error;
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  login: (usuario, password) =>
    request("/auth/login", { method: "POST", body: { usuario, password }, auth: false }),
  me: () => request("/auth/me"),
};
