"""Git helpers — add / commit / push / mv / rm."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True, check=check,
    )


def git_add(*paths: str) -> None:
    _run("git", "add", *paths)


def git_rm(path: str) -> None:
    _run("git", "rm", "-f", path)


def git_mv(old: str, new: str) -> None:
    dest = ROOT / new
    dest.parent.mkdir(parents=True, exist_ok=True)
    _run("git", "mv", old, new)


def git_commit(message: str, author: str = "admin") -> None:
    _run(
        "git", "commit",
        "-m", message,
        "--author", f"{author} <{author}@artefactosdeguerra>",
        check=False,
    )


def git_push() -> subprocess.CompletedProcess:
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        remote = f"https://x-access-token:{token}@github.com/jcaballeroramos/adg.git"
        return _run("git", "push", remote, "main", check=False)
    return _run("git", "push", check=False)
