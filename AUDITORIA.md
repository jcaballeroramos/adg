# Auditoría de la wiki · 12 agosto 2026

Cuatro revisores pasaron por las 231 fichas. Lo mecánico está corregido (enlaces, duplicados,
reorganización, huérfanas); este documento recoge **lo que no se puede corregir sin
verificación primaria**, porque son cifras que van a cartela o a guion y las fuentes internas
se contradicen. Cada punto lista las fichas implicadas.

Lo ya corregido está en el historial de git de este commit y no se repite aquí.

---

## Resuelto con fuente primaria (aplicado)

**A/78/324 es de Alice Jill Edwards, no de Ní Aoláin.** Verificado contra docs.un.org y
OHCHR: el informe (24-08-2023, presentado el 12-10-2023) es de la Relatora contra la Tortura
Alice Jill Edwards, sucesora de Melzer desde agosto de 2022. Fionnuala Ní Aoláin fue relatora
de **antiterrorismo** (2017-2023), nunca de tortura. La ficha de Milipol era la única que lo
tenía bien. Corregido en las fichas y creada la ficha de Edwards.

---

## Cifras en disputa · decidir antes de usar en pantalla

### 1. Muertes totales en España
Cuatro cifras incompatibles: 24 muertos 1976-2019 (compilacion-espana) · ~77 desde 1978
(impacto-agregado, con doble contabilidad demostrable: suma Cabacas dos veces) · ~61+
(stop-bales-listado) · 23 en 1976-2000 (nicola, carles-guillot). Hay que fijar cifra y
definición (¿solo balas de goma? ¿todo material antidisturbios? ¿incluye Tarajal y Melilla?).

### 2. Energía cinética de la bala de goma española
El dato técnico más citable del documental tiene tres versiones que no pueden convivir:
- 144 J de energía, umbral letal 122 J atribuido a Omega (tipos-de-armas-tabla, compilacion-espana)
- 830 J, umbral 522 J atribuido a STOA/Parlamento Europeo (roger-espanol)
- y la propia tabla da 85 g a 720 km/h, que son ~1.700 J: incompatible con los 144
Además juan-pablo-pernalete atribuye el umbral de 122 J a MAXAM, que es un fabricante, no una
fuente. Pendiente: buscar el informe Omega y el STOA originales y fijar los dos números.

### 3. Heridos oculares en Chile 2019
La horquilla del INDH aparece como 222, 300+, 460 y 500+ según la ficha. Probablemente todas
son verdad con cortes temporales distintos: hay que **fechar cada cifra** y elegir una
canónica (la ficha del caso fija "más de 460, INDH").

### 4. Colombia, Paro 2021, lesiones oculares
11 (Popayán, se estaba usando como total nacional — ya matizado), 103 (El Tiempo) y 150
(MOCAO). Elegir cuál va a cartela.

### 5. Quién fabrica el LBD40
verney-carron lo lista como producto propio (2007); brugger-thomet lo llama "BT-GL06/LBD40";
target-dynamics dice que es diseño B&T que se vende como LBD40; redcore desempata a favor de
Verney-Carron. Son las armas de Francia y de los casos catalanes: hay que fijar fabricante,
diseñador y licencias. (Nota: el LBD 40 estándar francés es de Brügger & Thomet vendido vía
distribuidores; Verney-Carron fabricó el Flash-Ball anterior. Verificar y unificar.)

### 6. La granada de Rémi Fraisse
La ficha se contradice sola: GLI-F4 en frontmatter y cuerpo, OF-F1 en la nota de precisión.
Los recuentos de granadas usadas esa noche tampoco cuadran (700+ vs 339). Marcado con aviso
en la ficha.

### 7. Tarajal
36 vs 5 botes de humo, y la lista de 14 víctimas incluye a "Samba Martine", que es el caso
del CIE de Aluche (2011), no Tarajal. Marcado con aviso en la ficha; la lista entera necesita
verificación antes de aparecer en pantalla.

### 8. SED 1872 · ¿MAXAM o Nobel Sport?
Las dos fichas reclaman en frontmatter ser la Sociedad Española de Dinamita fundada por
Alfred Nobel en 1872. Una es sucesora societaria (probablemente MAXAM vía Unión Española de
Explosivos) y la otra heredera de marca. Verificar y dejar una sola genealogía.

### 9. Serie de facturación del mercado mundial
En mercado-mundial.md, 2019 da 867 M$ entre vecinos de 5.600-8.600 M$ (error de orden de
magnitud casi seguro), y 2020 > 2021 sin explicación. Revisar las fuentes de cada año.

