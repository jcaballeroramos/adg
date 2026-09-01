---
tipo: empresa
estado: borrador
nombre: IDEMIA
pais: Francia
sede: Courbevoie (Île-de-France)
fundacion: 2017
antecesores: ["Morpho / Safran Identity & Security", "Oberthur Technologies"]
matriz: Advent International (private equity)
producto_emblematico: Reconocimiento facial y de iris (MFACE, OneLook, BORDERGUARD)
fuentes:
  - https://www.idemia.com/
  - https://en.wikipedia.org/wiki/IDEMIA
  - https://www.biometricupdate.com/202207/ngos-sue-idemia-for-failing-to-consider-human-rights-risks-in-kenyan-digital-id
  - https://www.business-humanrights.org/en/latest-news/response-from-idemia-to-allegations-about-sale-of-surveillance-technology-in-latin-america/
tags: [idemia, morpho, francia, biometria, reconocimiento-facial, iris, huella, identidad, control-fronteras, vigilancia, ees, eurosatory, aadhaar, kenia, egipto, china]
---

# IDEMIA

Multinacional **francesa** de **biometría, identidad y seguridad**, con sede en **Courbevoie** (extrarradio de París) y propiedad del fondo de capital riesgo **Advent International**. Nació en **2017** de la fusión de **Morpho** (la antigua división de identidad de **Safran**) y **Oberthur Technologies**. Es uno de los mayores proveedores mundiales de **reconocimiento facial, de iris y de huella dactilar**, de **documentos de identidad** (DNI, pasaportes biométricos, permisos de conducir) y de **sistemas de control de fronteras**. Según la propia empresa, presta servicio a **más de 600 organismos gubernamentales** y **2.400 empresas en 180 países**, con unos **2.900 M€ de facturación (2023)** y ~**15.000 empleados**.

En el vocabulario de esta wiki, IDEMIA representa **la otra cara del continuo de control**: no la munición ni el lanzador, sino la **infraestructura de identificación** que decide, en la frontera o en la puerta de un evento, **quién pasa y quién queda bloqueado**. La misma lógica de "separar y clasificar" del [[combined-systems|VENOM]] —"determinar la intención", "separar combatientes de no combatientes"—, pero ejecutada por algoritmo sobre el rostro de cada persona.

## Datos

- 🌐 https://www.idemia.com/
- País: **Francia** · sede en **Courbevoie**
- Constituida en **2017** (fusión Morpho/Safran + Oberthur); rebautizada IDEMIA el 28-sep-2017.
- Propiedad de **Advent International** (private equity).
- Facturación **~2.900 M€ (2023)** · **~15.000** empleados.
- Afirma haber producido **3.000 millones de documentos de identidad** en el mundo (dato 2020).
- CEO de **IDEMIA Public Security** (la división de seguridad pública / fronteras): **Matthew Cole** (desde enero de 2024).

## Qué hace

### Biometría e identidad
- **Reconocimiento facial, de iris y de huella dactilar**; sistemas automáticos de identificación por huella (**AFIS**), venas del dedo.
- Fabricación de **documentos de identidad**: DNI electrónicos, **pasaportes biométricos**, permisos de conducir.
- Productos emblemáticos: **MFACE** (identificación facial de un flujo continuo de personas en movimiento), **OneLook** (captura simultánea de rostro e iris "en menos de dos segundos"), **MorphoWave** (terminales de huella sin contacto).

### Control de fronteras
- Suite **BORDERGUARD** y gama **Augmented Borders**: verificación de identidad "sin fricción" en aeropuertos y pasos fronterizos.
- Proveedor del **Sistema de Entradas y Salidas (EES)** de la **Unión Europea** —el registro biométrico de todos los viajeros de terceros países que cruzan el espacio Schengen— junto a **Sopra Steria** (sistema de matching biométrico declarado listo en 2025).
- Despliegues en el aeropuerto de **Changi (Singapur)**, entre otros.

### Vigilancia y seguridad pública ("public security")
- Sistemas forenses y de identificación para **policías y ministerios del interior** (bases de datos biométricas, cotejo de rostros a partir de foto o vídeo).
- En EE.UU. opera **IdentoGO** (cientos de puntos de captura de huellas), gestiona **TSA PreCheck** y provee tecnología de carnés de conducir a numerosos estados.

