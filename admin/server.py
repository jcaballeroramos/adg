"""FastAPI app — serves static site + admin panel + API."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from admin.auth import router as auth_router
from admin.api_notes import router as notes_router
from admin.api_media import router as media_router
from admin.api_build import router as build_router
from admin.schemas import router as schemas_router
from admin.api_search import router as search_router

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ADMIN_STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Artefactos de Guerra — Admin")

# API routers
app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(media_router)
app.include_router(build_router)
app.include_router(schemas_router)
app.include_router(search_router)


@app.on_event("startup")
def build_site_on_startup():
    if not SITE.exists() or not (SITE / "index.html").exists():
        print("[admin] Building site on startup...")
        subprocess.run(["python3", "build.py"], cwd=ROOT)
        print("[admin] Build complete.")


# Admin SPA — /admin serves admin/static/index.html
@app.get("/admin")
@app.get("/admin/")
def admin_index():
    return FileResponse(ADMIN_STATIC / "index.html")


# Admin static assets
app.mount("/admin/static", StaticFiles(directory=str(ADMIN_STATIC)), name="admin-static")

# Public media (audio, fotos, pdf). site/media es un symlink que apunta fuera de
# SITE y StaticFiles lo bloquea por seguridad → se sirve aquí desde la carpeta real.
MEDIA = ROOT / "media"
if MEDIA.exists():
    app.mount("/media", StaticFiles(directory=str(MEDIA)), name="media")

# Archivo local de Eurosatory (vídeos ~11GB + fotos originales). Vive FUERA del
# repo, no se sube a Railway: el montaje solo se activa donde la carpeta existe
# (tu Mac). Permite enlazar a los originales desde las notas del wiki en local.
EUROSATORY_LOCAL = ROOT.parent.parent / "ADG_EurosatoryPress"
if EUROSATORY_LOCAL.exists():
    app.mount("/eurosatory-local", StaticFiles(directory=str(EUROSATORY_LOCAL)), name="eurosatory-local")

# Static site (must be last — catch-all)
if SITE.exists():
    app.mount("/", StaticFiles(directory=str(SITE), html=True), name="site")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8765))
    uvicorn.run("admin.server:app", host="0.0.0.0", port=port, reload=True)
