/* Admin SPA — Artefactos de Guerra */

// ── Theme ──
function getTheme() {
  return localStorage.getItem('adg-admin-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
}
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = t === 'dark' ? '\u263E' : '\u2600';
}
function toggleTheme() {
  const t = getTheme() === 'dark' ? 'light' : 'dark';
  localStorage.setItem('adg-admin-theme', t);
  applyTheme(t);
}
applyTheme(getTheme());

let currentUser = null;
let allNotes = [];
let schemas = null;
let editor = null;
let currentFilter = null;

// ── API helpers ──
async function api(path, opts = {}) {
  const headers = { ...opts.headers };
  if (opts.body && typeof opts.body === 'string') headers['Content-Type'] = 'application/json';
  const res = await fetch(path, {
    credentials: 'same-origin',
    ...opts,
    headers,
  });
  if (res.status === 401) { showLogin(); throw new Error('No auth'); }
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Error');
  return data;
}

function toast(msg, isError = false) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (isError ? ' error' : '');
  setTimeout(() => el.className = 'toast', 3000);
}

// ── Auth ──
async function checkAuth() {
  try {
    const data = await api('/api/auth/me');
    currentUser = data.username;
    showApp();
  } catch { showLogin(); }
}

function showLogin() {
  document.getElementById('login-screen').style.display = '';
  document.getElementById('app-screen').style.display = 'none';
}

function showApp() {
  document.getElementById('login-screen').style.display = 'none';
  document.getElementById('app-screen').style.display = '';
  document.getElementById('topbar-user').textContent = currentUser;
  applyTheme(getTheme());
  loadNotes();
  loadSchemas();
}

async function doLogin() {
  const u = document.getElementById('login-user').value.trim();
  const p = document.getElementById('login-pass').value;
  try {
    await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ username: u, password: p }) });
    currentUser = u;
    showApp();
  } catch (e) {
    document.getElementById('login-error').textContent = 'Credenciales incorrectas';
  }
}

async function doLogout() {
  await api('/api/auth/logout', { method: 'POST' });
  currentUser = null;
  showLogin();
}

// Enter key on login
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.getElementById('login-screen').style.display !== 'none') doLogin();
});

// ── Data ──
async function loadNotes() {
  allNotes = await api('/api/notes/');
  renderSidebar();
  renderNotesList();
}

async function loadSchemas() {
  schemas = await api('/api/schemas/');
}

// ── Sidebar ──
function renderSidebar() {
  const cats = {};
  allNotes.forEach(n => {
    const c = n.category || '_root';
    if (!cats[c]) cats[c] = 0;
    cats[c]++;
  });

  const order = ['_root','historia','autores-y-referencias','ferias-de-armas','empresas-de-armas','usos-de-armas','casos','marco-legal','herramientas'];
  const labels = {
    '_root':'General','historia':'Historia','autores-y-referencias':'Autores y referencias',
    'ferias-de-armas':'Ferias de armas','empresas-de-armas':'Empresas de armas',
    'usos-de-armas':'Usos de armas','casos':'Casos','marco-legal':'Marco legal',
    'herramientas':'Herramientas',
  };

  let html = '<h3>Navegacion</h3>';
  html += `<a class="nav-item ${!currentFilter ? 'active' : ''}" onclick="filterCat(null)">Todas las notas <span class="nav-count">${allNotes.length}</span></a>`;
  order.forEach(c => {
    if (!cats[c]) return;
    const active = currentFilter === c ? 'active' : '';
    html += `<a class="nav-item ${active}" onclick="filterCat('${c}')">${labels[c] || c} <span class="nav-count">${cats[c]}</span></a>`;
  });

  html += '<h3 style="margin-top:24px">Acciones</h3>';
  html += '<a class="nav-item" onclick="showCreateForm()">+ Nueva nota</a>';
  html += '<a class="nav-item" onclick="showMediaBrowser()">Media</a>';

  document.getElementById('sidebar').innerHTML = html;
}

