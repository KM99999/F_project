# Fase 0 — Fundaciones y Autenticación

> **Demo al final de la fase:** el cliente abre la URL, ve una **pantalla de
> login real**, ingresa credenciales y entra a un área protegida (aún vacía).
> Es la primera cosa tangible que se muestra.

## Objetivo

Dejar lista la base sobre la que se construye todo: repositorio, contenedores,
base de datos, esqueletos de backend y frontend, y un **flujo de autenticación
funcional**. Sin esto no hay nada que mostrar ni dónde colgar las pantallas.

## Por qué va primero

- Es lo más rápido de volver demostrable: una pantalla de login es visible y
  validable por el cliente sin necesidad de IA ni pipeline.
- Establece el control de acceso exigido por seguridad (§6.2): "acceso a datos
  restringido al desarrollador".
- Toda pantalla posterior vive detrás del login, así que conviene tenerlo desde
  el día uno.

## Alcance / checklist

### Infraestructura base
- [ ] Repositorio inicializado con la estructura de carpetas (ver
      [stack-tecnologico](../referencia/stack-tecnologico.md)).
- [ ] `docker-compose` con servicios: `api` (FastAPI), `db` (PostgreSQL),
      `frontend` (React), `nginx`.
- [ ] PostgreSQL levantado con migraciones iniciales.
- [ ] Nginx como reverse proxy.
- [ ] HTTPS con Let's Encrypt vía Certbot (obligatorio — datos financieros).
- [ ] `.env` fuera del repositorio; secretos solo por variables de entorno.

### Backend — esqueleto y auth
- [ ] FastAPI corriendo con healthcheck.
- [ ] SQLAlchemy configurado.
- [ ] Tabla `usuarios` (`id`, `usuario`, `password_hash`, `rol`, `created_at`).
- [ ] Hash de contraseña (bcrypt/argon2). Nunca texto plano.
- [ ] Endpoint de login que emite token (JWT o sesión) y middleware que protege
      rutas privadas.
- [ ] Seed de un usuario inicial (desarrollador / operador del cliente).

### Frontend — esqueleto y login
- [ ] React SPA inicializada.
- [ ] **Pantalla de login** (usuario + contraseña).
- [ ] Manejo de token y rutas protegidas (redirige a login si no autenticado).
- [ ] Layout base / shell de la app con navegación entre las 3 pantallas
      (placeholders por ahora).

## Requisitos relevantes del documento original

- **Stack** (§3): Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy, React, Docker,
  Nginx, Certbot.
- **Seguridad** (§6.2): HTTPS obligatorio, acceso restringido, almacenamiento
  cifrado, secretos en variables de entorno, `.env` fuera del repo.
- **Modelo de datos** (§7): tabla `usuarios`.
- **Convenciones** (§10): código en inglés; strings de UI, roles y mensajes en
  español.

## Criterios de "listo"

- Se accede al sistema por HTTPS.
- Login funciona contra la tabla `usuarios`; credenciales inválidas se rechazan.
- Las rutas privadas redirigen a login si no hay sesión válida.
- `docker-compose up` levanta todo el stack desde cero.

## Notas

- El **NDA debe estar firmado** antes de cargar cualquier muestra real (§6.2).
  Esta fase no requiere datos reales, así que puede arrancar en paralelo a la
  gestión del NDA.
- Mantener el rol (`rol`) simple por ahora; la diferenciación fina de permisos no
  es parte de M1.
