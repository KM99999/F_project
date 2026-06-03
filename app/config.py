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

    # AI / Anthropic (Fase 2). The project doc pinned "claude-3-5-sonnet", which
    # is now retired; "claude-sonnet-4-6" is its current Sonnet-tier replacement.
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_timeout_seconds: float = 60.0  # §6.3: 60s timeout per receipt
    anthropic_max_retries: int = 5  # §6.3: retries with exponential backoff

    # Local storage for uploaded receipt images (Fase 2). Replaced by an
    # S3-compatible bucket later (§3 infraestructura).
    upload_dir: str = "/data/uploads"
    # Public base path the API serves uploads under (see main.py static mount).
    upload_url_prefix: str = "/media"

    # Seed user (used by scripts/seed_user.py for the first login).
    # NOTE: this default password is weak — acceptable only for local/testing.
    # Override SEED_USER_PASSWORD in .env before handling real data (§6.2).
    seed_user_username: str = "administrator"
    seed_user_password: str = "123456789"
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
