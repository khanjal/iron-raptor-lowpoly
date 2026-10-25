// The asset browser: search, categories, tag chips, a grid of thumbnails and the viewer panel. Reads manifest.json; deep links use the URL hash (#GV_Sedan_01).
import { Viewer } from './viewer.js';

const $ = (id) => document.getElementById(id);
const el = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else if (v !== false && v != null) e.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids) if (kid != null) e.append(kid);
  return e;
};

// Which tags are shown under which heading; anything else goes under "More tags".
const TAG_GROUPS = [
  ['Setting', ['modern', 'retro', 'classic', 'rural', 'urban', 'suburban', 'sci-fi', 'diner']],
  ['Condition', ['new', 'damaged', 'rotten', 'abandoned', 'fresh', 'weathered']],
  ['Colour', ['red', 'blue', 'green', 'yellow', 'white', 'black', 'brown', 'grey', 'cream', 'violet']],
];
const FEATURES = [['animated', 'Animated (clips)', (a) => a.clips.length > 0], ['opens', 'Has moving parts', (a) => a.interactive], ['lit', 'Has lights', (a) => !!a.lights]];

const state = {
  assets: [], byId: new Map(), was: new Map(), wantPaint: null, wantTheme: null, themes: {}, glow: [], common: [], max: false,
  q: '', category: '', tags: new Set(), features: new Set(),
  current: null, viewer: null, expanded: new Set(),
};

// ---- data -------------------------------------------------------------------------------------------------------------------------------
async function init() {
  let doc;
  try {
    const r = await fetch('manifest.json');
    if (!r.ok) throw new Error(r.status);
    doc = await r.json();
  } catch (e) {
    $('count').textContent = 'Could not load manifest.json (' + e.message + '). Run tools/make_manifest.py, or serve the site folder over http.';
    return;
  }
  state.assets = doc.assets;
  state.glow = (doc.palette && doc.palette.glow) || [];
  state.common = (doc.palette && doc.palette.common) || [];
  state.realistic = (doc.palette && doc.palette.realistic) || {};
  state.themes = doc.themes || {};
  for (const a of state.assets) {
    a.haystack = [a.name, a.id, ...(a.aliases || []), a.type.replace(/[\/-]/g, ' '), ...a.tags].join(' ').toLowerCase();
    state.byId.set(a.id, a);
    for (const old of a.aliases || []) state.was.set(old, { asset: a }); // an id the model had before: old links and bookmarks still open it
    for (const p of a.paints || []) if (p.was) state.was.set(p.was, { asset: a, paint: p.name }); // a model that became a colour or a style keeps its old link
    for (const t of a.themes || []) if (t.was) state.was.set(t.was, { asset: a, theme: t.name });
  }
  readUrlState();
  if ((new URLSearchParams(location.search).get('cat') || '') !== state.category) writeUrlState();   // an old ?cat=alien link is rewritten to sci-fi, as an old #id is
  buildTree();
  buildChips();
  render();
  window.addEventListener('hashchange', syncFromHash);
  syncFromHash();
}

// ---- filtering --------------------------------------------------------------------------------------------------------------------------
function matches(a, skip = {}) {
  if (!skip.q && state.q) {
    for (const t of state.q.toLowerCase().split(/\s+/).filter(Boolean)) if (!a.haystack.includes(t)) return false;
  }
  if (!skip.category && state.category && !(a.type === state.category || a.type.startsWith(state.category + '/'))) return false;
  for (const t of state.tags) if (skip.tag !== t && !a.tags.includes(t)) return false;
  for (const f of state.features) if (skip.feature !== f && !FEATURES.find((x) => x[0] === f)[2](a)) return false;
  return true;
}

function render() {
  const list = state.assets.filter((a) => matches(a));
  const grid = $('grid');
  grid.replaceChildren(...list.map(card));
  $('count').textContent = list.length === state.assets.length ? `${list.length} models` : `${list.length} of ${state.assets.length} models`;
  $('empty').hidden = list.length > 0;
  const active = state.q || state.category || state.tags.size || state.features.size;
  $('clear').hidden = !active;
  updateTree();
  updateChips();
}

