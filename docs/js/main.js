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
const schema2 = Array.isArray(manifest?.levels) && manifest.levels.length > 0;
const LEVELS = schema2 ? manifest.levels : [{ id: 'G', name: 'Ground floor', datumZ: 0, cutZ: CUT, glb: 'home.glb' }];
const level = (id) => LEVELS.find((l) => l.id === id);
const ORDER = [...new Set([...(schema2 && manifest.loadOrder || []), ...LEVELS.map((l) => l.id)])].filter(level);
const levelName = (id) => level(id)?.name || house?.levels?.find((l) => l.id === id)?.name || (id === 'X' ? 'Outside' : id);
const realtime = qs.get('lighting') === 'realtime' || !manifest?.lightmaps?.length;
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
function prepare(model) {
  const mine = [];
  model.traverse((o) => o.isMesh && mine.push(o));
  for (const o of mine) mapMats(o, (m) => {
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
  model.traverse((o) => { for (const n of [o.userData.name, o.name]) if (n && !byName.has(n)) byName.set(n, o); });   // names are unique across levels
  meshes.push(...mine);
  return mine;
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
const IBL_DIFFUSE = 'iblIrradiance += getIBLIrradiance( geometryNormal );', LM_LINE = 'vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;';
const SPEC_ONLY_CHUNK = THREE.ShaderChunk.lights_fragment_maps.replace(IBL_DIFFUSE, 'iblIrradiance += ( 1.0 - lmMix ) * lmProbe * getIBLIrradiance( geometryNormal );')
  .replace(LM_LINE, 'vec3 lightMapIrradiance = lmMix * mix( texture2D( lightMapOff, vLightMapUv ).rgb * lightMapOffIntensity, lightMapTexel.rgb * lightMapIntensity, lmOn );');
if (SPEC_ONLY_CHUNK.includes(IBL_DIFFUSE)) console.warn('three.js shader changed: lightmapped surfaces are lit twice');
if (!SPEC_ONLY_CHUNK.includes('lmOn')) console.warn('three.js shader changed: light switches cannot dim the bake');
const specOnly = (sh) => {
  sh.fragmentShader = sh.fragmentShader.replace('#include <lights_fragment_maps>', SPEC_ONLY_CHUNK)
    .replace('#include <lightmap_pars_fragment>', '#include <lightmap_pars_fragment>\nuniform sampler2D lightMapOff;\nuniform float lightMapOffIntensity;\nuniform float lmOn;\nuniform float lmMix;\nuniform float lmProbe;');
};
// Per-room light state shared by the bake materials (lmOn, the lights-off map), probe reflections, realtime lamps and
// lamp emissives; interact.js eases `on` toward `target`. ratio / pratio = brightness of the lights-off lightmap /
// probe relative to the lights-on one; wait > 0 holds the fade while the lights-off images load.
const roomLights = new Map();
const roomLight = (id) => roomLights.get(id) || roomLights.set(id, { on: { value: 1 }, target: 1, ratio: 0.12, mats: [], lamps: [], ems: [],
  uOff: { value: null }, uOffK: { value: 0 } }).get(id);
const lightF = (L) => { const r = L.pratio ?? L.ratio; return r + (1 - r) * L.on.value; };
function meanLinear(img) {             // mean linear value of an 8-bit sRGB image, from a 32x32 thumbnail
  const c = Object.assign(document.createElement('canvas'), { width: 32, height: 32 }), g = c.getContext('2d', { willReadFrequently: true });
  g.drawImage(img, 0, 0, 32, 32);
  const d = g.getImageData(0, 0, 32, 32).data; let s = 0;
  for (let i = 0; i < d.length; i += 4) for (let j = 0; j < 3; j++) { const v = d[i + j] / 255; s += v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }
  return s / (d.length * 0.75);
}
const ratioOf = (a, ka, b, kb) => Math.min(1, Math.max(0.01, (meanLinear(a.image) * ka) / Math.max(1e-6, meanLinear(b.image) * kb)));
const texCache = new Map();
function loadTex(u, atlas = false) {   // once per file; on phones an atlas over 2048 px is drawn down to 2048 on load
  if (!texCache.has(u)) texCache.set(u, texLoader.loadAsync('assets/' + u).then((t) => {
    const im = t.image, s = touch && atlas ? 2048 / Math.max(im.width, im.height) : 1;
    if (s < 1) { const c = Object.assign(document.createElement('canvas'), { width: Math.round(im.width * s), height: Math.round(im.height * s) }); c.getContext('2d').drawImage(im, 0, 0, c.width, c.height); t.image = c; }
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
// first use of a switch: load the lights-off lightmap and probe of the rooms it controls; the fade waits for them
function ensureOff(ids) {
  if (realtime) return;
  for (const id of ids) {
    const L = roomLight(id);
    if (L.offP) continue;
    const lmo = (manifest.lightmapsOff || []).find((q) => q.room === id), pro = (manifest.probesOff || []).find((q) => q.room === id);
    L.wait = (L.wait || 0) + 1;
    L.offP = Promise.all([lmo && loadTex(lmo.image, true), pro && loadTex(pro.image)]).then(([t, pt]) => {
      if (t) L.off = { tex: t, k: Math.PI * (lmo.intensity ?? 1) };
      if (pt) L.probeOff = { tex: pt, k: pro.intensity ?? 1 };
      syncOff(L);
    }).finally(() => { L.wait--; });
  }
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
          const u = { lightMapOff: lm.L.uOff, lightMapOffIntensity: lm.L.uOffK, lmOn: lm.L.on, lmMix: { value: 1 }, lmProbe: { value: 1 } };
          Object.assign(c, { lightMap: lm.tex, lightMapIntensity: lm.k, onBeforeCompile: (sh) => { specOnly(sh); Object.assign(sh.uniforms, u); } });
        }
        if (Lp) Lp.mats.push({ m: c, k });
        matCache.set(key, c);
      }
      return matCache.get(key);
    });
    o.userData.baked = !!lm;        // not "lm": the GLB extras already use userData.lm = 'static' | 'dynamic'
  }
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
  if (gl.s >= gl.L) S.glide = null;
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
ix = initInteract({ walk, roomLight, castRay, emissiveToView: (c) => (wbInv ? c.applyMatrix3(wbInv) : c), feetY: () => S.z, onLights: ensureOff, lmProbe: lmProbeScale,
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
  else if (/^Digit[1-9]$/.test(k)) jump(curGroup()[+k.slice(5) - 1]?.id);          // rooms of the floor you are on
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
const dollLevelOf = (lv) => (HOUSE_LEVELS.includes(lv) ? lv : 'G');           // outside -> the ground floor
function setDollLevel(id) {             // a level id or 'all'
  dhLevel = id;
  const lv = level(id), all = id === 'all';
  cutY = all ? Infinity : lv?.cutZ ?? CUT;
  cutPlanes[0].constant = cutY;
  renderer.clippingPlanes = S.mode === 'orbit' && !all ? cutPlanes : [];
  const out = levelScenes.get('X');
  if (out) out.visible = !(S.mode === 'orbit' && id === 'B');        // the lawn and shed would float beside the basement
  if (S.mode === 'orbit' && lv) { const dy = (lv.datumZ ?? 0) - orbit.target.y; orbit.target.y += dy; camera.position.y += dy; }
  for (const b of dhEl.children) b.setAttribute('aria-pressed', b.dataset.level === id);
  hoverDirty = true;
}
const dhEl = $('#dh-levels');
if (schema2 && HOUSE_LEVELS.length > 1) {
  dhEl.hidden = false;
  for (const id of [...HOUSE_LEVELS, 'all']) {
    const b = Object.assign(document.createElement('button'), { type: 'button', textContent: id === 'all' ? 'All' : id, title: id === 'all' ? 'Whole house' : `Cut above: ${levelName(id)}` });
    b.dataset.level = id; b.onclick = () => setDollLevel(id); dhEl.append(b);
  }
}
function setMode(m) {
  if (m === S.mode) return;
  S.mode = m; ptrs.clear(); pinch = null; S.anim = S.glide = null; fadeEl.style.opacity = '0'; document.exitPointerLock?.(); ring.visible = false; hoverDirty = true;
  camera.fov = FOV; camera.updateProjectionMatrix();     // the dollhouse zooms by distance; walk eases back to its own zoom
  document.body.classList.toggle('orbit', m === 'orbit');
  $('#mode-walk').setAttribute('aria-pressed', m === 'walk'); $('#mode-orbit').setAttribute('aria-pressed', m === 'orbit');
  scene.background = m === 'orbit' ? DARK : SKY;
  if (m === 'orbit') {
    const id = dollLevelOf(S.level), d = level(id)?.datumZ ?? 0, [fx, fy] = G.yawDir(S.yaw);
    orbit.target.set(S.x, d, -S.y); camera.position.set(S.x - fx * 6, d + 9, -(S.y - fy * 6));
    orbit.enabled = true; orbit.update();
    setDollLevel(id);
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
  onPick: (x, y) => { const L = sheetLayer(); if (S.mode === 'orbit' && schema2) setDollLevel(dollLevelOf(L)); teleport(x, y, hasLayer(L) ? L : S.layer); },
  onHover: (x, y) => { $('#plan-xy').textContent = `X ${Math.round(x * 1000)}  Y ${Math.round(y * 1000)}`; },
}) : null;
if (!planView) $('.plan-empty').hidden = false;
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
const nav = $('#rooms'), groupOf = new Map();
const jumpList = rooms.filter((r) => vps[r.id]);
const LV_TAG = { B: 'B', G: 'G', 1: '1F', 2: '2F', X: 'OUT' };
for (const lv of [...new Set([...(house?.levels || []).map((l) => l.id), 'G', 'X'])]) {
  const list = jumpList.filter((r) => r.level === lv);
  if (!list.length) continue;
  const grp = Object.assign(document.createElement('div'), { className: 'grp' });
  grp.dataset.level = lv; grp.setAttribute('role', 'group'); grp.setAttribute('aria-label', levelName(lv));
  if (house?.levels?.length) grp.append(Object.assign(document.createElement('span'), { className: 'lv', textContent: LV_TAG[lv] ?? lv, title: levelName(lv) }));
  list.forEach((r, i) => {
    const b = document.createElement('button'), k = document.createElement('kbd');
    b.type = 'button'; b.dataset.room = r.id; b.title = r.name; k.textContent = i + 1;
    b.append(r.name.split(/ \/| \(| and /)[0].replace(/ room$/i, ''), ' ', k); b.onclick = () => jump(r.id); grp.append(b);   // short name, full one in title
  });
  nav.append(grp); groupOf.set(lv, list);
}
const curGroup = () => groupOf.get(S.level) || groupOf.get('G') || [...groupOf.values()][0] || [];
// the floor you are on changed: the plan sheet follows (a tab click overrides until the next change), its tab and room
// group are marked, the dollhouse cut follows in the dollhouse
function onLevel(lv) {
  if (!lv || lv === S.level) return;
  S.level = lv;
  if (planView?.sheets.some((s) => s.id === lv)) showSheet(lv);
  for (const b of tabsEl.children) b.classList.toggle('here', b.dataset.sheet === lv);
  const cur = groupOf.has(lv) ? lv : 'G';
  for (const g of nav.children) g.classList.toggle('cur', g.dataset.level === cur);
  if (groupOf.size > 1) nav.querySelector('.grp.cur')?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
}
function updateRoom(x, y) {
  const L = S.mode === 'walk' || dhLevel === 'all' ? S.layer : G.layerOfLevel(dhLevel);
  const h = walk && (G.cellAt(walk, L, x, y) || (S.mode === 'orbit' ? G.cellAt(walk, 'G', x, y) : null));
  onLevel(S.mode === 'orbit' && dhLevel !== 'all' ? dhLevel : h?.level || S.level || 'G');
  const r = h ? rooms.find((q) => q.id === h.room) || null : walk ? null : G.roomAt(rooms, x, y);
  if (r?.id === S.room?.id) return;
  S.room = r; $('#plan-room').textContent = r ? r.name : '';
  for (const b of nav.querySelectorAll('button')) b.setAttribute('aria-current', b.dataset.room === r?.id);
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
  else await applyBake(id, mine);
  root.add(model); levelScenes.set(id, model);
  if (id === 'X') model.visible = !(S.mode === 'orbit' && dhLevel === 'B');
  ix.add(model); ixLevels.push(id);     // its doors, switches and lamps work from now on
  hoverDirty = true;
  return true;
}
try { await loadLevel(ORDER[0], (e) => progress(e.loaded, e.total)); }
catch (err) { msg.textContent = 'The 3D model is not available yet.'; bar.parentElement.classList.remove('indet'); throw err; }

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
  if (planView) {                       // marker on the sheet of the visitor's floor, and always on SITE (hollow indoors)
    const sl = planView.sheet.level ?? planView.sheetId, multi = planView.sheets.length > 1;
    const mark = !multi || sl === S.level ? 'full' : planView.sheetId === 'X' ? 'hollow' : null;
    planView.setViewer({ x: px, y: py, dir, hfov: G.hfov(camera.fov, camera.aspect), mark }, S.room);
  }
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

// debug / test handle
window.viewer = { THREE, G, scene, camera, renderer, orbit, S, walk, rooms, vps, planView, setMode, teleport, jump, ix, walkTo, castAt, castRay, ring, roomLights,
  FOV, FOV_MIN, FOV_MAX, LEVELS, ORDER, levelScenes, ixLevels, setDollLevel, streaming, schema2, targetOf, lmProbeScale,
  info: () => ({ mode: S.mode, x: S.x, y: S.y, z: S.z, layer: S.layer, level: S.level, yaw: S.yaw, room: S.room?.id ?? null, sheet: planView?.sheetId ?? null,
    realtime, meshes: meshes.length, lightmapped: meshes.filter((m) => m.userData.baked).length, probed: meshes.filter((m) => !realtime && !m.userData.baked).length,
    glass: meshes.filter((m) => m.userData.glass).length, eye: camera.position.y - S.z }) };
