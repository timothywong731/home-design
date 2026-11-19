// Pure geometry for the viewer (no three.js import) - node-tested by docs/test/geom.test.mjs.
// House frame (spec/house.json): metres, x right, y into the house (rear drawn UP the plan), z up.
// glTF/three frame: (x, z, -y). So plan (x, y) = (three.x, -three.z).
// Yaw convention used everywhere here: degrees/radians CCW seen from above, 0 = facing +Y (into the house).

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

export const roomAt = (rooms, x, y) => rooms.find((r) => pointInPoly(x, y, r.polygon)) || null;

// ---- walkable area: rooms inset by the body radius, joined by portals through open doorways ----
// Body radius: small enough for the 0.61 m WC door and the gaps round the dining table, still > the distance from the
// eye to the near-plane corners at 90 deg fov on a 2.4:1 screen (0.14 m), so the camera never clips into a wall.
export const BODY = 0.15;
const PASSABLE = new Set(['door', 'double_door', 'french_door', 'arch', 'opening']);

// rect around a wall opening: along = clear width minus the body, across = wall thickness + body + overlap
function portalFor(o, wall, r) {
  const [ax, ay] = wall.a, [bx, by] = wall.b, L = Math.hypot(bx - ax, by - ay);
  const ux = (bx - ax) / L, uy = (by - ay) / L, nx = -uy, ny = ux;
  const ha = Math.max(0.04, o.width / 2 - r), hc = (wall.thickness || 0) / 2 + r + 0.05;
  const [cx, cy] = o.center;
  const p = (s, t) => [cx + ux * s + nx * t, cy + uy * s + ny * t];
  return { id: o.id, rooms: o.connects, center: [cx, cy], normal: [nx, ny], depth: (wall.thickness || 0) / 2,
    width: o.width, poly: [p(-ha, -hc), p(ha, -hc), p(ha, hc), p(-ha, hc)], open: o.openAngle !== 0 };
}
const bbox = (poly) => { const xs = poly.map((p) => p[0]), ys = poly.map((p) => p[1]); return [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)]; };

// house = spec/house.json shape. obstacles = [[x,y],...] polygons (furniture footprints) that block; soft = small
// furniture the walker may pass through (slowed). Every door between two walkable rooms gets a portal; portal.open
// starts as the door stands (openAngle 0 = shut) and is switched by the viewer when a leaf is opened or closed.
// Openings to anything that is not a walkable room (outside, the stairs) never get one.
export function buildWalk(house, { radius = BODY, exclude = ['stairs'], obstacles = [], soft = [] } = {}) {
  const rooms = house.rooms.filter((r) => !exclude.includes(r.id));
  const ids = new Set(rooms.map((r) => r.id)), walls = new Map((house.walls || []).map((w) => [w.id, w]));
  const portals = (house.openings || [])
    .filter((o) => PASSABLE.has(o.type) && (o.connects || []).every((c) => ids.has(c)) && walls.has(o.wall))
    .map((o) => portalFor(o, walls.get(o.wall), radius));
  return { rooms, portals, radius, obstacles, soft, boxes: obstacles.map(bbox) };
}

export function isFree(walk, x, y) {
  const r = walk.radius, bx = walk.boxes || (walk.boxes = walk.obstacles.map(bbox));
  for (let i = 0; i < walk.obstacles.length; i++) {
    const b = bx[i], ob = walk.obstacles[i];
    if (x < b[0] - r || y < b[1] - r || x > b[2] + r || y > b[3] + r) continue;
    if (pointInPoly(x, y, ob) || edgeDist(x, y, ob) < r) return false;
  }
  for (const p of walk.portals) if (p.open !== false && pointInPoly(x, y, p.poly)) return true;
  for (const rm of walk.rooms) if (pointInPoly(x, y, rm.polygon) && edgeDist(x, y, rm.polygon) >= r) return true;
  return false;
}
// inside a soft obstacle (chair, stool, bin, small plant): walkable, but the walker slows down
export const isSoft = (walk, x, y) => (walk.soft || []).some((ob) => pointInPoly(x, y, ob));

