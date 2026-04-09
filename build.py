#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
Artefactos de Guerra — static site generator.

Reads every .md file under wiki/, parses frontmatter + wikilinks,
and outputs a self-contained static site in site/ with:

- One HTML page per note
- Sidebar navigation by category
- Backlinks per note
- D3 graph view of the full wiki
- Client-side search

Usage:
    python3 build.py          # build
    python3 build.py --serve  # build + serve on http://localhost:8765
"""

import os
import re
import json
import shutil
import html
import sys
from pathlib import Path

import yaml
import markdown

ROOT = Path(__file__).parent
WIKI = ROOT / "wiki"
SITE = ROOT / "site"
ASSETS = ROOT / "assets"
MEDIA = ROOT / "media"

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
PENDIENTES_HEADING_RE = re.compile(r"^##+\s+Pendientes\s*$", re.MULTILINE | re.IGNORECASE)
PENDIENTE_ITEM_RE = re.compile(r"^\s*-\s*\[\s*( |x|X)?\s*\]\s+(.+?)$", re.MULTILINE)


def _extract_pendientes_raw(body: str):
    items = []
    matches = list(PENDIENTES_HEADING_RE.finditer(body))
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        next_heading = re.search(r"^#{1,2}\s+\S", body[start:end], re.MULTILINE)
        section = body[start:start + next_heading.start()] if next_heading else body[start:end]
        for itm in PENDIENTE_ITEM_RE.finditer(section):
            done = itm.group(1) and itm.group(1).lower() == "x"
            text = itm.group(2).strip()
            items.append((bool(done), text))
    return items


def count_pendientes(body: str):
    items = _extract_pendientes_raw(body)
    total = len(items)
    done = sum(1 for d, _ in items if d)
    return done, total

YT_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:youtube\.com/(?:watch\?[^\s)\]]*?v=|shorts/|embed/)|youtu\.be/)"
    r"([A-Za-z0-9_-]{11})(?:[^\s)\]]*)"
)
AUDIO_EXT_RE = re.compile(r"\.(?:mp3|m4a|wav|ogg|aac)(?:[?#]|$)", re.IGNORECASE)

# [HH:MM:SS] or [MM:SS] or (HH:MM:SS) — bracketed or parenthesized timecodes
TC_RE = re.compile(r"(\[|\()(\d{1,2}):(\d{2})(?::(\d{2}))?(\]|\))")


def yt_extract(url):
    """Return (video_id, start_seconds or None) from a YouTube URL."""
    m = YT_URL_RE.search(url)
    if not m:
        return None, None
    vid = m.group(1)
    ts = re.search(r"[?&]t=(\d+)", url)
    start = int(ts.group(1)) if ts else None
    return vid, start


def yt_embed_html(url, width="100%"):
    vid, start = yt_extract(url)
    if not vid:
        return None
    params = f"?start={start}" if start else ""
    # Use youtube-nocookie.com (privacy-enhanced mode) — it's more permissive
    # with referrer/origin restrictions than the regular embed domain.
    return (
        f'<div class="yt-embed">'
        f'<iframe src="https://www.youtube-nocookie.com/embed/{vid}{params}" '
        f'title="YouTube video" frameborder="0" loading="lazy" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
        f'</div>'
    )


def audio_html(src_rel, up_prefix="", player_id="note-audio"):
    href = f"{up_prefix}{src_rel}"
    return (
        f'<div class="audio-wrap">'
        f'<audio id="{player_id}" controls preload="metadata" src="{href}"></audio>'
        f'<div class="audio-meta">🎧 <a href="{href}" download>Descargar</a></div>'
        f"</div>"
    )


def tc_to_seconds(h, m, s):
    if s is None:
        # [MM:SS] → treat as minutes:seconds
        return int(h) * 60 + int(m)
    return int(h) * 3600 + int(m) * 60 + int(s)


def tc_replace(m):
    open_, h, mi, s, close = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    # mismatch guard
    if (open_ == "[" and close != "]") or (open_ == "(" and close != ")"):
        return m.group(0)
    sec = tc_to_seconds(h, mi, s)
    if s is not None:
        label = f"{h}:{mi}:{s}"
    else:
        label = f"{h}:{mi}"
    return f'{open_}<a class="tc" data-t="{sec}" href="#note-audio">{label}</a>{close}'


def extract_pendientes(body: str):
    return _extract_pendientes_raw(body)


def build_pendientes_index(notes, slug_to_meta):
    by_cat = {}
    total = 0
    done = 0
    for n in notes:
        items = extract_pendientes(n["body"])
        if not items:
            continue
        for d, t in items:
            total += 1
            if d:
                done += 1
        by_cat.setdefault(n["category"], []).append((n, items))

    lines = [
        "---",
        "tipo: índice-pendientes",
        "estado: auto-generado",
        "tags: [pendientes, auto, todo]",
        "---",
        "",
        "# Pendientes — agregado automático",
        "",
        f"> **Total**: {total} ítems · **Completados**: {done} · **Por hacer**: {total - done}",
        "",
        "Esta página se regenera en cada `python3 build.py`. **No la edites a mano**: añade o marca pendientes en la sección `## Pendientes` de cada nota individual y vuelve a compilar.",
        "",
    ]

    for cat in CATEGORY_ORDER:
        if cat not in by_cat:
            continue
        cat_label = CATEGORY_LABELS.get(cat, cat)
        # count for this category
        cat_total = sum(len(items) for _, items in by_cat[cat])
        cat_done = sum(1 for _, items in by_cat[cat] for d, _ in items if d)
        lines.append(f"## {cat_label}  ·  *{cat_done}/{cat_total}*")
        lines.append("")
        for n, items in sorted(by_cat[cat], key=lambda x: x[0]["title"].lower()):
            lines.append(f"### [[{n['slug'].split('/')[-1]}|{n['title']}]]")
            for d, t in items:
                marker = "x" if d else " "
                lines.append(f"- [{marker}] {t}")
            lines.append("")
        lines.append("")

    return "\n".join(lines)


def preprocess_media(body, already_embedded=None):
    """Find any YouTube URL or audio URL in the body, keep the original line, and append an embed below it.

    `already_embedded` is an optional set/iterable of URLs or YouTube video IDs
    that were already embedded elsewhere (e.g. in the frontmatter "Fuentes"
    block) so we don't render them twice.
    """
    lines = body.split("\n")
    out = []
    seen = set()  # avoid duplicate embeds for the same URL
    seen_vids = set()  # avoid duplicate embeds for the same YouTube video id
    if already_embedded:
        for u in already_embedded:
            seen.add(u)
            vid, _ = yt_extract(u)
            if vid:
                seen_vids.add(vid)
    yt_pat = re.compile(
        r"https?://(?:www\.)?(?:youtube\.com/(?:watch\?[^\s)\]\"']*?v=[A-Za-z0-9_-]{11}"
        r"|shorts/[A-Za-z0-9_-]{11}"
        r"|embed/[A-Za-z0-9_-]{11})"
        r"|youtu\.be/[A-Za-z0-9_-]{11})"
        r"[^\s)\]\"'<>]*"
    )
    audio_pat = re.compile(r"https?://[^\s)\]\"'<>]+\.(?:mp3|m4a|wav|ogg|aac)(?:\?[^\s)\]\"'<>]*)?")

    for line in lines:
        out.append(line)
        # YouTube
        for m in yt_pat.finditer(line):
            url = m.group(0).rstrip(".,;:)]")
            if url in seen:
                continue
            vid, _ = yt_extract(url)
            if vid and vid in seen_vids:
                seen.add(url)
                continue
            seen.add(url)
            if vid:
                seen_vids.add(vid)
            emb = yt_embed_html(url)
            if emb:
                out.append("")
                out.append(emb)
                out.append("")
        # Audio files (only if not a YouTube)
        for m in audio_pat.finditer(line):
            url = m.group(0).rstrip(".,;:)]")
            if url in seen:
                continue
            seen.add(url)
            out.append("")
            out.append(f'<div class="audio-wrap"><audio controls preload="metadata" src="{url}"></audio></div>')
            out.append("")
    return "\n".join(out)


def preprocess_timecodes(body, enable):
    if not enable:
        return body
    return TC_RE.sub(tc_replace, body)


# ---------- parsing ----------

def parse_note(md_path: Path):
    raw = md_path.read_text(encoding="utf-8")
    fm = {}
    body = raw
    m = FRONTMATTER_RE.match(raw)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            fm = {}
        body = raw[m.end():]

    rel = md_path.relative_to(WIKI).as_posix()
    slug = rel[:-3]  # strip .md
    parts = rel.split("/")
    category = parts[0] if len(parts) > 1 else "_root"
    subcategory = parts[1] if len(parts) > 2 else None

    # first heading as title (fallback: filename)
    title_m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else md_path.stem

    # extract wikilinks (with optional section anchors)
    links_raw = WIKILINK_RE.findall(body)
    links = []
    for l in links_raw:
        target = l.split("|")[0].split("#")[0].strip()
        links.append(target)

    pending_done, pending_total = count_pendientes(body)
    return {
        "path": md_path,
        "rel": rel,
        "slug": slug,  # e.g. casos/roger-espanol
        "category": category,
        "subcategory": subcategory,
        "title": title,
        "frontmatter": fm,
        "body": body,
        "links_raw": links,
        "pending_done": pending_done,
        "pending_total": pending_total,
    }


def resolve_link(source_slug: str, target: str, all_slugs: set) -> str | None:
    """Resolve a wikilink target (which may be relative) to an absolute slug."""
    # Remove leading/trailing slashes
    target = target.strip("/")
    # Exact match as-is
    if target in all_slugs:
        return target

    # Relative paths: source is a slug like "casos/roger-espanol"
    source_dir = "/".join(source_slug.split("/")[:-1])
    parts = target.split("/")
    stack = source_dir.split("/") if source_dir else []
    for p in parts:
        if p == "..":
            if stack:
                stack.pop()
        elif p == ".":
            continue
        else:
            stack.append(p)
    candidate = "/".join(stack)
    if candidate in all_slugs:
        return candidate

    # Try as basename across all slugs
    base = target.split("/")[-1]
    for s in all_slugs:
        if s.endswith("/" + base) or s == base:
            return s
    return None


# ---------- rendering ----------

def md_to_html(body: str, slug: str, all_slugs: set, link_map: dict, has_audio: bool = False, already_embedded=None) -> str:
    """Convert wikilinks + media embeds + timecodes, then markdown."""
    def repl(m):
        target = m.group(1)
        label = target
        if "|" in target:
            target, label = target.split("|", 1)
        resolved = resolve_link(slug, target.split("#")[0].strip(), all_slugs)
        if resolved:
            href = relative_href(slug, resolved)
            return f'<a class="wikilink" href="{href}">{html.escape(label)}</a>'
        return f'<span class="wikilink broken" title="Broken link: {html.escape(target)}">{html.escape(label)}</span>'

    pre = WIKILINK_RE.sub(repl, body)
    pre = preprocess_media(pre, already_embedded=already_embedded)
    pre = preprocess_timecodes(pre, enable=has_audio)
    return markdown.markdown(
        pre,
        extensions=["extra", "toc", "sane_lists", "tables", "fenced_code", "md_in_html"],
    )


def relative_href(from_slug: str, to_slug: str) -> str:
    depth = from_slug.count("/")
    prefix = "../" * depth
    return f"{prefix}{to_slug}.html"


def page_template(note, content_html, sidebar_html, backlinks_html, outlinks_html, local_graph_html, audio_player_html, toc_html, all_slugs):
    title = note["title"]
    slug = note["slug"]
    depth = slug.count("/")
    up = "../" * depth

    fm = note["frontmatter"]
    meta_chips = []
    if fm.get("tipo"):
        meta_chips.append(f'<span class="chip chip-tipo">{html.escape(str(fm["tipo"]))}</span>')

    sources_html = ""
    fuentes = fm.get("fuentes") or fm.get("fuente") or []
    if isinstance(fuentes, str):
        fuentes = [fuentes]
    if fuentes:
        parts = []
        for f in fuentes:
            f_str = str(f)
            emb = yt_embed_html(f_str)
            if emb:
                parts.append(
                    f'<div class="source-item">{emb}'
                    f'<div class="source-link"><a href="{html.escape(f_str)}" target="_blank" rel="noopener">{html.escape(f_str)}</a></div>'
                    f'</div>'
                )
            elif AUDIO_EXT_RE.search(f_str):
                parts.append(
                    f'<div class="source-item"><div class="audio-wrap"><audio controls preload="metadata" src="{html.escape(f_str)}"></audio></div>'
                    f'<div class="source-link"><a href="{html.escape(f_str)}" target="_blank" rel="noopener">{html.escape(f_str)}</a></div>'
                    f'</div>'
                )
            else:
                parts.append(
                    f'<div class="source-item source-text"><a href="{html.escape(f_str)}" target="_blank" rel="noopener">{html.escape(f_str)}</a></div>'
                )
        sources_html = f'<div class="sources"><h4>Fuentes</h4>{"".join(parts)}</div>'

    breadcrumb = html.escape(note['category'])
    if note.get('subcategory'):
        breadcrumb += f" / {html.escape(note['subcategory'])}"
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Artefactos de Guerra</title>
<link rel="stylesheet" href="{up}assets/style.css">
<script>
// apply theme before paint to avoid flash
(function(){{try{{var t=localStorage.getItem('adg-theme')||'dark';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
<script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <a class="brand" href="{up}index.html">Artefactos de Guerra</a>
    <div class="search-box"><input id="search" type="search" placeholder="Buscar…" autocomplete="off"></div>
    <div class="sidebar-tools">
      <a href="{up}graph.html">Grafo</a>
      <a href="{up}timeline.html">Timeline</a>
      <a href="{up}map.html">Mapa</a>
      <button id="theme-toggle" class="theme-toggle" type="button" title="Cambiar tema">◑</button>
    </div>
    <nav class="nav">{sidebar_html}</nav>
  </aside>
  <main class="content">
    <header class="note-header">
      <div class="breadcrumb">{breadcrumb}</div>
      <h1>{html.escape(title)}</h1>
      <div class="chips">{''.join(meta_chips)}</div>
    </header>
    {audio_player_html}
    {toc_html}
    <article class="note-body">
      {content_html}
    </article>
    {sources_html}
    {local_graph_html}
    <div class="links-block">
      {outlinks_html}
      {backlinks_html}
    </div>
  </main>
</div>
<script>window.__SITE_ROOT__ = "{up}";</script>
<script src="{up}assets/site.js"></script>
</body>
</html>
"""


