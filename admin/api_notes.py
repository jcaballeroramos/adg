"""CRUD API for wiki markdown notes."""
from __future__ import annotations

import re
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from admin.auth import require_user
from admin.git_ops import git_add, git_rm, git_mv, git_commit, git_push

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

router = APIRouter(prefix="/api/notes", tags=["notes"])


def _parse_note(md_path: Path) -> dict:
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
    slug = rel[:-3]
    parts = rel.split("/")
    category = parts[0] if len(parts) > 1 else "_root"
    subcategory = parts[1] if len(parts) > 2 else None

    title_m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else md_path.stem

    return {
        "slug": slug,
        "title": title,
        "category": category,
        "subcategory": subcategory,
        "tipo": fm.get("tipo", ""),
        "estado": fm.get("estado", ""),
        "tags": fm.get("tags", []),
        "frontmatter": fm,
        "body": body,
    }


@router.get("/")
def list_notes(request: Request):
    require_user(request)
    notes = []
    for md in sorted(WIKI.rglob("*.md")):
        if md.name.startswith("."):
            continue
        try:
            n = _parse_note(md)
            notes.append({
                "slug": n["slug"],
                "title": n["title"],
                "category": n["category"],
                "subcategory": n["subcategory"],
                "tipo": n["tipo"],
                "estado": n["estado"],
                "tags": n["tags"],
            })
        except Exception:
            pass
    return notes


@router.get("/{slug:path}")
def get_note(slug: str, request: Request):
    require_user(request)
    md_path = WIKI / f"{slug}.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    n = _parse_note(md_path)
    return {
        "slug": n["slug"],
        "title": n["title"],
        "category": n["category"],
        "subcategory": n["subcategory"],
        "frontmatter": n["frontmatter"],
        "body": n["body"],
    }


class NoteBody(BaseModel):
    frontmatter: dict = {}
    body: str = ""


def _write_note(md_path: Path, frontmatter: dict, body: str) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    fm_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = f"---\n{fm_str}---\n\n{body}"
    md_path.write_text(content, encoding="utf-8")


@router.put("/{slug:path}")
def update_note(slug: str, data: NoteBody, request: Request):
    user = require_user(request)
    md_path = WIKI / f"{slug}.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    _write_note(md_path, data.frontmatter, data.body)
    rel = md_path.relative_to(ROOT).as_posix()
    git_add(rel)
    git_commit(f"Editar: {slug} (por {user})", author=user)
    git_push()
    return {"ok": True, "slug": slug}


class CreateBody(BaseModel):
    slug: str
    frontmatter: dict = {}
    body: str = ""


@router.post("/")
def create_note(data: CreateBody, request: Request):
    user = require_user(request)
    md_path = WIKI / f"{data.slug}.md"
    if md_path.exists():
        raise HTTPException(status_code=409, detail="Ya existe una nota con ese slug")
    _write_note(md_path, data.frontmatter, data.body)
    rel = md_path.relative_to(ROOT).as_posix()
    git_add(rel)
    git_commit(f"Crear: {data.slug} (por {user})", author=user)
    git_push()
    return {"ok": True, "slug": data.slug}


@router.delete("/{slug:path}")
def delete_note(slug: str, request: Request):
    user = require_user(request)
    md_path = WIKI / f"{slug}.md"
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    rel = md_path.relative_to(ROOT).as_posix()
    git_rm(rel)
    git_commit(f"Borrar: {slug} (por {user})", author=user)
    git_push()
    return {"ok": True, "slug": slug}


class MoveBody(BaseModel):
    new_slug: str


@router.post("/{slug:path}/move")
def move_note(slug: str, data: MoveBody, request: Request):
    user = require_user(request)
    old_path = WIKI / f"{slug}.md"
    if not old_path.exists():
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    new_path = WIKI / f"{data.new_slug}.md"
    if new_path.exists():
        raise HTTPException(status_code=409, detail="Ya existe una nota en el destino")
    old_rel = old_path.relative_to(ROOT).as_posix()
    new_rel = new_path.relative_to(ROOT).as_posix()
    git_mv(old_rel, new_rel)
    git_commit(f"Mover: {slug} -> {data.new_slug} (por {user})", author=user)
    git_push()
    return {"ok": True, "slug": data.new_slug}
