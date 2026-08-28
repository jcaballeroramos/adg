"""Simple cookie-based auth for 3 known users."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.environ.get("ADG_SECRET_KEY", "dev-secret-change-me")

# Users loaded from env: [{"username":"jorge","password":"..."},...]
_raw = os.environ.get("ADG_USERS", '[{"username":"jorge","password":"admin1123"},{"username":"anna","password":"admin1123"},{"username":"irene","password":"admin1123"}]')
USERS: dict[str, str] = {}
for u in json.loads(_raw):
    USERS[u["username"]] = u["password"]

COOKIE_NAME = "adg_session"
_sessions: dict[str, str] = {}  # token -> username


def _sign(token: str) -> str:
    sig = hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{token}.{sig}"


def _verify(signed: str) -> Optional[str]:
    if "." not in signed:
        return None
    token, sig = signed.rsplit(".", 1)
    expected = hmac.new(SECRET_KEY.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(sig, expected):
        return None
    return token


def get_current_user(request: Request) -> Optional[str]:
    cookie = request.cookies.get(COOKIE_NAME)
    if not cookie:
        return None
    token = _verify(cookie)
    if not token:
        return None
    return _sessions.get(token)


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
    stored = USERS.get(body.username)
    if not stored or stored != body.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = secrets.token_hex(24)
    _sessions[token] = body.username
    signed = _sign(token)
    is_prod = os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("PORT")
    response.set_cookie(
        COOKIE_NAME, signed, httponly=True, samesite="lax",
        max_age=86400 * 7, secure=bool(is_prod),
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
        raise HTTPException(status_code=401, detail="No autenticado")
    return {"username": user}
