"""Seed the initial user so the client can log in for the first demo.

Credentials come from the environment (SEED_USER_EMAIL / SEED_USER_PASSWORD).
Idempotent: if a user with that email already exists, it is left untouched.

Run:
    python -m scripts.seed_user
"""

from app.config import settings
from app.core.security import hash_password
from app.db.models import Usuario
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Usuario).filter(Usuario.email == settings.seed_user_email).first()
        if existing:
            print(f"El usuario '{settings.seed_user_email}' ya existe. Nada que hacer.")
            return

        user = Usuario(
            email=settings.seed_user_email,
            password_hash=hash_password(settings.seed_user_password),
            rol=settings.seed_user_role,
        )
        db.add(user)
        db.commit()
        print(f"Usuario inicial creado: {settings.seed_user_email} (rol: {settings.seed_user_role})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
