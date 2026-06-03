"""Pipeline orchestrator (§5.1): classify -> extract -> normalize -> persist.

Fase 2 stops at persistence. Duplicate detection (hashes, score, estado) is
added in Fase 3; for now every receipt is stored as `unico` with score 0.
"""

import logging

from sqlalchemy.orm import Session

from app.core import classifier, normalize, storage
from app.db.models import Recibo
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
        estado="unico",   # detection runs in Fase 3
        score=0,
        confianza_por_campo=confianza,
    )
    db.add(recibo)
    db.commit()
    db.refresh(recibo)
    logger.info("Recibo %s procesado (tipo=%s)", recibo.id, recibo.tipo_documento)
    return recibo
