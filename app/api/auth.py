"""Authentication endpoints: login and current-user lookup."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.models import Usuario
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Validate credentials and return a JWT access token."""
    user = db.query(Usuario).filter(Usuario.usuario == payload.usuario).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        # Same message for both cases: do not reveal whether the user exists.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Return the authenticated user — used by the SPA to confirm the session."""
    return current_user
