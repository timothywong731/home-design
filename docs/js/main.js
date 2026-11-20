// House walkthrough viewer: three.js r180 via import map (no build step), relative URLs only.
// Frames: house/plan (x right, y into the house, z up) -> three (x, z, -y); see geom.js.
// Assets (blender/MULTILEVEL.md 10, 11.3): manifest schema 2 = one GLB per level (B G 1 2 X), loaded in `loadOrder`
// under one root, each lit and made operable as it arrives; schema 1 = home.glb as the only level G.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import * as G from './geom.js';
import { PlanView } from './plan2d.js';
import { initInteract } from './interact.js';

const LIBS = 'https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/libs/';
const EYE = 1.6, WALK = 1.4, RUN = 2.8, TURN = 1.9, FOV = 70, CUT = 2.2;
const GLIDE = 2.5, FOV_MIN = 22, FOV_MAX = 90, POINT_RANGE = 4;    // double-click walk speed, wheel zoom, pointing reach
const qs = new URLSearchParams(location.search);
const $ = (s) => document.querySelector(s);
const getJSON = (u) => fetch(u).then((r) => (r.ok ? r.json() : null)).catch(() => null);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), lerp = (a, b, t) => a + (b - a) * t;
const wrap = (a) => Math.atan2(Math.sin(a), Math.cos(a));
const touch = matchMedia('(pointer: coarse)').matches;
document.body.classList.toggle('touch', touch);

// The Blender scene is viewed (and its colours were tuned) through AgX with the look "Medium High Contrast"
// (blender/lib/lighting.py). three's AgX has no looks and its sigmoid is a looser fit that lifts the darks, so a
// contrast of 1.2 about 0.69 is applied in its log space, just before the sigmoid. Constants fitted to Blender's OCIO
// output (greys 0.01..4: rms display error 0.047 -> 0.013). ?look=none shows three's plain AgX.
if (qs.get('look') !== 'none') {
  const SIG = 'color = agxDefaultContrastApprox( color );', src = THREE.ShaderChunk.tonemapping_pars_fragment;
  THREE.ShaderChunk.tonemapping_pars_fragment = src.replace(SIG, 'color = agxDefaultContrastApprox( clamp( ( color - 0.69 ) * 1.2 + 0.69, 0.0, 1.0 ) );');
  if (!src.includes(SIG)) console.warn('three.js AgX shader changed: contrast look not applied');
}

