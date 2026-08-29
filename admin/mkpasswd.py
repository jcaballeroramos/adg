#!/usr/bin/env python3
"""Genera el valor de ADG_USERS con las contraseñas en hash bcrypt.

    python3 admin/mkpasswd.py

Pide los usuarios y sus contraseñas sin mostrarlas por pantalla, e imprime la
línea lista para pegar en las variables de entorno de Railway. La contraseña
en claro no se guarda en ningún sitio.
"""
import getpass
import json
import secrets

import bcrypt

users = []
print("Cuentas para ADG_USERS. Enter en el usuario para terminar.\n")
while True:
    u = input("usuario: ").strip()
    if not u:
        break
    p1 = getpass.getpass("  contraseña: ")
    p2 = getpass.getpass("  repite:     ")
    if p1 != p2:
        print("  ✗ no coinciden, repite esta cuenta\n")
        continue
    if len(p1) < 12:
        print("  ✗ mínimo 12 caracteres\n")
        continue
    users.append({"username": u, "hash": bcrypt.hashpw(p1.encode(), bcrypt.gensalt(12)).decode()})
    print("  ✓ añadida\n")

if not users:
    raise SystemExit("Sin cuentas, no genero nada.")

print("\n" + "=" * 70)
print("Pega estas DOS variables en Railway → Variables. No las commitees.\n")
print("ADG_USERS=" + json.dumps(users, separators=(",", ":")))
print()
print("ADG_SECRET_KEY=" + secrets.token_hex(32))
print("=" * 70)
