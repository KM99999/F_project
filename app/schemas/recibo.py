"""Pydantic schemas for receipts (API I/O) and the AI extraction result."""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

TipoDocumento = Literal["pdf_estructurado", "foto_impreso", "foto_manuscrito"]
Estado = Literal["unico", "posible_duplicado", "duplicado_confirmado"]
Confianza = Literal["alta", "media", "baja"]


# --- AI extraction (internal) ---------------------------------------------

class ConfianzaPorCampo(BaseModel):
    fecha: Optional[Confianza] = None
    monto: Optional[Confianza] = None
    cliente: Optional[Confianza] = None
    emisor: Optional[Confianza] = None


class ExtractionResult(BaseModel):
    """Validated shape Claude must return. `null` for fields not found (§10)."""

    tipo_documento: Optional[TipoDocumento] = None
    fecha: Optional[str] = None          # raw, as printed; normalized downstream
    monto: Optional[str] = None          # raw amount string
    moneda: Optional[str] = None
    cliente: Optional[str] = None
    emisor: Optional[str] = None
    concepto: Optional[str] = None
    forma_pago: Optional[str] = None
    confianza_por_campo: Optional[ConfianzaPorCampo] = None


# --- API output ------------------------------------------------------------

class ReciboOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_documento: str
    imagen_url: Optional[str] = None
    fecha: Optional[str] = None
    monto: Optional[Decimal] = None
    moneda: Optional[str] = None
    cliente: Optional[str] = None
    cliente_original: Optional[str] = None
    emisor: Optional[str] = None
    emisor_original: Optional[str] = None
    concepto: Optional[str] = None
    forma_pago: Optional[str] = None
    estado: Estado
    score: int
    confianza_por_campo: Optional[dict] = None
    created_at: datetime


class ReciboDetalle(ReciboOut):
    # Similar cases are computed in Fase 3; empty for now.
    similares: list = []


class ReciboListOut(BaseModel):
    items: list[ReciboOut]
    total: int
    page: int
    pageSize: int
    totalPages: int
