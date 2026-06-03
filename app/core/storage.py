"""Local storage for uploaded receipt files (§3 — replaced by S3 bucket later).

Saves bytes under settings.upload_dir and returns a public URL the API serves
(see the static mount in app/main.py).
"""

import os
import uuid

from app.config import settings


def save_upload(content: bytes, filename: str) -> str:
    """Persist the upload and return its public URL."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(filename)[1].lower() or ".bin"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.upload_dir, stored_name)
    with open(path, "wb") as f:
        f.write(content)
    return f"{settings.upload_url_prefix}/{stored_name}"
