import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { uploadVerificacion } from "../api/recibos.js";

const ACCEPT = ".pdf,.jpg,.jpeg,.png,.webp,.heic";

// One drop/select zone for a single document.
function DocZone({ label, hint, file, onPick, disabled }) {
  const inputRef = useRef(null);
  const [over, setOver] = useState(false);

  function pick(f) {
    if (f) onPick(f);
  }

  return (
    <div
      className={`dropzone ${over ? "dropzone--over" : ""} ${file ? "dropzone--filled" : ""}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setOver(false);
        if (!disabled) pick(e.dataTransfer.files?.[0]);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        capture="environment"
        hidden
        onChange={(e) => pick(e.target.files?.[0])}
      />
      <strong>{label}</strong>
      {file ? (
        <p className="ok small">✓ {file.name}</p>
      ) : (
        <p className="muted small">{hint}</p>
      )}
    </div>
  );
}

export default function CargaPage() {
  const navigate = useNavigate();
  const [recibo, setRecibo] = useState(null);
  const [carnet, setCarnet] = useState(null);
  const [progress, setProgress] = useState(null); // { pct, label }
  const [done, setDone] = useState(null);
  const [error, setError] = useState("");

  const busy = progress !== null;

  async function procesar() {
    if (!recibo || !carnet) return;
    setError("");
    setDone(null);
    setProgress({ pct: 0, label: "Preparando…" });
    try {
      const nuevo = await uploadVerificacion(recibo, carnet, (step) => setProgress(step));
      setDone(nuevo);
    } catch (err) {
      setError(err.message || "No se pudo procesar la verificación.");
    } finally {
      setProgress(null);
    }
  }

  function reset() {
    setRecibo(null);
    setCarnet(null);
    setDone(null);
    setError("");
  }

  return (
    <section className="page">
      <h2>Nueva verificación</h2>

      {!done && (
        <>
          <p className="muted">
            Subí los <strong>dos documentos</strong> de la solicitud: el recibo y el
            carnet/identidad del cliente. Se procesan en un único resultado.
          </p>

          <div className="doc-grid">
            <DocZone
              label="1) Recibo"
              hint="PDF o foto del recibo"
              file={recibo}
              onPick={setRecibo}
              disabled={busy}
            />
            <DocZone
              label="2) Carnet del cliente"
              hint="Foto o PDF del carnet (con el código)"
              file={carnet}
              onPick={setCarnet}
              disabled={busy}
            />
          </div>

          {busy ? (
            <div className="progress-box">
              <p>{progress.label}</p>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress.pct}%` }} />
              </div>
              <p className="muted small">{progress.pct}%</p>
            </div>
          ) : (
            <button onClick={procesar} disabled={!recibo || !carnet} style={{ marginTop: "1rem" }}>
              Procesar verificación
            </button>
          )}

          {error && !busy && <p className="error" style={{ marginTop: "1rem" }}>{error}</p>}
        </>
      )}

      {done && (
        <div className="upload-done">
          <p className="ok">✓ Verificación procesada: recibo y carnet.</p>
          <div className="upload-actions">
            <button onClick={() => navigate(`/recibos/${done.id}`)}>Ver detalle</button>
            <button className="btn-ghost" onClick={reset}>
              Nueva verificación
            </button>
            <button className="btn-ghost" onClick={() => navigate("/recibos")}>
              Ir a la lista
            </button>
          </div>
        </div>
      )}

      <p className="muted small note">
        El sistema clasifica el recibo y extrae sus 6 campos, y del carnet toma el
        nombre y el código del cliente. La detección de duplicados corre sobre el recibo.
      </p>
    </section>
  );
}