CATEGORY_LABELS = {
    "ferias-de-armas": "Ferias de armas",
    "empresas-de-armas": "Empresas de armas",
    "casos": "Casos",
    "usos-de-armas": "Usos de armas",
    "autores-y-referencias": "Autores y referencias",
    "herramientas": "Herramientas",
    "marco-legal": "Marco legal",
    "historia": "Historia",
    "_root": "General",
    # sub-category labels
    "feindef": "FEINDEF",
    "publicidad": "Publicidad",
    "renders": "Renders",
    "testimonios": "Testimonios",
    "entrenamientos": "Entrenamientos",
    "paul-rocher": "Paul Rocher",
    "organizaciones": "Organizaciones",
    "oftalmologa-estrella-fernandez": "Dra. Estrella Fernández",
    "empresas": "Empresas",
    "latam": "América Latina",
    "internacionales": "Internacionales",
    "bibliografia": "Bibliografía",
    "figuras-historicas": "Figuras históricas",
}

CATEGORY_ORDER = [
    "_root",                   # 0. General (índice)
    "historia",                # 1. De dónde vienen las armas
    "autores-y-referencias",   # 2. Quién analiza y documenta
    "ferias-de-armas",         # 3. Dónde se venden
    "empresas-de-armas",       # 4. Quién las fabrica
    "usos-de-armas",           # 5. Cómo se entrena su uso
    "casos",                   # 6. Las víctimas
    "marco-legal",             # 7. Qué dice la ley
    "herramientas",            # 8. Infraestructura periodística / técnica
]

# Sub-category ordering (narrativamente, no alfabético)
SUBCAT_ORDER = {
    "casos": ["internacionales", "latam", "oftalmologa-estrella-fernandez"],
    "empresas-de-armas": ["empresas", "publicidad", "renders"],
    "ferias-de-armas": ["feindef"],
    "usos-de-armas": ["entrenamientos", "testimonios"],
    "autores-y-referencias": ["paul-rocher", "figuras-historicas", "organizaciones"],
    "marco-legal": ["bibliografia"],
}
PENDIENTES_LABEL = "✓ Pendientes (auto)"


def build_toc(body: str) -> str:
    """Generate an inline collapsible TOC from h2 headings. Only if 5+ headings."""
    headings = re.findall(r"^(#{2,3})\s+(.+?)$", body, re.MULTILINE)
    if len(headings) < 5:
        return ""
    items = []
    for lvl, text in headings:
        clean = re.sub(r"[`*_]", "", text).strip()
        slug = re.sub(r"[^\w\s-]", "", clean.lower()).strip().replace(" ", "-")
        cls = "toc-h2" if len(lvl) == 2 else "toc-h3"
        items.append(f'<li class="{cls}"><a href="#{slug}">{html.escape(clean)}</a></li>')
    return f'<details class="note-toc"><summary>Contenido de esta nota</summary><ul>{"".join(items)}</ul></details>'


def _pending_chip(note):
    """Return an HTML chip showing pending items count, or empty string.
    Hide the chip when there's only 0-1 pending — only flag notes that are
    meaningfully incomplete (2+ items)."""
    total = note.get("pending_total", 0)
    if total == 0:
        return ""
    done = note.get("pending_done", 0)
    left = total - done
    if left == 0:
        return ""  # don't clutter sidebar with ✓ chips
    if left < 2:
        return ""  # single pending items are noise
    return f' <span class="nav-chip" title="{left} tareas pendientes en esta nota (sección ## Pendientes)">☐ {left}</span>'


def group_notes(notes):
    """Return nested dict: cat -> {'_direct': [...], subcat: [...], ...}."""
    tree = {}
    for n in notes:
        cat = n["category"]
        tree.setdefault(cat, {"_direct": {}})
        if n["subcategory"]:
            tree[cat].setdefault(n["subcategory"], []).append(n)
        else:
            tree[cat]["_direct"].setdefault("_direct", []).append(n)
    return tree


def build_sidebar(tree):
    parts = []
    for cat in CATEGORY_ORDER:
        if cat not in tree:
            continue
        label = CATEGORY_LABELS.get(cat, cat)
        parts.append(f'<details open class="nav-group"><summary>{html.escape(label)}</summary>')

        # direct notes (no subcategory)
        direct = tree[cat].get("_direct", {}).get("_direct", [])
        if direct:
            parts.append('<ul class="nav-direct">')
            for n in sorted(direct, key=lambda x: x["title"].lower()):
                parts.append(
                    f'<li><a data-slug="{n["slug"]}" href="__SLUG__{n["slug"]}.html">{html.escape(n["title"])}{_pending_chip(n)}</a></li>'
                )
            parts.append("</ul>")

        # subcategories — narrative order if defined, else alphabetical
        subs = [k for k in tree[cat].keys() if k != "_direct"]
        preferred = SUBCAT_ORDER.get(cat, [])
        subs = [s for s in preferred if s in subs] + sorted([s for s in subs if s not in preferred])
        for sub in subs:
            sub_label = CATEGORY_LABELS.get(sub, sub)
            parts.append(f'<details open class="nav-subgroup"><summary>{html.escape(sub_label)}</summary><ul>')
            for n in sorted(tree[cat][sub], key=lambda x: x["title"].lower()):
                parts.append(
                    f'<li><a data-slug="{n["slug"]}" href="__SLUG__{n["slug"]}.html">{html.escape(n["title"])}{_pending_chip(n)}</a></li>'
                )
            parts.append("</ul></details>")

        parts.append("</details>")
    return "\n".join(parts)


# ---------- graph ----------

def build_graph_data(notes, link_map):
    # degree
    degree = {n["slug"]: 0 for n in notes}
    edges = []
    for src, targets in link_map.items():
        for t in targets:
            if src == t:
                continue
            edges.append({"source": src, "target": t})
            degree[src] = degree.get(src, 0) + 1
            degree[t] = degree.get(t, 0) + 1

    nodes = []
    for n in notes:
        nodes.append({
            "id": n["slug"],
            "title": n["title"],
            "category": n["category"],
            "subcategory": n["subcategory"] or "",
            "estado": n["frontmatter"].get("estado", ""),
            "degree": degree.get(n["slug"], 0),
        })
    return {"nodes": nodes, "edges": edges}


def build_local_graph_data(slug, notes, link_map, backlink_map, slug_to_meta):
    """Subgraph: slug + all its 1-hop neighbors."""
    out = link_map.get(slug, [])
    inc = backlink_map.get(slug, [])
    neighbor_ids = set(out) | set(inc) | {slug}

    nodes = []
    for s in neighbor_ids:
        meta = slug_to_meta.get(s, {})
        nodes.append({
            "id": s,
            "title": meta.get("title", s),
            "category": meta.get("category", ""),
            "is_center": s == slug,
        })
    edges = []
    for t in out:
        if t in neighbor_ids:
            edges.append({"source": slug, "target": t, "direction": "out"})
    for src in inc:
        if src in neighbor_ids:
            edges.append({"source": src, "target": slug, "direction": "in"})
    return {"nodes": nodes, "edges": edges}


