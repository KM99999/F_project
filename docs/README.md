# Documentación — Sistema de Verificación de Recibos de Pago

Esta carpeta es la **descomposición navegable** del documento de contexto
[`contexto_proyecto_recibos.md`](../contexto_proyecto_recibos.md), reorganizada
para facilitar el desarrollo paso a paso.

El archivo original sigue siendo la **fuente canónica** (integración con Claude /
CLAUDE.md). Estos documentos no lo reemplazan: lo ordenan en secuencia de
construcción y separan el *qué construir* (referencia) del *en qué orden y cómo*
(fases).

## Cómo leer esta documentación

1. Empieza por el **[roadmap](00-roadmap.md)** — define el orden de construcción y
   el cronograma verificable.
2. Sigue las **fases en orden**. Cada fase termina en algo **demostrable al
   cliente**, no en trabajo invisible.
3. Consulta **`referencia/`** cuando necesites el detalle técnico de un tema
   transversal (stack, modelo de datos, API, convenciones).

## Principio de priorización

> **Construir primero lo que se le puede mostrar al cliente.**

El orden de fases pone adelante lo visible y verificable (login, pantallas), y
deja el trabajo de motor interno detrás de una UI que ya existe. Esto da demos
tempranas, feedback continuo y reduce el riesgo de construir algo invisible que
el cliente no puede validar.

## Mapa de fases

| Fase | Entrega demostrable | Milestone |
|---|---|---|
| [0 — Fundaciones y Auth](fases/fase-0-fundaciones-y-auth.md) | Login funcional + área protegida | M1 |
| [1 — Pantallas UI](fases/fase-1-pantallas-ui.md) | Las 3 pantallas navegables (datos mock) | M1 |
| [2 — Pipeline de extracción](fases/fase-2-pipeline-extraccion.md) | Subir recibo real → ver campos extraídos | M1 |
| [3 — Motor de detección](fases/fase-3-motor-deteccion.md) | Subir duplicado → se marca en color | M1 |
| [4 — Exportación y cierre M1](fases/fase-4-exportacion-y-cierre-m1.md) | Export Excel + sistema en producción | M1 |
| [5 — Milestone 2](fases/fase-5-milestone-2.md) | Calibración, capa visual, automatización | M2 |

## Entrega al cliente

- [Documento de entrega — Milestone 1](ENTREGA-M1.md) — inventario de activos, propiedad/control, traspaso, operación
- [Manual de operación](MANUAL-OPERACION.md) — cómo usar el sistema (acceso, carga, lista, detalle, export)

## Despliegue

- [Despliegue en VPS — Fase 0](deploy/vps-fase-0.md) — runbook (Docker, dominio, HTTPS)

## Referencia transversal

- [Visión y objetivos](referencia/vision-y-objetivos.md)
- [Stack tecnológico y estructura del proyecto](referencia/stack-tecnologico.md)
- [Modelo de datos](referencia/modelo-de-datos.md)
- [API REST](referencia/api-rest.md)
- [Requisitos no funcionales](referencia/requisitos-no-funcionales.md)
- [Convenciones del proyecto](referencia/convenciones.md)
- [Glosario y riesgos](referencia/glosario-y-riesgos.md)
