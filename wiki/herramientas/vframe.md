---
tipo: herramienta
estado: borrador
nombre: VFRAME — Visual Forensics and Metadata Extraction
categoria: Investigación visual / verificación / detección de munición
disciplina: Computer vision + derechos humanos
fuentes:
  - https://vframe.io/about/
tags: [vframe, computer-vision, munición, derechos-humanos, forensic, ml]
---

# Herramienta · VFRAME

**VFRAME (Visual Forensics and Metadata Extraction)** es una plataforma de código abierto que usa **visión por computador y aprendizaje automático** para ayudar a organizaciones de derechos humanos a **detectar, catalogar y verificar munición y armas** en grandes volúmenes de material audiovisual (vídeos de conflictos, redes sociales, archivos periodísticos).

## Por qué importa para el documental
- Es **exactamente la contrapartida ciudadana** a los sistemas de vigilancia algorítmica que compran las policías. En lugar de detectar "cabezas de manifestantes" como hace el [[../ferias-de-armas/feindef/04-fn-smart-protector|FN Smart Protector]], VFRAME detecta **el arma lanzada**.
- Herramienta **open-source** → replicable, auditable, sin intereses comerciales.
- Encarna la tesis que conecta el proyecto con [[../casos/roger-espanol|Roger Español]] y la **"semilla del algoritmo"** de Irídia: usar IA para identificar abusos policiales en vez de para multiplicarlos.

## Qué hace técnicamente
- Modelos entrenados para detectar **submuniciones de racimo** (ej. ShOAB-0.5 rusa, PTAB-2.5KO, etc.) en metraje de conflicto.
- **Sintetización de datos** (synthetic data) para entrenar sin necesidad de miles de ejemplos reales — generan renders 3D de las municiones y los inyectan en escenas.
- Pipeline modular: extracción de frames → detección → clasificación → metadata → verificación humana.
- Procesamiento **on-device / local** para no enviar material sensible a nubes comerciales.

## Casos de uso documentados
- Trabajo con **Syrian Archive** y otras organizaciones que preservan vídeos de crímenes de guerra.
- Detección de municiones prohibidas para apoyar investigaciones legales.

## Cómo podría conectar con nuestra película
1. **Hilo narrativo**: "la misma tecnología" — las policías compran IA para detectar cabezas, los investigadores de DDHH la usan para detectar armas.
2. **Posible entrevista** con los responsables del proyecto (ver pendientes).
3. **Material visual**: ver si VFRAME puede procesar vídeo de manifestaciones en busca de munición "menos letal" (lacrimógenas, LBD, GLI-F4) y generar evidencia reproducible.

## Conexiones
- ↔ [[../ferias-de-armas/feindef/04-fn-smart-protector]] — el contra-ejemplo industrial.
- ↔ [[../casos/roger-espanol]] — Irídia identificó al agente a mano; VFRAME automatiza esa lógica para otras investigaciones.
- ↔ [[../marco-legal/amnistia-internacional]] — Amnistía / Omega Research son el tipo de cliente ideal de VFRAME.
- ↔ [[yolo-v3-weapon-detection]] — base técnica comparable (YOLO y familia) pero en el campo académico y con otro propósito.

## Fuentes
- https://vframe.io/about/
