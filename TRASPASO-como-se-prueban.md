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

## Lo que falta · la sección 3

La página tiene una sección «Las otras familias» que ahora mismo solo enlaza a las fichas que ya
existían. Hay que escribirla con el mismo nivel de detalle que la parte cinética: **qué norma se
aplica y quién la publica, con qué se mide, contra qué se dispara o aplica (maniquí, animal,
voluntario, simulante), qué magnitudes se registran, qué umbral separa aceptable de inaceptable y
qué agujeros reconoce la propia literatura.**

Familias pendientes, con las fichas del wiki a las que hay que enlazar:

| Familia | Ficha existente |
|---|---|
| Electrochoque (TASER y similares) | `wiki/historia/taser.md` |
| Granadas de aturdimiento (flashbang) | sin ficha propia |
| Cañones de agua | `wiki/historia/canones-agua.md` |
| Gases lacrimógenos y spray de pimienta | `wiki/historia/armas-quimicas.md` |
| Armas acústicas (LRAD) | `wiki/historia/armas-acusticas.md` |

Pistas de por dónde tirar, sin verificar todavía:

- Para electrochoque, la literatura de Kroll, Ho y Dawes sobre fibrilación ventricular y captura
  cardiaca, y los ensayos en cerdo.
- Normas transversales: el trabajo de estandarización de la OTAN sobre proyectiles cinéticos no
  letales (**STANREC 4744**, comprobar si es público), el Joint Non-Lethal Weapons Directorate del
  Departamento de Defensa estadounidense y su Human Effects Center of Excellence.
- El Instituto Nacional de Justicia estadounidense publica en abierto en `ojp.gov`; de ahí salen
  cuatro de los nueve PDF que ya tenemos.

**Aviso**: se lanzó un agente de investigación sobre esto que quedó corriendo en la sesión
anterior. Sus resultados **no se traspasan**. Hay que rehacer la búsqueda.

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
