#!/usr/bin/env bash
# Despliegue de PRUEBA (Etapa A — HTTP) en un VPS Linux con Docker.
#
# Uso (dentro del repo clonado, en el VPS):
#   bash scripts/deploy_test.sh
#
# - Crea .env desde .env.example si no existe.
# - Genera JWT_SECRET_KEY y POSTGRES_PASSWORD fuertes automáticamente.
# - Pide la ANTHROPIC_API_KEY (necesaria para la extracción de la Fase 2).
# - Levanta el stack con docker compose y muestra el estado.
#
# ⚠️ Solo para PRUEBA con datos NO sensibles. Para datos reales hace falta HTTPS
#    (ver docs/deploy/vps-fase-0.md, Etapa B).
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "==> Creando .env desde .env.example"
  cp .env.example .env

  JWT=$(openssl rand -hex 32)
  PGPASS=$(openssl rand -hex 16)
  sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=${JWT}|" .env
  sed -i "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${PGPASS}|" .env
  echo "==> JWT_SECRET_KEY y POSTGRES_PASSWORD generados."

  printf "Pegá tu ANTHROPIC_API_KEY (Enter para dejarla vacía por ahora): "
  read -r APIKEY || true
  if [ -n "${APIKEY:-}" ]; then
    sed -i "s|^ANTHROPIC_API_KEY=.*|ANTHROPIC_API_KEY=${APIKEY}|" .env
    echo "==> ANTHROPIC_API_KEY configurada."
  else
    echo "==> Sin API key: el login y las pantallas funcionan, pero subir un recibo fallará en la extracción."
  fi
  echo "==> Usuario de login (por defecto): administrator / 123456789  (cambiar en .env para producción)"
else
  echo "==> .env ya existe; no se modifica."
fi

echo "==> Construyendo y levantando el stack..."
docker compose up -d --build

echo "==> Estado de los servicios:"
docker compose ps

IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo ""
echo "Listo. Abrí:  http://${IP:-IP_DEL_VPS}:8080"
echo "Login:        ver SEED_USER_* en .env (por defecto administrator / 123456789)"
echo "Logs API:     docker compose logs -f api"
