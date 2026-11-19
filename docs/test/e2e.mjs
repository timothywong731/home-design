// End-to-end check of the viewer in Chromium. Serves docs/ under /home-design/ (like GitHub Pages), drives the page,
// writes screenshots + console log to build/e2e/, exits non-zero on console errors or failed checks.
// Setup once:  npm install --prefix build/e2e playwright@1.65.1   (npx playwright install chromium if no browser yet)
// Run:         node docs/test/e2e.mjs [--headed] [--only desktop,ref,realtime,phone,ix] [--assets <dir>]
//   --assets serves assets/ from another folder (e.g. a fresh export under build/, before it is copied into docs/)
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('../', import.meta.url)), OUT = fileURLToPath(new URL('../../build/e2e/', import.meta.url));
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const ASSETS = arg('--assets') && resolve(arg('--assets')), ONLY = arg('--only')?.split(','), run = (b) => !ONLY || ONLY.includes(b);
const { chromium } = createRequire(OUT)('playwright');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.glb': 'model/gltf-binary', '.jpg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.ktx2': 'image/ktx2', '.dxf': 'image/vnd.dxf', '.pdf': 'application/pdf' };
const server = createServer(async (req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (!url.startsWith('/home-design/')) { res.writeHead(404).end(); return; }
  const rel = normalize(url.slice('/home-design/'.length) || 'index.html').replace(/^([/\\]|\.\.)+/, '');
  const file = join(ROOT, rel.endsWith('/') || !rel ? join(rel, 'index.html') : rel);   // --assets: that folder first, then docs/assets
  try {
    const body = await (ASSETS && rel.replace(/\\/g, '/').startsWith('assets/') ? readFile(join(ASSETS, rel.slice(7))).catch(() => readFile(file)) : readFile(file));
    res.writeHead(200, { 'content-type': TYPES[extname(rel)] || 'application/octet-stream', 'content-length': body.length });
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch { res.writeHead(404).end(); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}/home-design/`;
await mkdir(OUT, { recursive: true });

const logs = [], fails = [];
const check = (ok, what) => { console.log(`${ok ? 'PASS' : 'FAIL'}  ${what}`); if (!ok) fails.push(what); };
const launch = (channel) => chromium.launch({ channel, headless: !process.argv.includes('--headed'), args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] });
const browser = await launch(undefined).catch(() => launch('chrome'));    // bundled browser, else the installed Chrome

async function open(ctxOpts, query = '', setup) {
  const ctx = await browser.newContext(ctxOpts), page = await ctx.newPage();
  if (setup) await setup(page);
  page.on('console', (m) => {
    const loc = m.location()?.url || '', line = `[${m.type()}] ${m.text()} ${loc}`;
    logs.push(line);
    if (m.type() === 'error') fails.push('console: ' + line);          // every asset is real now: a 404 is a failure
  });
  page.on('pageerror', (e) => { console.log('[pageerror]', e.message); logs.push('[pageerror] ' + e.message); fails.push('pageerror: ' + e.message); });
  await page.goto(BASE + query);
  await page.waitForSelector('#loader.done', { timeout: 60000 });
  await page.waitForTimeout(800);
  return { ctx, page };
}
const info = (page) => page.evaluate(() => window.viewer.info());
// wait until nothing moves (room jump / walk, door swings, light fades): frames are dt-clamped, so when the GPU is
// shared with Cycles bakes an animation can take longer than its nominal time
const idle = (page, ms = 150) => page.waitForFunction(() => {
  const v = window.viewer;
  return !v.S.anim && !v.S.glide && v.ix.groups().every((g) => g.p === g.state) && [...v.roomLights.values()].every((L) => (L.x ?? L.target) === L.target);
}, null, { timeout: 20000, polling: 50 }).catch(() => {}).then(() => page.waitForTimeout(ms));
const shot = (page, name, el) => (el ? page.locator(el).screenshot({ path: OUT + name }) : page.screenshot({ path: OUT + name }));

// ---- desktop ----
if (run('desktop')) {
  // gallery: fake renders/index.json + images via request interception (nothing written into docs/renders)
  const fakeRenders = async (page) => {
    await page.route('**/renders/index.json', (r) => r.fulfill({ json: [{ file: 'a.jpg', title: 'Hallway (test image)' }, 'b.jpg'] }));
    await page.route(/renders\/[ab]\.jpg$/, async (r) => r.fulfill({ contentType: 'image/jpeg',
      body: await readFile(join(ROOT, 'assets/probes', r.request().url().endsWith('a.jpg') ? 'hallway.jpg' : 'living.jpg')).catch(() => Buffer.alloc(0)) }));
  };
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } }, '', fakeRenders);
  let i = await info(page);
  console.log('info', JSON.stringify(i));
  check(i.room === 'hallway', `spawns in the hallway (${i.room})`);
  check(i.realtime || i.lightmapped > 0, `lightmaps applied when a manifest exists (${i.lightmapped} meshes)`);
  // baked lighting on the real export: every manifest object found with uv1 (no warnings), probes on everything
  const bake = await page.evaluate(async () => {
    const m = await (await fetch('assets/manifest.json')).json(), all = [];
    const { scene, ring, ix } = window.viewer;          // the model only: not the floor ring, not effect materials (TV, flame)
    scene.traverse((o) => o.isMesh && o !== ring && !ix.tagged(o) && all.push(...[].concat(o.material).map((mat) => ({ o, mat }))));
    const lit = all.filter((a) => a.o.userData.baked);
    return { listed: m.lightmaps.reduce((n, l) => n + l.objects.length, 0), probes: m.probes.length, standin: !!m.standin,
      noEnv: all.filter((a) => !a.mat.envMap).length, noUv1: lit.filter((a) => !a.o.geometry.attributes.uv1).length,
      badLm: lit.filter(({ mat }) => !(mat.lightMap?.channel === 1 && mat.lightMap.flipY === false && mat.lightMap.colorSpace === 'srgb' && mat.lightMapIntensity > 3)).length };
  });
  check(!bake.standin && bake.listed > 50 && bake.probes >= 7, `real export manifest (${bake.listed} lightmapped objects, ${bake.probes} probes)`);
  check(bake.noUv1 === 0 && bake.badLm === 0, 'lightmaps on uv1, flipY off, sRGB, intensity x PI');
  check(i.probed > 0 && bake.noEnv === 0, `room probes on every material (${i.probed} meshes lit by probe alone)`);
  check(!logs.some((l) => /not found in the GLB|no second UV|image missing|shader changed/.test(l)), 'no lightmap / probe warnings');
  await shot(page, 'walk_spawn.png');

  // keyboard walking: W for 1 s moves forward (+Y) and stays inside the walkable area
  await page.locator('#scene').focus();
  await page.keyboard.down('KeyW'); await page.waitForTimeout(1000); await page.keyboard.up('KeyW');
  const j = await info(page);
  check(j.y > i.y + 0.5 && Math.abs(j.x - i.x) < 0.05, `W walks into the house (y ${i.y.toFixed(2)} -> ${j.y.toFixed(2)})`);
  check(await page.evaluate(() => { const v = window.viewer; return !v.walk || v.G.isFree(v.walk, v.S.x, v.S.y); }), 'position is inside the walkable area');
  // walking into a wall is blocked: face east (-90deg) in the front hall and push for 2 s
  await page.evaluate(() => { const S = window.viewer.S; S.x = 0; S.y = 3; S.yaw = -Math.PI / 2; });
  await page.keyboard.down('KeyW'); await page.waitForTimeout(2000); await page.keyboard.up('KeyW');
  i = await info(page);
  check(i.room === 'hallway' && i.x < 0.5, `wall stops the walker (x = ${i.x.toFixed(2)})`);

  // real openings: W through the open living-room door; the closed under-stairs door stays shut
  await page.evaluate(() => Object.assign(window.viewer.S, { x: 0, y: 4.09, yaw: -Math.PI / 2 }));
  await page.keyboard.down('KeyW'); await page.waitForTimeout(1500); await page.keyboard.up('KeyW');
  i = await info(page); check(i.room === 'living', `walks through the living-room doorway (${i.room}, x = ${i.x.toFixed(2)})`);
  await page.evaluate(() => Object.assign(window.viewer.S, { x: 0.57, y: 8.2, yaw: Math.PI }));
  await page.keyboard.down('KeyW'); await page.waitForTimeout(1200); await page.keyboard.up('KeyW');
  i = await info(page); check(i.room === 'hallway' && i.y > 7.68, `closed under-stairs door blocks (y = ${i.y.toFixed(2)})`);

  // room jump buttons + keys, and a walk-mode screenshot of every room
  await page.getByRole('button', { name: /^Living/ }).click(); await idle(page);
  i = await info(page); check(i.room === 'living', `room button -> living (${i.room})`);
  await page.keyboard.press('Digit6'); await idle(page);   // 6th room in the list
  i = await info(page); check(i.room === 'utility', `key 6 -> utility (${i.room})`);
  for (const id of await page.evaluate(() => Object.keys(window.viewer.vps))) {
    await page.evaluate((id) => window.viewer.jump(id), id); await idle(page);
    i = await info(page); check(i.room === id, `jump -> ${id} (${i.room})`);
    await shot(page, `walk_${id}.png`);
  }
  await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { anim: null, x: -0.3, y: 3.6, pitch: 0.12, yaw: G.dirYaw(0.87, 2.6) }); });
  await page.waitForTimeout(300); await shot(page, 'walk_stairs.png');      // the staircase, seen from the hall

  // 3D <-> plan registration: stand in every open doorway. The GLB's jambs must sit half a clear width either side
  // (model = house.json), the plan's wall poche must be open there and solid just past the jambs (plan = house.json),
  // and the plan marker must be drawn on that spot.
  const doors = await page.evaluate(async () => {
    const house = await (await fetch('assets/house.json')).json();       // a pocket door's leaf stands ~0.09 m out of its pocket
    return window.viewer.walk.portals.map((q) => ({ id: q.id, c: q.center, n: q.normal, w: q.width, pocket: house.openings.find((o) => o.id === q.id).slideToward ? 0.1 : 0 }));
  });
  for (const d of doors) {
    const r = await page.evaluate(async (d) => {
      const { THREE, G, S, scene, planView: p } = window.viewer, [cx, cy] = d.c, ux = d.n[1], uy = -d.n[0], h = d.w / 2;
      Object.assign(S, { anim: null, x: cx, y: cy, pitch: -1.2, yaw: G.dirYaw(d.n[0], d.n[1]) });   // look down at the threshold
      Object.assign(p.v, { cx, cy, s: p.c.height / 4.5 }); p.dirty = true;        // zoom the plan on the doorway
      await new Promise((f) => requestAnimationFrame(() => requestAnimationFrame(f)));
      const ray = new THREE.Raycaster(); ray.far = 3;
      const jambs = [1, -1].map((s) => {
        ray.set(new THREE.Vector3(cx, 1.0, -cy), new THREE.Vector3(s * ux, 0, -s * uy));
        return ray.intersectObject(scene, true)[0]?.distance ?? 9;
      });
      const hatch = p.plan.entities.filter((e) => e.type === 'hatch' && e.layer === 'A-WALL-PATT');
      const solid = (x, y) => hatch.some((e) => G.pointInPoly(x, y, e.pts));
      const [X, Y] = p.toScreen(S.x, S.y), px = p.c.getContext('2d').getImageData(Math.round(X), Math.round(Y), 1, 1).data;
      return { jambs, open: !solid(cx, cy), ends: [1, -1].map((s) => solid(cx + s * ux * (h + 0.04), cy + s * uy * (h + 0.04))),
        marker: px[0] > 200 && px[1] < 140 && px[2] < 110, room: document.querySelector('#plan-room').textContent };
    }, d);
    // linings / frames narrow the hole by up to 60 mm a side; nothing may stand inside the clear width or beyond the wall face
    const ok3d = r.jambs.every((j) => j > d.w / 2 - 0.065 - d.pocket && j < d.w / 2 + 0.01);
    check(ok3d && r.open && r.ends.every(Boolean) && r.marker,
      `doorway ${d.id}: 3D jambs ${r.jambs.map((j) => Math.round(j * 1000))} mm vs half width ${Math.round(d.w * 500)}; plan open ${r.open}, jambs solid ${r.ends}; marker on spot ${r.marker}`);
    await shot(page, `door_${d.id}.png`);
  }
  await page.evaluate(() => { window.viewer.planView.fit(); window.viewer.S.pitch = 0; });
  await page.evaluate(() => window.viewer.jump('dining')); await idle(page);

  // plan marker sits at the camera position (dot centre pixel = marker colour)
  const px = await page.evaluate(() => {
    const { planView: p, S } = window.viewer, [X, Y] = p.toScreen(S.x, S.y), d = p.c.getContext('2d').getImageData(Math.round(X), Math.round(Y), 1, 1).data;
    return [...d];
  });
  check(px[0] > 200 && px[1] < 140 && px[2] < 110, `plan marker drawn at the camera position (rgb ${px.slice(0, 3)})`);
  check((await page.textContent('#plan-room')).toLowerCase().includes('dining'), 'plan names the current room');
  await shot(page, 'plan_cad.png', '#plan');
  await page.click('#plan-theme'); await page.waitForTimeout(200);
  await shot(page, 'plan_paper.png', '#plan');
  await page.click('#plan-theme');

  // click-to-teleport into the kitchen
  const target = await page.evaluate(() => {
    const p = window.viewer.planView, r = p.c.getBoundingClientRect(), [X, Y] = p.toScreen(2.8, 7.0);
    return [r.left + (X * r.width) / p.c.width, r.top + (Y * r.height) / p.c.height];
  });
  await page.mouse.click(...target); await idle(page);
  i = await info(page); check(i.room === 'kitchen', `plan click teleports to the kitchen (${i.room} @ ${i.x.toFixed(2)},${i.y.toFixed(2)})`);
  await shot(page, 'teleport_kitchen.png');
  // click into a wall lands on the nearest free point
  await page.evaluate(() => window.viewer.teleport(0.725, 3.0)); await idle(page);
  i = await info(page); check(['hallway', 'living'].includes(i.room), `teleport into a wall snaps to a free spot (${i.room})`);

  // dollhouse
  await page.click('#mode-orbit'); await page.waitForTimeout(1200);
  i = await info(page); check(i.mode === 'orbit', 'dollhouse mode on');
  await shot(page, 'orbit.png');
  await page.evaluate(() => window.viewer.jump('living')); await page.waitForTimeout(600);
  await shot(page, 'orbit_living.png');
  await page.evaluate(() => { const { orbit, camera } = window.viewer; orbit.target.set(0.7, 1.5, -4); camera.position.set(-0.6, 4.2, -2.4); });
  await page.waitForTimeout(600); await shot(page, 'orbit_closeup.png');           // section caps on the cut walls
  const before = await page.evaluate(() => window.viewer.orbit.target.toArray());
  await page.mouse.click(...target); await page.waitForTimeout(300);
  const after = await page.evaluate(() => window.viewer.orbit.target.toArray());
  check(Math.hypot(after[0] - before[0], after[2] - before[2]) > 0.5, 'plan click moves the dollhouse target');
  await page.keyboard.press('KeyO'); await page.waitForTimeout(500);
  i = await info(page); check(i.mode === 'walk' && i.room === 'kitchen', `back to walk where the dollhouse pointed (${i.room})`);

  await page.keyboard.press('Shift+Slash'); await page.waitForTimeout(300);
  check(await page.evaluate(() => document.querySelector('#help').open), 'help opens with ?');
  await shot(page, 'help.png'); await page.keyboard.press('Escape');
  await page.click('#plan-max'); await page.waitForTimeout(400); await shot(page, 'plan_max.png');
  await page.click('#plan-theme'); await page.waitForTimeout(300); await shot(page, 'plan_max_paper.png'); await page.click('#plan-theme');
  // downloads: the buttons hand over the real files
  for (const [sel, name, magic] of [['#dl-dxf', 'ground-floor-plan.dxf', 'SECTION'], ['#dl-pdf', 'ground-floor-plan.pdf', '%PDF']]) {
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click(sel)]);
    const body = await readFile(await dl.path());
    check(dl.suggestedFilename() === name && body.length > 10000 && body.toString('latin1', 0, 24).includes(magic), `${name} downloads (${body.length} bytes)`);
  }
  await page.click('#plan-max');
  check(await page.isVisible('#btn-gallery'), 'Renders button shown when renders/index.json exists');
  await page.click('#btn-gallery'); await page.waitForTimeout(300); await shot(page, 'gallery.png');
  await page.click('#gallery .grid button'); await page.waitForTimeout(300); await page.keyboard.press('ArrowRight'); await page.waitForTimeout(300);
  check((await page.getAttribute('#gallery .lightbox img', 'src')).endsWith('b.jpg'), 'lightbox opens and arrow keys step through renders');
  await shot(page, 'lightbox.png'); await page.keyboard.press('Escape');
  await ctx.close();
}
// ---- views matching the Cycles reference stills (960x540, vfov 70, UI hidden) for lightmap calibration ----
if (run('ref')) {
  const { ctx, page } = await open({ viewport: { width: 960, height: 540 } });
  await page.addStyleTag({ content: '#topbar,#plan,#hint,#pad{display:none!important}' });
  for (const [tag, pos, room] of [['hall', [0, 3], null], ['living', [1.25, 4.09], 'living']]) {
    await page.evaluate(([pos, room]) => {
      const { S, G, rooms } = window.viewer, c = room ? G.centroid(rooms.find((r) => r.id === room).polygon) : [pos[0], pos[1] + 1];
      Object.assign(S, { anim: null, x: pos[0], y: pos[1], pitch: 0, yaw: G.dirYaw(c[0] - pos[0], c[1] - pos[1]) });
    }, [pos, room]);
    await page.waitForTimeout(400); await shot(page, `ref_${tag}_viewer.png`);
  }
  await ctx.close();
}
// ---- real-time fallback lighting ----
if (run('realtime')) {
  const { ctx, page } = await open({ viewport: { width: 1280, height: 800 } }, '?lighting=realtime');
  check((await info(page)).realtime, 'realtime fallback active with ?lighting=realtime');
  await page.evaluate(() => window.viewer.jump('living')); await page.waitForTimeout(1500);
  await shot(page, 'realtime_living.png');
  await ctx.close();
}
// ---- phone ----
if (run('phone')) {
  const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  check(await page.evaluate(() => document.body.classList.contains('touch')), 'touch UI on a phone');
  await shot(page, 'phone.png');
  // move pad: hold the knob forward for 1 s
  const i0 = await info(page), pad = await page.locator('#pad').boundingBox();
  const cdp = await ctx.newCDPSession(page), cx = pad.x + pad.width / 2, cy = pad.y + pad.height / 2;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: cx, y: cy }] });
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: cx, y: cy - 40 }] });
  await page.waitForTimeout(1000);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  const i1 = await info(page);
  check(i1.y > i0.y + 0.3, `touch pad walks forward (y ${i0.y.toFixed(2)} -> ${i1.y.toFixed(2)})`);
  await page.tap('#plan-toggle'); await page.waitForTimeout(200); await shot(page, 'phone_plan_collapsed.png');
  await page.tap('#plan-toggle'); await page.tap('#plan-max'); await page.waitForTimeout(400); await shot(page, 'phone_plan_max.png');
  // tap the plan: teleports on touch too
  const tap = await page.evaluate(() => {
    const p = window.viewer.planView, r = p.c.getBoundingClientRect(), [X, Y] = p.toScreen(1.2, 14.6);
    return [r.left + (X * r.width) / p.c.width, r.top + (Y * r.height) / p.c.height];
  });
  await page.touchscreen.tap(...tap); await idle(page);
  const i2 = await info(page); check(i2.room === 'dining', `tap on the plan teleports (${i2.room})`);
  await page.tap('#plan-max'); await page.tap('#mode-orbit'); await page.waitForTimeout(800); await shot(page, 'phone_orbit.png');
  await ctx.close();
}
// ---- interactions + mouse navigation, on the real tags of the published GLB (node extras `ix`, blender/INTERACT.md) ----
// up to 60 triangle centres on a group's visible meshes, spread over its surface (largest triangles first): points a
// ray can really hit, unlike box samples that fall inside a carcass or between curtains
const surf = (id) => {
  const { THREE, scene, ix } = window.viewer, tris = [], a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  scene.traverse((m) => {
    if (!m.isMesh || ix.groupOf(m) !== id) return;
    for (let o = m; o; o = o.parent) if (!o.visible) return;
    const pos = m.geometry.attributes.position, idx = m.geometry.index, n = (idx ? idx.count : pos.count) / 3, step = Math.max(1, Math.floor(n / 400));
    for (let t = 0; t < n; t += step) {
      const [i, j, k] = [0, 1, 2].map((q) => (idx ? idx.getX(3 * t + q) : 3 * t + q));
      a.fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld); b.fromBufferAttribute(pos, j).applyMatrix4(m.matrixWorld); c.fromBufferAttribute(pos, k).applyMatrix4(m.matrixWorld);
      tris.push([b.clone().sub(a).cross(c.clone().sub(a)).length(), a.clone().add(b).add(c).multiplyScalar(1 / 3)]);
    }
  });
  tris.sort((p, q) => q[0] - p[0]);
  const out = [], k = Math.max(1, Math.floor(tris.length / 60));
  for (let i = 0; i < tris.length && out.length < 60; i += k) out.push(tris[i][1]);
  return out;
};
const inPage = (page) => page.evaluate(`window.__surf = ${surf}`);
const settle = (page, ms = 0) => page.evaluate((ms) => new Promise((f) => setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(f)), ms)), ms);
// stand 0.8..2.4 m from a group where some point of it is in plain sight at eye height and look at that point; [x, y] or null
const approach = (page, id) => page.evaluate((id) => {
  const { THREE, G, S, walk, ix, castRay } = window.viewer, pts = window.__surf(id).slice(0, 50), [tx, ty] = G.threeToPlan(ix.box(id).getCenter(new THREE.Vector3()));
  for (const R of [1.1, 0.8, 1.4, 1.8, 2.4]) for (let k = 0; k < 36; k++) {
    const a = (k / 36) * 2 * Math.PI, x = tx + R * Math.cos(a), y = ty + R * Math.sin(a), eye = new THREE.Vector3(x, 1.6, -y);
    if (!G.isFree(walk, x, y)) continue;
    for (const p of pts) {
      const dir = p.clone().sub(eye), hit = castRay(eye, dir.clone().normalize(), dir.length() + 0.3);
      if (!hit || ix.groupOf(hit.object) !== id) continue;
      const [hx, hy] = G.threeToPlan(hit.point);
      Object.assign(S, { anim: null, glide: null, x, y, yaw: G.dirYaw(hx - x, hy - y), pitch: Math.atan2(hit.point.y - 1.6, Math.hypot(hx - x, hy - y)) });
      return [x, y];
    }
  }
  return null;
}, id);
// a screen pixel whose ray really hits the group (tried over points on its surface), or null
const pixelOf = (page, id) => page.evaluate((id) => {
  const { camera, castAt, ix, renderer } = window.viewer, r = renderer.domElement.getBoundingClientRect();
  camera.updateMatrixWorld();
  for (const p of window.__surf(id)) {
    p.project(camera);
    if (Math.abs(p.x) > 0.95 || Math.abs(p.y) > 0.95 || p.z > 1) continue;
    const X = r.left + ((p.x + 1) / 2) * r.width, Y = r.top + ((1 - p.y) / 2) * r.height;
    if (document.elementFromPoint(X, Y) !== renderer.domElement) continue;        // under the plan, the top bar, the pad
    const hit = castAt(X, Y);
    if (hit && ix.groupOf(hit.object) === id) return [X, Y];
  }
  return null;
}, id);
// mean luminance (0..255) of the frame as rendered right now (render + read back in one task, so the buffer is valid)
const meanLum = (page) => page.evaluate(() => {
  const { renderer, scene, camera } = window.viewer, c = Object.assign(document.createElement('canvas'), { width: 192, height: 120 }), g = c.getContext('2d');
  renderer.render(scene, camera); g.drawImage(renderer.domElement, 0, 0, 192, 120);
  const d = g.getImageData(0, 0, 192, 120).data; let s = 0;
  for (let i = 0; i < d.length; i += 4) s += 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
  return s / (d.length / 4);
});
// first pixel down column X whose ray hits bare floor (not a step or a skirting); to = where a double-click should end
const floorAim = (page, X, Ys) => page.evaluate(([X, Ys]) => {
  const { castAt, G, walk, renderer } = window.viewer;
  for (const Y of Ys) {
    const hit = document.elementFromPoint(X, Y) === renderer.domElement && castAt(X, Y);
    const n = hit?.face?.normal.clone().transformDirection(hit.object.matrixWorld);
    if (n && n.y > 0.7 && hit.point.y < 0.3) { const p = G.threeToPlan(hit.point); return { X, Y, to: G.nearestFree(walk, p[0], p[1], 1.5) }; }
  }
  return { X, Y: Ys[0], to: null };
}, [X, Ys]);
const groups = (page) => page.evaluate(() => window.viewer.ix.groups());
const stateOf = (page, id) => page.evaluate((id) => window.viewer.ix.state(id), id);
const centreOf = (page, id) => page.evaluate((id) => window.viewer.ix.box(id).getCenter(new window.viewer.THREE.Vector3()).toArray(), id);
const skip = (what) => console.log(`SKIP  ${what}`);

if (run('ix')) {
  let i;
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } });
  await inPage(page);
  const gs = await groups(page), byId = new Map(gs.map((g) => [g.id, g])), kinds = {};
  for (const g of gs) kinds[g.kind] = (kinds[g.kind] || 0) + 1;
  console.log(`ix: ${gs.length} groups ${JSON.stringify(kinds)}, ${(await page.evaluate(() => window.viewer.ix.clocks())).length} clock hands`);
  check(gs.length > 50 && gs.every((g) => typeof g.hint === 'string' && g.hint), 'interaction groups built from the GLB tags, each with a hint label');
  check(['move', 'light', 'lamp', 'tv', 'water', 'flame', 'curtain'].every((k) => kinds[k]), `every kind of thing is operable (${Object.keys(kinds)})`);
  const shown = await page.evaluate(() => { const bad = []; window.viewer.scene.traverse((o) => { if (typeof o.userData.ix !== 'string') return; const d = JSON.parse(o.userData.ix); if (d.t === 'show' && o.visible !== (d.when === 0)) bad.push(o.userData.name); }); return bad; });
  check(!shown.length, `at load every state-1 object is hidden and every state-0 one shown (${shown})`);
  const hintOf = (id) => byId.get(id)?.hint;
  check(hintOf('vestibule.d_street.leaf.0') === 'Open front door' && hintOf('utility.switch.light') === 'Turn WC light off' && hintOf('wc.pan.seat') === 'Lift toilet seat'
    && hintOf('kitchen.switch') === 'Lights off' && hintOf('living.tv') === 'Switch TV on', `hint labels (${['vestibule.d_street.leaf.0', 'utility.switch.light', 'wc.pan.seat', 'kitchen.switch', 'living.tv'].map(hintOf)})`);
  await page.mouse.move(700, 450);
  await page.locator('#scene').focus();
  const toggle = (id) => page.evaluate((id) => window.viewer.ix.toggle(id), id);
  const openOf = (id) => page.evaluate((id) => window.viewer.ix.groups().find((g) => g.id === id).open, id);
  const visible = (names) => page.evaluate((names) => { const v = {}; window.viewer.scene.traverse((o) => { if (names.includes(o.userData.name)) v[o.userData.name] = o.visible; }); return names.map((n) => v[n]); }, names);

  // A. a door: hover hint + pointer, click toggles leaf and doorway (shut = impassable), Space toggles it back
  const portalIds = await page.evaluate(() => window.viewer.walk.portals.map((p) => p.id));
  const doors = gs.filter((g) => g.blocks.some((b) => portalIds.includes(b)));
  const door = doors.find((g) => g.blocks.includes('d_kitchen')) || doors[0];
  if (!door) skip('door: no leaf blocks a walkable doorway');
  else {
    const pid = door.blocks.find((b) => portalIds.includes(b));
    const doorway = () => page.evaluate((id) => { const { walk, G } = window.viewer, p = walk.portals.find((q) => q.id === id); return { open: p.open !== false, free: G.isFree(walk, ...p.center) }; }, pid);
    check(!!(await approach(page, door.id)), `stands in sight of ${door.id}`); await settle(page, 100);
    const d0 = await doorway(), c0 = await centreOf(page, door.id), px = await pixelOf(page, door.id);
    check(d0.open === door.open && d0.free === d0.open, `doorway ${pid} starts ${d0.open ? 'passable' : 'shut'}, like its leaf`);
    if (!px) check(false, `a pixel on ${door.id}`);
    else {
      await page.mouse.move(...px); await settle(page, 120); await shot(page, 'ix_door_0.png');
      const tip = await page.evaluate(() => ({ text: document.querySelector('#ix-tip').textContent, shown: !document.querySelector('#ix-tip').hidden, cursor: document.querySelector('#scene').style.cursor }));
      check(tip.shown && /^(Open|Close) door$/.test(tip.text) && tip.cursor === 'pointer', `hover: pointer cursor and label "${tip.text}"`);
      await page.mouse.click(...px); await page.waitForTimeout(400); await idle(page);
      const d1 = await doorway(), c1 = await centreOf(page, door.id), moved = Math.hypot(c1[0] - c0[0], c1[2] - c0[2]);
      check((await stateOf(page, door.id)) === 1 && d1.open === !d0.open && d1.free === d1.open, `click toggles the leaf and its doorway (passable ${d0.open} -> ${d1.open})`);
      check(moved > 0.15, `the leaf swings (centre moves ${Math.round(moved * 1000)} mm)`);
      await page.mouse.move(700, 20); await settle(page, 120); await shot(page, 'ix_door_1.png');   // pointer off the scene
      await approach(page, door.id); await page.evaluate(() => { window.viewer.S.pitch -= 0.25; }); await settle(page, 250);  // in reach of the shut leaf, aimed a little off it
      const pre = await groups(page);
      await page.locator('#scene').focus(); await page.keyboard.press('Space'); await idle(page);
      const changed = (await groups(page)).filter((g, k) => g.state !== pre[k].state).map((g) => g.id);
      check((await stateOf(page, door.id)) === 0 && (await doorway()).open === d0.open, `Space toggles the door in front back (toggled: ${changed})`);
    }
    // shut on a walker standing in the doorway: they are let out, and a shut door is no route
    if (!(await openOf(door.id))) { await toggle(door.id); await idle(page); }
    const inDoor = await page.evaluate((id) => { const { S, walk } = window.viewer, p = walk.portals.find((q) => q.id === id); Object.assign(S, { anim: null, glide: null, x: p.center[0], y: p.center[1] }); return p.center; }, pid);
    await toggle(door.id); await idle(page, 300);
    const out = await page.evaluate((c) => { const { S, G, walk } = window.viewer; return { free: G.isFree(walk, S.x, S.y), d: Math.hypot(S.x - c[0], S.y - c[1]) }; }, inDoor);
    check(out.free && out.d > 0.1, `closing the door on the walker moves them out of the doorway (${Math.round(out.d * 1000)} mm)`);
    if (pid === 'd_kitchen') {
      const shut = await page.evaluate(() => window.viewer.G.route(window.viewer.walk, [0, 3], [2.8, 7.0]));
      await toggle(door.id); await idle(page);
      const open = await page.evaluate(() => window.viewer.G.route(window.viewer.walk, [0, 3], [2.8, 7.0]));
      check(shut === null && !!open, 'no route into the kitchen while its door is shut, one once it is open');
    } else { await toggle(door.id); await idle(page); }
  }

  // A2. the pocket door slides shut across its doorway and back
  {
    const id = 'utility.d_wc.leaf', c0 = await centreOf(page, id);
    await toggle(id); await idle(page);
    const c1 = await centreOf(page, id), shut = await page.evaluate(() => window.viewer.walk.portals.find((p) => p.id === 'd_wc').open === false);
    check(shut && Math.hypot(c1[0] - c0[0], c1[2] - c0[2]) > 0.4, `${id} slides shut (${Math.round(Math.hypot(c1[0] - c0[0], c1[2] - c0[2]) * 1000)} mm) and closes d_wc`);
    await toggle(id); await idle(page);
  }

  // B. a cupboard door: hover label, click opens it about its hinge
  {
    const id = 'kitchen.base.hob.h2';
    check(!!(await approach(page, id)), `stands in sight of ${id}`); await settle(page, 100);
    const c0 = await centreOf(page, id), px = await pixelOf(page, id);
    if (!px) check(false, `a pixel on ${id}`);
    else {
      await page.mouse.move(...px); await settle(page, 120);
      const tip = await page.evaluate(() => document.querySelector('#ix-tip').textContent);
      await shot(page, 'ix_cupboard_0.png');
      await page.mouse.click(...px); await page.waitForTimeout(400); await idle(page);
      const c1 = await centreOf(page, id), moved = Math.hypot(c1[0] - c0[0], c1[1] - c0[1], c1[2] - c0[2]);
      check(tip === 'Open cupboard' && (await stateOf(page, id)) === 1 && moved > 0.08, `"${tip}": click opens ${id} (centre moves ${Math.round(moved * 1000)} mm)`);
      await page.mouse.move(700, 20); await settle(page, 120); await shot(page, 'ix_cupboard_1.png'); await toggle(id); await idle(page);
    }
  }
  // B2. a drawer at knee height is within reach of Space (reach is measured from the body, not the eye)
  {
    const id = 'vestibule.stool.drawer.0';
    check(!!(await approach(page, id)), `stands in sight of ${id}`); await page.mouse.move(700, 20); await settle(page, 100);
    const c0 = await centreOf(page, id);
    await page.locator('#scene').focus(); await page.keyboard.press('Space'); await idle(page);
    const c1 = await centreOf(page, id), moved = Math.hypot(c1[0] - c0[0], c1[2] - c0[2]);
    check((await stateOf(page, id)) === 1 && moved > 0.25, `Space opens the low ${id} (slides ${Math.round(moved * 1000)} mm)`);
    await shot(page, 'ix_drawer.png'); await toggle(id); await idle(page);
  }
  // B3. excl: fronts whose swings cross are never open together - opening one shuts the other first
  {
    await toggle('kitchen.dishwasher'); await idle(page);
    await toggle('kitchen.base.hob.drawer.2'); await idle(page);
    check(!(await openOf('kitchen.dishwasher')) && (await openOf('kitchen.base.hob.drawer.2')), 'opening the hob drawer shuts the dishwasher (excl)');
    await toggle('kitchen.base.hob.drawer.2'); await idle(page);
  }

  // C. both TVs: the picture is drawn by code, moves, and goes away again
  for (const tv of gs.filter((g) => g.kind === 'tv')) {
    await toggle(tv.id); await page.waitForTimeout(400);
    await approach(page, tv.id); await page.waitForTimeout(1000);
    const frame = () => page.evaluate((id) => {
      const c = window.viewer.ix.tvCanvas(id), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let s = 0, h = 0;
      for (let i = 0; i < d.length; i += 4) { s += d[i] + d[i + 1] + d[i + 2]; h = (h * 31 + d[i] + d[i + 1] * 7 + d[i + 2] * 13) | 0; }
      return { mean: s / (d.length * 0.75), h };
    }, tv.id);
    const a = await frame(); await page.waitForTimeout(700); const b = await frame();
    const pic = tv.nodes.filter((n) => /picture/.test(n));
    check(a.h !== b.h && a.mean > 30 && (await visible(pic)).every(Boolean), `${tv.id}: picture shown and animating (mean ${a.mean.toFixed(0)}, two frames differ)`);
    await shot(page, `ix_${tv.id.replace(/\W+/g, '_')}_on.png`); await toggle(tv.id); await idle(page);
    check((await stateOf(page, tv.id)) === 0 && !(await visible(pic)).some(Boolean), `${tv.id} switches off`);
  }

  // C2. every other effect group - taps (water), hob burners (flame), fridge / oven lights (glow), curtains (cross-fade):
  // its state-1 objects appear and its state-0 objects go, and back
  const fxg = gs.filter((g) => g.fx.length && g.kind !== 'tv');
  const shows = await page.evaluate((ids) => { const o = {}; window.viewer.scene.traverse((n) => { if (typeof n.userData.ix !== 'string') return; const d = JSON.parse(n.userData.ix); if (d.t === 'show' && ids.includes(d.g)) (o[d.g] ||= []).push([n.userData.name, d.when]); }); return o; }, fxg.map((g) => g.id));
  const fxState = async (on) => { const bad = []; for (const g of fxg) { const v = await visible(shows[g.id].map((s) => s[0])); shows[g.id].forEach(([n, w], k) => { if (v[k] !== (w === (on ? 1 : 0))) bad.push(n); }); } return bad; };
  for (const g of fxg) await toggle(g.id);
  await idle(page, 300);
  const badOn = await fxState(true);
  await page.evaluate(() => window.viewer.jump('kitchen')); await idle(page);
  await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { x: 3.0, y: 6.65, yaw: G.dirYaw(0.8, -0.05), pitch: -0.55 }); }); await settle(page, 150);
  await shot(page, 'ix_hob_on.png');
  for (const g of fxg) await toggle(g.id);
  await idle(page);
  const badOff = await fxState(false);
  check(!badOn.length && !badOff.length && (await groups(page)).filter((g) => fxg.some((f) => f.id === g.id)).every((g) => g.state === 0),
    `${fxg.length} effect groups (${[...new Set(fxg.map((g) => g.kind))]}) show their state-1 objects and hide them again (${badOn}${badOff})`);

  // C3. the toilet seat lifts
  {
    const id = 'wc.pan.seat', c0 = await centreOf(page, id);
    await toggle(id); await idle(page);
    const c1 = await centreOf(page, id);
    check(c1[1] - c0[1] > 0.12, `${id} lifts (centre rises ${Math.round((c1[1] - c0[1]) * 1000)} mm)`);
    await toggle(id); await idle(page);
  }

  // D. clock hands follow the visitor's local time
  const hands = await page.evaluate(() => {
    const d = new Date(), m = d.getMinutes() + (d.getSeconds() + d.getMilliseconds() / 1000) / 60, h = (d.getHours() % 12) + m / 60;
    return window.viewer.ix.clocks().map((c) => {
      const want = 2 * Math.PI * { h: h / 12, m: m / 60, s: d.getSeconds() / 60 }[c.hand];
      return { ...c, err: Math.abs(Math.atan2(Math.sin(c.angle - want), Math.cos(c.angle - want))) };
    });
  });
  if (!hands.length) skip('clock: no clock hands');
  else check(hands.every((c) => c.err < (c.hand === 's' ? 0.12 : 0.01)), `clock hands at local time (${hands.map((c) => `${c.name} ${c.hand} err ${c.err.toFixed(4)} rad`).join(', ')})`);

  // E. a light switch: the room's bake dims to the lights-off set and comes back
  const light = gs.find((g) => g.kind === 'light' && g.rooms.includes('kitchen')) || gs.find((g) => g.kind === 'light');
  if (!light) skip('lights: no switch');
  else {
    await page.evaluate((r) => window.viewer.jump(r), light.rooms[0]); await idle(page, 400);
    const on = await meanLum(page); await shot(page, 'ix_lights_on.png');
    await toggle(light.id); await idle(page);
    const off = await meanLum(page), hint = (await groups(page)).find((g) => g.id === light.id).hint; await shot(page, 'ix_lights_off.png');
    check(off < on * 0.75 && hint === 'Lights on', `${light.id}: ${light.rooms} lights off darkens the view (mean ${on.toFixed(1)} -> ${off.toFixed(1)}), hint "${hint}"`);
    await toggle(light.id); await idle(page);
    const back = await meanLum(page);
    check(Math.abs(back - on) < on * 0.04, `... and back on (${back.toFixed(1)})`);
  }
  // E2. switches act on the rooms they are wired to (the WC light switch is in the utility); lamps go dark with their room,
  // the table lamp on its own plug included, and come back
  {
    const lit = () => page.evaluate(() => Object.fromEntries([...window.viewer.roomLights].map(([r, L]) => [r, L.target])));
    await toggle('utility.switch.light'); await idle(page);
    const l1 = await lit();
    check(l1.wc === 0 && l1.utility === 1, `utility.switch.light switches the WC (wc ${l1.wc}, utility ${l1.utility})`);
    await toggle('utility.switch.light'); await idle(page);
    await page.evaluate(() => window.viewer.jump('living')); await idle(page, 200);
    await toggle('living.dimmer'); await idle(page);
    const lamps = (await groups(page)).filter((g) => g.kind === 'lamp' && (g.rooms.includes('living') || g.home === 'living'));
    const glow = await page.evaluate(() => { let s = 0; window.viewer.scene.traverse((o) => { if (o.isMesh && /living\.(sconce|table_lamp)/.test(o.userData.name || o.parent?.userData.name || '')) for (const m of [].concat(o.material)) s += m.emissiveIntensity > 0 && m.emissive && m.emissive.r + m.emissive.g > 0 ? m.emissiveIntensity : 0; }); return s; });
    await shot(page, 'ix_living_off.png');
    check(lamps.length >= 3 && lamps.every((g) => g.state === 1) && glow < 1e-3, `living lights off: ${lamps.map((g) => g.id)} dark (emissive sum ${glow.toFixed(3)})`);
    await toggle('living.dimmer'); await idle(page);
    check((await groups(page)).filter((g) => lamps.some((l) => l.id === g.id)).every((g) => g.state === 0), '... and lit again with the room');
  }

  // F. double-click on the floor walks there (ring under the cursor first); the double-click operates nothing
  await page.evaluate(() => Object.assign(window.viewer.S, { anim: null, glide: null, x: 0, y: 3, yaw: 0, pitch: -0.3 })); await settle(page, 100);
  const states = (await groups(page)).map((g) => g.state).join();
  const aim = await floorAim(page, 720, [640, 680, 720, 600]);
  await page.mouse.move(aim.X, aim.Y); await settle(page, 80);
  const ring = await page.evaluate(() => window.viewer.ring.visible); await shot(page, 'ix_ring.png');
  await page.mouse.dblclick(aim.X, aim.Y); await page.waitForTimeout(300);
  await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 10000 }).catch(() => {});
  i = await info(page);
  check(ring && aim.to && Math.hypot(i.x - aim.to[0], i.y - aim.to[1]) < 0.15,
    `double-click walks to the floor point (${aim.to?.map((v) => v.toFixed(2))} -> ${i.x.toFixed(2)}, ${i.y.toFixed(2)}; ring ${ring})`);
  check((await groups(page)).map((g) => g.state).join() === states, 'the double-click operated nothing');
  // ... on a wall: to the floor in front of it
  await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { anim: null, glide: null, x: 0, y: 3.3, yaw: G.dirYaw(-1, 0), pitch: 0 }); }); await settle(page, 100);
  await page.mouse.dblclick(720, 450); await page.waitForTimeout(300);
  await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 10000 }).catch(() => {});
  i = await info(page);
  check(i.x < -0.1 && i.x > -0.52 && Math.abs(i.y - 3.3) < 0.1, `double-click on a wall walks up to it (x ${i.x.toFixed(2)})`);
  await page.evaluate(() => window.viewer.walkTo(1.2, 14.6)); await page.waitForTimeout(300);
  await page.keyboard.press('ArrowLeft');
  check(await page.evaluate(() => !window.viewer.S.glide), 'a key press stops the walk');
  // K. after a click on a toolbar button, Space uses the thing in front instead of pressing the button again
  await page.getByRole('button', { name: /^Kitchen/ }).click(); await idle(page);
  await approach(page, 'kitchen.wall.w1'); await page.mouse.move(700, 20); await settle(page, 100);
  await page.keyboard.press('Space'); await idle(page);
  check((await stateOf(page, 'kitchen.wall.w1')) === 1 && (await info(page)).room === 'kitchen', 'Space after clicking a room button opens the cupboard in front');
  await toggle('kitchen.wall.w1'); await idle(page);

  // G. wheel zoom (field of view, eased, clamped); the plan's view cone follows
  await page.mouse.move(720, 450); await page.mouse.wheel(0, -800); await page.waitForTimeout(700);
  const z1 = await page.evaluate(() => { const { camera, planView, G } = window.viewer; return { fov: camera.fov, hfov: planView.viewer.hfov, want: G.hfov(camera.fov, camera.aspect) }; });
  check(z1.fov < 45 && z1.fov >= 21.99 && Math.abs(z1.hfov - z1.want) < 0.02, `wheel zooms in (fov ${z1.fov.toFixed(1)}), the plan cone follows`);
  await shot(page, 'ix_zoom.png');
  await page.mouse.wheel(0, 5000); await page.waitForTimeout(900);
  const z2 = await page.evaluate(() => window.viewer.camera.fov);
  check(z2 > 85 && z2 <= 90.01, `wheel zooms out to the 90 deg limit (${z2.toFixed(1)})`);
  await page.evaluate(() => { window.viewer.S.fovT = window.viewer.FOV; }); await page.waitForTimeout(700);

  // H. narrow gaps, walked for real: both long sides of the dining table, past the kitchen bins, into the WC
  const gaps = await page.evaluate(async () => {
    const foot = await (await fetch('assets/footprints.json')).json(), list = Array.isArray(foot) ? foot : foot.items || [];
    const o = list.find((f) => f.name === 'dining.table')?.obb, xs = o?.map((p) => p[0]), ys = o?.map((p) => p[1]), ty = o && (Math.min(...ys) + Math.max(...ys)) / 2;
    return [...(o ? [['west side of the dining table', [Math.min(...xs) - 0.25, ty]], ['east side of the dining table', [Math.max(...xs) + 0.25, ty]]] : []),
      ['kitchen bins', [2.88, 8.5]], ['WC', [1.75, 9.75]], ['gap between the sofa and the coffee table', [2.2, 2.0]]];
  });
  for (const [what, p] of gaps) {
    const ok = await page.evaluate((p) => window.viewer.walkTo(...p), p);
    await page.waitForTimeout(300); await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 15000 }).catch(() => {});
    i = await info(page);
    check(ok && Math.hypot(i.x - p[0], i.y - p[1]) < 0.2, `walks to the ${what} (${i.x.toFixed(2)}, ${i.y.toFixed(2)})`);
    await shot(page, `ix_gap_${what.replace(/\W+/g, '_')}.png`);
  }

  // I. the dollhouse: click operates too
  const target = door;
  if (target) {
    await page.evaluate(() => window.viewer.setMode('orbit')); await page.waitForTimeout(500);
    let px = null;
    for (const az of [0.8, 2.4, 3.9, 5.5]) {
      await page.evaluate(([id, az]) => {
        const { ix, orbit, camera, THREE } = window.viewer, c = ix.box(id).getCenter(new THREE.Vector3());
        orbit.target.copy(c); camera.position.set(c.x + 2.6 * Math.cos(az), c.y + 3.6, c.z + 2.6 * Math.sin(az)); orbit.update();
      }, [target.id, az]);
      await settle(page, 300);
      if ((px = await pixelOf(page, target.id))) break;
    }
    if (!px) check(false, `a pixel on ${target.id} in the dollhouse`);
    else {
      const s0 = await stateOf(page, target.id);
      await page.mouse.click(...px); await page.waitForTimeout(100); await idle(page);
      check((await stateOf(page, target.id)) !== s0, `click in the dollhouse toggles ${target.id}`);
      await shot(page, 'ix_dollhouse.png'); await toggle(target.id);
    }
    await page.evaluate(() => window.viewer.setMode('walk'));
  }
  await ctx.close();

  // J. touch: tap operates, double-tap walks
  {
    const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await inPage(page);
    if (door && (await approach(page, door.id))) {
      await settle(page, 100);
      const px = await pixelOf(page, door.id), s0 = await stateOf(page, door.id);
      if (px) { await page.touchscreen.tap(...px); await page.waitForTimeout(400); await idle(page); }
      check(!!px && (await stateOf(page, door.id)) !== s0, 'a tap toggles the door on a phone');
      await shot(page, 'ix_phone_door.png');
    }
    await page.evaluate(() => Object.assign(window.viewer.S, { anim: null, glide: null, x: 0, y: 3, yaw: 0, pitch: -0.3 })); await settle(page, 100);
    const aim = await floorAim(page, 230, [700, 740, 660, 780, 620]);
    await page.touchscreen.tap(aim.X, aim.Y); await page.touchscreen.tap(aim.X, aim.Y); await page.waitForTimeout(300);
    await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 10000 }).catch(() => {});
    i = await info(page);
    check(aim.to && Math.hypot(i.x - aim.to[0], i.y - aim.to[1]) < 0.15, `double-tap walks there (${aim.to?.map((v) => v.toFixed(2))} -> ${i.x.toFixed(2)}, ${i.y.toFixed(2)})`);
    // pinch: two fingers apart zoom in, together zoom out; nothing is operated
    const cdp = await ctx.newCDPSession(page), states = (await groups(page)).map((g) => g.state).join();
    const pinch = async (x0, dx) => {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 195 - x0, y: 620, id: 1 }, { x: 195 + x0, y: 620, id: 2 }] });
      for (let k = 1; k <= 8; k++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 195 - x0 - k * dx, y: 620, id: 1 }, { x: 195 + x0 + k * dx, y: 620, id: 2 }] }); await page.waitForTimeout(30); }
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await page.waitForTimeout(800);
      return page.evaluate(() => window.viewer.camera.fov);
    };
    const f1 = await pinch(40, 8), f2 = await pinch(104, -8);
    check(f1 < 40 && f2 > 65 && (await groups(page)).map((g) => g.state).join() === states, `pinch zooms in and out (fov ${f1.toFixed(0)} -> ${f2.toFixed(0)}) and operates nothing`);
    await shot(page, 'ix_phone_hint.png');
    await ctx.close();
  }
}

await browser.close(); server.close();
await writeFile(OUT + 'console.txt', logs.join('\n'));
console.log(`\nscreenshots + console.txt in ${OUT}`);
console.log(fails.length ? `FAILED (${fails.length}):\n  ${fails.join('\n  ')}` : 'ALL CHECKS PASSED');
process.exit(fails.length ? 1 : 0);
