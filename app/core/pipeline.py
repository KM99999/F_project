"""Pipeline orchestrator (§5.1): classify -> extract -> normalize -> detect -> persist.

Images are re-encoded to a clean JPEG before extraction (handles iPhone HEIC,
oversized photos and wrong extensions) and the converted copy is what we store,
so it also displays in the browser. PDFs are sent/stored as-is.
"""

import logging
import os

from sqlalchemy.orm import Session

from app.core import classifier, normalize, storage
from app.db.models import Recibo
from app.detection import engine, exact
from app.detection import phash as phash_mod
from app.vision import extractor

logger = logging.getLogger("recibos.pipeline")


def _jpg_name(filename: str) -> str:
    base = os.path.splitext(filename or "imagen")[0]
    return f"{base}.jpg"


def _process_recibo(file_bytes: bytes, filename: str, content_type: str):
    """Return (ExtractionResult, store_bytes, store_name, phash_source|None)."""
    if classifier.is_pdf(content_type, filename):
        # Siempre por visión sobre el PDF: lee el texto digital Y el contenido
        # escaneado/manuscrito. Un PDF "con texto" (membrete impreso) puede tener
        # los datos clave (monto, cliente) escritos a mano sobre el formulario, y
        # esos no están en la capa de texto.
        logger.info("Recibo PDF -> extracción por documento (visión: texto + manuscrito)")
        result = extractor.extract_from_pdf_document(file_bytes)
        result.tipo_documento = "pdf_estructurado"
        return result, file_bytes, filename, None

    img_bytes, media_type = classifier.normalize_for_claude(file_bytes)
    logger.info("Recibo clasificado: imagen (%s)", media_type)
    result = extractor.extract_from_image(img_bytes, media_type)
    return result, img_bytes, _jpg_name(filename), img_bytes


def _process_carnet(file_bytes: bytes, filename: str, content_type: str):
    """Return (CarnetExtraction, store_bytes, store_name)."""
    if classifier.is_pdf(content_type, filename):
        return extractor.extract_carnet_from_pdf_document(file_bytes), file_bytes, filename
    img_bytes, media_type = classifier.normalize_for_claude(file_bytes)
    return extractor.extract_carnet_from_image(img_bytes, media_type), img_bytes, _jpg_name(filename)


def process_verificacion(
    db: Session,
    recibo_bytes: bytes,
    recibo_name: str,
    recibo_ct: str,
    carnet_bytes: bytes,
    carnet_name: str,
    carnet_ct: str,
) -> Recibo:
    """Process a verification: receipt + client carnet -> one persisted record."""
    extracted, rb_store, rb_name, phash_src = _process_recibo(recibo_bytes, recibo_name, recibo_ct)
    imagen_url = storage.save_upload(rb_store, rb_name)

    # Carnet (obligatorio): estructurado y claro -> extracción directa.
    carnet, cb_store, cb_name = _process_carnet(carnet_bytes, carnet_name, carnet_ct)
    carnet_url = storage.save_upload(cb_store, cb_name)

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
        carnet_imagen_url=carnet_url,
        carnet_codigo=(carnet.codigo or "").strip() or None,
        carnet_nombre=carnet.nombre,
        carnet_fecha_nac=carnet.fecha_nacimiento,
    )

    # --- Detección de duplicados (Fase 3) ---
    # pHash solo para imágenes; los PDFs estructurados se apoyan en el match exacto.
    phash = phash_mod.compute_phash(phash_src) if phash_src is not None else None
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
