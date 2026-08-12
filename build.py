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
    for s in sorted(all_slugs):
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
(function(){{try{{var t=localStorage.getItem('adg-theme')||'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
<script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
<button id="sidebar-open-btn" class="sidebar-open-btn" title="Abrir menú (M)" aria-label="Abrir menú">☰</button>
<div class="layout">
  <aside class="sidebar">
    <button id="sidebar-close-btn" class="sidebar-close-btn" title="Ocultar menú (M)" aria-label="Ocultar menú">◂</button>
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
<script>
(function(){{
  var body = document.body;
  var openBtn = document.getElementById('sidebar-open-btn');
  var closeBtn = document.getElementById('sidebar-close-btn');
  function setSidebar(collapsed) {{
    body.classList.toggle('sidebar-collapsed', collapsed);
    try {{ localStorage.setItem('adg-sidebar', collapsed ? 'off' : 'on'); }} catch (e) {{}}
  }}
  // Default: collapsed unless user has explicitly opened it before
  try {{
    if (localStorage.getItem('adg-sidebar') !== 'on') body.classList.add('sidebar-collapsed');
  }} catch (e) {{ body.classList.add('sidebar-collapsed'); }}
  if (openBtn) openBtn.addEventListener('click', function(){{ setSidebar(false); }});
  if (closeBtn) closeBtn.addEventListener('click', function(){{ setSidebar(true); }});
  document.addEventListener('keydown', function(e){{
    if (e.key === 'm' || e.key === 'M') {{
      var ae = document.activeElement;
      if (ae && (ae.tagName === 'INPUT' || ae.tagName === 'TEXTAREA')) return;
      setSidebar(!body.classList.contains('sidebar-collapsed'));
    }}
  }});
}})();
</script>
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
    "testimonios": "Testimonios",
    "espana-europa": "España y Europa",
    "estados-unidos": "Estados Unidos",
    "congresos": "Congresos",
    "empresas": "Empresas",
    "latam": "América Latina",
    "internacionales": "Internacionales",
    "bibliografia": "Bibliografía",
    "figuras-historicas": "Figuras históricas",
    "referentes": "Referentes audiovisuales",
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
    "casos": ["espana-europa", "estados-unidos", "latam", "internacionales"],
    "autores-y-referencias": ["paul-rocher", "testimonios", "figuras-historicas", "organizaciones", "referentes"],
    "empresas-de-armas": ["empresas", "publicidad", "renders"],
    "ferias-de-armas": ["feindef", "congresos"],
    "usos-de-armas": ["entrenamientos", "testimonios"],
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

def load_semantic():
    """Relaciones por embeddings (semantic.py). Sin fichero → capa vacía."""
    p = ROOT / "semantic-cache.json"
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("related", {}) or {}
    except Exception:
        return {}


def build_graph_data(notes, link_map, semantic_related=None):
    # degree
    degree = {n["slug"]: 0 for n in notes}
    edges = []
    seen_pairs = set()
    for src, targets in link_map.items():
        for t in targets:
            if src == t:
                continue
            edges.append({"source": src, "target": t})
            seen_pairs.add(frozenset((src, t)))
            degree[src] = degree.get(src, 0) + 1
            degree[t] = degree.get(t, 0) + 1
    # aristas semánticas (embeddings): solo entre notas existentes y no
    # redundantes con un wikilink manual
    if semantic_related:
        slugs = {n["slug"] for n in notes}
        for src, rels in semantic_related.items():
            for r in rels:
                t = r["slug"]
                if src not in slugs or t not in slugs:
                    continue
                pair = frozenset((src, t))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                edges.append({
                    "source": src, "target": t,
                    "kind": "sem", "sim": r.get("sim", 0),
                })

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
// Order chosen to tell a story left → right:
// Historia → Marco legal → Empresas → Ferias → Usos → Casos → Autores → Herramientas
const ORDERED_CATS = ['historia','marco-legal','empresas-de-armas','ferias-de-armas','usos-de-armas','casos','autores-y-referencias','herramientas'];
const categories = [...new Set(data.nodes.map(n => n.category))];
const catList = ORDERED_CATS.filter(c => categories.includes(c));
const color = (c) => PALETTE[c] || '#999';

const links = data.edges.map(d => Object.assign({}, d));
const nodes = data.nodes.map(d => Object.assign({}, d));

// neighbors index (undirected)
const neighbors = {};
nodes.forEach(n => neighbors[n.id] = new Set([n.id]));
links.forEach(l => {
  neighbors[l.source].add(l.target);
  neighbors[l.target].add(l.source);
});

// degree-rank inside each category — for hierarchy
const ranked = {};
nodes.forEach(n => { (ranked[n.category] = ranked[n.category] || []).push(n); });
const topByCategory = {};
Object.keys(ranked).forEach(c => {
  ranked[c].sort((a,b) => b.degree - a.degree);
  topByCategory[c] = new Set(ranked[c].slice(0, Math.max(3, Math.ceil(ranked[c].length * 0.18))).map(n => n.id));
  ranked[c].forEach((n, i) => { n._rank = i; n._rankPct = ranked[c].length > 1 ? i / (ranked[c].length - 1) : 0.5; });
});

const viewW = window.innerWidth;
const viewH = window.innerHeight - 60;

// Virtual canvas — wider than viewport, so we have room to spread
const W = Math.max(viewW * 1.6, 2400);
const H = Math.max(viewH * 1.2, 1300);

// One column per category
const colWidth = W / catList.length;
const catX = {};
catList.forEach((c, i) => { catX[c] = (i + 0.5) * colWidth; });

const svg = d3.select('#graph').append('svg')
  .attr('width', viewW).attr('height', viewH);

// Defs: arrow + soft column tint gradients (we'll render bands behind nodes)
svg.append('defs').append('marker')
  .attr('id', 'arrow').attr('viewBox', '0 -5 10 10')
  .attr('refX', 22).attr('refY', 0)
  .attr('markerWidth', 5).attr('markerHeight', 5)
  .attr('orient', 'auto')
  .append('path').attr('d', 'M0,-4 L10,0 L0,4').attr('class', 'arrow-path');
svg.append('defs').append('marker')
  .attr('id', 'arrow-hot').attr('viewBox', '0 -5 10 10')
  .attr('refX', 22).attr('refY', 0)
  .attr('markerWidth', 7).attr('markerHeight', 7)
  .attr('orient', 'auto')
  .append('path').attr('d', 'M0,-4 L10,0 L0,4').attr('class', 'arrow-path-hot');

const g = svg.append('g');

let currentZoom = 1;

svg.on('click', (e) => { if (e.target.tagName === 'svg' || e.target.classList?.contains('column-bg')) clearFocus(); });

// --- Column bands inside the zoomable g (they pan/zoom with the graph) ---
const columnG = g.append('g').attr('class', 'columns');
const colBg = columnG.selectAll('rect').data(catList).enter().append('rect')
  .attr('class', 'column-bg')
  .attr('data-cat', d => d)
  .attr('x', d => catX[d] - colWidth / 2 + 8)
  .attr('y', 60)
  .attr('width', colWidth - 16)
  .attr('height', H - 60)
  .attr('fill', d => color(d))
  .attr('fill-opacity', 0.045)
  .attr('rx', 14)
  .on('click', (e, d) => { e.stopPropagation(); toggleIsolate(d); });

// Short variants used when the column is too narrow to display the full label
const CAT_SHORT = {
  'historia':              'HISTORIA',
  'marco-legal':           'LEGAL',
  'empresas-de-armas':     'EMPRESAS',
  'ferias-de-armas':       'FERIAS',
  'usos-de-armas':         'USOS',
  'casos':                 'CASOS',
  'autores-y-referencias': 'AUTORES',
  'herramientas':          'HERRAM.',
};

// --- Column TITLES on a fixed overlay layer (do NOT zoom/pan with the graph).
//     Pills are sized to the column width, never to the text width. ---
const titlesLayer = svg.append('g').attr('class', 'titles-fixed').attr('pointer-events', 'all');
const colTitle = titlesLayer.selectAll('g').data(catList).enter().append('g')
  .attr('class', 'column-title-wrap')
  .attr('data-cat', d => d)
  .style('cursor', 'pointer')
  .on('click', (e, d) => { e.stopPropagation(); toggleIsolate(d); });
colTitle.append('rect').attr('class', 'column-title-bg').attr('rx', 8).attr('ry', 8);
colTitle.append('text')
  .attr('class', 'column-title-text')
  .attr('text-anchor', 'middle')
  .attr('fill', d => color(d));

const PILL_H = 28;
const PILL_GAP = 8;     // gap between adjacent pills
const PILL_PAD_X = 14;  // inner horizontal padding for text

function positionTitles() {
  const t = d3.zoomTransform(svg.node());
  const screenColW = colWidth * t.k;
  // Pill width: tight to its column, minus a small gap on each side
  const pillW = Math.max(40, screenColW - PILL_GAP);
  colTitle.each(function(d) {
    const wrap = d3.select(this);
    const cx = t.applyX(catX[d]);
    wrap.attr('transform', 'translate(' + (cx - pillW / 2) + ', 8)');
    wrap.select('rect')
      .attr('x', 0).attr('y', 0)
      .attr('width', pillW).attr('height', PILL_H);
    const txt = wrap.select('text')
      .attr('x', pillW / 2)
      .attr('y', PILL_H / 2 + 4)
      .attr('font-size', null);
    // Try full label first; if too wide, fall back to short; if still too wide, shrink font.
    const fullLabel = (CAT_LABELS[d] || d).toUpperCase();
    txt.text(fullLabel);
    let bbW = txt.node().getBBox().width;
    const inner = pillW - PILL_PAD_X;
    if (bbW > inner) {
      const shortLabel = (CAT_SHORT[d] || fullLabel).toUpperCase();
      txt.text(shortLabel);
      bbW = txt.node().getBBox().width;
      if (bbW > inner) {
        const scale = inner / bbW;
        txt.attr('font-size', Math.max(8, Math.floor(12 * scale)) + 'px');
      }
    }
  });
}

const zoomBehavior = d3.zoom().scaleExtent([0.15, 4]).on('zoom', (e) => {
  g.attr('transform', e.transform);
  currentZoom = e.transform.k;
  updateLabelVisibility();
  positionTitles();
});
svg.call(zoomBehavior);

const hiddenCats = new Set();

// --- Simulation with column anchors + degree-based y ---
// HARD column lock: every node gets a fixed X within its category column band.
// This guarantees columns are pure — no node bleeds into a neighbor category
// just because it shares many links with it.
const colInnerWidth = colWidth * 0.55;
function seededRand(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 10000) / 10000; }
function columnX(d) {
  const base = catX[d.category] || W / 2;
  // deterministic offset within the column band so repeated builds look identical
  return base + (seededRand(d.id) - 0.5) * colInnerWidth;
}
nodes.forEach(n => {
  n.fx = columnX(n);
  n.x = n.fx;
  n.y = 100 + (n._rankPct || 0.5) * (H - 180);
});

const sim = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(70).strength(0.08))
  .force('charge', d3.forceManyBody().strength(-160).distanceMax(280))
  .force('collide', d3.forceCollide().radius(d => 16 + Math.sqrt(d.degree) * 2.8).strength(1))
  // Y only — X is locked via fx
  .force('y', d3.forceY(d => 100 + (d._rankPct || 0.5) * (H - 180)).strength(0.22))
  .alphaDecay(0.025);

const link = g.append('g').attr('class', 'links').selectAll('line')
  .data(links).enter().append('line')
  .attr('stroke-width', d => d.kind === 'sem' ? 0.8 : 1)
  .attr('class', d => d.kind === 'sem' ? 'link-sem' : null)
  .attr('stroke-dasharray', d => d.kind === 'sem' ? '3 4' : null)
  .attr('marker-end', d => d.kind === 'sem' ? null : 'url(#arrow)');

const node = g.append('g').attr('class', 'nodes').selectAll('g')
  .data(nodes).enter().append('g')
  .attr('class', 'node')
  .call(d3.drag()
    .on('start', (event, d) => { if (!event.active) sim.alphaTarget(0.25).restart(); d.fy = d.y; })
    .on('drag',  (event, d) => { d.fx = event.x; d.fy = event.y; })
    .on('end',   (event, d) => {
      if (!event.active) sim.alphaTarget(0);
      // re-anchor to the category column; free Y
      d.fx = columnX(d);
      d.fy = null;
    }));

node.append('circle')
  .attr('r', d => 5 + Math.sqrt(d.degree) * 2.1)
  .attr('fill', d => color(d.category))
  .attr('class', 'g-node-circle')
  .attr('stroke-width', d => topByCategory[d.category]?.has(d.id) ? 2 : 1.4)
  .attr('stroke-dasharray', d => d.estado === 'stub' ? '2 2' : null);

// Labels are centered BELOW the node and truncated to fit the column width,
// so they never bleed into a neighbouring column.
const CHAR_PX = 5.5;
const maxLabelChars = Math.max(10, Math.floor((colWidth - 24) / CHAR_PX));
function truncate(s, n) { return (s || '').length > n ? s.slice(0, n - 1) + '…' : (s || ''); }
node.append('text')
  .attr('x', 0)
  .attr('y', d => 16 + Math.sqrt(d.degree) * 2.1)
  .attr('text-anchor', 'middle')
  .attr('class', d => 'g-node-label' + (topByCategory[d.category]?.has(d.id) ? ' g-label-major' : ' g-label-minor'))
  .attr('font-size', d => topByCategory[d.category]?.has(d.id) ? '12px' : '10.5px')
  .attr('pointer-events', 'none')
  .text(d => truncate(d.title, maxLabelChars));

node.append('title').text(d => d.title + ' — ' + (CAT_LABELS[d.category] || d.category) + ' · ' + d.degree + ' conexiones');

function isolatedMode() {
  return hiddenCats.size === catList.length - 1;
}
function updateLabelVisibility() {
  const showMinor = isolatedMode() || currentZoom >= 1.5;
  g.selectAll('text.g-label-minor').style('opacity', showMinor ? 1 : 0);
  // Column titles always visible
  colTitle.style('opacity', currentZoom < 0.7 ? 0.4 : 1);
}

let focused = null;
node.on('mouseover', (e, d) => { if (!focused) highlight(d.id, true); })
    .on('mouseout',  () => { if (!focused) clearHighlight(); })
    .on('click',     (e, d) => {
      e.stopPropagation();
      if (focused === d.id) { clearFocus(); return; }
      focused = d.id;
      highlight(focused, false);
      renderInfo(d);
    })
    .on('dblclick',  (e, d) => { e.stopPropagation(); window.location.href = d.id + '.html'; });

function highlight(id, tempHover) {
  node.classed('dim', n => !neighbors[id].has(n.id))
      .classed('highlight', n => n.id === id)
      .classed('neighbor', n => n.id !== id && neighbors[id].has(n.id));
  link.classed('dim', l => l.source.id !== id && l.target.id !== id)
      .classed('highlight', l => l.source.id === id || l.target.id === id)
      .attr('marker-end', l => (l.source.id === id || l.target.id === id) ? 'url(#arrow-hot)' : 'url(#arrow)');
  // While focused, force-show neighbor labels even if minor
  g.selectAll('text.g-label-minor').style('opacity', function(d) {
    if (!d) return null;
    if (neighbors[id].has(d.id)) return 1;
    return isolatedMode() || currentZoom >= 1.5 ? 1 : 0;
  });
}
function clearHighlight() {
  node.classed('dim', false).classed('highlight', false).classed('neighbor', false);
  link.classed('dim', false).classed('highlight', false).attr('marker-end', 'url(#arrow)');
  updateLabelVisibility();
}
function clearFocus() { focused = null; clearHighlight(); renderInfo(null); }

function applyCategoryFilter() {
  node.style('display', n => hiddenCats.has(n.category) ? 'none' : null);
  link.style('display', l => (hiddenCats.has(l.source.category) || hiddenCats.has(l.target.category)) ? 'none' : null);
  colBg.attr('fill-opacity', d => hiddenCats.has(d) ? 0.01 : (isolatedMode() ? 0.1 : 0.045));
  colTitle.style('opacity', d => hiddenCats.has(d) ? 0.15 : 1);
  updateLabelVisibility();
  renderMini();
}

function fitToView(target) {
  // target: 'isolated' (only visible nodes), 'all' (full graph), or undefined
  const targets = (target === 'isolated' || (target === undefined && hiddenCats.size > 0))
    ? nodes.filter(n => !hiddenCats.has(n.category))
    : nodes;
  if (!targets.length) return;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  targets.forEach(n => {
    if (typeof n.x !== 'number') return;
    minX = Math.min(minX, n.x); maxX = Math.max(maxX, n.x);
    minY = Math.min(minY, n.y); maxY = Math.max(maxY, n.y);
  });
  if (!isFinite(minX)) return;
  const padX = 120, padY = 80;
  const bw = (maxX - minX) + padX * 2;
  const bh = (maxY - minY) + padY * 2;
  const scale = Math.min(viewW / bw, viewH / bh, 1.8);
  const tx = viewW / 2 - ((minX + maxX) / 2) * scale;
  const ty = viewH / 2 - ((minY + maxY) / 2) * scale;
  svg.transition().duration(650).call(zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
}

function toggleIsolate(c) {
  const wasIsolated = isolatedMode() && !hiddenCats.has(c);
  if (wasIsolated) {
    // un-isolate
    hiddenCats.clear();
    document.querySelectorAll('.legend-btn').forEach(b => b.classList.remove('off'));
  } else {
    hiddenCats.clear();
    catList.forEach(other => { if (other !== c) hiddenCats.add(other); });
    document.querySelectorAll('.legend-btn').forEach(btn => {
      if (btn.dataset.cat === c) btn.classList.remove('off');
      else btn.classList.add('off');
    });
  }
  applyCategoryFilter();
  sim.alpha(0.4).restart();
  setTimeout(() => fitToView(), 250);
}

// Top safety margin so nodes never enter the title area
const TOP_MARGIN = 90;
sim.on('tick', () => {
  // Clamp y so the topmost nodes never collide with the column titles
  nodes.forEach(n => { if (n.y < TOP_MARGIN) n.y = TOP_MARGIN; });
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
  renderMini();
});

// --- Toggle de aristas semánticas (embeddings) ---
const semCount = links.filter(l => l.kind === 'sem').length;
if (semCount) {
  const semBtn = document.createElement('button');
  semBtn.className = 'legend-btn sem-toggle';
  semBtn.innerHTML = '<span class="swatch swatch-sem"></span>' +
                     '<span class="legend-label">Afinidad semántica</span>' +
                     '<span class="legend-count">' + semCount + '</span>';
  let semOn = true;
  semBtn.onclick = () => {
    semOn = !semOn;
    semBtn.classList.toggle('off', !semOn);
    link.filter(d => d.kind === 'sem').style('display', semOn ? null : 'none');
  };
  const host = document.getElementById('graph-legend');
  if (host) host.appendChild(semBtn);
}

// --- Legend with category counts ---
const legendEl = document.getElementById('graph-legend');
const catCount = {};
nodes.forEach(n => { catCount[n.category] = (catCount[n.category]||0) + 1; });
catList.forEach(c => {
  const btn = document.createElement('button');
  btn.className = 'legend-btn';
  btn.dataset.cat = c;
  btn.innerHTML = '<span class="swatch" style="background:' + color(c) + '"></span>' +
                  '<span class="legend-label">' + (CAT_LABELS[c] || c) + '</span>' +
                  '<span class="legend-count">' + (catCount[c]||0) + '</span>';
  btn.onclick = () => {
    if (hiddenCats.has(c)) { hiddenCats.delete(c); btn.classList.remove('off'); }
    else { hiddenCats.add(c); btn.classList.add('off'); }
    applyCategoryFilter();
  };
  legendEl.appendChild(btn);
});

const isoEl = document.getElementById('graph-isolate');
if (isoEl) {
  const allBtn = document.createElement('button');
  allBtn.className = 'iso-btn iso-all';
  allBtn.textContent = '↺ Todas';
  allBtn.onclick = () => {
    hiddenCats.clear();
    document.querySelectorAll('.legend-btn').forEach(b => b.classList.remove('off'));
    applyCategoryFilter();
    setTimeout(() => fitToView('all'), 100);
  };
  isoEl.appendChild(allBtn);
  catList.forEach(c => {
    const b = document.createElement('button');
    b.className = 'iso-btn';
    b.title = 'Aislar ' + (CAT_LABELS[c]||c);
    b.innerHTML = '<span class="swatch" style="background:'+color(c)+'"></span><span class="iso-label">'+(CAT_LABELS[c]||c)+'</span>';
    b.onclick = () => toggleIsolate(c);
    isoEl.appendChild(b);
  });
}

const infoEl = document.getElementById('graph-info');
function renderInfo(d) {
  if (!infoEl) return;
  if (!d) { infoEl.classList.remove('visible'); infoEl.innerHTML = ''; return; }
  const nbrs = [...neighbors[d.id]].filter(id => id !== d.id);
  const byCat = {};
  nbrs.forEach(id => {
    const n = nodes.find(x => x.id === id);
    if (!n) return;
    (byCat[n.category] = byCat[n.category] || []).push(n);
  });
  let html = '<div class="info-head">'
    + '<span class="info-swatch" style="background:'+color(d.category)+'"></span>'
    + '<div class="info-titles"><div class="info-title">'+escapeHtml(d.title)+'</div>'
    + '<div class="info-cat">'+(CAT_LABELS[d.category]||d.category)+' · '+d.degree+' conexiones</div></div>'
    + '<button class="info-close" title="Cerrar">×</button></div>'
    + '<a class="info-open" href="'+d.id+'.html">Abrir nota →</a>';
  if (nbrs.length) {
    html += '<div class="info-section-title">Conectado con</div>';
    Object.keys(byCat).sort((a,b) => catList.indexOf(a) - catList.indexOf(b)).forEach(c => {
      html += '<div class="info-group"><div class="info-group-head"><span class="swatch" style="background:'+color(c)+'"></span>'+(CAT_LABELS[c]||c)+' <span class="info-count">'+byCat[c].length+'</span></div><ul>';
      byCat[c].sort((a,b)=>a.title.localeCompare(b.title)).forEach(n => {
        html += '<li><a href="'+n.id+'.html" data-node="'+n.id+'" class="info-nbr">'+escapeHtml(n.title)+'</a></li>';
      });
      html += '</ul></div>';
    });
  }
  infoEl.innerHTML = html;
  infoEl.classList.add('visible');
  infoEl.querySelector('.info-close').onclick = () => clearFocus();
  infoEl.querySelectorAll('.info-nbr').forEach(a => {
    a.addEventListener('mouseenter', () => { node.classed('hover-trace', n => n.id === a.dataset.node); });
    a.addEventListener('mouseleave', () => { node.classed('hover-trace', false); });
    a.addEventListener('click', (e) => {
      if (!e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        const id = a.dataset.node;
        const n = nodes.find(x => x.id === id);
        if (n) { focused = id; highlight(id, false); centerOn(n); renderInfo(n); }
      }
    });
  });
}
function escapeHtml(s) {
  return (s+'').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function centerOn(n) {
  if (typeof n.x !== 'number') return;
  const scale = Math.max(currentZoom, 1.3);
  const tx = viewW / 2 - n.x * scale;
  const ty = viewH / 2 - n.y * scale;
  svg.transition().duration(450).call(zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
}

document.getElementById('graph-reset').onclick = () => {
  hiddenCats.clear();
  document.querySelectorAll('.legend-btn').forEach(b => b.classList.remove('off'));
  applyCategoryFilter();
  clearFocus();
  searchInput.value = '';
  applySearchHighlight('');
  sim.alpha(0.6).restart();
  setTimeout(() => fitToView('all'), 300);
};

const searchInput = document.getElementById('graph-search');
const searchResultsEl = document.getElementById('graph-search-results');
const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');

function applySearchHighlight(query) {
  const q = norm((query || '').trim());
  if (!q) {
    node.classed('g-match', false).classed('g-search-dim', false);
    link.classed('g-search-dim', false);
    if (searchResultsEl) { searchResultsEl.innerHTML = ''; searchResultsEl.classList.remove('visible'); }
    return;
  }
  const matches = [];
  nodes.forEach(n => {
    if (norm(n.title).includes(q) || norm(n.id).includes(q)) matches.push(n);
  });
  matches.sort((a,b) => b.degree - a.degree);
  const matchSet = new Set(matches.map(n => n.id));
  node.classed('g-match', d => matchSet.has(d.id))
      .classed('g-search-dim', d => !matchSet.has(d.id));
  link.classed('g-search-dim', l => !matchSet.has(l.source.id) && !matchSet.has(l.target.id));
  if (searchResultsEl) {
    if (matches.length === 0) {
      searchResultsEl.innerHTML = '<div class="search-empty">Sin resultados</div>';
    } else {
      const top = matches.slice(0, 12);
      searchResultsEl.innerHTML = top.map(n =>
        '<button class="search-item" data-id="'+n.id+'">' +
        '<span class="swatch" style="background:'+color(n.category)+'"></span>' +
        '<span class="search-item-title">'+escapeHtml(n.title)+'</span>' +
        '<span class="search-item-cat">'+(CAT_LABELS[n.category]||n.category)+'</span>' +
        '</button>'
      ).join('') + (matches.length > 12 ? '<div class="search-empty">+'+(matches.length-12)+' más…</div>' : '');
      searchResultsEl.querySelectorAll('.search-item').forEach(b => {
        b.onclick = () => {
          const id = b.dataset.id;
          const n = nodes.find(x => x.id === id);
          if (!n) return;
          focused = id; highlight(id, false); centerOn(n); renderInfo(n);
          searchResultsEl.classList.remove('visible');
        };
      });
    }
    searchResultsEl.classList.add('visible');
  }
  if (matches.length > 0) centerOn(matches[0]);
}
searchInput.addEventListener('input', (e) => applySearchHighlight(e.target.value));
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') { searchInput.value = ''; applySearchHighlight(''); searchInput.blur(); }
  else if (e.key === 'Enter') {
    const first = searchResultsEl && searchResultsEl.querySelector('.search-item');
    if (first) first.click();
  }
});
searchInput.addEventListener('focus', () => { if (searchInput.value) applySearchHighlight(searchInput.value); });
document.addEventListener('click', (e) => {
  if (searchResultsEl && !searchResultsEl.contains(e.target) && e.target !== searchInput) {
    searchResultsEl.classList.remove('visible');
  }
});

document.addEventListener('keydown', (e) => {
  if (document.activeElement === searchInput) return;
  if (e.key === '/' || e.key === 'f') { e.preventDefault(); searchInput.focus(); }
  else if (e.key === 'Escape') { clearFocus(); searchInput.value = ''; applySearchHighlight(''); }
  else if (e.key === '0') { fitToView('all'); }
  else if (e.key === '+' || e.key === '=') { svg.transition().duration(200).call(zoomBehavior.scaleBy, 1.3); }
  else if (e.key === '-') { svg.transition().duration(200).call(zoomBehavior.scaleBy, 0.7); }
});

const zoomInBtn = document.getElementById('zoom-in');
const zoomOutBtn = document.getElementById('zoom-out');
const zoomFitBtn = document.getElementById('zoom-fit');
if (zoomInBtn) zoomInBtn.onclick = () => svg.transition().duration(200).call(zoomBehavior.scaleBy, 1.3);
if (zoomOutBtn) zoomOutBtn.onclick = () => svg.transition().duration(200).call(zoomBehavior.scaleBy, 0.7);
if (zoomFitBtn) zoomFitBtn.onclick = () => fitToView('all');

// Mini-map
const miniSvg = d3.select('#graph-mini svg');
const miniW = 200, miniH = 140;
var miniNodes = null, miniViewport = null, miniBounds = null, miniLast = 0;
if (miniSvg.size()) {
  miniSvg.attr('viewBox', '0 0 ' + miniW + ' ' + miniH).append('rect')
    .attr('width', miniW).attr('height', miniH).attr('class', 'mini-bg');
  miniNodes = miniSvg.append('g');
  miniViewport = miniSvg.append('rect').attr('class', 'mini-viewport').attr('fill', 'none');
  miniSvg.on('click', function(e) {
    const rect = miniSvg.node().getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width * miniW;
    const py = (e.clientY - rect.top) / rect.height * miniH;
    if (!miniBounds) return;
    const [minX, minY, maxX, maxY] = miniBounds;
    const sx = (maxX - minX) / miniW;
    const sy = (maxY - minY) / miniH;
    const gx = minX + px * sx;
    const gy = minY + py * sy;
    const tx = viewW / 2 - gx * currentZoom;
    const ty = viewH / 2 - gy * currentZoom;
    svg.transition().duration(300).call(zoomBehavior.transform, d3.zoomIdentity.translate(tx, ty).scale(currentZoom));
  });
}
function renderMini() {
  if (!miniNodes) return;
  const now = performance.now();
  if (now - miniLast < 100) return;
  miniLast = now;
  const visible = nodes.filter(n => !hiddenCats.has(n.category) && typeof n.x === 'number');
  if (!visible.length) return;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  visible.forEach(n => {
    if (n.x < minX) minX = n.x; if (n.x > maxX) maxX = n.x;
    if (n.y < minY) minY = n.y; if (n.y > maxY) maxY = n.y;
  });
  if (!isFinite(minX)) return;
  const padX = (maxX - minX) * 0.06 || 40;
  const padY = (maxY - minY) * 0.06 || 40;
  minX -= padX; minY -= padY; maxX += padX; maxY += padY;
  miniBounds = [minX, minY, maxX, maxY];
  const sx = miniW / (maxX - minX);
  const sy = miniH / (maxY - minY);
  const dots = miniNodes.selectAll('circle').data(visible, d => d.id);
  dots.enter().append('circle')
    .merge(dots)
    .attr('cx', d => (d.x - minX) * sx)
    .attr('cy', d => (d.y - minY) * sy)
    .attr('r', d => Math.max(0.8, Math.sqrt(d.degree) * 0.45))
    .attr('fill', d => color(d.category));
  dots.exit().remove();
  const t = d3.zoomTransform(svg.node());
  const vx = (-t.x / t.k - minX) * sx;
  const vy = (-t.y / t.k - minY) * sy;
  const vw = (viewW / t.k) * sx;
  const vh = (viewH / t.k) * sy;
  miniViewport
    .attr('x', Math.max(0, vx)).attr('y', Math.max(0, vy))
    .attr('width', Math.min(miniW, Math.max(0, vw)))
    .attr('height', Math.min(miniH, Math.max(0, vh)));
}

window.addEventListener('resize', () => {
  const w = window.innerWidth, h = window.innerHeight - 60;
  svg.attr('width', w).attr('height', h);
});

// Initial fit-to-view after simulation settles a bit
setTimeout(() => { fitToView('all'); positionTitles(); }, 800);
setTimeout(positionTitles, 100);
positionTitles();
updateLabelVisibility();
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
(function(){{try{{var t=localStorage.getItem('adg-theme')||'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
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
    {"slug": "casos/espana-europa/inigo-cabacas", "title": "Iñigo Cabacas (Bilbao 2012)", "country": "España", "lng": -2.9253, "lat": 43.2630, "type": "muerto", "year": 2012},
    {"slug": "casos/espana-europa/ester-quintana", "title": "Ester Quintana (Barcelona 2012)", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "ojo", "year": 2012},
    {"slug": "casos/espana-europa/juan-andres-benitez", "title": "Juan Andrés Benítez (Raval 2013)", "country": "España", "lng": 2.1700, "lat": 41.3793, "type": "muerto", "year": 2013},
    {"slug": "casos/espana-europa/roger-espanol", "title": "Roger Español (1-O 2017)", "country": "España", "lng": 2.1850, "lat": 41.4030, "type": "ojo", "year": 2017},
    {"slug": "casos/espana-europa/africa-pablo-hasel", "title": "África (Pablo Hasél 2021)", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "ojo", "year": 2021},
    {"slug": "casos/espana-europa/olga-proces", "title": "Olga (Procés 2019)", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "lesion", "year": 2019},
    {"slug": "casos/espana-europa/antonio-c-badalona", "title": "Antonio C. (Badalona 2021, taser)", "country": "España", "lng": 2.2454, "lat": 41.4500, "type": "muerto", "year": 2021},
    {"slug": "casos/espana-europa/carles-guillot", "title": "Carles Guillot", "country": "España", "lng": 2.1734, "lat": 41.3851, "type": "ojo", "year": 2010},
    {"slug": "casos/espana-europa/tarajal-2014", "title": "Tarajal — 14 muertos (2014)", "country": "España", "lng": -5.3625, "lat": 35.8894, "type": "masacre", "year": 2014},
    {"slug": "casos/espana-europa/roger-garcia-foam-2019", "title": "Roger García (Proces 2019, foam)", "country": "España", "lng": 2.1750, "lat": 41.3880, "type": "ojo", "year": 2019},
    {"slug": "casos/espana-europa/abdelillah-foam-2019", "title": "Abdelillah (Proces 2019, foam)", "country": "España", "lng": 2.1780, "lat": 41.3860, "type": "ojo", "year": 2019},
    {"slug": "casos/espana-europa/melilla-2022", "title": "Melilla — 37 muertos (2022)", "country": "España", "lng": -2.9381, "lat": 35.2923, "type": "masacre", "year": 2022},
    # Francia
    {"slug": "casos/espana-europa/remi-fraisse", "title": "Rémi Fraisse (Sivens 2014)", "country": "Francia", "lng": 1.8, "lat": 43.9, "type": "muerto", "year": 2014},
    {"slug": "casos/espana-europa/steve-maia-canico", "title": "Steve Maia Caniço (Nantes 2019)", "country": "Francia", "lng": -1.5536, "lat": 47.2184, "type": "muerto", "year": 2019},
    # UK
    {"slug": "casos/espana-europa/stephen-geddis", "title": "Stephen Geddis (Belfast 1975)", "country": "Reino Unido", "lng": -5.9301, "lat": 54.5973, "type": "muerto", "year": 1975},
    {"slug": "casos/internacionales/rodney-king-1991", "title": "Rodney King (Los Ángeles 1991)", "country": "Estados Unidos", "lng": -118.2437, "lat": 34.0522, "type": "lesion", "year": 1991},
    # LATAM
    {"slug": "casos/latam/fabiola-campillai", "title": "Fabiola Campillai (Chile 2019)", "country": "Chile", "lng": -70.6483, "lat": -33.4489, "type": "ceguera", "year": 2019},
    {"slug": "casos/latam/chile-estallido-2019", "title": "Chile estallido 2019 — 460+ ojos", "country": "Chile", "lng": -70.6483, "lat": -33.4489, "type": "masacre", "year": 2019},
    {"slug": "casos/latam/rufo-chacon", "title": "Rufo Chacón (Venezuela 2019)", "country": "Venezuela", "lng": -72.2225, "lat": 7.7669, "type": "ceguera", "year": 2019},
    {"slug": "casos/latam/juan-pablo-pernalete", "title": "Juan Pablo Pernalete (Caracas 2017)", "country": "Venezuela", "lng": -66.9036, "lat": 10.4806, "type": "muerto", "year": 2017},
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
    {"slug": "casos/internacionales/angelo-garand-francia-2017", "title": "Angelo Garand — abatido por GIGN (2017)", "country": "Francia", "lng": 1.2500, "lat": 47.5000, "type": "muerto", "year": 2017},
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
(function(){try{var t=localStorage.getItem('adg-theme')||'light';document.documentElement.setAttribute('data-theme',t);}catch(e){}})();
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
(function(){{try{{var t=localStorage.getItem('adg-theme')||'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
<script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body class="graph-page">
<header class="graph-header">
  <a class="brand" href="index.html">◂ Artefactos de Guerra</a>
  <span class="graph-title">Grafo de conexiones</span>
  <div class="graph-search-wrap">
    <input id="graph-search" type="search" placeholder="Buscar nodo…  (atajo: /)" autocomplete="off" spellcheck="false">
    <div id="graph-search-results" class="search-results"></div>
  </div>
  <div class="graph-actions">
    <button id="zoom-out" title="Zoom out (-)">−</button>
    <button id="zoom-fit" title="Centrar (0)">⊙</button>
    <button id="zoom-in" title="Zoom in (+)">+</button>
    <button id="graph-reset" title="Reset todo">↺</button>
    <button id="theme-toggle" class="theme-toggle" type="button" title="Cambiar tema">◐</button>
  </div>
</header>
<button id="graph-panel-open" class="graph-panel-open" title="Abrir panel (P)" aria-label="Abrir panel">☰</button>
<aside class="graph-panel">
  <button id="graph-panel-close" class="graph-panel-close" title="Ocultar panel (P)" aria-label="Ocultar panel">◂</button>
  <div class="panel-section">
    <h4>Categorías</h4>
    <div id="graph-legend"></div>
  </div>
  <div class="panel-section">
    <h4>Aislar</h4>
    <div id="graph-isolate" class="isolate-row"></div>
  </div>
  <details class="panel-help">
    <summary>Cómo navegar</summary>
    <ul>
      <li><b>Hover</b>: resalta vecinos.</li>
      <li><b>Click</b>: fija foco y abre panel.</li>
      <li><b>Doble click</b>: abre la nota.</li>
      <li><b>/</b> o <b>f</b>: buscar.</li>
      <li><b>+ / −</b>: zoom. <b>0</b>: centrar. <b>Esc</b>: reset.</li>
      <li><b>P</b>: mostrar / ocultar este panel.</li>
      <li><b>Click leyenda</b>: ocultar categoría.</li>
      <li><b>Aislar</b>: muestra solo esa categoría.</li>
    </ul>
  </details>
</aside>
<aside id="graph-info" class="graph-info"></aside>
<div id="graph-mini" class="graph-mini" title="Mini-mapa — clic para centrar"><svg></svg></div>
<div id="graph"></div>
<script>{js}</script>
<script>
(function(){{
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.addEventListener('click', function(){{
    var cur = document.documentElement.getAttribute('data-theme') || 'dark';
    var nxt = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nxt);
    try {{ localStorage.setItem('adg-theme', nxt); }} catch (e) {{}}
  }});

  // Panel toggle (collapse / expand the left sidebar)
  var body = document.body;
  var openBtn = document.getElementById('graph-panel-open');
  var closeBtn = document.getElementById('graph-panel-close');
  function setPanel(collapsed) {{
    body.classList.toggle('panel-collapsed', collapsed);
    try {{ localStorage.setItem('adg-graph-panel', collapsed ? 'off' : 'on'); }} catch (e) {{}}
  }}
  try {{
    if (localStorage.getItem('adg-graph-panel') === 'off') body.classList.add('panel-collapsed');
  }} catch (e) {{}}
  if (openBtn) openBtn.addEventListener('click', function(){{ setPanel(false); }});
  if (closeBtn) closeBtn.addEventListener('click', function(){{ setPanel(true); }});
  document.addEventListener('keydown', function(e){{
    if (e.key === 'p' || e.key === 'P') {{
      if (document.activeElement && document.activeElement.tagName === 'INPUT') return;
      setPanel(!body.classList.contains('panel-collapsed'));
    }}
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

CATEGORY_DESC = {
    "historia": "De dónde viene cada artefacto: genealogías de la porra al taser, 1850 a hoy.",
    "autores-y-referencias": "Quién analiza y documenta: investigadores, testimonios y organizaciones.",
    "ferias-de-armas": "Dónde se venden: FEINDEF, EUROSATORY y el circuito internacional.",
    "empresas-de-armas": "Quién las fabrica: fichas de industria, renders y publicidad.",
    "usos-de-armas": "Cómo se entrena su uso: doctrina, congresos y formación policial.",
    "casos": "Las víctimas, caso a caso, en tres continentes.",
    "marco-legal": "Qué dice la ley: ONU, TEDH, normativa y bibliografía crítica.",
    "herramientas": "La infraestructura técnica y periodística para auditarlas.",
    "_root": "Índice y material general.",
}

CATEGORY_COLORS = {
    "ferias-de-armas": "#e05d3d",
    "empresas-de-armas": "#f0a94a",
    "casos": "#d33f6a",
    "usos-de-armas": "#6eb8d6",
    "autores-y-referencias": "#f5d05e",
    "herramientas": "#46d4c6",
    "marco-legal": "#a78bfa",
    "historia": "#5fd49e",
    "_root": "#aaaaaa",
}


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

    # grados de conexión para elegir las entradas clave de cada categoría
    inbound = {}
    for n in notes:
        for raw in n["links_raw"]:
            t = raw.split("|")[0].split("#")[0].strip()
            stem = Path(t).stem.lower()
            inbound[stem] = inbound.get(stem, 0) + 1

    def note_key(n):
        stem = Path(n["slug"]).stem.lower()
        return inbound.get(stem, 0)

    def render_items(note_list):
        items = []
        for n in sorted(note_list, key=lambda x: x["title"].lower()):
            items.append(f'<li><a href="{n["slug"]}.html">{html.escape(n["title"])}</a></li>')
        return "".join(items)

    cards_html = []
    cat_num = 0
    for cat in CATEGORY_ORDER:
        if cat not in tree:
            continue
        cat_num += 1
        label = CATEGORY_LABELS.get(cat, cat)
        color = CATEGORY_COLORS.get(cat, "#999")
        cat_notes = [n for n in notes if n["category"] == cat]
        count = len(cat_notes)

        # entradas clave: primero los 00-índices, luego las más referenciadas
        indices = [n for n in cat_notes if Path(n["slug"]).stem.startswith("00")]
        rest = sorted(
            [n for n in cat_notes if not Path(n["slug"]).stem.startswith("00")],
            key=note_key, reverse=True,
        )
        top = (indices + rest)[:6]
        top_html = "".join(
            f'<li><a href="{n["slug"]}.html">{html.escape(n["title"])}</a></li>'
            for n in top
        )

        # lista completa plegada, agrupada por subcategoría
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
        full_html = (
            f'<details class="cat-all"><summary>Todas ({count})</summary>'
            f'{"".join(inner_parts)}</details>'
        ) if count > len(top) else ""

        desc = CATEGORY_DESC.get(cat, "")
        cards_html.append(
            f'<section class="home-card" style="--cat-color:{color}">'
            f'<h2><span><span class="cat-num">{cat_num:02d}</span>{html.escape(label)}</span>'
            f'<span class="cat-count">{count}</span></h2>'
            f'<p class="cat-desc">{html.escape(desc)}</p>'
            f'<ul>{top_html}</ul>'
            f'{full_html}'
            f'</section>'
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
(function(){{try{{var t=localStorage.getItem('adg-theme')||'light';document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
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
      <p class="tagline">Vademécum de investigación · una película de Jorge Caballero</p>
      <h1>Artefactos de <em>guerra.</em></h1>
      <div class="stats"><span>{stats['total']} notas</span> · <span>{stats['categorias']} categorías</span> · <span>{stats['casos']} casos</span> · <span>{stats['empresas']} fichas de industria</span></div>
      <div class="home-cta">
        <a class="cta-btn primary" href="timeline.html">Cronología 1850 → 2026</a>
        <a class="cta-btn" href="map.html">Mapa mundial de casos</a>
        <a class="cta-btn" href="graph.html">Grafo de conexiones</a>
        <a class="cta-btn" href="casos/impacto-agregado.html">Impacto agregado · las cifras del daño</a>
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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,900;1,300&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root,
:root[data-theme="dark"] {
  --bg: #141312;
  --bg-panel: #1c1917;
  --bg-hover: #292524;
  --fg: #e7e5e4;
  --fg-dim: #a8a29e;
  --accent: #f59e0b;
  --border: #2b2725;
  --chip-bg: #292524;
  --link: #fbbf5f;
  --panel-strong: #191614;
  --shadow: none;
  --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}
:root[data-theme="light"] {
  --bg: #fafaf9;
  --bg-panel: #ffffff;
  --bg-hover: #f5f5f4;
  --fg: #1c1917;
  --fg-dim: #78716c;
  --accent: #b91c1c;
  --border: #e7e5e4;
  --chip-bg: #f5f5f4;
  --link: #b91c1c;
  --panel-strong: #fafaf9;
  --shadow: none;
  --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}
* { box-sizing: border-box; }
html, body { margin:0; padding:0; background:var(--bg); color:var(--fg); font: 16px/1.7 "Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; letter-spacing: -0.01em; }
::selection { background: var(--fg); color: var(--bg); }
a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }
.home-card ul a, .note-body a, .nav-group li a { color: var(--fg); border-bottom: 1px solid var(--border); }
.home-card ul a:hover, .note-body a:hover { color: var(--accent); border-bottom-color: var(--accent); text-decoration: none; }
.note-body a[href^="http"] { border-bottom-style: dashed; }

.layout { display: grid; grid-template-columns: 260px 1fr; min-height: 100vh; transition: grid-template-columns .25s ease; }
.sidebar { background: var(--bg-panel); border-right: 1px solid var(--border); padding: 18px 14px; position: sticky; top:0; height:100vh; overflow-y:auto; font-size: 13px; transition: transform .25s ease, opacity .2s; }

/* Sidebar collapsed state */
body.sidebar-collapsed .layout { grid-template-columns: 0 1fr; }
body.sidebar-collapsed .sidebar { transform: translateX(-100%); opacity: 0; pointer-events: none; }
body.sidebar-collapsed .content { padding-left: 64px; }

/* Floating "open menu" button (visible only when sidebar is collapsed) */
.sidebar-open-btn { position: fixed; top: 16px; left: 16px; z-index: 50; width: 38px; height: 38px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; cursor: pointer; display: none; align-items: center; justify-content: center; font-size: 16px; color: var(--fg); box-shadow: 0 2px 10px rgba(0,0,0,.18); transition: border-color .15s, background .15s; }
.sidebar-open-btn:hover { border-color: var(--accent); background: var(--bg-hover); }
body.sidebar-collapsed .sidebar-open-btn { display: inline-flex; }

/* Close button inside the sidebar */
.sidebar-close-btn { position: absolute; top: 12px; right: 10px; width: 26px; height: 26px; background: transparent; color: var(--fg-dim); border: 0; border-radius: 0; font-size: 13px; cursor: pointer; padding: 0; display: flex; align-items: center; justify-content: center; }
.sidebar-close-btn:hover { color: var(--fg); background: var(--bg-hover); }
.brand { font-family: var(--mono); font-weight:700; font-size:13px; letter-spacing:.14em; text-transform: uppercase; display:block; margin-bottom:18px; color:var(--fg); }
.search-box input { width:100%; padding:10px 14px; background:var(--bg); color:var(--fg); border:1px solid var(--border); border-radius: 0; font-size:14px; transition: border-color .15s; }
.search-box input:focus { outline:none; border-color:var(--accent); box-shadow: 0 0 0 3px rgba(224,93,61,0.1); }
.nav { margin-top: 18px; font-size: 14px; }
.nav-group { margin-bottom: 12px; }
.nav-group summary { cursor: pointer; font-family: var(--mono); font-weight:700; color:var(--fg-dim); padding:6px 4px; text-transform:uppercase; font-size:10px; letter-spacing:.14em; }
.nav-group ul { list-style:none; padding:2px 0 8px 8px; margin:0; }
.nav-group li a { display:block; padding:5px 8px; border-radius: 0; color:var(--fg); font-size:13.5px; border-left:2px solid transparent; transition: none; }
.nav-group li a:hover { background:var(--bg-hover); text-decoration:none; border-left-color:var(--accent); }
.nav-group li a.active { background:var(--bg-hover); border-left-color:var(--accent); color:var(--accent); font-weight: 600; }
.nav-chip { display: inline-block; margin-left: 6px; padding: 1px 6px; font-size: 10px; font-weight: 600; background: var(--accent); color: #fff; border-radius: 0; vertical-align: middle; }
.nav-chip-done { background: #5fd49e; color: #0b1a10; }
.sidebar-legend { padding: 8px 12px; margin-bottom: 10px; font-size: 11px; color: var(--text-muted); border: 1px dashed var(--border); border-radius: 0; line-height: 1.6; }
.sidebar-legend .nav-chip { margin-left: 0; margin-right: 4px; }
.file-warning { background: #ffd54a; color: #1a1a1a; padding: 10px 16px; font-size: 13px; line-height: 1.5; border-bottom: 2px solid #c89a00; }
.file-warning code { background: rgba(0,0,0,0.12); padding: 1px 5px; border-radius: 0; font-size: 12px; }
.file-warning a { color: #6e3a00; font-weight: 700; }

/* TOC lateral (notas largas) */
.note-toc { margin: 0 0 32px 0; padding: 0; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; font-size: 14px; }
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
.tl-item .tl-card { background: var(--bg-panel); border: 1px solid var(--border); border-left: 3px solid var(--era-color, var(--accent)); border-radius: 0; padding: 14px 18px; }
.tl-item .tl-card h3 { margin: 0 0 8px 0; font-size: 15px; color: var(--fg); }
.tl-item .tl-content { font-size: 13px; line-height: 1.55; color: var(--fg); }
.tl-item .tl-content p { margin: 6px 0; }
.tl-item .tl-content blockquote { border-left: 2px solid var(--era-color, var(--accent)); margin: 8px 0; padding: 4px 12px; background: var(--bg-hover); font-style: italic; color: var(--fg-dim); border-radius: 0; }
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
.map-legend { position: fixed; top: 80px; left: 20px; width: 200px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; padding: 14px 16px; z-index: 5; backdrop-filter: blur(6px); }
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
#map-tooltip { display: none; position: absolute; pointer-events: none; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; padding: 8px 12px; font-size: 12px; color: var(--fg); z-index: 100; max-width: 280px; box-shadow: var(--shadow); }
#map-tooltip .tt-country { color: var(--fg-dim); font-size: 11px; }
.nav-subgroup { margin: 4px 0 4px 6px; padding-left: 8px; border-left: 1px solid var(--border); }
.nav-subgroup summary { cursor: pointer; font-family: var(--mono); font-weight:500; color:var(--fg-dim); padding:4px 4px; font-size:10px; text-transform: uppercase; letter-spacing:.12em; }
.nav-subgroup ul { padding-left: 6px; }
.nav-direct { margin-bottom: 4px; }
.home-subcat { margin: 14px 0 6px 0; font-size: 12px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); font-weight: 600; }
.graph-link { display:block; margin-top:14px; padding:10px 12px; background:var(--bg-hover); border:1px solid var(--border); border-radius: 0; font-size:13px; text-align:center; color:var(--fg); }
.graph-link:hover { border-color:var(--accent); text-decoration:none; }
.sidebar-tools { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 6px; margin: 12px 0 16px 0; }
.sidebar-tools a, .sidebar-tools button { padding: 8px 0; background: var(--bg-hover); border: 1px solid var(--border); border-radius: 0; font-size: 12px; font-weight: 500; text-align: center; color: var(--fg-dim); cursor: pointer; text-decoration: none; transition: all .15s; }
.sidebar-tools a:hover, .sidebar-tools button:hover { border-color: var(--accent); color: var(--accent); background: var(--bg); text-decoration: none; }
.theme-toggle { width: 36px; padding: 8px 0; background: var(--bg-hover); border: 1px solid var(--border); border-radius: 0; font-size: 14px; color: var(--fg-dim); cursor: pointer; transition: all .15s; }
.theme-toggle:hover { border-color: var(--accent); }
.theme-toggle:hover { border-color: var(--accent); }

/* Sticky audio player */
.sticky-audio { position: sticky; top: 0; z-index: 20; margin: 0 -52px 24px -52px; padding: 14px 52px; background: var(--panel-strong); border-bottom: 1px solid var(--border); box-shadow: var(--shadow); }
.sticky-audio audio { width: 100%; display: block; }
.sticky-audio-meta { font-size: 11px; color: var(--fg-dim); margin-top: 6px; text-transform: uppercase; letter-spacing: .6px; }

/* YouTube embeds */
.yt-embed { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; margin: 16px 0; border-radius: 0; border: 1px solid var(--border); background: #000; }
.yt-embed iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }

/* Audio wrap (inside body) */
.audio-wrap { margin: 14px 0; padding: 12px 14px; background: var(--panel-strong); border: 1px solid var(--border); border-radius: 0; }
.audio-wrap audio { width: 100%; display: block; }
.audio-meta { font-size: 11px; color: var(--fg-dim); margin-top: 6px; }

/* Timecode links */
a.tc { color: var(--accent); font-variant-numeric: tabular-nums; font-weight: 600; text-decoration: none; padding: 0 2px; border-radius: 0; cursor: pointer; }
a.tc:hover { background: var(--accent); color: #fff; text-decoration: none; }

/* Sources (frontmatter) */
.sources { margin-top: 28px; }
.sources h4 { margin: 0 0 10px 0; font-size: 11px; text-transform: uppercase; letter-spacing: .6px; color: var(--fg-dim); }
.source-item { margin-bottom: 14px; }
.source-link { font-size: 12px; color: var(--fg-dim); word-break: break-all; margin-top: 4px; }
.source-text { padding: 10px 14px; background: var(--panel-strong); border: 1px solid var(--border); border-radius: 0; font-size: 13px; word-break: break-all; }

.content { padding: 48px 60px 80px 60px; max-width: 820px; margin: 0 auto; }
.note-header { margin-bottom: 36px; }
.breadcrumb { font-family: var(--mono); font-size: 10.5px; color: var(--accent); margin-bottom: 14px; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; display: flex; align-items: center; gap: 10px; }
.breadcrumb::before { content: ""; width: 28px; height: 1px; background: var(--accent); }
.note-header h1 { margin: 0 0 10px; font-size: clamp(30px, 4.2vw, 44px); line-height: 1.08; letter-spacing: -.03em; font-weight: 200; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { display:inline-block; padding:2px 8px; background:var(--chip-bg); border:1px solid var(--border); font-family: var(--mono); font-size:10px; letter-spacing:.1em; text-transform: uppercase; color:var(--fg-dim); }
.chip-tipo { background: transparent; color: var(--fg-dim); border-color: var(--border); }
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
.note-body code { background:var(--bg-hover); padding:2px 6px; border-radius: 0; font-size:.9em; }
.note-body pre { background:var(--bg); padding:14px; border-radius: 0; overflow:auto; border:1px solid var(--border); }
.note-body table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 14px; }
.note-body th, .note-body td { border: 1px solid var(--border); padding: 10px 12px; text-align: left; vertical-align: top; }
.note-body th { background: var(--bg-hover); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .3px; }
.note-body td { line-height: 1.5; }
.note-body ul, .note-body ol { padding-left: 22px; }
.note-body a.wikilink { color: var(--accent); border-bottom:1px dashed var(--fg-dim); }
.note-body a.wikilink.broken, .note-body .wikilink.broken { color: #c0392b; border-bottom:1px dashed #c0392b; cursor:help; }

/* legacy .sources rule — replaced by embed-aware version below */

/* .backlinks and .outlinks styled in links-block section below */

.home-header h1 { font-size: clamp(44px, 6vw, 72px); margin: 0 0 10px 0; letter-spacing: -.035em; font-weight: 200; line-height: 1; }
.home-header h1 em { font-style: italic; font-weight: 300; color: var(--accent); }
.tagline { font-family: var(--mono); font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: var(--fg-dim); margin: 0 0 14px 0; display: flex; align-items: center; gap: 10px; }
.tagline::before { content: ""; width: 28px; height: 1px; background: var(--accent); }
.stats { font-family: var(--mono); font-size: 11.5px; color: var(--fg-dim); display: flex; flex-wrap: wrap; gap: 6px 16px; letter-spacing: .04em; }
.stats span { color: var(--fg); font-weight: 600; }
.home-cta { margin-top: 20px; display: flex; flex-wrap: wrap; gap: 10px; }
.cta-btn { display: inline-block; padding: 11px 16px; border: 1px solid var(--border); color: var(--fg); font-family: var(--mono); font-size: 11px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; text-decoration: none; background: var(--bg-panel); transition: border-color .15s, background .15s, color .15s; }
.cta-btn:hover { border-color: var(--accent); text-decoration: none; background: var(--bg-hover); }
.cta-btn.primary { background: var(--fg); color: var(--bg); border-color: var(--fg); }
.cta-btn.primary:hover { background: var(--accent); border-color: var(--accent); color: #fff; }
.home-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; margin-top: 28px; }
.home-card { background: var(--bg-panel); border: 1px solid var(--border); border-top: 3px solid var(--cat-color, var(--accent)); padding: 20px 22px; }
.home-card h2 { margin:0 0 4px 0; font-family: var(--mono); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing:.14em; color: var(--fg); border:none; padding:0; display:flex; justify-content:space-between; align-items:baseline; }
.home-card h2 .cat-num { color: var(--cat-color, var(--accent)); margin-right: 8px; }
.home-card h2 .cat-count { font-weight: 400; color: var(--fg-dim); font-size: 11px; }
.home-card .cat-desc { font-size: 13.5px; line-height: 1.55; color: var(--fg-dim); margin: 0 0 12px 0; }
.home-card details.cat-all summary { cursor: pointer; font-family: var(--mono); font-size: 10.5px; letter-spacing: .1em; text-transform: uppercase; color: var(--accent); padding: 8px 0 2px; list-style: none; }
.home-card details.cat-all summary::-webkit-details-marker { display: none; }
.home-card details.cat-all summary::after { content: " ↓"; }
.home-card details.cat-all[open] summary::after { content: " ↑"; }
.home-card ul { list-style:none; padding:0; margin:0; }
.home-card li { padding: 6px 0; font-size: 14px; line-height: 1.4; }
.home-card li + li { border-top: 1px solid var(--border); }
.home-card li a { display: block; }
.home-card li:last-child { border-bottom: none; }

.graph-page { background: var(--bg); overflow: hidden; color: var(--fg); }
.graph-page svg text { fill: var(--fg); paint-order: stroke; stroke: var(--bg); stroke-width: 3px; stroke-linejoin: round; }
.graph-page .g-node-label { fill: var(--fg); }
.graph-page .g-label-major { font-weight: 600; }
.graph-page .g-label-minor { opacity: 0; transition: opacity .25s; }
.graph-page .g-node-circle { stroke: var(--bg); }
.graph-page .arrow-path { fill: var(--fg-dim); }
.graph-page .arrow-path-hot { fill: var(--accent); }
.graph-page .links line { stroke: var(--fg-dim) !important; stroke-opacity: 0.3; }
.graph-page .links line.dim { stroke-opacity: 0.05; }
.graph-page .links line.highlight { stroke: var(--accent) !important; stroke-opacity: 0.95; stroke-width: 2; }
.graph-page .nodes .node.highlight circle { stroke: var(--fg) !important; stroke-width: 3; filter: drop-shadow(0 0 8px var(--accent)); }
.graph-page .nodes .node.hover-trace circle { stroke: #ffd54a !important; stroke-width: 3; filter: drop-shadow(0 0 8px rgba(255, 213, 74, .8)); }

/* Header */
.graph-header { display:flex; align-items:center; gap:14px; padding:12px 22px; background:var(--bg-panel); border-bottom:1px solid var(--border); position: relative; z-index: 20; }
.graph-header .graph-actions { margin-left: auto; display:flex; gap:6px; }
.graph-header button { background:var(--bg-hover); color:var(--fg); border:1px solid var(--border); border-radius: 0; padding:6px 10px; font-size:13px; cursor:pointer; min-width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; }
.graph-header button:hover { border-color:var(--accent); }
.graph-header .graph-search-wrap { position: relative; }
.graph-header #graph-search { background: var(--bg-hover); color: var(--fg); border: 1px solid var(--border); border-radius: 0; padding: 7px 12px; font-size: 13px; width: 260px; outline: none; }
.graph-header #graph-search::placeholder { color: var(--fg-dim); }
.graph-header #graph-search:focus { border-color: var(--accent); }
.graph-title { color: var(--fg-dim); font-size:13px; text-transform:uppercase; letter-spacing:.6px; }

/* Search dropdown */
.graph-page .search-results { display: none; position: absolute; top: calc(100% + 6px); left: 0; width: 360px; max-height: 60vh; overflow-y: auto; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; box-shadow: 0 8px 24px rgba(0,0,0,.4); z-index: 50; padding: 4px; }
.graph-page .search-results.visible { display: block; }
.graph-page .search-item { display: flex; align-items: center; gap: 10px; width: 100%; background: transparent; border: 0; border-radius: 0; padding: 8px 10px; cursor: pointer; text-align: left; color: var(--fg); font-size: 13px; }
.graph-page .search-item:hover { background: var(--bg-hover); }
.graph-page .search-item .swatch { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.graph-page .search-item-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.graph-page .search-item-cat { font-size: 11px; color: var(--fg-dim); text-transform: uppercase; letter-spacing: .4px; }
.graph-page .search-empty { padding: 10px 12px; font-size: 12px; color: var(--fg-dim); }

/* Search highlight on graph */
.nodes .node.g-match circle { stroke: #ffd54a !important; stroke-width: 3.5 !important; filter: drop-shadow(0 0 6px rgba(255, 213, 74, 0.9)); }
.nodes .node.g-match text { fill: #ffd54a !important; font-weight: 700; font-size: 13px !important; opacity: 1 !important; }
.nodes .node.g-search-dim { opacity: 0.1; }
.links line.g-search-dim { stroke-opacity: 0.04; }

/* Left panel — categorías + aislar + ayuda */
.graph-panel { position: fixed; top: 78px; left: 20px; width: 250px; background: var(--bg-panel); border:1px solid var(--border); border-radius: 0; padding: 14px 14px 8px 14px; z-index: 8; backdrop-filter: blur(6px); box-shadow: 0 4px 18px rgba(0,0,0,.25); max-height: calc(100vh - 100px); overflow-y: auto; transition: transform .25s ease, opacity .2s; }

/* Floating "open panel" button (visible only when panel is collapsed) */
.graph-panel-open { position: fixed; top: 78px; left: 20px; width: 36px; height: 36px; background: var(--bg-panel); color: var(--fg); border: 1px solid var(--border); border-radius: 0; font-size: 16px; cursor: pointer; z-index: 9; display: none; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,.3); transition: border-color .15s, background .15s; }
.graph-panel-open:hover { border-color: var(--accent); background: var(--bg-hover); }

/* Close button inside the panel */
.graph-panel-close { position: absolute; top: 10px; right: 10px; width: 24px; height: 24px; background: transparent; color: var(--fg-dim); border: 0; border-radius: 0; font-size: 13px; cursor: pointer; line-height: 1; padding: 0; display: flex; align-items: center; justify-content: center; }
.graph-panel-close:hover { color: var(--fg); background: var(--bg-hover); }

/* Collapsed state: hide panel, show open button */
.panel-collapsed .graph-panel { transform: translateX(calc(-100% - 30px)); opacity: 0; pointer-events: none; }
.panel-collapsed .graph-panel-open { display: inline-flex; }
.graph-panel .panel-section { margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.graph-panel .panel-section:last-of-type { border-bottom: none; }
.graph-panel h4 { margin: 0 0 6px 0; font-size: 10px; text-transform: uppercase; letter-spacing: .8px; color: var(--fg-dim); font-weight: 600; }
.graph-panel .legend-btn { display: flex; align-items: center; gap: 8px; width: 100%; background: transparent; border: 1px solid transparent; color: var(--fg); padding: 5px 8px; border-radius: 0; cursor: pointer; font-size: 13px; text-align: left; margin-bottom: 1px; transition: background .15s; }
.graph-panel .legend-btn:hover { background: var(--bg-hover); }
.graph-panel .legend-btn.off { opacity: .35; text-decoration: line-through; }
.graph-panel .legend-label { flex: 1; }
.graph-panel .legend-count { font-size: 11px; color: var(--fg-dim); font-variant-numeric: tabular-nums; }
.graph-panel .swatch { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; border: 1px solid var(--border); }

/* Isolate row */
.graph-panel .isolate-row { display: flex; flex-direction: column; gap: 2px; }
.graph-panel .iso-btn { display: flex; align-items: center; gap: 8px; width: 100%; background: transparent; border: 1px solid var(--border); border-radius: 0; padding: 5px 8px; cursor: pointer; transition: border-color .15s, background .15s; color: var(--fg); font-size: 12px; text-align: left; }
.graph-panel .iso-btn:hover { border-color: var(--accent); background: var(--bg-hover); }
.graph-panel .iso-btn .swatch { width: 11px; height: 11px; border-radius: 50%; border: 0; flex-shrink: 0; }
.graph-panel .iso-btn .iso-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.graph-panel .iso-btn.iso-all { color: var(--fg-dim); font-size: 11px; text-transform: uppercase; letter-spacing: .6px; justify-content: center; margin-bottom: 4px; }
.graph-panel .iso-btn.iso-all:hover { color: var(--fg); }

/* Column bands + titles in graph */
.graph-page .column-bg { transition: fill-opacity .3s; cursor: pointer; }
.graph-page .column-bg:hover { fill-opacity: 0.085 !important; }
.graph-page .nodes .node.neighbor circle { stroke: var(--fg) !important; stroke-opacity: .6; stroke-width: 2; }

/* Fixed column titles overlay — never zoom/pan, always readable on top of nodes */
.graph-page .titles-fixed { pointer-events: all; }
.graph-page .column-title-wrap { transition: opacity .2s; }
.graph-page .column-title-bg { fill: var(--bg-panel); fill-opacity: 0.96; stroke: var(--border); stroke-width: 1; transition: fill-opacity .15s, stroke-width .15s; }
.graph-page .column-title-wrap:hover .column-title-bg { fill-opacity: 1; stroke-width: 1.5; }
.graph-page .column-title-text { font-size: 12px; font-weight: 700; letter-spacing: 1.4px; stroke: none; dominant-baseline: middle; }

/* Collapsible help */
.graph-panel .panel-help { font-size: 11px; color: var(--fg-dim); margin-top: 4px; }
.graph-panel .panel-help summary { cursor: pointer; padding: 4px 0; font-size: 10px; text-transform: uppercase; letter-spacing: .8px; user-select: none; }
.graph-panel .panel-help summary::marker { color: var(--fg-dim); }
.graph-panel .panel-help ul { list-style: none; padding: 6px 0 0 0; margin: 0; line-height: 1.7; }
.graph-panel .panel-help b { color: var(--fg); background: var(--bg-hover); padding: 1px 5px; border-radius: 0; font-size: 10.5px; }

/* Right info panel */
.graph-info { position: fixed; top: 78px; right: 20px; width: 320px; max-height: calc(100vh - 100px); overflow-y: auto; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; padding: 0; z-index: 8; box-shadow: 0 4px 24px rgba(0,0,0,.35); opacity: 0; transform: translateX(20px); transition: opacity .25s, transform .25s; pointer-events: none; }
.graph-info.visible { opacity: 1; transform: translateX(0); pointer-events: auto; }
.graph-info .info-head { display: flex; align-items: flex-start; gap: 10px; padding: 14px 16px 12px 16px; border-bottom: 1px solid var(--border); }
.graph-info .info-swatch { width: 14px; height: 14px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; border: 1.5px solid var(--bg); }
.graph-info .info-titles { flex: 1; }
.graph-info .info-title { font-size: 15px; font-weight: 600; line-height: 1.25; color: var(--fg); }
.graph-info .info-cat { font-size: 11px; color: var(--fg-dim); text-transform: uppercase; letter-spacing: .6px; margin-top: 4px; }
.graph-info .info-close { background: transparent; border: 0; color: var(--fg-dim); cursor: pointer; font-size: 22px; line-height: 1; padding: 0 6px; }
.graph-info .info-close:hover { color: var(--fg); }
.graph-info .info-open { display: block; margin: 10px 16px; padding: 8px 12px; background: var(--accent); color: var(--bg); border-radius: 0; text-align: center; font-size: 13px; font-weight: 600; text-decoration: none; }
.graph-info .info-open:hover { filter: brightness(1.15); }
.graph-info .info-section-title { font-size: 10px; text-transform: uppercase; letter-spacing: .8px; color: var(--fg-dim); padding: 8px 16px 4px 16px; border-top: 1px solid var(--border); margin-top: 8px; }
.graph-info .info-group { padding: 4px 16px 8px 16px; }
.graph-info .info-group-head { display: flex; align-items: center; gap: 6px; font-size: 11px; text-transform: uppercase; letter-spacing: .5px; color: var(--fg-dim); padding: 6px 0 4px 0; font-weight: 600; }
.graph-info .info-group-head .swatch { width: 8px; height: 8px; border-radius: 50%; border: 0; }
.graph-info .info-group-head .info-count { margin-left: auto; opacity: .8; }
.graph-info .info-group ul { list-style: none; padding: 0; margin: 0; }
.graph-info .info-group li { padding: 0; }
.graph-info .info-nbr { display: block; padding: 4px 8px; font-size: 13px; color: var(--fg); text-decoration: none; border-radius: 0; line-height: 1.3; }
.graph-info .info-nbr:hover { background: var(--bg-hover); color: var(--accent); }

/* Mini-map */
.graph-mini { position: fixed; bottom: 18px; right: 20px; width: 200px; height: 150px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 0; padding: 8px; z-index: 7; box-shadow: 0 4px 12px rgba(0,0,0,.3); }
.graph-mini svg { width: 100%; height: 100%; cursor: pointer; }
.graph-mini .mini-bg { fill: var(--bg); }
.graph-mini .mini-viewport { stroke: var(--accent); stroke-width: 1.2; fill: rgba(255,255,255,.04); pointer-events: none; }
[data-theme="light"] .graph-mini .mini-viewport { fill: rgba(0,0,0,.04); }

#graph { width:100vw; height:calc(100vh - 60px); }
.links line { transition: stroke .2s, stroke-opacity .2s, stroke-width .2s; }
.nodes .node { cursor: pointer; transition: opacity .2s; }
.nodes .node.dim { opacity: 0.14; }
.nodes .node text { pointer-events: none; font-family: -apple-system, sans-serif; }

@media (max-width: 1100px) {
  .graph-info { width: 280px; }
}
@media (max-width: 900px) {
  .graph-mini { display: none; }
  .graph-info { display: none; }
  .graph-panel { position: static; width: auto; margin: 14px; max-height: none; }
}

/* Local graph embedded in note page */
.local-graph-wrap { margin-top: 40px; padding: 16px 20px; background:var(--bg-panel); border:1px solid var(--border); border-radius: 0; }
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
.semrel { grid-column: 1 / -1; border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 0; padding: 14px 16px; background: var(--bg-panel); }
.semrel h4 { margin: 0 0 8px; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: var(--fg-dim); }
.semrel ul { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px 14px; }
.semrel li { display: flex; align-items: baseline; gap: 6px; font-size: 14px; }
.semrel .sem-sim { font-size: 11px; color: var(--fg-dim); font-variant-numeric: tabular-nums; }
.semrel-note { margin-top: 8px; font-size: 11px; color: var(--fg-dim); }
.links .link-sem { stroke: var(--accent); stroke-opacity: .35; }
.swatch-sem { width: 14px; height: 0; border-top: 2px dashed var(--accent); display: inline-block; }
.outlinks, .backlinks { margin: 0; padding: 16px 20px; background:var(--bg-panel); border:1px solid var(--border); border-radius: 0; }
.outlinks { border-left: 3px solid #6eb8d6; }
.backlinks { border-left: 3px solid var(--accent); }
.outlinks h4, .backlinks h4 { margin: 0 0 8px 0; color: var(--fg-dim); text-transform: uppercase; font-size: 11px; letter-spacing:.6px; }
.outlinks ul, .backlinks ul { margin:0; padding-left: 18px; font-size: 13.5px; }

@media (max-width: 900px) {
  .links-block { grid-template-columns: 1fr; }
}

/* Global site-search results (NOT graph-page). Specificity-scoped to body:not(.graph-page) via cascade order. */
body:not(.graph-page) .search-results { position: fixed; top: 0; left: 280px; right: 0; background: var(--bg-panel); color: var(--fg); padding: 24px 52px; max-height: 80vh; overflow-y: auto; display:none; z-index:100; border-bottom: 1px solid var(--border); box-shadow: 0 8px 24px rgba(0,0,0,.25); }
body:not(.graph-page) .search-results.open { display: block; }
body:not(.graph-page) .search-results h3 { margin-top: 0; color: var(--fg); }
body:not(.graph-page) .search-result { padding: 10px 0; border-bottom: 1px solid var(--border); color: var(--fg); }
body:not(.graph-page) .search-result a { color: var(--fg); text-decoration: none; font-weight: 600; display: block; margin: 2px 0; }
body:not(.graph-page) .search-result a:hover { color: var(--accent); }
body:not(.graph-page) .search-result > div:last-child { color: var(--fg-dim); font-size: 13px; line-height: 1.5; }
body:not(.graph-page) .search-result b { color: var(--accent); background: transparent; padding: 0; }
body:not(.graph-page) .search-result .cat { font-size: 11px; color: var(--fg-dim); text-transform: uppercase; letter-spacing: .5px; }

@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; }
  .content { padding: 24px 22px 60px 22px; }
  body:not(.graph-page) .search-results { left: 0; padding: 18px 22px; }
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
  const saved = (function () { try { return localStorage.getItem('adg-theme'); } catch (e) { return null; }})() || 'light';
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
        note = parse_note(md)
        # material interno: jamás al sitio publicado
        if str(note["frontmatter"].get("estado", "")).strip().lower() == "interno":
            continue
        notes.append(note)
    all_slugs = {n["slug"] for n in notes}

    # capa semántica (embeddings) — opcional
    semantic_related = load_semantic()

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

        # relacionadas por embeddings (capa semántica)
        sem_rels = [
            r for r in semantic_related.get(n["slug"], [])
            if r["slug"] in all_slugs
        ]
        if sem_rels:
            items = "".join(
                f'<li><a href="{relative_href(n["slug"], r["slug"])}">'
                f'{html.escape(slug_to_title.get(r["slug"], r["slug"]))}</a>'
                f'<span class="sem-sim">{int(r["sim"] * 100)}%</span></li>'
                for r in sem_rels
            )
            out_html += (
                f'<div class="semrel"><h4>≈ Relacionadas</h4>'
                f'<ul>{items}</ul>'
                f'<div class="semrel-note">afinidad por embeddings, no por enlace manual</div>'
                f'</div>'
            )

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
    graph_data = build_graph_data(notes, link_map, semantic_related)
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
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            print(f"\n  Serving at http://localhost:{port}  (Ctrl+C to stop)")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n  Stopped.")


if __name__ == "__main__":
    main()
