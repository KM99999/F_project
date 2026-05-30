"""Shared API dependencies (authentication guard)."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import Usuario
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales inválidas o sesión expirada.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    """Resolve the authenticated user from the bearer token, or raise 401."""
    subject = decode_access_token(token)
    if subject is None:
        raise _CREDENTIALS_ERROR

    user = db.get(Usuario, int(subject))
    if user is None:
        raise _CREDENTIALS_ERROR
    return user
