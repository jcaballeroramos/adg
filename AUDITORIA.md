# Auditoría de la wiki · 12 agosto 2026, revisada el 26 de agosto de 2026

Cuatro revisores pasaron por las 231 fichas en agosto. Lo mecánico quedó corregido (enlaces,
duplicados, reorganización, huérfanas), y este documento recogía lo que no se podía corregir sin
verificación primaria, porque son cifras que van a cartela o a guion y las fuentes internas se
contradicen.

El 26 de agosto se hizo una segunda pasada con dos fases. En la primera, cada cifra en disputa la
buscó un agente en documento primario, otro agente independiente intentó refutar lo que el primero
daba por bueno, y donde los dos chocaron un tercero fue al documento a decidir. Regla de trabajo:
nada se da por verificado con una sola fuente ni con fuentes que se citen entre sí, y
«no verificable» es un resultado válido y preferible a dar por bueno algo que va a salir en
pantalla. En la segunda fase, doce agentes leyeron las 237 fichas buscando lo que la auditoría de
agosto no cubría, es decir, cifras, fechas, modelos de arma y referencias normativas sin fuente
anotada en la propia ficha.

Trece de las catorce cifras en disputa quedan cerradas con documento. Lo que sigue abierto está en
su propio apartado, dicho explícitamente y con la vía por donde habría que ir a buscarlo.

Dos avisos sobre el material de partida. El primero, que `raw/` no contiene el volcado original:
`raw/00-lote1-documento-original.md` sigue siendo el placeholder de cuatro líneas que nunca se
rellenó, de modo que el barrido se hizo sobre `wiki/`, que son 237 ficheros. El segundo, sobre el estado de
las fichas: **las correcciones de la fase 1 ya están aplicadas** en la rama
`correcciones-auditoria-agosto-2026`, 40 fichas, cada una con la fuente escrita dentro. **El barrido está cerrado entero**: los 384 datos sin fuente se han verificado en
cuatro rondas y están aplicados.

Lo ya corregido en agosto está en el historial de git y no se repite.

---

## Resuelto con fuente primaria

**A/78/324 es de Alice Jill Edwards, no de Ní Aoláin.** Verificado contra docs.un.org y
OHCHR: el informe (24-08-2023, presentado el 12-10-2023) es de la Relatora contra la Tortura
Alice Jill Edwards, sucesora de Melzer desde agosto de 2022. Fionnuala Ní Aoláin fue relatora
de **antiterrorismo** (2017-2023), nunca de tortura. La ficha de Milipol era la única que lo
tenía bien. Corregido en las fichas y creada la ficha de Edwards.

---

### 1 · Muertes totales en España

**Los ~77 son doble contabilidad, y la propia wiki explicitaba la fórmula que los genera.**
impacto-agregado sumaba «24 por balas de goma + Tarajal 2014 + Melilla 2022 + Iñigo Cabacas +
Antonio C. Badalona». Los 24 de El Salto ya incluyen a Cabacas y ya incluyen las muertes del
Tarajal, ambos nominalmente en su cronología, de modo que la suma cuenta dos veces entre 15 y 16
muertes. La fecha de inicio «1978» también es incorrecta bajo cualquier recuento: la primera
muerte documentada tanto por Stop Bales de Goma como por El Salto es Juan Gabriel Rodrigo Knafo,
Tarragona, 5 de marzo de 1976. Corrigiendo el doble cómputo la misma fórmula daría del orden de
62, que es probablemente el origen del «~61+» que circulaba. Ninguna fuente sostiene 77.

**Las ocho muertes de 1976 a 2000 sí están documentadas y con nombre.** El informe de Stop Bales
de Goma de 2013 registra a Juan Gabriel Rodrigo Knafo (Tarragona, 1976), Carlos Gustavo Frechen
Solana (Barcelona, Diada de 1977), Pancho Egea (Cartagena, 1977), José Luis Aristizabal Lasa e
Isidro Susperregi Aldako (Donostia, 1977), Ursino Gallego (14 años, cerca de Madrid, 1979),
Valentín González Ramírez (Valencia, 1979) y Rosa Zarra (Euskadi, 1995). Irídia/Novact 2021
recoge la misma lista en su nota al pie 163 y la formula como «al menos, 8 muertes y una veintena
de heridos de gravedad» entre 1976 y 2000. El informe de 2013 advierte que la lista no es
completa.

**El «24 muertos 1976-2019» que atribuíamos a El Salto no aguanta como recuento.** El titular
actual dice «al menos 45 heridos graves y 24 fallecidos», pero la entradilla del mismo artículo
dice 23, la ventana que el texto declara termina en 2017 y no en 2019, la última muerte de su
cronología es el Tarajal de febrero de 2014, y si se cuentan los nombres que da salen 25. El
artículo ha cambiado de cifra al menos tres veces: el slug de la URL conserva «35 heridos graves
y 23 fallecidos», Irídia lo citó en 2021 como «44 heridos graves y 23 fallecidos» y hoy titula
«45 y 24». No es un recuento con metodología, es un titular movedizo.

**Los recuentos no son comparables y no admiten una cifra total única.** Cada uno usa una
definición y una ventana distintas, y varios se citan entre sí. Stop Bales de Goma 2013 cuenta
balas de goma por impacto directo desde 1976, con 9 muertes nominales y lista declarada
incompleta. Irídia/Novact 2021 cubre solo 2000-2020 y da 40 personas afectadas, de las que 15
fallecidas, contando a Cabacas por impacto directo y 14 ahogados en el Tarajal por causa
indirecta, y para el análisis de lesiones excluye deliberadamente a los 14 del Tarajal y trabaja
con 26 personas. El Salto cubre 1976-2014/2017. Amnistía Internacional y Omega, en ACT
30/6384/2023, dan «una muerte por traumatismo craneal y 24 lesiones graves entre 2000 y 2020»
para pelotas de goma, y cuentan el Tarajal aparte, más cuatro casos de foam también aparte.
eldiario.es en 2016 daba 16, que son las 15 del Tarajal más Cabacas. Ninguno incluye foam, gas,
porra ni taser en el cómputo de muertes, ninguno incluye Melilla 2022, y ninguno es un censo. El
propio informe de Irídia lo dice: «el Estado español no dispone de registros oficiales que den
cuenta de la totalidad de personas muertas o heridas a causa de las balas de goma».

**Melilla 2022 no debe contarse dentro del total.** Ninguna de las fuentes del expediente adscribe
esas muertes al material antidisturbios en el sentido en que lo hace el resto del recuento, y
mezclarlas rompe la definición con la que se construyó la serie. Va aparte, con su propia ficha y
sus propias fuentes.

**El listado histórico de la wiki hay que reescribirlo entero, y esto es lo más urgente del bloque.**
`stop-bales-listado-historico.md` atribuye al informe de Stop Bales de Goma nueve nombres que no
están en él. Búsqueda literal sobre el PDF descargado: «Santiago» 0 ocurrencias, «Germán» 0, «Cano»
0, «Gladys» 0, «Arregi» 0, «Castillo» 0, «Zabala» 0, «Zabalza» 0. La lista real del informe es
Rodrigo Knafo, Frechen Solana, Egea, Aristizabal Lasa, Susperregi Aldako, Ursino Gallego, González
Ramírez y Rosa Zarra. Hay además causas de muerte cambiadas: Gladys del Estal (Tudela, 3 de junio
de 1979) murió por munición real de un subfusil Z-70 de la Guardia Civil; Germán Rodríguez
(Pamplona, 8 de julio de 1978) murió por un disparo en la frente, en unos Sanfermines con once
heridos de bala; Mikel Zabalza murió en 1985 bajo custodia de la Guardia Civil, que es un caso de
tortura sin relación con material antidisturbios, y la propia ficha lo reconoce. Y la wiki atribuye
a Stop Bales de Goma el recuento de los Sucesos de Vitoria de marzo de 1976 cuando lo que el informe
registra de 1976 es a Rodrigo Knafo en Tarragona, en una manifestación de protesta por Vitoria:
«Vitoria» aparece una sola vez en todo el documento, en esa frase. Son nombres muy cargados y
atribuirles una causa de muerte equivocada desacredita el resto del trabajo.

Lo que se puede llevar a pantalla es la cifra con su definición y su ventana, nunca un total.
La formulación defendible es «al menos 8 muertes por bala de goma entre 1976 y 2000 (Stop Bales
de Goma; Irídia/Novact 2021)» y, por separado, el Tarajal, Cabacas y Melilla con sus propias
fuentes.

---

### 2 · Energía cinética de la bala de goma española

**El umbral es 122 J y los informes del Parlamento Europeo lo transmiten, no lo originan.** El estudio final
del STOA *Crowd Control Technologies*, PE 168.394/Fin.St., Luxemburgo junio de 2000, lleva en
su ficha catalográfica «Author: OMEGA Foundation, Manchester, UK». Fija tres zonas: por debajo
de 20,3 J «safe or low hazard», entre 40,7 y 122 J «a dangerous area», y por encima de 122 J
(90 foot pounds) «being in the severe damage region». La escala no es de Omega: la Tabla 2 la
atribuye a Egner, D.O. et al. (1973), *A multi disciplinary technique for the evaluation of
less lethal weapons Vol 1*, US Department of Justice, y el informe STOA anterior (PE 166 499,
6 de enero de 1998) ya la traía atribuida al Technical Report 24-75 de Wargovich et al., US
Army Land and Warfare Laboratory, 1975. Omega y STOA son el mismo documento, de modo que la
atribución honesta para cartela es «ensayos del US Army Land Warfare Laboratory, recogidos por el
informe STOA/Omega del Parlamento Europeo (2000)».
El documento dice «severe damage region», no «letal»; el salto a letal es una recomendación
política del propio informe («Any Kinetic Impact Weapons with an energy greater than 122 joules
should be considered as a lethal firearm»). Un detalle más: el umbral original es 90 foot-pounds,
cifra redonda imperial, y los 122 J son un artefacto de conversión.
<https://www.europarl.europa.eu/RegData/etudes/etudes/stoa/2000/168394/DG-4-STOA_ET(2000)168394_EN(PAR02).pdf>
<https://www.statewatch.org/media/documents/news/2005/may/steve-wright-stoa-rep.pdf>

**El encuadre del umbral hay que cambiarlo, y esto afecta al guion.** Presentar los 122 J como una
frontera que la bala española cruza de manera excepcional es engañoso, porque la cruzan todas. El
propio STOA 2000 dice que «seven of the European weapons were in the "severe damage" region and one
was in the "dangerous" region. Thus nearly all of the kinetic energy weapons currently authorised
for use in Europe operate in the severe damage region and are therefore potentially lethal», y
Omega mide en 2003 la munición británica L21A1 en 257 J, «more than twice the designated severe
damage KE of 122 joules». Cartela segura: «por encima de 122 julios los ensayos militares
estadounidenses de los años setenta situaban los impactos en la región de daño severo; el informe
del Parlamento Europeo de 2000 recomendó por ello tratarlos como arma letal». No escribir «el
Parlamento Europeo fija el umbral en 122 J».

**Los 522 J no existen.** Ningún informe del STOA contiene esa cifra. Se buscó «522» en el
texto completo de PE 166 499 (1998) y de PE 168.394/Fin.St. (2000), con cero apariciones en
ambos. El origen es un artículo de Tomás Gisbert (Centre Delàs) publicado en Diagonal el 26 de
abril de 2012, que escribe «en este informe se señalaban los 522 julios de energía cinética
como el límite que distingue a las armas letales de las menos letales» y lo hipervincula
precisamente al informe de 1998 que dice 122. Es un error de transcripción propagado durante
trece años. Retirar de roger-espanol y de donde aparezca.
<https://www.elsaltodiario.com/hemeroteca-diagonal/balas-de-goma-un-historial-de-impunidad>

**Los 830 J tampoco tienen documento.** Aparecen por primera vez en el mismo artículo de
Gisbert (2012) sin referencia, y se repiten en La Marea el 11 de junio de 2013 atribuidos al
informe de Stop Bales de Goma de 2013, sin metodología de medición ni ficha técnica. La Marea
compara los 830 J contra 122 J, no contra 522: la combinación «830 J frente a umbral 522 J»
que traía la wiki es un collage de dos textos distintos. El informe de Irídia de 2021, que es
el trabajo documental más extenso publicado sobre esta munición, con acceso a sumarios, pliegos
y respuestas parlamentarias, no recoge la cifra 830 en ningún punto. No debe ir a cartela.

