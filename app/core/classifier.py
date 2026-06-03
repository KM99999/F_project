"""Document classification (§5.1).

- PDF with selectable text (pdfplumber finds text) -> "pdf_estructurado".
- PDF with no extractable text (scanned image) -> treated as a photo.
- Image files -> photo; printed-vs-handwritten is decided by Claude during extraction.
"""

import io
import logging

import pdfplumber

logger = logging.getLogger("recibos.classify")

# Minimum chars of extracted text to consider a PDF "structured" (not scanned).
_MIN_PDF_TEXT = 20

IMAGE_MEDIA_TYPES = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
    "image/webp": "image/webp",
    "image/gif": "image/gif",
}


def is_pdf(content_type: str, filename: str) -> bool:
    return content_type == "application/pdf" or filename.lower().endswith(".pdf")


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Return concatenated selectable text from the PDF (empty if scanned)."""
    parts: list[str] = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                if text:
                    parts.append(text)
    except Exception as exc:  # noqa: BLE001 — corrupt/unsupported PDF
        logger.warning("pdfplumber failed: %s", exc)
        return ""
    return "\n".join(parts).strip()


def has_structured_text(pdf_text: str) -> bool:
    return len(pdf_text) >= _MIN_PDF_TEXT


def resolve_image_media_type(content_type: str, filename: str) -> str:
    """Map an uploaded image to a media type Claude accepts; default to JPEG."""
    if content_type in IMAGE_MEDIA_TYPES:
        return IMAGE_MEDIA_TYPES[content_type]
    lower = filename.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".gif"):
        return "image/gif"
    return "image/jpeg"