GRAPH_JS_TEMPLATE = r"""
const data = __DATA__;
const CAT_LABELS = __CAT_LABELS__;

const width = window.innerWidth;
const height = window.innerHeight - 60;

const svg = d3.select('#graph').append('svg')
  .attr('width', width).attr('height', height);

// arrow marker (themed via CSS)
svg.append('defs').append('marker')
  .attr('id', 'arrow').attr('viewBox', '0 -5 10 10')
  .attr('refX', 20).attr('refY', 0)
  .attr('markerWidth', 6).attr('markerHeight', 6)
  .attr('orient', 'auto')
  .append('path').attr('d', 'M0,-4 L10,0 L0,4').attr('class', 'arrow-path');

svg.append('defs').append('marker')
  .attr('id', 'arrow-hot').attr('viewBox', '0 -5 10 10')
  .attr('refX', 20).attr('refY', 0)
  .attr('markerWidth', 7).attr('markerHeight', 7)
  .attr('orient', 'auto')
  .append('path').attr('d', 'M0,-4 L10,0 L0,4').attr('class', 'arrow-path-hot');

const g = svg.append('g');
const zoomBehavior = d3.zoom().scaleExtent([0.15, 4]).on('zoom', (e) => g.attr('transform', e.transform));
svg.call(zoomBehavior);

// background click = clear focus
svg.on('click', (e) => { if (e.target.tagName === 'svg') clearFocus(); });

// High-contrast palette ordered to match CATEGORY_ORDER
const PALETTE = {
  'ferias-de-armas':      '#e05d3d',
  'empresas-de-armas':    '#f0a94a',
  'casos':                '#d33f6a',
  'usos-de-armas':        '#6eb8d6',
  'autores-y-referencias':'#f5d05e',
  'herramientas':         '#46d4c6',
  'marco-legal':          '#a78bfa',
  'historia':             '#5fd49e',
  '_root':                '#aaaaaa',
};
const categories = [...new Set(data.nodes.map(n => n.category))];
const color = (c) => PALETTE[c] || '#999';

const links = data.edges.map(d => Object.assign({}, d));
const nodes = data.nodes.map(d => Object.assign({}, d));

// neighbors index
const neighbors = {};
nodes.forEach(n => neighbors[n.id] = new Set([n.id]));
links.forEach(l => {
  neighbors[l.source].add(l.target);
  neighbors[l.target].add(l.source);
});

// hidden categories (legend filter)
const hiddenCats = new Set();

const sim = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(d => 90 + 8 * Math.log(1 + (d.source.degree||0) + (d.target.degree||0))))
  .force('charge', d3.forceManyBody().strength(-300))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collide', d3.forceCollide().radius(d => 14 + Math.sqrt(d.degree) * 3))
  .force('x', d3.forceX(width / 2).strength(0.03))
  .force('y', d3.forceY(height / 2).strength(0.03));

const link = g.append('g').attr('class', 'links').selectAll('line')
  .data(links).enter().append('line')
  .attr('stroke-width', 1.2)
  .attr('marker-end', 'url(#arrow)');

const node = g.append('g').attr('class', 'nodes').selectAll('g')
  .data(nodes).enter().append('g')
  .attr('class', 'node')
  .call(d3.drag()
    .on('start', (event, d) => { if (!event.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on('drag',  (event, d) => { d.fx = event.x; d.fy = event.y; })
    .on('end',   (event, d) => { if (!event.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));

node.append('circle')
  .attr('r', d => 7 + Math.sqrt(d.degree) * 2.5)
  .attr('fill', d => color(d.category))
  .attr('class', 'g-node-circle')
  .attr('stroke-width', 1.8)
  .attr('stroke-dasharray', d => d.estado === 'stub' ? '2 2' : null);

node.append('text')
  .attr('x', d => 9 + Math.sqrt(d.degree) * 2.5)
  .attr('y', 4)
  .attr('class', 'g-node-label')
  .attr('font-size', '11px')
  .attr('pointer-events', 'none')
  .text(d => d.title);

node.append('title').text(d => d.title + ' — ' + (CAT_LABELS[d.category] || d.category) + ' · ' + d.degree + ' conexiones');

let focused = null;
node.on('mouseover', (e, d) => { if (!focused) highlight(d.id); })
    .on('mouseout',  () => { if (!focused) clearHighlight(); })
    .on('click',     (e, d) => { e.stopPropagation(); focused = (focused === d.id ? null : d.id); if (focused) highlight(focused); else clearHighlight(); })
    .on('dblclick',  (e, d) => { e.stopPropagation(); window.location.href = d.id + '.html'; });

function highlight(id) {
  node.classed('dim', n => !neighbors[id].has(n.id))
      .classed('highlight', n => n.id === id);
  link.classed('dim', l => l.source.id !== id && l.target.id !== id)
      .classed('highlight', l => l.source.id === id || l.target.id === id)
      .attr('marker-end', l => (l.source.id === id || l.target.id === id) ? 'url(#arrow-hot)' : 'url(#arrow)');
}
function clearHighlight() {
  node.classed('dim', false).classed('highlight', false);
  link.classed('dim', false).classed('highlight', false)
      .attr('marker-end', 'url(#arrow)');
}
function clearFocus() { focused = null; clearHighlight(); }

function applyCategoryFilter() {
  node.style('display', n => hiddenCats.has(n.category) ? 'none' : null);
  link.style('display', l => {
    const hideSrc = hiddenCats.has(l.source.category);
    const hideTgt = hiddenCats.has(l.target.category);
    return (hideSrc || hideTgt) ? 'none' : null;
  });
}

sim.on('tick', () => {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
});

// clickable legend
const legendEl = document.getElementById('graph-legend');
const orderedCats = ['ferias-de-armas','empresas-de-armas','casos','usos-de-armas','autores-y-referencias','herramientas','marco-legal','historia'];
orderedCats.filter(c => categories.includes(c)).forEach(c => {
  const btn = document.createElement('button');
  btn.className = 'legend-btn';
  btn.innerHTML = '<span class="swatch" style="background:' + color(c) + '"></span>' + (CAT_LABELS[c] || c);
  btn.onclick = () => {
    if (hiddenCats.has(c)) { hiddenCats.delete(c); btn.classList.remove('off'); }
    else { hiddenCats.add(c); btn.classList.add('off'); }
    applyCategoryFilter();
  };
  legendEl.appendChild(btn);
});

// reset button
document.getElementById('graph-reset').onclick = () => {
  hiddenCats.clear();
  document.querySelectorAll('.legend-btn').forEach(b => b.classList.remove('off'));
  applyCategoryFilter();
  clearFocus();
  sim.alpha(0.8).restart();
};

// search input — highlights + centers matching nodes
const searchInput = document.getElementById('graph-search');
const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
function applySearchHighlight(query) {
  const q = norm((query || '').trim());
  if (!q) {
    node.classed('g-match', false).classed('g-search-dim', false);
    link.classed('g-search-dim', false);
    return;
  }
  const matches = new Set();
  nodes.forEach(n => {
    if (norm(n.title).includes(q) || norm(n.id).includes(q)) matches.add(n.id);
  });
  node.classed('g-match', d => matches.has(d.id))
      .classed('g-search-dim', d => !matches.has(d.id));
  link.classed('g-search-dim', l => !matches.has(l.source.id) && !matches.has(l.target.id));
  // center on first match
  if (matches.size > 0) {
    const firstId = matches.values().next().value;
    const first = nodes.find(n => n.id === firstId);
    if (first && first.x !== undefined) {
      const scale = 1.4;
      const tx = width / 2 - first.x * scale;
      const ty = height / 2 - first.y * scale;
      svg.transition().duration(500).call(
        zoomBehavior.transform,
        d3.zoomIdentity.translate(tx, ty).scale(scale)
      );
    }
  }
}
searchInput.addEventListener('input', (e) => applySearchHighlight(e.target.value));
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    searchInput.value = '';
    applySearchHighlight('');
  }
});
"""


TIMELINE_YEAR_RE = re.compile(
    r"^###\s+(?:(\d{4})(?:-(\d{4}))?|(\d{4}s)(?:-(\d{4}s))?|(?:Siglo\s+\w+|Años\s+\d+s?|\d{4}s|Principios.*?|Mediados.*?|Finales.*?|\w+\s+\d{4}|\d{1,2}\s+\w+\s+\d{4}))\s*(.*?)$",
    re.MULTILINE | re.IGNORECASE,
)