**La cifra defendible es 144 J, y es un máximo.** Irídia, *Stop Balas de Goma* (2021), p. 41:
el reductor de energía acoplado a la bocacha tiene tres posiciones y «con ambas ventanas
cerradas el proyectil es disparado con la máxima energía, 144 julios». El propio informe
subraya que no hay información pública sobre la energía en las posiciones abierta y
semicerrada, ni trazabilidad de en qué posición estaba el reductor en cada disparo. La
comprobación aritmética cuadra con los datos oficiales: el catálogo *Law Enforcement* de MAXAM
da 60 m/s de velocidad de salida, y la respuesta del Gobierno al Senado de 16 de abril de 2018
(expediente 684/36171, pregunta del senador Jon Iñarritu) fija el proyectil en 80-85 g y 54,30
mm. 0,5 × 0,080 × 60² = 144 J exactos. Redacción segura: «hasta 144 julios con el reductor de
energía cerrado (Irídia, 2021)».
<https://iridia.cat/wp-content/uploads/2021/06/Informe-Balas-de-Goma_V2.pdf>

**Los 720 km/h se caen.** El peso (80-85 g) y el diámetro (54,30 mm) están en la respuesta del
Gobierno al Senado, pero la velocidad de 200 m/s procede de la cadena Gisbert 2012 / La Marea
2013 sin ningún documento detrás. El fabricante del cartucho da 60 m/s, y las mediciones de
baton rounds británicos del informe de Omega para la Northern Ireland Human Rights Commission
(2003) sitúan el L5A7 en 60,5-65 m/s y el L21A1 en 70-74 m/s. 200 m/s queda fuera de todo el
rango conocido de proyectiles de impacto cinético, y con 85 g daría ~1.700 J, incompatible con
las dos energías que la propia wiki manejaba. Retirar de tipos-de-armas-tabla y de la ficha de
la oftalmóloga Estrella Fernández.
<https://omegaresearchfoundation.org/storage/2024/05/Baton-Rounds.pdf>

**MAXAM no fija ningún umbral, y tampoco fabrica la bola.** Según Irídia (2021, p. 42, notas
92 y 99), MAXAM fabrica el cartucho lanzador de pólvora negra que impulsa el proyectil; las
bolas de caucho las fabrica Manufacturas del Tormes Barbero, S.L. según la respuesta del
Gobierno de 16 de abril de 2018, y un lote de cartuchos 12/70 del expediente 009/20/AR/01 de
la Dirección General de la Policía se adjudicó a Armas y Cartuchos del Sur, S.L. Corregir la
ficha de MAXAM y la de juan-pablo-pernalete, que atribuyen el umbral de 122 J al fabricante.
Añadido: la Tabla 2 del STOA 2000 lista catorce municiones de impacto de nueve países y no
incluye ninguna española, de modo que en ese informe no hay dato español ni de 144 ni de 830.

**La hipótesis de la confusión entre julios y J/cm² queda descartada.** La densidad de energía
es la métrica estándar en balística forense (Bir, Stewart y Wilhelm, *Skin Penetration
Assessment of Less Lethal Kinetic Energy Munitions*, Journal of Forensic Sciences 50(6), 2005,
con 166 impactos sobre ocho cadáveres y penetración desde 33,14 J/cm²; Fierz, *Eye* 2024,
25.000 J/m² para daño ocular irreversible), pero los 122 J son inequívocamente un valor
absoluto, dado con su equivalente en foot-pounds, y ninguna de las cifras en disputa es una
lectura errónea de un valor por área. La explicación real es un error de transcripción de 2012
más una cifra de activismo sin medición.

---

### 3 · Heridos oculares en Chile 2019

**La cifra canónica es 460, cerrada, con corte del 13 de marzo de 2020.** Es el último recuento
observacional del INDH, publicado el 19 de marzo de 2020 con el encabezado «datos desde 17 de
octubre de 2019 e ingresados hasta el 13 de marzo de 2020». Desglose oficial: 425 casos (92%) de
«lesión o trauma» y 35 (8%) de «estallido o pérdida», abiertos en cuatro diagnósticos, estallido
ocular 26, pérdida ocular 9, lesión ocular 247 y trauma ocular 178, con 411 de los 460 en la
Región Metropolitana. Hay que escribir «460», nunca «más de 460» ni «+460»: el INDH dejó de
contar así después de marzo de 2020 y la cifra no va a crecer. Corregir chile-estallido-2019 e
impacto-agregado, que llevan «+460».

**El 222 corresponde al corte del 18 de noviembre de 2019 y está en documento primario.** El
reporte «Información constatada por el INDH al 18-11-2019 a las 16.30 hrs», recuperado del propio
servidor del INDH, da en su Tabla 3 estallido ocular 2, lesión ocular 61, pérdida ocular 5 y
trauma ocular 154, total 222, con 194 en la Región Metropolitana. Solo 7 de las 222 son estallido
o pérdida, un 3,2%.

**El 2.381 de la ficha de Fabiola Campillai está mal en el dígito y en la etiqueta.** El primario
tiene dos tablas distintas. La Tabla 1, «personas registradas en hospitales», da 2.351 adultos más
218 niños, niñas y adolescentes, «un total de 2.587 personas catastradas». La Tabla 2, «total
heridos y fallecidos», da 1.482 por disparos más 903 por otras causas más 6 fallecidos, que suman
2.391. El 2.391 incluye muertos y no es el censo hospitalario. Redacción fiel: «222 personas con
heridas oculares y 2.391 personas heridas o fallecidas registradas por observadores del INDH en
centros de salud (2.587 catastradas en hospitales), datos del 17 de octubre al 18 de noviembre de
2019».

**El «300+» tiene dos anclajes válidos, y el 347 es bueno.** El INDH Informe Anual 2019,
«Situación de los Derechos Humanos en Chile en el Contexto de la Crisis Social», dice en su p. 35
que «según las inspecciones realizadas en recintos hospitalarios al 30 de noviembre, se reporta un
total de 347 heridas oculares», y lo repite en conclusiones. Su nota 62 explica por qué difiere del
reporte periódico de esa misma fecha, que daba 241: la cifra anual «es hasta el 30 de noviembre e
incluye las cifras reportadas por las Sedes Regionales del INDH», es decir, es una consolidación
retrospectiva, mientras que el reporte diario era una instantánea de ingesta con seis regiones
marcadas «Sin Reporte» y la Metropolitana sin actualizar. El Colegio Médico daba 340 en la misma
fecha. El otro anclaje es el reporte del 6 de diciembre de 2019, que da 352 y que ACNUDH reproduce.
Para amnistia-policia-bajo-la-lupa, sustituir «300+ traumas oculares» por «347 personas con heridas
oculares al 30 de noviembre de 2019 (INDH, Informe Anual 2019)» o por «352 al 6 de diciembre de
2019». Dos cautelas al citar el 347: la Tabla 7 del Informe Anual suma 317 y su título dice
«Principales tipos», de modo que no es un desglose exhaustivo y no debe publicarse como si cerrara;
y el propio informe es ambiguo sobre el eje temporal, porque el texto anuncia gráficos «por día de
ocurrencia del evento» y el Gráfico 7 se titula «según fecha de registro».

**El «500+» no es del INDH.** Su máximo histórico es 460 y a partir de ahí su cifra pública baja,
no sube. El «más de 500» viene de las organizaciones de sobrevivientes, declarado ante la comisión
especial investigadora de la Cámara de Diputados en 2021, y la literatura revisada por pares lo
formula como horquilla, «entre 400 y 500 víctimas». Como referencia contigua, el programa estatal
PIRO del Minsal registraba 397 casos ingresados hasta marzo de 2022 más 60 que no ingresaron.

**El INDH cambió de criterio en marzo de 2020 y por eso circulan cifras bajas atribuidas también
a él.** Desde entonces informa solo las víctimas de trauma ocular por cuyos hechos ha presentado
querella: 220 en el balance de octubre de 2023 (sobre 3.216 querellas y 3.777 víctimas) y 227 en
el de octubre de 2024 (sobre 3.233 querellas y 3.828 víctimas). El desglose judicial a cuatro años
distingue desenlaces: 50 personas con estallido ocular, 82 con pérdida de visión y 88 con otra
lesión. Si la cartela necesita el desenlace visual y no el prediagnóstico, esa es la cifra
correcta, diciendo que es el universo de querellas.

**La serie del INDH es de ingesta, no de ocurrencia.** Las cabeceras dicen «datos ingresados
hasta», y el salto de 241 el 30 de noviembre a 352 el 6 de diciembre, en seis días, lo demuestra.
Cualquier línea de tiempo construida con esos cortes describe cuándo se registraron los casos, no
cuándo ocurrieron.

**La serie clínica de la Unidad de Trauma Ocular es otra cosa y no debe mezclarse.** El informe de
la UTO del Hospital del Salvador difundido por la Sociedad Chilena de Oftalmología con fecha 8 de
noviembre de 2019 da 168 pacientes con trauma ocular severo entre el 18 de octubre y el 8 de
noviembre, 32 con herida penetrante o estallido, 80,3% por impacto de balín antidisturbios, y 74
de 140 pacientes con agudeza visual registrada por debajo de 20/200, es decir ceguera legal según
la OMS, con 9 evisceraciones. La serie publicada en *Eye* (Nature) en agosto de 2020 da 259
pacientes atendidos entre el 18 de octubre y el 30 de noviembre, 182 de ellos por proyectiles de
impacto cinético, y el 48,9% con deterioro visual severo o ceguera se calcula sobre esos 182, no
sobre los 259. El Minsal, vía transparencia a Amnistía, da 239 pacientes de la UTO para la misma
ventana en que la UTO publica 259.

---

### 4 · Colombia, Paro Nacional 2021

**El 103 es correcto y es de Temblores, no de El Tiempo.** Procede del registro de la plataforma
GRITA publicado en «Tiros a la vista: traumas oculares en el marco del Paro Nacional» (Amnistía
Internacional, Temblores ONG y PAIIS-Universidad de los Andes, AMR 23/5005/2021, 26 de noviembre
de 2021): al menos 103 casos de lesiones oculares entre el 28 de abril y el 20 de julio de 2021,
una cada 0,81 días. Desglose por departamento: Bogotá 56 (54,37%), Valle del Cauca 12, Cauca 8,
Nariño 7, Cundinamarca 6, Antioquia 5, Risaralda 3, Boyacá 2, y uno en Atlántico, Casanare,
Santander y Tolima. Gravedad: 14 casos de pérdida del ojo y 14 de pérdida total de la visión. El
Tiempo es el medio que lo difundió ese día.

**Los 150 de MOCAO no existen.** Sus dos cifras propias son 116 lesiones oculares a nivel nacional
entre el 28 de abril y el 31 de diciembre de 2021, registradas en el sistema SIAP de la Campaña
Defender la Libertad con documentación de MOCAO, y 169 casos desde la creación del ESMAD en 1999
hasta junio de 2022 (48 entre 1999 y 2019, más 121 entre 2020 y junio de 2022). Ambas están en
«Represión en la mira. Lesiones oculares en el marco de las protestas en Colombia» (CSPP, Campaña
Defender la Libertad, MOCAO y CAPS, ISBN 978-958-53871-2-6). La palabra «150» no aparece en ninguna
página del informe.

**Los 11 de Popayán son otra cosa.** La CIDH, en sus observaciones tras la visita de trabajo del 8
al 10 de junio de 2021 (párr. 54), informa de 11 investigaciones disciplinarias abiertas por
lesiones oculares en todo el país, de las cuales solo una en Popayán, con 5 en Bogotá, 3 en
Risaralda, 1 en Medellín y 1 en Neiva. El dato territorial disponible es por departamento: GRITA
registra 8 casos en el Cauca. Para Popayán ciudad no hay cifra publicada.

**MOCAO no cuenta lo mismo que Temblores.** Temblores usa GRITA, con denuncia ciudadana y
triangulación. La Campaña Defender la Libertad, con documentación de MOCAO, usa el sistema SIAP,
que combina redes sociales y medios, línea nacional de emergencia y Comisiones de Verificación en
terreno, y da 88 casos al 21 de julio y 116 en la ventana ampliada. Los registros institucionales
son más bajos porque solo recogen denuncia formal: la Defensoría del Pueblo registró 18 casos a
mediados de junio de 2021 y la Fiscalía consolidó 79 víctimas, de las que 62 quedaron relacionadas
con las protestas. La cifra segura para cartela es «más de 100 personas con lesiones oculares
durante el Paro Nacional de 2021», sostenida por tres sistemas de conteo independientes.

