# Fase 5 — Milestone 2: Refinamiento y automatización

> **Contexto:** se ejecuta **después** de la fase intermedia de uso real, usando
> los datos acumulados. Duración 2 semanas, USD 700.

## Objetivo

Calibrar el sistema con datos reales, añadir la capa visual avanzada, automatizar
los casos de alta certeza, entregar auditoría legible y reportes mensuales, y
cerrar el proyecto con documentación.

## Alcance / checklist

### Calibración con datos reales
- [ ] Recalcular umbrales (`umbral_alto`, `umbral_bajo`) con la señal acumulada
      en la fase intermedia, reemplazando los provisorios de la Fase 3.

### Auditoría (§5.8)
- [ ] Log de decisiones por recibo con **justificación legible para
      no-técnicos**, accesible desde la UI:
  - Por qué se clasificó en ese estado.
  - Qué señales contribuyeron al score.
  - Qué casos similares se compararon.
- [ ] Buen ejemplo: *"Duplicado de recibo #1234 por coincidencia exacta de
      emisor, fecha y monto."* — Mal ejemplo: *"pHash distance = 4."*

### Reportes mensuales (§5.9)
Exportables a PDF y Excel:
- [ ] Total de recibos procesados.
- [ ] Distribución por tipo de documento.
- [ ] Duplicados: auto-confirmados, revisados manualmente, falsos positivos.
- [ ] Tiempo promedio de procesamiento.
- [ ] Precisión observada del periodo (sobre casos revisados manualmente).
- [ ] Definir herramienta de PDF (WeasyPrint o ReportLab).

### Capa visual avanzada (§5.10)
> **Decisión de alcance (fin de Semana 5):** priorizar **bien una** capa antes
> que dos mediocres (riesgo identificado).

- **Similitud de firma manuscrita**
  - [ ] Detectar zona de firma (esquina inferior derecha; baja densidad de texto
        impreso + alta densidad de trazos).
  - [ ] Embedding visual con **CLIP pre-entrenado**.
  - [ ] Comparar contra firmas previas; similitud alta con emisor no coincidente
        en otros campos = señal sospechosa.
  - [ ] Tabla `firmas_embeddings`.
- **Detección de manipulación de imagen**
  - [ ] Metadatos EXIF: ausencia de EXIF de cámara = señal de fotocopia (no
        prueba).
  - [ ] Compresión JPEG: bloques inconsistentes sugieren edición local.
  - [ ] Comparación de layout: misma estructura con datos distintos = plantilla
        reusada.

### Automatización (§5.11)
Reglas basadas en umbrales calibrados:
- [ ] Auto-confirmar duplicado si `score > umbral_alto` **Y** match exacto de
      campos clave.
- [ ] Auto-clasificar único si `score < umbral_bajo`.
- [ ] Zona gris (intermedios) **sigue a revisión humana**. Conservadora por
      diseño.

### Notificaciones (§5.12)
- [ ] Email cuando se detecta duplicado de alta certeza.
- [ ] Panel de notificaciones en UI con casos pendientes y contador de urgencia.
- [ ] Frecuencia configurable: inmediato vs. resumen diario.

### Cierre
- [ ] Documentación entregada (manual de usuario, doc técnica).
- [ ] Acta M2 firmada.

## Requisitos relevantes del documento original

- §5.8 auditoría, §5.9 reportes, §5.10 capa visual, §5.11 automatización,
  §5.12 notificaciones.
- **Modelo de datos** (§7): tabla `firmas_embeddings`.
- **Exportación** (§3): PDF a definir (WeasyPrint o ReportLab).

## Criterios de "listo" (= aceptación M2)

- **Reducción medible del volumen de revisión manual** respecto a M1, manteniendo
  o mejorando la precisión en detección de duplicados reales sobre datos de uso
  observados (§8 M2).
- Auditoría legible accesible desde la UI.
- Reportes mensuales exportables.
- Acta M2 firmada.

## Notas

- La automatización es **conservadora por diseño**: solo automatiza los extremos
  de alta certeza; la zona gris siempre va a revisión humana.