// ---------- renderer / scene ----------
const canvas = $('#scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
const phone = touch || Math.min(screen.width, screen.height) < 600;      // phones: 1.5x pixels at most (fill rate, memory)
renderer.setPixelRatio(Math.min(devicePixelRatio, phone ? 1.5 : 2));
renderer.setSize(innerWidth, innerHeight, false);
const scene = new THREE.Scene();
// walk: the sky as Cycles shows it (manifest.sky: an equirect image, or a colour); dollhouse: neutral
let SKY = new THREE.Color(0x296c97);
const DARK = new THREE.Color(0x15181b);
scene.background = SKY;
const camera = new THREE.PerspectiveCamera(FOV, innerWidth / innerHeight, 0.05, 150);
camera.rotation.order = 'YXZ';
const pmrem = new THREE.PMREMGenerator(renderer);
const roomEnv = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
const texLoader = new THREE.TextureLoader();

// ---------- loading screen ----------
const bar = $('#bar'), msg = $('#loader-msg'), chip = $('#chip');
// Over the first view (manifest.firstView: the first GLB, its level's lightmaps and probes, the json): the GLB's bytes as
// they stream, then each baked image as it arrives ("Loading lighting"). No firstView: the GLB alone.
const load = { glb: 0, glbTotal: 0, tex: 0, done: false };
function progress(loaded = load.glb, total = load.glbTotal) {
  Object.assign(load, { glb: loaded, glbTotal: total });
  const all = load.first || total, got = loaded + load.tex, mb = (got / 1048576).toFixed(1);
  const known = all > 0 && got <= all * 1.02;           // gzip on Pages can make loaded > total
  bar.parentElement.classList.toggle('indet', !known);
  if (known) bar.style.width = `${Math.min(100, (100 * got) / all)}%`;
  const what = total > 0 && loaded >= total && load.first ? 'Loading lighting' : 'Loading model';
  msg.textContent = known ? `${what} ${Math.round(Math.min(100, (100 * got) / all))}% · ${mb} MB` : `${what} · ${mb} MB`;
}

msg.textContent = 'Loading plan…';
const [manifest, house, planJson, foot, renders] = await Promise.all(
  ['assets/manifest.json', 'assets/house.json', 'assets/plan.json', 'assets/footprints.json', 'renders/index.json'].map(getJSON));
const schema2 = Array.isArray(manifest?.levels) && manifest.levels.length > 0;
const LEVELS = schema2 ? manifest.levels : [{ id: 'G', name: 'Ground floor', datumZ: 0, cutZ: CUT, glb: 'home.glb' }];
const level = (id) => LEVELS.find((l) => l.id === id);
const ORDER = [...new Set([...(schema2 && manifest.loadOrder || []), ...LEVELS.map((l) => l.id)])].filter(level);
const levelName = (id) => level(id)?.name || house?.levels?.find((l) => l.id === id)?.name || (id === 'X' ? 'Outside' : id);
const realtime = qs.get('lighting') === 'realtime' || !manifest?.lightmaps?.length;
const bakedBytes = new Map([...(manifest?.lightmaps || []), ...(manifest?.probes || [])].map((e) => [e.image, e.bytes || 0]));
if (!realtime && manifest?.firstView?.bytes && schema2) {   // what is not the GLB or a baked image (the json) is already here
  const fv = manifest.firstView, glb = LEVELS.find((l) => fv.files?.includes(l.glb));
  load.first = fv.bytes; load.tex = Math.max(0, fv.bytes - (glb?.bytes || 0) - (fv.files || []).reduce((n, f) => n + (bakedBytes.get(f) || 0), 0));
}
const CIRCUITS = realtime ? [] : manifest?.circuits || [];       // rooms with several lighting circuits (INTERACT.md)
const sky = manifest?.sky;
if (typeof sky === 'string') SKY.set(sky); else if (sky?.color) SKY.set(sky.color);    // schema 1: a hex string
if (sky?.image) texLoader.loadAsync('assets/' + sky.image).then((t) => {   // displayed 8-bit image: not tone-mapped
  Object.assign(t, { mapping: THREE.EquirectangularReflectionMapping, colorSpace: THREE.SRGBColorSpace });
  SKY = t; if (S.mode === 'walk') scene.background = t;
}).catch(() => console.warn('sky image missing:', sky.image));
// Lamps, lit shades and LED strips are authored warm for the 3000 K white balance of the Cycles view. The bake has
// that balance multiplied in; emissive colours come unbalanced in the GLB, so the same matrix is applied here.
if (!realtime && manifest?.whiteBalance) {
  const M = manifest.whiteBalance, col = (j) => `vec3( ${M.map((r) => r[j].toFixed(5)).join(', ')} )`;
  THREE.ShaderChunk.emissivemap_fragment += `\ntotalEmissiveRadiance = max( mat3( ${col(0)}, ${col(1)}, ${col(2)} ) * totalEmissiveRadiance, vec3( 0.0 ) );\n`;
}
const rooms = (manifest?.rooms || planJson?.rooms || house?.rooms || []).map((r) => ({ id: r.id, name: r.name || r.id, polygon: r.polygon,
  ceilZ: r.ceilZ ?? r.ceilingZ ?? 2.9, floorZ: r.floorZ ?? 0, level: r.level ?? G.levelOf(house, r.id), kind: r.kind ?? (G.PSEUDO_ROOMS.includes(r.id) ? 'site' : 'room') }));
const isExterior = (id) => { const r = rooms.find((q) => q.id === id); return r ? ['site', 'exterior'].includes(r.kind) : G.PSEUDO_ROOMS.includes(id); };
const walk = house ? G.buildWalk(house, { obstacles: G.obstaclesFrom(foot, false, house), soft: G.obstaclesFrom(foot, true, house) }) : null;
const hasLayer = (L) => !walk || walk.layers.includes(L);
const spawnLayer = G.layerOfLevel(manifest?.spawn?.level || 'G');
const spawn = { pos: (manifest?.spawn?.pos || house?.spawn || G.centroid(rooms[0]?.polygon || [[0, 1]])).slice(0, 2),
  yaw: ((manifest?.spawn?.yaw ?? 0) * Math.PI) / 180, layer: hasLayer(spawnLayer) ? spawnLayer : walk.layers[0] };   // yaw: degrees, 0 = +Y, CCW
const vps = walk ? G.viewpoints(walk, spawn)
  : Object.fromEntries(rooms.map((r) => [r.id, { pos: G.centroid(r.polygon), yaw: 0, layer: 'G' }]));
// hand-framed room-jump views from the export (first hero still of each room), snapped to walkable floor of the room's
// layer; the room holding the spawn point keeps the spawn view
const spawnRoom = walk && G.cellAt(walk, spawn.layer, ...spawn.pos)?.room;
for (const [id, v] of Object.entries((walk && manifest?.viewpoints) || {})) {
  const vp = vps[id], p = vp && spawnRoom !== id ? G.nearestFree(walk, vp.layer, v.pos[0], v.pos[1], 0.6) : null;
  if (p && G.cellAt(walk, vp.layer, ...p)?.room === id) vps[id] = { pos: p, yaw: G.dirYaw(v.look[0] - p[0], v.look[1] - p[1]), layer: vp.layer };
}

const TM = { agx: THREE.AgXToneMapping, neutral: THREE.NeutralToneMapping, aces: THREE.ACESFilmicToneMapping, none: THREE.NoToneMapping };
renderer.toneMapping = TM[qs.get('tm') || manifest?.toneMapping] ?? THREE.AgXToneMapping;
renderer.toneMappingExposure = +(qs.get('exposure') || manifest?.exposure || 1.0);

// ---------- model: one root, one scene per level ----------
const draco = new DRACOLoader().setDecoderPath(LIBS + 'draco/gltf/');
const ktx2 = new KTX2Loader().setTranscoderPath(LIBS + 'basis/').detectSupport(renderer);
const loader = new GLTFLoader().setDRACOLoader(draco).setKTX2Loader(ktx2).setMeshoptDecoder(MeshoptDecoder);
const root = new THREE.Group();
root.name = 'house'; scene.add(root);
const levelScenes = new Map(), meshes = [], byName = new Map();
const maxAniso = Math.min(8, renderer.capabilities.getMaxAnisotropy());
const mapMats = (o, f) => (Array.isArray(o.material) ? o.material.map(f) : f(o.material));
const drawDown = (im, max) => {        // an image drawn down to `max` px on its long side (a canvas), or itself
  const s = max / Math.max(im.width, im.height);
  if (s >= 1) return im;
  const c = Object.assign(document.createElement('canvas'), { width: Math.round(im.width * s), height: Math.round(im.height * s) });
  c.getContext('2d').drawImage(im, 0, 0, c.width, c.height);
  return c;
};
// GLB textures: the export writes an image into every level GLB that uses it, so the same picture arrives up to five
// times; one THREE.Texture per image name + size (+ sampling) serves every level. Phones (coarse pointer or a small
// screen) get colour maps over 512 px drawn down before upload. Unnamed images are never merged.
const TEX_SLOTS = ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap'];
const sharedTex = new Map();
function shareTextures(m) {
  for (const k of TEX_SLOTS) {
    const t = m[k], im = t?.image;
    if (!im) continue;
    const key = t.name && [t.name, im.width, im.height, t.colorSpace, t.wrapS, t.wrapT, t.channel, t.flipY, ...t.offset, ...t.repeat, t.rotation].join('|');
    const s = key && sharedTex.get(key);
    if (s) { m[k] = s; continue; }
    if (phone && (k === 'map' || k === 'emissiveMap') && Math.max(im.width, im.height) > 512) { t.image = drawDown(im, 512); t.needsUpdate = true; }
    t.anisotropy = maxAniso;
    if (key) sharedTex.set(key, t);
  }
}
function prepare(model) {
  const mine = [];
  model.traverse((o) => o.isMesh && mine.push(o));
  for (const o of mine) mapMats(o, (m) => {
    shareTextures(m);
    if (/glass|glaz/i.test(m.name) || m.transmission > 0) {
      // The export's glass is already alpha-blended (clear = 10 % mirror, frosted/obscure/dark keep their own alpha):
      // leave it alone. Only opaque or transmissive glass from elsewhere is turned into cheap see-through glass.
      if (m.transmission > 0 || !m.transparent) {
        if (m.isMeshPhysicalMaterial) m.transmission = 0;
        Object.assign(m, { transparent: true, opacity: Math.min(m.opacity, 0.22), roughness: Math.min(m.roughness, 0.08), metalness: 0 });
      }
      m.depthWrite = false; o.userData.glass = true; o.renderOrder = 2;
    }
    return m;
  });
  model.traverse((o) => { for (const n of [o.userData.name, o.name]) if (n && !byName.has(n)) byName.set(n, o); });   // names are unique across levels
  meshes.push(...mine);
  model.updateMatrixWorld(true);
  for (const o of mine) {
    if (o.userData.glass) glazed.add((o.userData.name || o.parent?.userData.name || '').split('.')[1]);   // <room>.<door>.leaf.glass, .frame.glass
    const rs = cullRooms(o);
    if (rs) cullList.push({ o, rs });
    if (o.userData.ix || o.parent?.userData.ix) continue;     // what the dollhouse may hide (never a tagged object: interact.js owns their visibility)
    const room = o.userData.room ?? o.parent?.userData.room, name = o.userData.name || o.parent?.userData.name || '';
    dhBox.setFromObject(o);
    dhMeshes.push(dhEntry(o, room, dhBox.min.y, dhBox.max.y, /\.ceiling$/.test(name) ? rooms.find((r) => r.id === room)?.level ?? null : null));
  }
  cullKey = null;
  return mine;
}
// the dollhouse levels whose cut hides a mesh: wholly above the cut, roof rising over the level, a ceiling of the level
const dhMeshes = [], dhBox = new THREE.Box3();
const dhEntry = (o, room, minY, maxY, ceil) => ({ o, room, minY, maxY, hide: new Set(LEVELS.filter((l) => minY > (l.cutZ ?? CUT) || (room === 'roof' && maxY > (l.datumZ ?? 0) + 1.2) || ceil === l.id).map((l) => l.id)) });

// ---------- static batching: the untagged, opaque, non-emissive meshes of one room sharing one (baked) material and
// one dollhouse rule are drawn as one world-space mesh. The originals stay for rays and names, never drawn (layer mask 0).
let nBatch = 0;
function batch(model, mine) {
  const tagged = (o) => { for (; o; o = o.parent) if (typeof o.userData.ix === 'string') return true; return false; };
  const dh = new Map(dhMeshes.map((d) => [d.o, d])), cu = new Map(cullList.map((c) => [c.o, c])), groups = new Map();
  for (const o of mine) {
    const m = o.material, g = o.geometry, d = dh.get(o);
    if (Array.isArray(m) || m.transparent || o.userData.glass || !d || tagged(o) || (m.emissive && m.emissive.r + m.emissive.g + m.emissive.b > 0 && m.emissiveIntensity > 0)) continue;
    const key = [d.room, m.uuid, Object.keys(g.attributes).sort().join(), !!g.index, [...d.hide].join(''), cu.has(o)].join('|');
    (groups.get(key) || groups.set(key, []).get(key)).push(o);
  }
  for (const list of groups.values()) {
    if (list.length < 2) continue;
    const geos = list.map((o) => {
      const g = o.geometry, out = new THREE.BufferGeometry(), n = g.attributes.position.count;
      for (const [k, a] of Object.entries(g.attributes)) {
        const arr = new Float32Array(n * a.itemSize);
        for (let i = 0; i < n; i++) for (let j = 0; j < a.itemSize; j++) arr[i * a.itemSize + j] = a.getComponent(i, j);
        out.setAttribute(k, new THREE.BufferAttribute(arr, a.itemSize));
      }
      if (g.index) {                    // a mirrored object: flip the winding, the world matrix will no longer do it
        const ix = Array.from(g.index.array);
        if (o.matrixWorld.determinant() < 0) for (let t = 0; t < ix.length; t += 3) [ix[t + 1], ix[t + 2]] = [ix[t + 2], ix[t + 1]];
        out.setIndex(ix);
      }
      return out.applyMatrix4(o.matrixWorld);
    });
    const o0 = list[0], d0 = dh.get(o0), b = new THREE.Mesh(mergeGeometries(geos), o0.material);
    b.name = `batch_${nBatch}`; Object.assign(b.userData, { name: `${d0.room}.batch.${nBatch++}`, room: d0.room, baked: o0.userData.baked, lm: 'static', batch: list.length });
    b.castShadow = o0.castShadow; b.receiveShadow = o0.receiveShadow;
    model.add(b); b.updateMatrixWorld(true);
    const rs = new Set(list.flatMap((o) => cu.get(o)?.rs || []));
    for (const o of list) { o.layers.mask = 0; const c = cu.get(o); if (c) cullList.splice(cullList.indexOf(c), 1); }
    if (cu.has(o0)) cullList.push({ o: b, rs: [...rs] });
    const bb = new THREE.Box3().setFromObject(b); dhMeshes.push({ o: b, room: d0.room, minY: bb.min.y, maxY: bb.max.y, hide: d0.hide });
  }
  cullKey = null;
}

// ---------- walk-mode culling: only the rooms seen through the openings in view are drawn (geom.js sightGraph) ----------
// A mesh belongs to its room, to both rooms of the opening its name names (<room>.<opening>.lining / .leaf / .frame), to
// every room its centre stands in, else (outside every room) to the outdoors. Culled meshes leave camera layer 0 only:
// `visible` stays the dollhouse's and interact.js's, and rays (castRay calls raycast directly) still hit them.
const sight = walk && G.sightGraph(house), cullList = [], glazed = new Set();
let cullKey = null, CULL = qs.get('cull') !== 'off';
const cc = new THREE.Vector3();
function cullRooms(o) {
  const room = o.userData.room ?? o.parent?.userData.room, name = o.userData.name || o.parent?.userData.name || '';
  if (!sight?.nodes.has(room)) return null;                      // no room / not in the graph: always drawn
  const rs = new Set([room, ...(sight.ends.get(name.split('.')[1]) || [])]);
  dhBox.setFromObject(o).getCenter(cc);
  const [x, y] = G.threeToPlan(cc), top = (r) => (r.kind === 'room' || r.kind === 'stairwell' || r.kind === 'void' ? Math.max(r.ceilZ, r.floorZ + 2.2) : r.floorZ + 15);
  // rooms its box (3 cm in) reaches into: a corner or the centre in the room, or a room corner in the box
  const b = dhBox.expandByScalar(-0.03), X0 = b.min.x, X1 = b.max.x, Y0 = -b.max.z, Y1 = -b.min.z;
  const pts = [[x, y], [X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]];
  const meets = (r) => r.polygon && b.max.y > r.floorZ - 0.3 && b.min.y < top(r) + 0.3
    && (pts.some((p) => G.pointInPoly(p[0], p[1], r.polygon)) || r.polygon.some((p) => p[0] > X0 && p[0] < X1 && p[1] > Y0 && p[1] < Y1));
  const inside = rooms.filter(meets);
  const near = inside.length ? inside : rooms.filter((r) => r.polygon && cc.y > r.floorZ - 0.3 && cc.y < top(r) + 0.3 && G.edgeDist(x, y, r.polygon) < 0.35);
  for (const r of near) rs.add(r.id);
  if (!near.length) rs.add('facade');
  return [...rs].every((r) => sight.nodes.has(r)) ? [...rs] : null;
}
const pj = new THREE.Vector3();
function viewRect(b, rect) {           // plan box -> its NDC rectangle inside rect; rect when it reaches behind the eye
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, behind = 0;
  for (let k = 0; k < 8; k++) {
    pj.set(k & 1 ? b[3] : b[0], k & 4 ? b[5] : b[2], -(k & 2 ? b[4] : b[1])).applyMatrix4(camera.matrixWorldInverse);
    if (pj.z > -camera.near) { behind++; continue; }
    pj.applyMatrix4(camera.projectionMatrix);
    x0 = Math.min(x0, pj.x); x1 = Math.max(x1, pj.x); y0 = Math.min(y0, pj.y); y1 = Math.max(y1, pj.y);
  }
  if (behind === 8) return null;
  if (behind) return rect;
  const r = [Math.max(rect[0], x0), Math.min(rect[1], x1), Math.max(rect[2], y0), Math.min(rect[3], y1)];
  return r[0] < r[1] && r[2] < r[3] ? r : null;
}
// Every frame in walk mode: the rooms seen and the rectangles they are seen through; a mesh is drawn when its bounding
// sphere's screen box meets a rectangle of one of its rooms and covers more than a pixel. Off (dollhouse, ?cull=off):
// everything on layer 0 again.
let seen = null;
const csph = new THREE.Sphere(), vc = new THREE.Vector3();
function cull() {
  const shut = CULL && ix.shut();      // a shut solid door is opaque; glazing (a leaf or its transom) is not
  seen = CULL && S.mode === 'walk' && sight && S.room
    ? (camera.updateMatrixWorld(), G.seenRooms(sight, S.room.id, (b, r, e) => (e.door && shut.has(e.door) && !glazed.has(e.door) ? null : viewRect(b, r)))) : null;
  if (!seen) {
    if (cullKey !== '') { cullKey = ''; for (const c of cullList) c.o.layers.mask = 1; }
    return;
  }
  cullKey = 'on';
  // NDC radius of 0.75 px; 1.5 px for what is seen through an opening (a knob across the hall, a pot in the garden)
  const P = camera.projectionMatrix.elements, V = camera.matrixWorldInverse, px = 2 / renderer.domElement.height, here = S.room.id;
  for (const c of cullList) {
    const g = c.o.geometry;
    if (!g.boundingSphere) g.computeBoundingSphere();
    csph.copy(g.boundingSphere).applyMatrix4(c.o.matrixWorld); vc.copy(csph.center).applyMatrix4(V);
    const r = csph.radius, d = -vc.z, across = d - r < camera.near;
    let x0 = -1, x1 = 1, y0 = -1, y1 = 1, vis = false;
    if (!across) {                      // screen box of the sphere's view-space box (depths d - r .. d + r)
      if ((r / d) * P[5] < (c.rs.includes(here) ? 0.75 : 1.5) * px) { c.o.layers.mask = 0; continue; }
      const lo = (a) => (a >= 0 ? a / (d + r) : a / (d - r)), hi = (a) => (a >= 0 ? a / (d - r) : a / (d + r));
      x0 = P[0] * lo(vc.x - r); x1 = P[0] * hi(vc.x + r); y0 = P[5] * lo(vc.y - r); y1 = P[5] * hi(vc.y + r);
    }
    for (let i = 0; i < c.rs.length && !vis; i++) for (const q of seen.get(c.rs[i]) || []) if (q[0] < x1 && q[1] > x0 && q[2] < y1 && q[3] > y0) { vis = true; break; }
    c.o.layers.mask = vis ? 1 : 0;
  }
}
const findNode = (n) => byName.get(n) || byName.get(THREE.PropertyBinding.sanitizeNodeName(n));

// ---------- lighting ----------
// Baked lighting, per mesh:
//  - lightmap (objects listed in the manifest): manifest intensity = linear scale of the 8-bit image
//    (linear = srgbDecode(px) * intensity) of a Cycles DIFFUSE direct+indirect bake (white-Lambert radiance). three's
//    lightMap is irradiance (divided by PI in the BRDF) -> * PI. Second UV set, flipY false.
//  - room probe (equirect, centre = +X) as envMap on EVERY mesh: all the light of meshes without a lightmap, but
//    reflections only on lightmapped ones (their diffuse light is already in the lightmap -> IBL irradiance removed).
//  - light switches: each lightmapped material mixes its room's lights-on map with the lights-off map (manifest
//    lightmapsOff, loaded on the first switch use; until then the on-map at 12 %) by the room's lmOn uniform.
//  - lmMix (1 = bake): a baked door leaf / front that moves away from its modelled pose fades from its lightmap to the
//    probe's diffuse light (interact.js), since the bake only fits the pose it was baked in; lmProbe scales that probe
//    light to the brightness the bake gave the leaf (an exterior leaf would jump to its room's brighter probe).
//  - circuits (rooms with several, manifest.circuits): one atlas per circuit holding its lamps' light alone; with some
//    circuits lit the off slot shows lights-off + the lit circuits, and lmOn = the product of the circuit states, so the
//    lights-on atlas shows only while every circuit is lit (INTERACT.md, Circuits).
const IBL_DIFFUSE = 'iblIrradiance += getIBLIrradiance( geometryNormal );', LM_LINE = 'vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;';
// A room partly lit (circuits): A = lights-off + the lit circuits (darker than their share where the bake's circuits sum
// short of the lights-on bake), B = lights-on less the unlit circuits (exactly their share); the lit share s moves A -> B,
// so all off is the lights-off bake, all on the lights-on one, and switching anything off never brightens (B >= A, the
// lights-on bake caps it) - IX-01's safety net, whatever the bake.
const lmChunk = (K) => THREE.ShaderChunk.lights_fragment_maps.replace(IBL_DIFFUSE, 'iblIrradiance += ( 1.0 - lmMix ) * lmProbe * getIBLIrradiance( geometryNormal );')
  .replace(LM_LINE, !K ? 'vec3 lightMapIrradiance = lmMix * mix( texture2D( lightMapOff, vLightMapUv ).rgb * lightMapOffIntensity, lightMapTexel.rgb * lightMapIntensity, lmOn );'
    : 'vec3 lmOnT = lightMapTexel.rgb * lightMapIntensity, lmOff = texture2D( lightMapOff, vLightMapUv ).rgb * lightMapOffIntensity, lmA = lmOff, lmB = lmOnT; float lmS = 0.0;\n'
    + Array.from({ length: K }, (_, i) => `{ vec3 c = lmC${i}K * texture2D( lmC${i}, vLightMapUv ).rgb; lmA += lmC${i}On * c; lmB -= ( 1.0 - lmC${i}On ) * c; lmS += lmC${i}On * lmC${i}S; }\n`).join('')
    + 'vec3 lightMapIrradiance = lmMix * mix( min( mix( lmA, max( lmA, lmB ), clamp( lmS, 0.0, 1.0 ) ), max( lmOnT, lmOff ) ), lmOnT, lmOn );');
const SPEC_ONLY_CHUNK = lmChunk(0);
if (SPEC_ONLY_CHUNK.includes(IBL_DIFFUSE)) console.warn('three.js shader changed: lightmapped surfaces are lit twice');
if (!SPEC_ONLY_CHUNK.includes('lmOn')) console.warn('three.js shader changed: light switches cannot dim the bake');
const specOnly = (sh, K = 0) => {
  sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_maps>', K ? lmChunk(K) : SPEC_ONLY_CHUNK)
    .replace('#include <lightmap_pars_fragment>', '#include <lightmap_pars_fragment>\nuniform sampler2D lightMapOff;\nuniform float lightMapOffIntensity;\nuniform float lmOn;\nuniform float lmMix;\nuniform float lmProbe;'
      + Array.from({ length: K }, (_, i) => `\nuniform sampler2D lmC${i};\nuniform float lmC${i}K;\nuniform float lmC${i}On;\nuniform float lmC${i}S;`).join(''));
};
// Per-room light state shared by the bake materials (lmOn, the lights-off map), probe reflections, realtime lamps and
// lamp emissives; interact.js eases `on` toward `target`. ratio / pratio = brightness of the lights-off lightmap /
// probe relative to the lights-on one; wait > 0 holds the fade while the lights-off images load. A room with several
// circuits has `circuits` [{name, groups, share, emissive, on, target, x, tex, k, ems}], each eased on its own; then
// `target` = 1 while any circuit is lit and `on` = the product of the circuit states.
const roomLights = new Map();
const roomLight = (id) => roomLights.get(id) || roomLights.set(id, { on: { value: 1 }, target: 1, ratio: 0.12, mats: [], lamps: [], ems: [],
  uOff: { value: null }, uOffK: { value: 0 }, bright,
  circuits: CIRCUITS.filter((c) => c.room === id).map((c) => ({ ...c, emissive: new Set(c.emissive || []), on: { value: 1 }, target: 1, x: 1, tex: { value: null }, k: { value: 0 }, ems: [] })) }).get(id);
// light of a room relative to all lamps on, for its probe-lit objects: lights-off probe + the lit share of the lamps
function bright() {
  const r = this.pratio ?? this.ratio, cs = this.circuits;
  return r + (1 - r) * (cs.length ? cs.reduce((s, c) => s + (c.share ?? 1 / cs.length) * c.on.value, 0) : this.on.value);
}
const lightF = (L) => L.bright();
function meanLinear(img) {             // mean linear value of an 8-bit sRGB image, from a 32x32 thumbnail
  const c = Object.assign(document.createElement('canvas'), { width: 32, height: 32 }), g = c.getContext('2d', { willReadFrequently: true });
  g.drawImage(img, 0, 0, 32, 32);
  const d = g.getImageData(0, 0, 32, 32).data; let s = 0;
  for (let i = 0; i < d.length; i += 4) for (let j = 0; j < 3; j++) { const v = d[i + j] / 255; s += v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }
  return s / (d.length * 0.75);
}
const ratioOf = (a, ka, b, kb) => Math.min(1, Math.max(0.01, (meanLinear(a.image) * ka) / Math.max(1e-6, meanLinear(b.image) * kb)));
const texCache = new Map();
// once per file. Phones (or under 4 GB of memory) draw an atlas down to 1024 px and a probe to 512 on load: a quarter
// of the decoded memory each (its PMREM copy too), which is what keeps the WebGL context alive there.
const smallTex = phone || navigator.deviceMemory <= 4;
function loadTex(u, atlas = false) {
  if (!texCache.has(u)) texCache.set(u, texLoader.loadAsync('assets/' + u).then((t) => {
    if (!load.done) { load.tex += bakedBytes.get(u) || 0; progress(); }
    if (smallTex) t.image = drawDown(t.image, atlas ? 1024 : 512);
    if (atlas) Object.assign(t, { channel: 1, flipY: false, colorSpace: THREE.SRGBColorSpace, anisotropy: maxAniso });
    else Object.assign(t, { mapping: THREE.EquirectangularReflectionMapping, colorSpace: THREE.SRGBColorSpace });
    return t;
  }).catch(() => (console.warn('baked image missing:', u), null)));
  return texCache.get(u);
}
function syncOff(L) {                  // lights-off map + ratios from whatever of the room has arrived so far
  if (L.lm) {
    if (L.off) { L.uOff.value = L.off.tex; L.uOffK.value = L.off.k; L.ratio = ratioOf(L.off.tex, L.off.k, L.lm.tex, L.lm.k); }
    else { L.uOff.value = L.lm.tex; L.uOffK.value = L.lm.k * 0.12; }
  }
  if (L.probe && L.probeOff) L.pratio = ratioOf(L.probeOff.tex, L.probeOff.k, L.probe.tex, L.probe.k);
}
// first use of a switch: load the lights-off lightmap and probe (and the circuit atlases) of the rooms it controls; the
// fade waits for them
function ensureOff(ids) {
  if (realtime) return;
  for (const id of ids) {
    const L = roomLight(id);
    if (L.offP) continue;
    const lmo = (manifest.lightmapsOff || []).find((q) => q.room === id), pro = (manifest.probesOff || []).find((q) => q.room === id);
    L.wait = (L.wait || 0) + 1;
    L.offP = Promise.all([lmo && loadTex(lmo.image, true), pro && loadTex(pro.image), ...L.circuits.map((c) => loadTex(c.image, true))]).then(([t, pt, ...cs]) => {
      if (t) L.off = { tex: t, k: Math.PI * (lmo.intensity ?? 1) };
      if (pt) L.probeOff = { tex: pt, k: pro.intensity ?? 1 };
      cs.forEach((ct, i) => { const c = L.circuits[i]; if (ct) { c.tex.value = ct; c.k.value = Math.PI * (c.intensity ?? 1); } });
      syncOff(L);
    }).finally(() => { L.wait--; });
  }
}
// rooms that start with their lights off (the eaves: kind void, looked into through a hatch; eaves.md 8), set before
// their level is lit. The lights-off images still load on the first switch use: until then the off slot shows the
// lights-on atlas at 12 % (syncOff), dark enough for a void seen through a hatch.
function startOff(id) {
  const L = roomLight(id);
  L.target = L.x = L.on.value = 0;
  for (const c of L.circuits) c.target = c.x = c.on.value = 0;
}
// probe of a mesh: its room's; else the nearest of the same exterior-ness (level X and kind-exterior rooms choose
// among front / side_passage / garden / shed / balcony, all others among the interior probes)
const probeList = (manifest?.probes || []).map((p) => ({ ...p, rm: rooms.find((r) => r.id === p.room), ext: isExterior(p.room) })).filter((p) => p.rm);
const box = new THREE.Box3(), v3 = new THREE.Vector3(), matCache = new Map();
function probeFor(o, lv) {
  const id = o.userData.room ?? o.parent?.userData.room, own = probeList.find((p) => p.room === id);
  if (own) return own;
  const ext = lv === 'X' || isExterior(id);
  let cands = probeList.filter((p) => p.ext === ext);
  if (!cands.length) cands = probeList;
  if (!cands.length) return null;
  box.setFromObject(o).getCenter(v3);
  const [x, y] = G.threeToPlan(v3), z = v3.y, d = (p) => Math.hypot(p.pos[0] - x, p.pos[1] - y, (p.pos[2] ?? 1.5) - z);
  return cands.find((p) => G.pointInPoly(x, y, p.rm.polygon) && z > p.rm.floorZ - 0.5 && z < Math.max(p.rm.ceilZ ?? 0, p.rm.floorZ + 3) + 0.5)
    || cands.reduce((a, b) => (d(a) < d(b) ? a : b));
}
async function applyBake(lv, mine) {
  const lmOf = new Map(); let missing = 0, nouv = 0;          // mesh -> { tex, k, L }
  await Promise.all((manifest.lightmaps || []).filter((lm) => (lm.level ?? 'G') === lv).map(async (lm) => {
    const tex = await loadTex(lm.image, true);
    if (!tex) return;
    const k = Math.PI * (lm.intensity ?? 1), L = roomLight(lm.room);
    L.lm = { tex, k }; syncOff(L);
    for (const n of lm.objects || []) {
      const node = findNode(n);
      if (!node) { missing++; continue; }
      node.traverse((o) => {
        if (!o.isMesh) return;
        if (o.geometry.attributes.uv1) lmOf.set(o, { tex, k, L }); else nouv++;
      });
    }
  }));
  if (missing) console.warn(`${missing} lightmapped object names not found in the GLB`);
  if (nouv) console.warn(`${nouv} lightmapped meshes have no second UV set (uv1)`);
  const need = new Map(mine.map((o) => [o, probeFor(o, lv)]));
  const texs = new Map(await Promise.all([...new Set(need.values())].filter(Boolean).map(async (p) => [p, await loadTex(p.image)])));
  for (const o of mine) {
    const lm = lmOf.get(o), p = need.get(o), ptex = p && texs.get(p), env = ptex || roomEnv, k = ptex ? p.intensity ?? 1 : 0.6;
    const Lp = ptex ? roomLight(p.room) : null;
    if (Lp && !Lp.probe) { Lp.probe = { tex: ptex, k }; syncOff(Lp); }
    o.material = mapMats(o, (m) => {
      const key = m.uuid + env.uuid + (lm ? lm.tex.uuid : '');
      if (!matCache.has(key)) {
        const c = Object.assign(m.clone(), { envMap: env, envMapIntensity: Lp ? k * lightF(Lp) : k });
        if (lm) {
          const u = { lightMapOff: lm.L.uOff, lightMapOffIntensity: lm.L.uOffK, lmOn: lm.L.on, lmMix: { value: 1 }, lmProbe: { value: 1 } }, K = lm.L.circuits.length;
          lm.L.circuits.forEach((cc, i) => Object.assign(u, { [`lmC${i}`]: cc.tex, [`lmC${i}K`]: cc.k, [`lmC${i}On`]: cc.on, [`lmC${i}S`]: { value: cc.share ?? 1 / K } }));
          Object.assign(c, { lightMap: lm.tex, lightMapIntensity: lm.k, onBeforeCompile: (sh) => { specOnly(sh, K); Object.assign(sh.uniforms, u); } });
          if (K) c.customProgramCacheKey = () => `lm-circuits-${K}`;    // same function text, other shader: keep programs apart
        }
        if (m.name === 'mirror' && ptex && p.rm?.polygon && qs.get('box') !== 'off') boxProject(c, p);
        if (Lp) Lp.mats.push({ m: c, k });
        matCache.set(key, c);
      }
      return matCache.get(key);
    });
    o.userData.baked = !!lm;        // not "lm": the GLB extras already use userData.lm = 'static' | 'dynamic'
  }
}

// Mirrors: the room probe, parallax-corrected - a reflected ray is followed to the room's box (plan bounds, floor to
// ceiling) and the probe is read toward that point from where it was taken, so the hall mirror shows the stair and the
// newel where they are instead of a magnified blur of whatever lies that way from the middle of the hall.
const BOX_LINE = 'reflectVec = inverseTransformDirection( reflectVec, viewMatrix );';
const BOX_GLSL = `
{ vec3 bA = ( boxMax - vBoxWorld ) / reflectVec, bB = ( boxMin - vBoxWorld ) / reflectVec, bF = max( bA, bB );
  reflectVec = vBoxWorld + reflectVec * max( 0.0, min( min( bF.x, bF.y ), bF.z ) ) - boxProbe; }`;
if (!THREE.ShaderChunk.envmap_physical_pars_fragment.includes(BOX_LINE)) console.warn('three.js shader changed: mirrors are not box-projected');
// The box: the room's extent through the probe along x and along y (an L-shaped hall: the hall itself, not its bounds).
function spanAt(poly, k, at, c) {      // interval of the polygon along axis k on the line (other axis) = at, holding c
  const xs = [];
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[j], b = poly[i];
    if ((a[1 - k] > at) !== (b[1 - k] > at)) xs.push(a[k] + ((at - a[1 - k]) / (b[1 - k] - a[1 - k])) * (b[k] - a[k]));
  }
  xs.sort((p, q) => p - q);
  for (let i = 0; i + 1 < xs.length; i += 2) if (c >= xs[i] - 1e-6 && c <= xs[i + 1] + 1e-6) return [xs[i], xs[i + 1]];
  const all = poly.map((q) => q[k]);
  return [Math.min(...all), Math.max(...all)];
}
// A face within 0.5 m of the probe (a probe taken in a doorway) goes out to the room's bounds: seen from that close, it
// would magnify a strip of jamb into the whole mirror.
function boxProject(c, p) {
  const pl = p.rm.polygon, ext = (k, s, [a, b]) => { const all = pl.map((q) => q[k]); return [s - a < 0.5 ? Math.min(...all) : a, b - s < 0.5 ? Math.max(...all) : b]; };
  const [x0, x1] = ext(0, p.pos[0], spanAt(pl, 0, p.pos[1], p.pos[0])), [y0, y1] = ext(1, p.pos[1], spanAt(pl, 1, p.pos[0], p.pos[1]));
  const top = p.rm.ceilZ > p.rm.floorZ ? p.rm.ceilZ : p.rm.floorZ + 2.6;
  const u = { boxMin: { value: new THREE.Vector3(x0, p.rm.floorZ, -y1) }, boxMax: { value: new THREE.Vector3(x1, top, -y0) },
    boxProbe: { value: new THREE.Vector3(p.pos[0], p.pos[2] ?? p.rm.floorZ + 1.5, -p.pos[1]) } };
  const ob = c.onBeforeCompile, key = c.customProgramCacheKey;
  c.onBeforeCompile = (sh, r) => {
    ob.call(c, sh, r);
    sh.vertexShader = sh.vertexShader.replace('void main() {', 'varying vec3 vBoxWorld;\nvoid main() {')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvBoxWorld = worldPosition.xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <envmap_physical_pars_fragment>',
      `uniform vec3 boxMin;\nuniform vec3 boxMax;\nuniform vec3 boxProbe;\nvarying vec3 vBoxWorld;\n${THREE.ShaderChunk.envmap_physical_pars_fragment.replace(BOX_LINE, BOX_LINE + BOX_GLSL)}`);
    Object.assign(sh.uniforms, u);
  };
  c.customProgramCacheKey = () => `boxenv-${key.call(c)}`;
  c.userData.boxProbe = true;
}

