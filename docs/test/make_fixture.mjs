// node docs/test/make_fixture.mjs [--house spec/house.json] [--out build/e2e/assets2] [--plan build/plan_fx/plan.json]
// --plan: use that plan.json (and the house-plans.* beside it) instead of the outline drawing
// Schema-2 viewer fixture (blender/MULTILEVEL.md 12.g): a manifest that wraps today's docs/assets/home.glb as level G
// (lightmaps / probes of today's export, tagged level G), two tiny generated levels (X, 1: a few tagged boxes, to
// exercise streaming and cross-level switches), B and 2 without a GLB, house.json = the fixture, a plan.json schema 2
// drawn from the fixture (outlines only: one sheet per level + SITE), a generated equirect sky.
// The e2e server serves --assets first and falls back to docs/assets, so the GLB and the images are not copied.
// Run the schema-2 e2e with:  node docs/test/e2e.mjs --assets build/e2e/assets2
import { readFileSync, writeFileSync, mkdirSync, statSync, copyFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { deflateSync, crc32 } from 'node:zlib';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const HOUSE = resolve(ROOT, arg('--house', 'spec/house.json')), OUT = resolve(ROOT, arg('--out', 'build/e2e/assets2')), PLAN = arg('--plan') && resolve(ROOT, arg('--plan'));
const house = JSON.parse(readFileSync(HOUSE)), m1 = JSON.parse(readFileSync(resolve(ROOT, 'docs/assets/manifest.json')));
if (!house.levels?.length) throw new Error(`${HOUSE} is not a schema-2 house`);
mkdirSync(OUT, { recursive: true });
const write = (f, o) => writeFileSync(resolve(OUT, f), typeof o === 'string' || Buffer.isBuffer(o) ? o : JSON.stringify(o, null, 1));
const area = (p) => Math.abs(p.reduce((a, q, i) => a + q[0] * p[(i + 1) % p.length][1] - p[(i + 1) % p.length][0] * q[1], 0) / 2);
const bounds = (pts) => ({ minX: Math.min(...pts.map((p) => p[0])), minY: Math.min(...pts.map((p) => p[1])), maxX: Math.max(...pts.map((p) => p[0])), maxY: Math.max(...pts.map((p) => p[1])) });
const PSEUDO = ['front', 'side_passage', 'garden', 'shed'];
const ext = house.exterior;

// ---- two tiny generated levels, so progressive loading and incremental interactions are exercised: X holds a deck
// slab and a switch wired to the first-floor landing; level 1 (arriving later) holds that landing's lamp, a floor slab
// and a door leaf that blocks d_ensuite. Boxes in Blender coordinates, written as glTF (x, z, -y), extras as the export.
function gltf(boxes) {
  const parts = [], bufferViews = [], accessors = [], meshes = [], materials = [], nodes = [];
  let off = 0;
  const view = (arr, target) => { const b = Buffer.from(arr.buffer); parts.push(b); bufferViews.push({ buffer: 0, byteOffset: off, byteLength: b.length, target }); off += b.length; return bufferViews.length - 1; };
  for (const [name, min, max, extras, color, emissive] of boxes) {
    const lo = [min[0], min[2], -max[1]], hi = [max[0], max[2], -min[1]], c = lo.map((v, k) => (v + hi[k]) / 2), h = lo.map((v, k) => (hi[k] - v) / 2);
    const pos = [], nrm = [], idx = [];
    for (const [n, u, v] of [[0, 1, 2], [1, 2, 0], [2, 0, 1]]) for (const s of [1, -1]) {      // face normal axis n, tangents u x v = n
      const [a, b] = s > 0 ? [u, v] : [v, u], base = pos.length / 3;
      for (const [su, sv] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
        const p = c.slice(); p[n] += s * h[n]; p[a] += su * h[a]; p[b] += sv * h[b]; pos.push(...p);
        const q = [0, 0, 0]; q[n] = s; nrm.push(...q);
      }
      idx.push(base, base + 1, base + 2, base, base + 2, base + 3);
    }
    const P = view(new Float32Array(pos), 34962), N = view(new Float32Array(nrm), 34962), I = view(new Uint16Array(idx), 34963);
    accessors.push({ bufferView: P, componentType: 5126, count: 24, type: 'VEC3', min: lo, max: hi }, { bufferView: N, componentType: 5126, count: 24, type: 'VEC3' },
      { bufferView: I, componentType: 5123, count: 36, type: 'SCALAR' });
    materials.push({ name: `${name}.mat`, pbrMetallicRoughness: { baseColorFactor: [...color, 1], metallicFactor: 0, roughnessFactor: 0.8 }, ...(emissive ? { emissiveFactor: emissive } : {}) });
    meshes.push({ name, primitives: [{ attributes: { POSITION: accessors.length - 3, NORMAL: accessors.length - 2 }, indices: accessors.length - 1, material: materials.length - 1 }] });
    nodes.push({ name, mesh: meshes.length - 1, extras: { name, ...extras } });
  }
  const bin = Buffer.concat(parts);
  return { asset: { version: '2.0', generator: 'docs/test/make_fixture.mjs' }, scene: 0, scenes: [{ nodes: nodes.map((_, i) => i) }], nodes, meshes, materials,
    accessors, bufferViews, buffers: [{ byteLength: bin.length, uri: `data:application/octet-stream;base64,${bin.toString('base64')}` }] };
}
mkdirSync(resolve(OUT, 'glb'), { recursive: true });
const ixs = (o) => JSON.stringify(o);
write('glb/X.gltf', gltf([
  ['garden.test_deck', [-0.75, 17.36, -0.1], [3.4, 20.5, -0.05], { room: 'garden', level: 'X', lm: 'static' }, [0.32, 0.24, 0.18]],
  ['garden.switch_test', [1.9, 17.37, 1.2], [1.98, 17.39, 1.28], { room: 'garden', level: 'X', lm: 'dynamic', ix: ixs({ t: 'light', rooms: ['landing1_rear'], label: 'Landing lights' }) }, [0.9, 0.9, 0.9]],
  ['neighbours.test_block', [-1.2, 16.0, 0], [-0.9, 16.3, 2.0], { room: 'neighbours', level: 'X', lm: 'static' }, [0.6, 0.55, 0.5]],   // no probe of its own: an exterior one
]));
// an exterior probe for the garden (a copy of a real probe under its own name, so the texture is told apart)
mkdirSync(resolve(OUT, 'probes'), { recursive: true });
copyFileSync(resolve(ROOT, 'docs/assets/probes/vestibule.jpg'), resolve(OUT, 'probes/garden.jpg'));
write('glb/1.gltf', gltf([
  ['landing1_rear.test_floor', [-0.65, 8.83, 2.99], [0.25, 11.5, 3.04], { room: 'landing1_rear', level: '1', lm: 'static' }, [0.5, 0.48, 0.45]],
  ['landing1_rear.lamp_test', [-0.3, 10.0, 5.4], [-0.1, 10.2, 5.45], { room: 'landing1_rear', level: '1', lm: 'dynamic' }, [1, 1, 1], [1, 0.8, 0.5]],
  ['blue_ensuite.door_test', [1.34, 12.88, 3.04], [2.026, 12.92, 5.02], { room: 'blue_ensuite', level: '1', lm: 'static',
    ix: ixs({ t: 'hinge', g: 'blue_ensuite.door_test', p: [1.34, 12.9, 3.04], a: [0, 0, 1], deg: 90, blocks: 'd_ensuite', label: 'Door' }) }, [0.55, 0.4, 0.25]],
]));

// ---- manifest schema 2 (section 10) ----
const cutZ = (lv) => Math.min(...house.rooms.filter((r) => r.level === lv && r.kind === 'room').map((r) => r.ceilingZ)) - 0.07;
const glbBytes = statSync(resolve(ROOT, 'docs/assets/home.glb')).size;
const GLB = { G: 'home.glb', X: 'glb/X.gltf', 1: 'glb/1.gltf' }, size = (id) => (id === 'G' ? glbBytes : GLB[id] ? statSync(resolve(OUT, GLB[id])).size : 0);
const levels = [...house.levels.map((l) => ({ id: l.id, name: l.name, datumZ: l.datumZ, cutZ: +cutZ(l.id).toFixed(3),
  glb: GLB[l.id] ?? null, bytes: size(l.id), triangles: l.id === 'G' ? m1.glb?.triangles ?? 0 : GLB[l.id] ? 36 : 0,
  rooms: house.rooms.filter((r) => r.level === l.id).map((r) => r.id) })),
{ id: 'X', name: 'Outside', datumZ: -0.3, cutZ: null, glb: GLB.X, bytes: size('X'), triangles: 24, rooms: [...PSEUDO, 'facade', 'roof', 'neighbours'] }];
const largestZone = (room) => ext.zones.filter((z) => z.room === room && z.walk !== false).sort((a, b) => area(b.polygon) - area(a.polygon))[0];
const site = PSEUDO.map((id) => {
  if (id === 'shed') { const w = ext.buildings[0].rooms.find((r) => r.walk); return { id, level: 'X', kind: 'site', name: 'Shed / workshop', polygon: w.polygon, floorZ: w.floorZ, ceilZ: null }; }
  const z = largestZone(id);
  return { id, level: 'X', kind: 'site', name: { front: 'Front / parking', side_passage: 'Side passage', garden: 'Garden' }[id], polygon: z.polygon, floorZ: z.z, ceilZ: null };
});
const tagG = (list) => (list || []).map((e) => ({ ...e, level: 'G' }));
const manifest = { schema: 2, levels, loadOrder: ['G', 'X', '1', '2', 'B'],
  rooms: [...house.rooms.map((r) => ({ id: r.id, level: r.level, kind: r.kind, name: r.name, polygon: r.polygon, floorZ: r.floorZ, ceilZ: r.ceilingZ ?? null })), ...site],
  lightmaps: tagG(m1.lightmaps), lightmapsOff: tagG(m1.lightmapsOff), probesOff: tagG(m1.probesOff),
  probes: [...tagG(m1.probes), { room: 'garden', level: 'X', image: 'probes/garden.jpg', pos: [1.3, 18.9, 1.45], intensity: 1.0 }],
  viewpoints: m1.viewpoints, spawn: { pos: house.spawn, yaw: 0, level: 'G' },
  toneMapping: m1.toneMapping, exposure: m1.exposure, whiteBalance: m1.whiteBalance,
  sky: { image: 'sky.png', color: '#8fb4d9', sunDir: [0.429, -0.807, 0.407] },
  firstView: { bytes: glbBytes, files: ['home.glb'] }, encoding: m1.encoding,
  fixture: 'docs/test/make_fixture.mjs: phase-1 home.glb as level G over the schema-2 house; X and 1 are tiny generated test levels' };
write('manifest.json', manifest);
write('house.json', readFileSync(HOUSE));

// ---- sky: 512 x 256 equirect gradient PNG (zenith blue to a warm horizon, darker ground), centre = +X ----
{
  const W = 512, H = 256, raw = Buffer.alloc((W * 3 + 1) * H);
  for (let y = 0; y < H; y++) {
    raw[y * (W * 3 + 1)] = 0;
    const el = (0.5 - y / H) * Math.PI;      // +pi/2 at the top
    for (let x = 0; x < W; x++) {
      const t = Math.max(0, Math.sin(el)), c = el >= 0 ? [143 + (60 - 143) * t ** 0.6, 180 + (120 - 180) * t ** 0.6, 217 + (190 - 217) * t ** 0.6].map((v, i) => v + (1 - t) ** 8 * [70, 45, 10][i])
        : [92, 88, 80];
      for (let k = 0; k < 3; k++) raw[y * (W * 3 + 1) + 1 + x * 3 + k] = Math.max(0, Math.min(255, Math.round(c[k])));
    }
  }
  const chunk = (type, data) => { const len = Buffer.alloc(4), crc = Buffer.alloc(4), td = Buffer.concat([Buffer.from(type), data]); len.writeUInt32BE(data.length); crc.writeUInt32BE(crc32(td)); return Buffer.concat([len, td, crc]); };
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(W, 0); ihdr.writeUInt32BE(H, 4); ihdr[8] = 8; ihdr[9] = 2;
  write('sky.png', Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]));
}