function filterCat(cat) {
  currentFilter = cat;
  renderSidebar();
  renderNotesList();
}

// ── Notes list ──
function renderNotesList(search = '') {
  let notes = allNotes;
  if (currentFilter) notes = notes.filter(n => n.category === currentFilter);
  if (search) {
    const q = search.toLowerCase();
    notes = notes.filter(n => n.title.toLowerCase().includes(q) || n.slug.toLowerCase().includes(q) || (n.tags || []).some(t => t.toLowerCase().includes(q)));
  }

  let html = '<div class="search-bar">';
  html += `<input type="text" placeholder="Buscar notas..." oninput="renderNotesList(this.value)" value="${esc(search)}">`;
  html += `<button class="btn btn-accent" onclick="showCreateForm()">+ Nueva nota</button>`;
  html += '</div>';

  html += '<table class="notes-table"><thead><tr>';
  html += '<th>Titulo</th><th>Categoria</th><th>Tipo</th><th>Tags</th>';
  html += '</tr></thead><tbody>';

  notes.forEach(n => {
    const catLabel = n.subcategory ? `${n.category}/${n.subcategory}` : n.category;
    const tags = (n.tags || []).slice(0, 3).map(t => `<span class="chip">${esc(t)}</span>`).join(' ');
    html += `<tr>`;
    html += `<td class="note-title" onclick="openEditor('${esc(n.slug)}')">${esc(n.title)}</td>`;
    html += `<td><span class="chip">${esc(catLabel)}</span></td>`;
    html += `<td>${n.tipo ? `<span class="chip">${esc(n.tipo)}</span>` : ''}</td>`;
    html += `<td>${tags}</td>`;
    html += `</tr>`;
  });

  html += '</tbody></table>';
  document.getElementById('main').innerHTML = html;
}

// ── Editor ──
function destroyEditor() {
  if (editor) {
    try { editor.toTextArea(); } catch(e) {}
    editor = null;
  }
  // Clean up any orphaned EasyMDE instances
  document.querySelectorAll('.EasyMDEContainer').forEach(el => el.remove());
}

async function openEditor(slug) {
  const note = await api(`/api/notes/${slug}`);
  destroyEditor();

  let html = '<div class="editor-header">';
  html += `<h2>${esc(note.title)}</h2>`;
  html += '<div class="editor-actions">';
  html += `<button class="btn" onclick="destroyEditor();renderNotesList()">Volver</button>`;
  html += `<button class="btn btn-danger" onclick="deleteNote('${esc(slug)}')">Borrar</button>`;
  html += `<button class="btn" onclick="showMoveModal('${esc(slug)}')">Mover</button>`;
  html += `<button class="btn btn-accent" onclick="saveNote('${esc(slug)}')">Guardar</button>`;
  html += '</div></div>';

  // Frontmatter form
  html += '<div class="fm-grid" id="fm-grid">';
  html += renderFmFields(note.frontmatter);
  html += '</div>';

  // Markdown editor
  html += '<textarea id="md-editor"></textarea>';

  // Bottom save
  html += '<div style="margin-top:16px;display:flex;gap:8px;justify-content:flex-end">';
  html += `<button class="btn btn-accent" onclick="saveNote('${esc(slug)}')">Guardar cambios</button>`;
  html += '</div>';

  document.getElementById('main').innerHTML = html;
  document.getElementById('md-editor').value = note.body;

  editor = new EasyMDE({
    element: document.getElementById('md-editor'),
    spellChecker: false,
    autofocus: false,
    status: ['lines', 'words'],
    toolbar: ['bold','italic','heading','|','quote','unordered-list','ordered-list','|','link','image','table','|','preview','side-by-side','|','guide'],
    minHeight: '400px',
  });
}

