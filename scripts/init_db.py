"""Create database tables.

Phase 0 uses SQLAlchemy `create_all` for simplicity. When the schema starts
evolving (Phase 2+), migrate this to Alembic so changes are versioned.

Run:
    python -m scripts.init_db
"""

from app.db import models  # noqa: F401  (import registers models on Base.metadata)
from app.db.session import Base, engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas / verificadas correctamente.")


if __name__ == "__main__":
    main()