// a baked leaf's probe scale: the light its bake gave the face that looks the way it swings (that face's surroundings
// are where the leaf ends up: the deck for a French door, the vestibule for the street door), area-weighted from a
// 512 px copy of the atlas, over the probe's (PMREM irradiance ~ PI * envMapIntensity * mean radiance).
// side: world direction the leaf swings toward (three frame), or null for both faces. ponytail: one scale per leaf.
const lmPixels = new Map(), tv = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()], tn = new THREE.Vector3();
function lmProbeScale(o, m, side = null) {
  const img = m.lightMap?.image, env = m.envMap?.image;
  if (!img || !env) return 1;
  if (!lmPixels.has(img)) {
    const c = Object.assign(document.createElement('canvas'), { width: 512, height: 512 }), g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(img, 0, 0, 512, 512); lmPixels.set(img, g.getImageData(0, 0, 512, 512).data);
  }
  const px = lmPixels.get(img), lin = (b) => { const v = b / 255; return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const sum = [0, 0, 0, 0];                    // [light * area, area] facing `side`, then over all triangles
  o.updateMatrixWorld(true);
  o.traverse((me) => {
    const g = me.geometry, uv = me.isMesh && [].concat(me.material).some((q) => q.lightMap?.image === img) && g.attributes.uv1, ix = g?.index;
    if (!uv) return;
    const pos = g.attributes.position, tri = (ix ? ix.count : pos.count) / 3, st = Math.max(1, Math.floor(tri / 4000)), at = (k) => (ix ? ix.getX(k) : k);
    for (let t = 0; t < tri; t += st) {
      let u = 0, w = 0;
      for (let j = 0; j < 3; j++) { const k = at(3 * t + j); u += uv.getX(k) / 3; w += uv.getY(k) / 3; tv[j].fromBufferAttribute(pos, k).applyMatrix4(me.matrixWorld); }
      tn.subVectors(tv[1], tv[0]).cross(tv[2].sub(tv[0]));
      const a = tn.length(), i = 4 * (Math.min(511, Math.max(0, Math.floor(w * 512))) * 512 + Math.min(511, Math.max(0, Math.floor(u * 512))));
      const l = ((lin(px[i]) + lin(px[i + 1]) + lin(px[i + 2])) / 3) * a;
      sum[2] += l; sum[3] += a;
      if (side && a > 0 && tn.dot(side) > 0.5 * a) { sum[0] += l; sum[1] += a; }
    }
  });
  const lm = sum[1] > 0 ? sum[0] / sum[1] : sum[3] > 0 ? sum[2] / sum[3] : null, probe = Math.PI * m.envMapIntensity * meanLinear(env);
  return lm !== null && probe > 0 ? clamp((lm * m.lightMapIntensity) / probe, 0.05, 1.5) : 1;
}

// Fallback when there is no bake: image-based fill + warm lamp per room + low sun with soft shadows.
function realtimeRig() {
  scene.environment = roomEnv; scene.environmentIntensity = 0.45;
  scene.add(new THREE.HemisphereLight(0xfff3e6, 0x2b241e, 0.35));
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const b = house?.bounds || planJson?.bounds || { minX: -1, minY: -1, maxX: 5, maxY: 18 };
  const cx = (b.minX + b.maxX) / 2, cy = (b.minY + b.maxY) / 2, R = Math.hypot(b.maxX - b.minX, b.maxY - b.minY) / 2 + 2;
  const sun = new THREE.DirectionalLight(0xfff0dc, 2.6);
  sun.position.set(cx - 6, 6.5, -b.minY + 9); sun.target.position.set(cx, 0, -cy);
  Object.assign(sun.shadow.camera, { left: -R, right: R, top: R, bottom: -R, near: 0.5, far: 60 });
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; sun.shadow.radius = 3;
  scene.add(sun, sun.target);
  for (const r of rooms) {
    if (r.kind !== 'room' || r.id === 'stairs') continue;
    const [x, y] = G.centroid(r.polygon), xs = r.polygon.map((p) => p[0]), ys = r.polygon.map((p) => p[1]);
    const ext = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
    const lamp = new THREE.PointLight(0xffd3a3, 3 + 1.4 * Math.abs(G.polyArea(r.polygon)), ext * 0.75 + 1, 2);
    lamp.position.set(x, r.floorZ + Math.min(r.ceilZ - r.floorZ, 3) - 0.35, -y);
    scene.add(lamp); roomLight(r.id).lamps.push({ light: lamp, k: lamp.intensity });
  }
}
if (realtime) realtimeRig();

// ---------- raycasting (pointing, double-click targets, line of sight) ----------
// Nearest-first: meshes sorted by where the ray enters their bounding sphere, stopping once a hit is nearer than the
// next sphere - only a handful of the triangles are ever tested. Hidden objects, untagged glass and (in the
// dollhouse) everything above the cut plane are looked through.
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), sph = new THREE.Sphere(), hitAt = new THREE.Vector3(), hits = [];
const shown = (o) => { for (; o; o = o.parent) if (!o.visible) return false; return true; };
let ix = null, cutY = Infinity;
function castRay(origin, dir, far = 60, glass = false) {     // glass: untagged glass stops the ray (reach, not sight)
  ray.set(origin, dir); ray.far = far;
  const cand = [];
  for (const o of meshes) {
    if (!o.geometry.boundingSphere) o.geometry.computeBoundingSphere();
    sph.copy(o.geometry.boundingSphere).applyMatrix4(o.matrixWorld);
    const d = sph.containsPoint(origin) ? 0 : ray.ray.intersectSphere(sph, hitAt) ? origin.distanceTo(hitAt) : Infinity;
    if (d <= far) cand.push([d, o]);
  }
  cand.sort((a, b) => a[0] - b[0]);
  let best = null;
  for (const [d, o] of cand) {
    if (best && d > best.distance) break;
    if (!shown(o) || (o.userData.glass && !glass && !ix?.tagged(o))) continue;
    hits.length = 0; o.raycast(ray, hits);
    for (const h of hits) if (h.distance <= far && (!best || h.distance < best.distance) && !(S.mode === 'orbit' && h.point.y > cutY)) best = h;
  }
  return best;
}
function castAt(cx, cy, far) {
  const r = canvas.getBoundingClientRect();
  ndc.set(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  return castRay(ray.ray.origin.clone(), ray.ray.direction.clone(), far);
}

// ---------- walk state: plan position, walk layer, floor height (eased), eye height (lower under sloped ceilings) ----------
const S = { mode: 'walk', x: spawn.pos[0], y: spawn.pos[1], layer: spawn.layer, z: 0, eye: EYE, level: null, yaw: spawn.yaw, pitch: 0, room: null,
  keys: new Set(), pad: [0, 0], anim: null, glide: null, fovT: FOV };
const here = () => ({ x: S.x, y: S.y, layer: S.layer });
const floorAt = (L, x, y) => (walk ? G.zAt(walk, L, x, y) : 0);
if (walk) { const p = G.nearestFree(walk, S.layer, S.x, S.y); if (p) [S.x, S.y] = p; S.z = floorAt(S.layer, S.x, S.y) ?? 0; }
const fadeEl = $('#fade');

function goTo(x, y, yaw = S.yaw, layer = S.layer, pitch = 0) {   // short eased glide (teleport / room jump); another layer: a cut
  S.glide = null;
  S.anim = layer !== S.layer ? { cut: true, t: 0, x1: x, y1: y, a1: yaw, layer, p1: pitch }
    : { x0: S.x, y0: S.y, a0: S.yaw, p0: S.pitch, x1: x, y1: y, a1: S.yaw + wrap(yaw - S.yaw), p1: pitch, t: 0 };
}
// Street-View walk: route through open doorways, round furniture and up / down the stairs, glide along it at GLIDE m/s
// with eased start / stop, the view turning gently toward the way ahead. Any key or drag cancels.
function walkTo(x, y, layer = S.layer) {
  if (!walk) { goTo(x, y); return true; }
  const p = G.nearestFree(walk, layer, x, y, 1.5), path = p && G.route(walk, here(), { x: p[0], y: p[1], layer });
  if (!path || G.pathLength(path) < 0.05) return false;
  S.anim = null; S.glide = { path, pts: path.map((q) => [q.x, q.y]), L: G.pathLength(path), s: 0, v: 0 }; hideHint();
  return true;
}
function along(pts, s) {
  for (let i = 1; i < pts.length; i++) {
    const [ax, ay] = pts[i - 1], [bx, by] = pts[i], l = Math.hypot(bx - ax, by - ay);
    if (s <= l || i === pts.length - 1) { const t = l ? Math.min(1, s / l) : 1; return [ax + (bx - ax) * t, ay + (by - ay) * t]; }
    s -= l;
  }
  return pts[0];
}
function glide(dt) {
  const gl = S.glide;
  gl.v = Math.min(GLIDE, gl.v + 4 * dt, Math.sqrt(6 * (gl.L - gl.s)) + 0.05);     // 4 m/s2 up, 3 m/s2 down
  gl.s = Math.min(gl.L, gl.s + gl.v * dt);
  const [x, y] = along(gl.pts, gl.s), [ax, ay] = along(gl.pts, Math.min(gl.L, gl.s + 1));
  const m = G.move(walk, here(), x, y);                                         // changes layer inside stair portals
  if (Math.hypot(m.x - x, m.y - y) > 0.2) { S.glide = null; return; }           // a door was shut across the route
  S.x = m.x; S.y = m.y; S.layer = m.layer;
  if (Math.hypot(ax - x, ay - y) > 0.3) S.yaw += wrap(G.dirYaw(ax - x, ay - y) - S.yaw) * Math.min(1, dt * 2.2);
  S.pitch -= S.pitch * Math.min(1, dt * 1.5);
  if (gl.s >= gl.L) { S.glide = null; arrive(gl.path[gl.path.length - 1]); }
}
// End of a walk: inside a stair mouth both layers are free and the glide keeps the one it came on - take the target's.
// On a flight, turn to face along it (up from its lower half, down from its upper half), not at the wall the path ran to.
function arrive(end) {
  if (end.layer !== S.layer && G.isFree(walk, end.layer, S.x, S.y)) S.layer = end.layer;
  const c = walk.cells.find((q) => q.kind === 'flight' && q.layer === S.layer);
  if (!c?.risers?.length) return;
  const [a, b] = c.risers.reduce((m, r) => (G.segDist(S.x, S.y, ...r[0], ...r[1]) < G.segDist(S.x, S.y, ...m[0], ...m[1]) ? r : m));
  const z = floorAt(S.layer, S.x, S.y) ?? c.fromZ, up = Math.abs(z - c.fromZ) < Math.abs(c.toZ - z) ? 1 : -1;   // passed a riser = left of a->b
  goTo(S.x, S.y, G.dirYaw(-(b[1] - a[1]) * up, (b[0] - a[0]) * up));
}
// floor point a double-click on this hit walks to: the floor itself, or the floor in front of a wall / object. The
// layer is the one whose floor height is nearest the hit (floor hits within 0.3 m, wall hits within floor..floor+2.6).
function targetOf(hit) {
  if (!hit || !walk) return null;
  const n = hit.face ? hit.face.normal.clone().transformDirection(hit.object.matrixWorld) : null, hy = hit.point.y;
  let [x, y] = G.threeToPlan(hit.point);
  const zs = walk.layers.map((L) => ({ L, z: G.zAt(walk, L, x, y) })).filter((c) => c.z !== null);
  // a riser seen from below (the flight's ramp passes within a riser height of the hit) counts as that flight's floor
  const riser = n && Math.abs(n.y) < 0.3 && zs.some((c) => walk.cells.some((k) => k.kind === 'flight' && k.layer === c.L) && Math.abs(hy - c.z) < 0.25);
  const floor = riser || (n && n.y > 0.7 && zs.some((c) => Math.abs(c.z - hy) < 0.3));
  if (!floor) {
    const dx = camera.position.x - hit.point.x, dz = camera.position.z - hit.point.z, l = Math.hypot(dx, dz) || 1;
    x += (dx / l) * 0.45; y -= (dz / l) * 0.45;
  }
  const cands = walk.layers.map((L) => ({ L, z: G.zAt(walk, L, x, y) }))
    .filter((c) => c.z !== null && (floor ? Math.abs(c.z - hy) < 0.3 : hy > c.z - 0.3 && hy < c.z + 2.6))
    .sort((a, b) => Math.abs(a.z - hy) - Math.abs(b.z - hy));
  if (!cands.length) cands.push({ L: S.layer });
  for (const c of cands) {
    const p = G.nearestFree(walk, c.L, x, y, 1.5);
    if (p) return { p, layer: c.L, y: floor && !riser && Math.hypot(p[0] - x, p[1] - y) < 0.05 ? hy : null };
  }
  return null;
}

// The interaction engine (GLB node extras `ix`, blender/INTERACT.md), fed one level scene at a time as they arrive.
// Emissives are white-balanced in the shader (above), so the hover tint goes in through the inverse matrix.
const wbInv = !realtime && manifest?.whiteBalance && new THREE.Matrix3().set(...manifest.whiteBalance.flat()).invert();
// the openings of each void room (eaves): its switch, behind the knee wall, is used through an open hatch
const via = Object.fromEntries(rooms.filter((r) => r.kind === 'void').map((r) => [r.id, (house?.openings || []).filter((o) => (o.connects || []).includes(r.id)).map((o) => o.id)]));
ix = initInteract({ walk, roomLight, castRay, emissiveToView: (c) => (wbInv ? c.applyMatrix3(wbInv) : c), feetY: () => S.z, onLights: ensureOff, lmProbe: lmProbeScale,
  circuitRooms: [...new Set(CIRCUITS.map((c) => c.room))], via,
  onClone: (m, c) => { for (const L of roomLights.values()) for (const x of L.mats) if (x.m === m) { L.mats.push({ m: c, k: x.k }); return; } },
  onPortals: () => {                    // a door shut on the walker standing in its doorway: step out of it
    if (!walk || G.isFree(walk, S.layer, S.x, S.y)) return;
    const p = G.nearestFree(walk, S.layer, S.x, S.y, 1.5); if (p) goTo(p[0], p[1]);
  } });
function tween(dt) {
  const a = S.anim;
  if (a.cut) {                          // to another layer: 150 ms through black, cut at the darkest, no flying through floors
    a.t = Math.min(1, a.t + dt / 0.15);
    if (a.t >= 0.5 && !a.done) { a.done = true; Object.assign(S, { x: a.x1, y: a.y1, yaw: a.a1, pitch: a.p1, layer: a.layer }); S.z = floorAt(S.layer, S.x, S.y) ?? S.z; }
    fadeEl.style.opacity = String(1 - Math.abs(2 * a.t - 1));
    if (a.t >= 1) S.anim = null;
    return;
  }
  a.t = Math.min(1, a.t + dt / 0.6); const e = a.t * a.t * (3 - 2 * a.t);
  S.x = lerp(a.x0, a.x1, e); S.y = lerp(a.y0, a.y1, e); S.yaw = lerp(a.a0, a.a1, e); S.pitch = lerp(a.p0, a.p1, e);
  if (a.t >= 1) S.anim = null;
}
const on = (...codes) => (codes.some((c) => S.keys.has(c)) ? 1 : 0);
function stepWalk(dt) {
  S.yaw += (on('ArrowLeft') - on('ArrowRight')) * TURN * dt;
  let f = on('KeyW', 'ArrowUp') - on('KeyS', 'ArrowDown') + S.pad[1], s = on('KeyD') - on('KeyA') + S.pad[0];
  const l = Math.hypot(f, s);
  if (l > 1) { f /= l; s /= l; }
  if (l > 0.02) {
    S.anim = S.glide = null; hideHint();
    const slow = walk && G.isSoft(walk, S.layer, S.x, S.y) ? 0.6 : 1;          // wading past a chair or a bin
    const sp = (on('ShiftLeft', 'ShiftRight') ? RUN : WALK) * slow * dt, [fx, fy] = G.yawDir(S.yaw);   // right = (fy, -fx)
    const nx = S.x + (fx * f + fy * s) * sp, ny = S.y + (fy * f - fx * s) * sp;
    if (walk) { const m = G.move(walk, here(), nx, ny); S.x = m.x; S.y = m.y; S.layer = m.layer; } else { S.x = nx; S.y = ny; }
  }
  if (S.glide) glide(dt);
  if (S.anim) tween(dt);
  if (Math.abs(camera.fov - S.fovT) > 0.01) { camera.fov += (S.fovT - camera.fov) * Math.min(1, dt * 9); camera.updateProjectionMatrix(); }
  // floor and eye ease at 10 / s: single risers and split-level steps are instantaneous in plan, smooth on screen
  const k = Math.min(1, 10 * dt), tz = floorAt(S.layer, S.x, S.y) ?? S.z, te = walk ? Math.min(EYE, G.headroomAt(walk, S.layer, S.x, S.y) - 0.12) : EYE;
  S.z += (tz - S.z) * k; S.eye += (te - S.eye) * k;
  camera.position.set(S.x, S.z + S.eye, -S.y);
  camera.rotation.set(S.pitch, S.yaw, 0);
}

// ---------- input: keys ----------
const MOVE = new Set(['KeyW', 'KeyA', 'KeyS', 'KeyD', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']);
const locked = () => document.pointerLockElement === canvas;
const toggleLock = () => (locked() ? document.exitPointerLock() : S.mode === 'walk' && canvas.requestPointerLock?.()?.catch?.(() => {}));
addEventListener('keydown', (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey || document.querySelector('dialog[open]')) return;
  const k = e.code;
  S.glide = null;
  if ((k === 'Space' || k === 'KeyE') && !/^(BUTTON|A|INPUT)$/.test(document.activeElement?.tagName)) { e.preventDefault(); if (!e.repeat) ix.use(camera); }
  else if (k === 'KeyL') toggleLock();
  else if (k === 'KeyO') setMode(S.mode === 'walk' ? 'orbit' : 'walk');
  else if (k === 'KeyP') togglePlan();
  else if (e.key === '?' || k === 'KeyH') toggleHelp();
  else if (k === 'Escape' && planEl.classList.contains('max')) $('#plan-max').click();
  else if (/^Digit[1-9]$/.test(k)) jump(curGroup()[+k.slice(5) - 1]?.id);          // rooms of the floor open in the bar
  else if ((k === 'PageUp' || k === 'PageDown') && groupOf.size > 1) {             // open the floor above / below in the bar
    const ids = [...groupOf.keys()]; e.preventDefault(); openGroup(ids[clamp(ids.indexOf(openLv) + (k === 'PageUp' ? 1 : -1), 0, ids.length - 1)]);
  }
  else if (MOVE.has(k) || k.startsWith('Shift')) {
    if (MOVE.has(k) && document.activeElement?.tagName === 'BUTTON' && k.startsWith('Arrow')) return;
    S.keys.add(k); if (MOVE.has(k)) e.preventDefault();
  }
});
// a pointer click leaves no focus on a toolbar button, so the next Space uses the thing in front instead of pressing it again
addEventListener('click', (e) => { const b = e.detail > 0 && e.target.closest?.('button'); if (b && !b.closest('dialog')) b.blur(); });
addEventListener('keyup', (e) => S.keys.delete(e.code));
addEventListener('blur', () => S.keys.clear());

// ---------- input: pointer ----------
// drag = look (grab the scene); click / tap (< 5 px, < 600 ms) = operate what is under it; a second click / tap
// within DBL ms = walk there; two fingers = pinch zoom; wheel = zoom (walk mode changes the field of view).
const ptrs = new Map();
let pinch = null, lastTap = null, hoverXY = null, hoverDirty = true;
function look(dx, dy, k) { k *= camera.fov / FOV; S.yaw += dx * k; S.pitch = clamp(S.pitch + dy * k, -1.3, 1.3); S.anim = S.glide = null; hideHint(); }
canvas.addEventListener('pointerdown', (e) => {
  if (e.pointerType === 'mouse' && e.button !== 0) return;
  ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, t0: performance.now(), moved: false, pinched: false });
  if (S.mode !== 'walk') return;
  try { canvas.setPointerCapture(e.pointerId); } catch {}       // the pointer may already be gone (fast touch)
  if (ptrs.size === 2) {
    const [a, b] = [...ptrs.values()]; a.pinched = b.pinched = true;
    pinch = { d: Math.max(20, Math.hypot(a.x - b.x, a.y - b.y)), fov: S.fovT };
  }
});
canvas.addEventListener('pointermove', (e) => {
  hoverDirty = true;
  if (locked()) {                                                   // mouse-look: move right = look right
    for (const p of ptrs.values()) if (Math.abs(e.movementX) + Math.abs(e.movementY) > 2) p.moved = true;   // a look, not a click
    return look(-e.movementX, -e.movementY, 0.0022);
  }
  const p = ptrs.get(e.pointerId);
  if (e.pointerType === 'mouse') hoverXY = [e.clientX, e.clientY];
  if (!p) return;
  if (Math.hypot(e.clientX - p.x0, e.clientY - p.y0) > 5) p.moved = true;
  if (S.mode === 'walk') {
    if (pinch && ptrs.size === 2) {
      p.x = e.clientX; p.y = e.clientY; const [a, b] = [...ptrs.values()];
      S.fovT = clamp((pinch.fov * pinch.d) / Math.max(20, Math.hypot(a.x - b.x, a.y - b.y)), FOV_MIN, FOV_MAX);
      return;
    }
    if (p.moved && !p.pinched) look(e.clientX - p.x, e.clientY - p.y, e.pointerType === 'touch' ? 0.0065 : 0.0045);
  }
  p.x = e.clientX; p.y = e.clientY;
});
const endPtr = (e) => {
  const p = ptrs.get(e.pointerId);
  ptrs.delete(e.pointerId);
  if (ptrs.size < 2) pinch = null;
  if (p && e.type === 'pointerup' && !p.moved && !p.pinched && performance.now() - p.t0 < 600) tap(e.clientX, e.clientY);
};
canvas.addEventListener('pointerup', endPtr); canvas.addEventListener('pointercancel', endPtr);
canvas.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && !locked()) { hoverXY = null; hoverDirty = true; } });
canvas.addEventListener('wheel', (e) => {
  if (S.mode !== 'walk') return;                   // the dollhouse keeps its orbit zoom
  e.preventDefault(); S.fovT = clamp(S.fovT * Math.exp(e.deltaY * 0.0012), FOV_MIN, FOV_MAX);
}, { passive: false });
// In walk mode a click on something operable waits out the double-click window, so a double-click on a door walks
// up to it instead of also opening it. The dollhouse has no double-click: it operates at once.
const DBL = 350;
let pending = null;
function tap(x, y) {
  if (locked()) [x, y] = [innerWidth / 2, innerHeight / 2];          // mouse-look: the crosshair
  const now = performance.now(), walking = S.mode === 'walk', range = walking ? POINT_RANGE : Infinity;
  const dbl = walking && lastTap && now - lastTap.t < DBL && Math.hypot(x - lastTap.x, y - lastTap.y) < 16;
  lastTap = dbl ? null : { t: now, x, y };
  clearTimeout(pending);
  const hit = castAt(x, y);
  if (dbl) { const t = targetOf(hit); if (t) walkTo(...t.p, t.layer); }
  else if (ix.hover(hit, range)) pending = setTimeout(() => { ix.click(hit, range); hoverDirty = true; }, walking ? DBL : 0);
  hoverDirty = true;
}
$('#btn-look').onclick = toggleLock;
document.addEventListener('pointerlockchange', () => { document.body.classList.toggle('locked', locked()); $('#btn-look').setAttribute('aria-pressed', locked()); hoverDirty = true; });

