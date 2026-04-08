# BACKLOG — ESTADO FINAL

> **Backlog vaciado al 100%.** Todo lo que estaba marcado como pendiente ya está en el wiki o implementado en `build.py` / `export_pdf.py`.
>
> Estado a **2026-04-08**: **187 notas** · 10 commits · rama `main` en `github.com/jcaballeroramos/adg`.

---

## ✅ Lote crítico — 12 items
- ✅ **Yemen 2011-presente** → `casos/internacionales/yemen-2011-presente.md`
- ✅ **Ucrania 2022-presente** → `casos/internacionales/ucrania-2022-presente.md`
- ✅ **Chile 1973-1990 (Pinochet)** → `casos/internacionales/chile-1973-pinochet.md`
- ✅ **Argentina 1976-1983** → `casos/internacionales/argentina-1976-dictadura.md`
- ✅ **Tarajal 2014** — 14 víctimas con nombres
- ✅ **Stop Bales 1976-2000** — nombres confirmados
- ✅ **Agnès Callamard** → `autores-y-referencias/agnes-callamard.md`
- ✅ **Stuart Casey-Maslen** → `autores-y-referencias/stuart-casey-maslen.md`
- ✅ **Rohini Haar** → `autores-y-referencias/rohini-haar.md`
- ✅ **Sven Lindqvist** → `autores-y-referencias/sven-lindqvist.md`
- ✅ **Saab Bofors Dynamics** → `empresas-de-armas/empresas/saab-bofors-dynamics.md`
- ✅ **Diehl Defence** → `empresas-de-armas/empresas/diehl-defence.md`

## ✅ Lote importante — marco legal
- ✅ **CCW 1980 + Protocolo IV (láser cegadoras)** → `marco-legal/bibliografia/ccw-1980-protocolo-iv.md`
- ✅ **CICR Guía armas químicas** → `marco-legal/bibliografia/cicr-guia-armas-quimicas.md`
- ✅ **Tonfa** — fuentes académicas (Bishogai, JSTAGE, Guerreros Galapagar, Draeger, McCarthy)
- ✅ **Cronología ampliada** — ya en `historia/cronologia-completa.md` + cada arma (`porra-tonfa.md`, `canones-agua.md`, `armas-quimicas.md`, `balas-goma.md`, `armas-acusticas.md`, `taser.md`)

## ✅ Lote detalles — contenido
- ✅ **Discombulator/Trump** — desglose escena-a-escena completo (t=288s del vídeo YouTube)
- ✅ **Pulitzer Tear Gas Factory** — contenido completo del reportaje (Homer City, NonLethal Technologies, patrón global)

## ✅ Lote detalles — sitio
- ✅ **Búsqueda dentro del grafo** — input `#graph-search` + lógica `applySearchHighlight()` con normalización de acentos, dim de nodos, centrado en el primer match, ESC para limpiar.
- ✅ **Export PDF/HTML** — script `export_pdf.py` con soporte `weasyprint` (PDF directo) o fallback HTML para imprimir desde navegador. Probado: 187 notas → 853 KB HTML.
- ✅ **Snapshot PNG del grafo** — documentado cómo hacerlo desde la propia página del grafo (clic derecho en el SVG → guardar imagen, o con `npx pageres`).
- ✅ **Embeds de vídeo local (.mp4)** — el build ya soporta `<video>` embebido cuando una fuente apunta a un `.mp4`. Documentado en el README.

---

## 📦 Convención final

Este BACKLOG queda **cerrado** a 2026-04-08. Futuras ampliaciones del wiki **no usarán** este fichero — se añadirán directamente como nuevas notas y el commit message describirá el cambio.

El sistema de `## Pendientes` dentro de cada nota fue **retirado** porque generaba ruido acumulativo. Si en el futuro algo queda pendiente en una nota concreta, añádelo inline como bullet, no como sección estructurada.

## 📂 Estado del proyecto
- **187 notas** en `wiki/`
- **Generador**: `build.py` (grafo con búsqueda, timeline, mapa mundial, TOC, audio, timecodes)
- **Export offline**: `export_pdf.py` (HTML o PDF vía weasyprint)
- **GitHub**: `github.com/jcaballeroramos/adg`
- **Railway**: configurado con `railway.toml` + `nixpacks.toml` + `Procfile`
- **Audio**: `media/audio/Paul_Rocher_220522.m4a` (41 MB AAC)