### Pagos y SIM
- Tarjetas de pago (incluidas **tarjetas biométricas** con huella en lugar de PIN) y tarjetas SIM — herencia del negocio de Oberthur.

## Clientes estatales (selección)

- **Unión Europea** — sistema **EES** de control de fronteras Schengen (con Sopra Steria).
- **India** — proyecto **Aadhaar**: enrolamiento biométrico (iris, huellas, rostro) de más de **1.300 millones** de personas.
- **Estados Unidos** — **TSA**, **FBI**, gobiernos federal y estatales; carnés de conducir y captura de huellas.
- **Francia** — programas nacionales de identidad.
- **Singapur, Emiratos Árabes Unidos, Albania** — despliegues biométricos y de reconocimiento facial.
- **Kenia** — kits de captura biométrica para el registro nacional **Huduma Namba / NIIMS** (2018-19) → ver controversias.
- **Sesgo del sistema**: los tests del **NIST** (*Face Recognition Vendor Test*) documentan tasas de falso positivo notablemente más altas para rostros de mujeres negras que para los de mujeres blancas.
  > ✅ **Cerrado el 1 de septiembre de 2026 con el informe del NIST.** *Face Recognition Vendor Test (FRVT) Part 3: Demographic Effects*, **NISTIR 8280**, diciembre de 2019.
  >
  > **Lo que se puede decir**: el NIST encontró **tasas de falso positivo más altas para mujeres afroamericanas que para ningún otro grupo** en la búsqueda uno-contra-muchos, y avisa de por qué eso importa más que el resto: *«Differentials in false positives in one-to-many matching are particularly important because the consequences could include false accusations»*. **Falsas acusaciones.**
  >
  > **Sobre la magnitud**: en verificación uno-a-uno, las diferencias entre personas blancas y negras van **de diez a cien veces** según el algoritmo. Con un umbral en el que un hombre blanco da falso positivo una vez de cada mil, **de 167 algoritmos todos menos dos tenían más del doble de probabilidad de identificar mal a una mujer negra, y algunos llegaban a cuarenta veces**.
  >
  > **Redacción segura**: dar el rango con su fuente, «de diez a cien veces según el algoritmo, NISTIR 8280», nunca un multiplicador único. El «~10 veces» era el extremo bajo del rango presentado como si fuera la cifra.
- **Compra por Amadeus**: la adquisición de **IDEMIA Public Security** por Amadeus se anunció por unos **1.200 M€** (abril de 2026). ⚠️ Cifra pendiente de confirmar en el hecho relevante.

## Contexto — Eurosatory 2026

El director de IDEMIA presente en **[[../../ferias-de-armas/eurosatory-2026/00-overview|Eurosatory 2026]]** presentó la oferta de la empresa en clave de **control de fronteras y biometría para eventos**, con el argumento de **"facilitar el paso a quienes cumplen las normas y bloquear a quienes no"**, y describió su tecnología como **"la mejor protección para el policía"** *(cita textual pendiente de verificar contra el material de prensa de la feria)*.

Ese encuadre es exactamente el que interesa al documental: la vigilancia biométrica **vendida como servicio de orden público** en el mismo recinto donde se exhiben carros de combate y equipo antidisturbios. El eufemismo "facilitar / bloquear" traslada al rostro la misma operación de **clasificación de multitudes** que el resto de esta wiki documenta en forma de gas, bala de goma o cañón de agua. La "protección del policía" convierte una **base de datos** en un arma defensiva más del arsenal de seguridad interior.

## Controversias (derechos humanos y vigilancia)