// ---------- pointing feedback: hover highlight + hint label, Space candidate, floor ring ----------
const tip = $('#ix-tip');
const ring = (() => {
  const c = Object.assign(document.createElement('canvas'), { width: 128, height: 128 }), g = c.getContext('2d'), gr = g.createRadialGradient(64, 64, 26, 64, 64, 62);
  for (const [s, a] of [[0, 0], [0.45, 0.15], [0.62, 0.95], [0.76, 0.95], [1, 0]]) gr.addColorStop(s, `rgba(255,255,255,${a})`);
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.46).rotateX(-Math.PI / 2),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, opacity: 0.75, depthWrite: false, toneMapped: false }));
  m.renderOrder = 3; m.visible = false; scene.add(m);
  return m;
})();
let nextBest = 0;
function showTip(text, x, y, key) {
  tip.hidden = !text;
  if (!text) return;
  tip.classList.toggle('key', !!key);
  tip.replaceChildren(...(key ? [Object.assign(document.createElement('kbd'), { textContent: 'Space' })] : []), text);   // labels are data: text only
  tip.style.left = key ? '' : `${x + 16}px`; tip.style.top = key ? '' : `${y + 18}px`;
}
function updatePointer(now) {
  const xy = locked() ? [innerWidth / 2, innerHeight / 2] : hoverXY;
  let g = ix.hovered();
  if (hoverDirty || S.glide || S.anim || S.keys.size) {           // re-cast only when something moved
    hoverDirty = false;
    const hit = xy && !ptrs.size ? castAt(...xy) : null;
    g = ix.hover(hit, S.mode === 'orbit' ? Infinity : POINT_RANGE);
    canvas.style.cursor = g ? 'pointer' : '';
    const t = !g && S.mode === 'walk' && !S.glide ? targetOf(hit) : null;
    ring.visible = !!t;
    if (t) ring.position.set(t.p[0], (t.y ?? floorAt(t.layer, ...t.p) ?? 0) + 0.012, -t.p[1]);
  }
  if (g) return showTip(ix.verb(g), ...(xy || [0, 0]));
  if (touch || S.mode !== 'walk') return showTip('');
  if (now > nextBest) { nextBest = now + 200; const b = ix.best(camera); showTip(b && ix.verb(b), 0, 0, true); }
}

