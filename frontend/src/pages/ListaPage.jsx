import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";

import { exportExcel, fetchRecibos } from "../api/recibos.js";
import EstadoBadge from "../components/EstadoBadge.jsx";

const ESTADOS = [
  { value: "", label: "Todos los estados" },
  { value: "unico", label: "Único" },
  { value: "posible_duplicado", label: "Posible duplicado" },
  { value: "duplicado_confirmado", label: "Duplicado confirmado" },
];

// Date object -> "YYYY-MM-DD" (local), for the API.
function toISO(d) {
  if (!d) return "";
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function formatFecha(iso) {
  if (!iso) return "—";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
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
  const [desdeDate, setDesdeDate] = useState(null);
  const [hastaDate, setHastaDate] = useState(null);
  const [campoFecha, setCampoFecha] = useState("servicio"); // servicio | procesamiento
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);

  const desde = toISO(desdeDate);
  const hasta = toISO(hastaDate);

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetchRecibos({ estado, desde, hasta, campoFecha, page }).then((res) => {
      if (active) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, [estado, desde, hasta, campoFecha, page]);

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
          Buscar por
          <select
            value={campoFecha}
            onChange={(e) => {
              setPage(1);
              setCampoFecha(e.target.value);
            }}
          >
            <option value="servicio">Fecha del servicio</option>
            <option value="procesamiento">Fecha de procesamiento</option>
          </select>
        </label>
        <label>
          Desde
          <DatePicker
            selected={desdeDate}
            onChange={(d) => {
              setPage(1);
              setDesdeDate(d);
            }}
            dateFormat="dd/MM/yyyy"
            placeholderText="DD/MM/AAAA"
            isClearable
            className="datepicker-input"
          />
        </label>
        <label>
          Hasta
          <DatePicker
            selected={hastaDate}
            onChange={(d) => {
              setPage(1);
              setHastaDate(d);
            }}
            dateFormat="dd/MM/yyyy"
            placeholderText="DD/MM/AAAA"
            isClearable
            minDate={desdeDate ?? undefined}
            className="datepicker-input"
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
              <th>Código</th>
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
                <td>
                  {r.cliente_original}
                  {r.alerta_nombre && (
                    <span className="flag" title="El nombre del recibo no coincide con el del carnet">
                      🚩
                    </span>
                  )}
                </td>
                <td>{r.carnet_codigo ?? "—"}</td>
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
