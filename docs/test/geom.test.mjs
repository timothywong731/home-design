// node docs/test/geom.test.mjs                                       - house<->three frame + walk logic on spec/house.json
// HOUSE=build/fixtures/house2.json node docs/test/geom.test.mjs      - the multi-level checks of blender/MULTILEVEL.md 12.g
// A schema-1 house runs the phase-1 checks (with docs/assets/footprints.json), a schema-2 house the walk-layer checks
// and the route traces of MULTILEVEL.md section 16 with their floor-Z sequences.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import * as G from '../js/geom.js';

const ROOT = fileURLToPath(new URL('../../', import.meta.url));
const near = (a, b, e = 1e-9) => assert.ok(Math.abs(a - b) < e, `${a} != ${b}`);

// frame: Blender (x, y, z) -> three (x, z, -y)
const t = G.planToThree(1.25, 8.5, 1.6);
assert.deepEqual([t.x, t.y, t.z], [1.25, 1.6, -8.5]);
assert.deepEqual(G.threeToPlan(t), [1.25, 8.5]);
// yaw 0 looks into the house (+Y) = three -Z; yaw +90deg turns left (CCW from above) to -X
near(G.yawDir(0)[0], 0); near(G.yawDir(0)[1], 1);
near(G.yawDir(Math.PI / 2)[0], -1); near(G.yawDir(Math.PI / 2)[1], 0);
near(G.dirYaw(0, 1), 0); near(G.dirYaw(-1, 0), Math.PI / 2); near(G.dirYaw(1, 0), -Math.PI / 2);
// three: camera.rotation.y = yaw, order YXZ -> forward = (-sin yaw, 0, -cos yaw) -> plan (-sin, cos) = yawDir
for (const yaw of [0, 0.7, -2.1]) {
  const f3 = { x: -Math.sin(yaw), z: -Math.cos(yaw) }, [px, py] = G.threeToPlan(f3), [dx, dy] = G.yawDir(yaw);
  near(px, dx); near(py, dy);
}
near(G.hfov(90, 1), Math.PI / 2);

// polygon helpers
const sq = [[0, 0], [2, 0], [2, 2], [0, 2]];
assert.ok(G.pointInPoly(1, 1, sq) && !G.pointInPoly(3, 1, sq));
near(G.polyArea(sq), 4); assert.deepEqual(G.centroid(sq), [1, 1]);
near(G.edgeDist(1, 0.5, sq), 0.5);
// zone fall (gap 5): z[0] at `from`, z[1] at `to`, clamped beyond
const fz = { z: -0.06, fall: { from: [1.9, -0.12], to: [1.9, -5.2], z: [-0.06, -0.14] } };
near(G.zoneZ(fz, 0, -0.12), -0.06); near(G.zoneZ(fz, 3, -5.2), -0.14); near(G.zoneZ(fz, 3, -9), -0.14); near(G.zoneZ(fz, 0, 2), -0.06);

const HOUSE = process.env.HOUSE || 'spec/house.json';
const house = JSON.parse(readFileSync(resolve(ROOT, HOUSE)));
const legsFree = (W, pts) => pts.every((p, i) => !i || p.layer !== pts[i - 1].layer || [0.25, 0.5, 0.75, 1].every((f) => {
  const q = pts[i - 1]; return G.isFree(W, q.layer, q.x + (p.x - q.x) * f, q.y + (p.y - q.y) * f);
}));
if (house.levels?.length) schema2(house); else schema1(house);

