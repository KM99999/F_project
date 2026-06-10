"""Convierte los documentos de entrega (.md) a PDF.

Uso (en un contenedor con el repo montado en el working dir):
    pip install markdown fpdf2
    python scripts/md_to_pdf.py

Genera docs/ENTREGA-M1.pdf y docs/MANUAL-OPERACION.pdf. Usa fpdf2 (PDF puro
Python, sin dependencias del sistema). Es una utilidad de documentación; no forma
parte de la app en ejecución.
"""

import re

import markdown
from fpdf import FPDF

# Reemplazos: emojis/box-drawing y caracteres fuera de latin-1 (fuentes core).
REPL = {
    "\U0001F7E2": "(verde)", "\U0001F7E1": "(amarillo)", "\U0001F534": "(rojo)",
    "\U0001F6A9": "[bandera]", "\U0001F504": "[reprocesar]", "\U0001F4C4": "[doc]",
    "⚠️": "[atencion]", "⚠": "[atencion]", "✅": "[OK]",
    "→": "->", "►": ">", "▼": "v", "│": "|", "└": "+", "├": "+", "─": "-",
    "—": "-", "–": "-", "•": "-", "≈": "~", "●": "*",
    "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...",
}

DOCS = [
    ("docs/ENTREGA-M1.md", "docs/ENTREGA-M1.pdf"),
    ("docs/MANUAL-OPERACION.md", "docs/MANUAL-OPERACION.pdf"),
]


def clean(text: str) -> str:
    for k, v in REPL.items():
        text = text.replace(k, v)
    # Las fuentes core de fpdf usan latin-1: descartar lo que no entre.
    return text.encode("latin-1", "ignore").decode("latin-1")


def fix_for_fpdf(html: str) -> str:
    """fpdf2 no admite etiquetas anidadas dentro de celdas ni dentro de <pre>.
    Quita <code> en todo el documento y aplana el contenido de td/th."""
    html = html.replace("<code>", "").replace("</code>", "")
    for tag in ("<thead>", "</thead>", "<tbody>", "</tbody>"):
        html = html.replace(tag, "")
    html = html.replace("<table>", '<table border="1">')

    def strip_inner(m):
        return m.group(1) + re.sub(r"<[^>]+>", "", m.group(2)) + m.group(3)

    return re.sub(r"(<(?:td|th)[^>]*>)(.*?)(</(?:td|th)>)", strip_inner, html, flags=re.S)


def main() -> None:
    for src, out in DOCS:
        with open(src, encoding="utf-8") as f:
            html = markdown.markdown(clean(f.read()), extensions=["tables", "fenced_code"])
        html = fix_for_fpdf(html)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.write_html(html)
        pdf.output(out)
        print("PDF generado:", out)


if __name__ == "__main__":
    main()
