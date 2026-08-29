"""Búsqueda semántica. La clave de Gemini vive SOLO aquí, en el servidor.

El navegador manda la consulta y recibe resultados. Nunca ve la clave ni los
vectores. El endpoint exige sesión iniciada y tiene tres topes de gasto, por
este orden:

  1. Caché de consultas: la misma pregunta no se vuelve a embeber jamás.
  2. Límite por usuario y hora.
  3. Tope diario global, que corta aunque todas las cuentas estén limpias.

Sin GEMINI_API_KEY el endpoint responde 503 y el sitio sigue funcionando con
la búsqueda literal, que es pública y gratis.
"""
from __future__ import annotations

import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from collections import OrderedDict
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from admin.auth import require_user

router = APIRouter(prefix="/api/search", tags=["search"])

ROOT = Path(__file__).resolve().parent.parent
CACHE_FILE = ROOT / "semantic-cache.json"

MODELS = ["gemini-embedding-2", "gemini-embedding-2-preview", "gemini-embedding-001"]
DIMS = 768
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{m}:embedContent"

# ── Topes de gasto ────────────────────────────────────────────────────────
PER_USER_HOUR = int(os.environ.get("ADG_SEARCH_PER_USER_HOUR", "40"))
GLOBAL_DAY = int(os.environ.get("ADG_SEARCH_GLOBAL_DAY", "400"))
QUERY_CACHE_MAX = 2000
MAX_QUERY_CHARS = 300

_query_cache: OrderedDict[str, list[float]] = OrderedDict()
_user_hits: dict[str, list[float]] = {}
_day_count = {"day": "", "n": 0}

_vectors: dict[str, list[float]] = {}
_meta: dict[str, dict] = {}


def _today() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def _load_corpus() -> None:
    """Carga los vectores del caché. Se queda en memoria del servidor."""
    global _vectors, _meta
    if not CACHE_FILE.exists():
        return
    data = json.loads(CACHE_FILE.read_text())
    _vectors = {s: v["v"] for s, v in data.get("vectors", {}).items() if "v" in v}
    index = ROOT / "site" / "search-index.json"
    if index.exists():
        _meta = {e["slug"]: e for e in json.loads(index.read_text())}


_load_corpus()


def _norm_query(q: str) -> str:
    return re.sub(r"\s+", " ", q.strip().lower())[:MAX_QUERY_CHARS]


def _embed(text: str) -> list[float]:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise HTTPException(503, "La búsqueda semántica no está disponible en este servidor.")
    body = json.dumps({
        "model": "models/" + MODELS[0],
        "content": {"parts": [{"text": text}]},
        "taskType": "SEMANTIC_SIMILARITY",
        "outputDimensionality": DIMS,
    }).encode()
    last = None
    for m in MODELS:
        req = urllib.request.Request(
            ENDPOINT.format(m=m),
            data=body.replace(MODELS[0].encode(), m.encode()),
            headers={"Content-Type": "application/json", "x-goog-api-key": key},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                v = json.loads(r.read())["embedding"]["values"]
                n = math.sqrt(sum(x * x for x in v)) or 1.0
                return [x / n for x in v]
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (400, 404):      # modelo no disponible: prueba el siguiente
                continue
            break
        except Exception as e:            # noqa: BLE001
            last = e
            break
    raise HTTPException(502, f"El proveedor de embeddings falló: {last}")


class Query(BaseModel):
    q: str = Field(min_length=2, max_length=MAX_QUERY_CHARS)
    limit: int = Field(default=15, ge=1, le=40)


@router.get("/status")
def status(request: Request):
    """Qué hay disponible. No exige sesión: el sitio lo usa para decidir la UI."""
    from admin.auth import get_current_user
    return {
        "disponible": bool(os.environ.get("GEMINI_API_KEY", "").strip()) and bool(_vectors),
        "autenticado": bool(get_current_user(request)),
        "fichas_indexadas": len(_vectors),
        "consultas_hoy": _day_count["n"] if _day_count["day"] == _today() else 0,
        "tope_diario": GLOBAL_DAY,
    }


@router.post("/semantic")
def semantic(body: Query, request: Request):
    user = require_user(request)          # ← 401 si no hay sesión
    if not _vectors:
        raise HTTPException(503, "No hay vectores cargados en el servidor.")

    q = _norm_query(body.q)
    if len(q) < 2:
        raise HTTPException(400, "Consulta demasiado corta.")

    cached = q in _query_cache
    if not cached:
        # Tope por usuario
        now = time.time()
        hits = [t for t in _user_hits.get(user, []) if now - t < 3600]
        _user_hits[user] = hits
        if len(hits) >= PER_USER_HOUR:
            raise HTTPException(
                429, f"Has hecho {PER_USER_HOUR} consultas nuevas en una hora. "
                     "Es el tope por usuario. Vuelve a intentarlo más tarde."
            )
        # Tope diario global
        if _day_count["day"] != _today():
            _day_count.update(day=_today(), n=0)
        if _day_count["n"] >= GLOBAL_DAY:
            raise HTTPException(
                429, f"Se ha alcanzado el tope diario de {GLOBAL_DAY} consultas "
                     "del sitio. Se reinicia mañana."
            )
        vec = _embed(q)
        _query_cache[q] = vec
        _query_cache.move_to_end(q)
        while len(_query_cache) > QUERY_CACHE_MAX:
            _query_cache.popitem(last=False)
        _user_hits[user].append(now)
        _day_count["n"] += 1
    else:
        _query_cache.move_to_end(q)

    vec = _query_cache[q]
    scored = sorted(
        ((sum(a * b for a, b in zip(vec, v)), s) for s, v in _vectors.items()),
        reverse=True,
    )[: body.limit]

    return {
        "consulta": body.q,
        "desde_cache": cached,
        "resultados": [
            {
                "slug": s,
                "similitud": round(sim, 4),
                "titulo": _meta.get(s, {}).get("title", s.split("/")[-1]),
                "categoria": _meta.get(s, {}).get("category", ""),
                "extracto": _meta.get(s, {}).get("snippet", "")[:220],
            }
            for sim, s in scored
        ],
    }
