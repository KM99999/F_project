"""Application settings, loaded from environment variables.

Secrets (DB credentials, JWT key) MUST come from the environment / .env file,
never hardcoded — see requisitos no funcionales (§6.2).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    app_name: str = "Sistema de Verificación de Recibos"
    environment: str = "development"

    # Database
    database_url: str = "postgresql+psycopg2://recibos:recibos@db:5432/recibos"

    # Auth / JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 hours

    # CORS — origin of the frontend SPA (dev default; override in prod)
    frontend_origin: str = "http://localhost:5173"

    # Seed user (used by scripts/seed_user.py for the first login)
    seed_user_email: str = "admin@recibos.local"
    seed_user_password: str = "cambiar-esta-clave"
    seed_user_role: str = "admin"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
