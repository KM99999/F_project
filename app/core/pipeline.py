"""Pipeline orchestrator (§5.1): classify -> extract -> normalize -> persist.

Fase 2 stops at persistence. Duplicate detection (hashes, score, estado) is
added in Fase 3; for now every receipt is stored as `unico` with score 0.
"""

import logging

from sqlalchemy.orm import Session

from app.core import classifier, normalize, storage
from app.db.models import Recibo
from app.detection import engine, exact
from app.detection import phash as phash_mod
from app.schemas.recibo import ExtractionResult
from app.vision import extractor

logger = logging.getLogger("recibos.pipeline")


def _extract(file_bytes: bytes, filename: str, content_type: str) -> ExtractionResult:
    """Classify the document and run the appropriate extraction path."""
    if classifier.is_pdf(content_type, filename):
        text = classifier.extract_pdf_text(file_bytes)
        if classifier.has_structured_text(text):
            logger.info("Documento clasificado: pdf_estructurado")
            return extractor.extract_from_pdf_text(text)
        logger.info("PDF sin texto seleccionable -> tratado como documento escaneado")
        return extractor.extract_from_pdf_document(file_bytes)

    media_type = classifier.resolve_image_media_type(content_type, filename)
    logger.info("Documento clasificado: imagen (%s)", media_type)
    return extractor.extract_from_image(file_bytes, media_type)


def process_receipt(
    db: Session, file_bytes: bytes, filename: str, content_type: str
) -> Recibo:
    """Run the full pipeline and persist the resulting receipt."""
    imagen_url = storage.save_upload(file_bytes, filename)
    extracted = _extract(file_bytes, filename, content_type)

    confianza = (
        extracted.confianza_por_campo.model_dump(exclude_none=True)
        if extracted.confianza_por_campo
        else None
    )

    recibo = Recibo(
        tipo_documento=extracted.tipo_documento or "foto_impreso",
        imagen_url=imagen_url,
        fecha=normalize.normalize_date(extracted.fecha),
        monto=normalize.normalize_amount(extracted.monto),
        moneda=normalize.normalize_currency(extracted.moneda),
        cliente=normalize.normalize_text(extracted.cliente),
        cliente_original=extracted.cliente,
        emisor=normalize.normalize_text(extracted.emisor),
        emisor_original=extracted.emisor,
        concepto=normalize.normalize_text(extracted.concepto),
        forma_pago=extracted.forma_pago,
        confianza_por_campo=confianza,
    )

    # --- Detección de duplicados (Fase 3) ---
    # pHash solo para imágenes; los PDFs estructurados se apoyan en el match exacto.
    phash = None
    if not classifier.is_pdf(content_type, filename):
        phash = phash_mod.compute_phash(file_bytes)
    recibo.phash = phash
    clave = exact.build_clave(recibo.emisor, recibo.fecha, recibo.monto, recibo.cliente)
    recibo.clave_compuesta_hash = exact.clave_hash(clave)

    estado, score = engine.evaluate(db, recibo, phash)
    recibo.estado = estado
    recibo.score = score

    db.add(recibo)
    db.commit()
    db.refresh(recibo)
    logger.info(
        "Recibo %s procesado (tipo=%s, estado=%s, score=%s)",
        recibo.id, recibo.tipo_documento, recibo.estado, recibo.score,
    )
    return recibo
