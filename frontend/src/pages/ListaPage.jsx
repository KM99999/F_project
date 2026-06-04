import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { exportExcel, fetchRecibos } from "../api/recibos.js";
import EstadoBadge from "../components/EstadoBadge.jsx";

const ESTADOS = [
  { value: "", label: "Todos los estados" },
  { value: "unico", label: "Único" },
  { value: "posible_duplicado", label: "Posible duplicado" },
  { value: "duplicado_confirmado", label: "Duplicado confirmado" },
];

function formatFecha(iso) {
  if (!iso) return "—";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
}

// "27/04/2026" -> "2026-04-27"; "" if not a complete valid date (so the filter
// only applies once the user finishes typing a full date).
function parseToISO(text) {
  if (!text) return "";
  const m = /^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$/.exec(text.trim());
  if (!m) return "";
  const d = m[1].padStart(2, "0");
  const mo = m[2].padStart(2, "0");
  if (+mo < 1 || +mo > 12 || +d < 1 || +d > 31) return "";
  return `${m[3]}-${mo}-${d}`;
}

// created_at is an ISO datetime; show only the date as DD/MM/AAAA (local).
function formatFechaProceso(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  const p = (n) => String(n).padStart(2, "0");
  return `${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()}`;
}

function formatMonto(monto, moneda) {
  if (monto == null) return "—";
  const n = Number(monto);
  if (Number.isNaN(n)) return String(monto);
  const formatted = n.toLocaleString("es-AR", { minimumFractionDigits: 2 });
  return moneda ? `${moneda} ${formatted}` : formatted;
}

export default function ListaPage() {
  const navigate = useNavigate();
  const [estado, setEstado] = useState("");
  const [desdeText, setDesdeText] = useState("");
  const [hastaText, setHastaText] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  // Date filters are typed as DD/MM/AAAA but sent to the API as ISO.
  const desde = parseToISO(desdeText);
  const hasta = parseToISO(hastaText);

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetchRecibos({ estado, desde, hasta, page }).then((res) => {
      if (active) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, [estado, desde, hasta, page]);

  async function handleExport() {
    setExporting(true);
    try {
      const blob = await exportExcel();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "recibos.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message || "No se pudo exportar.");
    } finally {
      setExporting(false);
    }
  }

  return (
    <section className="page">
      <div className="page-head">
        <h2>Recibos</h2>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button className="btn-ghost" onClick={handleExport} disabled={exporting}>
            {exporting ? "Exportando…" : "Exportar a Excel"}
          </button>
          <button onClick={() => navigate("/carga")}>+ Nueva verificación</button>
        </div>
      </div>

      <div className="filters">
        <label>
          Estado
          <select
            value={estado}
            onChange={(e) => {
              setPage(1);
              setEstado(e.target.value);
            }}
          >
            {ESTADOS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Desde
          <input
            type="text"
            inputMode="numeric"
            placeholder="DD/MM/AAAA"
            value={desdeText}
            onChange={(e) => {
              setPage(1);
              setDesdeText(e.target.value);
            }}
          />
        </label>
        <label>
          Hasta
          <input
            type="text"
            inputMode="numeric"
            placeholder="DD/MM/AAAA"
            value={hastaText}
            onChange={(e) => {
              setPage(1);
              setHastaText(e.target.value);
            }}
          />
        </label>
      </div>

      {loading ? (
        <p className="muted">Cargando…</p>
      ) : data.items.length === 0 ? (
        <p className="muted">No hay recibos para los filtros seleccionados.</p>
      ) : (
        <table className="table">
          <thead>
            <tr>
              <th>Fecha servicio</th>
              <th>Fecha proceso</th>
              <th>Cliente</th>
              <th>Emisor</th>
              <th className="right">Monto</th>
              <th>Concepto</th>
              <th>Estado</th>
              <th className="right">Score</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((r) => (
              <tr key={r.id} onClick={() => navigate(`/recibos/${r.id}`)} className="row-link">
                <td>{formatFecha(r.fecha)}</td>
                <td>{formatFechaProceso(r.created_at)}</td>
                <td>{r.cliente_original}</td>
                <td>{r.emisor_original}</td>
                <td className="right">{formatMonto(r.monto, r.moneda)}</td>
                <td>{r.concepto}</td>
                <td>
                  <EstadoBadge estado={r.estado} />
                </td>
                <td className="right">{r.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {data && data.totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Anterior
          </button>
          <span className="muted">
            Página {data.page} de {data.totalPages} ({data.total} recibos)
          </span>
          <button disabled={page >= data.totalPages} onClick={() => setPage((p) => p + 1)}>
            Siguiente
          </button>
        </div>
      )}
    </section>
  );
}
