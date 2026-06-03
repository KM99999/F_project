"""Perceptual hash (visual) — §5.3.

pHash of the receipt image; Hamming distance against existing hashes detects
visually similar images (crops, filters, photos of photocopies). Only applies to
image uploads — structured PDFs have no pHash and rely on the exact/field match.
"""

import io
import logging
from typing import Optional

logger = logging.getLogger("recibos.phash")


def compute_phash(image_bytes: bytes) -> Optional[str]:
    """Return the pHash as a hex string, or None on failure / unsupported input."""
    try:
        import imagehash
        from PIL import Image

        with Image.open(io.BytesIO(image_bytes)) as img:
            return str(imagehash.phash(img))
    except Exception as exc:  # noqa: BLE001 — bad/unsupported image
        logger.warning("compute_phash failed: %s", exc)
        return None


def hamming(hash_a: Optional[str], hash_b: Optional[str]) -> Optional[int]:
    """Hamming distance between two pHash hex strings (lower = more similar)."""
    if not hash_a or not hash_b:
        return None
    try:
        import imagehash

        return imagehash.hex_to_hash(hash_a) - imagehash.hex_to_hash(hash_b)
    except Exception as exc:  # noqa: BLE001
        logger.warning("hamming failed: %s", exc)
        return None
