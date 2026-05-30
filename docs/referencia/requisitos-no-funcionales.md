# Requisitos no funcionales

> Referencia transversal. Fuente: §6 del documento original.

## 6.1 Precisión
- **M1:** ≥ 85% de precisión global en extracción de los 4 campos clave (fecha,
  monto, cliente, emisor) sobre el ground truth acordado.
- **M2:** mantener o mejorar precisión respecto a M1, mientras se reduce el
  volumen de revisión manual.

## 6.2 Seguridad
- NDA firmado antes de recibir muestras reales.
- Acceso a datos restringido al desarrollador.
- Almacenamiento cifrado.
- Borrado de muestras al final del proyecto si el cliente lo prefiere.
- HTTPS obligatorio (sistema maneja datos financieros).
- Variables de entorno para secretos. Nunca en código. `.env` fuera del
  repositorio.

## 6.3 Operacional
- Backups automáticos diarios de PostgreSQL, retención mínima 30 días.
- Log estructurado de cada decisión del sistema (insumo crítico para M2 y
  auditoría).
- Reintentos con backoff exponencial para fallos de red en la API de Claude.
- Timeout 60 segundos por recibo.

## Dónde se aplican

| Requisito | Fase principal |
|---|---|
| HTTPS, secretos, acceso restringido | [Fase 0](../fases/fase-0-fundaciones-y-auth.md) |
| Precisión ≥ 85% | [Fase 2](../fases/fase-2-pipeline-extraccion.md) |
| Reintentos, timeout, log | [Fase 2](../fases/fase-2-pipeline-extraccion.md) |
| Backups, cifrado en producción | [Fase 4](../fases/fase-4-exportacion-y-cierre-m1.md) |
