// Pure geometry for the viewer (no three.js import) - node-tested by docs/test/geom.test.mjs.
// House frame (spec/house.json): metres, x right, y into the house (rear drawn UP the plan), z up.
// glTF/three frame: (x, z, -y). So plan (x, y) = (three.x, -three.z).
// Yaw convention used everywhere here: degrees/radians CCW seen from above, 0 = facing +Y (into the house).
// Walk layers (blender/MULTILEVEL.md 11.2): collision stays 2D; a layer is a set of cells that never overlap in plan
// (levels B G 1 2 + one per stair flight; the outside is part of G), joined by portals; the visitor is on one layer.

export const threeToPlan = (p) => [p.x, -p.z];
export const planToThree = (x, y, h = 0) => ({ x, y: h, z: -y });
// three camera rotation.y (order YXZ) IS the house yaw: forward (0,0,-1) rotated by +a about +Y -> plan (-sin a, cos a).
export const yawDir = (yaw) => [-Math.sin(yaw), Math.cos(yaw)];
export const dirYaw = (dx, dy) => Math.atan2(-dx, dy);
export const hfov = (vfovDeg, aspect) => 2 * Math.atan(Math.tan((vfovDeg * Math.PI) / 360) * aspect);

export function pointInPoly(x, y, poly) {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}

export function polyArea(poly) {
  let a = 0;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) a += poly[j][0] * poly[i][1] - poly[i][0] * poly[j][1];
  return a / 2;
}

export function centroid(poly) {
  let a = 0, cx = 0, cy = 0;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const f = poly[j][0] * poly[i][1] - poly[i][0] * poly[j][1];
    a += f; cx += (poly[j][0] + poly[i][0]) * f; cy += (poly[j][1] + poly[i][1]) * f;
  }
  return a ? [cx / (3 * a), cy / (3 * a)] : poly[0].slice();
}

export function segDist(px, py, ax, ay, bx, by) {
  const dx = bx - ax, dy = by - ay, l2 = dx * dx + dy * dy;
  const t = l2 ? Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / l2)) : 0;
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
}