const pad = $('#pad'), knob = $('#pad-knob'); let padId = null;
function padMove(e) {
  const r = pad.getBoundingClientRect(), R = r.width / 2;
  let dx = (e.clientX - r.left - R) / R, dy = (e.clientY - r.top - R) / R; const l = Math.hypot(dx, dy);
  if (l > 1) { dx /= l; dy /= l; }
  S.pad = [dx, -dy]; knob.style.transform = `translate(${dx * R * 0.6}px, ${dy * R * 0.6}px)`;
}
pad.addEventListener('pointerdown', (e) => { padId = e.pointerId; pad.setPointerCapture(padId); padMove(e); });
pad.addEventListener('pointermove', (e) => e.pointerId === padId && padMove(e));
const padEnd = (e) => { if (e.pointerId !== padId) return; padId = null; S.pad = [0, 0]; knob.style.transform = ''; };
pad.addEventListener('pointerup', padEnd); pad.addEventListener('pointercancel', padEnd);

// ---------- dollhouse (orbit): one clipping plane at the selected level's cutZ; "All" clips nothing ----------
const orbit = new OrbitControls(camera, canvas);
Object.assign(orbit, { enabled: false, enableDamping: true, dampingFactor: 0.08, maxPolarAngle: Math.PI * 0.47, minDistance: 1.5, maxDistance: 60 });
const cutPlanes = [new THREE.Plane(new THREE.Vector3(0, -1, 0), CUT)];     // drops ceilings, floors above and the roof
const tmp = new THREE.Vector3();
// Section caps: in the dollhouse, back faces exposed by the cut plane are drawn flat dark grey first, then the
// normal pass draws front faces over them - cut walls read as solid poché instead of see-through shells.
const capMat = new THREE.MeshBasicMaterial({ color: 0x8f8a83, side: THREE.BackSide });
const HOUSE_LEVELS = LEVELS.filter((l) => l.id !== 'X').map((l) => l.id);
let dhLevel = 'G';
const dollLevelOf = (lv) => (HOUSE_LEVELS.includes(lv) ? lv : schema2 ? 'all' : 'G');     // outside -> the whole plot
// What the dollhouse shows: never the neighbours' massing; on a level cut nothing wholly above the cut, no roof rising
// over the level (the loft slopes sit below the level-2 cut; a porch roof below the floor stays) and no ceiling of the
// level; "All" = house, roof and plot.
function dollVis() {
  const on = S.mode === 'orbit', cut = on && dhLevel !== 'all';
  for (const d of dhMeshes) d.o.visible = !on || (d.room !== 'neighbours' && !(cut && d.hide.has(dhLevel)));
  const out = levelScenes.get('X');
  if (out) out.visible = !(on && dhLevel === 'B');                  // the lawn and shed would float beside the basement
}
// plan box + heights of what a dollhouse level shows: the level's rooms from its floor to its cut; "all": the plot
function levelBox(id) {
  const all = id === 'all', lv = level(id), plot = all && house?.exterior?.plot?.polygon;
  const pts = plot || rooms.filter((r) => r.polygon && (all || r.level === id)).flatMap((r) => r.polygon);
  if (!pts.length) return null;
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]), top = Math.max(...LEVELS.map((l) => l.cutZ ?? -Infinity), CUT) + 1;
  return { minX: Math.min(...xs), maxX: Math.max(...xs), minY: Math.min(...ys), maxY: Math.max(...ys),
    z0: all ? level('X')?.datumZ ?? 0 : lv?.datumZ ?? 0, z1: all ? top : lv?.cutZ ?? CUT };
}
// Framing: the orbit target on the box centre (at height ty); of eight compass directions `el` radians up, the one that
// shows the box largest (a long plot side-on on a wide screen, end-on or corner-on on a phone), ties going to the side
// the camera is on; the camera just far enough for every corner of the box to be inside 85 % of the part of the view
// the open plan panel leaves free (its left side on a wide screen, its top on a phone). A view offset puts the target
// in the middle of that part (applyViewShift), so the target - the plan marker, the orbit pivot - stays on the house.
const fr = new THREE.Vector3(), fu = new THREE.Vector3(), fo = new THREE.Vector3(), TAN = Math.tan((FOV * Math.PI) / 360);
function planCover() {                  // [left, top] share of the view the plan panel covers
  if (planEl.classList.contains('collapsed') || planEl.classList.contains('max')) return [0, 0];
  const r = planEl.getBoundingClientRect();
  return innerWidth > 760 ? [clamp(r.right / innerWidth, 0, 0.5), 0] : [0, clamp(r.bottom / innerHeight, 0, 0.6)];
}
function applyViewShift() {             // the dollhouse's view offset (walk: none); the free part keeps a 70 deg view
  const W = innerWidth, H = innerHeight, [pl, pt] = S.mode === 'orbit' ? planCover() : [0, 0];
  camera.aspect = (W * (1 + pl)) / (H * (1 + pt));
  if (S.mode === 'orbit') camera.fov = (2 * Math.atan(TAN * (1 + pt)) * 180) / Math.PI;
  if (pl || pt) camera.setViewOffset(W * (1 + pl), H * (1 + pt), 0, 0, W, H); else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}
