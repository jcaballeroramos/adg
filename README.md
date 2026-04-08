# Artefactos de Guerra — Investigación

Repositorio modular de investigación para la película documental **Artefactos de Guerra** de Jorge Caballero.

Funciona como vademécum, diario de proceso y base de conocimiento. Inspirado en el flujo de [LLM Knowledge Bases de Karpathy](https://x.com/karpathy): documentos fuente en `raw/`, wiki destilada en `wiki/`, navegable desde Obsidian o cualquier editor de Markdown.

## Estructura

```
adg/
├── README.md              ← este índice
├── raw/                   ← fuentes brutas (transcripciones, PDFs, capturas)
├── assets/                ← imágenes, frames, gráficos
└── wiki/
    ├── 00-index.md        ← índice maestro de la wiki
    ├── entrenamientos/    ← formación policial / militar
    ├── feindef/           ← feria de defensa Madrid (bloques)
    ├── renders/           ← análisis de animaciones técnicas
    ├── casos/             ← víctimas y casos judiciales
    ├── testimonios/       ← comparecencias y entrevistas
    ├── marco-legal/       ← ONU, Amnistía, normativa
    └── historia/          ← genealogía de cada artefacto
```

## Convenciones

- **Un tema = un `.md`**. Modular, actualizable, manejable.
- Cada archivo lleva frontmatter con `tipo`, `estado`, `fuentes`, `tags`.
- Los enlaces internos usan rutas relativas tipo `[[../casos/roger-espanol]]`.
- Los vídeos y URLs externas se citan siempre en la sección `## Fuentes`.
- Lo que aún no está procesado va a `raw/` con el mismo nombre.

## Estado actual

- [x] Estructura base
- [x] Lote 1 — entrenamientos, FEINDEF, renders, casos, testimonios, marco legal, historia
- [ ] Lote 2 — pendiente
