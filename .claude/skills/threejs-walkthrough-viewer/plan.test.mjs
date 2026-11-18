import assert from 'node:assert'; import { makeMap, threeToPlan, planToThree, canvasHeading, pointInPoly } from './plan.mjs';
const m = makeMap({ minX: 0, minY: 0, maxX: 4, maxY: 8 }, 100, 200, 0);
const [cx, cy] = m.toCanvas(1, 2); const [bx, by] = m.toWorld(cx, cy); assert(Math.abs(bx - 1) < 1e-9 && Math.abs(by - 2) < 1e-9);
assert(m.toCanvas(0, 0)[1] === 200 && m.toCanvas(0, 8)[1] === 0);            // entrance (y=0) at the bottom, rear at the top
const t = planToThree(1, 2, 1.6); assert.deepEqual(threeToPlan(t), [1, 2]);
// walking from the front door into the house = Blender +Y = three -Z => heading must point UP the canvas (negative canvas y => angle -90deg)
assert(Math.abs(canvasHeading({ x: 0, y: 0, z: -1 }) + Math.PI / 2) < 1e-9);
assert(canvasHeading({ x: 1, y: 0, z: 0 }) === 0);                           // +X (right) stays right
assert(pointInPoly(1, 1, [[0, 0], [2, 0], [2, 2], [0, 2]]) && !pointInPoly(3, 1, [[0, 0], [2, 0], [2, 2], [0, 2]]));
console.log('plan ok');