// Move with wall sliding; sub-stepped so a fast step cannot tunnel through a thin wall.
export function move(walk, x0, y0, x1, y1) {
  const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / (walk.radius * 0.5)));
  const sx = (x1 - x0) / n, sy = (y1 - y0) / n;
  let x = x0, y = y0;
  for (let i = 0; i < n; i++) {
    if (isFree(walk, x + sx, y + sy)) { x += sx; y += sy; }
    else if (sx && isFree(walk, x + sx, y)) x += sx;
    else if (sy && isFree(walk, x, y + sy)) y += sy;
    else break;
  }
  return [x, y];
}

// Nearest free point (rings of 16 samples every 5 cm). ponytail: brute-force search, fine for clicks/teleports.
export function nearestFree(walk, x, y, maxR = 3) {
  if (isFree(walk, x, y)) return [x, y];
  for (let rr = 0.05; rr <= maxR; rr += 0.05) {
    let best = null, bd = Infinity;
    for (let k = 0; k < 16; k++) {
      const a = (k / 16) * Math.PI * 2, px = x + rr * Math.cos(a), py = y + rr * Math.sin(a);
      if (isFree(walk, px, py)) { const d = Math.hypot(px - x, py - y); if (d < bd) { bd = d; best = [px, py]; } }
    }
    if (best) return best;
  }
  return null;
}

// Route from a to b ([x, y]) through free space: A* on an h-metre grid (8-neighbour, soft obstacles cost 3x), then
// string-pulled to a few straight legs. Closed doors are not free, so they are never routes. Returns the polyline
// [a, ..., b] or null. ponytail: grid A* with lazy isFree, ~10k cells across the house; a navmesh if it ever lags.
export function route(walk, a, b, h = 0.05) {
  const K = 8192, key = (i, j) => (i + K / 2) * K + (j + K / 2), memo = new Map();   // cell -> 0 blocked, 1 free, 3 soft
  const cost = (i, j) => {
    const k = key(i, j); let v = memo.get(k);
    if (v === undefined) memo.set(k, (v = isFree(walk, i * h, j * h) ? (isSoft(walk, i * h, j * h) ? 3 : 1) : 0));
    return v;
  };
  const ok = (i, j) => cost(i, j) > 0;
  const snap = ([x, y]) => {           // nearest free grid node within 3 cells
    let best = null, bd = Infinity;
    for (let di = -3; di <= 3; di++) for (let dj = -3; dj <= 3; dj++) {
      const i = Math.round(x / h) + di, j = Math.round(y / h) + dj, d = Math.hypot(i * h - x, j * h - y);
      if (d < bd && ok(i, j)) { bd = d; best = [i, j]; }
    }
    return best;
  };
  const s = snap(a), t = snap(b);
  if (!s || !t) return null;
  const gs = new Map([[key(...s), 0]]), from = new Map(), heap = [[Math.hypot(t[0] - s[0], t[1] - s[1]), s[0], s[1]]];
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
  let found = false;
  for (let n = 0; heap.length && n < 200000; n++) {
    const [, i, j] = pop(), k = key(i, j), g = gs.get(k);
    if (i === t[0] && j === t[1]) { found = true; break; }
    for (const [di, dj] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
      const a2 = i + di, b2 = j + dj;
      if (!ok(a2, b2) || (di && dj && (!ok(i + di, j) || !ok(i, j + dj)))) continue;   // no corner cutting
      const k2 = key(a2, b2), g2 = g + Math.hypot(di, dj) * cost(a2, b2);
      if (g2 < (gs.get(k2) ?? Infinity)) { gs.set(k2, g2); from.set(k2, k); push([g2 + 1.5 * Math.hypot(t[0] - a2, t[1] - b2), a2, b2]); }
    }
  }
  if (!found) return null;
  const cells = [];
  for (let k = key(...t); k !== undefined; k = from.get(k)) cells.push([(Math.floor(k / K) - K / 2) * h, ((k % K) - K / 2) * h]);
  cells.reverse(); cells[0] = a.slice(); cells.push(b.slice());
  const clear = (p, q) => {            // straight leg stays in free space (it may cut through a chair: slowed, not blocked)
    const n = Math.ceil(Math.hypot(q[0] - p[0], q[1] - p[1]) / (h / 2));
    for (let i = 1; i < n; i++) { const x = p[0] + ((q[0] - p[0]) * i) / n, y = p[1] + ((q[1] - p[1]) * i) / n; if (!isFree(walk, x, y)) return false; }
    return true;
  };
  const out = [cells[0]];
  for (let i = 0, j = 1; j < cells.length; j++) if (!clear(cells[i], cells[j])) { i = j - 1; out.push(cells[i]); }
  out.push(cells[cells.length - 1]);
  return out;
}
export const pathLength = (pts) => pts.reduce((s, p, i) => (i ? s + Math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1]) : 0), 0);

