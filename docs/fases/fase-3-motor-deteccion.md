# Fase 3 — Motor de detección de duplicados

> **Demo al final de la fase:** el cliente sube un recibo que ya existe (o una
> foto de una fotocopia) y el sistema lo **marca en amarillo o rojo**, muestra el
> caso similar y habilita aprobar/rechazar. Es el corazón del producto.

## Objetivo

Construir el motor multicapa que asigna estado y score a cada recibo combinando
match exacto, hash perceptual y un score ponderado, y conectar el flujo de
revisión humana.

## Por qué va aquí

- Depende de que la extracción y persistencia (Fase 2) ya funcionen: el motor
  compara contra lo ya almacenado.
- Es lo que cumple el objetivo de negocio principal: **detectar duplicados antes
  de pagar**, con evidencia auditable.

## Alcance / checklist

### Match exacto (determinístico)
- [ ] Clave compuesta normalizada: `emisor + fecha + monto + cliente`.
- [ ] Hash de la clave indexado en PostgreSQL (`clave_compuesta_hash`).
- [ ] Coincidencia → score 100, estado `duplicado_confirmado`.

### Hash perceptual (visual)
- [ ] pHash de la imagen completa (`imagehash`, algoritmo pHash), indexado.
- [ ] Distancia de Hamming contra hashes existentes.
- [ ] Distancia baja → imágenes similares (recortes, filtros, fotos de
      fotocopias).

### Score de coincidencia (0-100)
Combinación ponderada:
- [ ] Match exacto de los 4 campos clave → contribución alta.
- [ ] pHash con distancia baja → contribución media-alta.
- [ ] Match parcial (3 de 4 campos) → contribución media.

### Umbrales y estados
Umbrales **iniciales provisorios** (se calibran en M2 con datos reales):
- [ ] `score < 40` → `unico`
- [ ] `40 <= score <= 75` → `posible_duplicado` (revisión humana)
- [ ] `score > 75` → `duplicado_confirmado`

### Integración
- [ ] `POST /recibos` ahora ejecuta el **pipeline completo**: extracción +
      detección, y guarda `estado`, `score`, hashes.
- [ ] `GET /recibos/{id}` devuelve casos similares para la Pantalla 3.
- [ ] `POST /recibos/{id}/revision` para aprobar/rechazar casos
      `posible_duplicado` (conecta los botones de la Fase 1).
- [ ] Registrar la decisión y sus señales en el log (base de la auditoría de M2).

## Requisitos relevantes del documento original

- **Motor de detección** (§5.3), **Estados** (§5.4).
- **API** (§5.5): `POST /recibos` (pipeline completo), `POST /recibos/{id}/revision`.
- **Modelo de datos** (§7): `clave_compuesta_hash`, `phash`, `estado`, `score`.
- **Objetivos de negocio** (§2): detectar duplicados antes de pagar, evidencia
  auditable, conservar siempre la revisión humana para baja confianza.

## Criterios de "listo"

- Un recibo idéntico a uno existente se marca `duplicado_confirmado` (rojo).
- Una variación visual similar cae en `posible_duplicado` (amarillo) y va a
  revisión humana.
- El flujo aprobar/rechazar actualiza el estado y queda registrado.

## Notas

- Los umbrales son **provisorios por diseño**; no perseguir la perfección aquí —
  se calibran en M2 con datos reales (Fase 5).
- **Zona gris conservadora** (riesgo: variaciones legítimas marcadas como
  duplicado): ante la duda, enviar a revisión humana, nunca auto-confirmar en M1.
- La revisión humana **no se elimina**: en un sistema con consecuencias
  financieras, conservarla es diseño correcto (§2).
