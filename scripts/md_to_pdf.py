"""Convierte los documentos de entrega (.md) a PDF.

Uso (en un contenedor con el repo montado en el working dir):
    pip install markdown xhtml2pdf
    python scripts/md_to_pdf.py

Genera docs/ENTREGA-M1.pdf y docs/MANUAL-OPERACION.pdf. Es una utilidad de
generación de documentación; no forma parte de la app en ejecución.
"""

import markdown
from xhtml2pdf import pisa

# Reemplazos para que los emojis/box-drawing no salgan como cuadros en el PDF.
REPL = {
    "\U0001F7E2": "(verde)", "\U0001F7E1": "(amarillo)", "\U0001F534": "(rojo)",
    "\U0001F6A9": "[bandera]", "\U0001F504": "[reprocesar]", "\U0001F4C4": "[doc]",
    "⚠️": "[atencion]", "⚠": "[atencion]", "✅": "[OK]",
    "→": "->", "►": ">", "▼": "v", "│": "|",
    "└": "+", "├": "+", "─": "-",
}

CSS = """
@page { size: A4; margin: 1.8cm; }
body { font-family: Helvetica; font-size: 10pt; color: #222; line-height: 1.45; }
h1 { font-size: 18pt; color: #111; border-bottom: 2px solid #2563eb; padding-bottom: 3px; }
h2 { font-size: 13pt; color: #2563eb; margin-top: 14px; }
h3 { font-size: 11pt; color: #111; }
code { background: #f3f4f6; font-family: Courier; font-size: 9pt; }
pre { background: #f3f4f6; padding: 6px; font-family: Courier; font-size: 8pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; }
th, td { border: 1px solid #bbb; padding: 3px 5px; }
th { background: #eef2f7; }
blockquote { background: #f8fafc; border-left: 3px solid #94a3b8; padding: 5px 9px; color: #444; }
a { color: #2563eb; }
"""

DOCS = [
    ("docs/ENTREGA-M1.md", "docs/ENTREGA-M1.pdf"),
    ("docs/MANUAL-OPERACION.md", "docs/MANUAL-OPERACION.pdf"),
]


def clean(text: str) -> str:
    for k, v in REPL.items():
        text = text.replace(k, v)
    return text


def main() -> None:
    for src, out in DOCS:
        with open(src, encoding="utf-8") as f:
            body = markdown.markdown(clean(f.read()), extensions=["tables", "fenced_code"])
        html = (
            "<html><head><meta charset='utf-8'><style>"
            + CSS
            + "</style></head><body>"
            + body
            + "</body></html>"
        )
        with open(out, "wb") as f:
            pisa.CreatePDF(html, dest=f, encoding="utf-8")
        print("PDF generado:", out)


if __name__ == "__main__":
    main()
