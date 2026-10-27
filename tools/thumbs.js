// Renders every model in site/manifest.json with the same viewer the site uses (256 x 256, transparent) and POSTs the PNG to tools/thumb_server.py.
// Rigged models are frozen at the first frame of their Idle clip; moving parts are shut (or as exported).
import { Viewer } from '../site/viewer.js';
const doc = await (await fetch('../site/manifest.json')).json();
const only = new URLSearchParams(location.search).get('only');
const v = new Viewer(document.getElementById('c'), { glow: doc.palette.glow });
v.renderer.setPixelRatio(1);
v.resize();
const log = document.getElementById('log');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms)); // (not requestAnimationFrame: it does not fire while the browser pane is hidden)
let done = 0;
for (const a of doc.assets) {
  if (only && !only.split(',').includes(a.id)) continue;
  const asset = { ...a, glb: '../site/' + a.glb };
  // one canvas, so the models are rendered, saved and replaced one at a time
  await v.load(asset); // NOSONAR: one canvas, so the models are rendered one at a time
  v.setPlaying(false);
  if (v.mixer) v.mixer.update(0); // the Idle pose at time 0
  await sleep(50); // NOSONAR: lets the drawn frame settle before the snapshot
  const png = v.snapshot();
  const r = await fetch('/save/' + a.id, { method: 'POST', body: png }); // NOSONAR: saved one at a time, stopping at the first failure
  if (!r.ok) throw new Error('save failed for ' + a.id);
  log.textContent = `${++done} done: ${a.id}`;
}
log.textContent = `finished: ${done} thumbnails`;
document.title = 'DONE ' + done;
