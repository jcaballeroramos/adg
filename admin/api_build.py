"""Build trigger — runs build.py to regenerate the static site."""
from __future__ import annotations

import subprocess
from pathlib import Path

from fastapi import APIRouter, Request

from admin.auth import require_user

ROOT = Path(__file__).resolve().parent.parent

router = APIRouter(prefix="/api/build", tags=["build"])


@router.post("/")
def trigger_build(request: Request):
    require_user(request)
    result = subprocess.run(
        ["python3", "build.py"],
        cwd=ROOT, capture_output=True, text=True,
    )
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-2000:] if result.stdout else "",
        "stderr": result.stderr[-2000:] if result.stderr else "",
    }
