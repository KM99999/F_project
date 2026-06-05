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


def detect_image_media_type(data: bytes, content_type: str = "", filename: str = "") -> str:
    """Detect the REAL image format from the file's magic bytes.

    Filenames/extensions lie (e.g. a .jpeg that is actually a PNG), and Claude
    rejects a mismatched media_type. Trust the bytes; fall back to the
    extension/content-type only if the signature is unknown.
    """
    sig = data[:12]
    if sig[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if sig[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if sig[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if sig[:4] == b"RIFF" and sig[8:12] == b"WEBP":
        return "image/webp"
    return resolve_image_media_type(content_type, filename)


_MAX_SIDE = 2000  # px — downscale huge phone photos before sending to Claude


def normalize_for_claude(data: bytes) -> tuple[bytes, str]:
    """Re-encode any uploaded image to a clean, Claude-supported JPEG.

    Handles iPhone HEIC, wrong extensions (jpeg-that-is-png), CMYK/RGBA, EXIF
    rotation, and oversized photos (downscaled). Returns (jpeg_bytes, media_type).
    Falls back to the original bytes + detected media type if re-encoding fails.
    """
    try:
        from PIL import Image, ImageOps

        try:
            import pillow_heif

            pillow_heif.register_heif_opener()
        except Exception:  # noqa: BLE001 — HEIC support optional
            pass

        with Image.open(io.BytesIO(data)) as im:
            im = ImageOps.exif_transpose(im)  # honour camera orientation
            im = im.convert("RGB")
            if max(im.size) > _MAX_SIDE:
                im.thumbnail((_MAX_SIDE, _MAX_SIDE))
            out = io.BytesIO()
            im.save(out, format="JPEG", quality=85)
            return out.getvalue(), "image/jpeg"
    except Exception as exc:  # noqa: BLE001 — unreadable/unsupported image
        logger.warning("normalize_for_claude failed: %s", exc)
        return data, detect_image_media_type(data)
