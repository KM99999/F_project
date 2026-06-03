// Data-service layer for receipts — now backed by the real API (Fase 2).
// Function signatures and returned shapes match what the screens already consume.

import { API_URL, getToken } from "./client.js";

function authHeaders(extra = {}) {
  const headers = { ...extra };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function asError(res) {
  let detail = "Error de servidor.";
  try {
    detail = (await res.json()).detail ?? detail;
  } catch {
    /* no JSON body */
  }
  const err = new Error(detail);
  err.status = res.status;
  return err;
}

// GET /recibos — paginated list with filters.
export async function fetchRecibos({ estado = "", desde = "", hasta = "", page = 1, pageSize = 10 } = {}) {
  const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) });
  if (estado) params.set("estado", estado);
  if (desde) params.set("desde", desde);
  if (hasta) params.set("hasta", hasta);

  const res = await fetch(`${API_URL}/recibos?${params.toString()}`, { headers: authHeaders() });
  if (!res.ok) throw await asError(res);
  return res.json();
}

// GET /recibos/{id}
export async function fetchRecibo(id) {
  const res = await fetch(`${API_URL}/recibos/${id}`, { headers: authHeaders() });
  if (!res.ok) throw await asError(res);
  return res.json();
}

// POST /recibos — verificación: recibo + carnet (ambos obligatorios).
// Uses XHR for real upload progress.
export function uploadVerificacion(reciboFile, carnetFile, onProgress) {
  return new Promise((resolve, reject) => {
    const form = new FormData();
    form.append("recibo", reciboFile);
    form.append("carnet", carnetFile);

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/recibos`);
    const token = getToken();
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        // Upload is ~half the perceived work; extraction (server-side) is the rest.
        const pct = Math.round((e.loaded / e.total) * 50);
        onProgress?.({ pct, label: "Subiendo archivo…" });
      }
    };
    // Once the body is sent, the server is classifying + extracting.
    xhr.upload.onload = () => onProgress?.({ pct: 70, label: "Extrayendo datos…" });

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        onProgress?.({ pct: 100, label: "Listo" });
        resolve(JSON.parse(xhr.responseText));
      } else {
        let detail = "No se pudo procesar el recibo.";
        try {
          detail = JSON.parse(xhr.responseText).detail ?? detail;
        } catch {
          /* ignore */
        }
        const err = new Error(detail);
        err.status = xhr.status;
        reject(err);
      }
    };
    xhr.onerror = () => reject(new Error("Error de red al subir el recibo."));
    xhr.send(form);
  });
}

// POST /recibos/{id}/revision — approve/reject (implemented in Fase 3).
export async function reviewRecibo(id, decision) {
  const res = await fetch(`${API_URL}/recibos/${id}/revision`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ decision }),
  });
  if (!res.ok) throw await asError(res);
  return res.json();
}