export function edgeDist(x, y, poly) {
  let d = Infinity;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) d = Math.min(d, segDist(x, y, ...poly[j], ...poly[i]));
  return d;
}
const polyDist = (x, y, poly) => (pointInPoly(x, y, poly) ? 0 : edgeDist(x, y, poly));
// convex hull of plan points (monotone chain) -> CCW polygon
export function hull(pts) {
  const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  if (p.length < 3) return p;
  const lo = [], up = [];
  for (const q of p) { while (lo.length > 1 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.reverse()) { while (up.length > 1 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}
const edges = (poly) => poly.map((p, i) => [p, poly[(i + 1) % poly.length]]);
const bbox = (poly) => { const xs = poly.map((p) => p[0]), ys = poly.map((p) => p[1]); return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]; };
const BB = new WeakMap(), bbOf = (poly) => BB.get(poly) || BB.set(poly, bbox(poly)).get(poly);
const inTol = (x, y, poly) => {                    // containment with 1 mm tolerance: zones and treads share edges
  const b = bbOf(poly);
  if (x < b[0] - 1e-3 || y < b[1] - 1e-3 || x > b[2] + 1e-3 || y > b[3] + 1e-3) return false;
  return pointInPoly(x, y, poly) || edgeDist(x, y, poly) < 1e-3;
};

export const roomAt = (rooms, x, y) => rooms.find((r) => pointInPoly(x, y, r.polygon)) || null;

// ---- house.json (schema 1 or 2) ----
export const PSEUDO_ROOMS = ['front', 'side_passage', 'garden', 'shed', 'facade', 'roof', 'neighbours'];
const kindOf = (r) => r.kind || (r.id === 'stairs' ? 'stairwell' : 'room');     // schema 1: the stairs were never walked
const stairsOf = (house) => (Array.isArray(house.stairs) ? house.stairs : []);  // schema 1: one dict, no flights
// level of a room id: house room -> its level (schema 1: G); pseudo-rooms and building rooms -> X; unknown -> G
export function levelOf(house, id) {
  const r = (house?.rooms || []).find((q) => q.id === id);
  if (r) return r.level || 'G';
  if (PSEUDO_ROOMS.includes(id)) return 'X';
  for (const b of house?.exterior?.buildings || []) if (b.room === id || b.id === id || (b.rooms || []).some((q) => q.id === id)) return 'X';
  return 'G';
}
export const layerOfLevel = (lv) => (lv === 'X' ? 'G' : lv);
// surface Z of a zone at (x, y): `fall` = linear between two points, clamped (MULTILEVEL.md gap 5)
export function zoneZ(zone, x, y) {
  const f = zone.fall;
  if (!f || x === undefined) return zone.z ?? 0;
  const dx = f.to[0] - f.from[0], dy = f.to[1] - f.from[1], l2 = dx * dx + dy * dy;
  const t = l2 ? Math.max(0, Math.min(1, ((x - f.from[0]) * dx + (y - f.from[1]) * dy) / l2)) : 0;
  return f.z[0] + t * (f.z[1] - f.z[0]);
}
// treads of a `steps` stair: strips between consecutive riser lines, z = fromZ +- (k + 1) * rise
function stepTreads(s) {
  const R = s.riserLines || [], sg = Math.sign((s.toZ ?? 0) - (s.fromZ ?? 0)) || 1, out = [];
  for (let k = 0; k + 1 < R.length; k++) out.push({ polygon: [...R[k], ...R[k + 1].slice().reverse()], z: s.fromZ + sg * (k + 1) * s.rise });
  return out;
}

// ---- walkable area: cells inset by the body radius, joined by portals through open doorways ----
// Body radius: small enough for the 0.61 m doors and the gaps round the dining table, still > the distance from the
// eye to the near-plane corners at 90 deg fov on a 2.4:1 screen (0.14 m), so the camera never clips into a wall.
export const BODY = 0.15;
const PASSABLE = new Set(['door', 'double_door', 'french_door', 'arch', 'opening']);
const HEADROOM = 1.25;           // under sloped ceilings a point with less headroom is not free (loft knee walls)

// rect around a wall opening: along = clear width minus the body, across = wall thickness + body + overlap
function portalFor(o, wall, r) {
  const [ax, ay] = wall.a, [bx, by] = wall.b, L = Math.hypot(bx - ax, by - ay);
  const ux = (bx - ax) / L, uy = (by - ay) / L, nx = -uy, ny = ux;
  const ha = Math.max(0.04, o.width / 2 - r), hc = (wall.thickness || 0) / 2 + r + 0.05;
  const [cx, cy] = o.center;
  const p = (s, t) => [cx + ux * s + nx * t, cy + uy * s + ny * t];
  return { id: o.id, center: [cx, cy], normal: [nx, ny], depth: (wall.thickness || 0) / 2,
    width: o.width, poly: [p(-ha, -hc), p(ha, -hc), p(ha, hc), p(-ha, hc)], open: o.openAngle !== 0 };
}

// house = house.json (schema 1 or 2). obstacles / soft = {layer: [[x, y], ...polygons]} (an array = layer G), the
// furniture footprints from obstaclesFrom; soft ones are walked through, slowed. Returns the structure of 11.2.
export function buildWalk(house, { radius = BODY, obstacles = {}, soft = {} } = {}) {
  const r = radius, ext = house.exterior || {};
  const stairs = stairsOf(house), flights = stairs.filter((s) => s.kind === 'flight' && s.walk), steps = stairs.filter((s) => s.kind === 'steps');
  const levels = house.levels?.length ? house.levels.map((l) => l.id) : ['G'];
  const layers = [...levels, ...flights.map((f) => f.id)];
  const roomById = new Map((house.rooms || []).map((q) => [q.id, q]));
  const lv = (id) => levelOf(house, id);
  const cells = [];
  for (const rm of house.rooms || []) {                    // 1. level cells: rooms of kind room / exterior
    if (!['room', 'exterior'].includes(kindOf(rm))) continue;
    const c = { id: rm.id, layer: lv(rm.id), level: lv(rm.id), kind: 'room', room: rm.id, polygon: rm.polygon, z: rm.floorZ ?? 0, ...(kindOf(rm) === 'exterior' ? { ext: true } : {}) };
    const tr = steps.filter((s) => s.toRoom === rm.id).flatMap(stepTreads);
    if (tr.length) c.treads = tr;
    if (rm.ceiling?.type === 'planes') c.planes = rm.ceiling.planes;
    cells.push(c);
  }
  for (const b of ext.buildings || []) for (const br of b.rooms || []) {   // walkable building rooms: cells of G
    if (br.walk) cells.push({ id: br.id, layer: 'G', level: 'X', kind: 'room', room: b.room || b.id, polygon: br.polygon, z: br.floorZ ?? 0 });
  }
  const byArea = (a, b) => Math.abs(polyArea(a.polygon)) - Math.abs(polyArea(b.polygon));
  const bWalls = (ext.buildings || []).flatMap((b) => b.walls || []), bOpenings = (ext.buildings || []).flatMap((b) => b.openings || []);
  const gates = [];
  if ((ext.zones || []).length) {                            // 2. the ground cell (layer G)
    const blockers = [], seg = (a, b, half = 0, portal) => blockers.push(portal ? { a, b, half, portal } : { a, b, half });
    for (const blk of ext.envelope?.blocks || []) for (const l of blk.levels || []) if (l.level === 'G') edges(l.polygon).forEach(([a, b]) => seg(a, b));
    for (const bd of ext.boundaries || []) {
      const half = (bd.thickness ?? (bd.type === 'neighbour_wall' ? 0 : 0.06)) / 2;
      if (bd.line) for (let k = 1; k < bd.line.length; k++) seg(bd.line[k - 1], bd.line[k], half, bd.type === 'gate' ? bd.id : undefined);
      if (bd.polygon) edges(bd.polygon).forEach(([a, b]) => seg(a, b));
      if (bd.type === 'gate' && bd.line) gates.push({ bd, half });
    }
    for (const w of bWalls) seg(w.a, w.b, (w.thickness || 0) / 2);
    for (const n of ext.neighbours || []) for (const p of n.polygon ? [n.polygon] : (n.parts || []).map((q) => q.polygon)) if (p) edges(p).forEach(([a, b]) => seg(a, b));
    cells.push({ id: 'ground', layer: 'G', level: 'X', kind: 'ground',
      zones: ext.zones.filter((z) => z.walk !== false).map((z) => ({ id: z.id, room: z.room, polygon: z.polygon, z: z.z ?? 0, ...(z.fall ? { fall: z.fall } : {}) })).sort(byArea),
      treads: (ext.steps || []).flatMap((s) => s.treads || []).map((t) => ({ polygon: t.polygon, z: t.z })).sort(byArea), blockers });
  }
  for (const f of flights) {                                 // 3. flight layers: one ramp cell each
    cells.push({ id: f.id, layer: f.id, level: [lv(f.fromRoom), lv(f.toRoom)], kind: 'flight', polygon: f.walk.polygon,
      fromZ: f.fromZ, toZ: f.toZ, risers: f.walk.risers, through: f.through || [f.fromRoom] });
  }
  // portals: doorways whose two ends resolve to cells (a walkable room, outside -> ground, a stairwell -> its flight)
  const roomCell = new Map(cells.filter((c) => c.kind === 'room').map((c) => [c.id, c])), ground = cells.find((c) => c.kind === 'ground');
  const resolve = (end, oid) => {
    if (end === 'outside') return ground || null;
    if (roomCell.has(end)) return roomCell.get(end);
    const rm = roomById.get(end);
    if (rm && kindOf(rm) === 'stairwell') return cells.find((c) => c.kind === 'flight' && flights.find((f) => f.id === c.id).walk.ends?.some((e) => e.opening === oid)) || null;
    return null;
  };
  const walls = new Map([...(house.walls || []), ...bWalls].map((w) => [w.id, w])), portals = [];
  for (const o of [...(house.openings || []), ...bOpenings]) {
    if (!PASSABLE.has(o.type) || !walls.has(o.wall)) continue;
    const ends = (o.connects || []).map((e) => resolve(e, o.id));
    if (ends.length !== 2 || !ends.every(Boolean)) continue;
    portals.push({ ...portalFor(o, walls.get(o.wall), r), layers: ends.map((c) => c.layer), cells: ends.map((c) => c.id), ...(/door/.test(o.type) ? { door: true } : {}) });
  }
  for (const s of steps) {                                   // single steps / step pairs: a thin portal on riserLines[0]
    const line = s.riserLines?.[0], a = roomCell.get(s.fromRoom), b = roomCell.get(s.toRoom);
    if (!line || !a || !b) continue;
    for (let k = 1; k < line.length; k++) {
      const p0 = line[k - 1], p1 = line[k], id = line.length > 2 ? `${s.id}.${k - 1}` : s.id;
      const o = { id, width: Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), center: [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2] };
      portals.push({ ...portalFor(o, { a: p0, b: p1, thickness: 0 }, r), layers: [a.layer, b.layer], cells: [a.id, b.id] });
    }
  }
  for (const { bd, half } of gates) {                         // the side gate: shut until its ix group opens it
    const [p0, p1] = bd.line, o = { id: bd.id, width: bd.width ?? Math.hypot(p1[0] - p0[0], p1[1] - p0[1]), center: [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2], openAngle: bd.openAngle ?? 0 };
    portals.push({ ...portalFor(o, { a: p0, b: p1, thickness: 2 * half }, r), layers: ['G', 'G'], cells: ['ground', 'ground'], door: true });
  }
  // obstacles per layer: furniture footprints + structural projections standing on the floor (piers, breasts, ducts)
  const perLayer = (o) => { const m = {}; for (const [k, v] of Object.entries(Array.isArray(o) ? { G: o } : o || {})) m[k] = v.slice(); return m; };
  const obs = perLayer(obstacles), sft = perLayer(soft);
  for (const f of house.features || []) {
    const c = roomCell.get(f.room);
    if (!c || !f.polygon || !Array.isArray(f.z) || !['pier', 'pilaster', 'chimney_breast', 'boxing'].includes(f.type)) continue;
    if (f.z[0] <= c.z + 0.1 && f.z[1] >= c.z + 1.0) (obs[c.layer] ||= []).push(f.polygon.map((p) => [p[0], p[1]]));
  }
  return { radius: r, layers, cells, portals, obstacles: obs, soft: sft };
}

// per-walk lookup tables (cells / portals by layer, obstacle boxes); built once, portals stay live objects
const IDX = new WeakMap();
function idx(walk) {
  let I = IDX.get(walk);
  if (I) return I;
  I = { cells: new Map(), portals: new Map(), boxes: new Map(), cell: new Map(walk.cells.map((c) => [c.id, c])), portal: new Map(walk.portals.map((p) => [p.id, p])) };
  for (const L of walk.layers) {
    I.cells.set(L, walk.cells.filter((c) => c.layer === L));
    I.portals.set(L, walk.portals.filter((p) => p.layers.includes(L)));
    I.boxes.set(L, (walk.obstacles[L] || []).map(bbox));
  }
  I.cross = walk.portals.filter((p) => p.layers[0] !== p.layers[1]);
  IDX.set(walk, I);
  return I;
}
const planeZ = (pl, x, y) => pl.z.c0 + (pl.z.cx || 0) * x + (pl.z.cy || 0) * y;
function ceilingAt(c, x, y) {                    // lowest ceiling plane over (x, y) of a cell with sloped planes
  let z = Infinity;
  for (const pl of c.planes || []) if (inTol(x, y, pl.polygon)) z = Math.min(z, planeZ(pl, x, y));
  return z;
}
// floor Z of a flight: a ramp over its riser lines (11.2.3); k = consecutive risers passed (point left of a->b)
function rampZ(c, x, y) {
  const R = c.risers, n = R.length;
  const side = ([a, b]) => ((b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0])) / Math.hypot(b[0] - a[0], b[1] - a[1]);
  let k = 0;
  while (k < n && side(R[k]) > 0) k++;
  if (k === 0) return c.fromZ;
  if (k === n) return c.toZ;
  const dk = Math.abs(side(R[k - 1])), dk1 = Math.abs(side(R[k]));
  return c.fromZ + ((c.toZ - c.fromZ) * (k - 1 + dk / (dk + dk1 || 1))) / (n - 1);
}
// a walkable piece of a cell at (x, y): { z, room, d }, d = polygon distance (0 inside), within = containment only.
// Pieces in lookup order (treads before floors / zones, smallest area first); a tie goes to the first.
const nearFrom = (c, z) => Math.abs(z - c.fromZ) < Math.abs(c.toZ - z);      // a flight: on its lower / from half
function pieceOf(c, x, y, within) {
  const P = c.kind === 'ground' ? [...c.treads.map((t) => [t.polygon, () => t.z]), ...c.zones.map((zn) => [zn.polygon, () => zoneZ(zn, x, y)])]
    : c.kind === 'flight' ? [[c.polygon, () => rampZ(c, x, y)]]
    : [...(c.treads || []).map((t) => [t.polygon, () => t.z]), [c.polygon, () => c.z]];
  let zf = null, bd = Infinity;
  for (const [poly, f] of P) {
    const d = within ? (inTol(x, y, poly) ? 0 : Infinity) : polyDist(x, y, poly);
    if (d < bd) { bd = d; zf = f; if (!d) break; }
  }
  if (!zf) return null;
  const z = zf();
  let room = c.room;
  if (c.kind === 'ground') room = (c.zones.find((zn) => inTol(x, y, zn.polygon)) || c.zones.reduce((a, zn) => (polyDist(x, y, zn.polygon) < polyDist(x, y, a.polygon) ? zn : a))).room;
  else if (c.kind === 'flight') room = c.through[nearFrom(c, z) ? 0 : c.through.length - 1];
  return { z, room, d: bd };
}
// where (x, y) is on layer L: the cell containing it, else (inside a wall thickness) the nearest walkable piece of the
// portal's cells on that layer. -> { cell, z, room, level } | null
export function cellAt(walk, L, x, y) {
  const I = idx(walk);
  for (const c of I.cells.get(L) || []) { const p = pieceOf(c, x, y, true); if (p) return hit(c, p); }
  let best = null, bc = null;
  for (const pt of I.portals.get(L) || []) {
    if (!pointInPoly(x, y, pt.poly)) continue;
    for (const id of pt.cells) {
      const c = I.cell.get(id);
      if (c.layer !== L) continue;
      const p = pieceOf(c, x, y, false);
      if (p && (!best || p.d < best.d)) { best = p; bc = c; }
    }
  }
  return best && hit(bc, best);
}
const hit = (c, p) => ({ cell: c, z: p.z, room: p.room, level: c.kind === 'flight' ? c.level[nearFrom(c, p.z) ? 0 : 1] : c.level });
export const zAt = (walk, L, x, y) => cellAt(walk, L, x, y)?.z ?? null;
export const levelAt = (walk, L, x, y) => cellAt(walk, L, x, y)?.level ?? null;
export function headroomAt(walk, L, x, y) {
  const h = cellAt(walk, L, x, y);
  return h?.cell.planes ? ceilingAt(h.cell, x, y) - h.z : Infinity;
}