def parse_cronologia_entries(body: str):
    """Extract every ### heading from cronologia-completa.md body + the paragraph(s) after it until next heading."""
    entries = []
    # find all headings level 2 and 3
    pattern = re.compile(r"^(##+)\s+(.+?)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    for i, m in enumerate(matches):
        level = len(m.group(1))
        text = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        # era heading (##) vs entry (###)
        if level == 2:
            entries.append({"type": "era", "title": text})
        elif level == 3:
            # try to extract year/date from the start of the title
            year_m = re.match(r"^(?:(\d{4})(?:-(\d{4}))?|(\w+\s+\d{4})|(\d{1,2}\s+\w+\s+\d{4}))", text)
            year = ""
            if year_m:
                groups = [g for g in year_m.groups() if g]
                year = groups[0] if groups else ""
            entries.append({
                "type": "entry",
                "title": text,
                "year": year,
                "content": content,
            })
    return entries


def era_color(era_title: str) -> str:
    """Return a background color for each era."""
    title = era_title.lower()
    if "xix" in title or "orígenes" in title or "origenes" in title:
        return "#8b5a2b"  # ochre — colonial
    if "1900-1945" in title or "guerras mundiales" in title:
        return "#6b4423"  # dark ochre — world wars
    if "1945-1990" in title or "guerra fría" in title or "guerra fria" in title:
        return "#a03c2e"  # red — cold war
    if "años 90" in title or "neoliberal" in title:
        return "#cc5c3c"  # orange — neoliberal
    if "siglo xxi" in title or "paradigma" in title:
        return "#e05d3d"  # accent — modern
    return "#666"


def render_cronologia_content(content: str) -> str:
    """Convert basic markdown in a timeline entry to HTML."""
    # remove wikilink brackets (already resolved link format)
    content = re.sub(r"\[\[([^\|\]]+)\|([^\]]+)\]\]", r"\2", content)
    content = re.sub(r"\[\[([^\]]+)\]\]", r"\1", content)
    # bold
    content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
    # italics
    content = re.sub(r"\*(.+?)\*", r"<em>\1</em>", content)
    # blockquote
    lines = []
    for line in content.split("\n"):
        if line.startswith("> "):
            lines.append(f'<blockquote>{html.escape(line[2:])}</blockquote>')
        elif line.strip().startswith("- "):
            lines.append(f'<li>{line.strip()[2:]}</li>')
        elif line.strip():
            lines.append(f'<p>{line}</p>')
        else:
            lines.append("")
    out = "\n".join(lines)
    # wrap consecutive <li> in <ul>
    out = re.sub(r"((?:<li>.*?</li>\n?)+)", r"<ul>\1</ul>", out, flags=re.DOTALL)
    return out


def timeline_page_html(crono_note, all_slugs, link_map):
    entries = parse_cronologia_entries(crono_note["body"])
    items_html = []
    current_era_color = "#666"
    for e in entries:
        if e["type"] == "era":
            color = era_color(e["title"])
            current_era_color = color
            items_html.append(
                f'<div class="tl-era" style="--era-color: {color}"><h2>{html.escape(e["title"])}</h2></div>'
            )
        else:
            year = e.get("year", "")
            title_text = e["title"]
            # strip the leading year from the title display if repeated
            content_html = render_cronologia_content(e["content"])
            items_html.append(
                f'<article class="tl-item" style="--era-color: {current_era_color}">'
                f'<div class="tl-dot"></div>'
                f'<div class="tl-year">{html.escape(year)}</div>'
                f'<div class="tl-card">'
                f'<h3>{html.escape(title_text)}</h3>'
                f'<div class="tl-content">{content_html}</div>'
                f'</div>'
                f'</article>'
            )
    body = "\n".join(items_html)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cronología visual — Artefactos de Guerra</title>
<link rel="stylesheet" href="assets/style.css">
<script>
(function(){{try{{var t=localStorage.getItem('adg-theme')||'dark';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>
<body class="timeline-page">
<header class="timeline-header">
  <a class="brand" href="index.html">◂ Artefactos de Guerra</a>
  <span class="tl-subtitle">Cronología visual · 1850 → 2026</span>
  <div class="timeline-actions">
    <button id="theme-toggle" class="theme-toggle" type="button" title="Cambiar tema">◐ Tema</button>
    <a class="graph-link" href="historia/cronologia-completa.html">Versión texto →</a>
  </div>
</header>
<main class="timeline-main">
  <div class="timeline-rail"></div>
  {body}
</main>
<script src="assets/site.js"></script>
</body>
</html>
"""


# Country positions [lng, lat] for the world map (curated)
COUNTRY_DATA = [
    # España
    {"slug": "casos/inigo-cabacas", "title": "Iñigo Cabacas (Bilbao 2012)", "country": "España", "lng": -2.9253, "lat": 43.2630, "type": "muerto", "year": 2012},
    {"slug": "casos/ester-quintana", "title": "Ester Quintana (Barcelona 2012)", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "ojo", "year": 2012},
    {"slug": "casos/juan-andres-benitez", "title": "Juan Andrés Benítez (Raval 2013)", "country": "España", "lng": 2.1700, "lat": 41.3793, "type": "muerto", "year": 2013},
    {"slug": "casos/roger-espanol", "title": "Roger Español (1-O 2017)", "country": "España", "lng": 2.1850, "lat": 41.4030, "type": "ojo", "year": 2017},
    {"slug": "casos/africa-pablo-hasel", "title": "África (Pablo Hasél 2021)", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "ojo", "year": 2021},
    {"slug": "casos/olga-proces", "title": "Olga (Procés 2019)", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "lesion", "year": 2019},
    {"slug": "casos/antonio-c-badalona", "title": "Antonio C. (Badalona 2021, taser)", "country": "España", "lng": 2.2454, "lat": 41.4500, "type": "muerto", "year": 2021},
    {"slug": "casos/carles-guillot", "title": "Carles Guillot", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "ojo", "year": 2010},
    {"slug": "casos/tarajal-2014", "title": "Tarajal — 14 muertos (2014)", "country": "España", "lng": -5.3625, "lat": 35.8894, "type": "masacre", "year": 2014},
    {"slug": "casos/roger-garcia-foam-2019", "title": "Roger García (Proces 2019, foam)", "country": "España", "lng": 2.1750, "lat": 41.3880, "type": "ojo", "year": 2019},
    {"slug": "casos/abdelillah-foam-2019", "title": "Abdelillah (Proces 2019, foam)", "country": "España", "lng": 2.1780, "lat": 41.3860, "type": "ojo", "year": 2019},
    {"slug": "casos/melilla-2022", "title": "Melilla — 37 muertos (2022)", "country": "España", "lng": -2.9381, "lat": 35.2923, "type": "masacre", "year": 2022},
    # Francia
    {"slug": "casos/remi-fraisse", "title": "Rémi Fraisse (Sivens 2014)", "country": "Francia", "lng": 1.8, "lat": 43.9, "type": "muerto", "year": 2014},
    {"slug": "casos/steve-maia-canico", "title": "Steve Maia Caniço (Nantes 2019)", "country": "Francia", "lng": -1.5536, "lat": 47.2184, "type": "muerto", "year": 2019},
    # UK
    {"slug": "casos/stephen-geddis", "title": "Stephen Geddis (Belfast 1975)", "country": "Reino Unido", "lng": -5.9301, "lat": 54.5973, "type": "muerto", "year": 1975},
    {"slug": "casos/rodney-king-1991", "title": "Rodney King (Los Ángeles 1991)", "country": "Estados Unidos", "lng": -118.2437, "lat": 34.0522, "type": "lesion", "year": 1991},
    # LATAM
    {"slug": "casos/fabiola-campillai", "title": "Fabiola Campillai (Chile 2019)", "country": "Chile", "lng": -70.6483, "lat": -33.4489, "type": "ceguera", "year": 2019},
    {"slug": "casos/latam/chile-estallido-2019", "title": "Chile estallido 2019 — 460+ ojos", "country": "Chile", "lng": -70.6483, "lat": -33.4489, "type": "masacre", "year": 2019},
    {"slug": "casos/rufo-chacon", "title": "Rufo Chacón (Venezuela 2019)", "country": "Venezuela", "lng": -72.2225, "lat": 7.7669, "type": "ceguera", "year": 2019},
    {"slug": "casos/juan-pablo-pernalete", "title": "Juan Pablo Pernalete (Caracas 2017)", "country": "Venezuela", "lng": -66.9036, "lat": 10.4806, "type": "muerto", "year": 2017},
    {"slug": "casos/latam/venezuela-2017-2019", "title": "Venezuela 2017-2019 — 248 muertos", "country": "Venezuela", "lng": -66.9036, "lat": 10.4806, "type": "masacre", "year": 2018},
    {"slug": "casos/latam/bolivia-2019", "title": "Bolivia 2019 — 37 muertos", "country": "Bolivia", "lng": -68.1500, "lat": -16.5000, "type": "masacre", "year": 2019},
    {"slug": "casos/latam/colombia-2021", "title": "Colombia Paro Nacional 2021", "country": "Colombia", "lng": -76.6044, "lat": 2.4448, "type": "masacre", "year": 2021},
    {"slug": "casos/latam/ecuador-2019", "title": "Ecuador Octubre 2019", "country": "Ecuador", "lng": -78.4678, "lat": -0.1807, "type": "masacre", "year": 2019},
    {"slug": "casos/latam/peru-2020", "title": "Perú Anti-Merino 2020", "country": "Perú", "lng": -77.0428, "lat": -12.0464, "type": "masacre", "year": 2020},
    {"slug": "casos/latam/guatemala-2020", "title": "Guatemala Noviembre 2020", "country": "Guatemala", "lng": -90.5069, "lat": 14.6349, "type": "masacre", "year": 2020},
    {"slug": "casos/latam/brasil-2017-2021", "title": "Brasil 2017-2021 (Recife)", "country": "Brasil", "lng": -34.8770, "lat": -8.0476, "type": "masacre", "year": 2021},
    {"slug": "casos/latam/mexico-feminista-2020", "title": "México marchas feministas", "country": "México", "lng": -99.1332, "lat": 19.4326, "type": "lesion", "year": 2020},
    {"slug": "casos/latam/ee-uu-frontera-sur", "title": "EE.UU. Frontera sur (compilación 2018-2024)", "country": "Estados Unidos", "lng": -117.0300, "lat": 32.5200, "type": "masacre", "year": 2020},
    {"slug": "casos/latam/maria-meza-tijuana-2018", "title": "María Meza — Tijuana, 25 nov 2018", "country": "México", "lng": -117.0382, "lat": 32.5149, "type": "lesion", "year": 2018},
    # Internacional
    {"slug": "casos/internacionales/endsars-nigeria-2020", "title": "EndSARS Nigeria (Lekki 2020)", "country": "Nigeria", "lng": 3.4500, "lat": 6.4500, "type": "masacre", "year": 2020},
    {"slug": "casos/internacionales/hong-kong-2019-2020", "title": "Hong Kong 2019-2020", "country": "Hong Kong", "lng": 114.1694, "lat": 22.3193, "type": "masacre", "year": 2019},
    {"slug": "casos/internacionales/myanmar-2021", "title": "Myanmar Golpe 2021 — +1500 muertos", "country": "Myanmar", "lng": 96.0785, "lat": 21.9162, "type": "masacre", "year": 2021},
    {"slug": "casos/internacionales/sri-lanka-2022", "title": "Sri Lanka Aragalaya 2022", "country": "Sri Lanka", "lng": 79.8612, "lat": 6.9271, "type": "masacre", "year": 2022},
    {"slug": "casos/internacionales/iran-mahsa-amini-2022", "title": "Irán «Mujer Vida Libertad» 2022 — Mahsa Amini", "country": "Irán", "lng": 51.3890, "lat": 35.6892, "type": "masacre", "year": 2022},
    {"slug": "casos/internacionales/bangladesh-2024", "title": "Bangladesh — Revolución de Julio 2024 — +1000 muertos", "country": "Bangladesh", "lng": 90.4125, "lat": 23.8103, "type": "masacre", "year": 2024},
    {"slug": "casos/internacionales/nepal-gen-z-2024", "title": "Nepal Gen Z 2024", "country": "Nepal", "lng": 85.3240, "lat": 27.7172, "type": "masacre", "year": 2024},
    {"slug": "casos/internacionales/palestina-2023-2024", "title": "Palestina — Cisjordania 2023-2024", "country": "Palestina", "lng": 35.2137, "lat": 31.7683, "type": "masacre", "year": 2023},
    {"slug": "casos/internacionales/egipto-tahrir-2011", "title": "Egipto — Plaza Tahrir 2011", "country": "Egipto", "lng": 31.2357, "lat": 30.0444, "type": "masacre", "year": 2011},
    {"slug": "casos/internacionales/libano-thawra-2019", "title": "Líbano — Thawra 2019", "country": "Líbano", "lng": 35.5018, "lat": 33.8938, "type": "masacre", "year": 2019},
    {"slug": "casos/internacionales/irak-tishreen-2019", "title": "Irak — Tishreen 2019 (+600 muertos)", "country": "Irak", "lng": 44.3661, "lat": 33.3152, "type": "masacre", "year": 2019},
    {"slug": "casos/internacionales/bahrein-2011", "title": "Bahréin 2011 — 34+ muertos por gas (PHR)", "country": "Bahréin", "lng": 50.5577, "lat": 26.0667, "type": "masacre", "year": 2011},
    {"slug": "casos/internacionales/tunez-2011", "title": "Túnez 2011 — Revolución del Jazmín", "country": "Túnez", "lng": 10.1815, "lat": 36.8065, "type": "masacre", "year": 2011},
    {"slug": "casos/internacionales/libia-2011", "title": "Libia 2011 — Bengasi / guerra civil", "country": "Libia", "lng": 20.0685, "lat": 32.1167, "type": "masacre", "year": 2011},
    {"slug": "casos/internacionales/siria-2011", "title": "Siria 2011 — Daraa / guerra civil", "country": "Siria", "lng": 36.1044, "lat": 32.6189, "type": "masacre", "year": 2011},
    {"slug": "casos/internacionales/yemen-2011-presente", "title": "Yemen 2011-presente — +377.000 muertos", "country": "Yemen", "lng": 44.2067, "lat": 15.3694, "type": "masacre", "year": 2015},
    {"slug": "casos/internacionales/ucrania-2022-presente", "title": "Ucrania 2022-presente — campo de prueba global", "country": "Ucrania", "lng": 30.5234, "lat": 50.4501, "type": "masacre", "year": 2022},
    {"slug": "casos/internacionales/chile-1973-pinochet", "title": "Chile 1973-1990 — dictadura de Pinochet", "country": "Chile", "lng": -70.6693, "lat": -33.4489, "type": "masacre", "year": 1973},
    {"slug": "casos/internacionales/argentina-1976-dictadura", "title": "Argentina 1976-1983 — dictadura militar", "country": "Argentina", "lng": -58.3816, "lat": -34.6037, "type": "masacre", "year": 1976},
]

MAP_PAGE_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mapa mundial — Artefactos de Guerra</title>
<link rel="stylesheet" href="assets/style.css">
<script>
(function(){try{var t=localStorage.getItem('adg-theme')||'dark';document.documentElement.setAttribute('data-theme',t);}catch(e){}})();
</script>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
</head>
<body class="map-page">
<header class="map-header">
  <a class="brand" href="index.html">◂ Artefactos de Guerra</a>
  <span class="map-subtitle">Mapa mundial de casos documentados</span>
  <div class="map-actions">
    <button id="theme-toggle" class="theme-toggle" type="button" title="Cambiar tema">◐ Tema</button>
  </div>
</header>
<aside class="map-legend">
  <h4>Tipo de caso</h4>
  <ul>
    <li><span class="dot dot-muerto"></span> Muerto/a</li>
    <li><span class="dot dot-masacre"></span> Masacre / múltiples víctimas</li>
    <li><span class="dot dot-ceguera"></span> Ceguera total</li>
    <li><span class="dot dot-ojo"></span> Pérdida de un ojo</li>
    <li><span class="dot dot-lesion"></span> Otra lesión</li>
  </ul>
  <p class="map-help">
    <b>Hover</b> · ver datos<br>
    <b>Click</b> · abrir nota<br>
    <b>Rueda</b> · zoom
  </p>
</aside>
<div id="map-container"></div>
<script>
const cases = __CASES__;

const width = window.innerWidth;
const height = window.innerHeight - 60;

const svg = d3.select('#map-container').append('svg')
  .attr('width', width).attr('height', height);

const g = svg.append('g');
svg.call(d3.zoom().scaleExtent([1, 8]).on('zoom', e => g.attr('transform', e.transform)));

const projection = d3.geoNaturalEarth1()
  .scale(width / 6.5)
  .translate([width / 2, height / 2 + 20]);
const path = d3.geoPath(projection);

// Load world topojson
d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json').then(world => {
  const countries = topojson.feature(world, world.objects.countries);
  g.append('g').attr('class', 'countries')
    .selectAll('path').data(countries.features).enter().append('path')
    .attr('d', path)
    .attr('class', 'country');

  // Plot cases
  const colors = {
    muerto: '#d33f6a',
    masacre: '#e05d3d',
    ceguera: '#a78bfa',
    ojo: '#f0a94a',
    lesion: '#6eb8d6'
  };

  const points = g.append('g').attr('class', 'points').selectAll('g')
    .data(cases).enter().append('g')
    .attr('transform', d => {
      const p = projection([d.lng, d.lat]);
      return p ? `translate(${p[0]},${p[1]})` : null;
    })
    .style('cursor', 'pointer')
    .on('mouseover', function(e, d) {
      d3.select(this).select('circle').transition().duration(120).attr('r', 9);
      tooltip.style.display = 'block';
      tooltip.innerHTML = `<strong>${d.title}</strong><br><span class="tt-country">${d.country} · ${d.year}</span>`;
    })
    .on('mousemove', function(e) {
      tooltip.style.left = (e.pageX + 14) + 'px';
      tooltip.style.top = (e.pageY + 14) + 'px';
    })
    .on('mouseout', function() {
      d3.select(this).select('circle').transition().duration(120).attr('r', 6);
      tooltip.style.display = 'none';
    })
    .on('click', (e, d) => { window.location.href = d.slug + '.html'; });

  points.append('circle')
    .attr('r', 6)
    .attr('fill', d => colors[d.type] || '#999')
    .attr('stroke', '#0b0b0e').attr('stroke-width', 1.5);
});

// tooltip element
const tooltip = document.createElement('div');
tooltip.id = 'map-tooltip';
document.body.appendChild(tooltip);
</script>
</body>
</html>
"""


def map_page_html(notes):
    cases_json = json.dumps(COUNTRY_DATA, ensure_ascii=False)
    return MAP_PAGE_TEMPLATE.replace("__CASES__", cases_json)


def graph_page_html(graph_data):
    cat_labels_js = json.dumps({k: v for k, v in CATEGORY_LABELS.items()}, ensure_ascii=False)
    data_json = json.dumps(graph_data, ensure_ascii=False)
    js = GRAPH_JS_TEMPLATE.replace("__DATA__", data_json).replace("__CAT_LABELS__", cat_labels_js)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Grafo — Artefactos de Guerra</title>
<link rel="stylesheet" href="assets/style.css">
<script>
(function(){{try{{var t=localStorage.getItem('adg-theme')||'dark';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
<script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body class="graph-page">
<header class="graph-header">
  <a class="brand" href="index.html">◂ Artefactos de Guerra</a>
  <span class="graph-title">Grafo de conexiones</span>
  <div class="graph-actions">
    <input id="graph-search" type="search" placeholder="Buscar nodo…" autocomplete="off" spellcheck="false">
    <button id="graph-reset" title="Reset">↺ Reset</button>
    <button id="theme-toggle" class="theme-toggle" type="button" title="Cambiar tema">◐ Tema</button>
  </div>
</header>
<aside class="graph-panel">
  <h4>Categorías</h4>
  <div id="graph-legend"></div>
  <p class="graph-help">
    <b>Hover</b> un nodo → resalta sus vecinos.<br>
    <b>Click</b> → fija el foco.<br>
    <b>Doble click</b> → abre la nota.<br>
    <b>Drag</b> → mover. <b>Rueda</b> → zoom.<br>
    <b>Click en leyenda</b> → ocultar categoría.
  </p>
</aside>
<div id="graph"></div>
<script>{js}</script>
<script>
(function(){{
  var btn = document.getElementById('theme-toggle');
  if (!btn) return;
  btn.addEventListener('click', function(){{
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    var nxt = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nxt);
    try {{ localStorage.setItem('adg-theme', nxt); }} catch (e) {{}}
  }});
}})();
</script>
</body>
</html>
"""


LOCAL_GRAPH_JS_TEMPLATE = r"""
(function(){
const data = __DATA__;
const el = document.getElementById('local-graph');
if (!el || !data.nodes.length) return;
const width = el.clientWidth;
const height = 280;

const PALETTE = {
  'ferias-de-armas':      '#e05d3d',
  'empresas-de-armas':    '#f0a94a',
  'casos':                '#d33f6a',
  'usos-de-armas':        '#6eb8d6',
  'autores-y-referencias':'#f5d05e',
  'herramientas':         '#46d4c6',
  'marco-legal':          '#a78bfa',
  'historia':             '#5fd49e',
  '_root':                '#aaaaaa',
};
const color = c => PALETTE[c] || '#999';

const svg = d3.select(el).append('svg').attr('width', width).attr('height', height);
svg.append('defs').append('marker')
  .attr('id', 'lg-arrow').attr('viewBox', '0 -5 10 10')
  .attr('refX', 16).attr('refY', 0).attr('markerWidth', 5).attr('markerHeight', 5).attr('orient', 'auto')
  .append('path').attr('d', 'M0,-4 L10,0 L0,4').attr('class', 'lg-arrow-path');

const nodes = data.nodes.map(d => Object.assign({}, d));
const links = data.edges.map(d => Object.assign({}, d));

const sim = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(95))
  .force('charge', d3.forceManyBody().strength(-300))
  .force('center', d3.forceCenter(width/2, height/2))
  .force('collide', d3.forceCollide().radius(40));

const link = svg.append('g').selectAll('line').data(links).enter().append('line')
  .attr('class', 'lg-link')
  .attr('marker-end', 'url(#lg-arrow)');

// drag behavior — works alongside click via defaultPrevented check
const drag = d3.drag()
  .on('start', (event, d) => { if (!event.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
  .on('drag',  (event, d) => { d.fx = event.x; d.fy = event.y; })
  .on('end',   (event, d) => { if (!event.active) sim.alphaTarget(0); /* keep fixed */ });

const node = svg.append('g').selectAll('g').data(nodes).enter().append('g')
  .attr('class', 'lg-node')
  .style('cursor', 'pointer')
  .call(drag)
  .on('click', (e, d) => {
    if (e.defaultPrevented) return;
    if (!d.is_center) window.location.href = '__UP__' + d.id + '.html';
  });

node.append('circle')
  .attr('r', d => d.is_center ? 11 : 7)
  .attr('fill', d => color(d.category))
  .attr('class', d => d.is_center ? 'lg-circle lg-circle-center' : 'lg-circle')
  .attr('stroke-width', d => d.is_center ? 3 : 1.5);

node.append('text')
  .attr('x', d => (d.is_center ? 15 : 11))
  .attr('y', 4)
  .attr('class', 'lg-label')
  .attr('font-size', '11px')
  .text(d => d.title.length > 40 ? d.title.slice(0, 38) + '…' : d.title);

node.append('title').text(d => d.title);

sim.on('tick', () => {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
});
})();
"""


def local_graph_script(slug, notes, link_map, backlink_map, slug_to_meta):
    data = build_local_graph_data(slug, notes, link_map, backlink_map, slug_to_meta)
    if not data["edges"]:
        return ""
    depth = slug.count("/")
    up = "../" * depth
    data_json = json.dumps(data, ensure_ascii=False)
    js = LOCAL_GRAPH_JS_TEMPLATE.replace("__DATA__", data_json).replace("__UP__", up)
    return f'<div class="local-graph-wrap"><h4>Red local</h4><div class="lg-hint">Arrastra para reorganizar · Click en un vecino para navegar</div><div id="local-graph"></div></div><script>{js}</script>'


# ---------- search index ----------

def build_search_index(notes):
    idx = []
    for n in notes:
        plain = re.sub(r"[#*_`>\[\]()]", "", n["body"])
        plain = re.sub(r"\s+", " ", plain).strip()[:600]
        idx.append({
            "slug": n["slug"],
            "title": n["title"],
            "category": n["category"],
            "snippet": plain,
        })
    return idx


# ---------- index page ----------

def index_page(tree, notes, sidebar_html):
    # Total pending items across the wiki
    total_pending = sum(n.get("pending_total", 0) - n.get("pending_done", 0) for n in notes)
    total_casos = sum(1 for n in notes if n["category"] == "casos")
    total_empresas = sum(1 for n in notes if n["category"] == "empresas-de-armas")
    stats = {
        "total": len(notes),
        "categorias": len(tree),
        "pendientes": total_pending,
        "casos": total_casos,
        "empresas": total_empresas,
    }

    def render_items(note_list):
        items = []
        for n in sorted(note_list, key=lambda x: x["title"].lower()):
            items.append(f'<li><a href="{n["slug"]}.html">{html.escape(n["title"])}</a></li>')
        return "".join(items)

    cards_html = []
    for cat in CATEGORY_ORDER:
        if cat not in tree:
            continue
        label = CATEGORY_LABELS.get(cat, cat)
        inner_parts = []

        direct = tree[cat].get("_direct", {}).get("_direct", [])
        if direct:
            inner_parts.append(f'<ul>{render_items(direct)}</ul>')

        subs = [k for k in tree[cat].keys() if k != "_direct"]
        for sub in sorted(subs):
            sub_label = CATEGORY_LABELS.get(sub, sub)
            inner_parts.append(
                f'<h3 class="home-subcat">{html.escape(sub_label)}</h3>'
                f'<ul>{render_items(tree[cat][sub])}</ul>'
            )

        cards_html.append(
            f'<section class="home-card"><h2>{html.escape(label)}</h2>{"".join(inner_parts)}</section>'
        )

    sidebar_rendered = sidebar_html.replace("__SLUG__", "")

    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Artefactos de Guerra — Investigación</title>
<link rel="stylesheet" href="assets/style.css">
<script>
(function(){{try{{var t=localStorage.getItem('adg-theme')||'dark';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>
<body>
<div class="layout">
  <aside class="sidebar">
    <a class="brand" href="index.html">Artefactos de Guerra</a>
    <div class="search-box"><input id="search" type="search" placeholder="Buscar…" autocomplete="off"></div>
    <div class="sidebar-tools">
      <a href="graph.html">Grafo</a>
      <a href="timeline.html">Timeline</a>
      <a href="map.html">Mapa</a>
      <button id="theme-toggle" class="theme-toggle" type="button" title="Cambiar tema">◑</button>
    </div>
    <nav class="nav">{sidebar_rendered}</nav>
  </aside>
  <main class="content">
    <header class="home-header">
      <h1>Artefactos de Guerra</h1>
      <p class="tagline">Vademécum de investigación — una película de Jorge Caballero.</p>
      <div class="stats"><span>{stats['total']} notas</span> · <span>{stats['categorias']} categorías</span> · <span>{stats['casos']} casos</span> · <span>{stats['empresas']} fichas de industria</span></div>
      <div class="home-cta">
        <a class="cta-btn primary" href="timeline.html">📅 Cronología visual 1850 → 2026</a>
        <a class="cta-btn" href="map.html">🌍 Mapa mundial de casos</a>
        <a class="cta-btn" href="graph.html">▣ Grafo de conexiones</a>
        <a class="cta-btn" href="casos/impacto-agregado.html">📊 Impacto agregado — las cifras del daño</a>
      </div>
    </header>
    <div class="home-grid">
      {''.join(cards_html)}
    </div>
  </main>
</div>
<script>window.__SITE_ROOT__ = "";</script>
<script src="assets/site.js"></script>
</body>
</html>
"""


# ---------- assets ----------

CSS = r"""
:root,
:root[data-theme="dark"] {
  --bg: #0e0e10;
  --bg-panel: #16171b;
  --bg-hover: #1f2127;
  --fg: #e8e6e1;
  --fg-dim: #9a9a9a;
  --accent: #e05d3d;
  --border: #262830;
  --chip-bg: #23262e;
  --link: #f0a68a;
  --panel-strong: #15161b;
  --shadow: 0 8px 24px rgba(0,0,0,.35);
}
:root[data-theme="light"] {
  --bg: #f8f6f1;
  --bg-panel: #ffffff;
  --bg-hover: #f1ede4;
  --fg: #1a1a1d;
  --fg-dim: #6a6a6a;
  --accent: #c64620;
  --border: #e2dfd5;
  --chip-bg: #ede9dd;
  --link: #b44219;
  --panel-strong: #fbf8f0;
  --shadow: 0 6px 18px rgba(0,0,0,.08);
}
* { box-sizing: border-box; }
html, body { margin:0; padding:0; background:var(--bg); color:var(--fg); font: 16px/1.7 -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", "Segoe UI", system-ui, sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; letter-spacing: -0.01em; }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }

.layout { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; }
.sidebar { background: var(--bg-panel); border-right: 1px solid var(--border); padding: 18px 14px; position: sticky; top:0; height:100vh; overflow-y:auto; font-size: 13px; }
.brand { font-weight:700; font-size:17px; display:block; margin-bottom:18px; color:var(--fg); letter-spacing:.2px; }
.search-box input { width:100%; padding:10px 14px; background:var(--bg); color:var(--fg); border:1px solid var(--border); border-radius:10px; font-size:14px; transition: border-color .15s; }
.search-box input:focus { outline:none; border-color:var(--accent); box-shadow: 0 0 0 3px rgba(224,93,61,0.1); }
.nav { margin-top: 18px; font-size: 14px; }
.nav-group { margin-bottom: 12px; }
.nav-group summary { cursor: pointer; font-weight:600; color:var(--fg-dim); padding:6px 4px; text-transform:uppercase; font-size:11px; letter-spacing:.6px; }
.nav-group ul { list-style:none; padding:2px 0 8px 8px; margin:0; }
.nav-group li a { display:block; padding:5px 8px; border-radius:6px; color:var(--fg); font-size:13.5px; border-left:2px solid transparent; transition: none; }
.nav-group li a:hover { background:var(--bg-hover); text-decoration:none; border-left-color:var(--accent); }
.nav-group li a.active { background:var(--bg-hover); border-left-color:var(--accent); color:var(--accent); font-weight: 600; }
.nav-chip { display: inline-block; margin-left: 6px; padding: 1px 6px; font-size: 10px; font-weight: 600; background: var(--accent); color: #fff; border-radius: 8px; vertical-align: middle; }
.nav-chip-done { background: #5fd49e; color: #0b1a10; }
.sidebar-legend { padding: 8px 12px; margin-bottom: 10px; font-size: 11px; color: var(--text-muted); border: 1px dashed var(--border); border-radius: 6px; line-height: 1.6; }
.sidebar-legend .nav-chip { margin-left: 0; margin-right: 4px; }
.file-warning { background: #ffd54a; color: #1a1a1a; padding: 10px 16px; font-size: 13px; line-height: 1.5; border-bottom: 2px solid #c89a00; }
.file-warning code { background: rgba(0,0,0,0.12); padding: 1px 5px; border-radius: 3px; font-size: 12px; }
.file-warning a { color: #6e3a00; font-weight: 700; }

/* TOC lateral (notas largas) */
.note-toc { margin: 0 0 32px 0; padding: 0; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; font-size: 14px; }
.note-toc summary { padding: 14px 20px; cursor: pointer; font-weight: 500; font-size: 13px; color: var(--fg-dim); list-style: none; display: flex; align-items: center; gap: 8px; }
.note-toc summary::-webkit-details-marker { display: none; }
.note-toc summary::before { content: '▸'; font-size: 11px; transition: transform .2s; }
.note-toc[open] summary::before { transform: rotate(90deg); }
.note-toc summary:hover { color: var(--fg); }
.note-toc ul { padding: 0 20px 16px 20px; margin: 0; list-style: none; }
.note-toc li { padding: 4px 0; }
.note-toc li a { color: var(--fg-dim); transition: color .15s; }
.note-toc li a:hover { color: var(--accent); text-decoration: none; }
.note-toc .toc-h3 { padding-left: 16px; font-size: 13px; }
.note-toc h4 { margin: 0 0 8px 0; font-size: 10px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); }
.note-toc ul { list-style: none; margin: 0; padding: 0; }
.note-toc li { line-height: 1.4; margin: 3px 0; }
.note-toc li a { color: var(--fg); text-decoration: none; }
.note-toc li a:hover { color: var(--accent); }
.toc-h2 { font-weight: 500; }
.toc-h3 { padding-left: 12px; font-size: 11px; color: var(--fg-dim); }
@media (max-width: 600px) { .note-toc ul { columns: 1; } }

/* Timeline visual page */
.timeline-page { background: var(--bg); color: var(--fg); }
.timeline-header { display: flex; align-items: center; gap: 18px; padding: 14px 28px; background: var(--bg-panel); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
.timeline-header .tl-subtitle { color: var(--fg-dim); font-size: 13px; text-transform: uppercase; letter-spacing: .6px; }
.timeline-header .timeline-actions { margin-left: auto; display: flex; gap: 10px; align-items: center; }
.timeline-main { max-width: 980px; margin: 40px auto 80px auto; padding: 0 30px; position: relative; }
.timeline-main::before { content: ""; position: absolute; top: 0; bottom: 0; left: 140px; width: 2px; background: linear-gradient(to bottom, transparent 0, var(--border) 30px, var(--border) calc(100% - 30px), transparent 100%); }
.tl-era { margin: 40px 0 28px -10px; padding-left: 180px; position: relative; }
.tl-era h2 { margin: 0; font-size: 18px; text-transform: uppercase; letter-spacing: .8px; color: var(--era-color, var(--accent)); border: none; padding: 0; }
.tl-era::before { content: ""; position: absolute; left: 135px; top: 50%; width: 12px; height: 12px; background: var(--era-color, var(--accent)); border-radius: 50%; transform: translateY(-50%); box-shadow: 0 0 0 4px var(--bg); }
.tl-item { display: grid; grid-template-columns: 130px 1fr; gap: 30px; margin: 18px 0; position: relative; align-items: start; }
.tl-item .tl-dot { position: absolute; left: 135px; top: 14px; width: 10px; height: 10px; background: var(--era-color, var(--accent)); border-radius: 50%; border: 2px solid var(--bg); box-shadow: 0 0 0 1px var(--border); }
.tl-item .tl-year { text-align: right; color: var(--era-color, var(--fg-dim)); font-weight: 600; font-size: 13px; padding-top: 10px; font-variant-numeric: tabular-nums; }
.tl-item .tl-card { background: var(--bg-panel); border: 1px solid var(--border); border-left: 3px solid var(--era-color, var(--accent)); border-radius: 8px; padding: 14px 18px; }
.tl-item .tl-card h3 { margin: 0 0 8px 0; font-size: 15px; color: var(--fg); }
.tl-item .tl-content { font-size: 13px; line-height: 1.55; color: var(--fg); }
.tl-item .tl-content p { margin: 6px 0; }
.tl-item .tl-content blockquote { border-left: 2px solid var(--era-color, var(--accent)); margin: 8px 0; padding: 4px 12px; background: var(--bg-hover); font-style: italic; color: var(--fg-dim); border-radius: 0 6px 6px 0; }
.tl-item .tl-content ul { margin: 6px 0; padding-left: 20px; }
.tl-item .tl-content strong { color: var(--fg); }
@media (max-width: 720px) {
  .timeline-main::before { left: 30px; }
  .tl-era { padding-left: 70px; }
  .tl-era::before { left: 25px; }
  .tl-item { grid-template-columns: 1fr; padding-left: 60px; }
  .tl-item .tl-dot { left: 25px; }
  .tl-item .tl-year { text-align: left; }
}

/* World map page */
.map-page { background: var(--bg); color: var(--fg); overflow: hidden; }
.map-header { display: flex; align-items: center; gap: 18px; padding: 14px 28px; background: var(--bg-panel); border-bottom: 1px solid var(--border); position: relative; z-index: 10; }
.map-header .map-subtitle { color: var(--fg-dim); font-size: 13px; text-transform: uppercase; letter-spacing: .6px; }
.map-header .map-actions { margin-left: auto; }
#map-container { width: 100vw; height: calc(100vh - 60px); }
.country { fill: var(--bg-panel); stroke: var(--border); stroke-width: .6; transition: fill .15s; }
.country:hover { fill: var(--bg-hover); }
.points circle { transition: r .15s; }
.map-legend { position: fixed; top: 80px; left: 20px; width: 200px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; z-index: 5; backdrop-filter: blur(6px); }
.map-legend h4 { margin: 0 0 8px 0; font-size: 11px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); }
.map-legend ul { list-style: none; padding: 0; margin: 0; font-size: 12px; }
.map-legend li { display: flex; align-items: center; gap: 8px; padding: 4px 0; }
.map-legend .dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; border: 1.5px solid var(--bg); flex-shrink: 0; }
.map-legend .dot-muerto { background: #d33f6a; }
.map-legend .dot-masacre { background: #e05d3d; }
.map-legend .dot-ceguera { background: #a78bfa; }
.map-legend .dot-ojo { background: #f0a94a; }
.map-legend .dot-lesion { background: #6eb8d6; }
.map-help { margin: 12px 0 0 0; padding-top: 10px; border-top: 1px solid var(--border); font-size: 11px; color: var(--fg-dim); line-height: 1.7; }
.map-help b { color: var(--fg); }
#map-tooltip { display: none; position: absolute; pointer-events: none; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; font-size: 12px; color: var(--fg); z-index: 100; max-width: 280px; box-shadow: var(--shadow); }
#map-tooltip .tt-country { color: var(--fg-dim); font-size: 11px; }
.nav-subgroup { margin: 4px 0 4px 6px; padding-left: 8px; border-left: 1px solid var(--border); }
.nav-subgroup summary { cursor: pointer; font-weight:500; color:var(--fg-dim); padding:4px 4px; font-size:11px; text-transform: uppercase; letter-spacing:.4px; }
.nav-subgroup ul { padding-left: 6px; }
.nav-direct { margin-bottom: 4px; }
.home-subcat { margin: 14px 0 6px 0; font-size: 12px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); font-weight: 600; }
.graph-link { display:block; margin-top:14px; padding:10px 12px; background:var(--bg-hover); border:1px solid var(--border); border-radius:8px; font-size:13px; text-align:center; color:var(--fg); }
.graph-link:hover { border-color:var(--accent); text-decoration:none; }
.sidebar-tools { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 6px; margin: 12px 0 16px 0; }
.sidebar-tools a, .sidebar-tools button { padding: 8px 0; background: var(--bg-hover); border: 1px solid var(--border); border-radius: 8px; font-size: 12px; font-weight: 500; text-align: center; color: var(--fg-dim); cursor: pointer; text-decoration: none; transition: all .15s; }
.sidebar-tools a:hover, .sidebar-tools button:hover { border-color: var(--accent); color: var(--accent); background: var(--bg); text-decoration: none; }
.theme-toggle { width: 36px; padding: 8px 0; background: var(--bg-hover); border: 1px solid var(--border); border-radius: 8px; font-size: 14px; color: var(--fg-dim); cursor: pointer; transition: all .15s; }
.theme-toggle:hover { border-color: var(--accent); }
.theme-toggle:hover { border-color: var(--accent); }

/* Sticky audio player */
.sticky-audio { position: sticky; top: 0; z-index: 20; margin: 0 -52px 24px -52px; padding: 14px 52px; background: var(--panel-strong); border-bottom: 1px solid var(--border); box-shadow: var(--shadow); }
.sticky-audio audio { width: 100%; display: block; }
.sticky-audio-meta { font-size: 11px; color: var(--fg-dim); margin-top: 6px; text-transform: uppercase; letter-spacing: .6px; }

/* YouTube embeds */
.yt-embed { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 16px 0; border-radius: 10px; border: 1px solid var(--border); background: #000; }
.yt-embed iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }

/* Audio wrap (inside body) */
.audio-wrap { margin: 14px 0; padding: 12px 14px; background: var(--panel-strong); border: 1px solid var(--border); border-radius: 10px; }
.audio-wrap audio { width: 100%; display: block; }
.audio-meta { font-size: 11px; color: var(--fg-dim); margin-top: 6px; }

/* Timecode links */
a.tc { color: var(--accent); font-variant-numeric: tabular-nums; font-weight: 600; text-decoration: none; padding: 0 2px; border-radius: 3px; cursor: pointer; }
a.tc:hover { background: var(--accent); color: #fff; text-decoration: none; }

/* Sources (frontmatter) */
.sources { margin-top: 28px; }
.sources h4 { margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); }
.source-item { margin-bottom: 14px; }
.source-link { font-size: 12px; color: var(--fg-dim); word-break: break-all; margin-top: 4px; }
.source-text { padding: 10px 14px; background: var(--panel-strong); border: 1px solid var(--border); border-radius: 8px; font-size: 13px; word-break: break-all; }

.content { padding: 48px 60px 80px 60px; max-width: 820px; margin: 0 auto; }
.note-header { margin-bottom: 36px; }
.breadcrumb { font-size: 12px; color: var(--fg-dim); margin-bottom: 8px; font-weight: 500; }
.note-header h1 { margin: 0; font-size: 32px; line-height: 1.2; letter-spacing: -.4px; font-weight: 700; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { display:inline-block; padding:2px 8px; border-radius:10px; background:var(--chip-bg); border:1px solid var(--border); font-size:11px; color:var(--fg-dim); }
.chip-tipo { background: rgba(232,196,155,0.15); color: var(--fg-dim); border-color: rgba(232,196,155,0.3); }
.chip-estado { font-weight:600; }
.chip-borrador { background: rgba(241,196,96,0.15); color: var(--fg-dim); border-color: rgba(241,196,96,0.3); }
.chip-literal { background: rgba(119,212,145,0.15); color: var(--fg-dim); border-color: rgba(119,212,145,0.3); }
.chip-stub { background: rgba(255,138,122,0.15); color: var(--fg-dim); border-color: rgba(255,138,122,0.3); }

.note-body h1 { display:none; }  /* title already rendered in header */
.note-body h2 { margin: 40px 0 16px 0; font-size: 22px; font-weight: 700; letter-spacing: -.2px; color: var(--fg); }
.note-body h3 { margin: 32px 0 12px 0; font-size: 17px; font-weight: 600; color: var(--fg); }
.note-body h4 { margin: 24px 0 8px 0; font-size: 15px; font-weight: 600; color: var(--fg-dim); }
.note-body h4 { font-size: 14px; color: var(--fg-dim); text-transform: uppercase; letter-spacing:.6px; }
.note-body blockquote { border-left: 3px solid var(--accent); padding: 12px 20px; color: var(--fg-dim); background: var(--bg-hover); margin: 20px 0; border-radius: 0 10px 10px 0; font-size: 15px; line-height: 1.6; }
.note-body p { margin: 12px 0; }
.note-body ul, .note-body ol { margin: 12px 0; padding-left: 24px; }
.note-body li { margin: 6px 0; }
.note-body code { background:var(--bg-hover); padding:2px 6px; border-radius:4px; font-size:.9em; }
.note-body pre { background:var(--bg); padding:14px; border-radius:8px; overflow:auto; border:1px solid var(--border); }
.note-body table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 14px; }
.note-body th, .note-body td { border: 1px solid var(--border); padding: 10px 12px; text-align: left; vertical-align: top; }
.note-body th { background: var(--bg-hover); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .3px; }
.note-body td { line-height: 1.5; }
.note-body ul, .note-body ol { padding-left: 22px; }
.note-body a.wikilink { color: var(--accent); border-bottom:1px dashed var(--fg-dim); }
.note-body a.wikilink.broken, .note-body .wikilink.broken { color: #c0392b; border-bottom:1px dashed #c0392b; cursor:help; }

/* legacy .sources rule — replaced by embed-aware version below */

/* .backlinks and .outlinks styled in links-block section below */

.home-header h1 { font-size: 42px; margin: 0 0 6px 0; letter-spacing: -.6px; }
.tagline { color: var(--fg-dim); margin: 0 0 10px 0; }
.stats { font-size: 13px; color: var(--fg-dim); display: flex; flex-wrap: wrap; gap: 6px 16px; }
.stats span { color: var(--fg); font-weight: 600; }
.home-cta { margin-top: 20px; display: flex; flex-wrap: wrap; gap: 10px; }
.cta-btn { display: inline-block; padding: 10px 18px; border: 1px solid var(--border); border-radius: 8px; color: var(--fg); font-size: 13px; text-decoration: none; background: var(--bg-panel); transition: border-color .15s, background .15s; }
.cta-btn:hover { border-color: var(--accent); text-decoration: none; background: var(--bg-hover); }
.cta-btn.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.cta-btn.primary:hover { background: var(--accent); filter: brightness(1.1); }
.home-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; margin-top: 28px; }
.home-card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 14px; padding: 20px 22px; }
.home-card h2 { margin:0 0 12px 0; font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing:.5px; color: var(--accent); border:none; padding:0; }
.home-card ul { list-style:none; padding:0; margin:0; }
.home-card li { padding: 6px 0; font-size: 14px; line-height: 1.4; }
.home-card li + li { border-top: 1px solid var(--border); }
.home-card li a { display: block; }
.home-card li:last-child { border-bottom: none; }

.graph-page { background: var(--bg); overflow: hidden; color: var(--fg); }
.graph-page svg text { fill: var(--fg); paint-order: stroke; stroke: var(--bg); stroke-width: 3px; stroke-linejoin: round; }
.graph-page .g-node-label { fill: var(--fg); }
.graph-page .g-node-circle { stroke: var(--bg); }
.graph-page .arrow-path { fill: var(--fg-dim); }
.graph-page .arrow-path-hot { fill: var(--accent); }
.graph-page .links line { stroke: var(--fg-dim) !important; stroke-opacity: 0.35; }
.graph-page .links line.dim { stroke-opacity: 0.06; }
.graph-page .links line.highlight { stroke: var(--accent) !important; stroke-opacity: 0.95; stroke-width: 2; }
.graph-page .nodes .node.highlight circle { stroke: var(--fg) !important; stroke-width: 2.5; }
.graph-header { display:flex; align-items:center; gap:18px; padding:14px 22px; background:var(--bg-panel); border-bottom:1px solid var(--border); position: relative; z-index: 10; }
.graph-header .graph-actions { margin-left: auto; }
.graph-header button,
.graph-header select { background:var(--bg-hover); color:var(--fg); border:1px solid var(--border); border-radius:6px; padding:6px 12px; font-size:12px; cursor:pointer; }
.graph-header button:hover,
.graph-header select:hover { border-color:var(--accent); }
.graph-header select { margin-right: 6px; }
.graph-header #graph-search { background: var(--bg-hover); color: var(--fg); border: 1px solid var(--border); border-radius: 6px; padding: 6px 12px; font-size: 12px; margin-right: 6px; width: 180px; outline: none; }
.graph-header #graph-search::placeholder { color: var(--fg-dim); }
.graph-header #graph-search:focus { border-color: var(--accent); }
.nodes .node.g-match circle { stroke: #ffd54a !important; stroke-width: 3.5 !important; filter: drop-shadow(0 0 6px rgba(255, 213, 74, 0.9)); }
.nodes .node.g-match text { fill: #ffd54a !important; font-weight: 700; font-size: 13px !important; }
.nodes .node.g-search-dim { opacity: 0.1; }
.links line.g-search-dim { stroke-opacity: 0.04; }
.graph-title { color: var(--fg-dim); font-size:13px; text-transform:uppercase; letter-spacing:.6px; }
.graph-panel { position: fixed; top: 80px; left: 20px; width: 240px; background: var(--bg-panel); border:1px solid var(--border); border-radius: 10px; padding: 14px 16px; z-index: 5; backdrop-filter: blur(6px); }
.graph-panel h4 { margin: 0 0 8px 0; font-size: 11px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); }
.graph-panel .legend-btn { display: flex; align-items: center; gap: 8px; width: 100%; background: transparent; border: 1px solid transparent; color: var(--fg); padding: 6px 8px; border-radius: 6px; cursor: pointer; font-size: 13px; text-align: left; margin-bottom: 2px; transition: background .15s; }
.graph-panel .legend-btn:hover { background: var(--bg-hover); }
.graph-panel .legend-btn.off { opacity: .35; text-decoration: line-through; }
.graph-panel .swatch { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; border: 1px solid var(--border); }
.graph-help { margin: 14px 0 0 0; padding-top: 12px; border-top: 1px solid var(--border); font-size: 11px; line-height: 1.6; color: var(--fg-dim); }
.graph-help b { color: var(--fg); }
#graph { width:100vw; height:calc(100vh - 60px); }
.links line { transition: stroke .2s, stroke-opacity .2s, stroke-width .2s; }
.nodes .node { cursor: pointer; transition: opacity .2s; }
.nodes .node.dim { opacity: 0.14; }
.nodes .node text { pointer-events: none; font-family: -apple-system, sans-serif; }

/* Local graph embedded in note page */
.local-graph-wrap { margin-top: 40px; padding: 16px 20px; background:var(--bg-panel); border:1px solid var(--border); border-radius: 14px; }
.local-graph-wrap h4 { margin: 0 0 8px 0; font-size: 11px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); }
.local-graph-wrap .lg-hint { font-size: 10px; color: var(--fg-dim); margin-bottom: 4px; }
#local-graph { width: 100%; height: 320px; overflow: hidden; }
#local-graph svg { display: block; }
/* Local graph — themed via CSS vars (fixes white-on-white in light theme) */
.lg-label { fill: var(--fg); pointer-events: none; }
.lg-link  { stroke: var(--fg-dim); stroke-opacity: 0.6; stroke-width: 1.3; }
.lg-circle { stroke: var(--bg); }
.lg-circle-center { stroke: var(--fg); }
.lg-arrow-path { fill: var(--fg-dim); }

/* Links block: outgoing + backlinks side by side */
.links-block { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 32px; }
.outlinks, .backlinks { margin: 0; padding: 16px 20px; background:var(--bg-panel); border:1px solid var(--border); border-radius:12px; }
.outlinks { border-left: 3px solid #6eb8d6; }
.backlinks { border-left: 3px solid var(--accent); }
.outlinks h4, .backlinks h4 { margin: 0 0 8px 0; color: var(--fg-dim); text-transform: uppercase; font-size: 11px; letter-spacing:.6px; }
.outlinks ul, .backlinks ul { margin:0; padding-left: 18px; font-size: 13.5px; }

@media (max-width: 900px) {
  .links-block { grid-template-columns: 1fr; }
  .graph-panel { position: static; width: auto; margin: 14px; }
}

.search-results { position: fixed; top: 0; left: 280px; right: 0; background: rgba(14,14,16,.97); padding: 24px 52px; max-height: 80vh; overflow-y: auto; display:none; z-index:100; border-bottom: 1px solid var(--border); }
.search-results.open { display: block; }
.search-results h3 { margin-top: 0; }
.search-result { padding: 10px 0; border-bottom: 1px solid var(--border); }
.search-result b { color: var(--accent); }
.search-result .cat { font-size: 11px; color: var(--fg-dim); text-transform: uppercase; }

@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; }
  .content { padding: 24px 22px 60px 22px; }
  .search-results { left: 0; padding: 18px 22px; }
}
"""

SITE_JS = r"""
// ===== file:// warning for YouTube embeds =====
(function () {
  if (window.location.protocol !== 'file:') return;
  if (!document.querySelector('.yt-embed')) return;
  const banner = document.createElement('div');
  banner.className = 'file-warning';
  banner.innerHTML = '⚠️ Estás abriendo el sitio con <code>file://</code>. YouTube bloquea los reproductores en este modo (Error 153). Para verlos: ejecuta <code>python3 build.py --serve</code> y abre <a href="http://localhost:8765" target="_blank">http://localhost:8765</a> · o despliega el sitio (ver <code>DEPLOY.md</code>).';
  document.body.insertBefore(banner, document.body.firstChild);
})();

// ===== Sidebar scroll persistence + active note =====
(function () {
  const sidebar = document.querySelector('.sidebar');
  if (!sidebar) return;
  const STORE_KEY = 'adg-sidebar-scroll';

  // Save scroll position before navigation
  function saveScroll() {
    try { sessionStorage.setItem(STORE_KEY, String(sidebar.scrollTop)); } catch (e) {}
  }
  sidebar.addEventListener('click', (e) => {
    // delay so click also follows the link
    setTimeout(saveScroll, 0);
  });
  window.addEventListener('beforeunload', saveScroll);

  // Restore scroll position
  try {
    const v = sessionStorage.getItem(STORE_KEY);
    if (v !== null) sidebar.scrollTop = parseInt(v, 10);
  } catch (e) {}

  // Highlight active note based on current path
  const path = window.location.pathname.split('/').pop() || 'index.html';
  // Match by data-slug ending with the filename without extension
  const currentSlug = path.replace(/\.html$/, '');
  let foundActive = null;
  document.querySelectorAll('.sidebar a[data-slug]').forEach(a => {
    const slug = a.getAttribute('data-slug');
    const tail = slug.split('/').pop();
    if (tail === currentSlug) {
      a.classList.add('active');
      foundActive = a;
    }
  });
  // Only scroll active into view if user has no saved scroll AND it's not visible
  if (foundActive) {
    const sb = sidebar.getBoundingClientRect();
    const ab = foundActive.getBoundingClientRect();
    if (ab.top < sb.top || ab.bottom > sb.bottom) {
      // only auto-scroll if no saved position (first visit)
      try {
        if (sessionStorage.getItem(STORE_KEY) === null) {
          foundActive.scrollIntoView({ block: 'center' });
        }
      } catch (e) {}
    }
  }
})();

// ===== Theme toggle =====
(function () {
  const root = document.documentElement;
  function setTheme(t) {
    root.setAttribute('data-theme', t);
    try { localStorage.setItem('adg-theme', t); } catch (e) {}
  }
  const saved = (function () { try { return localStorage.getItem('adg-theme'); } catch (e) { return null; }})() || 'dark';
  setTheme(saved);
  const btn = document.getElementById('theme-toggle');
  if (btn) {
    btn.addEventListener('click', () => {
      const current = root.getAttribute('data-theme') || 'dark';
      setTheme(current === 'dark' ? 'light' : 'dark');
    });
  }
})();

// ===== Timecode clicks → seek audio =====
(function () {
  const audio = document.getElementById('note-audio');
  if (!audio) return;
  document.querySelectorAll('a.tc').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const t = parseFloat(el.getAttribute('data-t'));
      if (!isNaN(t)) {
        audio.currentTime = t;
        audio.play().catch(()=>{});
        audio.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
})();

// ===== Search =====
(async function () {
  const root = window.__SITE_ROOT__ || "";
  let idx = [];
  try {
    const res = await fetch(root + 'search-index.json');
    idx = await res.json();
  } catch (e) { console.warn('no search index', e); return; }

  const input = document.getElementById('search');
  if (!input) return;
  let resultsEl = document.querySelector('.search-results');
  if (!resultsEl) {
    resultsEl = document.createElement('div');
    resultsEl.className = 'search-results';
    document.body.appendChild(resultsEl);
  }

  function render(matches, q) {
    if (!q) { resultsEl.classList.remove('open'); resultsEl.innerHTML = ''; return; }
    if (!matches.length) {
      resultsEl.innerHTML = '<h3>Sin resultados para "' + q + '"</h3>';
    } else {
      const highlight = (text) => text.replace(new RegExp('(' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<b>$1</b>');
      resultsEl.innerHTML = '<h3>' + matches.length + ' resultado(s) para "' + q + '"</h3>' +
        matches.map(m => `
          <div class="search-result">
            <div class="cat">${m.category}</div>
            <a href="${root}${m.slug}.html">${highlight(m.title)}</a>
            <div>${highlight(m.snippet)}</div>
          </div>`).join('');
    }
    resultsEl.classList.add('open');
  }

  input.addEventListener('input', () => {
    const q = input.value.trim();
    if (q.length < 2) { render([], ''); return; }
    const ql = q.toLowerCase();
    const matches = idx.filter(n =>
      n.title.toLowerCase().includes(ql) ||
      n.snippet.toLowerCase().includes(ql) ||
      n.category.toLowerCase().includes(ql)
    ).slice(0, 30);
    render(matches, q);
  });

  document.addEventListener('click', (e) => {
    if (!resultsEl.contains(e.target) && e.target !== input) {
      resultsEl.classList.remove('open');
    }
  });
})();
"""


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    (SITE / "assets").mkdir()

    # write CSS + JS
    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")
    (SITE / "assets" / "site.js").write_text(SITE_JS, encoding="utf-8")

    # copy raw assets if any
    if ASSETS.exists():
        for item in ASSETS.iterdir():
            target = SITE / "assets" / item.name
            if item.is_file():
                shutil.copy2(item, target)

    # copy media/ (audio, etc.) to site/media/ as symlink for speed
    if MEDIA.exists():
        site_media = SITE / "media"
        if site_media.exists() or site_media.is_symlink():
            try:
                site_media.unlink()
            except (IsADirectoryError, OSError):
                shutil.rmtree(site_media)
        try:
            os.symlink(MEDIA.resolve(), site_media)
        except OSError:
            shutil.copytree(MEDIA, site_media)

    # collect notes
    notes = []
    for md in sorted(WIKI.rglob("*.md")):
        rel = md.relative_to(WIKI).as_posix()
        # skip 00-pendientes.md — it's auto-regenerated below, so we avoid
        # parsing a stale version and duplicating the entry in the sidebar
        if rel == "00-pendientes.md":
            continue
        notes.append(parse_note(md))
    all_slugs = {n["slug"] for n in notes}

    # resolve links
    link_map = {}  # slug -> list of resolved target slugs
    for n in notes:
        resolved = []
        for raw in n["links_raw"]:
            r = resolve_link(n["slug"], raw, all_slugs)
            if r:
                resolved.append(r)
        link_map[n["slug"]] = resolved

    # backlinks
    backlink_map = {s: [] for s in all_slugs}
    for src, targets in link_map.items():
        for t in targets:
            if src not in backlink_map[t]:
                backlink_map[t].append(src)

    # group by category (two-level)
    tree = group_notes(notes)
    sidebar_template = build_sidebar(tree)
    slug_to_title = {n["slug"]: n["title"] for n in notes}

    # slug -> meta (for local graph)
    slug_to_meta = {
        n["slug"]: {"title": n["title"], "category": n["category"]}
        for n in notes
    }

    # ----- aggregate pending items disabled: project-level pendings live in BACKLOG.md -----
    # (previously we auto-generated 00-pendientes.md with every ## Pendientes item;
    # now there are none and we don't need that page)
    pend_path = WIKI / "00-pendientes.md"
    if pend_path.exists():
        try:
            pend_path.unlink()
        except OSError:
            pass
    site_pend_html = SITE / "00-pendientes.html"
    if site_pend_html.exists():
        try:
            site_pend_html.unlink()
        except OSError:
            pass

    # write each note
    for n in notes:
        fm = n["frontmatter"]
        # audio file from frontmatter (audio, audio_m4a, audio_mp3, audio_wav)
        audio_src = fm.get("audio") or fm.get("audio_m4a") or fm.get("audio_mp3") or fm.get("audio_wav")
        has_audio = bool(audio_src)
        depth = n["slug"].count("/")
        up = "../" * depth
        audio_player_html_block = ""
        if has_audio:
            audio_player_html_block = (
                f'<div class="sticky-audio">'
                f'<audio id="note-audio" controls preload="metadata" src="{up}{audio_src}"></audio>'
                f'<div class="sticky-audio-meta">🎧 Audio de la nota — haz clic en cualquier timecode para saltar</div>'
                f'</div>'
            )

        # URLs already embedded in the frontmatter "Fuentes" block — skip re-embedding inline
        _already_embedded = []
        _fuentes = fm.get("fuentes") or fm.get("fuente") or []
        if isinstance(_fuentes, str):
            _fuentes = [_fuentes]
        for _f in _fuentes:
            _already_embedded.append(str(_f))
        if audio_src:
            _already_embedded.append(f"{up}{audio_src}")

        body_html = md_to_html(n["body"], n["slug"], all_slugs, link_map, has_audio=has_audio, already_embedded=_already_embedded)

        # backlinks (incoming)
        incoming = backlink_map.get(n["slug"], [])
        if incoming:
            items = "".join(
                f'<li><a href="{relative_href(n["slug"], s)}">{html.escape(slug_to_title.get(s, s))}</a></li>'
                for s in sorted(incoming)
            )
            bl_html = f'<div class="backlinks"><h4>← Enlazado desde</h4><ul>{items}</ul></div>'
        else:
            bl_html = ""

        # outgoing
        outgoing = [t for t in link_map.get(n["slug"], []) if t != n["slug"]]
        # de-duplicate while preserving order
        seen = set()
        outgoing_unique = []
        for t in outgoing:
            if t not in seen:
                seen.add(t)
                outgoing_unique.append(t)
        if outgoing_unique:
            items = "".join(
                f'<li><a href="{relative_href(n["slug"], s)}">{html.escape(slug_to_title.get(s, s))}</a></li>'
                for s in outgoing_unique
            )
            out_html = f'<div class="outlinks"><h4>→ Enlaza con</h4><ul>{items}</ul></div>'
        else:
            out_html = ""

        # local graph
        lg_html = local_graph_script(n["slug"], notes, link_map, backlink_map, slug_to_meta)

        # sidebar with correct relative prefix
        sidebar_html = sidebar_template.replace("__SLUG__", up)

        toc_html = build_toc(n["body"])
        page = page_template(n, body_html, sidebar_html, bl_html, out_html, lg_html, audio_player_html_block, toc_html, all_slugs)
        out_path = SITE / f"{n['slug']}.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")

    # home
    home = index_page(tree, notes, sidebar_template)
    (SITE / "index.html").write_text(home, encoding="utf-8")

    # graph
    graph_data = build_graph_data(notes, link_map)
    (SITE / "graph.html").write_text(graph_page_html(graph_data), encoding="utf-8")

    # timeline (from cronologia-completa.md)
    crono_note = next((n for n in notes if n["slug"] == "historia/cronologia-completa"), None)
    if crono_note:
        (SITE / "timeline.html").write_text(
            timeline_page_html(crono_note, all_slugs, link_map), encoding="utf-8"
        )

    # world map of cases
    (SITE / "map.html").write_text(map_page_html(notes), encoding="utf-8")

    # search index
    (SITE / "search-index.json").write_text(
        json.dumps(build_search_index(notes), ensure_ascii=False), encoding="utf-8"
    )

    print(f"✓ Built {len(notes)} notes into {SITE}")
    print(f"  Open: file://{(SITE / 'index.html').resolve()}")

    if "--serve" in sys.argv:
        import http.server, socketserver
        os.chdir(SITE)
        port = 8765
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"\n  Serving at http://localhost:{port}  (Ctrl+C to stop)")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n  Stopped.")


if __name__ == "__main__":
    main()
