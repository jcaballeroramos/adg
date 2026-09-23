# Traspaso · «Cómo se prueban estas armas»

Estado a 23 de septiembre de 2026, tarde. **La sección de las otras familias ya está escrita.** Lo
que queda son cuatro documentos que no se pueden bajar de forma automatizada y una verificación.

## Qué hay publicado

**https://adg.up.railway.app/como-se-prueban** · fuente en `wiki/como-se-prueban.md` · enlace
desde la portada (botón junto a cronología, mapa y grafo, añadido en `build.py`).

Ocho secciones y **45 PDF fuente** en `media/pdf/ensayos/`, servidos en `/media/pdf/ensayos/`,
todos enlazados desde la página y comprobados uno a uno contra el fichero en disco.

| Sección | Qué cubre |
|---|---|
| 1 | Proyectiles cinéticos: banco de ensayo, las tres pruebas, umbrales, los nueve PDF originales |
| 2 | Qué pasa cuando se disparan: la revisión de *BMJ Open* de 2017 |
| 3 | Electrochoque: IEC 62792, protocolo canadiense, ensayo británico del TASER 10, cerdos, voluntarios, los tres umbrales que no coinciden |
| 4 | Granadas de aturdimiento: no existe protocolo, y se documenta cómo se comprobó |
| 5 | Cañones de agua: el expediente británico con las cifras tachadas, criterio comparativo |
| 6 | Gases lacrimógenos y spray de pimienta: la norma de 1985 aún activa, el OC sin norma |
| 7 | Armas acústicas: no hay norma, y en 2008 se pidió crearla por escrito |
| 8 | El marco de arriba: OTAN, el consejo de revisión estadounidense, la ONU |

Copia de trabajo de los nueve PDF originales fuera del repo en
`~/Desktop/WORKS/ADG_papers_balistica/`, con un `LEEME.md` que resume cada uno.

## Los cuatro hallazgos que sostienen la sección

**No existe protocolo de ensayo publicado para granadas de aturdimiento, cañones de agua ni armas
acústicas.** No es una laguna de la búsqueda. Se comprobó recorriendo el catálogo de las 23 normas
activas del Instituto Nacional de Justicia, que certifica el chaleco del policía y su pistola y no
certifica ninguna de las armas que usa contra el público.

**Lo que se usa en su lugar protege a otra persona.** La norma militar de ruido que rige para
aturdidoras y acústicas mide en la posición del operador. La norma laboral de ruido acota su
ámbito al empleo realizado en un centro de trabajo. Un manifestante no cabe en ninguna de las dos.

**El único umbral operativo del electrochoque se deriva por analogía.** Los 180 microculombios
canadienses salen de una norma sobre corriente que va de la mano izquierda a ambos pies,
dividiendo entre cuatro. Sus autores lo advierten y se blindan con una cláusula de indemnización.

**Se dispara contra una resistencia.** Cuando el ensayo británico del TASER 10 sustituyó la
resistencia por cartuchos reales disparados a dos metros, la tensión de pico salió un 2,5 % por
encima de la especificación del fabricante.

## Lo que queda pendiente

- **STANREC 4744 sigue sin verificar.** El catálogo de normas de la OTAN bloquea el acceso
  automatizado y el artículo de 2023 que lo describiría está cerrado, con el resumen suprimido por
  el editor. Título, autores, revista y año sí están comprobados. La vía práctica es **pedírselo a
  los autores**, que son el grupo de la Real Academia Militar de Bélgica con el que hay correo
  abierto desde el 22 de septiembre.
- DYMAT 2012, que compara la granada de esponja de 40 con el proyectil de 37. Devuelve 403 incluso
  en la página del artículo, con cookies y con agente de navegador. Hay que bajarlo a mano:
  https://www.epj-conferences.org/articles/epjconf/abs/2012/08/epjconf_dymat2012_03002/epjconf_dymat2012_03002.html
- La revisión de *BMJ Open* de 2017. Bloqueada en su servidor y en el espejo de PubMed Central:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5736036/
- ANSI/CPLSO 17, la única norma que se presenta como límites de seguridad para electrochoque.
  Cuesta entre mil y cinco mil dólares.
- La parte 2 del informe Himsworth sobre el CS. La parte 1 es Cmnd 4173 de 1969; el número de la
  parte 2 no se ha podido verificar y los papeles del comité están en la Wellcome Collection.
- Norma ASTM o ISO sobre aerosoles irritantes. Los dos catálogos bloquean el acceso automatizado.

## Trampas técnicas que ya han mordido

**URLs limpias** en `admin/server.py`: un middleware reintenta con `.html` cuando una ruta sin
extensión da 404. **No hacerlo con una ruta catch-all antes del mount**: todo lo que lleve punto
(CSS, PDF) devolvería 404 y el sitio se cae. Ya pasó una vez.

**La carpeta de PDF pesa 83 MB** y el repositorio entero 270. Antes de añadir más documentos,
mirar si compensa o si conviene enlazar a la fuente.

**Si se lanzan agentes de investigación, que no escriban en `wiki/como-se-prueban.md`.** En esta
sesión tres agentes editaron el fichero a la vez que la sesión principal y hubo que pararlos. Que
investiguen y devuelvan el informe; la página la escribe una sola mano.

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
