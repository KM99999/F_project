# Despliegue en VPS — Fase 0

Runbook para desplegar la Fase 0 (login + área protegida) en un VPS
(Hetzner / DigitalOcean) con Docker. Resultado final: el cliente accede por
HTTPS, ve la pantalla de login y entra al cascarón de las tres pantallas.

El despliegue tiene dos etapas:
- **Etapa A** — levantar por HTTP y verificar el login (feedback rápido).
- **Etapa B** — agregar dominio + HTTPS (Let's Encrypt) para producción.

> Convención: los comandos asumen un VPS Ubuntu 22.04+ y que ejecutás como un
> usuario con `sudo`.

---

## Prerrequisitos

- Un VPS con IP pública (Hetzner CX11 / DigitalOcean basic alcanza para la demo).
- Acceso SSH al VPS.
- Para la Etapa B: un dominio (o subdominio) cuyo registro **A** apunte a la IP
  del VPS (p. ej. `recibos.tudominio.com → 203.0.113.10`).

---

## 1. Conectarse e instalar Docker

```bash
ssh usuario@IP_DEL_VPS

# Docker Engine + plugin compose (script oficial)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER       # usar docker sin sudo
exit                                # cerrar sesión y reconectar para aplicar el grupo
```

Reconectar y verificar:

```bash
ssh usuario@IP_DEL_VPS
docker --version
docker compose version
```

## 2. Obtener el código

El repositorio es público, así que se clona directo:

```bash
git clone https://github.com/KM99999/F_project.git
cd F_project
```

## 3. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

Ajustar como mínimo:

- `JWT_SECRET_KEY` → un valor aleatorio fuerte. Generarlo con:
  ```bash
  openssl rand -hex 32
  ```
- `POSTGRES_PASSWORD` → una contraseña fuerte. La API arma su URL de conexión a
  partir de los `POSTGRES_*` automáticamente, así que **no hace falta** tocar
  `DATABASE_URL` (dejarlo comentado para el deploy con docker-compose).
- `SEED_USER_USERNAME` / `SEED_USER_PASSWORD` → credenciales del primer login que
  se le darán al cliente para la demo (el login es por usuario, no por email).
- `FRONTEND_ORIGIN` → en producción el SPA y la API comparten origen (mismo
  dominio), así que CORS no se usa; podés dejar el valor por defecto.

> `.env` está en `.gitignore`: nunca se sube al repositorio.

---

## Etapa A — Verificar por HTTP

Levanta el stack base (Postgres + API + nginx sirviendo el SPA en el puerto 8080):

```bash
docker compose up -d --build
docker compose ps           # los 3 servicios en estado "running"/"healthy"
docker compose logs api     # debe mostrar: tablas creadas, usuario sembrado, uvicorn arrancado
```

Probar:

- API viva: `curl http://localhost:8080/api/health` → `{"status":"ok",...}`
- En el navegador: `http://IP_DEL_VPS:8080` → pantalla de login.
- Ingresar con `SEED_USER_USERNAME` / `SEED_USER_PASSWORD` → entra al área protegida
  con la barra de navegación y las tres pantallas (placeholders).

Si esto funciona, la Fase 0 está verificada funcionalmente. Para producción,
continuar con la Etapa B.

> Recordá abrir los puertos en el firewall del proveedor / `ufw`:
> Etapa A → 8080; Etapa B → 80 y 443.

---

## Etapa B — Dominio + HTTPS

### 5. Emitir el primer certificado

Requiere que el registro **A** del dominio ya apunte a la IP del VPS y que el
puerto 80 esté libre.

```bash
# Liberar el puerto 80 (bajar el stack de la Etapa A)
docker compose down

# Carpetas que comparten nginx y certbot (bind-mounts)
mkdir -p letsencrypt certbot-webroot

# Emitir el certificado en modo standalone (ocupa el 80 sólo durante la emisión)
docker run --rm -p 80:80 \
  -v "$PWD/letsencrypt:/etc/letsencrypt" \
  certbot/certbot certonly --standalone \
  -d recibos.tudominio.com \
  --email tu-email@dominio.com --agree-tos --no-eff-email
```

Debe terminar con *"Successfully received certificate"* y dejar los archivos en
`letsencrypt/live/recibos.tudominio.com/`.

### 6. Poner el dominio en la config de nginx

Reemplazar el placeholder `__DOMAIN__` por tu dominio real en
[`docker/nginx/nginx.prod.conf`](../../docker/nginx/nginx.prod.conf):

```bash
sed -i 's/__DOMAIN__/recibos.tudominio.com/g' docker/nginx/nginx.prod.conf
```

### 7. Levantar con HTTPS

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Esto usa el overlay de producción:
- nginx escucha en **80** (redirige a HTTPS + sirve el challenge ACME) y **443**.
- el servicio `certbot` renueva el certificado cada 12 h automáticamente.

Probar:

- `https://recibos.tudominio.com` → login por HTTPS (candado válido).
- `http://recibos.tudominio.com` → redirige a HTTPS.
- Ingresar con las credenciales sembradas → área protegida.

> Tras una renovación de certificado, nginx necesita recargar para tomar el nuevo:
> `docker compose -f docker-compose.yml -f docker-compose.prod.yml exec frontend nginx -s reload`
> (o reiniciar el contenedor `frontend` periódicamente).

---

## Operación

- **Ver estado / logs:**
  `docker compose -f docker-compose.yml -f docker-compose.prod.yml ps`
  `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api`
- **Actualizar a una nueva versión del código:**
  ```bash
  git pull
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
  ```
- **Backups de PostgreSQL** (requisito §6.3, retención ≥ 30 días) — pendiente de
  configurar en la fase de cierre de M1 (Fase 4). Ejemplo de dump manual:
  ```bash
  docker compose exec db pg_dump -U recibos recibos > backup_$(date +%F).sql
  ```

## Notas de seguridad (§6.2)

- `JWT_SECRET_KEY` y contraseñas sólo en `.env` del servidor, nunca en el repo.
- HTTPS obligatorio en producción (datos financieros) — Etapa B.
- Acceso al VPS restringido (SSH con clave, firewall cerrado salvo 80/443).

## Pendiente de ejecución

> El código de la Fase 0 fue escrito y revisado pero **aún no se ejecutó**
> (el entorno de desarrollo no tiene Python/Node/Docker). Esta primera ejecución
> en el VPS es también la primera verificación real del build. Si algún paso
> falla (build de imágenes, arranque de la API), revisar `docker compose logs` y
> reportarlo para corregir.