function cellFree(walk, c, x, y) {
  const r = walk.radius;
  if (c.kind === 'ground') {
    if (!c.zones.some((zn) => inTol(x, y, zn.polygon))) return false;
    const I = idx(walk);
    for (const b of c.blockers) {
      if (b.portal && I.portal.get(b.portal)?.open) continue;
      if (segDist(x, y, b.a[0], b.a[1], b.b[0], b.b[1]) < r + b.half) return false;
    }
    return true;
  }
  if (!pointInPoly(x, y, c.polygon) || edgeDist(x, y, c.polygon) < r) return false;
  return !c.planes || ceilingAt(c, x, y) - (pieceOf(c, x, y, true)?.z ?? c.z) >= HEADROOM;
}
// moving obstacles: door leaves at their resting pose (interact.js), set again on every toggle; poly null removes
export function setObstacle(walk, id, layers, poly) {
  const d = (walk.dynamic ||= []), i = d.findIndex((o) => o.id === id);
  if (i >= 0) d.splice(i, 1);
  if (poly?.length >= 3) d.push({ id, layers, poly, bb: bbox(poly) });
}
// distance from (x, y) to the nearest moving obstacle of layer L (0 inside one)
export const dynDist = (walk, L, x, y) => Math.min(Infinity, ...(walk.dynamic || []).filter((o) => o.layers.includes(L)).map((o) => polyDist(x, y, o.poly)));
// free on layer L: outside every obstacle of L (fixed and moving), and inside an open portal of L or a cell of L
// (inset by the body)
export function isFree(walk, L, x, y) {
  const I = idx(walk), r = walk.radius, obs = walk.obstacles[L] || [], bx = I.boxes.get(L) || [];
  for (let i = 0; i < obs.length; i++) {
    const b = bx[i];
    if (x < b[0] - r || y < b[1] - r || x > b[2] + r || y > b[3] + r) continue;
    if (pointInPoly(x, y, obs[i]) || edgeDist(x, y, obs[i]) < r) return false;
  }
  for (const o of walk.dynamic || []) {
    const b = o.bb;
    if (x < b[0] - r || y < b[1] - r || x > b[2] + r || y > b[3] + r || !o.layers.includes(L)) continue;
    if (pointInPoly(x, y, o.poly) || edgeDist(x, y, o.poly) < r) return false;
  }
  for (const p of I.portals.get(L) || []) if (p.open !== false && pointInPoly(x, y, p.poly)) return true;
  for (const c of I.cells.get(L) || []) if (cellFree(walk, c, x, y)) return true;
  return false;
}
// inside a soft obstacle (chair, stool, bin, small plant): walkable, but the walker slows down
export const isSoft = (walk, L, x, y) => (walk.soft[L] || []).some((ob) => pointInPoly(x, y, ob));

