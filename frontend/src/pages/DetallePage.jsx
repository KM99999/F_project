import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { mediaUrl } from "../api/client.js";
import { fetchRecibo, reviewRecibo } from "../api/recibos.js";
import EstadoBadge from "../components/EstadoBadge.jsx";

const TIPO_LABELS = {
  pdf_estructurado: "PDF estructurado",
  foto_impreso: "Foto (impreso)",
  foto_manuscrito: "Foto (manuscrito)",
};

function formatFecha(iso) {
  if (!iso) return "—";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
  return m ? `${m[3]}/${m[2]}/${m[1]}` : iso;
}

function formatMonto(monto, moneda) {
  if (monto == null) return "—";
  const n = Number(monto);
  if (Number.isNaN(n)) return String(monto);
  const formatted = n.toLocaleString("es-AR", { minimumFractionDigits: 2 });
  return moneda ? `${moneda} ${formatted}` : formatted;
}

function Campo({ label, value, confianza }) {
  return (
    <div className="campo">
      <span className="campo-label">{label}</span>
      <span className="campo-value">
        {value || <span className="muted">—</span>}
        {confianza && <span className={`conf conf--${confianza}`}>confianza {confianza}</span>}
      </span>
    </div>
  );
}

export default function DetallePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [recibo, setRecibo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    fetchRecibo(id)
      .then((r) => active && setRecibo(r))
      .catch((e) => active && setError(e.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [id]);

  async function handleReview(decision) {
    setSubmitting(true);
    try {
      const updated = await reviewRecibo(id, decision);
      setRecibo((r) => ({ ...r, estado: updated.estado }));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <p className="muted">Cargando…</p>;
  if (error) return <p className="error">{error}</p>;

  const conf = recibo.confianza_por_campo ?? {};
  const esRevisable = recibo.estado === "posible_duplicado";

  return (
    <section className="page">
      <div className="page-head">
        <Link to="/recibos" className="back-link">
          ← Volver a la lista
        </Link>
        <EstadoBadge estado={recibo.estado} />
      </div>

      <h2>Recibo #{recibo.id}</h2>

      <div className="detalle-grid">
        {/* Imagen original (placeholder en Fase 1) */}
        <div className="detalle-imagen">
          {recibo.imagen_url ? (
            <a href={mediaUrl(recibo.imagen_url)} target="_blank" rel="noreferrer">
              <img className="doc-img" src={mediaUrl(recibo.imagen_url)} alt="Recibo" />
            </a>
          ) : (
            <div className="imagen-placeholder">
              <span>📄</span>
              <p className="muted">Imagen original del recibo</p>
            </div>
          )}
          <p className="muted small" style={{ marginTop: "0.5rem" }}>
            {TIPO_LABELS[recibo.tipo_documento] ?? recibo.tipo_documento}
          </p>
        </div>

        {/* Datos extraídos */}
        <div className="detalle-datos">
          <h3>Datos extraídos</h3>
          <Campo label="Fecha" value={formatFecha(recibo.fecha)} confianza={conf.fecha} />
          <Campo label="Monto" value={formatMonto(recibo.monto, recibo.moneda)} confianza={conf.monto} />
          <Campo label="Cliente" value={recibo.cliente_original} confianza={conf.cliente} />
          <Campo label="Emisor" value={recibo.emisor_original} confianza={conf.emisor} />
          <Campo label="Concepto" value={recibo.concepto} />
          <Campo label="Forma de pago" value={recibo.forma_pago} />
          <Campo label="Score de coincidencia" value={String(recibo.score)} />
        </div>
      </div>

      {/* Carnet del cliente (misma verificación) */}
      <div className="carnet">
        <h3>Carnet del cliente</h3>
        <Campo label="Código" value={recibo.carnet_codigo} />
        <Campo label="Nombre" value={recibo.carnet_nombre} />
        <Campo label="Fecha de nacimiento" value={recibo.carnet_fecha_nac} />
        {recibo.carnet_imagen_url && (
          <a href={mediaUrl(recibo.carnet_imagen_url)} target="_blank" rel="noreferrer">
            <img className="doc-img" src={mediaUrl(recibo.carnet_imagen_url)} alt="Carnet" style={{ marginTop: "0.75rem" }} />
          </a>
        )}
      </div>

      {/* Casos similares */}
      {recibo.similares.length > 0 && (
        <div className="similares">
          <h3>Casos similares</h3>
          {recibo.similares.map((s) => (
            <div key={s.id} className="similar">
              <Link to={`/recibos/${s.id}`}>Recibo #{s.id}</Link>
              <span className="similar-score">score {s.score}</span>
              <span className="muted">{s.motivo}</span>
            </div>
          ))}
        </div>
      )}

      {/* Revisión humana — solo para posible_duplicado */}
      {esRevisable && (
        <div className="revision">
          <h3>Revisión humana</h3>
          <p className="muted">
            Este caso quedó en zona gris. Confirmá si es un duplicado o márcalo como único.
          </p>
          <div className="revision-actions">
            <button className="btn-danger" disabled={submitting} onClick={() => handleReview("aprobar")}>
              Confirmar duplicado
            </button>
            <button className="btn-ghost" disabled={submitting} onClick={() => handleReview("rechazar")}>
              Marcar como único
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