### 10. Empresas del sector: 370 en 40 países (años 90) vs 200 en 60 países (2019)
La serie es imposible tal cual (cronologia vs centre-delas). Una de las dos transcripciones
está mal.

### 11. Bahréin 2011: 34 vs 39 muertos por gas, ambas atribuidas a PHR
Fechar/verificar el informe de Physicians for Human Rights.

### 12. Chalecos amarillos
19.071 disparos de LBD40 atribuidos a la vez a 2018, al primer semestre del movimiento y
contradichos por la serie 2018-2020 (18.805). Y "480 veces más" es casi seguro "+480%".
Las cifras de heridos varían entre fichas (24.000/300.000 vs 24.300/335.300 vs oficial
2.000/2.495). Fijar con Dufresne/Rocher delante.

### 13. Distancia mínima del fabricante de las foam SIR-X
20 m (roger-garcia) vs 30 m (africa-pablo-hasel). Sostiene el argumento del caso África
(disparo a 22 m): con 20 el fabricante quedaría cumplido, con 30 incumplido. Crítico.

### 14. Menores
- Rufo Chacón: 64 vs 52 perdigones (marcado en ficha).
- Rodney King/LA 1992: 63 vs 50+ muertos.
- Irlanda del Norte: "16 muertos, 9 niños" sin fuente (la cifra documentada habitual es 17/8).
- GLI-F4: 26 g TNT + 4 g hexógeno vs 25 g TNT sin hexógeno.
- LRAD: 162 dB vs 150-162 vs 152 dB SPL según ficha.
- Primera Intifada: 1988-1998 vs 1987-93.
- CS "desarrollado por el ejército de EEUU en 1920" — Corson y Stoughton lo sintetizaron en
  1928 en contexto académico. Revisar la entrada de la cronología.
- PR-24: datada 1958 en dos fichas; la datación habitual de la Monadnock es 1971.
- Protocolo IV CCW: "EE.UU. firmó en 1995" — verificar (la aceptación estadounidense es muy
  posterior).
- Testimonios Carne Cruda: nov 2024 vs nov 2025 según ficha (africa vs roger-garcia).
- Prohibición Euskadi: 2012 vs abril 2015.
- "África" vs "Áfrika" — decidir grafía (la propia campaña usa Áfrika en redes).
- "Dilan" vs "Dylan" Cruz.
- TEDH: "Kilici" y "Yasa" probablemente Kılıç y Yaşa; faltan números de demanda y años.

---

## Pendientes estructurales (no urgentes)

- **Fichas sin fuente con cifras duras**: transparencia-cuerpos-policiales-espana (85%/72%/91%
  sin URL), krusik-serbia (BIRN/OCCRP/HRW sin URL), zira-silah (125.000 pistolas sin enlace),
  las dos TEDH sin signatura.
- **Actores citados sin ficha**: EXPAL (protagonista del bloque FEINDEF "Puño de Darwin"),
  Genasys/LRAD (única familia de armas sin fabricante fichado), Pacem Defense, Etienne
  Lacroix Group (dueño de Falken).
- **06-cierre-abba** (FEINDEF): la afirmación del cierre (ABBA emitida contra la flotilla
  SUMUD) sigue sin fuente verificada; la propia ficha lo avisa. No usar en pantalla hasta
  cerrarla.
- **posibles fusiones**: resource-book-onu-2017 y unodc-ohchr-manual-uso-fuerza parecen el
  mismo documento (original inglés / traducción castellana). Verificar y fusionar.
- **mexico-feminista-2020, guatemala-2020, peru-2020, brasil-2017-2021, olga-proces,
  nepal-gen-z-2024**: por debajo del estándar del resto; nepal además puede tener el año mal
  (el levantamiento Gen Z con bloqueo de redes es de sept 2025).

---

## La capa que falta: embeddings

`semantic.py` está listo (gemini-embedding-2 con fallback, 768 dims, caché en
`semantic-cache.json` que se commitea para que Railway no necesite clave). Falta una
GEMINI_API_KEY válida: la de `~/.zshrc` es una credencial OAuth, no una API key, y todas las
AIza de los `.env` locales están revocadas. Crear una en https://aistudio.google.com/apikey y:

```
export GEMINI_API_KEY="<la clave>"   # solo en ~/.zshrc, nunca en el repo
cd ~/Desktop/CODE/projects/adg && python3 semantic.py && python3 build.py
```

Con eso aparecen la sección «≈ Relacionadas» en cada ficha y las aristas discontinuas de
afinidad en el grafo.
