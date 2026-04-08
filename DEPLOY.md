# DEPLOY — GitHub + Railway

Este sitio es estático (HTML+CSS+JS+audio M4A+md generados por `build.py`). El plan: **GitHub** como repositorio + **Railway** para servirlo.

> **¿Por qué Railway si es estático?** Porque tú lo pediste. Railway acepta perfectamente sitios estáticos sirviéndolos con un mini-servidor Python (lo que ya configuramos en `Procfile` / `railway.toml` / `nixpacks.toml`).

---

## PASO 1 · Crear el repositorio en GitHub

### 1.1 — Inicializar git en local
```bash
cd /Users/jorge/Desktop/CODE/projects/adg
git init
git add .
git status   # revisa que no incluya site/, __pycache__, ni el WAV
git commit -m "Initial commit — wiki Artefactos de Guerra (169 notas)"
```

### 1.2 — Crear el repo en GitHub
1. Ve a https://github.com/new
2. **Repository name**: `adg` (o `artefactos-de-guerra`)
3. **Visibility**: privado (recomendado mientras esté en desarrollo) o público
4. **NO** marques "Add README" ni `.gitignore` ni licencia (ya los tenemos)
5. **Create repository**

### 1.3 — Subir el código
GitHub te dará dos comandos. Usa la versión con SSH si tienes claves configuradas, o HTTPS:

```bash
# Opción A — SSH (si tienes claves)
git remote add origin git@github.com:TU_USUARIO/adg.git
git branch -M main
git push -u origin main

# Opción B — HTTPS
git remote add origin https://github.com/TU_USUARIO/adg.git
git branch -M main
git push -u origin main
```

A partir de aquí, cada cambio que quieras subir:
```bash
git add .
git commit -m "Descripción del cambio"
git push
```

---

## PASO 2 · Conectar Railway

### 2.1 — Crear cuenta y proyecto
1. Ve a https://railway.app
2. **Login with GitHub** (lo más rápido — autoriza Railway a leer tus repos).
3. **New Project** → **Deploy from GitHub repo** → elige `adg`.

### 2.2 — Railway lo detecta automáticamente
Railway leerá los archivos de configuración que ya están en el repo:
- **`railway.toml`** — configuración principal de Railway
- **`nixpacks.toml`** — fuerza Python 3.11 + pip install
- **`Procfile`** — comando de arranque
- **`requirements.txt`** — dependencias Python

Railway hará automáticamente:
1. Clonar el repo de GitHub.
2. Instalar Python 3.11 + `markdown` + `pyyaml`.
3. Ejecutar `python build.py` (genera `site/`).
4. Arrancar `python -m http.server $PORT` desde `site/`.
5. Asignar una URL pública del estilo `adg-production.up.railway.app`.

### 2.3 — Asignar dominio público
1. En tu proyecto Railway → **Settings** → **Networking** → **Generate Domain**.
2. Te dará `adg-production-xxxx.up.railway.app`. Esa es tu URL pública.
3. (Opcional) **Custom Domain** si quieres `artefactos-de-guerra.com`.

### 2.4 — Cada `git push` re-despliega
Railway está conectado a la rama `main` de tu repo. Cada vez que hagas `git push origin main`, Railway:
1. Detecta el push.
2. Re-compila el sitio (`python build.py`).
3. Reinicia el servidor.
4. La URL queda actualizada en ~1 minuto.

---

## PASO 3 · Verificar que YouTube funciona

Una vez desplegado:
1. Abre la URL de Railway en el navegador.
2. Ve a una nota con vídeo de YouTube — por ejemplo:
   - `usos-de-armas/entrenamientos/marines-camp-pendleton.html`
   - `usos-de-armas/entrenamientos/lexipol-gordon-graham.html`
   - `empresas-de-armas/renders/discombulator-trump.html`
   - `empresas-de-armas/renders/flash-bang-m84-tecnico.html`
3. Los vídeos **deberían reproducirse normalmente**. El Error 153 que veías era exclusivo de `file://` (ahora estás en `https://`).

> El sitio usa `youtube-nocookie.com` (más permisivo) + `referrerpolicy="strict-origin-when-cross-origin"` para que YouTube acepte los embeds desde dominios públicos sin problemas.

---

## Coste estimado en Railway

- **Plan Hobby**: $5/mes incluye **$5 de uso** (suficiente para este sitio).
- Un sitio estático con tráfico bajo consume **<$1/mes** en Railway.
- Si superas los $5, el sobrante se factura a $0.000463/GB-segundo (memoria) + ancho de banda.
- **Estimación realista** para este proyecto: **$3-5/mes**.

Si te parece caro o quieres gratis: **Cloudflare Pages**, **Netlify** o **GitHub Pages** son **gratis** y funcionan idénticamente. La configuración para esos servicios también está incluida en este repo (`.github/workflows/deploy.yml` para GitHub Pages).

---

## Resumen de archivos de despliegue en este repo

| Archivo | Para qué |
|---|---|
| `.gitignore` | Excluye `site/`, `__pycache__`, audio crudo |
| `requirements.txt` | Dependencias Python (markdown, pyyaml) |
| `railway.toml` | Configuración Railway |
| `nixpacks.toml` | Build environment para Railway/Cloudflare |
| `Procfile` | Comando de arranque (web server) |
| `.github/workflows/deploy.yml` | GitHub Actions → GitHub Pages (alternativa) |
| `build.py` | Generador del sitio (170 notas) |
| `wiki/` | Las notas en markdown |
| `media/audio/Paul_Rocher_220522.m4a` | Audio entrevista (41 MB) |

---

## Comandos rápidos de referencia

```bash
# Build local
python3 build.py

# Build + servidor local (los YouTube funcionan aquí)
python3 build.py --serve
# → http://localhost:8765

# Subir cambios
git add . && git commit -m "Mensaje" && git push

# Ver estado
git status
git log --oneline -10
```