**MOCAO significa otra cosa de lo que dicen las dos fichas.** Es «Movimiento en Resistencia contra
las Agresiones Oculares del ESMAD», como aparece en la portada de su propio informe y en el
artículo que tres de sus integrantes firman en Torture Journal. Se dio a conocer públicamente el 9
de abril de 2021. Ni «Movimiento Nacional por la Libertad y los Derechos de los Ojos» ni
«Movimiento de Colombianxs Afectadxs por la Violencia Ocular», que son las dos versiones que
circulaban en el repo.

**Los 146 heridos son del departamento del Cauca, no de Popayán ciudad, y el «1 muerto» está mal.**
El informe preliminar de la Misión de Solidaridad Internacional y Derechos Humanos difundido por la
Comisión Intereclesial de Justicia y Paz el 3 de junio de 2021 titula el apartado «6.a) Departamento
del Cauca- Popayán» y abre con «la delegación recorrió el departamento del Cauca, y pudo recabar las
siguientes denuncias», tras lo cual lista «146 Heridos en el marco de la manifestación». Es una
cifra de recorrido por el departamento, de una única misión de verificación de sociedad civil con
trabajo de campo del 25 y 26 de mayo, y sigue con fuente única: ni HRW, ni Lethal in Disguise, ni
OACNUDH, ni la CIDH dan cifra de heridos para Popayán o el Cauca. Si se conserva, debe ir como «146
heridos en el departamento del Cauca, según la Misión de Solidaridad Internacional y DDHH (junio de
2021)». El «1 muerto» lo contradice el propio documento que se invoca, que lista tres homicidios,
y ni siquiera los tres son del Cauca: el informe sitúa a Jordany Rosero Estrella en Putumayo. Lo
único verificado por dos fuentes independientes es la muerte de Sebastián Quintero Múnera el 14 de
mayo de 2021 en Popayán por munición del arma Venom, corroborada por el estudio de caso de Colombia
de «Lethal in Disguise» y por OACNUDH. Aviso colateral: ese mismo informe nombra a Alison como
«Alison Lizeth Salazar Miranda», y la ficha la llama de otra manera.

---

### 5 · Quién fabrica el LBD 40

**Es Brügger & Thomet, y la propia Verney-Carron lo declaró bajo juramento.** El GL-06 es un
lanzador monotiro de 40 × 46 mm fabricado por B&T AG (Thun, Suiza), y es el arma que Francia
denomina LBD 40. Guillaume Verney-Carron, director general de la empresa, ante la comisión de
investigación de la Asamblea Nacional el 14 de mayo de 2019: «Verney-Carron est également le
concepteur et fabricant du lanceur de balles de défense (LBD) de marque Flash-Ball», «le
Flash-Ball a un calibre de 44 millimètres que nous avons créé de toutes pièces» y, sobre el
calibre 40 × 46, «jusqu'à présent, nous ne nous sommes jamais positionnés sur ce marché».
Amnistía Internacional lo dice igual de claro en su declaración pública EUR 21/0304/2019 de 3
de mayo de 2019: «le LBD40 est produit par le fabricant suisse Brügger & Thomet sous le nom
GL06». La ficha de verney-carron que lo lista como producto propio de 2007 está mal; la de
target-dynamics tenía razón.
<https://www.assemblee-nationale.fr/dyn/15/comptes-rendus/cesecufo/l15cesecufo1819008_compte-rendu>

**Verney-Carron fabricó el Flash-Ball, de 44 mm, y es un arma distinta.** Primer mercado para
policía y gendarmería «des années 2000-2002», parque de 4.500 lanzadores. El cambio de
doctrina llega tras los disturbios de Villiers-le-Bel de 2007, cuando «la demande s'est portée
sur du calibre de 40 millimètres». El informe del Défenseur des droits de diciembre de 2017 lo
confirma: «afin de remplacer le Flash-Ball superpro®, une nouvelle munition de courte portée a
été adaptée au lanceur de balles de défense LBD 40x46».

**Suiza clasifica el LBD 40 como material de guerra y España es su segundo destino.** El
Consejo Federal suizo, respondiendo el 15 de mayo de 2019 a la interpelación 19.3188 de
Pierre-Alain Fridez: «le LBD40 est en principe aussi considéré comme du matériel de guerre» y
«des lanceurs LBD40 ont été exportés vers 25 pays ces cinq dernières années, à savoir, par
ordre d'importance décroissant, la France, l'Espagne, la Pologne, la Hongrie, les États-Unis».

**Quien suministra al Ministerio del Interior francés es Alsetex y Rivolier.** Aviso de
resultado BOAMP 19-176436 (27/11/2019), comprador SAELSI, expediente «LBD_40»: lote 3 de 1.280
lanzadores monotiro adjudicado el 20/11/2019 a Alsetex (grupo Etienne Lacroix) por 1.638.400 €,
lote 1 de 180 lanzadores de seis tiros a Rivolier el 19/11/2019 por 727.450 €, lote 2
infructuoso. Aviso BOAMP 26-81778 (21/08/2026): lote «lanceur mono-coup de calibre 40mm»
adjudicado el 16/06/2026 a Rivolier SAS por 6.083.615 €, más 1.906.840 € del lote de visores, total
publicado 7.990.455 €. Verney-Carron no figura en ningún campo de ninguno de los dos expedientes.

**El contrato de 2026 no es de Verney-Carron ni son 15 M€ ni 6.000 lanzadores.** Lyon Capitale
(2/07/2026) escribió «un marché à 15 millions d'euros» y «près de 6 000 lanceurs mono-coup de 40
millimètres», con entregas 2027-2030. El registro oficial dice otra cosa en los tres números: el
titular del lote es Rivolier SAS, el importe publicado es 7.990.455 € y el XML del anuncio de
licitación en TED (referencia 464923-2025, de 15/07/2025) fija «Poste 1: kit composé d'un lanceur
polyvalent […] et d'une cartouchière 3 600». Los 3.600 son la cantidad del escenario de valoración
del precio, en un acuerdo marco de 48 meses sin mínimo ni máximo publicados, de modo que lo correcto
es decir que la única cantidad publicada oficialmente es 3.600 kits. La compra de Verney-Carron por
el grupo Rivolier en junio de 2025 solo consta en esa misma prensa.

**En Catalunya es la misma arma y nunca se llama LBD 40.** El protocolo de los Mossos identifica
«marca i model: Brugger & Thomet BT-GL06. Llançadora mono tir del calibre 40x46», con munición
«d'impacte, SIR i SIR-X. Gas CS. Fumígena». La denominación oficial catalana es «llançadora de
40 mm».

---

### 6 · La granada de Rémi Fraisse

**Fue una OF-F1, no una GLI-F4.** El TEDH lo declara hecho no controvertido en *Fraisse et
autres c. France* (demandas 22525/21 y 47626/21, sentencia de 27 de febrero de 2025): «celui-ci
est décédé des suites de l'explosion d'une arme de dispersion à effet de souffle, une grenade
offensive OF-F1 lancée dans le cadre d'une opération de maintien de l'ordre par le maréchal des
logis-chef J., et tombée accidentellement entre son cou et le sac à dos qu'il portait». El
lanzamiento fue «en cloche» a la 1h45 del 26 de octubre de 2014 y la muerte se produjo a la
1h53. Ya el 28 de octubre de 2014 el procureur de la République de Albi lo había anunciado
públicamente. El frontmatter y el cuerpo de la ficha estaban mal y la nota de precisión tenía
razón.

**El recuento de la noche es 339, no 700.** Fueron 237 granadas lacrimógenas (CM6/MP7), 38
GLI-F4, 23 OF-F1 y 41 balas de defensa LBD 40 × 46. El Défenseur des droits lo formula como
«339 déflagrations sur un laps de temps d'un peu plus de trois heures» (décision MDS-2016-109).
Las «42 OF1» y las «10 GLI-F4» que traía la ficha no aparecen en ningún documento primario y
deben borrarse.

**La OF-F1 se retiró en tres pasos.** Suspensión de uso por Bernard Cazeneuve el 28 de octubre
de 2014, dos días después de la muerte; prohibición con efecto inmediato el 13 de noviembre de
2014 al publicarse el informe conjunto IGGN/IGPN; supresión definitiva por el décret n° 2017-1029
de 10 de mayo de 2017, que ordena que «dans le tableau figurant à l'article D. 211-17 du code de
la sécurité intérieure, les mots "grenades OF F1" sont supprimés».

**Francia fue condenada.** El TEDH declaró por unanimidad la violación del artículo 2 en su
vertiente material, y la no violación en la procesal, «en raison des lacunes du cadre juridique
et administratif alors applicable et des défaillances de l'encadrement dans la préparation et la
conduite des opérations litigieuses». Antes: non-lieu del TGI de Toulouse el 8 de enero de 2018,
confirmado por la cour d'appel el 9 de enero de 2020, recurso rechazado por la Cour de cassation
el 23 de marzo de 2021, y responsabilidad sin falta del Estado declarada por el tribunal
administratif de Toulouse el 25 de noviembre de 2021, que sin embargo apreció «une imprudence
fautive de la victime, exonérant partiellement l'État», con 14.400 € por progenitor, 9.600 € para
la hermana y 4.000 € por abuela.

---

### 7 · Tarajal

**Cinco botes de humo, no 36.** La cifra oficial la dio el secretario de Estado de Seguridad,
Francisco Martínez Vázquez, en la Comisión de Interior del Congreso el 19 de marzo de 2014:
«en lo que respecta al material antidisturbios empleados, se consumió el siguiente: 145 pelotas
de goma, cartuchos de proyección y 5 botes de ocultación». Irídia, que asiste a un superviviente
ante el Comité contra la Tortura de la ONU y trabaja con el sumario, da en 2025 la misma cifra y
completa el número que faltaba: «al menos 145 balas de goma, 355 cartuchos de proyección (salvas)
y 5 botes fumígenos, en un margen de tan solo 21 minutos». Ninguna fuente sostiene 36. Cuidado
también con El Salto, que escribe 15 y es un error frente al Diario de Sesiones.

**Las 145 pelotas de goma sí están bien**, y el «5» de la ficha estaba colocado en la casilla
equivocada: los 5 son los botes de humo y las salvas fueron 355. El desglose 145 + 355 + 5 suma
505, que es la cifra de disparos que circula asociada al recuento sobre las grabaciones.

**Samba Martine no tiene nada que ver con Tarajal, y el error es rastreable.** Era una mujer de
la República Democrática del Congo que murió el 19 de diciembre de 2011 en el Hospital 12 de
Octubre de Madrid, de criptococosis, tras 39 días internada en el CIE de Aluche y después de
pasar por el CETI de Melilla, donde se le había detectado el VIH sin que su historial la
acompañara al traslado. El dictamen 205/2020 del Consejo de Estado recoge esa fecha, esa
nacionalidad, ese hospital y esa causa, y no menciona Ceuta. El origen del error está en un
artículo de El Salto que enumera a las víctimas del Tarajal solo por nombre de pila («Yves,
Samba, Daouda, Armand, Luc, Roger Chimie, Larios, Youssouf, Ousmane, Keita, Jeannot, Oumarou,
Blaise») y, más abajo y en otro contexto, cita «casos como el de Samba Martine o Idrissa Diallo,
ambos fallecidos en CIE». Alguien fusionó los dos «Samba». El del Tarajal es Samba Baya,
senegalés de Kolda, y su cuerpo nunca apareció.

**La lista de 14 víctimas de la ficha hay que retirarla entera.** El informe de Caminando
Fronteras de marzo de 2014, que la propia ficha declara fuente principal, documenta trece
fallecidos, de los cuales doce llevan nombre y el decimotercero aparece expresamente sin
identificar. Los doce nombres del informe son Samba Baya (Senegal, Kolda), Youssouf (Guinea
Conakry), Keita Ibrahim (costamarfileño), Yves Martin Bilong (Camerún), Armand Ferdinand Souop
Tagne (Camerún, 23 años), Jeannot Flame (Camerún), Oumar Ben Sanda (Camerún), Blaise Fotchin
(Camerún), Daouda Dakole (Camerún), Ousman Kenzo (Camerún), Larios Fotio (Camerún) y Nana Roger
Chimi (Camerún). Ninguno de los nombres compuestos que traía la ficha («Armand Zébé Ébongo»,
«Blaise Mathey», «Yves Kimombé Mbenga», «Youssouf Diakité», «Daouda Sylla», «Keita Luis», «Roger
Chi Nkwonta», «Larios Fotiou», «Jeannot Mbida», «Oumarou Mamadou», «Luc Zogo») figura en ninguna
fuente localizable, y varias nacionalidades también estaban cambiadas. El propio informe advierte
de que las identificaciones son provisionales, hechas por familiares y compañeros, y de que «se
ha constatado la existencia de errores en la identificación oficial de algunos cuerpos en
Marruecos».

