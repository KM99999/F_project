"""ORM models.

Phase 0 only needs the `usuarios` table (authentication). The receipts,
decision-log and embeddings tables are added in later phases — see
docs/referencia/modelo-de-datos.md.

Note (project convention §10): code identifiers are in English, but DB table and
column names are in Spanish.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(50), nullable=False, default="operador")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Recibo(Base):
    __tablename__ = "recibos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo_documento: Mapped[str] = mapped_column(String(30), nullable=False)
    imagen_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Extracted + normalized fields (normalized for matching; *_original for UI).
    fecha: Mapped[str | None] = mapped_column(String(10), nullable=True)  # ISO YYYY-MM-DD
    monto: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    moneda: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cliente: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cliente_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emisor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emisor_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
    concepto: Mapped[str | None] = mapped_column(Text, nullable=True)
    forma_pago: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Detection fields — populated in Fase 3 (motor de detección).
    clave_compuesta_hash: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    phash: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    estado: Mapped[str] = mapped_column(String(30), nullable=False, default="unico")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Per-field confidence for handwritten receipts (alta/media/baja).
    confianza_por_campo: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
