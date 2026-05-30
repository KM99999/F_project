# Glosario y riesgos

> Referencia transversal. Fuente: §12 y §13 del documento original.

## Glosario (§12)

- **Ground truth:** conjunto de 30-50 recibos etiquetados manualmente con los
  valores correctos de los 6 campos. Es la referencia contra la que se mide la
  precisión.
- **pHash (perceptual hash):** hash robusto a recortes leves, cambios de brillo y
  compresión JPEG, usado para detectar imágenes visualmente similares.
- **Distancia de Hamming:** número de bits que difieren entre dos hashes. Valores
  bajos = imágenes muy similares.
- **Match exacto:** coincidencia de los 4 campos clave normalizados
  (emisor + fecha + monto + cliente).
- **Score:** valor 0-100 que combina match exacto y similitud visual.
- **Revisión humana:** flujo donde un operador del cliente aprueba o rechaza un
  caso clasificado como `posible_duplicado`.
- **Auditoría:** log con la justificación legible de cada decisión del sistema,
  accesible desde la UI.
- **Falso positivo:** recibo marcado como duplicado que en realidad es único.
- **Falso negativo:** duplicado real que el sistema dejó pasar como único.

## Riesgos identificados (§13)

| Riesgo | Mitigación |
|---|---|
| Precisión < 85% en validación de M1 | Validación intermedia obligatoria al final de Semana 2, antes de construir el motor de duplicados ([Fase 2](../fases/fase-2-pipeline-extraccion.md) → [Fase 3](../fases/fase-3-motor-deteccion.md)) |
| Volumen de uso real bajo en fase intermedia | Reuniones semanales con cliente para monitorear; alerta temprana si la calibración de M2 queda con poca señal |
| Capa visual avanzada excede tiempo | Decisión en fin de Semana 5: priorizar bien una capa antes que dos mediocres ([Fase 5](../fases/fase-5-milestone-2.md)) |
| Variaciones legítimas marcadas como duplicado | Zona gris conservadora; revisión humana siempre disponible |
| Costo de API escala más rápido que estimado | Monitoreo del costo real desde Semana 1; reportar al cliente si supera estimaciones |
