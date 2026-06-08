"""Detection engine — combines exact match, pHash and field overlap into a
0-100 score and an estado (§5.3 / §5.4).

Weighting (§5.3):
- exact match of the 4 key fields  -> high (100)
- pHash with low Hamming distance  -> medium-high
- partial match (3 of 4 fields)    -> medium

Thresholds (provisional — calibrated in M2):
- score < 40            -> unico
- 40 <= score <= 75     -> posible_duplicado (revisión humana)
- score > 75            -> duplicado_confirmado
"""

import logging
from typing import Optional

from sqlalchemy import select

from app.db.models import Recibo
from app.detection import phash as phash_mod

logger = logging.getLogger("recibos.detection")

THRESH_UNICO = 40
THRESH_CONFIRM = 75


def estado_from_score(score: int) -> str:
    if score < THRESH_UNICO:
        return "unico"
    if score <= THRESH_CONFIRM:
        return "posible_duplicado"
    return "duplicado_confirmado"


def _count_field_matches(a: Recibo, b: Recibo) -> int:
    n = 0
    if a.emisor and a.emisor == b.emisor:
        n += 1
    if a.fecha and a.fecha == b.fecha:
        n += 1
    if a.cliente and a.cliente == b.cliente:
        n += 1
    if a.monto is not None and b.monto is not None and a.monto == b.monto:
        n += 1
    return n


def _pair_score(a: Recibo, b: Recibo, a_phash: Optional[str] = None):
    """Return (score, fields_matched, hamming_distance|None)."""
    ah = a_phash if a_phash is not None else getattr(a, "phash", None)
    fields = _count_field_matches(a, b)
    if fields >= 4:
        score = 100
    elif fields == 3:
        score = 60
    elif fields == 2:
        score = 35
    else:
        score = 0

    dist = phash_mod.hamming(ah, b.phash)
    if dist is not None:
        if dist <= 4:
            score = max(score, 85)
        elif dist <= 6:
            score = max(score, 75)
        elif dist <= 12:
            score = max(score, 50)
    return score, fields, dist


def _motivo(fields: int, dist: Optional[int], exact: bool) -> str:
    if exact or fields >= 4:
        return "Coincidencia exacta de emisor, fecha, monto y cliente."
    if fields == 3:
        return "Coincidencia parcial (3 de 4 campos clave)."
    if dist is not None and dist <= 12:
        return "Imagen visualmente similar (hash perceptual cercano)."
    return "Coincidencia parcial de campos."


def evaluate(db, recibo: Recibo, phash: Optional[str], exclude_id: int | None = None) -> tuple[str, int]:
    """Score a receipt against existing ones. On reprocess the receipt is already
    persisted, so pass exclude_id to avoid it matching itself."""
    query = select(Recibo)
    if exclude_id is not None:
        query = query.where(Recibo.id != exclude_id)
    candidates = db.execute(query).scalars().all()

    # Exact composite-key match short-circuits to a confirmed duplicate.
    if recibo.clave_compuesta_hash:
        for c in candidates:
            if c.clave_compuesta_hash and c.clave_compuesta_hash == recibo.clave_compuesta_hash:
                return "duplicado_confirmado", 100

    best = 0
    for c in candidates:
        score, _, _ = _pair_score(recibo, c, a_phash=phash)
        best = max(best, score)
    return estado_from_score(best), best


def find_similares(db, recibo: Recibo, limit: int = 10) -> list[dict]:
    """Recompute similar cases for a persisted receipt (detail view)."""
    others = db.execute(select(Recibo).where(Recibo.id != recibo.id)).scalars().all()
    out: list[dict] = []
    for c in others:
        exact = bool(
            recibo.clave_compuesta_hash and recibo.clave_compuesta_hash == c.clave_compuesta_hash
        )
        score, fields, dist = _pair_score(recibo, c)
        if exact:
            score = 100
        if score >= THRESH_UNICO:
            out.append({"id": c.id, "score": score, "motivo": _motivo(fields, dist, exact)})
    out.sort(key=lambda x: -x["score"])
    return out[:limit]
