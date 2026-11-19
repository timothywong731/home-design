// node docs/test/geom.test.mjs  - checks the house<->three frame mapping and the walkable-area logic on spec/house.json
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import * as G from '../js/geom.js';

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

// walkable area on the real spec
const house = JSON.parse(readFileSync(new URL('../../spec/house.json', import.meta.url)));
const W = G.buildWalk(house, { radius: 0.2 });
const ids = W.portals.map((p) => p.id);
for (const d of ['d_inner', 'd_living', 'd_kitchen', 'd_utility', 'd_wc', 'd_dining']) assert.ok(ids.includes(d), `portal ${d}`);
for (const d of ['d_street', 'd_back', 'd_french', 'd_understairs', 'o_stair_foot']) assert.ok(!ids.includes(d), `no portal ${d}`);
assert.ok(G.isFree(W, ...house.spawn), 'spawn free');
assert.ok(!G.isFree(W, 0.725, 3.0), 'inside the hall/living wall');
assert.ok(G.isFree(W, 0.725, 4.09), 'in the living doorway');
assert.ok(!G.isFree(W, 0.6, 6.0), 'stairs are not walkable');
// walking east from the hall through the living-room door ends up in the living room
let p = [0.3, 4.09];
for (let i = 0; i < 40; i++) p = G.move(W, ...p, p[0] + 0.05, p[1]);
assert.equal(G.roomAt(house.rooms, ...p).id, 'living');
// walking east 1 m further north hits the wall and slides (stays in the hallway)
p = [0.3, 3.0];
for (let i = 0; i < 40; i++) p = G.move(W, ...p, p[0] + 0.05, p[1] + 0.01);
assert.equal(G.roomAt(house.rooms, ...p).id, 'hallway'); assert.ok(p[0] <= 0.45 + 1e-9);
// a single huge step cannot tunnel through a wall
p = G.move(W, 0, 3.0, 3.0, 3.0); assert.equal(G.roomAt(house.rooms, ...p).id, 'hallway');
// teleport into a wall snaps to the nearest free point
const q = G.nearestFree(W, 0.725, 3.0); assert.ok(G.isFree(W, ...q) && Math.hypot(q[0] - 0.725, q[1] - 3) < 0.4);
// every walkable room gets a free viewpoint inside it
const vp = G.viewpoints(W, house.spawn);
for (const r of W.rooms) { const v = vp[r.id]; assert.ok(G.isFree(W, ...v.pos), r.id); assert.equal(G.roomAt(house.rooms, ...v.pos).id, r.id); }
near(vp.hallway.yaw, 0); assert.deepEqual(vp.hallway.pos, house.spawn);
// ... and looks into the room, not at the wall beside the door (the WC is a 0.78 m slot: look down its length)
for (const r of W.rooms) { const v = vp[r.id], [dx, dy] = G.yawDir(v.yaw); assert.ok(G.isFree(W, v.pos[0] + 0.3 * dx, v.pos[1] + 0.3 * dy), `${r.id} view`); }
assert.ok(Math.abs(G.yawDir(vp.wc.yaw)[0]) > 0.99, 'wc viewpoint looks along the room');
// the export's footprints.json: [{name, room, plan_sym, obb}] - furniture blocks, overhead units do not
const real = G.obstaclesFrom([{ name: 'dining.table', room: 'dining', plan_sym: 'table', obb: [[0.7, 13.2], [1.6, 13.2], [1.6, 16], [0.7, 16]], height: 0.76 },
  { name: 'kitchen.wall.w1', room: 'kitchen', plan_sym: 'wall_unit', obb: [[4, 7.2], [4.3, 7.2], [4.3, 7.8], [4, 7.8]], height: 0.7 }]);
assert.equal(real.length, 1); assert.ok(!G.isFree(G.buildWalk(house, { obstacles: real }), 1.2, 14.6));
// obstacles from footprints (both encodings) block, rugs do not
const obs = G.obstaclesFrom({ items: [{ sym: 'table', center: [1.2, 14.6], size: [1, 2.4], rot: 0 }, { sym: 'rug', poly: [[1, 1], [3, 1], [3, 3], [1, 3]] }] });
assert.equal(obs.length, 1);
const W2 = G.buildWalk(house, { obstacles: obs });
assert.ok(!G.isFree(W2, 1.2, 14.6) && G.isFree(W, 1.2, 14.6));
// the furnished export: with the real furniture footprints as obstacles every room viewpoint can still be walked to
// from the spawn (flood fill on a 5 cm grid at the viewer's body radius), and the dining table really blocks
const foot = JSON.parse(readFileSync(new URL('../assets/footprints.json', import.meta.url)));
const WF = G.buildWalk(house, { radius: 0.2, obstacles: G.obstaclesFrom(foot) });
assert.ok(WF.obstacles.length > 30 && !G.isFree(WF, 1.14, 14.61), 'furniture footprints loaded, dining table solid');
const h = 0.05, cell = (x, y) => Math.round(x / h) + ',' + Math.round(y / h), seen = new Set([cell(...house.spawn)]);
for (const stack = [house.spawn.map((v) => Math.round(v / h))]; stack.length;) {
  const [i, j] = stack.pop();
  for (const [a, b] of [[i + 1, j], [i - 1, j], [i, j + 1], [i, j - 1]]) if (!seen.has(a + ',' + b) && G.isFree(WF, a * h, b * h)) { seen.add(a + ',' + b); stack.push([a, b]); }
}
for (const [id, v] of Object.entries(G.viewpoints(WF, house.spawn))) assert.ok(seen.has(cell(...v.pos)), `no walkable route from the spawn into ${id}`);
console.log('geom ok:', W.portals.length, 'portals,', W.rooms.length, 'walkable rooms,', WF.obstacles.length, 'furniture obstacles,', (seen.size * h * h).toFixed(1), 'm2 reachable');
