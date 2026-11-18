// 2D plan <-> 3D scene mapping. Pure functions (no three.js import), unit-tested with `node plan.test.mjs`.
// Blender world (x right, y into house, z up) -> glTF/three (x, z, -y)  [export_yup=True, verified on 5.1.1].
// So plan coords (bx, by) = (three.x, -three.z). Plan canvas: +bx right, +by UP the screen (entrance at bottom).

export function makeMap(bounds, w, h, pad = 12) {      // bounds = {minX,minY,maxX,maxY} in Blender metres
  const s = Math.min((w - 2 * pad) / (bounds.maxX - bounds.minX), (h - 2 * pad) / (bounds.maxY - bounds.minY));
  const ox = (w - s * (bounds.maxX - bounds.minX)) / 2, oy = (h - s * (bounds.maxY - bounds.minY)) / 2;
  return {
    s,
    toCanvas: (bx, by) => [ox + (bx - bounds.minX) * s, h - oy - (by - bounds.minY) * s],
    toWorld: (cx, cy) => [bounds.minX + (cx - ox) / s, bounds.minY + (h - oy - cy) / s],
  };
}
export const threeToPlan = (p) => [p.x, -p.z];                 // three position -> (bx, by)
export const planToThree = (bx, by, eyeY) => ({ x: bx, y: eyeY, z: -by });
// Heading on the canvas from camera.getWorldDirection(): canvas y is flipped vs by, and by = -dz, so (dx, dz).
export const canvasHeading = (dir) => Math.atan2(dir.z, dir.x);
export const hfov = (vfovDeg, aspect) => 2 * Math.atan(Math.tan((vfovDeg * Math.PI / 180) / 2) * aspect);

export function pointInPoly(x, y, poly) {                      // poly = [[x,y],...] in Blender metres
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
}

// Draw plan + viewer marker. house = { rooms:[{id,name,polygon:[[x,y]..]}], walls:[{a:[x,y],b:[x,y],thickness}] }
export function drawPlan(ctx, map, house, cam, vfov, aspect, activeRoom) {
  const { width: W, height: H } = ctx.canvas; ctx.clearRect(0, 0, W, H);
  for (const r of house.rooms) {
    ctx.beginPath(); r.polygon.forEach(([x, y], i) => { const [cx, cy] = map.toCanvas(x, y); i ? ctx.lineTo(cx, cy) : ctx.moveTo(cx, cy); });
    ctx.closePath(); ctx.fillStyle = r.id === activeRoom ? 'rgba(255,200,80,.35)' : 'rgba(255,255,255,.08)'; ctx.fill();
  }
  ctx.strokeStyle = '#ddd'; ctx.lineCap = 'butt';
  for (const w of house.walls || []) {
    const [ax, ay] = map.toCanvas(...w.a), [bx, by] = map.toCanvas(...w.b);
    ctx.lineWidth = Math.max(1.5, (w.thickness || 0.1) * map.s); ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
  }
  const [px, py] = map.toCanvas(...threeToPlan(cam.position)); const d = cam.getWorldDirection(new cam.position.constructor());
  const a = canvasHeading(d), half = hfov(vfov, aspect) / 2, R = 2.5 * map.s;   // cone reach 2.5 m
  ctx.beginPath(); ctx.moveTo(px, py); ctx.arc(px, py, R, a - half, a + half); ctx.closePath();
  ctx.fillStyle = 'rgba(80,160,255,.35)'; ctx.fill(); ctx.strokeStyle = '#4af'; ctx.lineWidth = 1; ctx.stroke();
  ctx.beginPath(); ctx.arc(px, py, 4, 0, 7); ctx.fillStyle = '#4af'; ctx.fill();
}