function card(a) {
  const img = el('img', { src: a.thumb, alt: '', loading: 'lazy', width: 256, height: 256 });
  img.addEventListener('error', () => { img.replaceWith(el('span', { class: 'muted', text: a.name[0] })); });
  const badges = el('div', { class: 'badges' });
  if (a.rigged && a.clips.length) badges.append(el('span', { class: 'badge', text: 'animated' }));
  if (a.interactive) badges.append(el('span', { class: 'badge', text: 'opens' }));
  if (a.variants.length) badges.append(el('span', { class: 'badge', text: a.variants.length + 1 + ' variants' }));
  const b = el('button', { type: 'button', onclick: () => open(a.id) },
    el('div', { class: 'img' }, img),
    el('div', { class: 'meta' }, el('div', { class: 'name', text: a.name }), el('div', { class: 'sub', text: a.type.split('/').slice(0, -1).join(' / ') || a.type }), badges));
  b.setAttribute('aria-label', a.name);
  return el('li', { class: 'card' + (state.current === a.id ? ' current' : ''), 'data-id': a.id }, b);
}

// ---- category tree ----------------------------------------------------------------------------------------------------------------------
function buildTree() {
  const root = { children: new Map(), path: '', count: 0 };
  for (const a of state.assets) {
    let n = root;
    const parts = a.type.split('/');
    parts.forEach((p, i) => {
      if (!n.children.has(p)) n.children.set(p, { children: new Map(), path: parts.slice(0, i + 1).join('/'), name: p, count: 0 });
      n = n.children.get(p);
    });
  }
  state.tree = root;
  $('tree').replaceChildren(treeList(root, true));
}

const LABELS = { 'sci-fi': 'Sci-fi' };   // names that keep their hyphen
function label(s) { return LABELS[s] || s.replace(/-/g, ' ').replace(/^./, (c) => c.toUpperCase()); }

function treeList(node, top) {
  const ul = el('ul');
  if (top) {
    ul.append(el('li', {}, el('button', { class: 'node', type: 'button', 'data-path': '', onclick: () => setCategory('') }, el('span', { class: 'caret' }), 'All models', el('span', { class: 'n' }))));
  }
  for (const child of [...node.children.values()].sort((a, b) => a.name.localeCompare(b.name))) {
    const li = el('li');
    const has = child.children.size > 0;
    const btn = el('button', { class: 'node', type: 'button', 'data-path': child.path, onclick: () => { setCategory(child.path); if (has) toggleExpand(child.path, true); } },
      el('span', { class: 'caret', text: has ? '▸' : '' }), label(child.name), el('span', { class: 'n' }));
    li.append(btn);
    if (has) { const sub = treeList(child, false); sub.hidden = true; sub.dataset.for = child.path; li.append(sub); }
    ul.append(li);
  }
  return ul;
}

function toggleExpand(path, force) {
  if (force) state.expanded.add(path); else if (state.expanded.has(path)) state.expanded.delete(path); else state.expanded.add(path);
  updateTree();
}

function updateTree() {
  // counts follow the other filters, so the tree shows where the current search has results
  const counts = new Map();
  for (const a of state.assets) {
    if (!matches(a, { category: true })) continue;
    const parts = a.type.split('/');
    for (let i = 1; i <= parts.length; i++) { const p = parts.slice(0, i).join('/'); counts.set(p, (counts.get(p) || 0) + 1); }
    counts.set('', (counts.get('') || 0) + 1);
  }
  // keep the chosen category's ancestors open
  if (state.category) { const parts = state.category.split('/'); for (let i = 1; i < parts.length; i++) state.expanded.add(parts.slice(0, i).join('/')); }
  for (const b of $('tree').querySelectorAll('.node')) {
    const p = b.dataset.path;
    b.querySelector('.n').textContent = counts.get(p) || 0;
    b.setAttribute('aria-current', p === state.category ? 'true' : 'false');
    b.style.opacity = counts.get(p) ? '' : '.45';
    const caret = b.querySelector('.caret');
    if (caret.textContent) caret.textContent = state.expanded.has(p) ? '▾' : '▸';
  }
  for (const ul of $('tree').querySelectorAll('ul[data-for]')) ul.hidden = !state.expanded.has(ul.dataset.for);
}

function setCategory(path) {
  state.category = state.category === path ? '' : path;
  if (path === '') state.category = '';
  writeUrlState();
  render();
}

