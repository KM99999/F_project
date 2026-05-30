"""FastAPI application entry point.

Phase 0 exposes a healthcheck and the authentication endpoints. Later phases add
the receipt pipeline, detection engine and export endpoints behind this same app.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
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


@app.get("/health", tags=["health"])
def health() -> dict:
    """Liveness probe used by docker-compose / nginx."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}
