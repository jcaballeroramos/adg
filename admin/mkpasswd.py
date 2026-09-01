#!/usr/bin/env python3
"""Genera ADG_USERS y ADG_SECRET_KEY. No necesita instalar nada.

    python3 admin/mkpasswd.py

Pide las contraseñas sin mostrarlas y devuelve las dos variables listas para
pegar en Railway. Usa PBKDF2-HMAC-SHA256 de la biblioteca estándar, así que
funciona con cualquier Python 3 sin dependencias. La contraseña en claro no
se guarda ni se muestra en ningún momento.
"""
import base64
import getpass
import hashlib
import json
import os
import secrets

ITERATIONS = 480_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    b64 = lambda b: base64.b64encode(b).decode()
    return f"pbkdf2_sha256${ITERATIONS}${b64(salt)}${b64(dk)}"


def emit(users) -> None:
    if not users:
        print("\nSin cuentas, no genero nada.\n")
        return
    print("\n" + "=" * 72)
    print("Pega estas DOS variables en Railway - Variables. No las commitees.\n")
    print("ADG_USERS=" + json.dumps(users, separators=(",", ":")))
    print()
    print("ADG_SECRET_KEY=" + secrets.token_hex(32))
    print("=" * 72 + "\n")


def main() -> None:
    users = []
    print("\nCuentas para ADG_USERS.")
    print("Cuando acabes, pulsa ENTER en 'usuario' sin escribir nada.\n")
    while True:
        try:
            u = input("usuario: ").strip()
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C no debe tirar a la basura las cuentas ya introducidas.
            print()
            break
        if not u:
            break
        try:
            p1 = getpass.getpass("  contraseña (no se ve al escribir): ")
            p2 = getpass.getpass("  repite:                           ")
        except (KeyboardInterrupt, EOFError):
            print()
            break
        if p1 != p2:
            print("  ✗ no coinciden, repite esta cuenta\n")
            continue
        if len(p1) < 12:
            print("  ✗ mínimo 12 caracteres\n")
            continue
        users.append({"username": u, "hash": hash_password(p1)})
        print("  ✓ añadida\n")

    emit(users)


if __name__ == "__main__":
    main()