// the layer a step to (x, y) lands on from (px, py) on layer L: L if free there, else the other layer of an open
// cross-layer portal the visitor stands in, if free there; null = blocked. Nothing else ever changes the layer.
function stepLayer(walk, L, px, py, x, y) {
  if (isFree(walk, L, x, y)) return L;
  for (const p of idx(walk).cross) {
    if (p.open === false || !p.layers.includes(L) || !pointInPoly(px, py, p.poly)) continue;
    const o = p.layers[0] === L ? p.layers[1] : p.layers[0];
    if (isFree(walk, o, x, y)) return o;
  }
  return null;
}
// a blocked step headed into an open doorway / stair mouth ahead (within 60 deg of its axis, at most 0.8 m off, in
// front of its mouth give or take a body radius): the sideways step toward the portal's centre line, so the walker
// funnels in instead of sliding along the jamb (or off through the next doorway)
function funnel(walk, L, x, y, sx, sy) {
  const l = Math.hypot(sx, sy);
  let best = null, bd = 0.8;
  for (const p of idx(walk).portals.get(L) || []) {
    if (p.open === false || Math.abs(sx * p.normal[0] + sy * p.normal[1]) < 0.5 * l || (p.center[0] - x) * sx + (p.center[1] - y) * sy <= 0) continue;
    const d = polyDist(x, y, p.poly), ux = -p.normal[1], uy = p.normal[0], off = (x - p.center[0]) * ux + (y - p.center[1]) * uy;
    if (d > bd || Math.abs(off) < 1e-3 || Math.abs(off) > p.width / 2 + 0.15) continue;
    const m = -Math.sign(off) * Math.min(Math.abs(off), l);
    best = [ux * m, uy * m]; bd = d;
  }
  return best;
}
// Move with wall sliding; sub-stepped so a fast step cannot tunnel through a thin wall. pos = {x, y, layer}.
export function move(walk, pos, x1, y1) {
  let { x, y, layer: L } = pos, l, f;
  const n = Math.max(1, Math.ceil(Math.hypot(x1 - x, y1 - y) / (walk.radius * 0.5)));
  const sx = (x1 - x) / n, sy = (y1 - y) / n;
  for (let i = 0; i < n; i++) {
    if ((l = stepLayer(walk, L, x, y, x + sx, y + sy)) !== null) { x += sx; y += sy; L = l; }
    else if ((f = funnel(walk, L, x, y, sx, sy)) && (l = stepLayer(walk, L, x, y, x + f[0], y + f[1])) !== null) { x += f[0]; y += f[1]; L = l; }
    else if (sx && (l = stepLayer(walk, L, x, y, x + sx, y)) !== null) { x += sx; L = l; }
    else if (sy && (l = stepLayer(walk, L, x, y, x, y + sy)) !== null) { y += sy; L = l; }
    else break;
  }
  return { x, y, layer: L };
}