// ------------------------------------------------------------------------------------------------- schema 1 (phase 1)
function schema1(house) {
  const P = (xy) => ({ x: xy[0], y: xy[1], layer: 'G' });
  const W = G.buildWalk(house, { radius: 0.2 }), free = (x, y) => G.isFree(W, 'G', x, y);
  assert.deepEqual(W.layers, ['G']);
  const room = (x, y) => G.cellAt(W, 'G', x, y)?.room;
  const ids = W.portals.filter((p) => p.open).map((p) => p.id);
  for (const d of ['d_inner', 'd_living', 'd_kitchen', 'd_utility', 'd_wc', 'd_dining']) assert.ok(ids.includes(d), `portal ${d}`);
  // shut doors and openings to unmodelled space (outside, the stairs) are never open portals
  for (const d of ['d_street', 'd_back', 'd_french', 'd_understairs', 'o_stair_foot']) assert.ok(!ids.includes(d), `no portal ${d}`);
  assert.ok(free(...house.spawn), 'spawn free');
  assert.ok(!free(0.725, 3.0), 'inside the hall/living wall');
  assert.ok(free(0.725, 4.09), 'in the living doorway');
  assert.ok(!free(0.6, 6.0), 'stairs are not walkable');
  // walking east from the hall through the living-room door ends up in the living room
  let p = P([0.3, 4.09]);
  for (let i = 0; i < 40; i++) p = G.move(W, p, p.x + 0.05, p.y);
  assert.equal(room(p.x, p.y), 'living');
  // walking east 1 m further north hits the wall and slides (stays in the hallway)
  p = P([0.3, 3.0]);
  for (let i = 0; i < 40; i++) p = G.move(W, p, p.x + 0.05, p.y + 0.01);
  assert.equal(room(p.x, p.y), 'hallway'); assert.ok(p.x <= 0.45 + 1e-9);
  // a single huge step cannot tunnel through a wall
  p = G.move(W, P([0, 3.0]), 3.0, 3.0); assert.equal(room(p.x, p.y), 'hallway');
  // teleport into a wall snaps to the nearest free point
  const q = G.nearestFree(W, 'G', 0.725, 3.0); assert.ok(free(...q) && Math.hypot(q[0] - 0.725, q[1] - 3) < 0.4);
  // every walkable room gets a free viewpoint inside it ... and looks into the room, not at the wall beside the door
  const vp = G.viewpoints(W, house.spawn), rooms = W.cells.filter((c) => c.kind === 'room');
  for (const r of rooms) { const v = vp[r.id]; assert.ok(free(...v.pos), r.id); assert.equal(room(...v.pos), r.id); assert.equal(v.layer, 'G'); }
  near(vp.hallway.yaw, 0); assert.deepEqual(vp.hallway.pos, house.spawn);
  for (const r of rooms) { const v = vp[r.id], [dx, dy] = G.yawDir(v.yaw); assert.ok(free(v.pos[0] + 0.3 * dx, v.pos[1] + 0.3 * dy), `${r.id} view`); }
  assert.ok(Math.abs(G.yawDir(vp.wc.yaw)[0]) > 0.99, 'wc viewpoint looks along the room (a 0.78 m slot)');
  // the export's footprints.json: [{name, room, plan_sym, obb}] - furniture blocks, overhead units do not
  const real = G.obstaclesFrom([{ name: 'dining.table', room: 'dining', plan_sym: 'table', obb: [[0.7, 13.2], [1.6, 13.2], [1.6, 16], [0.7, 16]], height: 0.76 },
    { name: 'kitchen.wall.w1', room: 'kitchen', plan_sym: 'wall_unit', obb: [[4, 7.2], [4.3, 7.2], [4.3, 7.8], [4, 7.8]], height: 0.7 }], false, house);
  assert.equal(real.G.length, 1); assert.ok(!G.isFree(G.buildWalk(house, { obstacles: real }), 'G', 1.2, 14.6));
  // obstacles from footprints (both encodings) block, rugs do not; an array of polygons means layer G
  const obs = G.obstaclesFrom({ items: [{ sym: 'table', center: [1.2, 14.6], size: [1, 2.4], rot: 0 }, { sym: 'rug', poly: [[1, 1], [3, 1], [3, 3], [1, 3]] }] });
  assert.equal(obs.G.length, 1);
  assert.ok(!G.isFree(G.buildWalk(house, { obstacles: obs.G }), 'G', 1.2, 14.6) && free(1.2, 14.6));
  // small furniture is soft: walkable (slowed), never an obstacle; tall plants still block
  const soft = G.obstaclesFrom([{ plan_sym: 'chair', obb: [[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]], height: 0.98 },
    { plan_sym: 'plant', obb: [[1, 0], [1.5, 0], [1.5, 0.5], [1, 0.5]], height: 1.8 }], true);
  assert.equal(soft.G.length, 1);
  assert.equal(G.obstaclesFrom([{ plan_sym: 'plant', obb: [[1, 0], [1.5, 0], [1.5, 0.5], [1, 0.5]], height: 1.8 }]).G.length, 1);

  // the furnished export at the viewer's body radius: the dining table blocks, chairs do not, and A* routes from the
  // spawn reach every room viewpoint and the tight places. Every leg of a route is free space.
  const foot = JSON.parse(readFileSync(resolve(ROOT, 'docs/assets/footprints.json')));
  const WF = G.buildWalk(house, { obstacles: G.obstaclesFrom(foot, false, house), soft: G.obstaclesFrom(foot, true, house) });
  assert.equal(WF.radius, G.BODY);
  assert.ok(WF.obstacles.G.length > 25 && !G.isFree(WF, 'G', 1.14, 14.61), 'furniture footprints loaded, dining table solid');
  const box = (name) => { const o = foot.find((f) => f.name === name).obb; return G.centroid(o).concat([Math.min(...o.map((p) => p[0])), Math.max(...o.map((p) => p[0]))]); };
  const chair = box('dining.chair.3');
  assert.ok(G.isFree(WF, 'G', chair[0], chair[1]) && G.isSoft(WF, 'G', chair[0], chair[1]), 'dining armchair is soft');
  const reach = (to, what) => {
    const t0 = performance.now(), p = G.route(WF, P(house.spawn), P(to));
    assert.ok(p && legsFree(WF, p), `no walkable route from the spawn to ${what}`);
    return { what, m: G.pathLength(p).toFixed(1), ms: Math.round(performance.now() - t0) };
  };
  const [tx, ty, tx0, tx1] = box('dining.table'), [fx0] = box('dining.fireplace').slice(2);
  const runs = Object.entries(G.viewpoints(WF, house.spawn)).map(([id, v]) => reach(v.pos, `the ${id} viewpoint`));
  runs.push(reach([tx0 - 0.25, ty], 'the west long side of the dining table'), reach([tx1 + 0.25, ty], 'the east long side of the dining table'),
    reach([-0.35, ty], 'between the west dining chairs and the wall'), reach([fx0 - 0.2, ty], 'between the east dining chairs and the fireplace'),
    reach([2.88, 8.5], 'the black kitchen bin'), reach([1.75, 9.75], 'the middle of the WC'));
  void tx;
  // closed doors are not routes: shut the kitchen door and the kitchen (no other way in) becomes unreachable
  const dk = WF.portals.find((p) => p.id === 'd_kitchen');
  dk.open = false; assert.equal(G.route(WF, P(house.spawn), P([2.8, 7.0])), null, 'route through a closed door'); dk.open = true;
  assert.ok(G.route(WF, P(house.spawn), P([2.8, 7.0])), 'route through the reopened door');
  console.log('geom ok (schema 1):', W.portals.length, 'portals,', rooms.length, 'walkable rooms,', WF.obstacles.G.length, 'obstacles,', WF.soft.G.length, 'soft;',
    'routes', runs.map((r) => `${r.what.replace(/^the /, '')} ${r.m} m/${r.ms} ms`).join('; '));
}