// ---- chips ------------------------------------------------------------------------------------------------------------------------------
function buildChips() {
  const all = new Map();
  for (const a of state.assets) for (const t of a.tags) all.set(t, (all.get(t) || 0) + 1);
  const used = new Set();
  const box = $('chips');
  box.replaceChildren();
  const group = (title, tags, extra) => {
    const wrap = el('div', { class: 'chip-group' }, el('h2', { text: title }));
    const chips = el('div', { class: 'chips' });
    for (const t of tags) chips.append(extra ? extra(t) : tagChip(t));
    wrap.append(chips);
    return wrap;
  };
  box.append(group('Features', FEATURES.map((f) => f[0]), (id) => featureChip(id)));
  for (const [title, tags] of TAG_GROUPS) {
    const present = tags.filter((t) => all.has(t));
    present.forEach((t) => used.add(t));
    if (present.length) box.append(group(title, present));
  }
  const rest = [...all.keys()].filter((t) => !used.has(t)).sort();
  const det = el('details', { class: 'more' }, el('summary', { text: `More tags (${rest.length})` }));
  const chips = el('div', { class: 'chips' });
  for (const t of rest) chips.append(tagChip(t));
  det.append(chips);
  box.append(det);
}

function tagChip(t) {
  return el('button', { class: 'chip', type: 'button', 'data-tag': t, 'aria-pressed': 'false', onclick: () => toggleTag(t) }, t, el('span', { class: 'n' }));
}
function featureChip(id) {
  const f = FEATURES.find((x) => x[0] === id);
  return el('button', { class: 'chip', type: 'button', 'data-feature': id, 'aria-pressed': 'false', onclick: () => toggleFeature(id) }, f[1], el('span', { class: 'n' }));
}

function updateChips() {
  for (const c of $('chips').querySelectorAll('.chip')) {
    const tag = c.dataset.tag, feat = c.dataset.feature;
    const on = tag ? state.tags.has(tag) : state.features.has(feat);
    c.setAttribute('aria-pressed', on);
    // how many models match with this chip added (or, if it is on, with it taken off): tells the visitor what a click would give
    let n = 0;
    for (const a of state.assets) {
      if (tag ? !matches(a, { tag }) || !a.tags.includes(tag) : !matches(a, { feature: feat }) || !FEATURES.find((x) => x[0] === feat)[2](a)) continue;
      n++;
    }
    c.querySelector('.n').textContent = n;
    c.classList.toggle('zero', n === 0 && !on);
  }
}

function toggleTag(t) { state.tags.has(t) ? state.tags.delete(t) : state.tags.add(t); writeUrlState(); render(); }
function toggleFeature(f) { state.features.has(f) ? state.features.delete(f) : state.features.add(f); writeUrlState(); render(); }

// ---- url --------------------------------------------------------------------------------------------------------------------------------
// The hash is the open model (#GV_Sedan_01). The filters live in the query string, so a link can carry both.
function readUrlState() {
  const p = new URLSearchParams(location.search);
  state.q = p.get('q') || '';
  state.category = (p.get('cat') || '').replace(/^alien(?=\/|$)/, 'sci-fi');      // links made while the category was still called alien
  state.tags = new Set((p.get('tags') || '').split(',').filter(Boolean));
  state.features = new Set((p.get('f') || '').split(',').filter(Boolean));
  $('search').value = state.q;
}
function writeUrlState() {
  const p = new URLSearchParams();
  if (state.q) p.set('q', state.q);
  if (state.category) p.set('cat', state.category);
  if (state.tags.size) p.set('tags', [...state.tags].join(','));
  if (state.features.size) p.set('f', [...state.features].join(','));
  const qs = p.toString();
  history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
}

// ---- viewer -----------------------------------------------------------------------------------------------------------------------------
function open(id) {
  if (location.hash.slice(1) !== id) location.hash = id; // hashchange does the rest
  else syncFromHash();
}

function syncFromHash() {
  const id = decodeURIComponent(location.hash.slice(1));
  let a = state.byId.get(id);
  if (!a && state.was.has(id)) { const w = state.was.get(id); a = w.asset; state.wantPaint = w.paint; state.wantTheme = w.theme; history.replaceState(null, '', location.pathname + location.search + '#' + a.id); }
  if (!a) { closeViewer(false); return; }
  showAsset(a);
}