// Nearest free point on layer L (rings of 16 samples every 5 cm). ponytail: brute-force search, fine for clicks/teleports.
export function nearestFree(walk, L, x, y, maxR = 3) {
  if (isFree(walk, L, x, y)) return [x, y];
  for (let rr = 0.05; rr <= maxR; rr += 0.05) {
    let best = null, bd = Infinity;
    for (let k = 0; k < 16; k++) {
      const a = (k / 16) * Math.PI * 2, px = x + rr * Math.cos(a), py = y + rr * Math.sin(a);
      if (isFree(walk, L, px, py)) { const d = Math.hypot(px - x, py - y); if (d < bd) { bd = d; best = [px, py]; } }
    }
    if (best) return best;
  }
  return null;
}

// Route from a to b ({x, y, layer}) through free space: A* on (layer, i, j) nodes of an h-metre grid (8-neighbour, soft
// obstacles cost 3x, a zero-cost link to the other layer of an open cross-layer portal containing the node), then
// string-pulled to a few straight legs inside each run of one layer. Closed doors are not free, so they are never
// routes. Returns [{x, y, layer}, ...] from a to b, or null. ponytail: grid A* with lazy isFree and a 2D heuristic
// (a target upstairs floods the floor below first: ~1e5 nodes worst case); a portal-graph heuristic if it ever lags.
export function route(walk, a, b, h = 0.05) {
  const K = 8192, H = K / 2, LN = walk.layers, li = new Map(LN.map((l, i) => [l, i])), I = idx(walk);
  const key = (l, i, j) => (l * K + i + H) * K + j + H;
  const memo = new Map();                                    // node -> 0 blocked, 1 free, 3 soft
  const cost = (l, i, j) => {
    const k = key(l, i, j); let v = memo.get(k);
    if (v === undefined) memo.set(k, (v = isFree(walk, LN[l], i * h, j * h) ? (isSoft(walk, LN[l], i * h, j * h) ? 3 : 1) : 0));
    return v;
  };
  const snap = (p) => {                 // nearest free grid node within 3 cells, on the point's layer
    const l = li.get(p.layer); let best = null, bd = Infinity;
    if (l === undefined) return null;
    for (let di = -3; di <= 3; di++) for (let dj = -3; dj <= 3; dj++) {
      const i = Math.round(p.x / h) + di, j = Math.round(p.y / h) + dj, d = Math.hypot(i * h - p.x, j * h - p.y);
      if (d < bd && cost(l, i, j)) { bd = d; best = [l, i, j]; }
    }
    return best;
  };
  const s = snap(a), t = snap(b);
  if (!s || !t) return null;
  const node = new Map([[key(...s), s]]), gs = new Map([[key(...s), 0]]), from = new Map(), hx = (i, j) => 1.5 * Math.hypot(t[1] - i, t[2] - j);
  const heap = [[hx(s[1], s[2]), key(...s)]];
  const push = (n) => { heap.push(n); for (let c = heap.length - 1, p; c && heap[(p = (c - 1) >> 1)][0] > heap[c][0]; c = p) [heap[c], heap[p]] = [heap[p], heap[c]]; };
  const pop = () => {
    const top = heap[0], last = heap.pop();
    if (heap.length) {
      heap[0] = last;
      for (let c = 0; ;) {
        const l = 2 * c + 1, r = l + 1; let m = c;
        if (l < heap.length && heap[l][0] < heap[m][0]) m = l;
        if (r < heap.length && heap[r][0] < heap[m][0]) m = r;
        if (m === c) break; [heap[c], heap[m]] = [heap[m], heap[c]]; c = m;
      }
    }
    return top;
  };
  const tk = key(...t), relax = (k, g, l, i, j, c) => {
    const k2 = key(l, i, j), g2 = g + c;
    if (g2 < (gs.get(k2) ?? Infinity)) { gs.set(k2, g2); from.set(k2, k); node.set(k2, [l, i, j]); push([g2 + hx(i, j), k2]); }
  };
  let found = false;
  for (let n = 0; heap.length && n < 400000; n++) {
    const [f, k] = pop(), [l, i, j] = node.get(k), g = gs.get(k);
    if (k === tk) { found = true; break; }
    if (f > g + hx(i, j) + 1e-9) continue;                  // stale heap entry
    const ok = (a2, b2) => cost(l, a2, b2) > 0;
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
      const a2 = i + di, b2 = j + dj;
      if (!ok(a2, b2) || (di && dj && (!ok(i + di, j) || !ok(i, j + dj)))) continue;   // no corner cutting
      relax(k, g, l, a2, b2, Math.hypot(di, dj) * cost(l, a2, b2));
    }
    const x = i * h, y = j * h;
    for (const p of I.cross) {
      if (p.open === false || !p.layers.includes(LN[l]) || !pointInPoly(x, y, p.poly)) continue;
      const o = li.get(p.layers[0] === LN[l] ? p.layers[1] : p.layers[0]);
      if (cost(o, i, j)) relax(k, g, o, i, j, 0);
    }
  }
  if (!found) return null;
  const pts = [];
  for (let k = tk; k !== undefined; k = from.get(k)) { const [l, i, j] = node.get(k); pts.push({ x: i * h, y: j * h, layer: LN[l] }); }
  pts.reverse(); pts[0] = { x: a.x, y: a.y, layer: a.layer }; pts.push({ x: b.x, y: b.y, layer: b.layer });
  const clear = (p, q) => {            // straight leg stays in free space (it may cut through a chair: slowed, not blocked)
    const n = Math.ceil(Math.hypot(q.x - p.x, q.y - p.y) / (h / 2));
    for (let i = 1; i < n; i++) if (!isFree(walk, p.layer, p.x + ((q.x - p.x) * i) / n, p.y + ((q.y - p.y) * i) / n)) return false;
    return true;
  };
  const out = [pts[0]];
  for (let i = 0, j = 1; j < pts.length; j++) {
    if (pts[j].layer !== pts[i].layer) {                  // a layer switch: keep both ends of the zero-length link
      if (out[out.length - 1] !== pts[j - 1]) out.push(pts[j - 1]);
      out.push(pts[j]); i = j;
    } else if (!clear(pts[i], pts[j])) { i = j - 1; if (out[out.length - 1] !== pts[i]) out.push(pts[i]); }
  }
  if (out[out.length - 1] !== pts[pts.length - 1]) out.push(pts[pts.length - 1]);
  return out;
}
const xy = (p) => (Array.isArray(p) ? p : [p.x, p.y]);
export const pathLength = (pts) => pts.reduce((s, p, i) => (i ? s + Math.hypot(xy(p)[0] - xy(pts[i - 1])[0], xy(p)[1] - xy(pts[i - 1])[1]) : 0), 0);

