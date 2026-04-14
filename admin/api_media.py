"""Media upload / list / delete API."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form

from admin.auth import require_user
from admin.git_ops import git_add, git_rm, git_commit, git_push

ROOT = Path(__file__).resolve().parent.parent
MEDIA = ROOT / "media"

router = APIRouter(prefix="/api/media", tags=["media"])

ALLOWED_EXT = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg",
    ".pdf", ".mp3", ".m4a", ".wav", ".mp4", ".webm",
}


@router.get("/")
def list_media(request: Request):
    require_user(request)
    files = []
    if not MEDIA.exists():
        return files
    for f in sorted(MEDIA.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            rel = f.relative_to(MEDIA).as_posix()
            files.append({
                "path": rel,
                "size": f.stat().st_size,
                "ext": f.suffix.lower(),
            })
    return files


@router.post("/upload")
async def upload_media(
    request: Request,
    file: UploadFile = File(...),
    subdir: str = Form(""),
):
    user = require_user(request)
    ext = Path(file.filename or "file").suffix.lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Tipo de archivo no permitido: {ext}")

    dest_dir = MEDIA / subdir if subdir else MEDIA
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (file.filename or "upload")

    content = await file.read()
    dest.write_bytes(content)

    rel = dest.relative_to(ROOT).as_posix()
    git_add(rel)
    git_commit(f"Media: subir {file.filename} (por {user})", author=user)
    git_push()
    return {"ok": True, "path": dest.relative_to(MEDIA).as_posix()}


@router.delete("/{path:path}")
def delete_media(path: str, request: Request):
    user = require_user(request)
    target = MEDIA / path
    if not target.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    rel = target.relative_to(ROOT).as_posix()
    git_rm(rel)
    git_commit(f"Media: borrar {path} (por {user})", author=user)
    git_push()
    return {"ok": True}
