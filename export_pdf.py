#!/usr/bin/env python3
"""
Export the whole wiki/ tree into a single offline PDF (or HTML as fallback).

Usage:
    python3 export_pdf.py                  # → out/artefactos-de-guerra.pdf
    python3 export_pdf.py --html            # → out/artefactos-de-guerra.html (no PDF)
    python3 export_pdf.py --output foo.pdf  # custom path

Requires:
    pip install markdown pyyaml
    pip install weasyprint   # optional, for PDF output

Without weasyprint the script falls back to producing a single
self-contained HTML file that can be opened in any browser and printed
to PDF from there (File → Print → Save as PDF).
"""
from __future__ import annotations
import argparse, html, re, sys
from pathlib import Path
import markdown
import yaml

ROOT = Path(__file__).parent.resolve()
WIKI = ROOT / "wiki"
OUT = ROOT / "out"

CATEGORY_ORDER = [
    "_root",
    "ferias-de-armas",
    "empresas-de-armas",
    "casos",
    "usos-de-armas",
    "autores-y-referencias",
    "herramientas",
    "marco-legal",
    "historia",
]
CATEGORY_LABELS = {
    "_root": "General",
    "ferias-de-armas": "Ferias de armas",
    "empresas-de-armas": "Empresas de armas",
    "casos": "Casos",
    "usos-de-armas": "Usos de armas",
    "autores-y-referencias": "Autores y referencias",
    "herramientas": "Herramientas",
    "marco-legal": "Marco legal",
    "historia": "Historia",
}

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def parse_note(md_path: Path):
    raw = md_path.read_text(encoding="utf-8")
    fm: dict = {}
    body = raw
    m = FRONTMATTER_RE.match(raw)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            fm = {}
        body = raw[m.end():]
    rel = md_path.relative_to(WIKI).as_posix()
    parts = rel.split("/")
    cat = parts[0] if len(parts) > 1 else "_root"
    title_m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else md_path.stem
    return {
        "slug": rel[:-3],
        "category": cat,
        "title": title,
        "body": body,
        "frontmatter": fm,
    }


def replace_wikilinks(body: str) -> str:
    def repl(m):
        target = m.group(1)
        if "|" in target:
            _, label = target.split("|", 1)
        else:
            label = target.split("/")[-1].replace("-", " ")
        return f'<span class="wikilink">{html.escape(label)}</span>'
    return WIKILINK_RE.sub(repl, body)


def md_to_html(body: str) -> str:
    pre = replace_wikilinks(body)
    return markdown.markdown(
        pre,
        extensions=["extra", "toc", "sane_lists", "tables", "fenced_code"],
    )


def collect_notes():
    notes = []
    for p in sorted(WIKI.rglob("*.md")):
        rel = p.relative_to(WIKI).as_posix()
        if rel == "00-pendientes.md":
            continue
        notes.append(parse_note(p))
    return notes


def group_by_category(notes):
    groups: dict[str, list] = {}
    for n in notes:
        groups.setdefault(n["category"], []).append(n)
    # ordered
    ordered = []
    for cat in CATEGORY_ORDER:
        if cat in groups:
            ordered.append((cat, sorted(groups[cat], key=lambda n: n["title"].lower())))
    return ordered


