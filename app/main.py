"""FastAPI application entry point.

Phase 0 exposes a healthcheck and the authentication endpoints. Later phases add
the receipt pipeline, detection engine and export endpoints behind this same app.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.export import router as export_router
from app.api.recibos import router as recibos_router
from app.config import settings

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(recibos_router)
app.include_router(export_router)

# Serve uploaded receipt images locally (replaced by an S3 bucket later).
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount(settings.upload_url_prefix, StaticFiles(directory=settings.upload_dir), name="media")


@app.get("/health", tags=["health"])
def health() -> dict:
    """Liveness probe used by docker-compose / nginx."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