// clear sight from (x, y) along yaw on layer L: how far the line stays on the layer's floor (walls, voids, doorways
// - open or not, they lead to other rooms - and the house seen from outside stop it; arches and steps do not), in 5 cm
// steps (thinner than a partition) up to max
function sight(walk, L, x, y, yaw, max = 8) {
  const [dx, dy] = yawDir(yaw), doors = (idx(walk).portals.get(L) || []).filter((p) => p.door);
  let t = 0;
  for (let px, py; t < max; t += 0.05) {
    px = x + dx * (t + 0.05); py = y + dy * (t + 0.05);
    if (!cellAt(walk, L, px, py) || doors.some((p) => pointInPoly(px, py, p.poly))) break;
  }
  return t;
}
// the yaw of the longest clear 20-deg cone of sight from (x, y) -> [yaw, its sight]
function deepest(walk, L, x, y) {
  const N = 36, s = Array.from({ length: N }, (_, k) => sight(walk, L, x, y, (2 * Math.PI * k) / N));
  let k0 = 0, b = -1;
  for (let k = 0; k < N; k++) { const c = Math.min(s[(k + N - 1) % N], s[k], s[(k + 1) % N]); if (c > b) { b = c; k0 = k; } }
  return [wrapA((2 * Math.PI * k0) / N), b];
}
const wrapA = (a) => Math.atan2(Math.sin(a), Math.cos(a));

