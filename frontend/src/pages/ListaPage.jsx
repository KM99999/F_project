import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { fetchRecibos } from "../api/recibos.js";
import EstadoBadge from "../components/EstadoBadge.jsx";

const ESTADOS = [
  { value: "", label: "Todos los estados" },
  { value: "unico", label: "Único" },
  { value: "posible_duplicado", label: "Posible duplicado" },
  { value: "duplicado_confirmado", label: "Duplicado confirmado" },
];

function formatMonto(monto, moneda) {
  if (monto == null) return "—";
  const n = Number(monto);
  if (Number.isNaN(n)) return String(monto);
  const formatted = n.toLocaleString("es-AR", { minimumFractionDigits: 2 });
  return moneda ? `${moneda} ${formatted}` : formatted;
}

export default function ListaPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState({ estado: "", desde: "", hasta: "" });
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetchRecibos({ ...filters, page }).then((res) => {
      if (active) {
        setData(res);
        setLoading(false);
      }
    });
    return () => {
      active = false;
    };
  }, [filters, page]);

  function updateFilter(key, value) {
    setPage(1);
    setFilters((f) => ({ ...f, [key]: value }));
  }

  return (
    <section className="page">
      <div className="page-head">
        <h2>Recibos</h2>
        <button onClick={() => navigate("/carga")}>+ Cargar recibo</button>
      </div>

      <div className="filters">
        <label>
          Estado
          <select value={filters.estado} onChange={(e) => updateFilter("estado", e.target.value)}>
            {ESTADOS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Desde
          <input type="date" value={filters.desde} onChange={(e) => updateFilter("desde", e.target.value)} />
        </label>
        <label>
          Hasta
          <input type="date" value={filters.hasta} onChange={(e) => updateFilter("hasta", e.target.value)} />
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
              <th>Fecha</th>
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
                <td>{r.fecha}</td>
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