// Maximised: the viewer covers the page and the stage fills it (css .viewer.max). The choice is remembered for the next model and visit.
function setMax(on) {
  state.max = on;
  $('viewer').classList.toggle('max', on);
  $('maximize').textContent = on ? 'Shrink' : 'Expand';
  document.body.style.overflow = on || matchMedia('(max-width: 62rem)').matches ? 'hidden' : '';   // the page behind a maximised viewer does not scroll
  try { localStorage.setItem('lowpoly-max', on ? '1' : ''); } catch (e) { /* private window: not remembered */ }
  if (state.viewer) state.viewer.resize();
}

function closeViewer(updateHash = true) {
  if (updateHash && location.hash) history.pushState(null, '', location.pathname + location.search);
  state.current = null;
  $('viewer').hidden = true;
  $('layout').classList.remove('has-viewer');
  document.body.style.overflow = '';
  for (const c of document.querySelectorAll('.card.current')) c.classList.remove('current');
}

async function showAsset(a) {
  state.current = a.id;
  $('viewer').hidden = false;
  $('layout').classList.add('has-viewer');
  setMax(state.max);
  if (matchMedia('(max-width: 62rem)').matches) document.body.style.overflow = 'hidden';
  $('filters').classList.remove('open');
  document.title = a.name + ' · Iron Raptor Lowpoly';
  for (const c of document.querySelectorAll('.card')) c.classList.toggle('current', c.dataset.id === a.id);
  fillDetails(a);

  if (!state.viewer) {
    try { state.viewer = new Viewer($('canvas'), { glow: state.glow }); }
    catch (e) { $('status').textContent = 'WebGL is not available here: ' + e.message; return; }
    window.lowpolyViewer = state.viewer; // handy in the browser console
    state.viewer.onPartsChanged = updatePartButtons;
    state.viewer.onHover = (role) => { const spin = role && state.viewer.parts[role] && state.viewer.parts[role].kind === 'spin'; $('hint').textContent = role ? `Click to ${spin ? 'start or stop' : 'open or close'}: ${role}` : defaultHint(); };
  }
  state.viewer.resize();
  $('status').textContent = 'Loading…';
  try {
    const info = await state.viewer.load(a);
    if (!info || state.current !== a.id) return;
    $('status').textContent = '';
    setupControls(a, info);
  } catch (e) {
    $('status').textContent = 'Could not load ' + a.glb + ': ' + e.message;
    console.error(e);
  }
}

function defaultHint() {
  const a = state.byId.get(state.current);
  return a && a.interactive ? 'Click a door, drawer, lid or wheel to open or spin it. Drag to orbit, scroll to zoom, right-drag to pan.' : 'Drag to orbit, scroll to zoom, right-drag to pan.';
}

// A breadcrumb click: close the viewer and show that category, opened in the tree like a click there. The filters the model passes (search, tags, features) are kept;
// if it does not pass them (a deep link with a query, a variant that lacks the tag) they are cleared, so the grid is never empty or hiding the model.
function jumpToCategory(a, path) {
  if (!matches(a, { category: true })) { state.q = ''; $('search').value = ''; state.tags.clear(); state.features.clear(); }
  state.category = path;
  if ($('tree').querySelector(`ul[data-for="${CSS.escape(path)}"]`)) state.expanded.add(path);
  writeUrlState();
  render();
  closeViewer();
  window.scrollTo(0, 0);
  const count = $('count');
  count.tabIndex = -1;
  count.focus({ preventScroll: true });   // the focused button went away with the viewer: put focus where the new list starts
}

