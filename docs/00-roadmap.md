# Roadmap de desarrollo — demoable-first

Plan de construcción ordenado para que **cada fase termine en algo que se le
puede mostrar al cliente**. Deriva del cronograma original (§11) y de la
estructura de milestones (§4), pero reordena las tareas para priorizar lo visible.

## Filosofía de orden

El documento original describe el sistema por capas técnicas (pipeline →
detección → UI). Para el desarrollo invertimos parcialmente ese orden:

1. **Primero el cascarón visible** (auth + pantallas con datos mock). El cliente
   ve y navega el producto en la primera semana.
2. **Después rellenamos el motor** (extracción, detección) detrás de pantallas
   que ya existen. Cada capa nueva "enciende" una pantalla que antes era mock.
3. **Al final, exportación y endurecimiento** para el cierre de M1.

Ventaja: demos tempranas, validación continua del cliente y descubrimiento
temprano de malentendidos sobre el flujo.

## Secuencia de fases

### Milestone 1 — Sistema base funcional (4 semanas, USD 1.400)

| Fase | Foco | Demo al final de la fase |
|---|---|---|
| [Fase 0](fases/fase-0-fundaciones-y-auth.md) | Infra + autenticación | Login real; tras entrar, área protegida vacía |
| [Fase 1](fases/fase-1-pantallas-ui.md) | Las 3 pantallas con datos mock | Cliente navega carga → lista → detalle completo |
| [Fase 2](fases/fase-2-pipeline-extraccion.md) | Clasificación + extracción + normalización | Sube un recibo real y ve los 6 campos extraídos |
| [Fase 3](fases/fase-3-motor-deteccion.md) | Match exacto + pHash + score + estados | Sube un duplicado y el sistema lo marca en color |
| [Fase 4](fases/fase-4-exportacion-y-cierre-m1.md) | Excel + producción + aceptación | Exporta a Excel; sistema desplegado en VPS |

### Fase intermedia — Uso real (3-4 semanas)

El cliente procesa recibos reales. No es tiempo muerto: el log estructurado
acumula los datos que calibran M2. Reuniones semanales documentando casos.

### Milestone 2 — Refinamiento y automatización (2 semanas, USD 700)

| Fase | Foco |
|---|---|
| [Fase 5](fases/fase-5-milestone-2.md) | Calibración con datos reales, auditoría, reportes, capa visual avanzada, automatización, notificaciones |

## Cronograma verificable (§11 original)

| Momento | Hito | Fase asociada |
|---|---|---|
| Fin de Fase 0 (negocio) | NDA firmado, 30-50 muestras etiquetadas, definición de precisión acordada | Pre-requisito de Fase 2 |
| Fin de Semana 1 | Clasificador funcional, pipeline PDFs estructurados con medición preliminar | Fase 0 + arranque Fase 2 |
| Fin de Semana 2 | Pipeline completo con ≥ 85% sobre ground truth | Fase 2 |
| Fin de Semana 3 | UI funcional con 3 pantallas, exportación a Excel con tipos correctos | Fases 1, 3 y 4 |
| Fin de Semana 4 | Sistema en producción, acta M1 firmada, pago liberado | Fase 4 |
| Fase intermedia | Log acumulando datos, reuniones semanales documentando casos | — |
| Fin de Semana 5 | Umbrales calibrados con datos reales, detección visual avanzada operativa o decidida | Fase 5 |
| Fin de Semana 6 | Automatización activa, reportes mensuales, documentación entregada, acta M2 firmada | Fase 5 |

> **Nota sobre validación intermedia:** el riesgo #1 (precisión < 85%) se mitiga
> con una validación obligatoria al final de Semana 2 (Fase 2), **antes** de
> construir el motor de duplicados (Fase 3). Ver [riesgos](referencia/glosario-y-riesgos.md).

## Dependencias entre fases

```
Fase 0 (auth + infra)
   └─> Fase 1 (UI mock)  ──────────────┐
   └─> Fase 2 (extracción) ─> Fase 3 (detección) ─> Fase 4 (export + cierre)
                                                          │
                                          [uso real] ─────┘─> Fase 5 (M2)
```

- Fase 1 y Fase 2 pueden avanzar en paralelo tras Fase 0 (una es frontend, otra
  backend). La UI mock de Fase 1 se "conecta" a datos reales al terminar Fase 2.
- Fase 3 depende de que la extracción y persistencia (Fase 2) ya funcionen.
- Fase 5 depende de datos reales acumulados durante la fase intermedia.
