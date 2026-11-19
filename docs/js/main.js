// Ground-floor walkthrough viewer: three.js r180 via import map (no build step), relative URLs only.
// Frames: house/plan (x right, y into the house, z up) -> three (x, z, -y); see geom.js.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
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
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight, false);
const scene = new THREE.Scene();
const SKY = new THREE.Color(0x296c97), DARK = new THREE.Color(0x15181b);   // walk: the sky as Cycles shows it through the windows (manifest.sky); dollhouse: neutral
scene.background = SKY;
const camera = new THREE.PerspectiveCamera(FOV, innerWidth / innerHeight, 0.05, 100);
camera.rotation.order = 'YXZ';
const pmrem = new THREE.PMREMGenerator(renderer);
const roomEnv = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// ---------- loading screen ----------
const bar = $('#bar'), msg = $('#loader-msg');
function progress(loaded, total) {
  const mb = (loaded / 1048576).toFixed(1);
  const known = total > 0 && loaded <= total;          // gzip on Pages can make loaded > total
  bar.parentElement.classList.toggle('indet', !known);
  if (known) bar.style.width = `${(100 * loaded) / total}%`;
  msg.textContent = known ? `Loading model ${Math.round((100 * loaded) / total)}% · ${mb} MB` : `Loading model · ${mb} MB`;
}

msg.textContent = 'Loading plan…';
const [manifest, house, planJson, foot, renders] = await Promise.all(
  ['assets/manifest.json', 'assets/house.json', 'assets/plan.json', 'assets/footprints.json', 'renders/index.json'].map(getJSON));
const realtime = qs.get('lighting') === 'realtime' || !manifest?.lightmaps?.length;
if (manifest?.sky) SKY.set(manifest.sky);
// Lamps, lit shades and LED strips are authored warm for the 3000 K white balance of the Cycles view. The bake has
// that balance multiplied in; emissive colours come unbalanced in the GLB, so the same matrix is applied here.
if (!realtime && manifest?.whiteBalance) {
  const M = manifest.whiteBalance, col = (j) => `vec3( ${M.map((r) => r[j].toFixed(5)).join(', ')} )`;
  THREE.ShaderChunk.emissivemap_fragment += `\ntotalEmissiveRadiance = max( mat3( ${col(0)}, ${col(1)}, ${col(2)} ) * totalEmissiveRadiance, vec3( 0.0 ) );\n`;
}
const rooms = (manifest?.rooms || planJson?.rooms || house?.rooms || [])
  .map((r) => ({ id: r.id, name: r.name || r.id, polygon: r.polygon, ceilZ: r.ceilZ ?? r.ceilingZ ?? 2.9, floorZ: r.floorZ ?? 0 }));
const walk = house ? G.buildWalk(house, { obstacles: G.obstaclesFrom(foot), soft: G.obstaclesFrom(foot, true) }) : null;
const spawn = { pos: (manifest?.spawn?.pos || house?.spawn || G.centroid(rooms[0]?.polygon || [[0, 1]])).slice(0, 2),
  yaw: ((manifest?.spawn?.yaw ?? 0) * Math.PI) / 180 };          // manifest yaw: degrees, 0 = facing +Y, CCW positive
const vps = walk ? G.viewpoints(walk, spawn.pos)
  : Object.fromEntries(rooms.map((r) => [r.id, { pos: G.centroid(r.polygon), yaw: 0 }]));
// hand-framed room-jump views from the export (first hero still of each room), snapped to walkable floor;
// the room holding the spawn point keeps the spawn view
for (const [id, v] of Object.entries((walk && manifest?.viewpoints) || {})) {
  const p = vps[id] && G.roomAt(rooms, ...spawn.pos)?.id !== id ? G.nearestFree(walk, v.pos[0], v.pos[1], 0.6) : null;
  if (p && G.roomAt(rooms, ...p)?.id === id) vps[id] = { pos: p, yaw: G.dirYaw(v.look[0] - p[0], v.look[1] - p[1]) };
}

