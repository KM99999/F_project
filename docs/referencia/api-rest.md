# API REST

> Referencia transversal. Fuente: §5.5 del documento original.

| Método | Endpoint | Función | Fase |
|---|---|---|---|
| POST | `/recibos` | Subir recibo y ejecutar pipeline completo | [2](../fases/fase-2-pipeline-extraccion.md) (extracción) → [3](../fases/fase-3-motor-deteccion.md) (pipeline completo) |
| GET | `/recibos` | Lista paginada con filtros (estado, fecha, cliente) | [2](../fases/fase-2-pipeline-extraccion.md) |
| GET | `/recibos/{id}` | Detalle: imagen, datos extraídos, casos similares | [2](../fases/fase-2-pipeline-extraccion.md) / [3](../fases/fase-3-motor-deteccion.md) (similares) |
| POST | `/recibos/{id}/revision` | Aprobar o rechazar un caso de baja confianza | [3](../fases/fase-3-motor-deteccion.md) |
| GET | `/export.xlsx` | Exportar a Excel con tipos correctos | [4](../fases/fase-4-exportacion-y-cierre-m1.md) |

> **Principio (§5.5):** mantener la API **estrecha** en M1. Solo agregar
> endpoints si son estrictamente necesarios.

> La autenticación (login, protección de rutas) se introduce en la
> [Fase 0](../fases/fase-0-fundaciones-y-auth.md). Todos los endpoints anteriores
> viven detrás de auth.
