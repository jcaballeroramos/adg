# Traspaso · «Cómo se prueban estas armas»

Estado a 23 de septiembre de 2026. Esta línea de trabajo se sigue en otra sesión.

## Qué hay hecho y publicado

**https://adg.up.railway.app/como-se-prueban** · fuente en `wiki/como-se-prueban.md` · enlace
desde la portada (botón junto a cronología, mapa y grafo, añadido en `build.py`).

La página cubre **solo los proyectiles cinéticos**: pelotas de goma, foam, saquitos, bastones
flexibles. Lleva el protocolo completo de ensayo, quién lo escribió y qué deja fuera.

**Nueve PDF fuente** en `media/pdf/ensayos/`, servidos en `/media/pdf/ensayos/`. Copia de trabajo
fuera del repo en `~/Desktop/WORKS/ADG_papers_balistica/`, con un `LEEME.md` que resume cada uno.

**URLs limpias** añadidas en `admin/server.py`: un middleware reintenta con `.html` cuando una
ruta sin extensión da 404. **No hacerlo con una ruta catch-all antes del mount**: todo lo que
lleve punto (CSS, PDF) devolvería 404 y el sitio se cae. Ya pasó una vez.

## COMPLETADO el 23-sep-2026

La página cubre ya **las seis familias**: proyectiles cinéticos, electrochoque, granadas de
aturdimiento, cañones de agua, irritantes químicos y armas acústicas, más el marco normativo de
arriba (OTAN, Estados Unidos, Europa y la ONU) y una sección final con lo que reconocen ellos
mismos. **42 documentos** descargables desde la propia página, todos de acceso abierto.

El hallazgo principal: **de las seis familias, solo el electrochoque tiene norma internacional de
medida, y esa norma mide la salida eléctrica, no la seguridad**. Para granadas de aturdimiento y
cañones de agua no existe norma en ninguna parte.

## Otros pendientes anotados en la propia página

- Bajar a mano el artículo de DYMAT 2012 que compara la esponja de 40 con el proyectil de 37.
  Es de acceso abierto pero su servidor bloquea la descarga automática:
  https://www.epj-conferences.org/articles/epjconf/abs/2012/08/epjconf_dymat2012_03002/epjconf_dymat2012_03002.html
- La revisión de BMJ Open 2017, igual: abierta pero con descarga bloqueada.
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5736036/
- Verificar si STANREC 4744 es público.

## Cómo trabajar con esto

```bash
cd ~/Desktop/CODE/projects/adg
python3 build.py          # genera site/ desde wiki/
git push origin main      # Railway despliega solo, tarda un minuto y medio
```

Para levantar el servidor en local hacen falta dos variables o el arranque falla a propósito:

```bash
ADG_SECRET_KEY=lo-que-sea ADG_USERS='[{"username":"x","hash":"y"}]' \
  python3 -m uvicorn admin.server:app --port 8799
```

`uvicorn` no está en el Python del sistema de este Mac; hay que hacer un entorno virtual.

En el cuerpo de las notas **solo funcionan los wikilinks** `[[ruta/nota|texto]]`; los enlaces
markdown a `.md` quedan rotos. Los enlaces a URL absolutas y a `/media/...` sí funcionan.

## Contexto de la película que explica por qué importa

Roger Español perdió el ojo derecho el 1 de octubre de 2017 por una pelota de goma de la Policía
Nacional. El informe forense habla de rotura del globo ocular y fracturas compatibles con impacto
de alta velocidad; los peritajes sitúan el disparo a 14,12 metros. En el informe que fundó el
protocolo de ensayo estadounidense se probaron diez municiones y **ninguna era una pelota de goma
esférica**. En España no hay ningún estudio publicado sobre estas lesiones. Ver
`wiki/casos/espana-europa/roger-espanol.md`.
