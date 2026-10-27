// The stress test (stress.html): many copies of one model from manifest.json, drawn as separate meshes or as one InstancedMesh per part of the model,
// with the frame rate and the draw calls. A rigged model's copies can play a clip when they are separate meshes; instanced copies share one still pose
// (the first frame of Idle), because an InstancedMesh is not skinned. "Repaint half" gives every other copy a repainted palette texture, the way the
// viewer's colour picker does, to show what a second texture does to the draw calls. Everything is local: the manifest, the GLBs and the vendored three.js.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { paintedTexture } from './viewer.js';

const GLASS = 'GlobalPaletteGlass';
const GOLDEN = Math.PI * (3 - Math.sqrt(5)); // turns each copy by the golden angle, so a field of them does not all face one way
const COUNTS = new Set(['100', '1000', '10000']);
const $ = (id) => document.getElementById(id);

const doc = await (await fetch('manifest.json')).json();
const byId = new Map(doc.assets.map((a) => [a.id, a]));
const loader = new GLTFLoader();

const renderer = new THREE.WebGLRenderer({ canvas: $('canvas'), antialias: true });
renderer.setPixelRatio(Math.min(globalThis.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;
const scene = new THREE.Scene();
scene.background = new THREE.Color(matchMedia('(prefers-color-scheme: dark)').matches ? 0x26282b : 0xe9e6df);
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8478, 1.55));
const key = new THREE.DirectionalLight(0xfff4e6, 1.35);
key.position.set(3, 5, 4);
scene.add(key);
const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const state = { model: null, gltf: null, pieces: [], painted: new Map(), field: null, mixers: [], playing: false, token: null };

// ---- the model ---------------------------------------------------------------------------------------------------------------------------
// Flat palette colours as the viewer draws them; the glass twin of the palette blends and is drawn after the solid parts.
function prepareMaterials(root) {
  root.traverse((o) => {
    if (!o.isMesh) return;
    const m = o.material;
    m.flatShading = true;
    m.roughness = 1;
    m.metalness = 0;
    if (m.name === GLASS) { m.transparent = true; m.depthWrite = false; o.renderOrder = 1; }
  });
}

// A skinned mesh posed by its skeleton, written out as a plain geometry (positions only; flat shading takes the normals from the faces).
function bakeSkinned(mesh) {
  mesh.skeleton.update();
  const g = mesh.geometry.clone();
  g.deleteAttribute('skinIndex');
  g.deleteAttribute('skinWeight');
  const pos = g.attributes.position, v = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    mesh.getVertexPosition(i, v);
    pos.setXYZ(i, v.x, v.y, v.z);
  }
  g.computeBoundingBox();
  g.computeBoundingSphere();
  return g;
}

// A skinned mesh works out its bounds from its posed vertices at its first render, which for 10,000 copies is a long first frame, and keeps them while
// the clip moves it, so a limb could be culled at the screen's edge. Its bounds are made once here, in the still pose with room to move, and copied.
function roomyBounds(mesh) {
  mesh.skeleton.update();
  mesh.computeBoundingSphere();
  mesh.boundingSphere.radius *= 1.5;
  mesh.computeBoundingBox();
  mesh.boundingBox.expandByScalar(mesh.boundingSphere.radius / 3);
}

// The model as {geometry, material, matrix, owned} pieces, one per mesh, for instancing; a rigged one in the first frame of its Idle clip.
function piecesOf(gltf) {
  const root = gltf.scene;
  const pose = gltf.animations.find((c) => c.name === 'Idle') || gltf.animations[0];
  if (pose) {
    const mixer = new THREE.AnimationMixer(root);
    mixer.clipAction(pose).play();
    mixer.update(0);
  }
  root.updateMatrixWorld(true);
  const pieces = [];
  root.traverse((o) => {
    if (!o.isMesh) return;
    const owned = !!o.isSkinnedMesh;
    if (owned) roomyBounds(o);
    pieces.push({ geometry: owned ? bakeSkinned(o) : o.geometry, material: o.material, matrix: o.matrixWorld.clone(), owned, order: o.renderOrder });
  });
  return pieces;
}