CSS = """
@page { size: A4; margin: 22mm 18mm 22mm 18mm; }
@page:first { margin-top: 60mm; }
body { font-family: "Helvetica Neue", "Arial", sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1a1a1a; }
h1.cover-title { font-size: 36pt; font-weight: 700; letter-spacing: -0.5pt; line-height: 1.1; page-break-after: always; margin-top: 40mm; }
h1.cover-subtitle { font-size: 14pt; color: #666; font-weight: 400; margin-top: 10mm; }
h1.cat-title { font-size: 26pt; page-break-before: always; border-bottom: 3px solid #d33f6a; padding-bottom: 6pt; margin-top: 0; color: #1a1a1a; }
h1 { font-size: 18pt; page-break-before: always; border-bottom: 1px solid #e0e0e0; padding-bottom: 4pt; margin-top: 0; }
h2 { font-size: 14pt; margin-top: 16pt; color: #333; }
h3 { font-size: 12pt; margin-top: 12pt; color: #444; }
h4 { font-size: 11pt; margin-top: 10pt; color: #555; text-transform: uppercase; letter-spacing: 0.3pt; }
p { margin: 6pt 0; text-align: justify; }
ul, ol { margin: 6pt 0; padding-left: 18pt; }
li { margin: 2pt 0; }
blockquote { border-left: 3px solid #d33f6a; padding-left: 10pt; margin: 10pt 0 10pt 4pt; color: #444; font-style: italic; }
code { background: #f5f5f5; padding: 1pt 4pt; border-radius: 2pt; font-family: "Menlo", monospace; font-size: 9pt; }
pre { background: #f5f5f5; padding: 8pt; border-radius: 4pt; overflow: auto; font-size: 9pt; }
table { border-collapse: collapse; width: 100%; margin: 10pt 0; font-size: 9.5pt; }
th, td { border: 1px solid #ccc; padding: 4pt 6pt; text-align: left; vertical-align: top; }
th { background: #f0f0f0; font-weight: 600; }
a { color: #1a5490; text-decoration: none; }
.wikilink { color: #1a5490; background: #eef3fb; padding: 0 3pt; border-radius: 2pt; font-size: 95%; }
.frontmatter-chips { font-size: 8.5pt; color: #666; margin: 4pt 0 10pt 0; }
.frontmatter-chips span { display: inline-block; background: #eee; padding: 1pt 6pt; border-radius: 8pt; margin-right: 4pt; margin-bottom: 2pt; }
.note { page-break-inside: avoid; }
.toc ul { list-style: none; padding-left: 12pt; }
.toc li { margin: 3pt 0; font-size: 10pt; }
.toc .toc-cat { font-weight: 600; text-transform: uppercase; font-size: 9pt; color: #d33f6a; letter-spacing: 0.5pt; margin-top: 8pt; display: block; }
"""


def build_html(notes) -> str:
    groups = group_by_category(notes)

    # cover
    out = [
        '<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">',
        "<title>Artefactos de Guerra — wiki completa</title>",
        f"<style>{CSS}</style></head><body>",
        '<h1 class="cover-title">Artefactos de Guerra</h1>',
        '<h1 class="cover-subtitle">Wiki de investigación · '
        f'{len(notes)} notas · export offline</h1>',
    ]

    # table of contents
    out.append('<div class="toc"><h1>Índice general</h1>')
    for cat, cat_notes in groups:
        out.append(f'<span class="toc-cat">{html.escape(CATEGORY_LABELS.get(cat, cat))}</span>')
        out.append('<ul>')
        for n in cat_notes:
            out.append(f'<li>{html.escape(n["title"])}</li>')
        out.append('</ul>')
    out.append('</div>')

    # content
    for cat, cat_notes in groups:
        out.append(f'<h1 class="cat-title">{html.escape(CATEGORY_LABELS.get(cat, cat))}</h1>')
        for n in cat_notes:
            chips = []
            fm = n["frontmatter"]
            if fm.get("tipo"):
                chips.append(f'<span>{html.escape(str(fm["tipo"]))}</span>')
            if fm.get("estado"):
                chips.append(f'<span>{html.escape(str(fm["estado"]))}</span>')
            if fm.get("pais"):
                chips.append(f'<span>{html.escape(str(fm["pais"]))}</span>')
            chips_html = f'<div class="frontmatter-chips">{"".join(chips)}</div>' if chips else ""
            # strip the first H1 from body (we add our own)
            body = re.sub(r"^#\s+.+\n", "", n["body"], count=1)
            body_html = md_to_html(body)
            out.append(f'<div class="note"><h1>{html.escape(n["title"])}</h1>{chips_html}{body_html}</div>')

    out.append("</body></html>")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html", action="store_true", help="Output HTML instead of PDF")
    ap.add_argument("--output", "-o", default=None, help="Custom output path")
    args = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    notes = collect_notes()
    print(f"→ Collected {len(notes)} notes")
    html_doc = build_html(notes)

    if args.html:
        path = Path(args.output) if args.output else OUT / "artefactos-de-guerra.html"
        path.write_text(html_doc, encoding="utf-8")
        print(f"✓ HTML → {path}  ({path.stat().st_size // 1024} KB)")
        print("  Open in a browser and File → Print → Save as PDF.")
        return

    # Try PDF via weasyprint
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError:
        # Fall back to HTML
        path = OUT / "artefactos-de-guerra.html"
        path.write_text(html_doc, encoding="utf-8")
        print(f"⚠ weasyprint not installed — wrote HTML fallback at {path}")
        print("  Install weasyprint for direct PDF output:")
        print("    pip install weasyprint")
        print("  Or open the HTML file and print to PDF from your browser.")
        return

    path = Path(args.output) if args.output else OUT / "artefactos-de-guerra.pdf"
    print("→ Rendering PDF with weasyprint (this may take 30-60s)...")
    HTML(string=html_doc, base_url=str(ROOT)).write_pdf(str(path))
    print(f"✓ PDF → {path}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
