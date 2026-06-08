"""Receipt endpoints (§5.5): upload + pipeline, paginated list, detail.

All endpoints require authentication. Duplicate-detection fields (estado/score/
similares) exist but are only meaningfully populated in Fase 3.
"""

import logging
import math
from datetime import date as date_cls

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import Date, cast, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core import pipeline
from app.detection import engine
from app.db.models import Recibo, Usuario
from app.db.session import get_db
from app.schemas.recibo import ReciboDetalle, ReciboListOut, ReciboOut, RevisionRequest

logger = logging.getLogger("recibos.api")

router = APIRouter(prefix="/recibos", tags=["recibos"])

_MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB por archivo (fotos de celular grandes)
_ALLOWED = {"application/pdf", "image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}


def _validate_upload(content: bytes, filename: str, content_type: str | None, etiqueta: str) -> None:
    if not content:
        raise HTTPException(status_code=400, detail=f"El {etiqueta} está vacío.")
    if len(content) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"El {etiqueta} supera el tamaño máximo (15 MB).")
    ok_ext = (filename or "").lower().endswith((".pdf", ".jpg", ".jpeg", ".png", ".webp", ".gif"))
    if content_type not in _ALLOWED and not ok_ext:
        raise HTTPException(status_code=415, detail=f"Tipo de archivo no soportado para el {etiqueta}.")


@router.post("", response_model=ReciboOut, status_code=status.HTTP_201_CREATED)
async def crear_verificacion(
    recibo: UploadFile = File(...),
    carnet: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> Recibo:
    """Upload a verification: receipt + client carnet (both required) and run the pipeline."""
    recibo_bytes = await recibo.read()
    carnet_bytes = await carnet.read()
    _validate_upload(recibo_bytes, recibo.filename or "", recibo.content_type, "recibo")
    _validate_upload(carnet_bytes, carnet.filename or "", carnet.content_type, "carnet")

    try:
        return pipeline.process_verificacion(
            db,
            recibo_bytes, recibo.filename or "recibo", recibo.content_type or "",
            carnet_bytes, carnet.filename or "carnet", carnet.content_type or "",
        )
    except RuntimeError as exc:  # e.g. missing API key
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Fallo al procesar la verificación")
        raise HTTPException(status_code=502, detail=f"No se pudo procesar la verificación: {exc}")


@router.get("", response_model=ReciboListOut)
def listar_recibos(
    estado: str | None = Query(default=None),
    desde: str | None = Query(default=None),
    hasta: str | None = Query(default=None),
    campo_fecha: str = Query(default="servicio"),  # "servicio" | "procesamiento"
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ReciboListOut:
    """Paginated list. Filters by estado and a date range over the chosen date
    field: servicio (Recibo.fecha) or procesamiento (Recibo.created_at) (§5.6)."""
    conditions = []
    if estado:
        conditions.append(Recibo.estado == estado)

    if campo_fecha == "procesamiento":
        col = cast(Recibo.created_at, Date)
        if desde:
            conditions.append(col >= date_cls.fromisoformat(desde))
        if hasta:
            conditions.append(col <= date_cls.fromisoformat(hasta))
    else:
        if desde:
            conditions.append(Recibo.fecha >= desde)
        if hasta:
            conditions.append(Recibo.fecha <= hasta)

    base = select(Recibo)
    for cond in conditions:
        base = base.where(cond)

    total = len(db.execute(base).scalars().all())
    rows = (
        db.execute(
            base.order_by(Recibo.created_at.desc())
            .offset((page - 1) * pageSize)
            .limit(pageSize)
        )
        .scalars()
        .all()
    )
    return ReciboListOut(
        items=[ReciboOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        pageSize=pageSize,
        totalPages=max(1, math.ceil(total / pageSize)),
    )


@router.get("/{recibo_id}", response_model=ReciboDetalle)
def obtener_recibo(
    recibo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> ReciboDetalle:
    """Receipt detail. `similares` is populated in Fase 3."""
    recibo = db.get(Recibo, recibo_id)
    if recibo is None:
        raise HTTPException(status_code=404, detail="Recibo no encontrado.")
    detalle = ReciboDetalle.model_validate(recibo)
    detalle.similares = engine.find_similares(db, recibo)
    return detalle


@router.post("/{recibo_id}/revision", response_model=ReciboOut)
def revisar_recibo(
    recibo_id: int,
    payload: RevisionRequest,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> Recibo:
    """Revisión humana (§5.6): aprobar => duplicado_confirmado; rechazar => unico."""
    recibo = db.get(Recibo, recibo_id)
    if recibo is None:
        raise HTTPException(status_code=404, detail="Recibo no encontrado.")
    recibo.estado = "duplicado_confirmado" if payload.decision == "aprobar" else "unico"
    db.commit()
    db.refresh(recibo)
    return recibo


@router.post("/{recibo_id}/reprocesar", response_model=ReciboOut)
def reprocesar_recibo(
    recibo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
) -> Recibo:
    """Re-ejecuta extracción + detección sobre los archivos ya guardados (sin re-subir)."""
    recibo = db.get(Recibo, recibo_id)
    if recibo is None:
        raise HTTPException(status_code=404, detail="Recibo no encontrado.")
    try:
        return pipeline.reprocess(db, recibo)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except FileNotFoundError:
        raise HTTPException(status_code=409, detail="No se encontró el archivo original para reprocesar.")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Fallo al reprocesar")
        raise HTTPException(status_code=502, detail=f"No se pudo reprocesar: {exc}")
