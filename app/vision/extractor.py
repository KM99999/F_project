"""Field extraction via Claude (vision for images, text for structured PDFs).

Returns a validated ExtractionResult. JSON is parsed and validated against the
Pydantic schema (robust across SDK versions); null fields are allowed.
"""

import base64
import json
import logging
import re

from app.config import settings
from app.schemas.recibo import CarnetExtraction, ExtractionResult
from app.vision import prompts
from app.vision.client import get_client

logger = logging.getLogger("recibos.vision")

# System prompt is stable -> cache it (prompt caching, ~90% cheaper on repeats).
_SYSTEM_BLOCKS = [
    {"type": "text", "text": prompts.EXTRACTION_SYSTEM, "cache_control": {"type": "ephemeral"}}
]
_CARNET_SYSTEM_BLOCKS = [
    {"type": "text", "text": prompts.CARNET_SYSTEM, "cache_control": {"type": "ephemeral"}}
]


def _json_dict(text: str) -> dict:
    """Extract the first JSON object from the model text."""
    cleaned = text.strip()
    # Strip accidental markdown fences if the model added them.
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError(f"La respuesta de Claude no contiene JSON: {text[:200]}")
        return json.loads(match.group(0))


def _parse_json(text: str) -> ExtractionResult:
    return ExtractionResult.model_validate(_json_dict(text))


def _message_text(response) -> str:
    return "".join(block.text for block in response.content if block.type == "text")


def extract_from_image(image_bytes: bytes, media_type: str) -> ExtractionResult:
    """Extract fields from a receipt image (printed or handwritten)."""
    client = get_client()
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=_SYSTEM_BLOCKS,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": prompts.IMAGE_USER_TEXT},
            ],
        }],
    )
    logger.info("extract_from_image usage: %s", response.usage)
    return _parse_json(_message_text(response))


def extract_from_pdf_document(pdf_bytes: bytes) -> ExtractionResult:
    """Extract from a scanned PDF (no selectable text) via Claude's PDF support."""
    client = get_client()
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=_SYSTEM_BLOCKS,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                {"type": "text", "text": prompts.IMAGE_USER_TEXT},
            ],
        }],
    )
    logger.info("extract_from_pdf_document usage: %s", response.usage)
    return _parse_json(_message_text(response))


def extract_from_pdf_text(texto: str) -> ExtractionResult:
    """Extract fields from the selectable text of a structured PDF."""
    client = get_client()
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1024,
        system=_SYSTEM_BLOCKS,
        messages=[{
            "role": "user",
            "content": prompts.PDF_TEXT_USER_TEMPLATE.format(texto=texto[:12000]),
        }],
    )
    logger.info("extract_from_pdf_text usage: %s", response.usage)
    result = _parse_json(_message_text(response))
    result.tipo_documento = "pdf_estructurado"
    return result


# --- Carnet extraction -----------------------------------------------------

def extract_carnet_from_image(image_bytes: bytes, media_type: str) -> CarnetExtraction:
    client = get_client()
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=512,
        system=_CARNET_SYSTEM_BLOCKS,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": prompts.CARNET_USER_TEXT},
            ],
        }],
    )
    logger.info("extract_carnet_from_image usage: %s", response.usage)
    return CarnetExtraction.model_validate(_json_dict(_message_text(response)))


def extract_carnet_from_pdf_document(pdf_bytes: bytes) -> CarnetExtraction:
    client = get_client()
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=512,
        system=_CARNET_SYSTEM_BLOCKS,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                {"type": "text", "text": prompts.CARNET_USER_TEXT},
            ],
        }],
    )
    logger.info("extract_carnet_from_pdf_document usage: %s", response.usage)
    return CarnetExtraction.model_validate(_json_dict(_message_text(response)))