// One "standing in the doorway, looking in" viewpoint per walkable room. spawn = [x, y] for the room holding it.
export function viewpoints(walk, spawn) {
  const out = {};
  for (const rm of walk.rooms) {
    const c = centroid(rm.polygon);
    let pos = null;
    if (spawn && pointInPoly(spawn[0], spawn[1], rm.polygon)) pos = spawn.slice();
    else {
      const p = walk.portals.filter((q) => q.open !== false && q.rooms.includes(rm.id) && q.rooms[0] !== q.rooms[1]).sort((a, b) => b.width - a.width)[0];
      if (p) {
        for (const s of [1, -1]) {
          const t = p.depth + 0.45, q = [p.center[0] + s * p.normal[0] * t, p.center[1] + s * p.normal[1] * t];
          if (pointInPoly(q[0], q[1], rm.polygon)) { pos = q; break; }
        }
      }
    }
    pos = nearestFree(walk, ...(pos || c)) || c;
    let aim = c;
    if (Math.hypot(c[0] - pos[0], c[1] - pos[1]) < 0.6) {      // small room (WC, porch): the centroid is underfoot, so
      const d = (p) => Math.hypot(p[0] - pos[0], p[1] - pos[1]); // look down the longest wall towards its far end
      const [a, b] = rm.polygon.map((p, i, P) => [p, P[(i + 1) % P.length]]).sort((e, f) => Math.hypot(f[1][0] - f[0][0], f[1][1] - f[0][1]) - Math.hypot(e[1][0] - e[0][0], e[1][1] - e[0][1]))[0];
      const s = d(b) > d(a) ? 1 : -1;
      aim = [pos[0] + s * (b[0] - a[0]), pos[1] + s * (b[1] - a[1])];
    }
    const yaw = spawn && pos[0] === spawn[0] && pos[1] === spawn[1] ? 0 : dirYaw(aim[0] - pos[0], aim[1] - pos[1]);
    out[rm.id] = { pos, yaw };
  }
  return out;
}

// footprints.json -> obstacle polygons. Accepts {items|footprints|objects:[...]} or a bare array; each entry
// gives a polygon ("poly"|"pts"|"corners"|"obb") or center+size+rot(deg). Non-blocking symbols are skipped.
// soft = true returns the small furniture instead (chairs, stools, bins, plants under 1.3 m): walkable, slowed.
const NONBLOCKING = new Set(['rug', 'mirror', 'tv', 'wall_unit', 'airer', 'shelf', 'towel_rail', 'radiator', 'stair']);
const SMALL = new Set(['chair', 'armchair', 'stool', 'bin', 'plant']);
export function obstaclesFrom(fp, soft = false) {
  const list = Array.isArray(fp) ? fp : (fp && (fp.items || fp.footprints || fp.objects)) || [];
  const out = [];
  for (const f of list) {
    const sym = f.sym || f.plan_sym || f.key || f.type;
    if (NONBLOCKING.has(sym) || soft !== (SMALL.has(sym) && !(f.height > 1.3))) continue;
    let poly = f.poly || f.pts || f.corners || f.obb || f.polygon;
    if (!poly && f.center && f.size) {
      const a = ((f.rot ?? f.angle ?? 0) * Math.PI) / 180, c = Math.cos(a), s = Math.sin(a);
      const [w, d] = [f.size[0] / 2, f.size[1] / 2];
      poly = [[-w, -d], [w, -d], [w, d], [-w, d]].map(([u, v]) => [f.center[0] + u * c - v * s, f.center[1] + u * s + v * c]);
    }
    if (Array.isArray(poly) && poly.length >= 3) out.push(poly.map((p) => [p[0], p[1]]));
  }
  return out;
}