**El número de muertos es 15 en el recuento oficial y judicial, 14 en el de las ONG.** El
Tribunal Constitucional, en el Auto 338/2023, habla de personas de las que «quince fallecieron
ahogadas en la playa ceutí del Tarajal». El CGPJ, al informar del auto de procesamiento de 24 de
septiembre de 2019, habla de 15 migrantes. El secretario de Estado explicó en el Congreso cómo se
llega a esa cifra: aparecieron cadáveres en la parte española el 8, el 12, el 13 y el 15 de
febrero, cinco en total en aguas españolas, «lo que arroja un balance final de 15 personas
fallecidas». CEAR, Amnistía, APDHA y Caminando Fronteras siguen usando 14, que corresponde a un
recuento distinto de los cuerpos hallados en Marruecos. Para cartela, lo defendible es «al menos
14; 15 según el recuento oficial y judicial». Caminando Fronteras advierte que el total nunca se
sabrá.

**El recorrido judicial de la ficha estaba mal en las tres fechas.** La secuencia documentada es
diligencias previas 123-2014 del Juzgado de Instrucción nº 6 de Ceuta; sobreseimiento provisional
en octubre de 2015; reapertura ordenada por la Audiencia Provincial de Cádiz en enero de 2017;
segundo archivo en enero de 2018; nueva revocación en agosto de 2018; auto de procesamiento de 16
guardias civiles el 24 de septiembre de 2019 por homicidio por imprudencia grave y denegación de
auxilio; sobreseimiento libre por la Sección Sexta de la Audiencia Provincial de Cádiz en julio de
2020; desestimación de los recursos de casación por el Tribunal Supremo en junio de 2022. Y el
Constitucional no rechazó el amparo en 2020: lo admitió a trámite por Auto 338/2023, de 3 de
julio, con voto particular, promovido por la Coordinadora de Barrios, la APDHE y CEAR. Hay además
dos denuncias de supervivientes ante el Comité contra la Tortura de la ONU con apoyo del ECCHR y
de Irídia, la de Ludovic N. en enero de 2024 y la de Brice O. en febrero de 2025.

---

### 8 · SED 1872

**MAXAM es la sucesora societaria; Nobel Sport no tiene ninguna relación con la sociedad
española.** La cadena es 1872, Galdácano (Bilbao), sociedad de dinamita fundada con privilegios
de Alfred Nobel, hoy inscrita en el Registro Mercantil de Madrid como SOCIEDAD ANÓNIMA ESPAÑOLA
DE LA DINAMITA (PRIVILEGIOS A. NOBEL) Y DE PRODUCTOS QUÍMICOS, sociedad unipersonal viva cuyo
socio único es MAXAMCORP HOLDING, S.L. desde el 15/03/2023 (hoja M-32204, tomo 16921, folio 84,
sección 8; CNAE 2051); de ella nace en 1896 Unión Española de Explosivos; hacia 1969-1970 la UEE
se une a la Compañía Española de Minas de Río Tinto y forma Unión Explosivos Río Tinto; en 1989
la fusión con S.A. Cros da lugar a Ercros, que se queda la química, y el negocio de explosivos
recupera trayectoria independiente en 1994; en 2006 el grupo adopta la marca MAXAM.

**No escribir «la UEE pasó a llamarse MAXAM en 2006».** MAXAMCORP HOLDING, S.L. no es una UEE
renombrada: se constituye el 03/02/2006 con CIF B84598754 y su ficha no contiene ningún acto de
cambio de denominación. MAXAMCORP INTERNATIONAL, S.L. se constituye el 01/02/2007. Y Unión Española
de Explosivos SAU sigue figurando como sociedad activa en el Registro Mercantil de Madrid con CNAE
6420 y últimas cuentas depositadas en 2019, trece años después del supuesto cambio de nombre;
UNION ESPAÑOLA DE EXPLOSIVOS-MSI INTERNATIONAL SA no fue absorbida por MAXAMCORP INTERNATIONAL
hasta el 03/03/2023. Lo que hubo en 2006 fue una arquitectura societaria nueva bajo una marca
nueva, con el nombre viejo vivo como sociedad, como marca y como nombre comercial.

La denominación que usa la ficha, «Sociedad Española de Dinamita», es la forma abreviada de la
comunicación corporativa. La registral es la larga, y las fuentes históricas vascas nombran la
sociedad en su origen como «Sociedad Anónima Española de la Pólvora Dinamítica».

**Nobel Sport es francesa y su origen es la pólvora, no la dinamita.** Su web reivindica una
tradición tricentenaria: la fábrica de Pont-de-Buis-lès-Quimerc'h (Finistère) nace de una orden de
Colbert de 19 de noviembre de 1687. La sociedad Nobel Sport explota ese emplazamiento desde 1994
como filial de la SNPE, que le cedió por completo su departamento de caza en el año 2000, y hoy
pertenece al grupo SofiSport junto con Cheddite. El apellido «Nobel» le viene por la rama francesa,
la Société Générale de la Dynamite creada en 1875 por Paul Barbe y Alfred Nobel, cuya heredera
societaria es Titanobel, adquirida por Incitec Pivot en 2022 y rebautizada Dyno Nobel en 2025.
Ni MAXAM ni Nobel Sport.

**Nobel Sport España se constituyó en 1993, no en 1872.** CIF A24271165, Registro Mercantil de
León, domicilio en Término de Villacil s/n, 24228 Valdefresno. Cambió su denominación a NOBEL
SPORT EXCOPESA, S.A. por inscripción de 9 de enero de 2025, publicada en el BORME el 16 de enero
de 2025. El dominio nobelsportespana.com que cita la ficha redirige hoy con un 301 a cartuchosjg.com.

---

### 9 · Serie de facturación del mercado mundial

**El 867 M$ de 2019 mide otro mercado, y por eso desentona.** Grand View Research
estima en 867,4 M$ el segmento de *less lethal ammunition* en 2019, que cubre solo proyectiles y
cartuchos y excluye Tasers, cañones de agua, LRAD y armas de energía dirigida. Los vecinos de
5.600-8.600 M$ son el mercado *non-lethal weapons* completo. MarketsandMarkets sitúa el segmento
de munición en 828 M$ (2018) y Polaris en 1.230 M$ (2022), lo que confirma la escala.

**Los 8.370 M$ de 2020 son una previsión de 2016, no una medición.** Proceden de
MarketsandMarkets, *Non-Lethal Weapons Market — Global Forecast to 2020*, publicado el 4 de abril
de 2016. Los 6.150 M$ de 2021 son un año base estimado por The Insight Partners cinco años
después. La caída aparente 2020 → 2021 es un artefacto de poner una proyección al lado de una
base real de otra consultora, sin ningún hecho económico detrás. La previsión de 2016 sobreestimó
el mercado en torno a un 35%.

**El «SGI Global Security Index» no puede ser fuente de 2015.** Es un índice bursátil patrocinado
por Société Générale sobre empresas de seguridad, que mide cotizaciones y no facturación
sectorial. Los 5.650 M$ de 2015 se deducen de la misma serie de MarketsandMarkets (8,37 / 1,082⁵
= 5,645). Error de categoría en la atribución.

**Los 8.580 M$ de 2024 son de Renub Research, no de INCLO.** *Lethal in Disguise 2* (INCLO, PHR y
Omega) se publicó el 22 de marzo de 2023 y no puede contener una estimación de 2024, y su página
oficial no recoge ninguna cifra de tamaño de mercado. Renub da 8,58 mm$ (2024) → 13,91 mm$ (2033),
CAGR 5,52%, y su ficha vigente ya ha corrido la base a 8,53 mm$ (2025) → 13,88 mm$ (2034).

**Los 9.380 M$ de 2028 son 9.280 en el informe original.** The Insight Partners proyecta «USD 9.28
billion by 2028». Los 9.380 vienen del Informe 56 del Centre Delàs, compatibles con aplicar un
+52% redondeado a 6.150. Si se usa, poner 9.280 M$ (The Insight Partners) o citar explícitamente
al Delàs.

La conclusión general es que la tabla encadena cuatro orígenes con definiciones no comparables, y
que la dispersión entre consultoras para un mismo horizonte va de 1,94 a 19,60 mil millones. Estos
informes comerciales no son fuente primaria en sentido estricto y conviene decirlo cada vez que se
usen.

---

### 10 · Empresas del sector

**Ninguna de las dos cifras estaba mal transcrita; lo que estaba mal era la atribución y el
montaje en serie.** El «370 en 40 países» no sale del informe STOA de 1998 sino del estudio final
*Crowd Control Technologies*, PE 168.394/FinSt., junio de 2000, resumen ejecutivo p. xix, y dice
«more than 369 major manufacturers, suppliers or distributers across 40 countries» por 1999,
frente a «only 13 companies in 5 countries» en 1978. Son fabricantes, proveedores y distribuidores
rastreados en literatura de ferias, no empresas fabricantes. El informe de 1998 (PE 166 499) da un
número distinto y mucho mayor, «some 856 companies across 47 countries», en recuento acumulativo.

**El «200 en 60 países» es de Omega, no del Centre Delàs.** El Informe 56 del Delàs (Ainhoa Ruiz
Benedicto y Anna Montull Garcia, noviembre de 2022, pp. 13-14) lo cita correctamente atribuyéndolo
a la Omega Research Foundation, 2019, cuyo texto original dice «Omega's databases contain details
of over 200 companies in over 60 countries currently manufacturing less lethal weapons». Su nota 11
precisa que la consulta excluyó medios de inmovilización y protecciones balísticas, y que cuenta
solo empresas que fabrican actualmente.

**No encadenar las tres cifras.** Cuentan cosas distintas. O se usa la serie homogénea de Jane's que
publica la propia Omega, 13 empresas en 5 países (1978) → 50 en 17 (1999) → 89 en 28 (2014-15), o
se dan los dos datos por separado con su definición. Convertir «more than 369» en «370» cerrado
también altera el dato.

---

### 11 · Bahréin 2011

**Las dos cifras son de PHR y son dos cortes de la misma serie.** Los 34 son de marzo de 2012, no
de agosto: PHR, *Tear Gas or Lethal Gas? Bahrain's Death Toll Mounts to 34*, 16 de marzo de 2012,
ventana desde el inicio del levantamiento (14 de febrero de 2011) hasta la publicación, y la
formulación exacta es «34 reported tear-gas-related deaths», compiladas a partir de entrevistas
con médicos locales y prensa. Los 39 son de *Bahrain's Continued Weaponizing of Tear Gas*, 25 de
octubre de 2013: «at least 39 confirmed deaths since 2011». Entre medias, el 27 de enero de 2012
PHR daba 13. El calificativo cambia de «reported» a «confirmed», de modo que conviene atribuir
cada cifra a su documento y a su fecha en vez de presentarlas como una progresión.

**El informe de agosto de 2012 no contiene ninguna cifra agregada.** *Weaponizing Tear Gas:
Bahrain's Unprecedented Use of Toxic Chemical Agents Against Civilians* (1 de agosto de 2012) solo
menciona el 34 en su nota al pie 56, remitiendo al texto de marzo. La ficha bahrein-2011 atribuye
el 34 al informe de agosto y hay que corregirlo.

**El informe Bassiouni no respalda ninguna de las dos.** El informe de la Bahrain Independent
Commission of Inquiry (23 de noviembre de 2011, revisión final de 10 de diciembre) tiene 67
menciones de «tear gas», todas en relatos de casos individuales, y ninguna en forma de recuento.
Lo que sí da es «between 14 February and 15 April 2011, there were 35 deaths that were linked to
the unrest in Bahrain during that period» (párrafo 848). Es fuente primaria para casos nominales,
no para la cifra agregada.

**Dos víctimas de la ficha están mal fechadas o mal identificadas.** Sayed Hashim Saeed (15 años)
no murió el 6 de octubre de 2011: el BCHR lo fecha el 30 de diciembre de 2011 y la cronología de
PHR el 31. Y el «Isa Abdul-Hassan (60 años), febrero 2011» no encaja con ningún registro; el caso
que sí consta en el listado del BCHR es Isa Mohammed Ali Abdullah, 71 años, Ma'ameer, muerto el 25
de marzo de 2011, asfixiado en su casa tras un gaseo extensivo del pueblo. Sí queda confirmado Ali
Jawad al-Shaikh, 14 años, impacto directo de bote en la cabeza, 31 de agosto de 2011.

---

### 12 · Chalecos amarillos

