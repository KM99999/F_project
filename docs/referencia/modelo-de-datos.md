# Modelo de datos

> Referencia transversal. Fuente: §7 del documento original.

## Tabla `recibos`
- `id` (PK)
- `tipo_documento` (`pdf_estructurado` | `foto_impreso` | `foto_manuscrito`)
- `imagen_url` (referencia al bucket)
- `fecha_extraida` (DATE, normalizada ISO 8601)
- `monto` (DECIMAL)
- `moneda` (VARCHAR)
- `cliente` (VARCHAR, normalizado)
- `cliente_original` (VARCHAR)
- `emisor` (VARCHAR, normalizado)
- `emisor_original` (VARCHAR)
- `concepto` (TEXT, normalizado)
- `forma_pago` (VARCHAR)
- `clave_compuesta_hash` (VARCHAR, indexado)
- `phash` (VARCHAR, indexado)
- `estado` (`unico` | `posible_duplicado` | `duplicado_confirmado`)
- `score` (INT, 0-100)
- `confianza_por_campo` (JSON, para manuscritos)
- `created_at`, `updated_at`

## Tabla `decisiones_log` (auditoría)
- `id`, `recibo_id`, `decision`, `justificacion_legible`,
  `senales_contribuyentes` (JSON), `casos_similares` (JSON),
  `revisor_id` (NULL si automática), `timestamp`

## Tabla `usuarios`
- `id`, `email`, `password_hash`, `rol`, `created_at`

## Tabla `firmas_embeddings` (M2)
- `id`, `recibo_id`, `embedding` (VECTOR), `created_at`

## Uso por fase

| Tabla | Se introduce en |
|---|---|
| `usuarios` | [Fase 0](../fases/fase-0-fundaciones-y-auth.md) |
| `recibos` (campos de extracción) | [Fase 2](../fases/fase-2-pipeline-extraccion.md) |
| `recibos` (hashes, estado, score) | [Fase 3](../fases/fase-3-motor-deteccion.md) |
| `decisiones_log` | [Fase 3](../fases/fase-3-motor-deteccion.md) (registro) / [Fase 5](../fases/fase-5-milestone-2.md) (auditoría legible) |
| `firmas_embeddings` | [Fase 5](../fases/fase-5-milestone-2.md) |