// One "standing in the doorway, looking in" viewpoint per walkable room (key = room id; the outside: one per
// pseudo-room, in its largest zone). spawn = {pos: [x, y], layer} (or [x, y] on G) for the room holding it.
// Outside, the visitor stands back from the door (up to 5 m) and looks at the house; a balcony looks out. A view that
// would face a wall close by turns to the deepest sight line in the room (through arches and steps, not doors).
// -> {room: {pos, yaw, layer, pitch?, into?: unit vector from its doorway into the room}}
export function viewpoints(walk, spawn) {
  const sp = spawn && (Array.isArray(spawn) ? { pos: spawn, layer: walk.layers.includes('G') ? 'G' : walk.layers[0] } : spawn);
  const I = idx(walk), spots = [], out = {};
  for (const c of walk.cells) {
    if (c.kind === 'room') spots.push({ key: c.room, layer: c.layer, polygon: c.polygon, cell: c.id, ext: !!c.ext });
    else if (c.kind === 'ground') {
      const big = new Map();
      for (const zn of c.zones) { const a = Math.abs(polyArea(zn.polygon)); if (zn.room && !(big.get(zn.room)?.a >= a)) big.set(zn.room, { a, zn }); }
      for (const [room, { zn }] of big) spots.push({ key: room, layer: c.layer, polygon: zn.polygon, cell: c.id, ground: true });
    }
  }
  for (const s of spots) {
    if (out[s.key]) continue;                                  // the shed: its workshop wins over the veranda
    const c = centroid(s.polygon);
    let pos = null, door = null, yaw = null;
    if (sp && sp.layer === s.layer && pointInPoly(sp.pos[0], sp.pos[1], s.polygon)) { pos = sp.pos.slice(); yaw = 0; }
    else {
      const ps = (I.portals.get(s.layer) || []).filter((q) => q.cells.includes(s.cell) && q.cells[0] !== q.cells[1])
        .sort((a, b) => (b.open !== false) - (a.open !== false) || b.width - a.width);   // open doors first, widest first
      for (const p of ps) {
        for (const sg of [1, -1]) {
          const t = p.depth + 0.45, q = [p.center[0] + sg * p.normal[0] * t, p.center[1] + sg * p.normal[1] * t];
          if (pointInPoly(q[0], q[1], s.polygon)) { pos = q; door = { p, n: [sg * p.normal[0], sg * p.normal[1]] }; break; }
        }
        if (pos) break;
      }
    }
    if (door && (s.ground || s.ext)) {
      const { p, n } = door, ny = dirYaw(...n), back = Math.min(5, 0.45 + sight(walk, s.layer, ...pos, ny, 7) - 1);
      if (s.ext) yaw = ny;                                     // a balcony: look out
      else if (back >= 2) {                                    // outside: stand back, face the house
        pos = [p.center[0] + n[0] * (p.depth + back), p.center[1] + n[1] * (p.depth + back)];
        yaw = wrapA(ny + Math.PI);
      }
    }
    pos = nearestFree(walk, s.layer, ...(pos || c)) || c;
    let pitch = 0;
    if (yaw === null) {
      let aim = c;
      const small = Math.hypot(c[0] - pos[0], c[1] - pos[1]) < 0.6;
      if (small) {                                               // small room (WC, porch): the centroid is underfoot, so
        const d = (p) => Math.hypot(p[0] - pos[0], p[1] - pos[1]);  // look down the longest wall towards its far end
        const [a, b] = edges(s.polygon).sort((e, f) => Math.hypot(f[1][0] - f[0][0], f[1][1] - f[0][1]) - Math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))[0];
        const sg = d(b) > d(a) ? 1 : -1;
        aim = [pos[0] + sg * (b[0] - a[0]), pos[1] + sg * (b[1] - a[1])];
      }
      yaw = dirYaw(aim[0] - pos[0], aim[1] - pos[1]);
      const near = small ? Math.min(...[-0.17, 0, 0.17].map((d) => sight(walk, s.layer, ...pos, yaw + d))) : Infinity;
      if (near < 1.5) {                                        // that wall is close: the deepest view, else (a quarter
        const [y2, far] = deepest(walk, s.layer, ...pos);       // landing) back out the way you came, down the flight
        if (far > 2 * near) yaw = y2;
        else if (far < 1.5 && door && !door.p.door) { yaw = dirYaw(-door.n[0], -door.n[1]); pitch = -0.35; }
      }
    }
    out[s.key] = { pos, yaw, layer: s.layer, ...(pitch ? { pitch } : {}), ...(door ? { into: door.n } : {}) };
  }
  return out;
}