**Los 19.071 son el año natural 2018 completo, no los primeros seis meses del movimiento.** El
informe anual de la IGPN de 2018, p. 29, da 4.005 declaraciones de empleo para 19.071 municiones
de LBD disparadas en 2018, un +200% respecto a 2017. El movimiento empezó el 17 de noviembre de
2018, de modo que seis meses de movimiento llegan hasta mayo de 2019 y no coinciden con el año
2018. La cifra equivalente para el arranque es otra: 13.460 disparos de la Police nationale entre
el 17 de noviembre de 2018 y el 5 de febrero de 2019, según datos de la IGPN recogidos por el
Sénat, más «un millar» estimado por la IGGN para la gendarmería móvil.

**Serie anual documentada.** Police nationale, todas las unidades, según datos del Ministerio del
Interior transmitidos a la comisión de leyes del Sénat: 2014, 3.814; 2015, 4.915; 2016, 6.604;
2017, 6.543; 2018, 19.071. Gendarmerie mobile, misma tabla: 7, 18, 15, 48 y 983. Continuación
según los informes anuales de la IGPN: 2019, 10.785 (−43%); 2020, 7.275. El control aritmético
cierra: la IGPN 2020 escribe «96 blessés pour 37.131 tirs» sobre los tres últimos años, y 19.071 +
10.785 + 7.275 = 37.131 exactos.

**Los 18.805 no contradicen nada.** No son una serie 2018-2020, son las municiones de LBD
disparadas entre el 17 de noviembre de 2018 y el 31 de diciembre de 2019, según el informe del
Observatoire des Street-médics de donde el Centre Delàs toma la cifra, junto con las 6.735 granadas
de désencerclement del mismo periodo. La aritmética lo confirma: 18.805 − 10.785 (año 2019
completo) = 8.020 para el tramo 17-nov a 31-dic de 2018, y 19.071 − 8.020 = 11.051 para el 1-ene a
16-nov. Corregir la atribución de periodo en centre-delas-armas-letales.

**El 480 es un multiplicador y no compara con el año anterior.** Paul Rocher escribe «entre 2009 et
2018, les tirs de LBD ont été multipliés par 480, passant de 40 à 19 000». El aumento de 2017 a
2018 fue del +200% según la IGPN. Queda sin verificar que en 2009 se dispararan 40 proyectiles:
Rocher lo atribuye genéricamente a «les chiffres du ministère de l'Intérieur» sin referencia, el
Défenseur des droits escribió en 2017 que «aucune donnée officielle ne nous renseigne sur le nombre
de fois où cette arme est utilisée», y el fichero TSUA, único registro sistemático, arranca en enero
de 2012. En 2009 el LBD 40 acababa de introducirse y lo que se usaba masivamente era el Flash-Ball,
de manera que el ×480 mide sobre todo la sustitución de un arma por otra.

**El 335.300 es una suma indebida.** El Observatoire des Street-médics, informe 2019-2020, estima
para el 17 de noviembre de 2018 - 14 de marzo de 2020: 27.800 (±3.360) personas heridas en total,
de ellas 24.300 (±4.200) atribuibles a las fuerzas del orden, y 311.000 (±47.200) personas
afectadas por gases lacrimógenos. El 335.300 de la wiki es 24.300 + 311.000, es decir heridos más
gaseados, que el informe presenta por separado. El 24.000/300.000 de Rocher es un redondeo de esas
mismas cifras y no un recuento distinto.

**La cifra oficial es 2.495, y solo cuenta a quien atendieron los bomberos.** Es el recuento del
COGIC transmitido por el Ministerio del Interior. El propio informe advierte que «ce chiffre du
COGIC ne comptabilisant en réalité que les personnes prises en charge par les sapeurs-pompiers». La
proporción entre recuento independiente y cifra oficial es de unas diez veces (24.300/2.495 ≈ 9,7),
no de 150 como decía impacto-agregado.

---

### 13 · Las foam SIR-X

**El fabricante es B&T AG (Suiza) y «SIR» significa Safe Impact Round.** No existe ninguna empresa
española SIR ni el nombre viene de «Sistema de Impacto Reducido». El protocolo de los Mossos lo
consigna literalmente: «característiques tècniques informades pel fabricant: Fabricant: B&T AG,
Suiza. Nombre: B&T 40 mm SIR-X», y para el SIR «ID del Producte: BT-23510. Número OTAN:
1310-22-616-1134». B&T lo confirma en su propia página del GL06: «a special feature of the GL06
family is its compatibility with the SIR ammunition (Safe Impact Round) developed by B&T». El
SIR-X es la variante de mayor alcance, misma ojiva y vaina distinta. La suministradora al
Departament d'Interior fue Eurodistribución de Sistemas España (EDS), S.L., que es distribuidora.
Esto obliga a corregir toda la wiki: hay que buscar B&T, no una empresa española.
<https://mossos.gencat.cat/web/.content/home/01_els_mossos_desquadra/eines_policials/doc/Protocol-dutilitzacio-de-les-llancadores-de-40-mm-i-dels-seus-projectils_16_07_2019-Revisio_27_10_2023-1.pdf>

**Los 20 m son del protocolo policial, no del fabricante, y la ficha de Roger García invierte el
sentido de la denuncia.** El PIT núm. 22, en su versión anterior a octubre de 2023, fijaba «la
distància per disparar aquest cartutx és de 20 a 50 metres» para el SIR-X y de 5 a 25 para el SIR.
Esa es precisamente la cifra que Irídia denuncia por ser inferior a la del fabricante. Ninguna
fuente atribuye 20 m a B&T.

**Los 30 m del protocolo vigente son de un dictamen de Omega, no del fabricante.** La revisión de
27 de octubre de 2023 fija en su apartado 3.2.2 que «les distàncies d'ús es troben entre els 30
metres la mínima i els 50 metres la màxima», y añade que «les distàncies establertes són més
garants que les del marge de seguretat proposat pel fabricant (25 metres la mínima i 80 la
màxima)», con nota al pie que remite al «Dictamen pericial de la Fundació d'Investigació Omega
sobre el Protocol dels Mossos d'Esquadra en l'ús del projectil SIR-X». El SIR sube de 25 a 30 m de
máximo. La revisión restringe además el disparo de abdomen hacia abajo.

**El argumento del caso de África se sostiene, y no depende de si el fabricante dice 25 o 30.** En
febrero de 2021 el protocolo permitía disparar desde 20 m, con lo que un disparo a 22 m quedaba
dentro del protocolo policial y por debajo de las dos cifras atribuidas al fabricante. La frase «con
20 m el fabricante quedaría cumplido» es falsa porque 20 m nunca fue cifra del fabricante. Dato
mejor y más visual, documentado por Irídia: la calle donde ocurrió no supera los 30 metros de
ancho, lo que hace materialmente imposible respetar un mínimo de 30 m.

---

### 14 · Menores, armas y fechas

**Rufo Chacón: 64 es compatible con el parte de Corposalud, y la fecha y el cuerpo policial de la
ficha están mal.** Luis Ramírez, presidente de Corposalud Táchira, el día de la cirugía habló de
«ocho perdigones en el globo ocular derecho, y cinco perdigones en el izquierdo, además de 52
perdigones en todo lo que es la región facial». El «además de» es decisivo: los 52 no incluyen los
oculares, y 52 + 12 o 13 da 64 o 65. El «64 perdigones» que declaró el propio Rufo a NTN24 en
noviembre de 2019 coincide con la suma de lo que dijo la autoridad sanitaria. El hecho es del 1 de
julio de 2019, no del 2 (la cirugía fue de madrugada del 2 y la prensa publicó ese día), y los
disparos fueron de Politáchira, no de la PNB, aunque a la protesta acudieran también la GNB y la
PNB. Los dos agentes fueron condenados el 4 de octubre de 2021, Javier Useche Blanco a 27 años y 9
meses y Henry José Ramírez Hernández a 21 años y 5 meses.

**Los Ángeles 1992: 63 son fichas investigadas, 54 muertes vinculadas.** La base de datos caso por
caso del Los Angeles Times («Deaths during the L.A. riots», 25 de abril de 2012) tiene 63
registros, y el propio periódico clasifica 9 como «Not riot-related». El desglose es 36
«Homicide», 10 «Officer involved shooting», 8 «Death» y 9 descartadas. Coincide con su cabecera:
«ten were shot to death by law enforcement officials. An additional 44 people died in other
homicides or incidents tied to the rioting». Public Health Reports, del Departamento de Salud del
Condado, da 53 muertes y 2.325 heridos. «63 muertos» a secas no es defendible.

**Irlanda del Norte: 17 muertos, 8 menores.** La wiki se equivocaba en los dos números. Tres
muertos por bala de goma, introducida en 1970, y catorce por bala de plástico, introducida por el
ejército en 1973 y por la RUC en 1978. Los ocho menores son Francis Rowntree (11, 22 abril 1972,
bala de goma), Stephen Geddis (10, 30 agosto 1975), Brian Stewart (13, 10 octubre 1976), Paul
Whitters (15, 25 abril 1981), Julie Livingstone (14, 13 mayo 1981), Carol Ann Kelly (12, 22 mayo
1981), Stephen McConomy (11, 19 abril 1982) y Seamus Duffy (15, 9 agosto 1989). Los otros nueve
son Tobias Molloy (18), Thomas Friel (21), Michael Donnelly (21), Henry Duffy (45), Nora McCabe
(30), Peter Doherty (36), Peter McGuinness (41), Sean Downes (22) y Keith White (20). Todos
católicos salvo Keith White. Responsables: British Army en 11 casos, RUC en 6. El informe del
Committee on the Administration of Justice de 1998 llega a la misma suma por otro camino:
«responsible for the deaths of 14 people, seven of whom were children», más «the rubber bullet,
first used in 1970, which resulted in three deaths». Confirma también que en 1981 murieron siete
personas por balas de plástico, cuatro adultos y tres menores, lo que corrige el «5» de
cronologia-completa, y documenta 16.656 balas de plástico disparadas solo en mayo de 1981.

**GLI-F4: retirada en enero de 2020, con la sustitución empezada en 2018.** El Ministerio del
Interior francés certifica por escrito que «la GLI F4 n'est donc plus utilisée par les FSI depuis
janvier 2020 avant même l'épuisement des stocks», tras el anuncio del ministro el domingo 26 de
enero de 2020. La sustituta es la GM2L, sin carga explosiva: «la suppression de la matière
explosive présente dans la GLI F4 par une composition pyrotechnique dans la nouvelle grenade GM2L
lui retire l'effet de souffle». La sustitución había empezado en el segundo semestre de 2018 según
la respuesta del Gobierno al Sénat de 21 de febrero de 2019.

**PR-24: la datación de 1958 no se sostiene.** El portfolio completo de Monadnock Lifetime Products
en Google Patents son 15 resultados, y la patente más antigua tiene prioridad de 13 de febrero de
1976 (CA1079320A, «Police type baton», inventor Paul D. Starrett). No hay ninguna patente de
Monadnock anterior a 1976, ni de 1958 ni de 1971. Esa patente de 1976 describe además un bastón
recto con un anillo, no un bastón de mango lateral. Retirar el 1958 de cronologia-completa y de
porra-tonfa; la datación de 1971 tampoco ha podido documentarse con fuente primaria.

**Primera Intifada: 1987-1993, y el 1988-1998 es la ventana de una serie estadística.** En la wiki
ese rango aparece siempre pegado al dato «58 palestinos muertos por balas de goma del ejército
israelí en 10 años». Hay que separar las dos cosas y atribuir la cifra a su fuente. La ficha
ciivo-ver-mas-alla-herida-2026, que da 1987-93, es la que coincide con la datación estándar.

**Protocolo IV de la CCW: adoptado en 1995, Estados Unidos obligado desde el 21 de enero de 2009.**
El Protocolo sobre armas láser cegadoras se adoptó en Viena el 13 de octubre de 1995 y entró en
vigor el 30 de julio de 1998. El registro depositario de la ONU (capítulo XXVI-2-a) no tiene
columna de firma para este instrumento, los Estados manifiestan consentimiento en obligarse, y
Estados Unidos consta con fecha 21 de enero de 2009, catorce años después. Fue transmitido al
Senado el 7 de enero de 1997 y el Comité de Relaciones Exteriores lo informó favorablemente el 29
de julio de 2008. El apunte sobre el programa PEP que la ficha colgaba de «el mismo año» pierde su
base cronológica.

**Catalunya: la resolución es de diciembre de 2013 y la prohibición efectiva de abril de 2014.** Son
tres actos distintos que la wiki había fundido en uno. La Resolució 476/X del Parlament de
Catalunya se adoptó en el Ple el 18 de diciembre de 2013 y se publicó el 23, y aprueba las
conclusiones del Informe de la Comissió d'Estudi dels Models de Seguretat i Ordre Públic i de l'Ús
de Material Antiavalots en Esdeveniments de Masses. No es una ley. El apartado 24 de esas
conclusiones ordena iniciar «inmediatamente» la retirada y fija que «en data 30 d'abril de 2014
sigui efectiva la prohibició total». Y el acto ejecutivo es la Instrucció 11/2014, de 30 d'abril,
de la Direcció General de la Policia, firmada por Manel Prat i Pelaez.

