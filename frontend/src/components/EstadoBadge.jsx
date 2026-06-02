// Color-coded badge for a receipt state (estado).
// Green = unico, yellow = posible_duplicado, red = duplicado_confirmado.

const LABELS = {
  unico: "Único",
  posible_duplicado: "Posible duplicado",
  duplicado_confirmado: "Duplicado confirmado",
};

export default function EstadoBadge({ estado }) {
  const label = LABELS[estado] ?? estado;
  return <span className={`badge badge--${estado}`}>{label}</span>;
}
