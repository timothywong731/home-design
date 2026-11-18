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
const PASSABLE = new Set(['door', 'double_door', 'french_door', 'arch', 'opening']);

// rect around a wall opening: along = clear width minus the body, across = wall thickness + body + overlap
function portalFor(o, wall, r) {
  const [ax, ay] = wall.a, [bx, by] = wall.b, L = Math.hypot(bx - ax, by - ay);
  const ux = (bx - ax) / L, uy = (by - ay) / L, nx = -uy, ny = ux;
  const ha = Math.max(0.04, o.width / 2 - r), hc = (wall.thickness || 0) / 2 + r + 0.05;
  const [cx, cy] = o.center;
  const p = (s, t) => [cx + ux * s + nx * t, cy + uy * s + ny * t];
  return { id: o.id, rooms: o.connects, center: [cx, cy], normal: [nx, ny], depth: (wall.thickness || 0) / 2,
    width: o.width, poly: [p(-ha, -hc), p(ha, -hc), p(ha, hc), p(-ha, hc)] };
}

// house = spec/house.json shape. obstacles = [[x,y],...] polygons (furniture footprints).
export function buildWalk(house, { radius = 0.2, exclude = ['stairs'], obstacles = [] } = {}) {
  const rooms = house.rooms.filter((r) => !exclude.includes(r.id));
  const ids = new Set(rooms.map((r) => r.id)), walls = new Map((house.walls || []).map((w) => [w.id, w]));
  const portals = (house.openings || [])
    .filter((o) => PASSABLE.has(o.type) && o.openAngle !== 0 && (o.connects || []).every((c) => ids.has(c)) && walls.has(o.wall))
    .map((o) => portalFor(o, walls.get(o.wall), radius));
  return { rooms, portals, radius, obstacles };
}

export function isFree(walk, x, y) {
  const r = walk.radius;
  for (const ob of walk.obstacles) if (pointInPoly(x, y, ob) || edgeDist(x, y, ob) < r) return false;
  for (const p of walk.portals) if (pointInPoly(x, y, p.poly)) return true;
  for (const rm of walk.rooms) if (pointInPoly(x, y, rm.polygon) && edgeDist(x, y, rm.polygon) >= r) return true;
  return false;
}

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

// One "standing in the doorway, looking in" viewpoint per walkable room. spawn = [x, y] for the room holding it.
export function viewpoints(walk, spawn) {
  const out = {};
  for (const rm of walk.rooms) {
    const c = centroid(rm.polygon);
    let pos = null;
    if (spawn && pointInPoly(spawn[0], spawn[1], rm.polygon)) pos = spawn.slice();
    else {
      const p = walk.portals.filter((q) => q.rooms.includes(rm.id) && q.rooms[0] !== q.rooms[1]).sort((a, b) => b.width - a.width)[0];
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
const SOFT = new Set(['rug', 'mirror', 'tv', 'wall_unit', 'airer', 'shelf', 'towel_rail', 'radiator', 'stair']);
export function obstaclesFrom(fp) {
  const list = Array.isArray(fp) ? fp : (fp && (fp.items || fp.footprints || fp.objects)) || [];
  const out = [];
  for (const f of list) {
    const sym = f.sym || f.plan_sym || f.key || f.type;
    if (SOFT.has(sym)) continue;
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