// ------------------------------------------------------------------------------------------------- schema 2 (phase 2)
function schema2(house) {
  const W = G.buildWalk(house), at = (L, x, y) => ({ x, y, layer: L });
  const portal = (id) => W.portals.find((p) => p.id === id), setOpen = (ids, v = true) => ids.forEach((id) => { portal(id).open = v; });
  assert.deepEqual(W.layers, ['B', 'G', '1', '2', 'stair_main', 'stair_basement', 'stair_second']);
  assert.deepEqual(portal('d_basement').layers, ['G', 'stair_basement']); assert.deepEqual(portal('o_basement_foot').layers, ['stair_basement', 'B']);
  assert.deepEqual(portal('o_ql_main').layers, ['1', 'stair_main']); assert.deepEqual(portal('o_stairs2_head').layers, ['2', 'stair_second']);
  assert.deepEqual(['steps_ql_rear.0', 'steps_ql_rear.1', 'steps_rear_front', 'step_head_platform', 'side_gate', 'shed_d1'].map((id) => !!portal(id)), [true, true, true, true, true, true]);
  assert.ok(!portal('w_bay_front'), 'no portal for a window');
  // round 3: hatches into the eaves (house.json: 0.70 high in the old set, below CLEAR -> no portal) and the shed store
  // doors are portals, shut until their leaves open them
  for (const o of house.openings.filter((q) => q.type === 'hatch')) assert.equal(!!portal(o.id) && portal(o.id).open === false, o.height >= G.CLEAR, `hatch ${o.id} (${o.height} high): a shut portal when >= ${G.CLEAR}`);
  assert.ok(portal('shed_store_doors') && !portal('shed_store_doors').open && portal('shed_store_doors').cells.includes('shed_store'), 'shed store doors: a shut portal into the store');
  // the basement door portal: x 0.415..0.725, y 7.38..7.88 (section 16)
  const bb = (p) => [0, 1].map((k) => [Math.min(...p.poly.map((q) => q[k])), Math.max(...p.poly.map((q) => q[k]))]);
  bb(portal('d_basement')).flat().forEach((v, i) => near(v, [0.415, 0.725, 7.38, 7.88][i], 1e-6));
  bb(portal('o_basement_foot')).flat().forEach((v, i) => near(v, [0.73, 1.45, 5.34, 5.85][i], 1e-6));

  // (0.57, 7.0) is free on three flight layers and not on G
  assert.deepEqual(W.layers.filter((L) => G.isFree(W, L, 0.57, 7.0)), ['stair_main', 'stair_basement', 'stair_second']);
  // with all doors open, the d_basement portal centre is not free on layer 1 (a portal exists only on its layers)
  const doors = W.portals.filter((p) => !p.open).map((p) => p.id);
  setOpen(doors);
  assert.ok(G.isFree(W, 'G', 0.57, 7.63) && G.isFree(W, 'stair_basement', 0.57, 7.63) && !G.isFree(W, '1', 0.57, 7.63), 'd_basement portal only on G / stair_basement');
  // zAt is finite at every 5 cm grid point of every open portal on both of its layers
  let n = 0;
  for (const p of W.portals) {
    const [[x0, x1], [y0, y1]] = bb(p);
    for (let x = Math.ceil(x0 / 0.05) * 0.05; x <= x1; x += 0.05) for (let y = Math.ceil(y0 / 0.05) * 0.05; y <= y1; y += 0.05) {
      if (!G.pointInPoly(x, y, p.poly)) continue;
      for (const L of p.layers) { const z = G.zAt(W, L, x, y); assert.ok(Number.isFinite(z), `zAt ${p.id} ${L} ${x.toFixed(2)},${y.toFixed(2)}`); n++; }
    }
  }
  // inside wall thicknesses the outer half takes the outside surface (section 11.2)
  const outerZ = (id) => { const p = portal(id), [cx, cy] = p.center, [nx, ny] = p.normal, out = G.zAt(W, 'G', cx + nx * p.depth * 0.7, cy + ny * p.depth * 0.7), inn = G.zAt(W, 'G', cx - nx * p.depth * 0.7, cy - ny * p.depth * 0.7); return Math.min(out, inn); };
  near(outerZ('d_street'), -0.06, 1e-6); near(outerZ('d_back'), -0.02, 1e-6); near(outerZ('d_french'), -0.05, 1e-6); near(outerZ('shed_d1'), -0.42, 1e-6);
  setOpen(doors, false);
  // the basement breast base blocks; a pier blocks the landing; the WC duct blocks
  assert.ok(!G.isFree(W, 'B', 4.05, 6.0) && G.isFree(W, 'B', 3.6, 6.0), 'basement breast base blocks');
  assert.ok(!G.isFree(W, '1', -0.6, 9.2) && !G.isFree(W, 'G', 3.0, 9.75), 'landing pier, WC duct block');
  // floors: split levels, treads of a step pair, ramps, falls; the level shown on a flight flips at mid-height
  near(G.zAt(W, '1', 0.5, 8.4), 2.85); near(G.zAt(W, '1', -0.3, 8.4), 3.04); near(G.zAt(W, '1', -0.3, 8.0), 3.23); near(G.zAt(W, '1', -0.3, 7.0), 3.42);
  near(G.zAt(W, '2', -0.3, 7.0), 6.22); near(G.zAt(W, '2', 1.0, 4.0), 6.49); near(G.zAt(W, '1', 1.0, 17.9), 3.0);
  near(G.zAt(W, 'stair_main', 0.5, 4.9), 0); near(G.zAt(W, 'stair_main', 0.5, 8.2), 2.85); near(G.zAt(W, 'stair_basement', 1.4, 5.6), -2.31);
  { const f = W.cells.find((c) => c.id === 'stair_main'), R = f.risers, k = R.length - 6, y = (R[k - 1][0][1] + R[k][0][1]) / 2;   // half-way between two straight risers
    near(G.zAt(W, 'stair_main', 0.57, y), f.fromZ + ((f.toZ - f.fromZ) * (k - 0.5)) / (R.length - 1), 1e-9); }
  assert.deepEqual([[0.57, 5.7], [0.57, 7.5]].map(([x, y]) => G.levelAt(W, 'stair_main', x, y)), ['G', '1']);
  assert.deepEqual([[0.57, 7.3], [0.57, 5.7]].map(([x, y]) => G.levelAt(W, 'stair_basement', x, y)), ['G', 'B']);
  assert.equal(G.levelAt(W, 'G', 2, 27), 'X'); assert.equal(G.cellAt(W, 'G', 2, 27).room, 'shed'); assert.equal(G.cellAt(W, 'G', 2, -3).room, 'front');
  near(G.zAt(W, 'G', 3.8, 9.1), -0.02); near(G.zAt(W, 'G', 3.8, 9.5), -0.16); near(G.zAt(W, 'G', ...G.centroid(house.exterior.zones.find((z) => z.id === 'deck_step_e').polygon)), -0.25);
  // low places (round 3): a point is free down to CLEAR (0.80) of headroom - the loft right up to its knee wall, the eaves
  // where the roof leaves that much; the eye follows the headroom (minus EYE_GAP 0.15, at least 0.55) over the body
  const loft = house.rooms.find((r) => r.id === 'loft_office'), fsl = loft.ceiling.planes.find((q) => q.id === 'front_slope');
  near(G.headroomAt(W, '2', 2.0, 4.0), fsl.z.c0 + fsl.z.cy * 4 - loft.floorZ, 1e-9);
  assert.ok(G.isFree(W, '2', 2.0, 2.54 + G.BODY + 0.01), 'loft: free right up to the front knee wall');
  near(G.headroomAt(W, 'G', 0, 3), house.rooms.find((r) => r.id === 'hallway').ceilingZ, 1e-9); assert.equal(G.headroomAt(W, 'G', 1.9, -3.0), Infinity, 'no ceiling outside');
  near(G.headroomAt(W, 'G', 2.0, 8.95), 2.03, 1e-9);                                                     // a ceiling zone: the kitchen nook soffit
  const ef = W.cells.find((c) => c.id === 'eaves_front'), er = W.cells.find((c) => c.id === 'eaves_rear');
  assert.ok(ef?.void && er?.void && ef.layer === '2', 'the eaves are walk cells of layer 2');
  const roofAt = (x, y) => Math.max(...house.roof.planes.filter((q) => q.level !== 'G' && G.pointInPoly(x, y, q.polygon)).map((q) => q.z.c0 + q.z.cx * x + q.z.cy * y));
  const planeAt = (q, x, y) => q.z.c0 + (q.z.cx || 0) * x + (q.z.cy || 0) * y;
  for (const [x, y] of [[3.0, 6.95], [2.0, 6.8], [0.0, 2.3], [2.48, 0.5], [1.5, 1.2], [4.0, 2.0]]) {   // under_roof (lib/ctx ceil_z): the lining
    const rm = house.rooms.find((r) => r.level === '2' && r.kind === 'void' && G.pointInPoly(x, y, r.polygon)), zf = G.zAt(W, '2', x, y);  // = min(ceilingZ,
    const lin = (rm.ceiling.planes || []).filter((q) => G.pointInPoly(x, y, q.polygon)).map((q) => planeAt(q, x, y));   // roof + offset, planes)
    near(G.headroomAt(W, '2', x, y), Math.min(rm.ceilingZ, roofAt(x, y) + (rm.ceiling.offset ?? -(house.roof.structure.thickness - 0.01)), ...lin) - zf, 1e-9);
  }
  if (house.rooms.find((r) => r.id === 'eaves_front')?.ceiling?.planes) {       // the lining eaves.py builds (group C, round 3)
    near(G.headroomAt(W, '2', 0.0, 2.44 - 1e-4), 1.00, 0.005);                 // knee-wall back of the main void
    near(G.headroomAt(W, '2', 2.48, 1.0), 1.70, 1e-9);                        // the strip of the bay-gable tunnel: ceilingZ
    near(G.headroomAt(W, '2', 2.0, 6.69 + 1e-4), 1.157, 0.001);                // eaves_rear at its south edge
  }
  near(G.zAt(W, '2', 3.0, 7.0), 6.37, 1e-9); near(G.zAt(W, '2', 2.0, 7.0), 6.49, 1e-9);                    // the eaves_rear floor step
  assert.ok(!G.isFree(W, '2', 0.0, 1.5) && G.headroomAt(W, '2', 0.0, 1.5) < G.CLEAR, 'west front eaves: lower than CLEAR, not free');
  const eye = (L, x, y) => G.eyeAt(W, L, x, y);
  near(eye('G', 0, 3), 1.6);
  near(eye('2', 3.0, 7.0), Math.max(G.EYE_MIN, G.headroomAt(W, '2', 3.0, 7.0 + G.BODY) - G.EYE_GAP), 1e-9);   // the low side of the body sets it
  const DEEP = [3.0, 6.95];                                    // the deepest free point of the rear eaves on x 3.0
  while (G.isFree(W, '2', DEEP[0], DEEP[1] + 0.01)) DEEP[1] += 0.01;
  DEEP[1] -= 0.03;
  assert.ok(eye('2', ...DEEP) < 1.0 && eye('2', 2.0, 4.0) > 1.5, `eye crouches in the rear eaves (${eye('2', ...DEEP).toFixed(2)} at y ${DEEP[1].toFixed(2)}), stands in the loft`);
  // narrow passages (radius 0.15): basement door lane 0.31 m, shaft 0.365, loft door 0.31, stair foot 0.20, quarter landing 0.30
  assert.ok(G.isFree(W, 'stair_basement', 0.42, 6.5) && G.isFree(W, 'stair_basement', 0.775, 6.5) && !G.isFree(W, 'stair_basement', 0.405, 6.5), 'basement shaft lane');
  assert.ok(G.isFree(W, '1', 0.57, 8.29) && G.isFree(W, '1', 0.57, 8.57) && !G.isFree(W, '1', 0.9, 8.27), 'quarter landing 0.30');

  // ---- route traces (section 16): route, its layers, the portals it passes, the floor-Z plateaus in order ----
  const trace = (W, pts) => {
    const zs = [], ps = [], ls = [];
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i];
      if (a.layer !== b.layer) continue;
      const k = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 0.05));
      for (let s = 0; s <= k; s++) {
        const x = a.x + ((b.x - a.x) * s) / k, y = a.y + ((b.y - a.y) * s) / k, z = G.zAt(W, a.layer, x, y);
        assert.ok(Number.isFinite(z), `route z at ${x.toFixed(2)},${y.toFixed(2)} on ${a.layer}`);
        if (!zs.length || Math.abs(z - zs[zs.length - 1]) > 0.004) zs.push(Math.round(z * 1000) / 1000);
        const pp = W.portals.find((p) => p.layers.includes(a.layer) && G.pointInPoly(x, y, p.poly));
        if (pp && ps[ps.length - 1] !== pp.id) ps.push(pp.id);
      }
      if (ls[ls.length - 1] !== a.layer) ls.push(a.layer);
    }
    return { zs, ps, ls };
  };
  const same = (a, b) => (typeof a === 'number' ? Math.abs(a - b) <= 0.006 : a === b);
  const subseq = (want, got) => { let i = 0; for (const z of got) if (i < want.length && same(z, want[i])) i++; return i === want.length; };
  // follow the route the way the viewer's glide does (move() towards each point in small steps): it must arrive
  const follow = (W, pts) => {
    let p = { ...pts[0] };
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i], k = Math.max(1, Math.ceil(Math.hypot(b.x - a.x, b.y - a.y) / 0.04));
      for (let s = 1; s <= k; s++) p = G.move(W, p, a.x + ((b.x - a.x) * s) / k, a.y + ((b.y - a.y) * s) / k);
    }
    return p;
  };
  // the alley has a gate at each end since round 3 (street_gate); the shower tray, the veranda and the store from the data
  const GATES = ['side_gate', ...(portal('street_gate') ? ['street_gate'] : [])];
  const b2 = house.rooms.find((r) => r.id === 'bathroom2').polygon, bx = (k, f) => f(...b2.map((q) => q[k]));
  const SHOWER = [bx(0, Math.min) + 0.55, bx(1, Math.max) - 0.35];                  // the tray in the NW corner (bathroom2.md)
  const shed = house.exterior.buildings[0], VERANDA = G.centroid(house.exterior.zones.find((z) => z.id === 'shed_veranda').polygon);
  // the store: as far in from its doorway as the walls let the body go - to its back wall shed_w_west_store (check-31)
  const sp = portal('shed_store_doors'), sc = G.centroid(shed.rooms.find((r) => r.id === 'shed_store').polygon), sd = Math.sign(sc[0] - sp.center[0]), STORE = sp.center.slice();
  sp.open = true; while (G.isFree(W, 'G', STORE[0] + sd * 0.01, STORE[1])) STORE[0] += sd * 0.01; sp.open = false; STORE[0] -= sd * 0.02;
  assert.ok((STORE[0] - sp.center[0]) * sd > 0.05, `the walker gets past the store's door line (to x ${STORE[0].toFixed(2)})`);
  const back = shed.walls.find((w) => w.id === 'shed_w_west_store');
  if (back) near(STORE[0], back.a[0] + back.thickness / 2 + G.BODY + 0.02, 0.011);       // blocked at the carved face, not deeper in
  const densify = (pts) => pts.flatMap((p, i) => {     // a route every 5 cm (its legs; a layer switch is a point)
    if (!i || p.layer !== pts[i - 1].layer) return [p];
    const a = pts[i - 1], k = Math.max(1, Math.ceil(Math.hypot(p.x - a.x, p.y - a.y) / 0.05));
    return Array.from({ length: k }, (_, s) => ({ x: a.x + ((p.x - a.x) * (s + 1)) / k, y: a.y + ((p.y - a.y) * (s + 1)) / k, layer: p.layer }));
  });
  const RT = [
    ['1 front door -> basement', ['d_basement'], at('G', 0, 0.3), at('B', 2.5, 7.0), ['G', 'stair_basement', 'B'], ['d_inner', 'd_basement', 'o_basement_foot'], [0, -2.31]],
    ['2 front door -> blue bedroom balcony', ['d_balcony'], at('G', 0, 0.3), at('1', 1.15, 17.9), ['G', 'stair_main', '1'], ['d_inner', 'o_stair_foot', 'o_ql_main', 'steps_ql_rear.0', 'd_blue', 'd_balcony'], [0, 2.85, 3.04, 3.0]],
    ['3 front door -> Slate Room (loft_office)', [], at('G', 0, 0.3), at('2', 2.0, 4.0), ['G', 'stair_main', '1', 'stair_second', '2'],
      ['o_stair_foot', 'o_ql_main', 'steps_ql_rear.0', 'steps_rear_front', 'o_stairs2_foot', 'o_stairs2_head', 'step_head_platform', 'd_loft'], [0, 2.85, 3.04, 3.23, 3.42, 6.02, 6.22, 6.49]],
    ['4 kitchen back door -> side passage -> garden -> shed', ['d_back', 'shed_d1'], at('G', 3.5, 7.5), at('G', 1.8, 27.6), ['G'], ['d_back', 'shed_d1'], [0, -0.02, -0.16, -0.3, -0.45, -0.42, -0.32]],
    ['5 dining French doors -> deck', ['d_french'], at('G', 1.2, 16.0), at('G', 1.2, 18.5), ['G'], ['d_french'], [0, -0.05]],
    ['6 street doors -> forecourt', ['d_street'], at('G', 0, 0.4), at('G', 1.9, -3.0), ['G'], ['d_street'], [0, -0.06, -0.105]],
    ['7 side passage -> side gate -> alley -> street gate -> alley mouth', GATES, at('G', 4.0, 12.0), at('G', 5.0, -2.0), ['G'], ['side_gate'], [-0.3, -0.2, -0.08]],
    // round 3: tight places (owner: "get into narrow spaces, such as the eaves storage")
    ['8 kitchen -> basement', ['d_basement'], at('G', 3.0, 7.0), at('B', 2.5, 7.0), ['G', 'stair_basement', 'B'], ['d_kitchen', 'd_basement', 'o_basement_foot'], [0, -2.31]],
    ...(portal('h_eaves_front_e') ? [['9 Slate Room -> front eaves through the east hatch -> bay-gable tunnel', ['h_eaves_front_e'], at('2', portal('h_eaves_front_e').center[0], 4.0),
      at('2', portal('h_eaves_front_e').center[0], 0.5), ['2'], ['h_eaves_front_e'], [6.49]]] : []),
    ['10 Slate Room -> rear eaves through the rear hatch', ['h_eaves_rear'], at('2', 2.0, 5.0), at('2', ...DEEP), ['2'], ['h_eaves_rear'], [6.49, 6.37]],
    ['11 landing -> second-floor bathroom -> into the shower', [], at('2', -0.2, 10.0), at('2', SHOWER[0], SHOWER[1]), ['2'], ['d_bath2'], [6.02]],
    ['12 shed veranda -> shed store', ['shed_store_doors'], at('G', ...VERANDA), at('G', ...STORE), ['G'], ['shed_store_doors'], [-0.42]],
  ];
  const out = [];
  if (!portal('h_eaves_front_e')) out.push('9 front eaves: SKIPPED (no portal: the hatch is lower than CLEAR in this house.json)');
  for (const [what, open, a, b, layers, via, zwant] of RT) {
    setOpen(open);
    const t0 = performance.now(), pts = G.route(W, a, b), ms = Math.round(performance.now() - t0);
    assert.ok(pts && legsFree(W, pts), `no walkable route: ${what}`);
    const { zs, ps, ls } = trace(W, pts), end = follow(W, pts);
    assert.deepEqual(ls, layers, `${what}: layers ${ls}`);
    assert.ok(subseq(via, ps), `${what}: portals ${ps} (want ${via} in order)`);
    assert.ok(subseq(zwant, zs), `${what}: floor Z ${zs} (want ${zwant} in order)`);
    assert.ok(end.layer === b.layer && Math.hypot(end.x - b.x, end.y - b.y) < 0.1, `${what}: following the route ends at ${end.x.toFixed(2)},${end.y.toFixed(2)} on ${end.layer}`);
    const dp = densify(pts), eyes = dp.map((q) => G.eyeAt(W, q.layer, q.x, q.y)), hr = Math.min(...dp.map((q) => G.headroomAt(W, q.layer, q.x, q.y)));
    assert.ok(eyes.every((e, i) => e < G.headroomAt(W, dp[i].layer, dp[i].x, dp[i].y) - 0.1), `${what}: the eye stays under the ceiling`);
    if (/eaves/.test(what)) assert.ok(Math.min(...eyes) < 1.0 && hr >= G.CLEAR - 1e-9 && eyes[0] > 1.5, `${what}: the eye drops below 1.0 (min ${Math.min(...eyes).toFixed(2)}, least headroom ${hr.toFixed(2)})`);
    if (/tunnel/.test(what)) assert.ok(eyes[eyes.length - 1] > 1.2, `${what}: stands up again in the tunnel (eye ${eyes[eyes.length - 1].toFixed(2)})`);
    out.push(`${what}: ${G.pathLength(pts).toFixed(1)} m, ${ms} ms, ${ls.join('>')}, Z ${zs.filter((z, i) => !i || i === zs.length - 1 || zwant.some((w) => Math.abs(w - z) < 0.006)).join(' ')}, eye ${Math.min(...eyes).toFixed(2)}..${Math.max(...eyes).toFixed(2)}`);
    setOpen(open, false);
  }
  // 13. a pen (the sauna cabin, footprint symbol in PENS): solid until interact.js finds the door leaf hung in its outline
  // (penDoor), then its walls with a gap that the leaf fills while shut: bathroom2 -> into the sauna (bathroom2.md: cabin
  // 1.366 x 0.753 in the NE corner, glass door 0.60 hung on its east edge 0.13 from the corner post, opening 100 deg out)
  {
    const x1 = bx(0, Math.max), y1 = bx(1, Math.max), pen = [[x1 - 1.42, y1 - 0.81], [x1 - 0.06, y1 - 0.81], [x1 - 0.06, y1 - 0.055], [x1 - 1.42, y1 - 0.055]];
    const fp = [{ room: 'bathroom2', plan_sym: 'sauna', obb: pen, height: 2.02 }];
    assert.equal(G.obstaclesFrom(fp, 'pen', house)['2']?.length, 1); assert.equal(G.obstaclesFrom(fp, false, house)['2'], undefined, 'a pen is no ordinary obstacle');
    const WP = G.buildWalk(house, { pens: G.obstaclesFrom(fp, 'pen', house) }), y0 = pen[0][1], hx = x1 - 0.2;
    const shut = [[hx - 0.6, y0 - 0.02], [hx, y0 - 0.02], [hx, y0 + 0.02], [hx - 0.6, y0 + 0.02]];
    const swing = (a) => shut.map(([x, y]) => [hx + (x - hx) * Math.cos(a) - (y - y0) * Math.sin(a), y0 + (x - hx) * Math.sin(a) + (y - y0) * Math.cos(a)]);
    const from = at('2', x1 - 1.9, y0 - 0.5), inside = at('2', hx - 0.35, y0 + 0.4);
    assert.ok(!G.isFree(WP, '2', inside.x, inside.y) && !G.route(WP, from, inside), 'the sauna is solid before its door is known');
    assert.ok(!G.penDoor(WP, '2', [[0, 3], [0.6, 3], [0.6, 3.04], [0, 3.04]]) && !G.penDoor(WP, '1', shut), 'a leaf elsewhere (or on another floor) hangs in no pen');
    assert.ok(G.penDoor(WP, '2', shut) && WP.pens[0].open && WP.pens[0].walls.length === 5 && !WP.obstacles['2'].includes(pen), 'the door leaf opens the pen: four walls, the door wall in two');
    G.setObstacle(WP, 'sauna.door', ['2'], shut);
    assert.ok(G.isFree(WP, '2', inside.x, inside.y) && !G.route(WP, from, inside), 'inside is free, the shut door keeps it closed');
    assert.ok(!G.isFree(WP, '2', pen[0][0] + 0.1, inside.y) && !G.isFree(WP, '2', inside.x, y1 - 0.1), 'its walls stand');
    G.setObstacle(WP, 'sauna.door', ['2'], swing((100 * Math.PI) / 180));
    const pr = G.route(WP, from, inside), end = pr && follow(WP, pr);
    assert.ok(pr && legsFree(WP, pr) && Math.hypot(end.x - inside.x, end.y - inside.y) < 0.1 && pr.some((q) => q.y > y0 + 0.1), 'bathroom2 -> into the sauna through its open door');
    out.push(`13 bathroom2 -> into the sauna (synthetic pen): ${G.pathLength(pr).toFixed(1)} m, eye ${G.eyeAt(WP, '2', inside.x, inside.y).toFixed(2)}`);
  }
  // closed doors are not routes: with d_basement shut the basement is unreachable; the shut gate cuts the alley off; a
  // shut hatch keeps the eaves out of reach, shut store doors the store
  assert.equal(G.route(W, at('2', 2.0, 5.0), at('2', 3.0, 6.95)), null, 'rear eaves reachable through the shut hatch');
  assert.equal(G.route(W, at('G', ...VERANDA), at('G', ...STORE)), null, 'shed store reachable through its shut doors');
  assert.equal(G.route(W, at('G', 0, 0.3), at('B', 2.5, 7.0)), null, 'basement reachable through the shut d_basement');
  setOpen(['d_back', ...GATES.slice(1)]);
  assert.equal(G.route(W, at('G', 4.0, 12.0), at('G', 5.0, -2.0)), null, 'alley reachable through the shut side gate');
  assert.ok(!G.isFree(W, 'G', 4.7, 9.455) && (setOpen(['side_gate']), G.isFree(W, 'G', 4.7, 9.455)), 'gate blocks only while shut');
  if (GATES.length > 1) {                    // the street gate shuts the alley off from the forecourt (an open gate: its whole line)
    setOpen(['street_gate'], false);
    assert.equal(G.route(W, at('G', 4.0, 12.0), at('G', 5.0, -2.0)), null, 'alley mouth reachable through the shut street gate');
  }
  setOpen(['d_back', ...GATES], false);

  // moving: the layer changes only inside a cross-layer portal (walk north up the stair foot, then back down)
  let p = at('G', 0.4, 4.6);
  for (let i = 0; i < 30; i++) p = G.move(W, p, p.x, p.y + 0.05);
  assert.ok(p.layer === 'stair_main' && p.y > 5.9, `walks onto the flight (${p.layer} ${p.y.toFixed(2)})`);
  for (let i = 0; i < 40; i++) p = G.move(W, p, p.x, p.y - 0.05);
  assert.ok(p.layer === 'G' && p.y < 4.7, `walks back off the flight (${p.layer} ${p.y.toFixed(2)})`);
  p = G.move(W, at('G', 0.4, 6.0), 0.4, 6.1); assert.equal(p.layer, 'G', 'no layer change outside a portal');

  // stair foot from beside the living door, aiming up the flight at the newel side: funnels into the stair mouth instead
  // of sliding along the stair front into the living room
  p = at('G', 0.5, 4.3);
  for (let i = 0; i < 80; i++) { const [dx, dy] = [0.25, 1.5].map((v) => (v / Math.hypot(0.25, 1.5)) * 0.05); p = G.move(W, p, p.x + dx, p.y + dy); }
  assert.ok(p.layer === 'stair_main' && p.y > 5.5, `funnels onto the flight (${p.layer} ${p.x.toFixed(2)}, ${p.y.toFixed(2)})`);

  // door leaves (moving obstacles, set by interact.js): a double door's shut leaf keeps its half of the doorway shut
  // while the other leaf has opened the portal; an open leaf is solid; the convex hull outlines a leaf
  near(G.polyArea(G.hull([[0, 1.74], [0.61, 1.74], [0.3, 1.8], [0.61, 1.87], [0, 1.87], [0.2, 1.8]])), 0.61 * 0.13, 1e-9);
  setOpen(['d_inner']);
  G.setObstacle(W, 'leaf0', ['G'], [[0, 1.74], [0.61, 1.74], [0.61, 1.87], [0, 1.87]]);
  assert.ok(!G.isFree(W, 'G', 0.3, 1.8) && G.isFree(W, 'G', -0.3, 1.8), 'shut leaf blocks its half, the other half is free');
  p = at('G', 0.3, 1.3);
  for (let i = 0; i < 30; i++) p = G.move(W, p, p.x, p.y + 0.05);
  assert.ok(p.y < 1.6, `walks into the shut leaf (${p.y.toFixed(2)})`);
  const half = G.route(W, at('G', 0.3, 1.3), at('G', 0.2, 2.6));
  assert.ok(half && legsFree(W, half) && half.every((q) => q.x < 0.6 || q.y < 1.5 || q.y > 2.1), 'route through the open half');
  G.setObstacle(W, 'leaf0', ['G'], null);
  assert.ok(G.isFree(W, 'G', 0.3, 1.8) && G.dynDist(W, 'G', 0.3, 1.8) === Infinity, 'obstacle removed');
  setOpen(['d_inner'], false);

  // footprints: level from the record, else from its room (pseudo / building -> X -> layer G, unknown -> G)
  const ob = G.obstaclesFrom([{ room: 'green_bedroom', plan_sym: 'bed', obb: sq }, { room: 'front', plan_sym: 'car', obb: sq }, { room: 'shed', plan_sym: 'workbench', obb: sq },
    { room: 'nowhere', plan_sym: 'table', obb: sq }, { room: 'garden', level: 'X', plan_sym: 'planter', obb: sq }, { room: 'basement', plan_sym: 'boiler', obb: sq }], false, house);
  assert.deepEqual(Object.fromEntries(Object.entries(ob).map(([k, v]) => [k, v.length])), { 1: 1, G: 4, B: 1 });
  // viewpoints: one per walkable room and per outdoor pseudo-room, free, on its own layer, looking into it
  const vp = G.viewpoints(W, { pos: house.spawn, layer: 'G' });
  for (const [id, v] of Object.entries(vp)) {
    assert.ok(G.isFree(W, v.layer, ...v.pos) && G.cellAt(W, v.layer, ...v.pos).room === id, `viewpoint ${id}`);
    const [dx, dy] = G.yawDir(v.yaw); assert.ok(G.isFree(W, v.layer, v.pos[0] + 0.3 * dx, v.pos[1] + 0.3 * dy), `${id} view`);
  }
  for (const id of ['basement', 'balcony', 'loft_office', 'front', 'garden', 'side_passage', 'shed']) assert.ok(vp[id], `viewpoint ${id}`);
  // outside: stand back from the street / French doors and face the house; the balcony looks out over the garden; the
  // quarter landing (a wall 1.2 m ahead, nothing deeper) looks back down the flight
  assert.ok(vp.front.pos[1] < -3 && G.yawDir(vp.front.yaw)[1] > 0.99, `front faces the house from the forecourt (${vp.front.pos})`);
  assert.ok(vp.garden.pos[1] > 20 && G.yawDir(vp.garden.yaw)[1] < -0.99, `garden faces the house (${vp.garden.pos})`);
  assert.ok(G.yawDir(vp.balcony.yaw)[1] > 0.99, 'balcony looks out');
  assert.ok(!vp.landing1_ql.pitch || (G.yawDir(vp.landing1_ql.yaw)[1] < -0.99 && vp.landing1_ql.pitch < 0), 'quarter landing: up the step to the rear corridor, or (nothing deeper) back down the main flight');
  assert.ok(!vp.eaves_front && !vp.stairs && !vp.stairs2, 'no viewpoint in voids / stairwells');
  // review additions are tolerated: the plan symbol `pipe` blocks; feature types ceiling_cove (ignored) and boxing
  // (blocks when it stands on the floor); floor_void.bottom (ignored); a neighbour given by `parts` alone still blocks
  assert.equal(G.obstaclesFrom([{ room: 'bathroom2', plan_sym: 'pipe', obb: sq }], false, house)['2']?.length, 1, 'pipe blocks');
  assert.equal(G.obstaclesFrom([{ room: 'green_bathroom', plan_sym: 'shower', obb: sq, height: 2 }], false, house)['1'], undefined, 'the shower is walked into');
  const h2 = structuredClone(house), nb = h2.exterior.neighbours[0];
  h2.features.push({ id: 't_cove', type: 'ceiling_cove', room: 'hallway', polygon: [[0.2, 3], [0.6, 3], [0.6, 3.4], [0.2, 3.4]], z: [2.4, 2.6] },
    { id: 't_box', type: 'boxing', room: 'hallway', polygon: [[0.2, 3], [0.6, 3], [0.6, 3.4], [0.2, 3.4]], z: [0, 2.4] },
    { id: 't_void', type: 'floor_void', level: 'G', room: 'hallway', polygon: [[0.2, 2], [0.6, 2], [0.6, 2.2], [0.2, 2.2]], z: 0, bottom: -0.03 });
  delete nb.polygon;
  const W2 = G.buildWalk(h2), gr = W2.cells.find((c) => c.kind === 'ground');
  assert.ok(!G.isFree(W2, 'G', 0.4, 3.2) && G.isFree(W, 'G', 0.4, 3.2), 'a floor-standing boxing blocks, a ceiling cove does not');
  assert.ok(nb.parts.every((p) => p.polygon.every(([x, y]) => gr.blockers.some((b) => Math.hypot(b.a[0] - x, b.a[1] - y) < 1e-9))), 'neighbour parts block');
  // walking round small obstacles (NAV-W-SNAG-CORNER): exactly tangent to a post is free; a step blocked on both axes at
  // its corner turns and slides round it; a push square into a wall or a post's face stays put (no drift)
  const box = { rooms: [{ id: 'r', polygon: [[-2, -2], [2, -2], [2, 2], [-2, 2]], floorZ: 0 }], openings: [], walls: [] };
  const WB = G.buildWalk(box, { obstacles: { G: [[[0, 0], [0.2, 0], [0.2, 0.2], [0, 0.2]]] } }), walkS = (x, y, dx, dy, k = 40) => { let q = at('G', x, y); for (let i = 0; i < k; i++) q = G.move(WB, q, q.x + dx, q.y + dy); return q; };
  assert.ok(G.isFree(WB, 'G', 0.2 + G.BODY, 0.1), 'tangent to the post is free');
  let q = walkS(0.35, 0.6, 0, -0.05); assert.ok(q.y < -1 && Math.abs(q.x - 0.35) < 1e-9, `tangent walk past the post (${q.x.toFixed(3)}, ${q.y.toFixed(3)})`);
  q = walkS(0.25, 0.6, 0, -0.05); assert.ok(q.y < -1, `slides round the post's corner (${q.x.toFixed(3)}, ${q.y.toFixed(3)})`);
  q = walkS(0.9, 1.7, 0, 0.05); assert.ok(Math.abs(q.x - 0.9) < 1e-9 && q.y < 1.86, `square into a wall: no drift (${q.x.toFixed(3)})`);
  q = walkS(0.1, 0.6, 0, -0.05); assert.ok(Math.abs(q.x - 0.1) < 1e-9 && q.y > 0.34, `square into the post's face: stays (${q.x.toFixed(3)}, ${q.y.toFixed(3)})`);

  // sight graph (walk-mode culling): openings join their rooms, 'outside' resolves to the zone looked onto; door edges
  // name their door; a fixed obscure pane is no edge; the stairwells open onto the landings beside them; zones join zones
  const SG = G.sightGraph(house), to = (a) => (SG.adj.get(a) || []).map((e) => e.to), edge = (a, b) => (SG.adj.get(a) || []).find((e) => e.to === b);
  assert.deepEqual(SG.ends.get('d_kitchen'), ['hallway', 'kitchen']); assert.deepEqual(SG.ends.get('w_bay_front'), ['living', 'front']);
  assert.deepEqual(SG.ends.get('d_french'), ['dining', 'garden']); assert.deepEqual(SG.ends.get('shed_d1'), ['shed', 'shed']);
  assert.equal(edge('hallway', 'kitchen').door, 'd_kitchen');
  assert.ok(!to('wc').includes('side_passage') && SG.ends.get('w_wc')[1] === 'side_passage', 'fixed obscure WC pane: no sight edge');
  assert.ok(to('stairs2').includes('landing2_platform') && to('stairs').includes('basement_stair'), 'stairwells open onto the rooms beside them (and down their floor voids)');
  assert.ok(to('front').includes('side_passage') && to('side_passage').includes('garden') && to('garden').includes('shed') && to('loft_office').includes('roof'), 'zones, roof window');
  const vb = edge('landing1_front', 'stairs2').box;                         // a stair mouth in no wall: the shared edge, floor to ceiling
  assert.ok(vb[2] < 3.42 && vb[5] > 8.6, `virtual opening box spans the well (${vb})`);
  // seenRooms: everything in view walks the graph (outdoor extras come with any outdoor node); a shut door stops it
  const all = G.seenRooms(SG, 'hallway', (b, r) => r), shutK = G.seenRooms(SG, 'kitchen', (b, r, e) => (e.door === 'd_kitchen' || e.door === 'd_back' ? null : r));
  assert.ok(all.has('kitchen') && all.has('garden') && all.has('facade') && all.has('neighbours') && all.get('hallway')[0].join() === '-1,1,-1,1', 'seen through open views');
  assert.ok(shutK.size === 1 && shutK.has('kitchen'), `kitchen with its doors shut sees only itself (${[...shutK.keys()]})`);
  const right = G.seenRooms(SG, 'hallway', (b, r) => [0, 1, r[2], r[3]]);   // a projector that keeps the right half
  assert.ok([...right.values()].every((l) => l.every((x) => x[0] >= 0 || x[0] === -1)), 'rectangles narrow along the path');

  console.log(`geom ok (schema 2): ${W.cells.length} cells on ${W.layers.length} layers, ${W.portals.length} portals, ${n} portal grid points with finite Z, ${Object.keys(vp).length} viewpoints`);
  for (const s of out) console.log('  route', s);
}
