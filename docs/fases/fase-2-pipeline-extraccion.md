# Fase 2 — Pipeline de extracción

> **Demo al final de la fase:** el cliente sube un recibo **real** (PDF, foto
> impresa o manuscrito) y ve los **6 campos extraídos y normalizados** en la
> pantalla de detalle. La Pantalla 1 deja de ser mock.

## Objetivo

Construir el pipeline que convierte un archivo entrante en datos estructurados:
clasificar el tipo de documento, extraer los campos clave y normalizarlos. Es el
primer punto donde el sistema produce **valor real medible** (precisión sobre
ground truth).

## Por qué va aquí

- Enciende la Pantalla 1 (carga real) y llena la Pantalla 2/3 con datos reales.
- Su precisión es el **criterio de aceptación de M1** y la validación intermedia
  obligatoria (riesgo #1) ocurre al final de esta fase, antes de la detección.

## Pre-requisitos de negocio

- [ ] NDA firmado.
- [ ] 30-50 muestras etiquetadas (**ground truth**) disponibles.
- [ ] Definición de precisión acordada con el cliente.

## Alcance / checklist

### Clasificación de tipo de documento
- [ ] PDF con texto seleccionable (`pdfplumber` extrae texto) → `pdf_estructurado`.
- [ ] PDF solo-imagen escaneada → tratar como foto.
- [ ] Imagen → llamada corta a Claude visión para clasificar `foto_impreso` vs
      `foto_manuscrito`.
- [ ] Salida: etiqueta `pdf_estructurado` | `foto_impreso` | `foto_manuscrito`.

### Extracción de campos
- [ ] PDFs estructurados: regex + reglas heurísticas; templates para emisores
      frecuentes; **fallback a Claude** si fallan las reglas en un campo crítico.
- [ ] Fotos: API de Claude con visión, prompt estructurado pidiendo JSON con
      esquema fijo.
- [ ] Manuscritos: pedir explícitamente **nivel de confianza por campo**
      (`alta` | `media` | `baja`).

**Campos clave (6):** Fecha · Monto · Cliente · Emisor · Concepto · Forma de pago.

### Normalización
- [ ] Fechas → ISO 8601 (`YYYY-MM-DD`); aceptar `DD/MM/YYYY`, `DD-MM-YY`, etc.
- [ ] Montos → `Decimal` sin símbolo; moneda en campo separado (`USD`, `ARS`…).
- [ ] Nombres/conceptos → lowercase, sin acentos, espacios colapsados,
      recortados. **Conservar la versión original** en campo aparte para la UI.

### Persistencia y API
- [ ] `POST /recibos` ejecuta clasificación → extracción → normalización →
      guarda en la tabla `recibos` (sin detección de duplicados todavía).
- [ ] `GET /recibos` (lista paginada) y `GET /recibos/{id}` (detalle) sirviendo
      datos reales a las pantallas de la Fase 1.
- [ ] Reintentos con backoff exponencial para fallos de red en la API de Claude.
- [ ] Timeout de 60 segundos por recibo.
- [ ] Log estructurado de cada procesamiento (insumo para M2 y auditoría).

## Requisitos relevantes del documento original

- **Pipeline** (§5.1), **Normalización** (§5.2).
- **API** (§5.5): `POST /recibos`, `GET /recibos`, `GET /recibos/{id}`.
- **Modelo de datos** (§7): tabla `recibos` (campos de extracción, `*_original`,
  `confianza_por_campo`).
- **Prompts a Claude** (§10): JSON estructurado, `null` para no encontrado, nunca
  inventar, 1-2 ejemplos few-shot, confianza por campo en manuscritos, modelo
  `claude-3-5-sonnet` fijo.
- **Operacional** (§6.3): reintentos, timeout, log estructurado.

## Criterios de "listo"

- **≥ 85% de precisión global** en los 4 campos clave (fecha, monto, cliente,
  emisor) sobre el ground truth acordado (§6.1, §8 M1).
- Los tres tipos de documento se clasifican y procesan correctamente.
- Las pantallas muestran datos reales extraídos, con versión normalizada y
  original disponible.

## Notas

- **Hito de control (fin de Semana 2):** validación intermedia obligatoria de la
  precisión **antes** de construir el motor de duplicados (Fase 3). Si no se
  alcanza el 85%, se ajusta extracción antes de seguir.
- Mantener el modelo de Claude constante entre ejecuciones para consistencia.
