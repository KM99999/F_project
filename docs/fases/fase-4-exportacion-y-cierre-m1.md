# Fase 4 — Exportación y cierre de M1

> **Demo al final de la fase:** el cliente exporta todos los recibos a un Excel
> con tipos correctos (fecha, monto, hyperlink) y una hoja resumen, sobre el
> **sistema ya desplegado en producción**. Se firma el acta de M1.

## Objetivo

Cerrar el Milestone 1: exportación a Excel, endurecimiento operacional y puesta
en producción, dejando el sistema listo para uso real.

## Alcance / checklist

### Exportación a Excel
- [ ] `GET /export.xlsx`.
- [ ] Columnas: fecha, cliente, monto, concepto, emisor, estado, score, link a
      imagen.
- [ ] Tipos de celda correctos: fecha como `datetime`, monto como número con
      formato de moneda, link como **hyperlink clickeable**.
- [ ] **Hoja resumen** con totales por estado (valor agregado a bajo costo).
- [ ] Implementado con `openpyxl`.

### Producción y operación
- [ ] Despliegue en VPS (Hetzner o DigitalOcean) vía Docker + docker-compose.
- [ ] Nginx + HTTPS (Let's Encrypt) verificados en producción.
- [ ] Almacenamiento de imágenes en bucket S3-compatible (R2 u otro).
- [ ] **Backups automáticos diarios** de PostgreSQL, retención mínima 30 días.
- [ ] Log estructurado de cada decisión activo (insumo para M2 y auditoría).
- [ ] Verificación final de seguridad (§6.2): cifrado, secretos fuera del código,
      acceso restringido.

### Cierre
- [ ] Validación de aceptación M1 con el cliente.
- [ ] Acta de M1 firmada → pago liberado.

## Requisitos relevantes del documento original

- **Exportación a Excel** (§5.7), **API** (§5.5): `GET /export.xlsx`.
- **No funcionales** (§6.1 precisión, §6.2 seguridad, §6.3 operacional).
- **Criterios de aceptación M1** (§8): sistema operativo procesando recibos
  reales con **≥ 85% de precisión** en extracción de los campos clave sobre el
  set de muestras representativas acordado.

## Criterios de "listo" (= aceptación M1)

- Sistema operativo en producción procesando recibos reales.
- Precisión ≥ 85% en extracción de los 4 campos clave sobre el ground truth.
- Export Excel con tipos correctos y hoja resumen funcionando.
- Backups diarios activos y verificados.
- Acta M1 firmada.

## Transición a la fase intermedia

Tras el cierre de M1 comienza la **fase intermedia (3-4 semanas)** de uso real:

- El cliente procesa sus recibos reales.
- El log estructurado **acumula los datos** que calibran M2 — no es tiempo
  muerto, es el insumo principal de la Fase 5.
- Reuniones semanales documentando casos reales.
- **Riesgo a vigilar:** si el volumen real es bajo, la calibración de M2 queda
  con poca señal → alerta temprana en las reuniones semanales.
