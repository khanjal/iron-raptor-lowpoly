// The 3D viewer: loads one GLB, frames it from the manifest's size, lights the flat palette colours, lets the visitor open the moving parts
// (doors, drawers, lids) and play a rig's clips. No framework; three.js is vendored under vendor/three.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const GLASS = 'GlobalPaletteGlass'; // the blended twin of the palette material (art/scripts/common.py): windows, bottles, domes
const GRID = 16; // the palette is a 16 x 16 grid of flat swatches (art/scripts/common.py)
const loader = new GLTFLoader();
// emitter colour names (art/scripts/emitters.py) -> light colours
const LIGHT_COLOURS = { warm: 0xffc97a, cool: 0xcfe4ff, flame: 0xff9a3c, red: 0xff3b30, green: 0x4cff7a, pink: 0xff6fb5 };

export class Viewer {
  constructor(canvas, { glow = [], transparent = true } = {}) {
    this.canvas = canvas;
    this.glow = glow; // [{name, index, hex}] swatches that light up
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: transparent, preserveDrawingBuffer: false });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.NoToneMapping; // palette colours stay the colours in the palette

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(35, 1, 0.01, 2000);
    // soft light: a sky/ground hemisphere does most of the work, so flat faces read as their palette colour; a key and a fill give the facets an edge
    const sky = new THREE.HemisphereLight(0xffffff, 0x8a8478, 1.55);
    this.scene.add(sky);
    const key = new THREE.DirectionalLight(0xfff4e6, 1.35);
    key.position.set(3, 5, 4);
    const fill = new THREE.DirectionalLight(0xdce8ff, 0.55);
    fill.position.set(-4, 2, -3);
    this.scene.add(key, fill);
    this.ambient = [[sky, 1.55], [key, 1.35], [fill, 0.55]]; // [light, normal intensity]: dimmed while the model's own lights are on

    this.lights = []; // {light, base, flicker, when, phase}: the model's own lights (its interactions file)
    this.lightsOn = true;

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.12;
    this.controls.screenSpacePanning = true;

    this.root = null; // the loaded model
    this.shadow = null;
    this.mixer = null;
    this.actions = {};
    this.clip = null;
    this.speed = 1;
    this.playing = true;
    this.parts = {}; // role -> state
    this.hover = null;
    this.clock = new THREE.Clock();
    this.ray = new THREE.Raycaster();
    this.pointer = new THREE.Vector2();
    this.onPartsChanged = () => {};
    this.onHover = () => {};
    this._bindPointer();
    this._frame = this._frame.bind(this);
    this._raf = requestAnimationFrame(this._frame);
    this._ro = new ResizeObserver(() => this.resize());
    this._ro.observe(canvas.parentElement || canvas);
    this.resize();
  }

  resize() {
    const p = this.canvas.parentElement || this.canvas;
    const w = Math.max(1, p.clientWidth), h = Math.max(1, p.clientHeight);
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
  }

  // ---- loading ---------------------------------------------------------------------------------------------------------------------------
  async load(asset) {
    const token = (this._token = Symbol());
    const gltf = await loader.loadAsync(asset.glb);
    if (token !== this._token) return null; // a newer load started
    this._clear();
    const root = gltf.scene;
    this.root = root;
    this.scene.add(root);
    this._materials(root, asset);
    this._parts(root, asset);
    await this._lights(root, asset, token);
    if (token !== this._token) return null;
    this._applyLights(); // (also puts the room light back after a model that dimmed it)
    this._clips(gltf, asset);
    this._frameModel(asset);
    this._groundShadow(asset);
    return { clips: Object.keys(this.actions), parts: Object.keys(this.parts), lights: this.lights.length };
  }

  _clear() {
    this.mixer = null;
    this.actions = {};
    this.clip = null;
    this.parts = {};
    this.lights = [];
    this.hover = null;
    if (this.shadow) { this.scene.remove(this.shadow); this.shadow.material.map.dispose(); this.shadow.material.dispose(); this.shadow.geometry.dispose(); this.shadow = null; }
    if (this.root) {
      this.scene.remove(this.root);
      const seen = new Set();
      this.root.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        const mats = Array.isArray(o.material) ? o.material : o.material ? [o.material] : [];
        for (const m of mats) {
          if (seen.has(m)) continue;
          seen.add(m);
          for (const k of ['map', 'emissiveMap']) if (m[k]) m[k].dispose();
          m.dispose();
        }
      });
      this.root = null;
    }
  }

  // Flat, unlit-looking palette colours; the glow swatches get an emissive map so they shine. The palette is 16 x 16 swatches in a small image;
  // swatch i is column i % 16, row i / 16 from the top, and every UV points at the middle of one swatch, so a mask of the glow swatches lines up with it.
  _materials(root, asset) {
    const emissive = new Map(); // base-colour image -> emissive texture
    root.traverse((o) => {
      if (!o.isMesh) return;
      const m = o.material;
      m.flatShading = true;
      m.roughness = 1;
      m.metalness = 0;
      m.side = THREE.FrontSide;
      if (m.name === GLASS) {
        // see-through: it blends over what is behind it and does not hide it, and it is drawn after the solid parts
        m.transparent = true;
        m.depthWrite = false;
        o.renderOrder = 1;
        o.userData.glass = true;
      }
      if (m.map && this.glow.length) {
        let tex = emissive.get(m.map.image);
        if (!tex) { tex = this._glowMap(m.map); emissive.set(m.map.image, tex); }
        m.emissiveMap = tex;
        m.emissive = new THREE.Color(0xffffff);
        m.emissiveIntensity = 1.25;
      }
      m.needsUpdate = true;
    });
  }

  // A colour variant of the model: every swatch in `swap` ({index: '#rrggbb'}) is painted over on a copy of the palette image, so the same mesh shows
  // another paint. An empty swap puts the original palette back. The glow map made from the original stays valid (it only looks at the glow swatches).
  setPaint(swap) {
    if (!this.root) return;
    const entries = Object.entries(swap || {});
    this.root.traverse((o) => {
      if (!o.isMesh || !o.material || !o.material.map) return;
      const m = o.material;
      if (!m.userData.basePalette) m.userData.basePalette = m.map;
      const base = m.userData.basePalette;
      if (m.map !== base) { m.map.dispose(); m.map = base; }
      if (entries.length) {
        const img = base.image, w = img.width, h = img.height, cell = Math.max(1, Math.round(w / GRID));
        const c = document.createElement('canvas');
        c.width = w; c.height = h;
        const g = c.getContext('2d');
        g.drawImage(img, 0, 0);
        for (const [i, hex] of entries) { g.fillStyle = hex; g.fillRect((i % GRID) * cell, Math.floor(i / GRID) * cell, cell, cell); }
        const t = new THREE.CanvasTexture(c);
        t.flipY = base.flipY; t.colorSpace = base.colorSpace; t.magFilter = base.magFilter; t.minFilter = base.minFilter; t.generateMipmaps = base.generateMipmaps;
        m.map = t;
      }
      m.needsUpdate = true;
    });
  }

  _glowMap(map) {
    const img = map.image;
    const w = img.width, h = img.height, cell = Math.max(1, Math.round(w / GRID));
    const c = document.createElement('canvas');
    c.width = w; c.height = h;
    const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0);
    const src = g.getImageData(0, 0, w, h), out = g.createImageData(w, h);
    for (const s of this.glow) {
      const x0 = (s.index % GRID) * cell, y0 = Math.floor(s.index / GRID) * cell;
      for (let y = y0; y < y0 + cell; y++) for (let x = x0; x < x0 + cell; x++) {
        const i = (y * w + x) * 4;
        out.data[i] = src.data[i]; out.data[i + 1] = src.data[i + 1]; out.data[i + 2] = src.data[i + 2]; out.data[i + 3] = 255;
      }
    }
    // black (no emission) everywhere else
    for (let i = 0; i < out.data.length; i += 4) if (out.data[i + 3] === 0) out.data[i + 3] = 255;
    g.putImageData(out, 0, 0);
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.magFilter = THREE.NearestFilter;
    tex.minFilter = THREE.NearestFilter;
    tex.flipY = map.flipY;
    tex.generateMipmaps = false;
    return tex;
  }

  // ---- lights ----------------------------------------------------------------------------------------------------------------------------
  // The model's own lights come from its interactions file (models/<id>.interactions.json, positions in Blender space: glTF is (x, z, -y)). A light that is
  // `when: "on"` or "always" shines, a "door_open" one (the fridge) when a part is open, a one-off ("trigger") and a broken one (working: false) never.
  async _lights(root, asset, token) {
    if (!asset.interactions) return;
    let doc;
    try { doc = await (await fetch(asset.interactions)).json(); } catch (e) { console.warn('no interactions file', e); return; }
    if (token !== this._token) return;
    const size = Math.max(0.15, ...asset.size);
    for (const e of Object.values(doc.emitters || {})) {
      if (e.kind !== 'light' || e.working === false || e.when === 'trigger') continue;
      const colour = LIGHT_COLOURS[e.colour] || LIGHT_COLOURS.warm;
      const spot = e.shape === 'spot';
      const base = 3.2 * size * size * (e.intensity || 1);
      const light = spot ? new THREE.SpotLight(colour, base * 2, e.range, 0.9, 0.55, 2) : new THREE.PointLight(colour, base, e.range, 2);
      const [x, y, z] = e.position;
      light.position.set(x, z, -y);
      if (spot) { light.target.position.set(x, z - 1, -y); root.add(light.target); }
      root.add(light);
      this.lights.push({ light, base: light.intensity, flicker: !!e.flicker, when: e.when || 'on', phase: Math.random() * 10 });
    }
  }

  setLights(on) { this.lightsOn = on; this._applyLights(); }

  // Lights on: the room gets dim enough for them to show. Lights off: back to the even light the palette colours are judged in.
  _applyLights() {
    const dim = this.lightsOn && this.lights.length ? 0.28 : 1;
    for (const [l, v] of this.ambient) l.intensity = v * dim;
    const open = Object.values(this.parts).some((p) => p.target > 0.5);
    for (const l of this.lights) l.light.visible = this.lightsOn && (l.when !== 'door_open' || open);
  }

  // ---- moving parts ----------------------------------------------------------------------------------------------------------------------
  _parts(root, asset) {
    const defs = asset.parts || {};
    for (const [role, d] of Object.entries(defs)) {
      const node = root.getObjectByName(role);
      if (!node) continue;
      const axis = new THREE.Vector3(...d.axis).normalize();
      const rest = d.rest || 0;
      const st = { role, node, kind: d.kind, axis, limit: d.limit, rest, meshes: [], s: 0, target: 0 };
      if (d.kind === 'spin') {
        // a wheel: turns about its axis for as long as it is switched on (limit is one turn, 360, and does not matter here)
        st.baseQuat = node.quaternion.clone();
        st.angle = 0;
        st.s = st.target = 0;
      } else if (d.kind === 'hinge') {
        // the exported pose may already be a little open (the Damaged styles); take that out to get the shut pose, then s runs 0 (shut) .. 1 (open by `limit`)
        st.baseQuat = node.quaternion.clone().multiply(new THREE.Quaternion().setFromAxisAngle(axis, THREE.MathUtils.degToRad(-rest)));
      } else {
        st.basePos = node.position.clone().addScaledVector(axis, -rest);
      }
      if (d.kind !== 'spin') st.s = st.target = d.limit ? rest / d.limit : 0;
      node.traverse((o) => {
        if (!o.isMesh) return;
        o.material = o.material.clone(); // own material, so hovering one part does not light the whole model
        st.meshes.push(o);
      });
      node.userData.part = role;
      this.parts[role] = st;
    }
  }

  _applyPart(st) {
    const amount = st.limit * st.s;
    if (st.kind === 'spin') {
      st.node.quaternion.copy(st.baseQuat).multiply(new THREE.Quaternion().setFromAxisAngle(st.axis, st.angle));
    } else if (st.kind === 'hinge') {
      st.node.quaternion.copy(st.baseQuat).multiply(new THREE.Quaternion().setFromAxisAngle(st.axis, THREE.MathUtils.degToRad(amount)));
    } else {
      st.node.position.copy(st.basePos).addScaledVector(st.axis, amount);
    }
  }

  togglePart(role) {
    const st = this.parts[role];
    if (!st) return;
    st.target = st.target > 0.5 ? 0 : 1;
    this.onPartsChanged(this.partStates());
    this._applyLights();
  }

  setAllParts(open) {
    for (const st of Object.values(this.parts)) st.target = open ? 1 : 0;
    this.onPartsChanged(this.partStates());
    this._applyLights();
  }

  partStates() {
    return Object.values(this.parts).map((p) => ({ role: p.role, kind: p.kind, open: p.target > 0.5 }));
  }

  _partAt(ev) {
    if (!this.root || !Object.keys(this.parts).length) return null;
    const r = this.canvas.getBoundingClientRect();
    this.pointer.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
    this.ray.setFromCamera(this.pointer, this.camera);
    const hits = this.ray.intersectObject(this.root, true);
    for (const h of hits) {
      for (let o = h.object; o; o = o.parent) if (o.userData.part) return o.userData.part;
      if (h.object.userData.glass) continue; // a window on the body: look through it to the door or drawer behind
      return null; // the first thing hit was the body: a part behind it is not clickable
    }
    return null;
  }

  _bindPointer() {
    let down = null;
    this.canvas.addEventListener('pointerdown', (e) => { down = { x: e.clientX, y: e.clientY, t: performance.now() }; });
    this.canvas.addEventListener('pointerup', (e) => {
      if (!down) return;
      const moved = Math.hypot(e.clientX - down.x, e.clientY - down.y), dt = performance.now() - down.t;
      down = null;
      if (moved > 5 || dt > 500) return; // a drag, not a click
      const role = this._partAt(e);
      if (role) this.togglePart(role);
    });
    this.canvas.addEventListener('pointermove', (e) => {
      if (e.buttons || e.pointerType === 'touch') return;
      this._hoverPending = e;
    });
    this.canvas.addEventListener('pointerleave', () => { this._hoverPending = null; this._setHover(null); });
  }

  _setHover(role) {
    if (role === this.hover) return;
    const light = (r, v) => { const st = this.parts[r]; if (st) for (const m of st.meshes) m.material.color.setScalar(v); };
    if (this.hover) light(this.hover, 1);
    this.hover = role;
    if (role) light(role, 1.3);
    this.canvas.style.cursor = role ? 'pointer' : '';
    this.onHover(role);
  }

  // ---- clips -----------------------------------------------------------------------------------------------------------------------------
  _clips(gltf, asset) {
    if (!gltf.animations.length) return;
    this.mixer = new THREE.AnimationMixer(this.root);
    for (const clip of gltf.animations) this.actions[clip.name] = this.mixer.clipAction(clip);
    const first = this.actions.Idle ? 'Idle' : gltf.animations[0].name;
    this.setClip(first, 0);
    this.mixer.timeScale = this.speed;
  }

  setClip(name, fade = 0.25) {
    const next = this.actions[name];
    if (!next) return;
    const prev = this.clip ? this.actions[this.clip] : null;
    next.reset().play();
    if (prev && prev !== next) prev.crossFadeTo(next, fade, false);
    this.clip = name;
  }

  setSpeed(v) { this.speed = v; if (this.mixer) this.mixer.timeScale = this.playing ? v : 0; }
  setPlaying(on) { this.playing = on; if (this.mixer) this.mixer.timeScale = on ? this.speed : 0; }

  // ---- camera and floor ------------------------------------------------------------------------------------------------------------------
  _frameModel(asset) {
    const [w, h, d] = asset.size; // metres: width, height, depth
    const radius = Math.max(0.004, 0.5 * Math.hypot(w, h, d));
    // A static model is framed on its real bounds. A skinned one is posed by its rig, so three.js's box for it is not the model's: use the manifest's size,
    // with the rig's origin (the middle of the feet) on the floor.
    const box = new THREE.Box3().setFromObject(this.root);
    const centre = asset.rigged || box.isEmpty() ? new THREE.Vector3(0, h / 2, 0) : box.getCenter(new THREE.Vector3());
    const fov = THREE.MathUtils.degToRad(this.camera.fov);
    const fitH = radius / Math.sin(fov / 2);
    const fitW = radius / Math.sin(Math.atan(Math.tan(fov / 2) * Math.min(1, this.camera.aspect)));
    const dist = Math.max(fitH, fitW) * 1.05;
    const dir = new THREE.Vector3(0.7, 0.42, 1).normalize(); // the front faces +Z: look at it from the front, a little to the right and above
    this.camera.near = Math.max(0.0005, dist / 200);
    this.camera.far = dist * 40;
    this.camera.updateProjectionMatrix();
    this.camera.position.copy(centre).addScaledVector(dir, dist);
    this.controls.target.copy(centre);
    this.controls.minDistance = radius * 0.35;
    this.controls.maxDistance = radius * 10;
    this.controls.update();
    this._home = { pos: this.camera.position.clone(), target: centre.clone() };
  }

  resetView() {
    if (!this._home) return;
    this.camera.position.copy(this._home.pos);
    this.controls.target.copy(this._home.target);
    this.controls.update();
  }

  _groundShadow(asset) {
    const [w0, h0, d] = asset.size;
    const w = asset.rigged ? Math.min(w0, Math.max(d, h0 * 0.5)) : w0; // (a person's width is the T-pose's arms)
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const g = c.getContext('2d');
    const grad = g.createRadialGradient(64, 64, 4, 64, 64, 62);
    grad.addColorStop(0, 'rgba(0,0,0,0.38)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = grad;
    g.fillRect(0, 0, 128, 128);
    const tex = new THREE.CanvasTexture(c);
    const box = new THREE.Box3().setFromObject(this.root);
    const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }));
    mesh.rotation.x = -Math.PI / 2;
    const span = Math.max(w, d, 0.01) * 1.5;
    mesh.scale.set(span, span, 1);
    const c3 = asset.rigged || box.isEmpty() ? new THREE.Vector3() : box.getCenter(new THREE.Vector3());
    mesh.position.set(c3.x, (asset.rigged || box.isEmpty() ? 0 : Math.min(0, box.min.y)) + 0.002, c3.z);
    mesh.renderOrder = -1;
    this.shadow = mesh;
    this.scene.add(mesh);
  }

  // ---- loop ------------------------------------------------------------------------------------------------------------------------------
  _frame() {
    this._raf = requestAnimationFrame(this._frame);
    const dt = Math.min(this.clock.getDelta(), 0.1);
    if (this.mixer) this.mixer.update(dt);
    for (const st of Object.values(this.parts)) {
      if (st.kind === 'spin') {
        if (st.target > 0.5) {
          st.angle = (st.angle + dt * 6) % (Math.PI * 2); // about one turn a second, the way a wheel turns at walking pace
          this._applyPart(st);
        }
      } else if (st.s !== st.target) {
        const step = dt / 0.45; // a door takes about half a second
        st.s = st.s < st.target ? Math.min(st.target, st.s + step) : Math.max(st.target, st.s - step);
        this._applyPart(st);
      }
    }
    if (this.lights.length) {
      const t = performance.now() / 1000;
      for (const l of this.lights) if (l.flicker) l.light.intensity = l.base * (0.8 + 0.2 * Math.sin(t * 23 + l.phase) * Math.sin(t * 7.3 + l.phase * 2));
    }
    if (this._hoverPending) { this._setHover(this._partAt(this._hoverPending)); this._hoverPending = null; }
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }

  // A PNG of what the camera sees now (for the thumbnails: tools/thumbs.html).
  snapshot() {
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
    return this.canvas.toDataURL('image/png');
  }

  dispose() {
    cancelAnimationFrame(this._raf);
    this._ro.disconnect();
    this._clear();
    this.renderer.dispose();
  }
}