**La Instrucció 11/2014 no menciona el foam ni el SIR-X.** Hace dos cosas: incorpora a la
Instrucció 16/2013 un punto nuevo, el 3.10, sobre el «dispositiu acústic de llarg abast» (LRAD), y
deroga la autorización del uso de pilotes de cautxú o de goma del punto 3.7 y su anexo, «en
especial en el PNT217/03/11 d'actuació policial en concentracions i manifestacions». Corregir
mossos-instrucciones-armamento: 11/2014 es retirada de la goma más entrada del LRAD.

**TEDH: las dos grafías y las dos signaturas.** Kılıcı c. Turquie, demanda nº 32738/11, sentencia
de 27 de noviembre de 2018, artículo 3. Los hechos son del 16 de marzo de 2009 en Estambul, con
impacto de bala de goma en la espalda y «une rougeur et une ecchymose sur une zone de forme ovale
d'une dimension approximative de 3 x 2 cm», y 5.000 € por daño moral. El §32 no declara que las
balas de goma violen el artículo 3 como regla general: razona que, aunque la lesión concreta fue
leve, la peligrosidad de esa munición no ofrece duda y el demandante quedó expuesto a un riesgo de
lesión mayor. Para el documental esa formulación es más útil que la maximalista, porque el
Tribunal reconoce la peligrosidad del arma incluso con daño mínimo. Abdullah Yaşa y otros c.
Turquía, demanda nº 44827/08, sentencia de 16 de julio de 2013, firme el 16 de octubre: impacto
directo de una granada de gas lacrimógeno en la nariz de un niño de 13 años el 29 de marzo de 2006
en Diyarbakır. Renombrar las dos fichas y añadir las signaturas.

---

## Sigue sin poder verificarse

Esto no es lo que quedó pendiente de mirar. Es lo que se buscó a fondo y no se pudo cerrar con
documento. Va aquí para que nadie lo dé por bueno por cansancio, y con la vía concreta por donde
habría que ir a buscarlo.

**Los 830 J de la bala de goma española.** No existe documento primario. La cifra nace en el
artículo de Gisbert (Diagonal, 26 de abril de 2012) sin referencia y se repite en La Marea el 11
de junio de 2013 atribuida al informe de Stop Bales de Goma de 2013, sin medición ni ficha
técnica. El enlace de Irídia a ese informe (issuu.com/stopbalesdegoma/docs/informe-sbg2013_es)
devuelve 404. Los 144 J de Irídia tampoco tienen doble fuente independiente: la corroboración es
aritmética (masa oficial por velocidad de fabricante), no una segunda medición, y el catálogo de
MAXAM que da los 60 m/s se cita a través de Irídia porque maxam.net ya no resuelve. Por dónde
seguir: pedir a Irídia el catálogo *Law Enforcement* de MAXAM que citan en su nota 92. (El informe de
Stop Bales de Goma de 2013 ya está localizado: ver arriba.)

**El informe de Stop Bales de Goma de 2013 SÍ está disponible** (comprobado el 27 de agosto de 2026).
La URL de `stopbalesdegoma.wordpress.com` devuelve **HTTP 200 y 5,8 MB**, y hay copia en el Internet
Archive (instantánea de 5 de julio de 2024). Lo que da 404 es el **enlace de issuu que cita Irídia**,
no el original. Este pendiente queda cerrado.

**El informe de test TR-16973.02 de B&T sobre el SIR-X.** Es la única fuente de los «30 metros del
fabricante», y solo la cita Irídia. Toda la prensa del 16 de febrero de 2022 (Directa, VilaWeb,
NacióDigital, El Punt Avui, elmon.cat, elDiario.es) reproduce su nota y no es independiente.
Amnistía Internacional Catalunya repite los 30 m en diciembre de 2023, probablemente de la misma
fuente. B&T no publica especificaciones de la SIR-X y el distribuidor solo da alcance efectivo (80
m). Para cartela hay que escribir «según el informe de test TR-16973.02 de B&T citado por Irídia»,
o usar los 25 m, que sí están en documento oficial abierto. La formulación completa que Irídia cita
es más específica de lo que teníamos: por debajo de 30 metros el proyectil puede causar «lesiones
severas como laceraciones, traumatismo craneoencefálico, rotura de bazo, hígado o corazón,
traumatismo torácico grave y hemorragias internas».

**Y hay un desenlace que la wiki no tenía**: el **28 de marzo de 2025 los Mossos retiraron el SIR-X**
de los arsenales de la ARRO y de la Brimo, por orden de Josep Lluís Trapero, en cumplimiento del
acuerdo del Parlament de 2023. Las unidades de orden público quedan solo con el SIR. Por dónde seguir: pedirlo a Irídia,
que lo tiene, y buscarlo en el sumario del Juzgado de Instrucción 7 de Barcelona.

**El dictamen pericial de la Fundació d'Investigació Omega sobre el protocolo de los Mossos.** Lo
cita el propio protocolo en su nota al pie como fundamento del margen de 30 a 50 metros, y no está
en línea. Por dónde seguir: pedirlo directamente a Omega Research Foundation.

**El pliego de licitación del SIR-X y las respuestas parlamentarias del Parlament.** No aparecen.
Lo que sí está documentado son los contratos de compra a Eurodistribución de Sistemas España (EDS),
S.L.: 240.891 € en 2014, 450.404 € en 2016 y un expediente de urgencia de 721.462 € el 22 de
octubre de 2019, en total 159.300 cartuchos por 1.412.757 € desde 2014 más 540.142 € en
equipamiento, según la investigación de CRÍTIC. Ninguno contiene distancias de empleo. Quedan sin
explorar el Portal de Contractació Pública de la Generalitat, las respuestas escritas del Parlament
y el informe de la Comissió d'Estudi del Model Policial.

**El gramaje de la GLI-F4.** No hay ficha técnica de Alsetex ni documento oficial francés con
gramos. La respuesta del Ministerio del Interior a la pregunta escrita AN nº 16653 habla solo de
«la matière active composée en partie de tolite», sin cantidad, y los «25 g de TNT» que circulan
proceden del texto de la pregunta del senador Pierre Laurent (nº 08058, 06/12/2018), no de la
respuesta. Circulan al menos tres versiones incompatibles. Precisión terminológica que la wiki
confunde: la literatura francesa habla de «hexocire», mezcla de hexógeno y cera, no de hexógeno
puro. No poner gramaje en cartela, o ponerlo atribuido y nunca como dato de fabricante.

**Los 165 dB de la GLI-F4.** Aparecen en documentos oficiales franceses solo dentro del texto de la
pregunta del diputado Bastien Lachaud, como afirmación suya. La respuesta del Ministerio describe
el «triple effet lacrymogène, sonore et de souffle» sin dar decibelios. La precisión «a 5 metros»
solo está en Désarmons-les! y en Wikipedia.

**Los decibelios del LRAD.** Ninguna de las tres cifras de la wiki (162, 150-162, 152 dB SPL) es
trazable: Genasys no publica especificaciones acústicas, las fichas de producto están detrás de un
formulario de captación y las páginas de recurso devuelven solo navegación. La hipótesis de que la
divergencia se explique por el modelo es plausible y no se ha podido documentar. Corrección
colateral que sí sale del catálogo del fabricante: los modelos LRAD 2000X y 3000X ya no figuran en
su gama. La actual es 100X, 450XL-MNT-MAG, 450XL-MNT-VAC y 100X-BLK-MAG-SYS (portátiles); 450XL-RT,
450XL-MMT, 500X-RT y 500X-MMT (medio alcance); 950NXT, 1000Xi-RT y 1950XL-RT (largo alcance); más
Mobile Sound Shield, Mobile Range System y 360XT.

**La prohibición de las balas de goma en Euskadi.** Ni 2012 ni abril de 2015 han podido
documentarse, y hay indicios de que el marco entero es incorrecto. Las dos piezas de elDiario.es
Euskadi que se pudieron abrir describen un cese de hecho, y una afirma explícitamente que no están
prohibidas sino desplazadas por una lanzadera de proyectiles viscoelásticos. Lo que se puede
afirmar con la prensa disponible, con la cautela de que es una sola redacción, es que desde la
muerte de Cabacas en abril de 2012 la Ertzaintza no ha vuelto a disparar una pelota de goma. No
poner ninguna de las dos fechas en cartela hasta tener el documento del Departamento de Seguridad
o del Parlamento Vasco.

**Las víctimas identificadas y no identificadas del Tarajal.** No hay cifra oficial consolidada y
las fuentes se contradicen. Amnistía escribió en febrero de 2015 que «aunque se cree conocer la
identidad de seis de los fallecidos, solo uno fue identificado oficialmente», y siete años después
que lo grave es «que no se haya identificado a cuatro de las víctimas», lo que implicaría once.
Caminando Fronteras documenta doce nombres y los califica de provisionales, y denuncia que la
identificación no pudo cerrarse por prohibición de identificación visual de los cuerpos,
prohibición de obtener fotografías para las familias y enterramiento exprés de los cuerpos hallados
en territorio español. La formulación honesta es «identificadas provisionalmente por familiares y
compañeros: doce. Identificación oficial: nunca completada». No poner cifra cerrada de no
identificados.

**El recuento propio del Centre Delàs de muertes en España.** No existe, o no está publicado. El
Centre Delàs trabaja el ángulo de industria y comercio; el censo de víctimas lo hacen Stop Bales
de Goma, Irídia y Novact. Su servidor está además protegido con Anubis y devuelve una página de
desafío en lugar del contenido. Retirar la atribución allí donde aparezca.

**Un recuento académico o parlamentario de muertes en España con metodología publicada.** No
aparece ninguno. Lo que hay en el lado parlamentario es la negación de que exista un recuento, en
las respuestas del Gobierno a Jon Iñarritu.

**Los 40 disparos de LBD en 2009 que sostienen el ×480 de Rocher.** Rocher lo atribuye
genéricamente a «les chiffres du ministère de l'Intérieur» sin referencia. El Défenseur des droits
escribió en 2017 que «aucune donnée officielle ne nous renseigne sur le nombre de fois où cette
arme est utilisée», y el fichero TSUA arranca en enero de 2012. El multiplicador puede citarse
atribuido a Rocher, no como dato oficial.

**El trabajo de Sebastian Roché sobre uso de la fuerza.** Quedó sin abrir. El presupuesto de
búsquedas de esa sesión se agotó antes de llegar. Pendiente para una segunda pasada.

**Las decisiones del Défenseur des droits sobre la GLI-F4.** Su portal documental devuelve «aucun
document trouvé» para «GLI-F4» y para «grenade lacrymogène instantanée». Que se pronunció lo
afirman terceros sin número de decisión. Hay que ir por número de decisión, no por buscador.

**Los informes de mercado comerciales, en bloque.** Ninguno alcanza el nivel de fuente primaria ni
el de informe de ONG con metodología publicada. No publican metodología auditable, lo único
accesible sin pagar es la nota de prensa (que es material de marketing del informe de pago) y
reescriben sus páginas en silencio: durante esta verificación, MarketsandMarkets, Global Market
Insights y Renub ya habían sustituido las cifras que citaba la ficha. Si van a pantalla, con
nombre de consultora, año de publicación y definición de mercado delante.

**La fecha del programa de Carne Cruda.** La contradicción puede ser aparente. El «26 de noviembre
de 2024» aparece tres veces en tres fichas distintas (africa-pablo-hasel, roger-garcia-foam-2019 e
iridia), siempre con el mismo identificador de episodio, «T12x47 — Tu palabra contra la de la
policía». El «noviembre de 2025» aparece una sola vez y no se refiere al programa: «Roger publicó
su testimonio en Instagram en noviembre 2025». Son dos hechos distintos, y basta con desambiguar la
frase.
---

## Correcciones aplicadas en las fichas

**Aplicadas el 26 de agosto de 2026** en la rama `correcciones-auditoria-agosto-2026`, cuatro
commits, 40 fichas tocadas. Cada corrección lleva la fuente escrita dentro de la ficha, y las que
retiran un dato dejan constancia de qué se retiró y por qué, para que no vuelva a entrar. `build.py`
corre limpio con 235 notas y no quedan enlaces internos rotos nuevos.

