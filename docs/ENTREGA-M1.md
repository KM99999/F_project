# Documento de entrega — Milestone 1

**Proyecto:** Sistema de Verificación de Recibos de Pago
**Fecha de entrega:** _(completar)_
**Entregado a:** Frank Lora (cliente)

Este documento detalla **todo lo desarrollado y entregado hasta la fecha**, qué
activos existen, **a quién pertenecen**, y los pasos para que el cliente quede con
el **control total** de lo que ya pagó. El objetivo es que no exista ninguna
dependencia del desarrollador para operar, mantener o mover el sistema.

---

## 1. Resumen

El sistema está construido con **tecnología estándar y abierta** (sin licencias ni
servicios propietarios que generen dependencia) y corre en **contenedores Docker
sobre el servidor (VPS) del propio cliente**. Esto significa que el cliente puede
operarlo, moverlo a otro servidor o continuarlo con cualquier desarrollador.

**No existe ningún candado técnico.** La mayor parte de los activos críticos ya
están bajo control del cliente; lo único pendiente de traspaso formal es el
**código fuente** (ver §2 y §3).

---

## 2. Inventario de activos y propiedad

| Activo | Dónde está | Propiedad / control actual | Acción |
|---|---|---|---|
| **Código fuente** | Repositorio GitHub `KM99999/F_project` | Cuenta del desarrollador | **Transferir al cliente** (§3.1) |
| **Servidor / infraestructura** | VPS del cliente (IP `66.94.107.182`) | **Del cliente** (su VPS) | Cambiar contraseña root (§3.2) |
| **Aplicación en ejecución** | Docker en el VPS (`/root/F_project`) | En el servidor del cliente | — |
| **Base de datos (PostgreSQL)** | Volumen Docker en el VPS | En el servidor del cliente | Backups (§6.3) |
| **Imágenes / documentos subidos** | Volumen Docker en el VPS | En el servidor del cliente | Backups (§6.3) |
| **Clave de IA (Anthropic API key)** | Archivo `.env` en el VPS | **Del cliente** (la generó el cliente) | Rotar (§3.3) |
| **Credenciales de la app** (usuario `administrator`) | Base de datos | **Del cliente** | Cambiar contraseña (§3.4) |

> En resumen: **el servidor, la clave de IA y las credenciales de la app ya son
> del cliente.** Falta entregar el **código fuente**.

---

## 3. Cómo tomar el control total (checklist de traspaso)

### 3.1. Código fuente (GitHub)
El desarrollador transfiere el repositorio a la cuenta del cliente, con **todo el
historial de cambios**. Opciones:
- **Transferencia de propiedad** (recomendada): el cliente indica su usuario de
  GitHub y el desarrollador hace *Settings → Transfer ownership* del repositorio.
- **Copia completa**: alternativamente, se entrega el código como archivo
  comprimido (ZIP) y/o se sube a un repositorio creado por el cliente.

Una vez transferido, el cliente es **dueño del código** y puede clonarlo:
```bash
git clone https://github.com/<cuenta-del-cliente>/F_project.git
```

### 3.2. Servidor (VPS) — cambiar la contraseña root
El cliente debe cambiar la contraseña de `root` de su VPS para que el acceso quede
únicamente bajo su control:
```bash
ssh root@66.94.107.182
passwd        # ingresar la nueva contraseña dos veces
```
A partir de ese momento, el desarrollador **no tiene acceso** al servidor salvo que
el cliente lo otorgue explícitamente.

### 3.3. Rotar la clave de IA (Anthropic)
1. Generar una nueva clave en https://console.anthropic.com/settings/keys y
   **revocar la anterior**.
2. En el VPS, actualizarla:
   ```bash
   cd /root/F_project
   nano .env          # reemplazar el valor de ANTHROPIC_API_KEY
   docker compose up -d --force-recreate api
   ```

### 3.4. Cambiar la contraseña de la aplicación
Cambiar la contraseña del usuario `administrator` (hoy es una de prueba). Se puede
hacer recreando el usuario o, cuando esté disponible la función de cambio de
contraseña en pantalla, desde el propio sistema.

### 3.5. (Opcional) Cuenta de IA propia
La clave de IA pertenece al cliente y el consumo se factura a su cuenta de
Anthropic. Costo estimado de operación: **USD 20–40 / mes** para ~2.000 recibos.

---

## 4. Stack tecnológico (sin dependencia)