// The swatches "Repaint half" changes: the model's second paint, or else its first paintable part in the first common colour that differs from it.
function repaintSwap(a) {
  if ((a.paints?.length ?? 0) > 1) return a.paints[1].swap;
  const part = a.paintable?.[0];
  if (!part) return null;
  const colour = doc.palette.common.find((c) => c.hex.toUpperCase() !== part.hex.toUpperCase());
  return colour ? { [part.swatch]: colour.hex } : null;
}

// One repainted copy of every material that has the palette texture (made once per model, shared by every repainted copy).
function paintedMaterials(gltf, swap) {
  const out = new Map();
  if (!swap) return out;
  gltf.scene.traverse((o) => {
    const m = o.material;
    if (!o.isMesh || !m.map || out.has(m)) return;
    const copy = m.clone();
    copy.map = paintedTexture(m.map, swap);
    out.set(m, copy);
  });
  return out;
}

function disposeModel() {
  if (!state.gltf) return;
  const textures = new Set(), materials = new Set();
  state.gltf.scene.traverse((o) => {
    if (!o.isMesh) return;
    o.geometry.dispose();
    materials.add(o.material);
  });
  for (const m of state.painted.values()) materials.add(m);
  for (const m of materials) {
    if (m.map) textures.add(m.map);
    m.dispose();
  }
  for (const t of textures) t.dispose();
  for (const p of state.pieces) if (p.owned) p.geometry.dispose();
  state.gltf = null;
  state.pieces = [];
  state.painted = new Map();
}

async function loadModel(a) {
  const token = (state.token = Symbol(a.id));
  $('note').textContent = 'Loading ' + a.name + '…';
  const gltf = await loader.loadAsync(a.glb);
  if (token !== state.token) return false; // another model was picked meanwhile
  clearField();
  disposeModel();
  prepareMaterials(gltf.scene);
  state.model = a;
  state.gltf = gltf;
  state.pieces = piecesOf(gltf);
  state.poseName = (gltf.animations.find((c) => c.name === 'Idle') || gltf.animations[0])?.name || '';
  state.painted = paintedMaterials(gltf, repaintSwap(a));
  return true;
}

// ---- the field of copies -----------------------------------------------------------------------------------------------------------------
// Copy i stands on a square grid, spaced by the model's footprint, turned by the golden angle.
function placement(i, n, a) {
  const side = Math.ceil(Math.sqrt(n));
  const step = Math.max(a.size[0], a.size[2], 0.005) * 1.6;
  const x = ((i % side) - (side - 1) / 2) * step, z = (Math.floor(i / side) - (side - 1) / 2) * step;
  return new THREE.Matrix4().compose(new THREE.Vector3(x, 0, z), new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), i * GOLDEN), new THREE.Vector3(1, 1, 1));
}

// A copy of a rigged model with its own skeleton (Object3D.clone keeps the original's), so it can play a clip at its own time.
function cloneRig(source) {
  const copy = source.clone(true);
  const bones = new Map();
  copy.traverse((o) => { if (o.isBone) bones.set(o.name, o); });
  const originals = [];
  source.traverse((o) => { if (o.isSkinnedMesh) originals.push(o); });
  let k = 0;
  copy.traverse((o) => {
    if (!o.isSkinnedMesh) return;
    const src = originals[k++];
    o.bind(new THREE.Skeleton(src.skeleton.bones.map((b) => bones.get(b.name)), src.skeleton.boneInverses), src.bindMatrix);
    o.boundingSphere = src.boundingSphere.clone();
    o.boundingBox = src.boundingBox.clone();
  });
  return copy;
}

function motionClip(gltf) {
  return gltf.animations.find((c) => c.name !== 'Idle') || gltf.animations[0] || null;
}

function repaintCopy(copy) {
  copy.traverse((o) => {
    const m = o.isMesh && state.painted.get(o.material);
    if (m) o.material = m;
  });
}

