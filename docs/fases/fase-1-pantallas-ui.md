# Fase 1 — Pantallas UI (cascarón navegable)

> **Demo al final de la fase:** el cliente recorre el flujo completo de las tres
> pantallas —carga, lista y detalle— con **datos de ejemplo (mock)**, antes de
> que exista el pipeline real. Valida el flujo y la disposición visual temprano.

## Objetivo

Construir las tres pantallas de la SPA con datos simulados, de modo que el
cliente pueda **ver y navegar el producto completo** y dar feedback sobre el
flujo mucho antes de que el motor esté listo.

## Por qué va aquí

- Es la entrega más visible y la que más feedback genera por unidad de esfuerzo.
- Permite validar el flujo de revisión humana (clave del negocio) sin depender de
  la IA.
- Las pantallas quedan listas para "encenderse" con datos reales al terminar la
  Fase 2 y la Fase 3: solo se cambia el origen de datos de mock a API.

## Alcance / checklist

### Pantalla 1 — Carga
- [ ] Drag-and-drop de archivos.
- [ ] Captura/foto desde celular.
- [ ] Indicador de progreso durante el procesamiento (simulado por ahora).

### Pantalla 2 — Lista
- [ ] Tabla con todos los recibos procesados.
- [ ] Estado en color: **verde** (`unico`), **amarillo** (`posible_duplicado`),
      **rojo** (`duplicado_confirmado`).
- [ ] Filtros por estado y por rango de fechas.
- [ ] Paginación.

### Pantalla 3 — Detalle y revisión
- [ ] Imagen original a la izquierda, datos extraídos a la derecha.
- [ ] Sección de casos similares debajo (si los hay).
- [ ] Botones **aprobar / rechazar**, visibles **solo** si el estado es
      `posible_duplicado`.

### Soporte
- [ ] Fixtures / datos mock que cubran los tres estados y casos con/ sin
      similares.
- [ ] Capa de datos del frontend desacoplada (mock hoy, API real luego).

## Requisitos relevantes del documento original

- **Interfaz web** (§5.6): las tres pantallas y su comportamiento.
- **Estados de recibo** (§5.4): `unico | posible_duplicado | duplicado_confirmado`.
- **Prioridad** (§5.6): *funcionalidad sobre estética*. El panel de revisión
  humana puede ser deliberadamente simple en M1.

## Criterios de "listo"

- Se navega login → carga → lista → detalle sin romper.
- Los tres estados se distinguen por color en la lista.
- Los filtros por estado y fecha funcionan sobre los datos mock.
- Los botones aprobar/rechazar aparecen solo en `posible_duplicado`.

## Notas

- **No** invertir en estética pulida en M1; el objetivo es flujo claro y
  funcional. La calidad visual se puede mejorar después sin reescribir lógica.
- Mantener los nombres de estado en `snake_case` español tal como se muestran al
  cliente (§10).
