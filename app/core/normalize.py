"""Normalization of extracted fields (§5.2).

- Dates  -> ISO 8601 (YYYY-MM-DD), accepting common DD/MM/YYYY style inputs.
- Amounts -> Decimal without currency symbols; currency kept separately.
- Names/concepts -> lowercase, accent-stripped, whitespace-collapsed, trimmed.
  The original value is preserved separately for display.
"""

import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

_DATE_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y",
    "%d.%m.%Y", "%d.%m.%y", "%Y/%m/%d",
]

_CURRENCY_SYMBOLS = {
    "$": "USD", "us$": "USD", "usd": "USD", "u$s": "USD",
    "ars": "ARS", "$ar": "ARS", "€": "EUR", "eur": "EUR",
}


def normalize_text(value: Optional[str]) -> Optional[str]:
    """lowercase, strip accents, collapse internal whitespace, trim."""
    if value is None:
        return None
    text = unicodedata.normalize("NFKD", value)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def normalize_date(value: Optional[str]) -> Optional[str]:
    """Return ISO YYYY-MM-DD, or None if unparseable."""
    if not value:
        return None
    raw = value.strip()
    # Already ISO?
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw
    for fmt in _DATE_FORMATS:
        try:
            parsed = datetime.strptime(raw, fmt).date()
            return _clamp_two_digit_year(parsed).isoformat()
        except ValueError:
            continue
    return None


def _clamp_two_digit_year(d: date) -> date:
    # strptime maps %y 00-68 -> 2000s, 69-99 -> 1900s; receipts are recent, keep as-is.
    return d


def normalize_amount(value: Optional[str]) -> Optional[Decimal]:
    """Parse an amount string to Decimal, handling thousands/decimal separators."""
    if value is None:
        return None
    raw = str(value).strip()
    # Drop currency symbols / letters, keep digits and separators.
    cleaned = re.sub(r"[^\d.,-]", "", raw)
    if not cleaned:
        return None

    # Decide which separator is the decimal one: assume the LAST , or . is decimal.
    last_comma = cleaned.rfind(",")
    last_dot = cleaned.rfind(".")
    if last_comma > last_dot:
        # comma is decimal -> remove dots (thousands), comma -> dot
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        # dot is decimal (or no comma) -> remove thousands commas
        cleaned = cleaned.replace(",", "")
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


def normalize_currency(value: Optional[str]) -> Optional[str]:
    """Map a currency symbol/string to an ISO-ish code (USD, ARS, EUR...)."""
    if not value:
        return None
    key = value.strip().lower()
    if key in _CURRENCY_SYMBOLS:
        return _CURRENCY_SYMBOLS[key]
    up = value.strip().upper()
    if re.fullmatch(r"[A-Z]{3}", up):
        return up
    return None