function fillDetails(a) {
  $('v-name').textContent = a.name;
  const segs = a.type.split('/');          // the breadcrumbs: each level jumps to that category
  $('v-type').replaceChildren(...segs.flatMap((s, i) => [
    ...(i ? [el('span', { 'aria-hidden': 'true', text: ' › ' })] : []),
    el('button', { class: 'crumb', type: 'button', title: 'Show all in ' + label(s), 'aria-label': 'Show all in ' + label(s), onclick: () => jumpToCategory(a, segs.slice(0, i + 1).join('/')) }, label(s)),
  ]));
  $('v-tris').textContent = a.triangles.toLocaleString();
  $('v-size').textContent = `${fmt(a.size[0])} × ${fmt(a.size[2])} × ${fmt(a.size[1])} m (width × depth × height)`;
  $('v-id').textContent = a.id;
  $('v-traits').textContent = [a.rigged ? 'rigged' : 'static', a.interactive ? 'moving parts: ' + Object.keys(a.parts).join(', ') : null, a.lights ? (a.lights === 1 ? '1 light' : a.lights + ' lights') : null, a.clips.length ? 'clips: ' + a.clips.join(', ') : null].filter(Boolean).join('; ');
  $('v-download').href = a.glb;
  $('v-download').setAttribute('download', a.id + '.glb');
  const tags = $('v-tags');
  tags.replaceChildren(...a.tags.map((t) => el('button', { class: 'chip small-chip', type: 'button', onclick: () => { state.tags.add(t); writeUrlState(); render(); $('filters').classList.add('open'); closeViewer(); } }, t)));
  const vs = a.variants.map((id) => state.byId.get(id)).filter(Boolean);
  $('v-variants').hidden = vs.length === 0;
  $('v-variant-list').replaceChildren(...[a, ...vs].sort((x, y) => x.id.localeCompare(y.id)).map((v) =>
    el('button', { class: 'pill', type: 'button', 'aria-current': v.id === a.id ? 'true' : 'false', onclick: () => open(v.id) }, v.name)));
  $('hint').hidden = false;
  $('hint').textContent = defaultHint();
}

// Look: a style (a theme from the manifest: one swap over the palette, the same for every model that lists it), the model's colour presets as chips, and a
// colour box for every paintable part, so any part can be any colour. The viewer repaints a copy of the palette image ({swatch index: '#RRGGBB'}); nothing
// about the mesh changes. What a person picks for a part wins over the style. A model with parts but no presets of its own gets Original plus the
// manifest's common colours (palette.common) for its first part, the main colour.
function setupLook(a) {
  const parts = a.paintable || [], themes = a.themes || [];
  const common = a.paints || !parts.length ? null : [{ name: 'Original', hex: parts[0].hex, swap: {} }, ...state.common.map((c) => ({ name: c.name, hex: c.hex, swap: { [parts[0].swatch]: c.hex } }))];
  const paints = a.paints || common || [];
  // Only for the common colours: the ones this kind of model really comes in are listed first, the rest wait behind "More colours".
  const real = a.paints ? null : state.realistic[a.type.split('/')[0]];
  const isWeird = (p) => !!real && p.name !== 'Original' && !real.includes(p.name);
  let showWeird = false;
  $('v-themes').hidden = themes.length === 0;
  $('v-paints').hidden = paints.length === 0 && parts.length === 0;
  if (!themes.length && !paints.length && !parts.length) return;
  let themeSwap = {}, overrides = {};
  const themeChips = new Map(), paintChips = new Map(), inputs = new Map();
  const press = (chips, name) => { for (const [n, b] of chips) b.setAttribute('aria-pressed', n === name ? 'true' : 'false'); };
  const apply = () => state.viewer.setPaint({ ...themeSwap, ...overrides });
  const syncInputs = () => { for (const part of parts) inputs.get(part.swatch).value = (overrides[part.swatch] || themeSwap[part.swatch] || part.hex).toLowerCase(); };
  const chooseTheme = (name) => { themeSwap = (name && state.themes[name]) || {}; syncInputs(); apply(); press(themeChips, name || ''); };
  const choosePaint = (p) => { if (isWeird(p) && !showWeird) { showWeird = true; syncMore(); } overrides = { ...p.swap }; syncInputs(); apply(); press(paintChips, p.name); };
  for (const t of [{ name: '' }, ...themes]) themeChips.set(t.name, el('button', { class: 'pill', type: 'button', onclick: () => chooseTheme(t.name) }, t.name || 'Classic'));
  for (const p of paints) paintChips.set(p.name, el('button', { class: 'pill paint', type: 'button', onclick: () => choosePaint(p) }, el('i', { style: 'background:' + p.hex }), p.name));
  for (const part of parts) {
    inputs.set(part.swatch, el('input', { type: 'color', value: part.hex.toLowerCase(), 'aria-label': part.part + ' colour', oninput: (e) => { overrides[part.swatch] = e.target.value.toUpperCase(); apply(); press(paintChips, ''); } }));
  }
  $('v-theme-list').replaceChildren(...themeChips.values());
  const more = el('button', { class: 'pill', type: 'button', 'aria-expanded': 'false', onclick: () => { showWeird = !showWeird; syncMore(); } });
  const syncMore = () => {
    for (const p of paints) paintChips.get(p.name).hidden = isWeird(p) && !showWeird;
    more.textContent = showWeird ? 'Fewer colours' : 'More colours';
    more.setAttribute('aria-expanded', showWeird);
  };
  syncMore();
  $('v-paint-list').replaceChildren(...paintChips.values(), ...(paints.some(isWeird) ? [more] : []));
  $('v-paint-parts').replaceChildren(...parts.map((part) => el('label', { class: 'paint-part' }, el('span', { text: part.part }), inputs.get(part.swatch))));
  chooseTheme(themes.some((t) => t.name === state.wantTheme) ? state.wantTheme : '');
  if (paints.length) choosePaint(paints.find((p) => p.name === state.wantPaint) || paints[0]);
  state.wantPaint = state.wantTheme = null;
}