function buildSeparate(field, n, repaint) {
  const { model: a, gltf } = state;
  const clip = a.rigged ? motionClip(gltf) : null;
  for (let i = 0; i < n; i++) {
    const copy = a.rigged ? cloneRig(gltf.scene) : gltf.scene.clone(true);
    placement(i, n, a).decompose(copy.position, copy.quaternion, copy.scale);
    if (repaint && i % 2) repaintCopy(copy);
    if (clip) {
      const mixer = new THREE.AnimationMixer(copy);
      mixer.clipAction(clip).play();
      mixer.update(clip.duration > 0 ? (i * 0.37) % clip.duration : 0); // each copy at its own point of the loop
      state.mixers.push(mixer);
    }
    field.add(copy);
  }
}

// One InstancedMesh per piece of the model and per paint: the same geometry and material drawn n times in one call.
function buildInstanced(field, n, repaint) {
  const a = state.model;
  const groups = repaint && state.painted.size ? [0, 1] : [0];
  const m = new THREE.Matrix4();
  for (const p of state.pieces) {
    for (const g of groups) {
      const material = g ? state.painted.get(p.material) || p.material : p.material;
      const size = Math.ceil((n - g) / groups.length);
      const mesh = new THREE.InstancedMesh(p.geometry, material, size);
      for (let j = 0; j < size; j++) mesh.setMatrixAt(j, m.multiplyMatrices(placement(j * groups.length + g, n, a), p.matrix));
      mesh.instanceMatrix.needsUpdate = true;
      mesh.computeBoundingSphere();
      mesh.renderOrder = p.order;
      field.add(mesh);
    }
  }
}

function clearField() {
  state.mixers = [];
  if (!state.field) return;
  scene.remove(state.field);
  state.field.traverse((o) => {
    if (o.isInstancedMesh) o.dispose();
    if (o.isSkinnedMesh) o.skeleton.dispose();
  });
  state.field = null;
}

function frameField(n, a) {
  const side = Math.ceil(Math.sqrt(n)) * Math.max(a.size[0], a.size[2], 0.005) * 1.6;
  const span = Math.max(side, a.size[1] * 4);
  camera.near = span / 2000;
  camera.far = span * 20;
  camera.position.set(0, span * 0.55, span * 0.95);
  camera.updateProjectionMatrix();
  controls.target.set(0, 0, 0);
  controls.minDistance = span * 0.02;
  controls.maxDistance = span * 6;
  controls.update();
}

function build() {
  const a = state.model;
  if (!a) return;
  const n = Number($('count').value), instanced = $('mode').value === 'instanced', repaint = $('paint').checked;
  clearField();
  const t0 = performance.now();
  const field = new THREE.Group();
  if (instanced) buildInstanced(field, n, repaint);
  else buildSeparate(field, n, repaint);
  scene.add(field);
  state.field = field;
  renderer.compile(scene, camera);
  $('built').textContent = Math.round(performance.now() - t0) + ' ms';
  frameField(n, a);
  syncClip();
}

// ---- controls ----------------------------------------------------------------------------------------------------------------------------
function clipNote(a, clip, instanced) {
  if (!a.rigged) return '';
  if (!clip) return 'This model has a rig but no clips.';
  if (instanced) return `Instanced copies share one still pose (the first frame of ${state.poseName}): an InstancedMesh is not skinned. Animating them takes baked vertex-animation textures.`;
  return '';
}

function syncClip() {
  const a = state.model, clip = a.rigged ? motionClip(state.gltf) : null, instanced = $('mode').value === 'instanced';
  const usable = !!clip && !instanced;
  $('clip').disabled = !usable;
  $('clip-label').classList.toggle('off', !usable);
  $('clip-name').textContent = clip ? clip.name : 'clip';
  state.playing = usable && $('clip').checked;
  $('paint').disabled = !state.painted.size;
  $('note').textContent = clipNote(a, clip, instanced);
}

