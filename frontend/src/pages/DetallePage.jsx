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

// Processing date/time (created_at) as DD/MM/AAAA HH:MM (local).
function formatFechaHora(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return String(value);
  const p = (n) => String(n).padStart(2, "0");
  return `${p(d.getDate())}/${p(d.getMonth() + 1)}/${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}`;
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

// Muestra el documento subido: PDF en visor embebido, imagen en <img>, y si la
// imagen no se puede previsualizar (p. ej. HEIC viejo), un enlace de respaldo.
function DocView({ url, label }) {
  const [imgError, setImgError] = useState(false);
  if (!url) {
    return (
      <div className="imagen-placeholder">
        <span>📄</span>
        <p className="muted">Sin {label.toLowerCase()}</p>
      </div>
    );
  }
  const full = mediaUrl(url);
  const isPdf = /\.pdf(\?|$)/i.test(url);

  if (isPdf) {
    return (
      <div>
        <iframe src={full} title={label} className="doc-frame" />
        <p className="small" style={{ marginTop: "0.5rem" }}>
          <a href={full} target="_blank" rel="noreferrer">
            Abrir {label} (PDF) en una pestaña
          </a>
        </p>
      </div>
    );
  }
  if (imgError) {
    return (
      <a href={full} target="_blank" rel="noreferrer">
        Ver {label} (no se pudo previsualizar)
      </a>
    );
  }
  return (
    <a href={full} target="_blank" rel="noreferrer">
      <img className="doc-img" src={full} alt={label} onError={() => setImgError(true)} />
    </a>
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
      <p className="muted small">Procesado en el sistema: {formatFechaHora(recibo.created_at)}</p>

      {recibo.alerta_nombre && (
        <div className="alerta-nombre">
          🚩 <strong>Atención:</strong> el nombre del recibo (<em>{recibo.cliente_original || "—"}</em>) no
          coincide con el del carnet (<em>{recibo.carnet_nombre || "—"}</em>). Verificá manualmente — puede
          ser un error de escritura o un carnet equivocado.
        </div>
      )}

      <div className="detalle-grid">
        {/* Imagen original (placeholder en Fase 1) */}
        <div className="detalle-imagen">
          <DocView url={recibo.imagen_url} label="Recibo" />
          <p className="muted small" style={{ marginTop: "0.5rem" }}>
            {TIPO_LABELS[recibo.tipo_documento] ?? recibo.tipo_documento}
          </p>
        </div>

        {/* Datos extraídos */}
        <div className="detalle-datos">
          <h3>Datos extraídos</h3>
          <Campo label="Fecha del servicio" value={formatFecha(recibo.fecha)} confianza={conf.fecha} />
          <Campo label="Fecha de procesamiento" value={formatFechaHora(recibo.created_at)} />
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
        <div style={{ marginTop: "0.75rem" }}>
          <DocView url={recibo.carnet_imagen_url} label="Carnet" />
        </div>
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
