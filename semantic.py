#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Capa semántica de la wiki — embeddings Gemini + relaciones por similitud.

Uso:
    python3 semantic.py           # calcula/refresca embeddings y relaciones
    python3 semantic.py --stats   # muestra cobertura y pares más cercanos

La clave va SOLO en la variable de entorno GEMINI_API_KEY (nunca en el repo,
nunca en el cliente). El resultado queda cacheado en semantic-cache.json,
que SÍ se commitea: así el build de Railway usa las relaciones sin tocar la
API. Si no hay clave y no hay caché, build.py funciona igual, sin la capa
semántica.

Modelo: gemini-embedding-2 (GA abr 2026), con fallback a
gemini-embedding-2-preview y gemini-embedding-001. Vectores de 768
dimensiones (MRL), suficientes para 231 notas y 6 veces más ligeros que
los 3072 por defecto.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent
WIKI = ROOT / "wiki"
CACHE = ROOT / "semantic-cache.json"

MODELS = ["gemini-embedding-2", "gemini-embedding-2-preview", "gemini-embedding-001"]
DIMS = 768
TASK = "SEMANTIC_SIMILARITY"
TOP_K = 6          # relacionadas por nota
MIN_SIM = 0.62     # umbral de similitud coseno para proponer relación
MAX_CHARS = 22000  # ~8k tokens de margen

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")


def note_text(path: Path) -> str:
    """Título + frontmatter clave + cuerpo, limpio de sintaxis, para embeber."""
    raw = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(raw)
    body = raw[m.end():] if m else raw
    fm_line = ""
    if m:
        keep = []
        for line in m.group(1).split("\n"):
            if re.match(r"^(tipo|tags|pais|arma|contexto|nombre|titulo|ambito|ámbito)\s*:", line):
                keep.append(line.strip())
        fm_line = " · ".join(keep)
    body = WIKILINK_RE.sub(lambda mm: mm.group(1).split("|")[-1], body)
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)
    body = re.sub(r"[#>*`|_-]{2,}", " ", body)
    text = f"{path.stem.replace('-', ' ')}\n{fm_line}\n{body}"
    return re.sub(r"\s+", " ", text).strip()[:MAX_CHARS]


def collect_notes() -> dict[str, Path]:
    return {
        str(p.relative_to(WIKI)).replace(".md", ""): p
        for p in sorted(WIKI.rglob("*.md"))
    }


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"model": None, "dims": DIMS, "vectors": {}, "related": {}}


def embed_batch(texts: list[str], key: str, model: str) -> list[list[float]]:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:batchEmbedContents"
    )
    reqs = [
        {
            "model": f"models/{model}",
            "content": {"parts": [{"text": t}]},
            "taskType": TASK,
            "outputDimensionality": DIMS,
        }
        for t in texts
    ]
    payload = json.dumps({"requests": reqs}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    return [e["values"] for e in data["embeddings"]]


def l2norm(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def cos(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute(verbose: bool = True) -> dict:
    notes = collect_notes()
    cache = load_cache()
    key = os.environ.get("GEMINI_API_KEY", "").strip()

    hashes = {}
    for slug, path in notes.items():
        text = note_text(path)
        hashes[slug] = (hashlib.sha256(text.encode()).hexdigest()[:16], text)

    # limpiar notas borradas
    cache["vectors"] = {
        s: v for s, v in cache.get("vectors", {}).items() if s in notes
    }

    stale = [
        s for s, (h, _) in hashes.items()
        if cache["vectors"].get(s, {}).get("hash") != h
    ]

    if stale and key:
        model = cache.get("model") or None
        done = 0
        # elegir modelo disponible una sola vez
        chosen = None
        for m in ([model] if model else []) + [x for x in MODELS if x != model]:
            try:
                embed_batch(["ping"], key, m)
                chosen = m
                break
            except urllib.error.HTTPError as e:
                if verbose:
                    print(f"  modelo {m}: HTTP {e.code}, pruebo siguiente")
            except Exception as e:
                if verbose:
                    print(f"  modelo {m}: {e}")
        if not chosen:
            print("✗ ningún modelo de embeddings disponible con esta clave")
        else:
            cache["model"] = chosen
            if verbose:
                print(f"→ {len(stale)} notas nuevas o cambiadas · modelo {chosen}")
            B = 20
            for i in range(0, len(stale), B):
                chunk = stale[i:i + B]
                texts = [hashes[s][1] for s in chunk]
                for attempt in range(3):
                    try:
                        vecs = embed_batch(texts, key, chosen)
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise
                        time.sleep(4 * (attempt + 1))
                for s, v in zip(chunk, vecs):
                    cache["vectors"][s] = {
                        "hash": hashes[s][0],
                        "v": [round(x, 5) for x in l2norm(v)],
                    }
                done += len(chunk)
                if verbose:
                    print(f"  {done}/{len(stale)}")
                time.sleep(0.4)
    elif stale and not key:
        if verbose:
            print(
                f"⚠ {len(stale)} notas sin embedding y sin GEMINI_API_KEY — "
                "uso solo la caché existente"
            )

    # relaciones: top-k por coseno, excluyendo lo ya enlazado por wikilink
    linked: dict[str, set] = {}
    for slug, path in notes.items():
        raw = path.read_text(encoding="utf-8")
        outs = set()
        for l in WIKILINK_RE.findall(raw):
            target = l.split("|")[0].split("#")[0].strip()
            outs.add(Path(target).stem.lower())
        linked[slug] = outs

    vecs = {s: d["v"] for s, d in cache["vectors"].items() if s in notes}
    related = {}
    slugs = sorted(vecs)
    for s in slugs:
        sims = []
        for t in slugs:
            if t == s:
                continue
            sims.append((cos(vecs[s], vecs[t]), t))
        sims.sort(reverse=True)
        picks = []
        for sim, t in sims[:24]:
            if sim < MIN_SIM:
                break
            # no repetir lo que ya está enlazado a mano
            if Path(t).stem.lower() in linked.get(s, set()):
                continue
            if Path(s).stem.lower() in linked.get(t, set()):
                continue
            picks.append({"slug": t, "sim": round(sim, 3)})
            if len(picks) >= TOP_K:
                break
        if picks:
            related[s] = picks
    cache["related"] = related
    cache["generated"] = time.strftime("%Y-%m-%d %H:%M")

    CACHE.write_text(
        json.dumps(cache, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    if verbose:
        print(
            f"✓ semantic-cache.json · {len(vecs)}/{len(notes)} notas con vector · "
            f"{sum(len(v) for v in related.values())} relaciones"
        )
    return cache


def stats():
    cache = load_cache()
    notes = collect_notes()
    vecs = {s: d["v"] for s, d in cache.get("vectors", {}).items() if s in notes}
    print(f"modelo: {cache.get('model')} · {len(vecs)}/{len(notes)} con vector")
    pairs = []
    slugs = sorted(vecs)
    for i, s in enumerate(slugs):
        for t in slugs[i + 1:]:
            pairs.append((cos(vecs[s], vecs[t]), s, t))
    pairs.sort(reverse=True)
    print("\npares más cercanos (posibles duplicados o fusiones):")
    for sim, s, t in pairs[:20]:
        print(f"  {sim:.3f}  {s}  <->  {t}")


if __name__ == "__main__":
    if "--stats" in sys.argv:
        stats()
    else:
        compute()
