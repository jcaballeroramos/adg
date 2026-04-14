"""Frontmatter field schemas per note tipo."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/schemas", tags=["schemas"])

COMMON_FIELDS = [
    {"name": "tipo", "type": "select", "options": [
        "caso", "empresa", "autor", "feria", "herramienta", "historia",
        "bibliografía", "render", "entrenamiento", "cronología", "taxonomía",
        "testimonio", "organización", "figura-histórica", "publicidad",
    ]},
    {"name": "estado", "type": "select", "options": ["stub", "borrador", "completo"]},
    {"name": "tags", "type": "tags"},
]

TYPE_FIELDS = {
    "caso": [
        {"name": "victima", "type": "text"},
        {"name": "edad", "type": "text"},
        {"name": "fecha_hechos", "type": "text"},
        {"name": "pais", "type": "text"},
        {"name": "ciudad", "type": "text"},
        {"name": "contexto", "type": "textarea"},
        {"name": "arma", "type": "text"},
        {"name": "fabricante_principal", "type": "text"},
        {"name": "resultado", "type": "text"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "empresa": [
        {"name": "nombre", "type": "text"},
        {"name": "pais", "type": "text"},
        {"name": "sede", "type": "text"},
        {"name": "matriz", "type": "text"},
        {"name": "web", "type": "url"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "bibliografía": [
        {"name": "editor", "type": "text"},
        {"name": "autor", "type": "text"},
        {"name": "año", "type": "text"},
        {"name": "titulo", "type": "text"},
        {"name": "ambito", "type": "text"},
        {"name": "financiacion", "type": "text"},
        {"name": "archivo", "type": "text"},
        {"name": "nombre_completo", "type": "text"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "autor": [
        {"name": "nombre", "type": "text"},
        {"name": "pais", "type": "text"},
        {"name": "afiliacion", "type": "text"},
        {"name": "web", "type": "url"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "feria": [
        {"name": "nombre", "type": "text"},
        {"name": "pais", "type": "text"},
        {"name": "ciudad", "type": "text"},
        {"name": "periodicidad", "type": "text"},
        {"name": "web", "type": "url"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "herramienta": [
        {"name": "nombre", "type": "text"},
        {"name": "url", "type": "url"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "historia": [
        {"name": "artefactos", "type": "tags"},
        {"name": "fuentes", "type": "url-list"},
    ],
    "render": [
        {"name": "fuentes", "type": "url-list"},
    ],
    "entrenamiento": [
        {"name": "fuentes", "type": "url-list"},
    ],
}


@router.get("/")
def get_schemas():
    return {
        "common": COMMON_FIELDS,
        "types": TYPE_FIELDS,
    }
