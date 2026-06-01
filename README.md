# Sistema de Verificación de Recibos de Pago

Sistema web para detectar recibos de pago duplicados (manuscritos, fotos y PDFs).
Documentación funcional y plan de desarrollo por fases en [`docs/`](docs/README.md).

## Estado

**Fase 0 — Fundaciones y Autenticación** (en curso). Entrega: login funcional +
área protegida con el cascarón de las tres pantallas. Ver
[docs/fases/fase-0-fundaciones-y-auth.md](docs/fases/fase-0-fundaciones-y-auth.md).

## Stack

Backend FastAPI (Python 3.11) + PostgreSQL + SQLAlchemy · Frontend React (Vite) ·
Docker Compose + Nginx. Detalle en
[docs/referencia/stack-tecnologico.md](docs/referencia/stack-tecnologico.md).

## Estructura

```
app/                Backend FastAPI
  api/              Endpoints (auth) + dependencias
  core/             Seguridad (hashing de contraseñas, JWT)
  db/               Modelos SQLAlchemy y sesión
  schemas/          Esquemas Pydantic (entrada/salida)
frontend/           SPA React (login + cascarón de las 3 pantallas)
scripts/            init_db, seed_user
docker/             Dockerfiles + config de nginx
docker-compose.yml  Orquestación (db, api, frontend)
docs/               Documentación funcional y plan por fases
```

## Cómo levantar el sistema (Fase 0)

> **Despliegue en VPS (producción / demo al cliente):** ver el runbook paso a paso
> en [docs/deploy/vps-fase-0.md](docs/deploy/vps-fase-0.md) (incluye HTTPS con
> Let's Encrypt).

### Opción A — Docker Compose (recomendada)

Requiere Docker.

```bash
cp .env.example .env          # ajustar secretos (JWT_SECRET_KEY, contraseñas)
docker compose up --build
```

- App web: **http://localhost:8080**
- La API levanta, crea las tablas (`init_db`) y siembra el usuario inicial
  (`seed_user`) automáticamente.
- Credenciales del primer login: las definidas en `.env`
  (`SEED_USER_EMAIL` / `SEED_USER_PASSWORD`).

### Opción B — Desarrollo local (sin Docker)

Requiere Python 3.11+, Node 20+ y un PostgreSQL accesible.

**Backend**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # DATABASE_URL apuntando a tu PostgreSQL
python -m scripts.init_db
python -m scripts.seed_user
uvicorn app.main:app --reload                        # http://localhost:8000
```

**Frontend**
```bash
cd frontend
cp .env.example .env          # VITE_API_URL=http://localhost:8000
npm install
npm run dev                   # http://localhost:5173
```

## Endpoints (Fase 0)

| Método | Endpoint | Descripción |
|---|---|---|
| GET  | `/health`     | Healthcheck |
| POST | `/auth/login` | Login con email + contraseña → token JWT |
| GET  | `/auth/me`    | Datos del usuario autenticado (requiere token) |

## Seguridad

- Secretos solo por variables de entorno; `.env` está fuera del repositorio.
- Contraseñas almacenadas con hash bcrypt, nunca en texto plano.
- En producción: HTTPS obligatorio (Let's Encrypt vía Certbot en nginx).

## Verificación pendiente

> El código de la Fase 0 fue escrito y revisado, pero **aún no se ejecutó** en
> este entorno (no hay Python/Node/Docker instalados en la máquina de desarrollo
> usada para escribirlo). Antes de la demo al cliente hay que correr
> `docker compose up --build` en una máquina con Docker y confirmar el login.
