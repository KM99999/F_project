import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { uploadRecibo } from "../api/recibos.js";

const ACCEPT = ".pdf,.jpg,.jpeg,.png,.webp,.heic";

export default function CargaPage() {
  const navigate = useNavigate();
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [progress, setProgress] = useState(null); // { pct, label }
  const [done, setDone] = useState(null); // uploaded receipt

  async function handleFile(file) {
    if (!file) return;
    setDone(null);
    setProgress({ pct: 0, label: "Preparando…" });
    const nuevo = await uploadRecibo(file, (step) => setProgress(step));
    setProgress(null);
    setDone(nuevo);
  }

  function onDrop(e) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  const busy = progress !== null;

  return (
    <section className="page">
      <h2>Cargar recibo</h2>

      {!done && (
        <div
          className={`dropzone ${dragOver ? "dropzone--over" : ""}`}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => !busy && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPT}
            capture="environment"
            hidden
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
          {busy ? (
            <div className="progress-box">
              <p>{progress.label}</p>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${progress.pct}%` }} />
              </div>
              <p className="muted small">{progress.pct}%</p>
            </div>
          ) : (
            <>
              <span className="dropzone-icon">⬆️</span>
              <p>
                Arrastrá un recibo aquí, o <strong>hacé clic para elegir</strong>
              </p>
              <p className="muted small">PDF o foto (también desde la cámara del celular)</p>
            </>
          )}
        </div>
      )}

      {done && (
        <div className="upload-done">
          <p className="ok">✓ Recibo procesado: datos extraídos.</p>
          <div className="upload-actions">
            <button onClick={() => navigate(`/recibos/${done.id}`)}>Ver detalle</button>
            <button className="btn-ghost" onClick={() => setDone(null)}>
              Cargar otro
            </button>
            <button className="btn-ghost" onClick={() => navigate("/recibos")}>
              Ir a la lista
            </button>
          </div>
        </div>
      )}

      <p className="muted small note">
        El sistema clasifica el documento y extrae los 6 campos con IA. La
        detección de duplicados (estado y casos similares) se activa en la Fase 3.
      </p>
    </section>
  );
}