function fitDist(b, dir, [pl, pt]) {
  fr.crossVectors(camera.up, dir).normalize(); fu.crossVectors(dir, fr);
  const tx = TAN * (innerWidth / innerHeight) * 0.85 * (1 - pl), tz = TAN * 0.85 * (1 - pt);
  let d = orbit.minDistance;
  for (const x of [b.minX, b.maxX]) for (const y of [b.minY, b.maxY]) for (const z of [b.z0, b.z1]) {
    fo.set(x, z, -y).sub(orbit.target);
    const a = fo.dot(dir);
    d = Math.max(d, a + Math.abs(fo.dot(fr)) / tx, a + Math.abs(fo.dot(fu)) / tz);
  }
  return d;
}
function frameBox(b, ty, el) {
  const cur = tmp.subVectors(camera.position, orbit.target).setY(0).normalize().clone(), p = planCover();
  orbit.target.set((b.minX + b.maxX) / 2, ty, -(b.minY + b.maxY) / 2);
  let best = null;
  for (let k = 0; k < 8; k++) {
    const a = (k * Math.PI) / 4, dir = new THREE.Vector3(Math.cos(a) * Math.cos(el), Math.sin(el), Math.sin(a) * Math.cos(el));
    const d = fitDist(b, dir, p), s = d * (1.04 - 0.02 * dir.clone().setY(0).normalize().dot(cur));
    if (!best || s < best.s) best = { s, d, dir };
  }
  orbit.maxDistance = Math.max(60, best.d * 1.6);
  camera.position.copy(orbit.target).addScaledVector(best.dir, best.d); applyViewShift(); orbit.update();
}
// a level id or 'all'; fit = frame what it shows (a level button, entering the dollhouse), else only the target height
function setDollLevel(id, fit = false) {
  dhLevel = id;
  const lv = level(id), all = id === 'all';
  cutY = all ? Infinity : lv?.cutZ ?? CUT;
  cutPlanes[0].constant = cutY;
  renderer.clippingPlanes = S.mode === 'orbit' && !all ? cutPlanes : [];
  dollVis();
  const b = S.mode === 'orbit' && fit && levelBox(id);
  if (b) frameBox(b, all ? (b.z0 + b.z1) / 3 : lv?.datumZ ?? 0, camera.aspect < 1 ? 1.15 : 1.0);   // 57 deg up (66 end-on): over the cut walls, the roof
  else if (S.mode === 'orbit' && lv) { const dy = (lv.datumZ ?? 0) - orbit.target.y; orbit.target.y += dy; camera.position.y += dy; }
  for (const x of dhEl.children) x.setAttribute('aria-pressed', x.dataset.level === id);
  hoverDirty = true;
}
const dhEl = $('#dh-levels');
if (schema2 && HOUSE_LEVELS.length > 1) {
  dhEl.hidden = false;
  for (const id of [...HOUSE_LEVELS, 'all']) {
    const b = Object.assign(document.createElement('button'), { type: 'button', textContent: id === 'all' ? 'All' : id, title: id === 'all' ? 'Whole house, roof and garden' : `Cut above: ${levelName(id)}` });
    b.dataset.level = id; b.onclick = () => setDollLevel(id, true); dhEl.append(b);
  }
}
function setMode(m) {
  if (m === S.mode) return;
  S.mode = m; ptrs.clear(); pinch = null; S.anim = S.glide = null; fadeEl.style.opacity = '0'; document.exitPointerLock?.(); ring.visible = false; hoverDirty = true;
  camera.fov = FOV; applyViewShift();    // the dollhouse zooms by distance; walk eases back to its own zoom
  document.body.classList.toggle('orbit', m === 'orbit');
  $('#mode-walk').setAttribute('aria-pressed', m === 'walk'); $('#mode-orbit').setAttribute('aria-pressed', m === 'orbit');
  scene.background = m === 'orbit' ? DARK : SKY;
  if (m === 'orbit') {                   // the floor you are on (outside: the whole plot), seen from behind you, framed
    const id = dollLevelOf(S.level), d = level(id)?.datumZ ?? 0, [fx, fy] = G.yawDir(S.yaw);
    orbit.target.set(S.x, d, -S.y); camera.position.set(S.x - fx * 6, d + 9, -(S.y - fy * 6));
    orbit.enabled = true; orbit.update();
    setDollLevel(id, true);
  } else {
    setDollLevel(dhLevel); orbit.enabled = false;            // clears the clipping, shows the outside again
    const [tx, ty] = G.threeToPlan(orbit.target);
    let L = dhLevel === 'all' ? S.layer : G.layerOfLevel(dhLevel), p = walk ? G.nearestFree(walk, L, tx, ty) : [tx, ty];
    if (!p && walk && L !== 'G') { L = 'G'; p = G.nearestFree(walk, L, tx, ty); }
    if (p) { [S.x, S.y] = p; S.layer = L; S.z = floorAt(L, S.x, S.y) ?? S.z; }
    tmp.subVectors(orbit.target, camera.position); S.yaw = G.dirYaw(tmp.x, -tmp.z); S.pitch = 0;
  }
}
$('#mode-walk').onclick = () => setMode('walk');
$('#mode-orbit').onclick = () => setMode('orbit');