Dos cosas no se han tocado. Las **transcripciones literales**: la comparecencia de la Dra. Estrella
Fernández ante el Parlament cita los 720 km/h, y lo que se ha hecho es añadir una nota editorial
delante, sin alterar sus palabras. Y los **nombres de fichero** de las dos del TEDH: renombrarlas
obligaría a reescribir todos los enlaces entrantes, así que la grafía queda corregida en el
contenido y el fichero se deja como está.

| Ficha | Qué cambia |
|---|---|
| `casos/espana-europa/roger-espanol.md` | Retirar «830 J» y «umbral 522 J del STOA». Reescribir el bloque técnico con 144 J máximos (Irídia 2021) y el encuadre correcto de los 122 J |
| `historia/tipos-de-armas-tabla.md` | Retirar «85 g a 720 km/h». Corregir la atribución del umbral de 122 J |
| `casos/latam/juan-pablo-pernalete.md` | El umbral de 122 J no es de MAXAM |
| `empresas-de-armas/empresas/maxam.md` | MAXAM fabrica el cartucho lanzador, no la bola de caucho. Añadir Manufacturas del Tormes Barbero y Armas y Cartuchos del Sur. Cambiar «la UEE pasó a llamarse MAXAM en 2006» por «en 2006 el grupo adopta la marca MAXAM». Citar Irídia 2021 para los 196 bares, 60 m/s y 175 m |
| `empresas-de-armas/empresas/nobel-sport.md` | Quitar toda la genealogía de 1872. Origen real: Pont-de-Buis 1687, SNPE, filializada en 1994, hoy SofiSport. Nobel Sport España se constituye en 1993 en León y hoy es Nobel Sport Excopesa. Corregir el dominio |
| `empresas-de-armas/empresas/verney-carron.md` | Quitar el LBD40 de la lista de productos propios. Fabricó el Flash-Ball de 44 mm. Corregir el contrato de 2026 |
| `empresas-de-armas/empresas/brugger-thomet.md` | Es el fabricante del GL-06/LBD 40 y de la munición SIR y SIR-X. Ampliar |
| `empresas-de-armas/empresas/target-dynamics-international.md` | Tenía razón sobre el LBD40. Consolidar |
| `casos/espana-europa/roger-garcia-foam-2019.md` | Los 20 m son del protocolo policial, no del fabricante. Corregir el sentido de la denuncia. Corregir la fecha de Carne Cruda a 2025 y retirar la afirmación de que testimonió en ese programa |
| `casos/espana-europa/africa-pablo-hasel.md` | Fabricante B&T, no una empresa española. Los 30 m salen del informe de test TR-16973.02 citado por Irídia, no de una ficha técnica abierta. Carne Cruda es del 25 de noviembre de 2025 |
| `casos/espana-europa/abdelillah-foam-2019.md` | No consta en el programa de Carne Cruda. Verificar si la confusión con Abderrahim (Torrejón de Ardoz) afecta a más de la ficha |
| `autores-y-referencias/organizaciones/iridia.md` | Fecha de Carne Cruda a 2025 |
| `casos/espana-europa/remi-fraisse.md` | GLI-F4 → OF-F1 en frontmatter y cuerpo. Recuento de la noche: 339 disparos con su desglose. Retirar «700+», «42 OF1» y «10 GLI-F4». Añadir la condena del TEDH y la exoneración parcial del TA de Toulouse |
| `casos/espana-europa/tarajal-2014.md` | 5 botes de humo, 355 salvas. Retirar la lista de 14 nombres y sustituirla por los 12 de Caminando Fronteras con la advertencia de provisionalidad. Eliminar a Samba Martine. Rehacer el recorrido judicial entero |
| `casos/espana-europa/stop-bales-listado-historico.md` | Reescribir entera. Nueve nombres no están en el informe que se les atribuye y hay causas de muerte cambiadas |
| `casos/impacto-agregado.md` | Retirar los ~77. Corregir el periodo de los 19.071. Corregir el 335.300. Corregir la ratio de 150× a ~10×. Separar la Primera Intifada de la ventana 1988-1998. Corregir el 146 de Popayán a departamento del Cauca |
| `casos/espana-europa/compilacion-espana.md` | El «24 (1976-2019)» no es un recuento con metodología. Sustituir por las tres afirmaciones con documento |
| `casos/latam/chile-estallido-2019.md` | «+460» → «460», con corte del 13 de marzo de 2020 y desglose 425/35 |
| `casos/latam/fabiola-campillai.md` | 2.381 hospitalizados → la redacción fiel de las dos tablas del INDH |
| `marco-legal/bibliografia/amnistia-policia-bajo-la-lupa.md` | «300+» → 347 al 30 de noviembre de 2019 (Informe Anual 2019) o 352 al 6 de diciembre |
| `casos/latam/colombia-2021.md` | El 103 es de Temblores. Retirar los 150 de MOCAO. Los 11 son investigaciones disciplinarias. Los 146 son del Cauca. Tres homicidios, no uno. Corregir el nombre de MOCAO |
| `casos/latam/00-compilacion-latam.md`, `casos/espana-europa/nicola-celebracion-mundial.md` | Retirar «MOCAO, 150 mutilados en un mes» |
| `casos/internacionales/bahrein-2011.md` | El 34 es de marzo de 2012, no del informe de agosto. Corregir la fecha de Sayed Hashim Saeed y la identidad de «Isa Abdul-Hassan» |
| `casos/latam/rufo-chacon.md` | Fecha 1 de julio de 2019, cuerpo Politáchira. No fijar cifra cerrada de perdigones. Retirar «perdigones de plomo Cheddite» del frontmatter |
| `casos/estados-unidos/rodney-king-1991.md` | «63 muertos» → 63 fichas investigadas, 54 vinculadas |
| `casos/espana-europa/stephen-geddis.md` y la entrada de Irlanda del Norte | 17 muertos, 8 menores, con la lista nominal y el desglose goma/plástico |
| `historia/cronologia-completa.md` | PR-24 no es de 1958. CS es de Corson y Stoughton, 1928. Siete muertos en 1981 por balas de plástico, tres menores. Primera Intifada 1987-1993 |
| `historia/porra-tonfa.md` | Quitar la datación de 1958 |
| `marco-legal/bibliografia/ccw-1980-protocolo-iv.md` | Estados Unidos queda obligado el 21 de enero de 2009, no en 1995. Reescribir el apartado del programa PEP |
| `marco-legal/cataluna-prohibicion-balas-goma.md` | Separar los tres actos: Resolució 476/X de 18 de diciembre de 2013, plazo del 30 de abril de 2014, Instrucció 11/2014 |
| `marco-legal/mossos-instrucciones-armamento.md` | La Instrucció 11/2014 retira la goma y da entrada al LRAD. No menciona el foam ni el SIR-X |
| `marco-legal/bibliografia/centre-delas-armas-letales.md` | Los 18.805 son del 17-nov-2018 al 31-dic-2019, no una serie 2018-2020 |
| `marco-legal/bibliografia/tedh-kilici-vs-turquia.md` | Kılıcı c. Turquie, demanda 32738/11, 27 de noviembre de 2018. Matizar el §32 |
| `marco-legal/bibliografia/tedh-yasa-vs-turquia.md` | Abdullah Yaşa y otros c. Turquía, demanda 44827/08, 16 de julio de 2013 |
| `empresas-de-armas/mercado-mundial.md` | Reetiquetar la serie entera con consultora, año de publicación y definición de mercado. El 2019 es munición, no armas. El 2020 es una previsión de 2016. Retirar la atribución al SGI Global Security Index y a INCLO. 9.280 en vez de 9.380 |
| `historia/cronologia-completa.md` y `marco-legal/bibliografia/centre-delas-armas-letales.md` | «370 en 40 países» es «más de 369 fabricantes, proveedores y distribuidores» del STOA de 2000, y «200 en 60 países» es de Omega 2019 citada por el Delàs. No encadenarlas |
| `autores-y-referencias/organizaciones/omega-research-foundation.md` | Es la autora del informe STOA de 2000. Ampliar |
| Donde aparezca | «África» y «Áfrika»: la campaña usa Áfrika. «Dilan» y «Dylan» Cruz: unificar |
---

## Barrido de las 237 fichas · datos sin fuente anotada

Doce agentes leyeron las 237 fichas de `wiki/` buscando solo lo que la auditoría de agosto no
cubría: cifras, fechas, modelos de arma y referencias normativas que aparecen sin que nada en la
propia ficha permita saber de dónde salen. No se tocó estilo ni estructura, y ninguna ficha se
modificó.

**384 hallazgos en 117 de las 237 fichas.** Por gravedad, 172 alta, 183 media y 29 baja. Por tipo,
190 cifras, 98 fechas, 58 modelos de arma y 38 referencias normativas. Gravedad alta quiere decir
cifra de daño, dato técnico del arma o referencia normativa concreta, que son las que pueden acabar
en cartela.

El listado completo, ficha por ficha y con la frase donde aparece cada dato, está en
[AUDITORIA-datos-sin-fuente.md](AUDITORIA-datos-sin-fuente.md).

### Segunda ronda: las tres fichas agregadoras, cerradas

El 26 de agosto se verificaron los **41 datos** de `impacto-agregado`, `cronologia-completa` y
`tipos-de-armas-tabla`, que son las que alimentan cartelas. Los agentes los descompusieron en 62
afirmaciones: **20 refutadas, 8 no verificables, 24 parciales y 10 verificadas**. Todas están ya
aplicadas en las fichas con su fuente.

Lo que más importa de esa ronda:

**El cianuro no aguanta.** Los «0,7 mg/L documentados en chalecos amarillos» no existen como valor
sanguíneo de nadie: el dossier de la Association Toxicologie-Chimie de Paris da nueve participantes,
seis lecturas previas entre 0 y 0,25 mg/L y seis posteriores entre 0,5 y 0,75, con media de 0,65. Y
los medidos no eran chalecos amarillos, sino el biólogo firmante y su equipo, que se autoexpusieron
en Montpellier en junio de 2019. El «1 mg/L = letal» está mal por un factor de tres: la ATSDR sitúa
la muerte por encima de 3,0 mg/L y 1 mg/L es la frontera entre rubefacción y obnubilación; el NRC
concluye que 0,5 mg/L «is considered nontoxic». El dossier de origen no está revisado por pares,
cita su propia tabla a una entrevista de prensa con su primer autor, y usa un kit validado para agua
y alimentos, no para sangre.

**Waco cambia de sentido.** Dos investigaciones oficiales independientes refutan que el gas causara
el incendio. Informe Provisional Danforth: «the CS and methylene chloride did not start or contribute
to the spread of the fire» y «did not kill any Davidians». Y son 75 muertos con 25 menores de 15
años, no 76 con 20. Waco sirve por la escala del gaseo, no como caso de muerte causada por el gas.

**Las cifras de 1964-1972 estaban inventadas.** «300 ciudades, 250 muertos, 10.000 heridos graves»
no sale de ninguna fuente localizable, y desde luego no del Informe Kerner, que cubre solo hasta 1967
y habla de 128 ciudades y 83 muertos. La serie académica estándar da, para 1964-1971, 752 motines,
228 muertos y 12.741 heridos.

**Cuatro errores de causa o de fecha.** Los estudiantes de Trisakti murieron por munición real, no
por cañón de agua. Baek Nam-gi es de 2015, no de 2010. Berkeley 1969 fue el desalojo del People's
Park con gas CS desde helicóptero, no balas de plástico contra manifestantes anti-Vietnam. Y
*Edrei contra Maguire* no declaró inconstitucional el LRAD: denegó la inmunidad cualificada a los
agentes, que es otra cosa.

**Y los 5.420 GMD arrastraban el mismo error de ventana que los 19.071 LBD**: son el año natural
2018 completo, de la misma página del mismo informe de la IGPN.

### Tercera ronda: las 38 fichas de empresa

Verificados los **95 datos** de las fichas de `empresas-de-armas`, que los agentes descompusieron en
107 afirmaciones: **17 verificadas, 54 parciales, 26 refutadas y 10 no verificables**. Todas
aplicadas.

El modo de fallo dominante en estas fichas es distinto al de las de caso: **la fuente corporativa
disfrazada de dato**. Por eso los agentes llevaban una regla añadida, que la web de una empresa vale
para su catálogo y sus especificaciones y nunca para su posición en el mercado.

**Nadie puede decir quién domina este mercado.** Seis fichas afirmaban ser «una de las N empresas que
dominan el mercado» con N distinto en cada una, 8, 10 y 15. Las seis salen de la misma Tabla 2 del
Informe 56 del Centre Delàs, que lista quince empresas, diez estadounidenses. Y no mide cuota: el
propio informe explica que recoge «las empresas que más destacan en el sector» según **dos informes
comerciales de pago**. La Omega Research Foundation se lo dice al ACNUDH sin rodeos: «there are no
reliable statistics for the size of the trade in less lethal weapons and equipment, partly because no
States adequately regulate the trade, or collect meaningful data on it». La ausencia de estadística
es en sí misma un dato del documental.

