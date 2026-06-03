"""Exact match (deterministic) — §5.3.

Composite key from the 4 normalized key fields (emisor + fecha + monto + cliente),
hashed (sha256) and indexed. Two receipts with the same hash are an exact match.
"""

import hashlib
from decimal import Decimal
from typing import Optional


def build_clave(
    emisor: Optional[str],
    fecha: Optional[str],
    monto: Optional[Decimal],
    cliente: Optional[str],
) -> Optional[str]:
    """Canonical composite key, or None if any key field is missing.

    Requiring all 4 fields avoids false matches between two receipts that merely
    share the same missing fields.
    """
    if not emisor or not fecha or monto is None or not cliente:
        return None
    monto_str = f"{Decimal(monto):.2f}"
    return f"{emisor}|{fecha}|{monto_str}|{cliente}"


def clave_hash(clave: Optional[str]) -> Optional[str]:
    if not clave:
        return None
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()