| Capa | Tecnología | Tipo |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Open source |
| Base de datos | PostgreSQL 16 | Open source |
| Frontend | React (Vite) | Open source |
| Contenedores | Docker + Docker Compose | Open source |
| Reverse proxy | Nginx | Open source |
| Extracción por IA | Anthropic Claude (API) | Servicio del cliente (su clave) |

Todo el stack es estándar de la industria. Cualquier desarrollador con experiencia
en estas tecnologías puede mantenerlo o continuarlo.

---

## 5. Arquitectura y dónde viven los datos

```
Navegador del usuario
        │ (HTTP/HTTPS)
        ▼
   Nginx (contenedor)  ──►  React SPA (interfaz)
        │  /api  ─────────►  FastAPI (contenedor)  ──►  PostgreSQL (contenedor + volumen)
        │  /media ────────►  Imágenes/PDF (volumen "uploads")
                              │
                              └──►  Anthropic Claude (nube) — solo para extraer datos
```

- **Los datos (base de datos e imágenes) viven en el VPS del cliente**, en volúmenes
  Docker persistentes (`db_data` y `uploads`).
- La **única salida a internet** es la llamada a la API de IA para extraer los
  campos de cada documento.

---

## 6. Operación

### 6.1. Desplegar / levantar el sistema
```bash
cd /root/F_project
cp .env.example .env     # si no existe; completar las claves
docker compose up -d --build
```
Acceso: `http://66.94.107.182:8080`. Guía detallada en
[docs/deploy/vps-fase-0.md](deploy/vps-fase-0.md).

### 6.2. Actualizar a una nueva versión
```bash
cd /root/F_project
git pull
docker compose up -d --build
```

### 6.3. Respaldos (backups)
**Base de datos:**
```bash
docker compose exec db pg_dump -U recibos recibos > backup_$(date +%F).sql
```
**Imágenes/documentos:** copiar el volumen `uploads` (o configurar un respaldo
periódico). Se recomienda **backup diario con retención mínima de 30 días**.

### 6.4. Ver estado y registros
```bash
docker compose ps
docker compose logs -f api
```

---

## 7. Funcionalidades entregadas (M1 + ajustes)

- **Acceso con usuario y contraseña** (sesión segura con token).
- **Verificación con dos documentos:** recibo **y** carnet del cliente en un único
  resultado.
- **Extracción automática con IA:** 6 campos del recibo (fecha, monto, cliente,
  emisor, concepto, forma de pago) y del carnet (nombre y **código**).
- **Soporte de fotos de celular** (incluido formato HEIC de iPhone), fotos grandes
  (se ajustan automáticamente) y **PDF** (incluso recibos manuscritos, leídos por
  visión).
- **Detección de duplicados:** coincidencia exacta + hash visual (pHash) + score,
  con estados **Único / Posible duplicado / Duplicado confirmado**.
- **Casos similares** y **revisión humana** (aprobar/rechazar) para los dudosos.
- **Alerta (red flag)** cuando el nombre del recibo no coincide con el del carnet.
- **Dos fechas:** del servicio (del recibo) y de procesamiento (de carga al sistema).
- **Lista con filtros** por estado y por rango de fechas (DD/MM/AAAA).
- **Detalle** con visor de imagen/PDF embebido y datos extraídos.
- **Reprocesar** un recibo ya cargado sin volver a subirlo.
- **Exportación a Excel** con hoja de resumen.

---

## 8. Seguridad y rotación de credenciales

Antes de operar con datos reales y sensibles, se recomienda:
- Cambiar la **contraseña root** del VPS (§3.2) y la de la **aplicación** (§3.4).
- Rotar la **clave de IA** (§3.3).
- Configurar **HTTPS** con un dominio (el sistema ya está preparado; ver runbook,
  Etapa B). El cliente maneja datos financieros, por lo que HTTPS es recomendable
  para producción.
- Mantener el archivo `.env` (que contiene las claves) **solo en el servidor**,
  nunca compartirlo.

---

## 9. Soporte y próximos pasos

- El **trabajo futuro se gestiona a través de Workana** (hitos y pagos protegidos
  para ambas partes).
- **Milestone 2** (pendiente): calibración de umbrales con datos reales, auditoría,
  reportes mensuales, capa visual avanzada, automatización y notificaciones.
- Mejoras solicitadas fuera del alcance original (gestión de usuarios, cambio de
  contraseña en pantalla, imagen institucional) se cotizan y agendan por Workana.

---

> **Manual de uso del sistema:** ver [docs/MANUAL-OPERACION.md](MANUAL-OPERACION.md).