const TM = { agx: THREE.AgXToneMapping, neutral: THREE.NeutralToneMapping, aces: THREE.ACESFilmicToneMapping, none: THREE.NoToneMapping };
renderer.toneMapping = TM[qs.get('tm') || manifest?.toneMapping] ?? THREE.AgXToneMapping;
renderer.toneMappingExposure = +(qs.get('exposure') || manifest?.exposure || (realtime ? 1.0 : 1.0));

// ---------- model ----------
const draco = new DRACOLoader().setDecoderPath(LIBS + 'draco/gltf/');
const ktx2 = new KTX2Loader().setTranscoderPath(LIBS + 'basis/').detectSupport(renderer);
const loader = new GLTFLoader().setDRACOLoader(draco).setKTX2Loader(ktx2).setMeshoptDecoder(MeshoptDecoder);
let gltf;
try { gltf = await loader.loadAsync('assets/home.glb', (e) => progress(e.loaded, e.total)); }
catch (err) { msg.textContent = 'The 3D model is not available yet.'; bar.parentElement.classList.remove('indet'); throw err; }
const model = gltf.scene;
scene.add(model);

const maxAniso = Math.min(8, renderer.capabilities.getMaxAnisotropy());
const meshes = [];
model.traverse((o) => o.isMesh && meshes.push(o));
const mapMats = (o, f) => (Array.isArray(o.material) ? o.material.map(f) : f(o.material));
for (const o of meshes) mapMats(o, (m) => {
  for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap']) if (m[k]) m[k].anisotropy = maxAniso;
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

// ---------- lighting ----------
const texLoader = new THREE.TextureLoader();
const byName = new Map();
model.traverse((o) => { for (const n of [o.userData.name, o.name]) if (n && !byName.has(n)) byName.set(n, o); });
const findNode = (n) => byName.get(n) || byName.get(THREE.PropertyBinding.sanitizeNodeName(n));

// Baked lighting, per mesh:
//  - lightmap (objects listed in the manifest): manifest intensity = linear scale of the 8-bit image
//    (linear = srgbDecode(px) * intensity) of a Cycles DIFFUSE direct+indirect bake (white-Lambert radiance). three's
//    lightMap is irradiance (divided by PI in the BRDF) -> * PI. Second UV set, flipY false.
//  - room probe (equirect, centre = +X) as envMap on EVERY mesh: all the light of meshes without a lightmap, but
//    reflections only on lightmapped ones (their diffuse light is already in the lightmap -> IBL irradiance removed).
//  - light switches: each lightmapped material mixes its room's lights-on map with the lights-off map (manifest
//    lightmapsOff, same atlases; missing -> the on-map at 12 %) by the room's lmOn uniform (eased by interact.js).
//  - lmMix (1 = bake): a baked door leaf / front that moves away from its modelled pose fades from its lightmap to the
//    probe's diffuse light (interact.js), since the bake only fits the pose it was baked in.
const IBL_DIFFUSE = 'iblIrradiance += getIBLIrradiance( geometryNormal );', LM_LINE = 'vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;';
const SPEC_ONLY_CHUNK = THREE.ShaderChunk.lights_fragment_maps.replace(IBL_DIFFUSE, 'iblIrradiance += ( 1.0 - lmMix ) * getIBLIrradiance( geometryNormal );')
  .replace(LM_LINE, 'vec3 lightMapIrradiance = lmMix * mix( texture2D( lightMapOff, vLightMapUv ).rgb * lightMapOffIntensity, lightMapTexel.rgb * lightMapIntensity, lmOn );');
if (SPEC_ONLY_CHUNK.includes(IBL_DIFFUSE)) console.warn('three.js shader changed: lightmapped surfaces are lit twice');
if (!SPEC_ONLY_CHUNK.includes('lmOn')) console.warn('three.js shader changed: light switches cannot dim the bake');
const specOnly = (sh) => {
  sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_maps>', SPEC_ONLY_CHUNK)
    .replace('#include <lightmap_pars_fragment>', '#include <lightmap_pars_fragment>\nuniform sampler2D lightMapOff;\nuniform float lightMapOffIntensity;\nuniform float lmOn;\nuniform float lmMix;');
};
// Per-room light state shared by the bake materials (lmOn), probe reflections, realtime lamps and lamp emissives;
// interact.js eases `on` toward `target`. ratio = brightness of the lights-off bake relative to the lights-on one.
const roomLights = new Map();
const roomLight = (id) => roomLights.get(id) || roomLights.set(id, { on: { value: 1 }, target: 1, ratio: 0.12, mats: [], lamps: [], ems: [] }).get(id);
function meanLinear(img) {             // mean linear value of an 8-bit sRGB image, from a 32x32 thumbnail
  const c = Object.assign(document.createElement('canvas'), { width: 32, height: 32 }), g = c.getContext('2d', { willReadFrequently: true });
  g.drawImage(img, 0, 0, 32, 32);
  const d = g.getImageData(0, 0, 32, 32).data; let s = 0;
  for (let i = 0; i < d.length; i += 4) for (let j = 0; j < 3; j++) { const v = d[i + j] / 255; s += v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }
  return s / (d.length * 0.75);
}

async function applyBake() {
  const load = (u) => texLoader.loadAsync('assets/' + u).catch(() => (console.warn('baked image missing:', u), null));
  const offs = new Map((await Promise.all((manifest.lightmapsOff || []).map(async (lm) => {
    const tex = await load(lm.image);
    if (!tex) return null;
    Object.assign(tex, { channel: 1, flipY: false, colorSpace: THREE.SRGBColorSpace, anisotropy: maxAniso });
    return [lm.room, { tex, k: Math.PI * (lm.intensity ?? 1) }];
  }))).filter(Boolean));
  const probes = (await Promise.all((manifest.probes || []).map(async (p) => {
    const room = rooms.find((r) => r.id === p.room), tex = await load(p.image);
    if (!tex || !room) return null;
    Object.assign(tex, { mapping: THREE.EquirectangularReflectionMapping, colorSpace: THREE.SRGBColorSpace });
    // lights off: probe-lit materials scale their probe by the brightness of the lights-off probe (manifest probesOff)
    const off = (manifest.probesOff || []).find((q) => q.room === p.room), offTex = off && await load(off.image);
    if (offTex) roomLight(p.room).pratio = Math.min(1, Math.max(0.01, (meanLinear(offTex.image) * (off.intensity ?? 1)) / Math.max(1e-6, meanLinear(tex.image) * (p.intensity ?? 1))));
    return { room, tex, c: G.centroid(room.polygon), k: p.intensity ?? 1 };
  }))).filter(Boolean);
  const lmOf = new Map(); let missing = 0, nouv = 0;          // mesh -> { tex, k }
  await Promise.all(manifest.lightmaps.map(async (lm) => {
    const tex = await load(lm.image);
    if (!tex) return;
    Object.assign(tex, { channel: 1, flipY: false, colorSpace: THREE.SRGBColorSpace, anisotropy: maxAniso });
    const k = Math.PI * (lm.intensity ?? 1), off = offs.get(lm.room) || { tex, k: k * 0.12 }, L = roomLight(lm.room);
    if (off.tex !== tex) L.ratio = Math.min(1, Math.max(0.01, (meanLinear(off.tex.image) * off.k) / Math.max(1e-6, meanLinear(tex.image) * k)));
    for (const n of lm.objects || []) {
      const node = findNode(n);
      if (!node) { missing++; continue; }
      node.traverse((o) => {
        if (!o.isMesh) return;
        if (o.geometry.attributes.uv1) lmOf.set(o, { tex, k, off, L }); else nouv++;
      });
    }
  }));
  if (missing) console.warn(`${missing} lightmapped object names not found in the GLB`);
  if (nouv) console.warn(`${nouv} lightmapped meshes have no second UV set (uv1)`);

  const box = new THREE.Box3(), v = new THREE.Vector3(), cache = new Map();
  const dist = (p, x, y) => Math.hypot(p.c[0] - x, p.c[1] - y);
  for (const o of meshes) {
    const lm = lmOf.get(o), id = o.userData.room || o.parent?.userData.room;      // glTF extras; a multi-material
    let pr = probes.find((p) => p.room.id === id);                                // node is a Group of meshes
    if (!pr && probes.length) {
      box.setFromObject(o).getCenter(v); const [x, y] = G.threeToPlan(v);
      pr = probes.find((p) => G.pointInPoly(x, y, p.room.polygon)) || probes.reduce((a, b) => (dist(a, x, y) < dist(b, x, y) ? a : b));
    }
    const env = pr ? pr.tex : roomEnv;
    o.material = mapMats(o, (m) => {
      const key = m.uuid + env.uuid + (lm ? lm.tex.uuid : '');
      if (!cache.has(key)) {
        const c = Object.assign(m.clone(), { envMap: env, envMapIntensity: pr ? pr.k : 0.6 });
        if (lm) {
          const u = { lightMapOff: { value: lm.off.tex }, lightMapOffIntensity: { value: lm.off.k }, lmOn: lm.L.on, lmMix: { value: 1 } };
          Object.assign(c, { lightMap: lm.tex, lightMapIntensity: lm.k, onBeforeCompile: (sh) => { specOnly(sh); Object.assign(sh.uniforms, u); } });
        }
        if (pr) roomLight(pr.room.id).mats.push({ m: c, k: pr.k });
        cache.set(key, c);
      }
      return cache.get(key);
    });
    o.userData.baked = !!lm;        // not "lm": the GLB extras already use userData.lm = 'static' | 'dynamic'
  }
}

// Fallback when there is no bake: image-based fill + warm lamp per room + low sun with soft shadows.
function realtimeRig() {
  scene.environment = roomEnv; scene.environmentIntensity = 0.45;
  scene.add(new THREE.HemisphereLight(0xfff3e6, 0x2b241e, 0.35));
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  for (const o of meshes) { o.castShadow = !o.userData.glass; o.receiveShadow = true; }
  const b = house?.bounds || planJson?.bounds || { minX: -1, minY: -1, maxX: 5, maxY: 18 };
  const cx = (b.minX + b.maxX) / 2, cy = (b.minY + b.maxY) / 2, R = Math.hypot(b.maxX - b.minX, b.maxY - b.minY) / 2 + 2;
  const sun = new THREE.DirectionalLight(0xfff0dc, 2.6);
  sun.position.set(cx - 6, 6.5, -b.minY + 9); sun.target.position.set(cx, 0, -cy);
  Object.assign(sun.shadow.camera, { left: -R, right: R, top: R, bottom: -R, near: 0.5, far: 60 });
  sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.03; sun.shadow.radius = 3;
  scene.add(sun, sun.target);
  for (const r of rooms) {
    if (r.id === 'stairs') continue;
    const [x, y] = G.centroid(r.polygon), xs = r.polygon.map((p) => p[0]), ys = r.polygon.map((p) => p[1]);
    const ext = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys));
    const lamp = new THREE.PointLight(0xffd3a3, 3 + 1.4 * Math.abs(G.polyArea(r.polygon)), ext * 0.75 + 1, 2);
    lamp.position.set(x, Math.min(r.ceilZ, 3) - 0.35, -y);
    scene.add(lamp); roomLight(r.id).lamps.push({ light: lamp, k: lamp.intensity });
  }
}