**Fox-Armor no vende escudos con púas.** Se descargaron las siete páginas de su catálogo de escudos,
80 URL de producto, y los dos sitemaps del dominio, 2.367 URL: cero ocurrencias de púa, pincho, spike
o barb. Le estábamos atribuyendo un producto prohibido que no fabrica. Lo que sí vende es un
**escudo eléctrico**, que el Anexo III.2.1 del Reglamento (UE) 2019/125 somete a licencia.

**«Intrínsecamente abusivo» no es de la Relatora.** Su fórmula es «intrínsecamente cruel, inhumano o
degradante», categoría A de A/78/324, párrafos 44, 50 y 51. La etiqueta viene de comunicados de
Amnistía y de Omega.

**Arquus ya no es del grupo Volvo.** AB Volvo cerró la venta a John Cockerill Defense el 2 de julio
de 2024.

**ALS y AMTEC son la misma empresa.** «ALS Less Lethal» es el nombre comercial de AMTEC Less Lethal
Systems (Perry, Florida), comprada por PACEM Defense el 18 de octubre de 2018. Las dos fichas deben
fusionarse.

**Tres correcciones de categoría que cambian el sentido.** Los 183 M$ de Condor son exportaciones del
**municipio** de Nova Iguaçu, atribuidas a la empresa por una inferencia que Omega declara. Los
+30.000 proyectiles de Diehl no existen: lo documentado es un contrato marco de hasta 350.000 hasta
2029 con una agrupación en la que está Nammo, y un pedido en firme de 4.700. Y St. Louis compró Skunk
**después** de Ferguson, no durante: factura del 14 de noviembre de 2014.

**Y dos fechas que sostenían un relato equivocado.** Millennium lleva desde 1999 y TEC Harseim desde
1977, así que salen del patrón de «empresas oportunistas sin trayectoria» que la ficha de Azimuth
construía. Las verdaderamente anómalas son Azimuth, de dispositivos médicos auditivos, y Mir & Cruz,
de venta al por mayor no especializada.

### Cuarta ronda: los 236 datos restantes

Casos, historia, autores, marco legal, ferias y guion. Los agentes los descompusieron en **207
afirmaciones: 32 verificadas, 102 parciales, 49 refutadas y 24 no verificables**. Es la ronda con la
tasa de refutación más alta, y la que obliga a mirar de frente un problema de método.

**Le poníamos nombre y apellidos al fabricante del gas sin tener nada.** En Argentina, «CS
estadounidense (CTS, Federal Labs) y local (Fabricaciones Militares)». En Chile, «CS y CN
estadounidense e israelí». En Líbano, «estadounidense, probablemente CTS o Safariland, y balas
brasileñas de Condor». En Túnez, «CAC Systems, Alsetex, Combined Systems, Federal Labs». En Libia,
«italiano, RUAG / Ammotec», cuando RUAG es suiza. **Cinco países, ninguna fuente.** Todas retiradas.
En Líbano, además, lo documentado apunta a lo contrario: Amnistía analizó 101 vídeos y 175
instancias de uso entre 2015 y 2020 y lo que identificó fue material **francés**, granadas Alsetex
CM4 y CM6, Nobel Securité MP7 y lanzagranadas Alsetex Chouka.

**Dos signaturas de la ONU que no existen.** `A/HRC/26/36/Add.4` no está en el sistema de documentos:
el contenido sobre armas menos letales está en el cuerpo del informe principal, sección E, párrafos
101-107. Y la «Resolución 73/304 sobre derechos humanos en la era de la IA» tampoco: A/RES/73/304 es
*«Towards torture-free trade»*, de 28 de junio de 2019, que resulta ser mucho más útil para el
proyecto que la que creíamos tener. La signatura de Melzer también estaba mal asignada: A/HRC/34/54
es su primer informe de presentación del mandato, y el temático es **A/72/178**.

**La genealogía colonial de la bala de goma se queda sin sus pilares.** El «Singapur, década de 1880,
trozos de madera cortados de mangos de escoba» —que la wiki presentaba como primer antecedente
documentado del proyectil de impacto cinético— **no tiene ninguna fuente**. Tampoco «los años 60 en
Hong Kong y Malasia», ni «1971, EE. UU. contra manifestantes anti-Vietnam» con su cita
entrecomillada sin atribuir, ni «la Alemania nazi de los años treinta» como primer uso del cañón de
agua. Es el relato que sostiene la ficha `historia/balas-goma` y hay que reconstruirlo entero.

**Rodney King: el Taser que citábamos no podía existir.** «Modelo TF-76 de Taser International» es
imposible en 1991, porque **Taser International no se llamaba así hasta 1998**; el arma del LAPD la
fabricaba Tasertron. Y ningún documento del caso identifica el modelo, ni tampoco el de las porras,
así que el «PR-24» también se retira.

**Y cuatro cifras que eran de otra cosa.** Los «+30 cañones de agua» de Hong Kong eran **tres**. El
patio de Melilla eran **200 m² con unas 400 personas**, no 1.350 m² con 700-800, y el dato correcto
es peor. Las «+1.000 denuncias» de Dufresne son **993 señalamientos**, de los que 781 son heridas y
211 son trabas a la prensa. Y los «2 muertos» de su recuento son **cuatro**.

**Lo que la ronda cierra en positivo**, y no es poco. La **escopeta Franchi SPS 350** queda
verificada por fin, en los pliegos de contratación del propio Cuerpo Nacional de Policía, cerrando un
pendiente de la primera ronda. El disparo a Roger Español fue a **14,12 metros**, según el auto de la
Audiencia de 19 de marzo de 2025. La patente del bastón eléctrico para ganado tiene número y fecha:
**US 427.549, «Electric Prod-Pole», John M. Burton, Wichita, concedida el 13 de mayo de 1890**, diez
años después de lo que decíamos. Y los 151.288 cartuchos de Chile salen de una respuesta de
Carabineros por transparencia, amparo rol C742-20, publicada por CIPER.

Lo que la ronda cierra en positivo: los **58 palestinos** quedan verificados con B'Tselem
(*Death Foretold*, diciembre de 1998), y el 28/30 resulta ser el desglose de esos mismos 58, no una
suma. Las **cuatro resoluciones del Parlamento Europeo** aparecen con documento y signatura, todas
del 13 de mayo de 1982, en el DOCE C 149 de 14.6.1982. Y la **ficha de Alsetex** de la GLI-F4 y la
GM2L resuelve el gramaje y los decibelios que la primera ronda había dado por no verificables.

Reparto por carpeta: 158 en `casos`, 107 en `empresas-de-armas`, 48 en `historia`, 36 en
`autores-y-referencias`, 16 en `marco-legal`, 13 en `ferias-de-armas` y 6 en `produccion`.

Las fichas con más carga son `historia/cronologia-completa.md` (16), `casos/latam/intermediarios-latam.md`
(13), `historia/tipos-de-armas-tabla.md` (13), `casos/impacto-agregado.md` (12) y
`marco-legal/cataluna-prohibicion-balas-goma.md` (10).

Cuatro patrones explican casi todo el volumen, y conviene atacarlos por patrón y no ficha a ficha.

**Las tres fichas agregadoras concentran el riesgo.** `impacto-agregado`, `cronologia-completa` y
`tipos-de-armas-tabla` son precisamente las que alimentan cartelas, y son las que menos fuente
llevan. En `impacto-agregado`, bloques enteros de país van sin una sola atribución: Venezuela (248
muertes en protestas, 33% de los homicidios intencionales por la fuerza pública, 160 fallecidas
solo en 2017), Bolivia (37 fallecidos durante el periodo Áñez, 22 en Sacaba y Senkata, 29 de los 37
por arma de fuego), Ecuador (40.000 bombas lacrimógenas), Guatemala (388 bombas lacrimógenas en un
solo día) y Perú. En `cronologia-completa`, entradas históricas de gran calibre sin nada detrás:
379 muertos en Amritsar, 250 muertos y 10.000 heridos graves en las revueltas de 1964-1972, 76
muertos en Waco, 117 en el teatro Dubrovka, 117 heridos por cañón de agua en Stuttgart, y las
cuatro resoluciones del Parlamento Europeo de los años ochenta sin signatura.

**Las series de disparos francesas nunca se cerraron del todo.** La auditoría de agosto fijó el
pleito de los 19.071 LBD40, pero las dos cifras que van al lado, 5.420 granadas de dispersión y
1.428 GLI-F4 en los primeros seis meses del movimiento, siguen sin fuente en la ficha.

**Las fichas de empresa dan datos técnicos y de contrato sin ninguna fuente.** La de MAXAM afirma
196 bares de presión, 60 m/s y 175 metros de alcance efectivo atribuyéndolo solo a «según la propia
empresa» (esos tres datos sí están en Irídia 2021, que los toma del catálogo *Law Enforcement* de
MAXAM, y basta con citarlo). Norinco lleva un contrato de 500 millones de dólares con Venezuela en
2012 y los modelos NF01 y VN-4; Saab Bofors, una venta de artillería a India por 1.300 millones;
Raytheon, el uso del Active Denial System en Afganistán en 2010 durante un mes; Sides, la
autorización francesa de exportar cañones de agua a Hong Kong en 2018; Telefónica Ingeniería de
Seguridad, la entrada del Taser X26 en España por contrato público. Ninguna de esas fichas tiene
apartado de fuentes.

**122 de las 237 fichas no contienen ni una sola URL.** El dato es del escaneo mecánico previo al
barrido, no del barrido, y explica el volumen: no es que los datos estén mal, es que en más de la
mitad del corpus no hay forma de comprobarlos. La lista completa de esas 122 está en el companion.

---

## Pendientes estructurales

- **Actores citados sin ficha**: EXPAL (protagonista del bloque FEINDEF «Puño de Darwin»),
  Genasys/LRAD (única familia de armas sin fabricante fichado), Pacem Defense, Etienne Lacroix Group
  (dueño de Falken y de Alsetex, que es quien fabrica la GLI-F4 y quien ganó el lote de 1.280
  lanzadores LBD 40 en 2019). Se añade B&T AG (Brügger & Thomet), que la segunda pasada ha
  identificado como fabricante del GL-06/LBD 40 y de la munición SIR y SIR-X, es decir, del arma
  francesa y de la catalana a la vez. Y Rivolier, adjudicataria del contrato francés de 2026.
- **06-cierre-abba** (FEINDEF): la afirmación del cierre (ABBA emitida contra la flotilla SUMUD)
  sigue sin fuente verificada; la propia ficha lo avisa. No usar en pantalla hasta cerrarla.
- **posibles fusiones**: resource-book-onu-2017 y unodc-ohchr-manual-uso-fuerza parecen el mismo
  documento (original inglés y traducción castellana). Verificar y fusionar.
- **mexico-feminista-2020, guatemala-2020, peru-2020, brasil-2017-2021, olga-proces,
  nepal-gen-z-2024**: por debajo del estándar del resto; nepal además puede tener el año mal (el
  levantamiento Gen Z con bloqueo de redes es de septiembre de 2025).
- **transparencia-cuerpos-policiales-espana** (85%/72%/91% sin URL), **krusik-serbia** (BIRN/OCCRP/HRW
  sin URL) y **zira-silah** (125.000 pistolas sin enlace) siguen igual, y ahora están además en el
  listado del barrido con el detalle de qué dato concreto falta por sostener.
- Las **dos fichas del TEDH** ya tienen signatura: Kılıcı c. Turquie, demanda 32738/11, sentencia de
  27 de noviembre de 2018; Abdullah Yaşa y otros c. Turquía, demanda 44827/08, sentencia de 16 de
  julio de 2013. Falta renombrarlas y corregir la grafía.

---

## La capa que falta: embeddings

`semantic.py` está listo (gemini-embedding-2 con fallback, 768 dims, caché en `semantic-cache.json`
que se commitea para que Railway no necesite clave). Falta una GEMINI_API_KEY válida: la de
`~/.zshrc` es una credencial OAuth, no una API key, y todas las AIza de los `.env` locales están
revocadas. Crear una en https://aistudio.google.com/apikey y:

```
export GEMINI_API_KEY="<la clave>"   # solo en ~/.zshrc, nunca en el repo
cd ~/Desktop/CODE/projects/adg && python3 semantic.py && python3 build.py
```

Con eso aparecen la sección «≈ Relacionadas» en cada ficha y las aristas discontinuas de afinidad en
el grafo.