function teleport(x, y, layer = S.layer) {
  const p = walk ? G.nearestFree(walk, layer, x, y, 2.5) : [x, y];
  if (!p) return;
  if (S.mode === 'walk') return goTo(p[0], p[1], S.yaw, layer);
  tmp.set(p[0], orbit.target.y, -p[1]).sub(orbit.target); orbit.target.add(tmp); camera.position.add(tmp); [S.x, S.y] = p; S.layer = layer;
}
function jump(id) {
  const v = vps[id], r = rooms.find((q) => q.id === id);
  if (!v || !r) return;
  let p = (walk && G.nearestFree(walk, v.layer, ...v.pos, 0.6)) || v.pos;        // clear of the door leaves as they stand now
  // an open leaf beside the doorway would fill the view: step on into the room (up to 1.2 m) until it is 0.6 m away
  for (let k = 0; walk && v.into && k < 8 && G.dynDist(walk, v.layer, ...p) < 0.6; k++) {
    const q = [p[0] + v.into[0] * 0.15, p[1] + v.into[1] * 0.15];
    if (!G.isFree(walk, v.layer, ...q)) break;
    p = q;
  }
  if (S.mode === 'walk') return goTo(p[0], p[1], v.yaw, v.layer, v.pitch);
  const lv = dollLevelOf(r.level), [cx, cy] = G.centroid(r.polygon), xs = r.polygon.map((p) => p[0]), ys = r.polygon.map((p) => p[1]);
  const d = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) * 1.3 + 3;
  tmp.subVectors(camera.position, orbit.target).normalize(); tmp.y = Math.max(tmp.y, 0.8); tmp.normalize();   // keep a high view
  orbit.target.set(cx, level(lv)?.datumZ ?? 0, -cy); camera.position.copy(orbit.target).addScaledVector(tmp, d);
  [S.x, S.y, S.layer] = [p[0], p[1], v.layer];
  if (schema2) setDollLevel(lv);
}

// ---------- plan panel: one sheet per level + the site sheet; it follows the floor you are on ----------
const planEl = $('#plan'), planCanvas = $('#plan-canvas'), tabsEl = $('#plan-tabs');
const plan = planJson || (house && {      // minimal fallback drawing from house.json until plan.json exists
  bounds: house.bounds, rooms, layers: [{ name: 'A-WALL', color: '#e8e8e8', paper: '#111111', lineweight: 0.35 }],
  entities: rooms.map((r) => ({ layer: 'A-WALL', type: 'polyline', pts: r.polygon, closed: true })) });
const sheetLayer = () => G.layerOfLevel(planView?.sheet.level || planView?.sheetId || 'G');
const planView = plan ? new PlanView(planCanvas, plan, {
  sheet: spawn.layer,
  onPick: (x, y) => { const L = sheetLayer(); if (S.mode === 'orbit' && schema2) setDollLevel(dollLevelOf(planView.sheet.level ?? planView.sheetId)); teleport(x, y, hasLayer(L) ? L : S.layer); },
  onHover: (x, y) => { $('#plan-xy').textContent = `X ${Math.round(x * 1000)}  Y ${Math.round(y * 1000)}`; },
}) : null;
if (!planView) $('.plan-empty').hidden = false;
planCanvas.addEventListener('pointerleave', () => { $('#plan-xy').textContent = ''; });   // no stale readout
function showSheet(id) {               // switch the drawing (tab click, or the visitor changed level)
  planView?.setSheet(id);
  const s = planView?.sheet?.title ? planView.sheet : plan?.sheet;            // schema 1: plan.sheet
  if (s) $('#plan-title').textContent = [s.title, s.scale].filter(Boolean).join(' · ');
  for (const b of tabsEl.children) b.setAttribute('aria-pressed', b.dataset.sheet === planView?.sheetId);
}
if (planView?.sheets.length > 1) {
  tabsEl.hidden = false;
  for (const s of planView.sheets) {
    const b = Object.assign(document.createElement('button'), { type: 'button', textContent: s.id === 'X' ? 'SITE' : s.id, title: s.title || levelName(s.id) });
    b.dataset.sheet = s.id; b.onclick = () => showSheet(s.id); tabsEl.append(b);
  }
}
showSheet(planView?.sheetId);
function togglePlan(force) {
  const c = planEl.classList.toggle('collapsed', force);
  $('#plan-toggle').setAttribute('aria-expanded', !c);
}
$('#plan-toggle').onclick = () => togglePlan();
new ResizeObserver(() => S.mode === 'orbit' && applyViewShift()).observe(planEl);   // collapsed, maximised, resized
$('#plan-fit').onclick = () => planView?.fit();
$('#plan-max').onclick = () => {
  if (planView) planView.fitted = false;          // refit once the ResizeObserver reports the new size
  const m = planEl.classList.toggle('max'); planEl.classList.remove('collapsed');
  $('#plan-max').setAttribute('aria-pressed', m);
};
function setTheme(t) {
  planEl.classList.toggle('paper', t === 'paper'); planView?.setTheme(t); $('#plan-theme').setAttribute('aria-pressed', t === 'paper');
  try { localStorage.setItem('planTheme', t); } catch {}
}
$('#plan-theme').onclick = () => setTheme(planEl.classList.contains('paper') ? 'cad' : 'paper');
try { if (localStorage.getItem('planTheme') === 'paper') setTheme('paper'); } catch {}
if (qs.get('plan') === 'paper') setTheme('paper');
const dlName = planJson?.sheets ? 'house-plans' : 'ground-floor-plan';      // schema 1: the ground-floor drawing
for (const [a, ext] of [[$('#dl-dxf'), 'dxf'], [$('#dl-pdf'), 'pdf']]) {
  a.setAttribute('href', `assets/${dlName}.${ext}`);
  fetch(a.getAttribute('href'), { method: 'HEAD' }).then((r) => { if (!r.ok) throw 0; })
    .catch(() => { a.setAttribute('aria-disabled', 'true'); a.removeAttribute('href'); a.title = 'Not generated yet'; });
}