- **Kenia — demanda por el registro digital (2022).** Las ONG **Data Rights**, **Nubian Rights Forum** y la **Kenya Human Rights Commission** demandaron a IDEMIA ante un tribunal de París **al amparo de la Ley francesa de Deber de Vigilancia** (*Loi sur le devoir de vigilance*, 2017), por suministrar los kits biométricos del **Huduma Namba / NIIMS** sin evaluar el riesgo de **exclusión de comunidades marginadas** (nubios, apátridas) y de **vigilancia** sobre una base de datos centralizada sin garantías. IDEMIA alegó que la ley cubre los riesgos de *su* actividad, no del *uso* que el cliente hace de sus productos.
- **Egipto (2018).** ONG internacionales, francesas y egipcias acusaron a IDEMIA de **lucrarse con la represión** del régimen y de proveer tecnología de vigilancia a un gobierno autoritario.
- **China (2015).** Según el informe *Out of Control* de **Amnistía Internacional** (2020), **Morpho** (hoy IDEMIA) suministró **equipos de reconocimiento facial** directamente a la **Oficina de Seguridad Pública de Shanghái**.
- **América Latina — Argentina, Brasil, Ecuador.** Un informe de **Access Now** documentó la venta de sistemas **Morpho RapID**, **Morpho Face Detective** y **Morpho Face Investigate** (reconocimiento facial de multitudes y a partir de foto/vídeo), incluido su presunto uso en el **subte de Buenos Aires**. IDEMIA negó tener "tecnología de vigilancia" en esos países y sostuvo que se trataba de identificación biométrica "forense".
- **Sesgo algorítmico.** Estudios independientes hallaron **sesgo racial y de género** en sus algoritmos: con el mismo umbral, el sistema confundía rostros de **mujeres negras ~10 veces más** que los de mujeres blancas. *(IDEMIA replica que el NIST situó su algoritmo entre los mejores del mundo en precisión.)*
- **Refugiados y migrantes (2022).** IDEMIA —junto a **Thales**— fue señalada por facilitar abusos mediante el suministro de **soluciones de vigilancia fronteriza**.
- **Corrupción (Nigeria).** Safran/Sagem, antecesora del negocio, fue **multada con 500.000 €** por un tribunal francés por **sobornar a funcionarios nigerianos** para lograr un contrato de DNI (~170 M€, hechos de 2000-2003).
- **Nepal.** Acusaciones (negadas por la empresa) de favoritismo y de provocar el colapso del sistema de pasaportes.

## Nota sobre la propiedad (2026)

En abril de 2026, el grupo de tecnología de viajes **Amadeus** anunció la compra de **IDEMIA Public Security** —la división de seguridad pública, biometría y fronteras— por unos **1.200 M€**. *(Operación anunciada; cierre y perímetro finales pendientes de verificar.)*

## Conexiones

- ↔ [[00-indice]]
- ↔ [[indra]] — la "Indra española": vigilancia por vídeo y deep learning, otra beneficiaria de los proyectos europeos de control de fronteras.
- ↔ [[telefonica-ingenieria-seguridad]] — brazo español de vigilancia/comunicaciones para cuerpos policiales.
- ↔ [[elbit-systems]] — el otro gran modelo de "seguridad fronteriza" tecnológica (sensores y vigilancia en Cisjordania/Gaza y fronteras exportadas).
- ↔ [[combined-systems]] — la misma lógica de **"separar y clasificar"** multitudes, aquí por algoritmo sobre el rostro en vez de por munición.
- ↔ [[../../ferias-de-armas/eurosatory-2026/00-overview]] — la feria donde IDEMIA presentó su discurso de fronteras y "protección del policía".
- ↔ [[../../herramientas/vframe]] — la contrapartida ciudadana: visión por computador **al servicio** de los derechos humanos, no de la vigilancia.
- ↔ [[../../autores-y-referencias/organizaciones/forensic-architecture]] — investigación forense contra la vigilancia estatal.
- ↔ [[../../casos/estados-unidos/ee-uu-frontera-sur]] — el debate sobre tecnología de control de fronteras.
- ↔ [[../../casos/espana-europa/melilla-2022]] · [[../../casos/espana-europa/tarajal-2014]] — la frontera sur europea como laboratorio de este mercado.
- NIST, *Face Recognition Vendor Test (FRVT) Part 3: Demographic Effects*, NISTIR 8280, diciembre de 2019: <https://nvlpubs.nist.gov/nistpubs/ir/2019/NIST.IR.8280.pdf>
