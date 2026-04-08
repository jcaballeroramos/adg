---
tipo: paper
estado: borrador
titulo: "Weapon Detection Using YOLO V3 for Smart Surveillance System"
autores:
  - Sanam Narejo (MUET, Pakistán)
  - Bishwajeet Pandey (Gran Sasso Science Institute, Italia)
  - Doris Esenarro Vargas (Universidad Nacional Federico Villarreal, Perú)
  - Ciro Rodriguez (Universidad Nacional Mayor de San Marcos, Perú)
  - M. Rizwan Anjum (Islamia University of Bahawalpur, Pakistán)
revista: "Mathematical Problems in Engineering"
volumen: 2021
articulo: 9975700
paginas: 9
publicado: 2021-05-12
doi: 10.1155/2021/9975700
licencia: Creative Commons Attribution
correspondencia: dr.pandey@ieee.org
tags: [paper, yolo, yolo-v3, weapon-detection, surveillance, deep-learning, cnn, darknet]
---

# Paper · Weapon Detection Using YOLO V3 for Smart Surveillance System

Paper académico (2021) que propone un sistema de **vigilancia automatizada** basado en **YOLO V3** para detectar armas (pistolas, rifles) y fuego en tiempo real desde cámaras CCTV, con el objetivo declarado de apoyar a las fuerzas del orden.

> ⚠️ **Importante para nuestra posición editorial:** este paper representa la **otra cara** de VFRAME. Mismo tipo de tecnología (detección de objetos con redes neuronales convolucionales), **propósito opuesto**: en vez de documentar abusos, alimenta el aparato de vigilancia que los produce. Lo archivamos por eso, como contrapunto.

## Cita
Narejo, S., Pandey, B., Esenarro Vargas, D., Rodriguez, C., & Anjum, M. R. (2021). *Weapon Detection Using YOLO V3 for Smart Surveillance System*. Mathematical Problems in Engineering, 2021, Article ID 9975700, 9 pages. https://doi.org/10.1155/2021/9975700

## Resumen (propio)
Los autores entrenan un modelo **YOLO V3** ("You Only Look Once") sobre un dataset propio recopilado manualmente de Google Images (≥50 imágenes por clase de arma) para detectar **pistolas y rifles**. Usan **transfer learning** sobre pesos preentrenados de COCO + ImageNet, evitando así la necesidad de GPUs potentes. Comparan con YOLO V2 y una CNN tradicional: YOLO V3 gana con **98,89% de precisión**, frente a 96,76% (YOLO V2) y 95% (CNN). El sistema incluye una base de datos con geolocalización (latitud, longitud, hora, lugar) y una interfaz Java Swing.

## Arquitectura resumida
- **Backbone**: Darknet-53 (53 capas convolucionales).
- **Detección multiescala**: 3 mapas de características a distintos niveles.
- **Capas totales**: 106 (53 + 53 añadidas para detección).
- **Función de pérdida**: `Loss = Lbox + Lcls + Lobj` (caja + clase + objeto).
- **Imágenes** redimensionadas a 416×416 antes del entrenamiento.
- **Framework**: Darknet.

## Resultados
| Modelo | Precisión |
|---|---|
| CNN tradicional (desde cero) | 95,00% |
| YOLO V2 | 96,76% |
| **YOLO V3** | **98,89%** |

## Propósito declarado
Los autores argumentan que:
- La "violencia con armas" genera trauma psicológico.
- La vigilancia humana tradicional **no basta** por cansancio y falta de atención.
- **4,2 por cada 100.000 personas mueren cada año en Pakistán** por tiroteos.
- Un sistema automatizado puede "salvar vidas humanas" y reducir delitos.
- Se plantea integrarlo en **robots de vigilancia y seguridad**.

## Lectura crítica (para el proyecto)

### 1. El marco es el marco
El paper asume sin discusión que **"más detección automática = más seguridad"**. No discute falsos positivos, sesgos del dataset (imágenes recogidas manualmente de Google, sin auditoría demográfica), cadena de custodia de la alerta, ni consecuencias políticas del despliegue.

### 2. Dataset opaco
> "We manually collected huge amount of images from Google. For each weapon class, we collected at least 50 images."

**50 imágenes por clase** es un dataset ínfimo para decir que el modelo "funciona en el mundo real". El 98,89% de precisión es sobre su propio split de validación, **no sobre metraje real de CCTV** en condiciones adversas (baja luz, oclusión, ángulos extremos).

### 3. Responsabilidad diluida
El sistema propone **alertar al operador humano**. Pero la alerta se basa en una bounding box generada por un modelo que no explica sus decisiones. Si la alerta llega a un agente armado sesgado → ver Rodney King y la cascada que describió [[../autores-y-referencias/paul-rocher/paul-rocher|Rocher]].

### 4. "Salvar vidas" vs. arquitectura de vigilancia
El paper naturaliza la **expansión del aparato de vigilancia** como "solución técnica a un problema social". Es **exactamente la tesis 3 de Paul Rocher** ([[../autores-y-referencias/paul-rocher/paul-rocher-entrevista|entrevista + ideas clave]]):
> Los gobiernos piensan que han encontrado una solución tecnológica milagrosa… porque no quieren hablar del problema social que hay detrás.

### 5. Robots
La conclusión del paper sugiere integrar el modelo en **robots de vigilancia**. La autonomía de los sistemas de fuego contra humanos está explícitamente prohibida en muchos marcos (incluidas las propias [[../marco-legal/onu-orientaciones-2020|Orientaciones ONU 2020]] cuando se combina con armas letales). Aquí la detección es "pasiva" pero la infraestructura que habilita es la misma.

## Conexiones
- ↔ [[vframe]] — mismo tipo de tecnología, propósito inverso (uso ciudadano vs. estatal).
- ↔ [[../ferias-de-armas/feindef/04-fn-smart-protector]] — el equivalente comercial industrial, ya en el mercado.
- ↔ [[../autores-y-referencias/paul-rocher/paul-rocher-entrevista]] — marco crítico sobre "soluciones técnicas a problemas sociales".
- ↔ [[../casos/roger-espanol]] — Irídia tuvo que hacer manualmente lo que sistemas como estos automatizan, **pero para el propósito opuesto**.

## Fuentes
- Publicado bajo Creative Commons Attribution: https://doi.org/10.1155/2021/9975700

## Pendientes
- [ ] Descargar el PDF a `raw/papers/` y añadir DOI enlazable.
- [ ] Buscar implementaciones alternativas con YOLO V5/V8/V10 (la familia YOLO ha avanzado mucho desde 2021).
- [ ] Cruzar con papers similares que traten específicamente **armas "menos letales"** (LBD, lacrimógenas, etc.) — no encontrado hasta ahora, puede ser gap de investigación interesante.
- [ ] Ver si VFRAME ha publicado comparativas con papers académicos de este tipo.