function fmt(n) { return n >= 10 ? n.toFixed(1) : n >= 1 ? n.toFixed(2) : n.toFixed(3); }

function setupControls(a, info) {
  const v = state.viewer;
  // moving parts
  setupLook(a); // the viewer has the model by now
  const roles = info.parts;
  $('v-parts').hidden = roles.length === 0;
  $('v-part-list').replaceChildren(...roles.map((r) => el('button', { class: 'pill', type: 'button', 'data-role': r, 'aria-pressed': 'false', onclick: () => v.togglePart(r) }, r)));
  updatePartButtons(v.partStates());
  // lights
  $('v-lights').hidden = !info.lights;
  setLightsButton(v.lightsOn);
  // clips
  const clips = info.clips;
  $('v-clips').hidden = clips.length === 0;
  const sel = $('clip');
  sel.replaceChildren(...clips.map((c) => el('option', { value: c, text: c })));
  if (clips.length) sel.value = v.clip;
  $('speed').value = v.speed;
  $('speed-out').textContent = v.speed.toFixed(1) + '×';
  $('play').textContent = v.playing ? 'Pause' : 'Play';
}

function setLightsButton(on) {
  $('lights-toggle').setAttribute('aria-pressed', on);
  $('lights-toggle').textContent = on ? 'Lights on' : 'Lights off';
}

function updatePartButtons(states) {
  for (const s of states) {
    const b = $('v-part-list').querySelector(`[data-role="${s.role}"]`);
    if (b) b.setAttribute('aria-pressed', s.open);
  }
  const anyClosed = states.some((s) => s.kind !== 'spin' && !s.open);
  $('open-all').hidden = !states.some((s) => s.kind !== 'spin'); // a model with only wheels has nothing to open
  $('open-all').textContent = anyClosed ? 'Open all' : 'Close all';
}

// ---- wiring -----------------------------------------------------------------------------------------------------------------------------
$('lights-toggle').addEventListener('click', () => { const on = !state.viewer.lightsOn; state.viewer.setLights(on); setLightsButton(on); });
$('search').addEventListener('input', (e) => { state.q = e.target.value.trim(); writeUrlState(); render(); });
$('clear').addEventListener('click', () => { state.q = ''; state.category = ''; state.tags.clear(); state.features.clear(); $('search').value = ''; writeUrlState(); render(); });
$('home').addEventListener('click', (e) => { e.preventDefault(); $('clear').click(); closeViewer(); });
$('filters-toggle').addEventListener('click', () => {
  const on = $('filters').classList.toggle('open');
  $('filters-toggle').setAttribute('aria-expanded', on);
});
$('close').addEventListener('click', () => closeViewer());
$('maximize').addEventListener('click', () => setMax(!state.max));
$('reset-view').addEventListener('click', () => state.viewer && state.viewer.resetView());
$('open-all').addEventListener('click', () => {
  if (!state.viewer) return;
  const states = state.viewer.partStates();
  state.viewer.setAllParts(states.some((s) => s.kind !== 'spin' && !s.open));
});
$('clip').addEventListener('change', (e) => state.viewer.setClip(e.target.value));
$('speed').addEventListener('input', (e) => { const v = parseFloat(e.target.value); state.viewer.setSpeed(v); $('speed-out').textContent = v.toFixed(1) + '×'; });
$('play').addEventListener('click', () => {
  const v = state.viewer;
  v.setPlaying(!v.playing);
  $('play').textContent = v.playing ? 'Pause' : 'Play';
});
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && state.current) { if (state.max) setMax(false); else closeViewer(); } });

try { state.max = localStorage.getItem('lowpoly-max') === '1'; } catch (e) { /* no storage: not maximised */ }
init();