if (realtime) realtimeRig();
else await applyBake();

// ---------- raycasting (pointing, double-click targets, line of sight) ----------
// Nearest-first: meshes sorted by where the ray enters their bounding sphere, stopping once a hit is nearer than the
// next sphere - only a handful of the 700k triangles are ever tested. Hidden objects, untagged glass and (in the
// dollhouse) everything above the cut plane are looked through.
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), sph = new THREE.Sphere(), hitAt = new THREE.Vector3(), hits = [];
const shown = (o) => { for (; o; o = o.parent) if (!o.visible) return false; return true; };
let ix = null;
function castRay(origin, dir, far = 60) {
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
    if (!shown(o) || (o.userData.glass && !ix?.tagged(o))) continue;
    hits.length = 0; o.raycast(ray, hits);
    for (const h of hits) if (h.distance <= far && (!best || h.distance < best.distance) && !(S.mode === 'orbit' && h.point.y > CUT)) best = h;
  }
  return best;
}
function castAt(cx, cy, far) {
  const r = canvas.getBoundingClientRect();
  ndc.set(((cx - r.left) / r.width) * 2 - 1, -((cy - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  return castRay(ray.ray.origin.clone(), ray.ray.direction.clone(), far);
}

// ---------- walk state ----------
const S = { mode: 'walk', x: spawn.pos[0], y: spawn.pos[1], yaw: spawn.yaw, pitch: 0, room: null, keys: new Set(), pad: [0, 0], anim: null, glide: null, fovT: FOV };
if (walk) [S.x, S.y] = G.nearestFree(walk, S.x, S.y) || [S.x, S.y];

function goTo(x, y, yaw = S.yaw) {        // short eased glide (teleport / room jump)
  S.glide = null;
  S.anim = { x0: S.x, y0: S.y, a0: S.yaw, p0: S.pitch, x1: x, y1: y, a1: S.yaw + wrap(yaw - S.yaw), t: 0 };
}
// Street-View walk: route through open doorways and round furniture, glide along it at GLIDE m/s with eased start /
// stop, the view turning gently toward the way ahead. Any key or drag cancels.
function walkTo(x, y) {
  if (!walk) { goTo(x, y); return true; }
  const p = G.nearestFree(walk, x, y, 1.5), path = p && G.route(walk, [S.x, S.y], p);
  if (!path || G.pathLength(path) < 0.05) return false;
  S.anim = null; S.glide = { path, L: G.pathLength(path), s: 0, v: 0 }; hideHint();
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
  const [x, y] = along(gl.path, gl.s), [ax, ay] = along(gl.path, Math.min(gl.L, gl.s + 1));
  const [mx, my] = G.move(walk, S.x, S.y, x, y);
  if (Math.hypot(mx - x, my - y) > 0.2) { S.glide = null; return; }               // a door was shut across the route
  S.x = mx; S.y = my;
  if (Math.hypot(ax - x, ay - y) > 0.3) S.yaw += wrap(G.dirYaw(ax - x, ay - y) - S.yaw) * Math.min(1, dt * 2.2);
  S.pitch -= S.pitch * Math.min(1, dt * 1.5);
  if (gl.s >= gl.L) S.glide = null;
}
// floor point a double-click on this hit walks to: the floor itself, or the floor in front of a wall / object
function targetOf(hit) {
  if (!hit || !walk) return null;
  const n = hit.face ? hit.face.normal.clone().transformDirection(hit.object.matrixWorld) : null;
  let [x, y] = G.threeToPlan(hit.point);
  const floor = n && n.y > 0.7 && hit.point.y < 0.3;
  if (!floor) {
    const dx = camera.position.x - hit.point.x, dz = camera.position.z - hit.point.z, l = Math.hypot(dx, dz) || 1;
    x += (dx / l) * 0.45; y -= (dz / l) * 0.45;
  }
  const p = G.nearestFree(walk, x, y, 1.5);
  return p && { p, y: floor && Math.hypot(p[0] - x, p[1] - y) < 0.05 ? hit.point.y : null };
}

// The interaction engine (GLB node extras `ix`, blender/INTERACT.md). Emissives are white-balanced in the shader (above),
// so the hover tint goes in through the inverse matrix.
const wbInv = !realtime && manifest?.whiteBalance && new THREE.Matrix3().set(...manifest.whiteBalance.flat()).invert();
ix = initInteract({ model, walk, roomLight, castRay, emissiveToView: (c) => (wbInv ? c.applyMatrix3(wbInv) : c),
  onClone: (m, c) => { for (const L of roomLights.values()) for (const x of L.mats) if (x.m === m) { L.mats.push({ m: c, k: x.k }); return; } },
  onPortals: () => {                    // a door shut on the walker standing in its doorway: step out of it
    if (!walk || G.isFree(walk, S.x, S.y)) return;
    const p = G.nearestFree(walk, S.x, S.y, 1.5); if (p) goTo(p[0], p[1]);
  } });
function tween(dt) {
  const a = S.anim; a.t = Math.min(1, a.t + dt / 0.6); const e = a.t * a.t * (3 - 2 * a.t);
  S.x = lerp(a.x0, a.x1, e); S.y = lerp(a.y0, a.y1, e); S.yaw = lerp(a.a0, a.a1, e); S.pitch = lerp(a.p0, 0, e);
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
    const slow = walk && G.isSoft(walk, S.x, S.y) ? 0.6 : 1;                  // wading past a chair or a bin
    const sp = (on('ShiftLeft', 'ShiftRight') ? RUN : WALK) * slow * dt, [fx, fy] = G.yawDir(S.yaw);   // right = (fy, -fx)
    const nx = S.x + (fx * f + fy * s) * sp, ny = S.y + (fy * f - fx * s) * sp;
    [S.x, S.y] = walk ? G.move(walk, S.x, S.y, nx, ny) : [nx, ny];
  }
  if (S.glide) glide(dt);
  if (S.anim) tween(dt);
  if (Math.abs(camera.fov - S.fovT) > 0.01) { camera.fov += (S.fovT - camera.fov) * Math.min(1, dt * 9); camera.updateProjectionMatrix(); }
  camera.position.set(S.x, EYE, -S.y);
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
  else if (/^Digit[1-9]$/.test(k)) jump(jumpList[+k.slice(5) - 1]?.id);
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
  if (dbl) { const t = targetOf(hit); if (t) walkTo(...t.p); }
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
    if (t) ring.position.set(t.p[0], (t.y ?? G.roomAt(rooms, ...t.p)?.floorZ ?? 0) + 0.012, -t.p[1]);
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

// ---------- dollhouse (orbit) ----------
const orbit = new OrbitControls(camera, canvas);
Object.assign(orbit, { enabled: false, enableDamping: true, dampingFactor: 0.08, maxPolarAngle: Math.PI * 0.47, minDistance: 1.5, maxDistance: 45 });
const cutPlanes = [new THREE.Plane(new THREE.Vector3(0, -1, 0), CUT)];     // drops ceilings and upper walls
const tmp = new THREE.Vector3();
// Section caps: in the dollhouse, back faces exposed by the cut plane are drawn flat dark grey first, then the
// normal pass draws front faces over them - cut walls read as solid poché instead of see-through shells.
const capMat = new THREE.MeshBasicMaterial({ color: 0x8f8a83, side: THREE.BackSide });
function setMode(m) {
  if (m === S.mode) return;
  S.mode = m; ptrs.clear(); pinch = null; S.anim = S.glide = null; document.exitPointerLock?.(); ring.visible = false; hoverDirty = true;
  camera.fov = FOV; camera.updateProjectionMatrix();     // the dollhouse zooms by distance; walk eases back to its own zoom
  document.body.classList.toggle('orbit', m === 'orbit');
  $('#mode-walk').setAttribute('aria-pressed', m === 'walk'); $('#mode-orbit').setAttribute('aria-pressed', m === 'orbit');
  scene.background = m === 'orbit' ? DARK : SKY;
  if (m === 'orbit') {
    renderer.clippingPlanes = cutPlanes;
    const [fx, fy] = G.yawDir(S.yaw);
    orbit.target.set(S.x, 0.6, -S.y); camera.position.set(S.x - fx * 6, 9, -(S.y - fy * 6));
    orbit.enabled = true; orbit.update();
  } else {
    renderer.clippingPlanes = []; orbit.enabled = false;
    const [tx, ty] = G.threeToPlan(orbit.target), p = walk ? G.nearestFree(walk, tx, ty) : [tx, ty];
    if (p) [S.x, S.y] = p;
    tmp.subVectors(orbit.target, camera.position); S.yaw = G.dirYaw(tmp.x, -tmp.z); S.pitch = 0;
  }
}
$('#mode-walk').onclick = () => setMode('walk');
$('#mode-orbit').onclick = () => setMode('orbit');

function teleport(x, y) {
  const p = walk ? G.nearestFree(walk, x, y, 2.5) : [x, y];
  if (!p) return;
  if (S.mode === 'walk') return goTo(p[0], p[1]);
  tmp.set(p[0], orbit.target.y, -p[1]).sub(orbit.target); orbit.target.add(tmp); camera.position.add(tmp); [S.x, S.y] = p;
}
function jump(id) {
  const v = vps[id], r = rooms.find((q) => q.id === id);
  if (!v || !r) return;
  if (S.mode === 'walk') return goTo(v.pos[0], v.pos[1], v.yaw);
  const [cx, cy] = G.centroid(r.polygon), xs = r.polygon.map((p) => p[0]), ys = r.polygon.map((p) => p[1]);
  const d = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) * 1.3 + 3;
  tmp.subVectors(camera.position, orbit.target).normalize(); tmp.y = Math.max(tmp.y, 0.8); tmp.normalize();   // keep a high view
  orbit.target.set(cx, 0.6, -cy); camera.position.copy(orbit.target).addScaledVector(tmp, d);
}

// ---------- plan panel ----------
const planEl = $('#plan'), planCanvas = $('#plan-canvas');
const plan = planJson || (house && {      // minimal fallback drawing from house.json until plan.json exists
  bounds: house.bounds, rooms, layers: [{ name: 'A-WALL', color: '#e8e8e8', paper: '#111111', lineweight: 0.35 }],
  entities: rooms.map((r) => ({ layer: 'A-WALL', type: 'polyline', pts: r.polygon, closed: true })) });
const planView = plan ? new PlanView(planCanvas, plan, {
  onPick: teleport,
  onHover: (x, y) => { $('#plan-xy').textContent = `X ${Math.round(x * 1000)}  Y ${Math.round(y * 1000)}`; },
}) : null;
if (!planView) $('.plan-empty').hidden = false;
if (plan?.sheet) $('#plan-title').textContent = [plan.sheet.title, plan.sheet.scale].filter(Boolean).join(' · ');
function togglePlan(force) {
  const c = planEl.classList.toggle('collapsed', force);
  $('#plan-toggle').setAttribute('aria-expanded', !c);
}
$('#plan-toggle').onclick = () => togglePlan();
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
for (const a of [$('#dl-dxf'), $('#dl-pdf')]) {
  fetch(a.getAttribute('href'), { method: 'HEAD' }).then((r) => { if (!r.ok) throw 0; })
    .catch(() => { a.setAttribute('aria-disabled', 'true'); a.removeAttribute('href'); a.title = 'Not generated yet'; });
}

// ---------- room buttons, help, gallery, hint ----------
const nav = $('#rooms');
const jumpList = rooms.filter((r) => vps[r.id]);
jumpList.forEach((r, i) => {
  const b = document.createElement('button'), k = document.createElement('kbd');
  b.type = 'button'; b.dataset.room = r.id; b.title = r.name; k.textContent = i + 1;
  b.append(r.name.split(' /')[0].replace(/ room$/i, ''), ' ', k); b.onclick = () => jump(r.id); nav.append(b);
});
function updateRoom(x, y) {
  const r = G.roomAt(rooms, x, y);
  if (r?.id === S.room?.id) return;
  S.room = r; $('#plan-room').textContent = r ? r.name : '';
  for (const b of nav.children) b.setAttribute('aria-current', b.dataset.room === r?.id);
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

// ---------- loop ----------
addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight, false);
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
  planView?.setViewer({ x: px, y: py, dir, hfov: G.hfov(camera.fov, camera.aspect) }, S.room);
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

// debug / test handle
window.viewer = { THREE, G, scene, camera, renderer, orbit, S, walk, rooms, vps, planView, setMode, teleport, jump, ix, walkTo, castAt, castRay, ring, roomLights,
  FOV, FOV_MIN, FOV_MAX,
  info: () => ({ mode: S.mode, x: S.x, y: S.y, yaw: S.yaw, room: S.room?.id ?? null, realtime, meshes: meshes.length,
    lightmapped: meshes.filter((m) => m.userData.baked).length, probed: meshes.filter((m) => !realtime && !m.userData.baked).length, glass: meshes.filter((m) => m.userData.glass).length }) };
