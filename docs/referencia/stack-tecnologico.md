# Stack tecnológico y estructura del proyecto

> Referencia transversal. Fuente: §3 y §10 (estructura) del documento original.

## Stack (§3)

### Backend
- Lenguaje: Python 3.11+
- Framework: FastAPI
- Base de datos: PostgreSQL
- ORM: SQLAlchemy (o equivalente)

### Procesamiento de IA y documentos
- Visión por IA: Claude 3.5 Sonnet (API de Anthropic)
- Extracción de texto en PDFs: `pdfplumber`
- Hash perceptual de imagen: `imagehash` (algoritmo pHash)
- Embeddings visuales para firmas (M2): CLIP pre-entrenado

### Frontend
- React (SPA mínima de tres pantallas)

### Infraestructura
- Despliegue: VPS (Hetzner o DigitalOcean)
- Contenedores: Docker + docker-compose
- Reverse proxy: Nginx
- HTTPS: Let's Encrypt vía Certbot
- Almacenamiento de imágenes: bucket S3-compatible (R2 de Cloudflare u otro)

### Exportación
- Excel: `openpyxl`
- PDF (reportes M2): a definir (WeasyPrint o ReportLab)

## Estructura sugerida del proyecto (§10)

```
/app
  /api          # FastAPI endpoints
  /core         # Pipeline orquestador, normalización
  /vision       # Llamadas a Claude, prompts, parsers
  /detection    # Match exacto, pHash, score
  /db           # Modelos, migraciones
  /export       # Excel, PDF
/frontend       # React SPA
/tests          # Ground truth, validaciones, tests unitarios
/scripts        # Utilidades de operación
/docs           # Manual de usuario, doc técnica
```

## Costos operacionales mensuales estimados (§9 — a cargo del cliente)

| Concepto | USD/mes |
|---|---|
| API de Claude (2.000 recibos) | 20-40 |
| VPS | 10-20 |
| PostgreSQL | 5-15 |
| Storage de imágenes | 5-10 |
| Dominio, SSL, backups | 5-10 |
| **Total** | **50-100** |

> No incluido en el alcance (§9): costos operacionales mensuales (los paga el
> cliente directamente), mantenimientos posteriores a M2, migración de datos
> legados, integración con sistemas de terceros no especificados.
