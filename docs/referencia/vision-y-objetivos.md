# Visión y objetivos

> Referencia transversal. Fuente: §1 y §2 del documento original.

## Visión general (§1)

Sistema web para detectar **recibos de pago duplicados**, incluyendo recibos
manuscritos, fotos de recibos impresos y archivos PDF. El propósito es reducir el
riesgo de **pago doble** por reenvío intencional o accidental del mismo recibo,
con trazabilidad y evidencia auditable de cada decisión del sistema.

- **Volumen estimado:** ~2.000 recibos/mes.
- **Arquitectura conceptual:** extracción por IA con visión → normalización →
  motor multicapa de detección (match exacto + hash perceptual + score) →
  revisión humana para casos de baja confianza → auditoría completa.

## Objetivos del negocio (§2)

- Detectar duplicados **antes** de procesar pagos.
- Generar **evidencia auditable** de cada decisión del sistema.
- Reducir la carga de revisión manual **sin eliminarla por completo**. La revisión
  humana siempre se conserva para casos de baja confianza; eliminarla en un
  sistema con consecuencias financieras es mal diseño.
