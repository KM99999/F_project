// Data-service layer for receipts.
//
// Fase 1: serves MOCK data from an in-memory copy so the UI is fully navigable.
// Fase 2/3: replace the bodies of these functions with real calls via api/client.js
// (e.g. request("/recibos"), request(`/recibos/${id}`), ...) — the signatures and
// returned shapes are designed to stay the same so the pages don't change.

import { RECIBOS } from "../mock/recibos.js";

// Mutable session copy so uploads/reviews are reflected while navigating.
let store = RECIBOS.map((r) => ({ ...r }));
let nextId = Math.max(...store.map((r) => r.id)) + 1;

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// GET /recibos — paginated list with filters (estado, date range).
export async function fetchRecibos({ estado = "", desde = "", hasta = "", page = 1, pageSize = 10 } = {}) {
  await delay(250);
  let items = [...store].sort((a, b) => b.created_at.localeCompare(a.created_at));

  if (estado) items = items.filter((r) => r.estado === estado);
  if (desde) items = items.filter((r) => r.fecha >= desde);
  if (hasta) items = items.filter((r) => r.fecha <= hasta);

  const total = items.length;
  const start = (page - 1) * pageSize;
  const pageItems = items.slice(start, start + pageSize);
  return { items: pageItems, total, page, pageSize, totalPages: Math.max(1, Math.ceil(total / pageSize)) };
}

// GET /recibos/{id} — detail, with resolved similar cases.
export async function fetchRecibo(id) {
  await delay(200);
  const recibo = store.find((r) => r.id === Number(id));
  if (!recibo) {
    const err = new Error("Recibo no encontrado.");
    err.status = 404;
    throw err;
  }
  const similares = (recibo.similares ?? []).map((s) => {
    const ref = store.find((r) => r.id === s.id);
    return { ...s, fecha: ref?.fecha, monto: ref?.monto, moneda: ref?.moneda, emisor_original: ref?.emisor_original };
  });
  return { ...recibo, similares };
}

// POST /recibos — simulate the upload + pipeline with progress callbacks.
// In Fase 2 this becomes a real multipart upload that runs the AI pipeline.
export async function uploadRecibo(file, onProgress) {
  const steps = [
    { pct: 25, label: "Subiendo archivo…" },
    { pct: 55, label: "Clasificando documento…" },
    { pct: 80, label: "Extrayendo campos…" },
    { pct: 100, label: "Listo" },
  ];
  for (const step of steps) {
    await delay(500);
    onProgress?.(step);
  }
  // Mock result: a new "unico" receipt so it appears in the list.
  const nuevo = {
    id: nextId++,
    tipo_documento: "foto_impreso",
    imagen_url: null,
    fecha: new Date().toISOString().slice(0, 10),
    monto: "0.00",
    moneda: "ARS",
    cliente: "(pendiente)",
    cliente_original: "(pendiente de extracción)",
    emisor: "(pendiente)",
    emisor_original: file?.name ?? "(archivo subido)",
    concepto: "Extracción simulada (Fase 1)",
    forma_pago: "—",
    estado: "unico",
    score: 0,
    confianza_por_campo: null,
    created_at: new Date().toISOString(),
    similares: [],
  };
  store = [nuevo, ...store];
  return nuevo;
}

// POST /recibos/{id}/revision — approve/reject a low-confidence case.
export async function reviewRecibo(id, decision) {
  await delay(250);
  const recibo = store.find((r) => r.id === Number(id));
  if (!recibo) throw new Error("Recibo no encontrado.");
  // aprobar => confirm duplicate; rechazar => mark as unique.
  recibo.estado = decision === "aprobar" ? "duplicado_confirmado" : "unico";
  return { ...recibo };
}