function renderFmFields(fm) {
  const tipo = fm.tipo || '';
  let html = '';

  // Common: tipo
  html += '<div class="fm-field">';
  html += '<label>Tipo</label>';
  html += '<select data-fm="tipo" onchange="onTipoChange(this.value)">';
  html += '<option value="">--</option>';
  const tipos = schemas?.common?.find(f => f.name === 'tipo')?.options || [];
  tipos.forEach(t => {
    html += `<option value="${esc(t)}" ${t === tipo ? 'selected' : ''}>${esc(t)}</option>`;
  });
  html += '</select></div>';

  // Common: estado
  html += '<div class="fm-field">';
  html += '<label>Estado</label>';
  html += '<select data-fm="estado">';
  html += '<option value="">--</option>';
  ['stub','borrador','completo'].forEach(s => {
    html += `<option value="${s}" ${s === (fm.estado||'') ? 'selected' : ''}>${s}</option>`;
  });
  html += '</select></div>';

  // Common: tags
  html += '<div class="fm-field full">';
  html += '<label>Tags (separados por coma)</label>';
  html += `<input data-fm="tags" type="text" value="${esc((fm.tags || []).join(', '))}">`;
  html += '</div>';

  // Type-specific fields
  const typeFields = schemas?.types?.[tipo] || [];
  typeFields.forEach(f => {
    const val = fm[f.name] || '';
    const cls = f.type === 'textarea' || f.type === 'url-list' ? 'fm-field full' : 'fm-field';
    html += `<div class="${cls}">`;
    html += `<label>${esc(f.name)}</label>`;
    if (f.type === 'textarea') {
      html += `<textarea data-fm="${esc(f.name)}">${esc(typeof val === 'string' ? val : JSON.stringify(val))}</textarea>`;
    } else if (f.type === 'url-list' || f.type === 'tags') {
      const arr = Array.isArray(val) ? val.join('\n') : val;
      html += `<textarea data-fm="${esc(f.name)}" rows="3">${esc(arr)}</textarea>`;
    } else {
      html += `<input data-fm="${esc(f.name)}" type="text" value="${esc(typeof val === 'string' ? val : String(val))}">`;
    }
    html += '</div>';
  });

  // Extra fields not in schema
  const knownFields = new Set(['tipo','estado','tags', ...typeFields.map(f => f.name)]);
  Object.entries(fm).forEach(([k, v]) => {
    if (knownFields.has(k)) return;
    html += '<div class="fm-field">';
    html += `<label>${esc(k)}</label>`;
    const sv = typeof v === 'string' ? v : Array.isArray(v) ? v.join(', ') : JSON.stringify(v);
    html += `<input data-fm="${esc(k)}" type="text" value="${esc(sv)}">`;
    html += '</div>';
  });

  return html;
}

function onTipoChange(newTipo) {
  // Re-render frontmatter fields preserving current values
  const fm = collectFrontmatter();
  fm.tipo = newTipo;
  document.getElementById('fm-grid').innerHTML = renderFmFields(fm);
}

function collectFrontmatter() {
  const fm = {};
  document.querySelectorAll('[data-fm]').forEach(el => {
    const key = el.dataset.fm;
    let val = el.value.trim();
    if (key === 'tags') {
      fm[key] = val ? val.split(',').map(t => t.trim()).filter(Boolean) : [];
    } else if (el.tagName === 'TEXTAREA' && (key === 'fuentes' || schemas?.types?.[fm.tipo]?.find(f => f.name === key && f.type === 'url-list'))) {
      fm[key] = val ? val.split('\n').map(l => l.trim()).filter(Boolean) : [];
    } else if (val) {
      // Try to preserve number types
      if (/^\d+$/.test(val)) fm[key] = parseInt(val, 10);
      else fm[key] = val;
    }
  });
  return fm;
}

async function saveNote(slug) {
  const fm = collectFrontmatter();
  const body = editor ? editor.value() : document.getElementById('md-editor').value;
  try {
    await api(`/api/notes/${slug}`, { method: 'PUT', body: JSON.stringify({ frontmatter: fm, body }) });
    toast('Nota guardada');
    await api('/api/build/', { method: 'POST' });
    toast('Sitio reconstruido');
    loadNotes();
  } catch (e) { toast('Error: ' + e.message, true); }
}