// ---------- room buttons (grouped by level), help, gallery, hint ----------
// One group per floor (B G 1F 2F OUT); only the open group lists its rooms, the others are a floor chip that opens
// them. The open group is the visitor's floor until a chip (or PageUp / PageDown) picks another; digits jump within it.
const nav = $('#rooms'), groupOf = new Map();
const jumpList = rooms.filter((r) => vps[r.id]);
const LV_TAG = { B: 'B', G: 'G', 1: '1F', 2: '2F', X: 'OUT' };
const shortName = (n) => { const s = n.split(/ \/| \(| and /)[0].replace(/ room$/i, '').replace(/^(first|second)-floor /i, ''); return s[0].toUpperCase() + s.slice(1); };
let openLv = null;
for (const lv of [...new Set([...(house?.levels || []).map((l) => l.id), 'G', 'X'])]) {
  const list = jumpList.filter((r) => r.level === lv);
  if (!list.length) continue;
  const grp = Object.assign(document.createElement('div'), { className: 'grp' });
  grp.dataset.level = lv; grp.setAttribute('role', 'group'); grp.setAttribute('aria-label', levelName(lv));
  if (house?.levels?.length) {
    const c = Object.assign(document.createElement('button'), { type: 'button', className: 'lv', textContent: LV_TAG[lv] ?? lv, title: `${levelName(lv)} (PageUp / PageDown)` });
    c.setAttribute('aria-expanded', 'false'); c.onclick = () => openGroup(lv); grp.append(c);
  }
  list.forEach((r, i) => {
    const b = document.createElement('button'), k = document.createElement('kbd');
    b.type = 'button'; b.dataset.room = r.id; b.title = `${r.name} (key ${i + 1})`; k.textContent = i + 1;
    b.append(shortName(r.name), ' ', k); b.onclick = () => jump(r.id); grp.append(b);   // short name, full one in title
  });
  nav.append(grp); groupOf.set(lv, list);
}
// a mouse wheel scrolls the strip sideways (it has no scrollbar)
nav.addEventListener('wheel', (e) => { if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) { nav.scrollLeft += e.deltaY; e.preventDefault(); } }, { passive: false });
const showCurrent = () => (nav.querySelector('.grp.open button[aria-current="true"]') || nav.querySelector('.grp.open'))?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
function openGroup(lv) {
  openLv = groupOf.has(lv) ? lv : groupOf.has('G') ? 'G' : [...groupOf.keys()][0];
  for (const g of nav.children) { const o = g.dataset.level === openLv; g.classList.toggle('open', o); g.querySelector('.lv')?.setAttribute('aria-expanded', o); }
  showCurrent();
}
openGroup(spawn.layer);
const curGroup = () => groupOf.get(openLv) || [];
// the floor you are on changed: the plan sheet follows (a tab click overrides until the next change), its tab and room
// group are marked and opened
function onLevel(lv) {
  if (!lv || lv === S.level) return;
  S.level = lv;
  if (planView?.sheets.some((s) => s.id === lv)) showSheet(lv);
  for (const b of tabsEl.children) b.classList.toggle('here', b.dataset.sheet === lv);
  for (const g of nav.children) g.classList.toggle('cur', g.dataset.level === lv);
  openGroup(lv);
}
// a flight is named for the floors it joins (its stairwell rooms span both: "Stair to the second floor (well)" read
// wrongly half-way up the main stair)
const flightName = (c) => house?.stairs?.find?.((s) => s.id === c.id)?.name
  || `Stairs, ${c.level.map((l) => levelName(l).split(/ \(| \//)[0].toLowerCase()).join(' to ')}`;
function updateRoom(x, y) {
  const L = S.mode === 'walk' || dhLevel === 'all' ? S.layer : G.layerOfLevel(dhLevel);
  // the dollhouse target over a stairwell or the eaves of the level shown: no room (not the ground floor's under it)
  const h = walk && (G.cellAt(walk, L, x, y) || (S.mode === 'orbit' && (dhLevel === 'all' || dhLevel === 'G') ? G.cellAt(walk, 'G', x, y) : null));
  onLevel(S.mode === 'orbit' && dhLevel !== 'all' ? dhLevel : h?.level || S.level || 'G');
  const r = h ? rooms.find((q) => q.id === h.room) || null : walk ? null : G.roomAt(rooms, x, y);
  const name = h?.cell.kind === 'flight' ? flightName(h.cell) : r?.name || '';
  if (r?.id === S.room?.id && name === S.roomName) return;
  S.room = r; S.roomName = name; $('#plan-room').textContent = name;
  for (const b of nav.querySelectorAll('button[data-room]')) b.setAttribute('aria-current', b.dataset.room === r?.id);
  showCurrent();
}
const help = $('#help');
function toggleHelp() { help.open ? help.close() : help.showModal(); }
$('#btn-help').onclick = toggleHelp;

const items = (Array.isArray(renders) ? renders : renders?.renders || renders?.images || [])
  .map((r) => (typeof r === 'string' ? { src: r } : { src: r.file || r.image || r.src, title: r.title || r.caption || '' })).filter((r) => r.src);
if (items.length) {
  const dlg = $('#gallery'), grid = dlg.querySelector('.grid'), lb = dlg.querySelector('.lightbox'), img = lb.querySelector('img'), cap = lb.querySelector('figcaption');
  let cur = 0;
  const show = (i) => {
    cur = (i + items.length) % items.length; img.src = 'renders/' + items[cur].src; img.alt = items[cur].title || `Render ${cur + 1}`;
    cap.textContent = items[cur].title || ''; grid.hidden = true; lb.hidden = false;
    if (!lb.contains(document.activeElement)) lb.querySelector('.next').focus();   // keep focus (and arrow keys) inside the dialog
  };
  const back = () => { lb.hidden = true; grid.hidden = false; };
  items.forEach((it, i) => {
    const b = document.createElement('button'), im = new Image();
    b.type = 'button'; im.src = 'renders/' + it.src; im.alt = it.title || `Render ${i + 1}`; im.loading = 'lazy'; b.append(im);
    if (it.title) { const s = document.createElement('span'); s.textContent = it.title; b.append(s); }
    b.onclick = () => show(i); grid.append(b);
  });
  lb.querySelector('.prev').onclick = () => show(cur - 1); lb.querySelector('.next').onclick = () => show(cur + 1); lb.querySelector('.back').onclick = back;
  dlg.addEventListener('keydown', (e) => { if (!lb.hidden && e.key === 'ArrowLeft') show(cur - 1); if (!lb.hidden && e.key === 'ArrowRight') show(cur + 1); });
  dlg.addEventListener('close', back);
  $('#btn-gallery').hidden = false; $('#btn-gallery').onclick = () => dlg.showModal();
}

const hint = $('#hint');
hint.textContent = touch ? 'Drag to look · pad to move · tap to use · double-tap to go · pinch to zoom'
  : 'Drag to look · WASD to move · double-click to go · click or Space to open · wheel to zoom · ? for help';
function hideHint() { hint.classList.add('gone'); }
setTimeout(hideHint, 10000);

// ---------- levels: load in loadOrder; the loading screen goes once the first is lit, the rest stream in ----------
const ixLevels = [];                    // levels handed to the interaction engine, in arrival order
async function loadLevel(id, onProgress) {
  const url = schema2 ? level(id).glb : 'home.glb';
  if (!url) return false;               // a level without a GLB is still walkable
  const model = (await loader.loadAsync('assets/' + url, onProgress)).scene;
  model.name = `level_${id}`; model.userData.level = id;
  const mine = prepare(model);
  if (realtime) for (const o of mine) { o.castShadow = !o.userData.glass; o.receiveShadow = true; }
  else {
    for (const r of rooms) if (r.kind === 'void' && r.level === id) startOff(r.id);
    await applyBake(id, mine);
  }
  if (qs.get('batch') !== 'off') batch(model, mine);
  root.add(model); levelScenes.set(id, model);
  dollVis();                            // arriving while the dollhouse is open: its rules apply at once
  ix.add(model); ixLevels.push(id);     // its doors, switches and lamps work from now on
  hoverDirty = true;
  return true;
}
try { await loadLevel(ORDER[0], (e) => progress(e.loaded, e.total)); }
catch (err) { msg.textContent = 'The 3D model is not available yet.'; bar.parentElement.classList.remove('indet'); throw err; }

// ---------- loop ----------
addEventListener('resize', () => {
  applyViewShift(); renderer.setSize(innerWidth, innerHeight, false);
});
let last = performance.now();
function frame(now) {
  const dt = Math.min((now - last) / 1000, 0.05); last = now;
  let px, py, dir;
  if (S.mode === 'walk') { stepWalk(dt); px = S.x; py = S.y; dir = G.yawDir(S.yaw); }
  else {
    orbit.update(); [px, py] = G.threeToPlan(orbit.target);
    tmp.subVectors(orbit.target, camera.position); const l = Math.hypot(tmp.x, tmp.z) || 1; dir = [tmp.x / l, -tmp.z / l];
  }
  updateRoom(px, py);
  ix.update(dt, now); updatePointer(now);
  if (planView) {                       // marker on the sheet of the visitor's floor, and always on SITE (hollow indoors)
    const sl = planView.sheet.level ?? planView.sheetId, multi = planView.sheets.length > 1;
    const mark = !multi || sl === S.level ? 'full' : planView.sheetId === 'X' ? 'hollow' : null;
    planView.setViewer({ x: px, y: py, dir, hfov: G.hfov(camera.fov, camera.aspect), mark }, S.room);
  }
  cull();
  if (S.mode === 'orbit') {
    scene.overrideMaterial = capMat; renderer.render(scene, camera); scene.overrideMaterial = null;
    // a Color background forces a clear even with autoClear off (WebGLBackground), so drop it for pass 2
    scene.background = null; renderer.autoClear = false; renderer.render(scene, camera); renderer.autoClear = true; scene.background = DARK;
  } else renderer.render(scene, camera);
}
stepWalk(0);
await renderer.compileAsync(scene, camera).catch(() => {});
renderer.setAnimationLoop(frame);
requestAnimationFrame(() => $('#loader').classList.add('done'));
load.done = true;

// the other levels, one after another, behind a small progress chip
const streaming = (async () => {
  for (const id of ORDER.slice(1)) {
    if (!(schema2 && level(id).glb)) continue;
    chip.hidden = false; chip.textContent = `Loading ${levelName(id).toLowerCase()}…`;
    try {
      await loadLevel(id, (e) => { if (e.total > 0 && e.loaded <= e.total) chip.textContent = `Loading ${levelName(id).toLowerCase()} · ${Math.round((100 * e.loaded) / e.total)}%`; });
      await renderer.compileAsync(levelScenes.get(id), camera, scene).catch(() => {});
    } catch (err) { console.warn(`level ${id} could not be loaded`, err); }
  }
  chip.hidden = true;
})();

// decoded texture memory of what the scene can draw (unique sources, mip chain +1/3; lights-off maps once loaded),
// uploading what is not on the GPU yet - for tests and measurements
function texStats() {
  const seen = new Map(), add = (t) => t?.image && !seen.has(t.source) && seen.set(t.source, t);
  scene.traverse((o) => { if (o.isMesh) for (const m of [].concat(o.material)) for (const k of [...TEX_SLOTS, 'lightMap']) add(m[k]); });
  for (const L of roomLights.values()) for (const t of [L.off?.tex, ...L.circuits.map((c) => c.tex.value)]) add(t);
  let bytes = 0;
  for (const t of seen.values()) { renderer.initTexture(t); bytes += (t.image.width || 0) * (t.image.height || 0) * 4 * (t.generateMipmaps ? 4 / 3 : 1); }
  return { gpuTextures: renderer.info.memory.textures, sources: seen.size, MB: +(bytes / 1048576).toFixed(1) };
}

// debug / test handle
window.viewer = { viewRect, texStats, sharedTex, cullList, seen: () => seen, setCull: (v) => { CULL = v; cullKey = null; cull(); }, dhMeshes, levelBox, openGroup, THREE, G, scene, camera, renderer, orbit, S, walk, rooms, vps, planView, setMode, teleport, jump, ix, walkTo, castAt, castRay, ring, roomLights,
  FOV, FOV_MIN, FOV_MAX, LEVELS, ORDER, levelScenes, ixLevels, setDollLevel, streaming, schema2, targetOf, lmProbeScale,
  info: () => ({ mode: S.mode, x: S.x, y: S.y, z: S.z, layer: S.layer, level: S.level, yaw: S.yaw, room: S.room?.id ?? null, sheet: planView?.sheetId ?? null,
    realtime, meshes: meshes.length, lightmapped: meshes.filter((m) => m.userData.baked).length, probed: meshes.filter((m) => !realtime && !m.userData.baked).length,
    glass: meshes.filter((m) => m.userData.glass).length, eye: camera.position.y - S.z, batches: nBatch, roomName: S.roomName ?? null }) };
