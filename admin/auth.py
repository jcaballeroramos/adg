"""Auth por cookie firmada. Sin credenciales en el repo.

Las cuentas se definen SOLO en la variable de entorno ADG_USERS, con la
contraseña en hash bcrypt, nunca en claro:

    ADG_USERS='[{"username":"jorge","hash":"$2b$12$..."}]'

Para generar un hash:  python3 admin/mkpasswd.py

En producción (Railway) el arranque FALLA si faltan ADG_USERS o
ADG_SECRET_KEY, en vez de caer a unas credenciales por defecto. Un fallo de
arranque se ve; una puerta abierta no.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

IS_PROD = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("PORT"))

SECRET_KEY = os.environ.get("ADG_SECRET_KEY", "").strip()
if not SECRET_KEY:
    if IS_PROD:
        raise RuntimeError(
            "ADG_SECRET_KEY no está definida. Sin ella las sesiones son "
            "falsificables. Defínela en las variables de Railway."
        )
    SECRET_KEY = "dev-only-" + secrets.token_hex(16)

_raw = os.environ.get("ADG_USERS", "").strip()
if not _raw:
    if IS_PROD:
        raise RuntimeError(
            "ADG_USERS no está definida. No hay cuentas por defecto a propósito: "
            "defínela en Railway con los hashes de admin/mkpasswd.py."
        )
    _raw = "[]"

USERS: dict[str, bytes] = {}
for u in json.loads(_raw):
    h = u.get("hash")
    if not h:
        raise RuntimeError(
            f"La cuenta {u.get('username')!r} de ADG_USERS no tiene 'hash'. "
            "Las contraseñas en claro ya no se aceptan: usa admin/mkpasswd.py."
        )
    USERS[u["username"]] = h.encode()

COOKIE_NAME = "adg_session"
SESSION_TTL = 86400 * 7
_sessions: dict[str, tuple[str, float]] = {}          # token -> (usuario, expira)
_failures: dict[str, list[float]] = {}                # usuario -> intentos fallidos
MAX_FAILURES, FAILURE_WINDOW = 8, 900                 # 8 intentos en 15 min

# Hash de una contraseña que nadie conoce. Se compara contra él cuando el
# usuario no existe, para que fallar por usuario y fallar por contraseña
# cuesten lo mismo en tiempo.
_DUMMY_HASH = bcrypt.hashpw(secrets.token_bytes(32), bcrypt.gensalt(12))


def _sign(token: str) -> str:
    sig = hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{token}.{sig}"


def _verify(signed: str) -> Optional[str]:
    if "." not in signed:
        return None
    token, sig = signed.rsplit(".", 1)
    expected = hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()[:32]
    return token if hmac.compare_digest(sig, expected) else None


def get_current_user(request: Request) -> Optional[str]:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return None
    token = _verify(cookie)
    if not token:
        return None
    entry = _sessions.get(token)
    if not entry:
        return None
    user, expires = entry
    if time.time() > expires:
        _sessions.pop(token, None)
        return None
    return user


def require_user(request: Request) -> str:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    return user


class LoginBody(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginBody, response: Response):
    now = time.time()
    recent = [t for t in _failures.get(body.username, []) if now - t < FAILURE_WINDOW]
    _failures[body.username] = recent
    if len(recent) >= MAX_FAILURES:
        raise HTTPException(429, "Demasiados intentos fallidos. Espera 15 minutos.")

    stored = USERS.get(body.username)
    # Se comprueba un hash siempre, exista o no la cuenta, para que el tiempo
    # de respuesta no revele qué usuarios existen.
    ok = bcrypt.checkpw(body.password.encode(), stored or _DUMMY_HASH)
    if stored is None:
        ok = False

    if not ok:
        _failures.setdefault(body.username, []).append(now)
        raise HTTPException(401, "Credenciales incorrectas")

    _failures.pop(body.username, None)
    token = secrets.token_hex(32)
    _sessions[token] = (body.username, now + SESSION_TTL)
    response.set_cookie(
        COOKIE_NAME, _sign(token), httponly=True, samesite="lax",
        max_age=SESSION_TTL, secure=IS_PROD,
    )
    return {"ok": True, "username": body.username}


@router.post("/logout")
def logout(request: Request, response: Response):
    cookie = request.cookies.get(COOKIE_NAME)
    if cookie:
        token = _verify(cookie)
        if token:
            _sessions.pop(token, None)
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(401, "No autenticado")
    return {"username": user}