// footprints.json -> obstacle polygons per layer {layer: [poly]}. Accepts {items|footprints|objects:[...]} or a bare
// array; each entry gives a polygon ("poly"|"pts"|"corners"|"obb") or center+size+rot(deg). Level = f.level, else the
// level of f.room in house.json (pseudo / building rooms X, unknown G); level X -> layer G. Non-blocking symbols are
// skipped; soft = true returns the small furniture instead (chairs, stools, bins, plants under 1.3 m): walkable, slowed.
const NONBLOCKING = new Set(['rug', 'mirror', 'tv', 'wall_unit', 'airer', 'shelf', 'towel_rail', 'radiator', 'stair', 'trellis', 'flagpole', 'condenser']);
const SMALL = new Set(['chair', 'armchair', 'stool', 'bin', 'plant', 'office_chair', 'bedside']);
export function obstaclesFrom(fp, soft = false, house = null) {
  const list = Array.isArray(fp) ? fp : (fp && (fp.items || fp.footprints || fp.objects)) || [];
  const out = {};
  for (const f of list) {
    const sym = f.sym || f.plan_sym || f.key || f.type;
    if (NONBLOCKING.has(sym) || soft !== (SMALL.has(sym) && !(f.height > 1.3))) continue;
    let poly = f.poly || f.pts || f.corners || f.obb || f.polygon;
    if (!poly && f.center && f.size) {
      const a = ((f.rot ?? f.angle ?? 0) * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a);
      const [w, d] = [f.size[0] / 2, f.size[1] / 2];
      poly = [[-w, -d], [w, -d], [w, d], [-w, d]].map(([u, v]) => [f.center[0] + u * c - v * s, f.center[1] + u * s + v * c]);
    }
    if (Array.isArray(poly) && poly.length >= 3) (out[layerOfLevel(f.level || levelOf(house, f.room))] ||= []).push(poly.map((p) => [p[0], p[1]]));
  }
  return out;
}
