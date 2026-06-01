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

    # Database — by default the URL is assembled from the POSTGRES_* parts below
    # (same values the db container uses), so there is a single source of truth.
    # Set database_url explicitly to override (e.g. localhost or sqlite for local dev).
    postgres_user: str = "recibos"
    postgres_password: str = "recibos"
    postgres_db: str = "recibos"
    db_host: str = "db"
    db_port: int = 5432
    database_url: str | None = None

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

    @property
    def sqlalchemy_url(self) -> str:
        """The effective database URL: explicit override, else built from parts."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.db_host}:{self.db_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