function writeUrl() {
  const q = new URLSearchParams({ model: $('model').value, count: $('count').value, mode: $('mode').value });
  if ($('clip').checked) q.set('clip', '1');
  if ($('paint').checked) q.set('paint', '1');
  history.replaceState(null, '', '?' + q);
}

function readUrl() {
  const q = new URLSearchParams(location.search);
  const model = byId.has(q.get('model')) ? q.get('model') : 'GN_Ant_01';
  $('model').value = byId.has(model) ? model : doc.assets[0].id;
  if (COUNTS.has(q.get('count'))) $('count').value = q.get('count');
  if (q.get('mode') === 'instanced') $('mode').value = 'instanced';
  $('clip').checked = q.get('clip') === '1';
  $('paint').checked = q.get('paint') === '1';
}

function fillModels() {
  const groups = new Map();
  for (const a of [...doc.assets].sort((x, y) => x.type.localeCompare(y.type) || x.name.localeCompare(y.name))) {
    const top = a.type.split('/')[0];
    if (!groups.has(top)) groups.set(top, Object.assign(document.createElement('optgroup'), { label: top }));
    const text = `${a.name} (${a.triangles} tris${a.rigged ? ', rigged' : ''})`;
    groups.get(top).append(new Option(text, a.id));
  }
  $('model').replaceChildren(...groups.values());
}

async function pickModel() {
  writeUrl();
  const a = byId.get($('model').value);
  try {
    if (await loadModel(a)) build();
  } catch (e) {
    console.warn(e);
    $('note').textContent = 'Could not load ' + a.name + '.';
  }
}

fillModels();
readUrl();
$('model').addEventListener('change', pickModel);
for (const id of ['count', 'mode', 'paint']) $(id).addEventListener('change', () => { writeUrl(); build(); });
$('clip').addEventListener('change', () => { writeUrl(); syncClip(); });

// ---- the loop ----------------------------------------------------------------------------------------------------------------------------
const clock = new THREE.Clock();
let frames = 0, since = performance.now();

function resize() {
  const w = Math.max(1, innerWidth), h = Math.max(1, innerHeight);
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

function showStats(now) {
  $('fps').textContent = (frames * 1000 / (now - since)).toFixed(1);
  $('calls').textContent = renderer.info.render.calls.toLocaleString('en');
  $('tris').textContent = renderer.info.render.triangles.toLocaleString('en');
  frames = 0;
  since = now;
}

function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), 0.1);
  if (state.playing) for (const m of state.mixers) m.update(dt);
  controls.update();
  renderer.render(scene, camera);
  frames++;
  if (now - since >= 1000) showStats(now);
}

// The FPS above is capped by the display (and by the browser, in a hidden tab). This times frames back to back instead: each one advances the clips,
// renders and reads one pixel back, which waits for the GPU to finish, so the time per frame is the real cost of the scene, uncapped.
function timeFrames(n = 60, budget = 3000) {
  const gl = renderer.getContext(), px = new Uint8Array(4);
  const step = () => {
    if (state.playing) for (const m of state.mixers) m.update(1 / 60);
    renderer.render(scene, camera);
    gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  };
  step(); // (the first frame may still upload buffers)
  const t0 = performance.now();
  let i = 0;
  while (i < n && (i < 3 || performance.now() - t0 < budget)) { step(); i++; } // a slow scene stops after about `budget` ms, not 60 frames
  const ms = (performance.now() - t0) / i, { calls, triangles } = renderer.info.render;
  $('bench-out').textContent = `${ms.toFixed(1)} ms a frame (${Math.round(1000 / ms)} FPS uncapped, ${i} frames)`;
  $('calls').textContent = calls.toLocaleString('en');
  $('tris').textContent = triangles.toLocaleString('en');
  return { ms, calls, triangles, frames: i };
}
$('bench').addEventListener('click', () => timeFrames());
globalThis.stressTimeFrames = timeFrames; // for measuring from the console: stressTimeFrames(120, 10000)

addEventListener('resize', resize);
resize();
await pickModel();
requestAnimationFrame(frame);