// ---- plan.json schema 2 (section 11.1): outlines only, one sheet per level + SITE, world coordinates ----
const L = (name, color, paper, lineweight) => ({ name, color, paper, lineweight });
const layers = [L('A-WALL', '#e8e8e8', '#111111', 0.35), L('A-STRS', '#ffff00', '#111111', 0.18), L('A-ANNO-TEXT', '#e8e8e8', '#111111', 0.18),
  L('L-SITE', '#00ff00', '#333333', 0.18), L('L-SITE-BNDY', '#ff0000', '#333333', 0.25), L('A-ROOF', '#808080', '#666666', 0.18)];
const cen = (p) => [p.reduce((a, q) => a + q[0], 0) / p.length, p.reduce((a, q) => a + q[1], 0) / p.length];
const poly = (layer, pts, extra = {}) => ({ layer, type: 'polyline', pts, closed: true, ...extra });
const text = (p, s, h) => ({ layer: 'A-ANNO-TEXT', type: 'text', p, h, text: s, align: 'center' });
const sheet = (id, title, scale, ents, rms, k) => {
  const pts = ents.flatMap((e) => e.pts || [e.p1, e.p2].filter(Boolean));
  const b = id === 'X' ? { minX: -1.18, minY: -5.5, maxX: 5.73, maxY: 29.2 } : bounds(pts);
  if (id !== 'X') Object.assign(b, { minX: b.minX - 0.6, minY: b.minY - 0.6, maxX: b.maxX + 0.6, maxY: b.maxY + 0.6 });
  return { id, level: id, title, scale, paper: 'A3', orientation: 'portrait', bounds: b, houseBounds: house.bounds, sheetBounds: b,
    linestyles: { dashed: [0.12 * k, 0.06 * k] }, hatch: { spacing: 0.09 * k }, dimstyle: { h: 0.174 * k, tick: 0.065 * k, extGap: 0.06 * k, extBeyond: 0.08 * k },
    dxfOffset: [0, 0], entities: ents, rooms: rms };
};
const TITLE = { B: 'BASEMENT PLAN', G: 'GROUND FLOOR PLAN', 1: 'FIRST FLOOR PLAN', 2: 'SECOND FLOOR PLAN' };
const sheets = house.levels.map(({ id }) => {
  const rs = house.rooms.filter((r) => r.level === id), ents = [];
  for (const r of rs) { ents.push(poly('A-WALL', r.polygon)); ents.push(text(cen(r.polygon), r.name.split(/ \(| \//)[0].toUpperCase(), 0.12)); }
  for (const s of house.stairs.filter((q) => q.walk && (house.rooms.find((r) => r.id === q.fromRoom)?.level === id || house.rooms.find((r) => r.id === q.toRoom)?.level === id))) {
    ents.push(poly('A-STRS', s.walk.polygon));
    for (const [a, b] of s.walk.risers) ents.push({ layer: 'A-STRS', type: 'line', p1: a, p2: b });
  }
  return sheet(id, TITLE[id], '1:50', ents, rs.map((r) => ({ id: r.id, name: r.name.toUpperCase(), polygon: r.polygon, floorZ: r.floorZ, area: +area(r.polygon).toFixed(1) })), 1);
});
{
  const ents = [poly('L-SITE-BNDY', ext.plot.polygon, { ls: 'dashed' })];
  for (const z of ext.zones) { ents.push(poly('L-SITE', z.polygon)); ents.push(text(cen(z.polygon), z.id.toUpperCase().replace(/_/g, ' '), 0.25)); }
  for (const b of ext.envelope.blocks) for (const l of b.levels) if (l.level === 'G') ents.push(poly('A-WALL', l.polygon));
  for (const w of ext.buildings[0].walls) ents.push({ layer: 'A-WALL', type: 'line', p1: w.a, p2: w.b });
  for (const b of ext.boundaries) if (b.line) ents.push({ layer: 'L-SITE-BNDY', type: 'line', p1: b.line[0], p2: b.line[b.line.length - 1] });
  sheets.push(sheet('X', 'SITE PLAN', '1:100', ents, [], 2));
}
write('plan.json', PLAN ? readFileSync(PLAN) : { schema: 2, units: 'm', layers, textNote: 'viewer test fixture (outlines only)', footprintSource: 'none', sheets });
// the download buttons: stand-ins with the right magic (the real files come from tools/plan)
for (const [from, to] of [['ground-floor-plan.dxf', 'house-plans.dxf'], ['ground-floor-plan.pdf', 'house-plans.pdf']]) {
  const src = PLAN && existsSync(resolve(PLAN, '..', to)) ? resolve(PLAN, '..', to) : resolve(ROOT, 'docs/assets', from);
  if (existsSync(src)) copyFileSync(src, resolve(OUT, to));
}
console.log(`fixture written to ${OUT}: ${levels.length} levels (G = home.glb ${(glbBytes / 1e6).toFixed(1)} MB), ${manifest.rooms.length} rooms, ${sheets.length} plan sheets`);