async function deleteNote(slug) {
  if (!confirm(`Borrar "${slug}"? Esta accion se puede deshacer con git.`)) return;
  try {
    await api(`/api/notes/${slug}`, { method: 'DELETE' });
    toast('Nota borrada');
    await api('/api/build/', { method: 'POST' });
    loadNotes();
    renderNotesList();
  } catch (e) { toast('Error: ' + e.message, true); }
}

function showMoveModal(slug) {
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.innerHTML = `
    <div class="modal">
      <h3>Mover nota</h3>
      <p style="color:var(--fg-dim);font-size:13px;margin-bottom:12px">Slug actual: ${esc(slug)}</p>
      <input id="move-slug" type="text" value="${esc(slug)}" style="width:100%;padding:8px 10px;background:var(--bg);border:1px solid var(--border);border-radius:6px;color:var(--fg);font-size:13px">
      <div class="modal-actions">
        <button class="btn" onclick="this.closest('.modal-overlay').remove()">Cancelar</button>
        <button class="btn btn-accent" onclick="doMove('${esc(slug)}')">Mover</button>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}

async function doMove(oldSlug) {
  const newSlug = document.getElementById('move-slug').value.trim();
  if (!newSlug || newSlug === oldSlug) return;
  try {
    await api(`/api/notes/${oldSlug}/move`, { method: 'POST', body: JSON.stringify({ new_slug: newSlug }) });
    document.querySelector('.modal-overlay')?.remove();
    toast('Nota movida');
    await api('/api/build/', { method: 'POST' });
    loadNotes();
    openEditor(newSlug);
  } catch (e) { toast('Error: ' + e.message, true); }
}

// ── Create note ──
function showCreateForm() {
  destroyEditor();

  // Build category options from existing notes
  const dirs = new Set();
  allNotes.forEach(n => {
    const parts = n.slug.split('/');
    if (parts.length > 1) dirs.add(parts.slice(0, -1).join('/'));
  });

  let html = '<div class="editor-header">';
  html += '<h2>Nueva nota</h2>';
  html += '<div class="editor-actions">';
  html += `<button class="btn" onclick="destroyEditor();renderNotesList()">Volver</button>`;
  html += `<button class="btn btn-accent" onclick="createNote()">Crear</button>`;
  html += '</div></div>';

  html += '<div class="fm-grid">';
  html += '<div class="fm-field"><label>Carpeta</label>';
  html += '<select id="new-dir">';
  [...dirs].sort().forEach(d => {
    html += `<option value="${esc(d)}">${esc(d)}</option>`;
  });
  html += '</select></div>';

  html += '<div class="fm-field"><label>Nombre archivo (sin .md)</label>';
  html += '<input id="new-filename" type="text" placeholder="mi-nueva-nota"></div>';

  // Common fields
  html += '<div class="fm-field"><label>Tipo</label>';
  html += '<select id="new-tipo"><option value="">--</option>';
  const tipos = schemas?.common?.find(f => f.name === 'tipo')?.options || [];
  tipos.forEach(t => { html += `<option value="${esc(t)}">${esc(t)}</option>`; });
  html += '</select></div>';

  html += '<div class="fm-field"><label>Estado</label>';
  html += '<select id="new-estado"><option value="borrador">borrador</option><option value="stub">stub</option><option value="completo">completo</option></select></div>';

  html += '<div class="fm-field full"><label>Tags (separados por coma)</label>';
  html += '<input id="new-tags" type="text"></div>';
  html += '</div>';

  html += '<textarea id="md-editor"></textarea>';

  document.getElementById('main').innerHTML = html;

  editor = new EasyMDE({
    element: document.getElementById('md-editor'),
    spellChecker: false,
    autofocus: false,
    status: ['lines', 'words'],
    toolbar: ['bold','italic','heading','|','quote','unordered-list','ordered-list','|','link','image','table','|','preview','side-by-side','|','guide'],
    minHeight: '400px',
    initialValue: '# Titulo\n\n',
  });
}

async function createNote() {
  const dir = document.getElementById('new-dir').value;
  const filename = document.getElementById('new-filename').value.trim();
  if (!filename) { toast('Nombre de archivo requerido', true); return; }

  const slug = dir ? `${dir}/${filename}` : filename;
  const fm = {};
  const tipo = document.getElementById('new-tipo').value;
  if (tipo) fm.tipo = tipo;
  const estado = document.getElementById('new-estado').value;
  if (estado) fm.estado = estado;
  const tags = document.getElementById('new-tags').value.trim();
  if (tags) fm.tags = tags.split(',').map(t => t.trim()).filter(Boolean);

  const body = editor ? editor.value() : '';

  try {
    await api('/api/notes/', { method: 'POST', body: JSON.stringify({ slug, frontmatter: fm, body }) });
    toast('Nota creada');
    await api('/api/build/', { method: 'POST' });
    loadNotes();
    openEditor(slug);
  } catch (e) { toast('Error: ' + e.message, true); }
}

// ── Media browser ──
async function showMediaBrowser() {
  const files = await api('/api/media/');
  let html = '<div class="editor-header">';
  html += '<h2>Media</h2>';
  html += '<div class="editor-actions">';
  html += `<button class="btn" onclick="destroyEditor();renderNotesList()">Volver</button>`;
  html += '</div></div>';

  html += '<div style="margin-bottom:16px">';
  html += '<input type="file" id="media-upload-input" style="display:none" onchange="uploadMedia()">';
  html += '<button class="btn btn-accent" onclick="document.getElementById(\'media-upload-input\').click()">Subir archivo</button>';
  html += ' <select id="media-subdir"><option value="">media/</option><option value="audio">media/audio/</option><option value="pdf">media/pdf/</option><option value="img">media/img/</option></select>';
  html += '</div>';

  html += '<table class="notes-table"><thead><tr>';
  html += '<th>Archivo</th><th>Tamano</th><th>Tipo</th><th></th>';
  html += '</tr></thead><tbody>';

  files.forEach(f => {
    const size = f.size > 1048576 ? (f.size / 1048576).toFixed(1) + ' MB' : (f.size / 1024).toFixed(0) + ' KB';
    html += `<tr>`;
    html += `<td>${esc(f.path)}</td>`;
    html += `<td>${size}</td>`;
    html += `<td><span class="chip">${esc(f.ext)}</span></td>`;
    html += `<td><button class="btn btn-danger" onclick="deleteMedia('${esc(f.path)}')">Borrar</button></td>`;
    html += '</tr>';
  });
  html += '</tbody></table>';
  document.getElementById('main').innerHTML = html;
}

async function uploadMedia() {
  const input = document.getElementById('media-upload-input');
  const file = input.files[0];
  if (!file) return;
  const subdir = document.getElementById('media-subdir').value;
  const formData = new FormData();
  formData.append('file', file);
  formData.append('subdir', subdir);
  try {
    await fetch('/api/media/upload', { method: 'POST', body: formData, credentials: 'same-origin' });
    toast('Archivo subido');
    showMediaBrowser();
  } catch (e) { toast('Error subiendo archivo', true); }
}

async function deleteMedia(path) {
  if (!confirm(`Borrar "${path}"?`)) return;
  try {
    await api(`/api/media/${path}`, { method: 'DELETE' });
    toast('Archivo borrado');
    showMediaBrowser();
  } catch (e) { toast('Error: ' + e.message, true); }
}

// ── Build ──
async function triggerBuild() {
  toast('Reconstruyendo sitio...');
  try {
    const r = await api('/api/build/', { method: 'POST' });
    if (r.ok) toast('Sitio reconstruido');
    else toast('Error en build: ' + r.stderr, true);
  } catch (e) { toast('Error: ' + e.message, true); }
}

// ── Util ──
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Init ──
checkAuth();
